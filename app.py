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
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize services
print("Initializing services...")
try:
    questions_service = QuestionsService()
    lecture_service = LectureService()
    print("✓ Services initialized successfully")
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
