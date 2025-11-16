"""
Flask Backend API for Romanian Education RAG System.
Provides endpoints for generating clarifying questions and lecture materials.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

from firebase_service import FirebaseService
from services import (
    QuestionsService,
    LectureService,
    PresentonService,
    PodcastService,
    HomeworkService,
    HomeworkQuestionsService,
    ChatbotService,
    QuizService,
    PDFParserService,
    HomeworkGradingService,
    FlashcardsService
)
from config import Config
from session_manager import get_session_manager

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize Firebase Storage at startup
FirebaseService.initialize()

# Initialize session manager
session_manager = get_session_manager()

# Initialize services
print("Initializing services...")
try:
    questions_service = QuestionsService()
    lecture_service = LectureService()
    homework_service = HomeworkService()
    homework_questions_service = HomeworkQuestionsService()
    chatbot_service = ChatbotService()
    quiz_service = QuizService()
    pdf_parser_service = PDFParserService()
    grading_service = HomeworkGradingService()
    flashcards_service = FlashcardsService()
    
    # Try to initialize Presenton service (optional)
    try:
        presenton_service = PresentonService()
        print("✓ Presenton service initialized successfully")
    except ValueError as e:
        presenton_service = None
        print(f"⚠ Presenton service not available: {e}")
    
    # Try to initialize Podcast service (optional)
    try:
        podcast_service = PodcastService()
        print("✓ Podcast service initialized successfully")
    except ValueError as e:
        podcast_service = None
        print(f"⚠ Podcast service not available: {e}")
    
    print("✓ Core services initialized successfully")
except Exception as e:
    print(f"❌ Error initializing services: {e}")
    raise


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Romanian Education RAG API is running"
    }), 200


@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    """
    Generate clarifying questions for lecture preparation.
    
    Expected JSON body:
    {
        "title": "Celula - unitatea structurală și funcțională a vieții",
        "subject": "Biologie",
        "grade": 6
    }
    
    Returns JSON with generated questions and response options.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        title = data.get('title')
        subject = data.get('subject')
        grade = data.get('grade')
        
        if not title or not subject or grade is None:
            return jsonify({
                "error": "Missing required parameters: title, subject, and grade are required"
            }), 400
        
        # Validate grade is an integer
        try:
            grade = int(grade)
            if grade < 1 or grade > 12:
                return jsonify({
                    "error": "Grade must be between 1 and 12"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "Grade must be a valid integer"
            }), 400
        
        # Generate questions
        result = questions_service.generate_questions(title, subject, grade)
        
        # Return response
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        print(f"Error in generate_questions: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-lecture', methods=['POST'])
def generate_lecture():
    """
    Generate student and teacher versions of a lecture using RAG.
    
    Expected JSON body:
    {
        "title": "Celula - unitatea structurală și funcțională a vieții",
        "subject": "biologie",
        "grade": 6,
        "questions": [
            {
                "id": 1,
                "question": "Care este scopul principal al lecției?",
                "type": "single-choice",
                "options": ["...", "..."]
            }
        ],
        "answers": {
            "1": "Introducerea conceptelor noi",
            "2": "50 minute (o oră)"
        }
    }
    
    Returns JSON with student_version and teacher_version in HTML format.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        title = data.get('title')
        subject = data.get('subject')
        grade = data.get('grade')
        questions = data.get('questions')
        answers = data.get('answers')
        
        if not title or not subject or grade is None or not questions or not answers:
            return jsonify({
                "error": "Missing required parameters: title, subject, grade, questions, and answers are required"
            }), 400
        
        # Validate grade
        try:
            grade = int(grade)
            if grade < 1 or grade > 12:
                return jsonify({
                    "error": "Grade must be between 1 and 12"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "Grade must be a valid integer"
            }), 400
        
        # Validate questions is a list
        if not isinstance(questions, list):
            return jsonify({
                "error": "Questions must be a list"
            }), 400
        
        # Validate answers is a dictionary
        if not isinstance(answers, dict):
            return jsonify({
                "error": "Answers must be a dictionary mapping question IDs to answers"
            }), 400
        
        # Generate lecture
        result = lecture_service.generate_lecture(
            title=title,
            subject=subject,
            grade=grade,
            questions=questions,
            answers=answers
        )
        
        # Return response
        return jsonify({
            "success": True,
            "data": {
                "student_version": result["student_version"],
                "teacher_version": result["teacher_version"]
            }
        }), 200
        
    except Exception as e:
        print(f"Error in generate_lecture: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-presentation', methods=['POST'])
def generate_presentation():
    """
    Generate a PowerPoint presentation from student lecture content using Presenton API.
    
    Expected JSON body:
    {
        "student_version": "<h1>Celula...</h1><p>Content...</p>",
        "n_slides": 8,
        "language": "Romanian",
        "template": "general",
        "tone": "educational"
    }
    
    Returns JSON with presentation download URL, edit URL, and parsed slides data.
    """
    try:
        # Check if Presenton service is available
        if presenton_service is None:
            return jsonify({
                "error": "Presenton service not configured. Please add PRESENTON_API_KEY to your .env file."
            }), 503
        
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        student_version = data.get('student_version')
        
        if not student_version:
            return jsonify({
                "error": "Missing required parameter: student_version is required"
            }), 400
        
        # Optional parameters with defaults
        n_slides = data.get('n_slides', 8)
        language = data.get('language', 'Romanian')
        template = data.get('template', 'general')
        tone = data.get('tone', 'educational')
        verbosity = data.get('verbosity', 'standard')
        export_as = data.get('export_as', 'pptx')
        image_type = data.get('image_type', 'stock')
        theme = data.get('theme')
        
        # Validate n_slides
        try:
            n_slides = int(n_slides)
            if n_slides < 1 or n_slides > 50:
                return jsonify({
                    "error": "n_slides must be between 1 and 50"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "n_slides must be a valid integer"
            }), 400
        
        # Generate presentation with slides data
        result = presenton_service.generate_and_get_slides(
            content=student_version,
            n_slides=n_slides,
            language=language,
            template=template,
            tone=tone,
            verbosity=verbosity,
            export_as=export_as,
            image_type=image_type,
            theme=theme
        )
        
        # Return response
        return jsonify({
            "success": True,
            "data": {
                "presentation": result["presentation"],
                "slides": result["slides"]
            }
        }), 200
        
    except Exception as e:
        print(f"Error in generate_presentation: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-podcast', methods=['POST'])
def generate_podcast():
    """
    Generate an educational podcast from lecture content with AI dialogue and TTS.
    
    Expected JSON body:
    {
        "student_version": "<h1>Title</h1><p>Content...</p>",
        "teacher_version": "<h1>Title</h1><div class=\"teacher-note\">...</div>",
        "grade": 6,
        "subject": "Biologie",
        "target_duration": 300,
        "return_dialogue": true
    }
    
    Returns audio file (MP3) and optionally the dialogue transcript.
    """
    try:
        # Check if Podcast service is available
        if podcast_service is None:
            return jsonify({
                "error": "Podcast service not configured. Please check your OpenAI API key."
            }), 503
        
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        student_version = data.get('student_version')
        teacher_version = data.get('teacher_version')
        grade = data.get('grade')
        subject = data.get('subject')
        teacher_id = data.get('teacher_id')
        lecture_id = data.get('lecture_id')
        
        if not student_version or not teacher_version:
            return jsonify({
                "error": "Missing required parameters: student_version and teacher_version are required"
            }), 400
        
        if not grade or not subject:
            return jsonify({
                "error": "Missing required parameters: grade and subject are required"
            }), 400
        
        if not teacher_id or not lecture_id:
            return jsonify({
                "error": "Missing required parameters: teacher_id and lecture_id are required"
            }), 400
        
        # Optional parameters
        target_duration = data.get('target_duration', 300)  # 5 minutes default
        return_dialogue = data.get('return_dialogue', True)
        silence_between_turns = data.get('silence_between_turns', 500)
        upload_to_firebase = data.get('upload_to_firebase', True)  # Default to Firebase upload
        
        # Validate target_duration
        try:
            target_duration = int(target_duration)
            if target_duration < 60 or target_duration > 1800:  # 1 minute to 30 minutes
                return jsonify({
                    "error": "target_duration must be between 60 and 1800 seconds"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "target_duration must be a valid integer"
            }), 400
        
        # Generate podcast
        print(f"Generating podcast: {subject}, Grade {grade}, Duration: {target_duration}s")
        result = podcast_service.create_podcast(
            student_content=student_version,
            teacher_content=teacher_version,
            grade=grade,
            subject=subject,
            target_duration=target_duration,
            silence_between_turns=silence_between_turns,
            teacher_id=teacher_id,
            lecture_id=lecture_id,
            upload_to_firebase=upload_to_firebase
        )
        
        audio_bytes = result['audio_bytes']
        dialogue = result['dialogue']
        duration_seconds = result['duration_seconds']
        firebase_info = result.get('firebase_info')
        
        # Build response
        response_data = {
            "success": True,
            "data": {
                "audio_size_bytes": result['size_bytes'],
                "duration_seconds": duration_seconds,
                "dialogue": dialogue if return_dialogue else None,
                "metadata": {
                    "grade": grade,
                    "subject": subject,
                    "teacher_id": teacher_id,
                    "lecture_id": lecture_id,
                    "duration_target": target_duration,
                    "turns_count": len(dialogue)
                }
            }
        }
        
        # Add Firebase info if uploaded
        if firebase_info:
            response_data["data"]["firebase"] = {
                "path": firebase_info['destination_path'],
                "download_url": firebase_info['download_url'],
                "size_bytes": firebase_info['size_bytes']
            }
            print(f"✓ Podcast uploaded to Firebase: {firebase_info['destination_path']}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error in generate_podcast: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    """
    Generate a single-choice quiz based on lecture content.
    
    Expected JSON body:
    {
        "student_version": "<h1>Lecture content...</h1>",
        "num_questions": 10
    }
    
    Returns JSON with generated quiz questions.
    """
    try:
        # Check if quiz service is available
        if quiz_service is None:
            return jsonify({
                "error": "Quiz service is not available"
            }), 503
        
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        student_version = data.get('student_version')
        num_questions = data.get('num_questions', 10)
        
        if not student_version:
            return jsonify({
                "error": "Missing required parameter: student_version"
            }), 400
        
        # Validate num_questions
        try:
            num_questions = int(num_questions)
            if num_questions < 1 or num_questions > 50:
                return jsonify({
                    "error": "num_questions must be between 1 and 50"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "num_questions must be a valid integer"
            }), 400
        
        # Generate quiz
        print(f"Generating quiz with {num_questions} questions...")
        quiz_data = quiz_service.generate_quiz(
            student_version=student_version,
            num_questions=num_questions
        )
        
        return jsonify({
            "success": True,
            "data": quiz_data
        }), 200
        
    except ValueError as e:
        # Validation errors from the service
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        print(f"Error in generate_quiz: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-homework-questions', methods=['POST'])
def generate_homework_questions():
    """
    Generate clarifying questions for homework preparation.
    
    Expected JSON body:
    {
        "lesson_content": "<h1>Celula...</h1><p>Content...</p>",
        "num_exercises": 5,
        "subject": "Biologie",
        "grade": 6
    }
    
    Returns JSON with generated questions and response options.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        lesson_content = data.get('lesson_content')
        num_exercises = data.get('num_exercises')
        subject = data.get('subject')
        grade = data.get('grade')
        
        if not lesson_content or not num_exercises or not subject or grade is None:
            return jsonify({
                "error": "Missing required parameters: lesson_content, num_exercises, subject, and grade are required"
            }), 400
        
        # Validate num_exercises
        try:
            num_exercises = int(num_exercises)
            if num_exercises < 1 or num_exercises > 20:
                return jsonify({
                    "error": "num_exercises must be between 1 and 20"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "num_exercises must be a valid integer"
            }), 400
        
        # Validate grade
        try:
            grade = int(grade)
            if grade < 1 or grade > 12:
                return jsonify({
                    "error": "Grade must be between 1 and 12"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "Grade must be a valid integer"
            }), 400
        
        # Generate questions
        result = homework_questions_service.generate_questions(
            lesson_content=lesson_content,
            num_exercises=num_exercises,
            subject=subject,
            grade=grade
        )
        
        # Return response
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        print(f"Error in generate_homework_questions: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-homework', methods=['POST'])
def generate_homework():
    """
    Generate homework exercises from lesson content using RAG.
    
    Expected JSON body:
    {
        "lesson_content": "<h1>Celula...</h1><p>Content...</p>",
        "num_exercises": 5,
        "subject": "biologie",
        "grade": 6,
        "questions": [
            {
                "id": 1,
                "question": "Ce nivel de dificultate ar trebui să aibă exercițiile?",
                "type": "single-choice",
                "options": ["...", "..."]
            }
        ],
        "answers": {
            "1": "Mediu - aplicare și înțelegere",
            "2": "Combinație de tipuri"
        }
    }
    
    Returns JSON with homework exercises in HTML format.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract and validate parameters
        lesson_content = data.get('lesson_content')
        num_exercises = data.get('num_exercises')
        subject = data.get('subject')
        grade = data.get('grade')
        questions = data.get('questions')
        answers = data.get('answers')
        
        if not lesson_content or not num_exercises or not subject or grade is None or not questions or not answers:
            return jsonify({
                "error": "Missing required parameters: lesson_content, num_exercises, subject, grade, questions, and answers are required"
            }), 400
        
        # Validate num_exercises
        try:
            num_exercises = int(num_exercises)
            if num_exercises < 1 or num_exercises > 20:
                return jsonify({
                    "error": "num_exercises must be between 1 and 20"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "num_exercises must be a valid integer"
            }), 400
        
        # Validate grade
        try:
            grade = int(grade)
            if grade < 1 or grade > 12:
                return jsonify({
                    "error": "Grade must be between 1 and 12"
                }), 400
        except (TypeError, ValueError):
            return jsonify({
                "error": "Grade must be a valid integer"
            }), 400
        
        # Validate questions is a list
        if not isinstance(questions, list):
            return jsonify({
                "error": "Questions must be a list"
            }), 400
        
        # Validate answers is a dictionary
        if not isinstance(answers, dict):
            return jsonify({
                "error": "Answers must be a dictionary mapping question IDs to answers"
            }), 400
        
        # Generate homework
        result = homework_service.generate_homework(
            lesson_content=lesson_content,
            num_exercises=num_exercises,
            subject=subject,
            grade=grade,
            questions=questions,
            answers=answers
        )
        
        # Return response
        return jsonify({
            "success": True,
            "data": {
                "homework": result["homework"]
            }
        }), 200
        
    except Exception as e:
        print(f"Error in generate_homework: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Educational chatbot with role-based adaptation (student or individual).
    Maintains session-based conversation history (not persisted).
    
    Expected JSON body for NEW session:
    {
        "lesson_content": "<h1>Celula...</h1><p>Content...</p>",
        "user_prompt": "Ce este citoplasma?",
        "subject": "Biologie",
        "user_role": "student",  // or "individual"
        "grade": 6  // required if user_role is "student"
    }
    
    Expected JSON body for EXISTING session:
    {
        "session_id": "uuid-string",
        "user_prompt": "Poți să-mi dai un exemplu?"
    }
    
    Returns JSON with chatbot response and session information.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        user_prompt = data.get('user_prompt')
        session_id = data.get('session_id')
        
        if not user_prompt:
            return jsonify({
                "error": "Missing required parameter: user_prompt is required"
            }), 400
        
        # Determine if this is a new session or continuing an existing one
        if session_id:
            # Continue existing session
            session = session_manager.get_session(session_id)
            
            if session is None:
                return jsonify({
                    "error": "Session not found or expired. Please create a new session."
                }), 404
            
            lesson_content = session["lesson_content"]
            subject = session["subject"]
            user_role = session["user_role"]
            grade = session["grade"]
            conversation_history = session["conversation_history"]
            
        else:
            # Create new session
            lesson_content = data.get('lesson_content')
            subject = data.get('subject')
            user_role = data.get('user_role')
            grade = data.get('grade')
            
            if not lesson_content or not subject or not user_role:
                return jsonify({
                    "error": "Missing required parameters for new session: lesson_content, subject, and user_role are required"
                }), 400
            
            # Validate user_role
            if user_role not in ["student", "individual"]:
                return jsonify({
                    "error": "user_role must be either 'student' or 'individual'"
                }), 400
            
            # Validate grade for students
            if user_role == "student":
                if grade is None:
                    return jsonify({
                        "error": "grade is required when user_role is 'student'"
                    }), 400
                
                try:
                    grade = int(grade)
                    if grade < 1 or grade > 12:
                        return jsonify({
                            "error": "grade must be between 1 and 12"
                        }), 400
                except (TypeError, ValueError):
                    return jsonify({
                        "error": "grade must be a valid integer"
                    }), 400
            
            # Create new session
            session_id = session_manager.create_session(
                lesson_content=lesson_content,
                subject=subject,
                user_role=user_role,
                grade=grade
            )
            conversation_history = []
        
        # Generate chatbot response
        print(f"Chat request: session={session_id}, subject={subject}, role={user_role}, grade={grade}")
        result = chatbot_service.chat(
            user_prompt=user_prompt,
            lesson_content=lesson_content,
            subject=subject,
            user_role=user_role,
            grade=grade,
            conversation_history=conversation_history
        )
        
        # Update session with new conversation history
        session_manager.update_session(session_id, result["conversation_history"])
        
        # Clean up expired sessions periodically
        if session_id and len(session_id) % 10 == 0:  # Every 10th request
            expired_count = session_manager.cleanup_expired_sessions()
            if expired_count > 0:
                print(f"Cleaned up {expired_count} expired sessions")
        
        # Return response
        return jsonify({
            "success": True,
            "data": {
                "session_id": session_id,
                "response": result["response"],
                "user_role": user_role,
                "grade": grade,
                "message_count": len(result["conversation_history"])
            }
        }), 200
        
    except ValueError as e:
        print(f"Validation error in chat: {e}")
        return jsonify({
            "error": str(e)
        }), 400
    except Exception as e:
        print(f"Error in chat: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/parse-submission', methods=['POST'])
def parse_submission():
    """
    Parse a PDF homework submission and extract handwritten text.
    
    Expected JSON body:
    {
        "submission_url": "https://example.com/homework.pdf"
    }
    
    Returns JSON with parsed text from the PDF.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract submission URL
        submission_url = data.get('submission_url')
        
        if not submission_url:
            return jsonify({
                "error": "Missing required parameter: submission_url is required"
            }), 400
        
        print(f"Parsing PDF submission from: {submission_url}")
        
        # Parse the PDF
        result = pdf_parser_service.parse_pdf_submission(submission_url)
        
        if not result.get("success"):
            return jsonify({
                "error": f"Failed to parse PDF: {result.get('error', 'Unknown error')}"
            }), 500
        
        # Return parsed text
        return jsonify({
            "success": True,
            "data": {
                "parsed_text": result["parsed_text"],
                "page_count": result["page_count"],
                "pages": result["pages"]
            }
        }), 200
        
    except Exception as e:
        print(f"Error parsing submission: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/grade-homework', methods=['POST'])
def grade_homework():
    """
    Grade a homework submission by comparing with the original assignment.
    
    Expected JSON body:
    {
        "homework_html": "<h1>Temă pentru acasă</h1>...",
        "parsed_submission": "=== PAGE 1 ===\nExercițiul 1...",
        "subject": "Biologie",
        "grade": 6
    }
    
    Returns JSON with grading results for each exercise and overall grade.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract parameters
        homework_html = data.get('homework_html')
        parsed_submission = data.get('parsed_submission')
        subject = data.get('subject', '')
        grade = data.get('grade')
        
        if not homework_html or not parsed_submission:
            return jsonify({
                "error": "Missing required parameters: homework_html and parsed_submission are required"
            }), 400
        
        print(f"Grading homework for {subject} grade {grade}")
        print(f"Homework length: {len(homework_html)} chars")
        print(f"Submission length: {len(parsed_submission)} chars")
        
        # Grade the homework
        result = grading_service.grade_homework(
            homework_html=homework_html,
            parsed_submission=parsed_submission,
            subject=subject,
            grade=grade
        )
        
        if not result.get("success"):
            return jsonify({
                "error": result.get("error", "Failed to grade homework")
            }), 500
        
        # Return grading results
        return jsonify({
            "success": True,
            "data": {
                "total_points_earned": result["total_points_earned"],
                "total_points_possible": result["total_points_possible"],
                "final_grade_percentage": result["final_grade_percentage"],
                "exercises": result["exercises"],
                "overall_feedback": result["overall_feedback"],
                "subject": result.get("subject", ""),
                "grade_level": result.get("grade_level")
            }
        }), 200
        
    except Exception as e:
        print(f"Error grading homework: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/generate-flashcards', methods=['POST'])
def generate_flashcards():
    """
    Generate flashcards from student lesson content.
    
    Expected JSON body:
    {
        "student_version": "<h1>Lesson content...</h1>",
        "num_flashcards": 10,
        "subject": "Biologie",
        "grade": 6
    }
    
    Returns JSON with flashcards array.
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Extract parameters
        student_version = data.get('student_version')
        num_flashcards = data.get('num_flashcards')
        subject = data.get('subject', '')
        grade = data.get('grade')
        
        if not student_version:
            return jsonify({
                "error": "Missing required parameter: student_version is required"
            }), 400
        
        if not num_flashcards:
            return jsonify({
                "error": "Missing required parameter: num_flashcards is required"
            }), 400
        
        # Validate num_flashcards
        try:
            num_flashcards = int(num_flashcards)
        except (ValueError, TypeError):
            return jsonify({
                "error": "num_flashcards must be a valid integer"
            }), 400
        
        if num_flashcards < 1 or num_flashcards > 50:
            return jsonify({
                "error": "num_flashcards must be between 1 and 50"
            }), 400
        
        print(f"Generating {num_flashcards} flashcards for {subject} grade {grade}")
        
        # Generate flashcards
        result = flashcards_service.generate_flashcards(
            student_version=student_version,
            num_flashcards=num_flashcards,
            subject=subject,
            grade=grade
        )
        
        if not result.get("success"):
            return jsonify({
                "error": result.get("error", "Failed to generate flashcards")
            }), 500
        
        # Return flashcards
        return jsonify({
            "success": True,
            "data": {
                "flashcards": result["flashcards"],
                "count": result["count"],
                "subject": result.get("subject", ""),
                "grade": result.get("grade")
            }
        }), 200
        
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
        print("\n" + "="*60)
        print("Romanian Education RAG API")
        print("="*60)
        print(f"Model: {Config.OPENAI_MODEL}")
        print(f"Embedding: {Config.OPENAI_EMBEDDING_MODEL}")
        print(f"Vector Store: {Config.VECTOR_STORE_PATH}")
        print("="*60 + "\n")
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        exit(1)
