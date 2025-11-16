"""
Flask Backend API for Romanian Education RAG System.
Provides endpoints for generating clarifying questions and lecture materials.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict
import traceback

from questions_service import QuestionsService
from lecture_service import LectureService
from presenton_service import PresentonService
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize services
print("Initializing services...")
try:
    questions_service = QuestionsService()
    lecture_service = LectureService()
    
    # Try to initialize Presenton service (optional)
    try:
        presenton_service = PresentonService()
        print("✓ Presenton service initialized successfully")
    except ValueError as e:
        presenton_service = None
        print(f"⚠ Presenton service not available: {e}")
    
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
