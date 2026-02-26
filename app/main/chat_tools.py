import json
from flask_login import current_user
from app import db
from app.models import Classroom, Quiz, Question, Choice

def list_my_classrooms():
    """List classrooms owned by the current teacher user."""
    if current_user.role != 'teacher':
        return "Only teachers can list classrooms."
    
    classrooms = Classroom.query.filter_by(admin_id=current_user.id).all()
    if not classrooms:
        return "You don't have any classrooms yet."
    
    return json.dumps([
        {"id": c.id, "name": c.name, "join_code": c.join_code}
        for c in classrooms
    ])

def create_quiz_in_classroom(classroom_id, title, description, questions):
    """
    Create a quiz in a specific classroom.
    questions should be a list of dictionaries:
    [{"text": "...", "choices": [{"text": "...", "is_correct": bool}]}]
    """
    if current_user.role != 'teacher':
        return "Only teachers can create quizzes."
    
    classroom = Classroom.query.get(classroom_id)
    if not classroom or classroom.admin_id != current_user.id:
        return f"Classroom with ID {classroom_id} not found or you are not the admin."
    
    try:
        new_quiz = Quiz(
            title=title,
            description=description,
            author=current_user,
            classroom=classroom
        )
        db.session.add(new_quiz)
        db.session.flush() # Get the new_quiz.id
        
        for q_data in questions:
            new_q = Question(question_text=q_data['text'], quiz=new_quiz)
            db.session.add(new_q)
            db.session.flush()
            
            for c_data in q_data['choices']:
                new_c = Choice(
                    choice_text=c_data['text'],
                    is_correct=c_data['is_correct'],
                    question=new_q
                )
                db.session.add(new_c)
        
        db.session.commit()
        return f"Successfully created quiz '{title}' in classroom '{classroom.name}' with {len(questions)} questions."
    except Exception as e:
        db.session.rollback()
        return f"Error creating quiz: {str(e)}"

# Define tools for Groq
CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_my_classrooms",
            "description": "Returns a list of classrooms owned by the current teacher. Includes classroom ID, name, and join code.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_quiz_in_classroom",
            "description": "Creates a new quiz with multiple choice questions in a specific classroom.",
            "parameters": {
                "type": "object",
                "properties": {
                    "classroom_id": {
                        "type": "integer",
                        "description": "The ID of the classroom where the quiz will be created."
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the quiz."
                    },
                    "description": {
                        "type": "string",
                        "description": "A short description of the quiz."
                    },
                    "questions": {
                        "type": "array",
                        "description": "A list of questions, each with its text and a set of choices.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "The question text."},
                                "choices": {
                                    "type": "array",
                                    "description": "Exactly 4 choices for the question.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string", "description": "The choice text."},
                                            "is_correct": {"type": "boolean", "description": "Whether this choice is correct."}
                                        },
                                        "required": ["text", "is_correct"]
                                    },
                                    "minItems": 2,
                                    "maxItems": 4
                                }
                            },
                            "required": ["text", "choices"]
                        }
                    }
                },
                "required": ["classroom_id", "title", "questions"]
            },
        },
    }
]
