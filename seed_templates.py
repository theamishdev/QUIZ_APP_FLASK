from app import create_app, db
from app.models import User, Quiz, Question, Choice
from werkzeug.security import generate_password_hash
import os
try:
    from dotenv import load_dotenv
    # Explicitly load from current directory
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

def seed_templates():
    print(f"DATABASE_URL from env: {os.environ.get('DATABASE_URL')}")
    app = create_app()
    with app.app_context():
        # Ensure all tables are created (including new is_template column)
        db.create_all()

        # Create a system user if it doesn't exist
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            system_user = User(
                username='system',
                email='system@quizify.com',
                password=generate_password_hash('system_pass_123'),
                fullname='System Library',
                role='teacher'
            )
            db.session.add(system_user)
            db.session.commit()

        templates = [
            {
                'title': 'Python Basics',
                'description': 'Test your knowledge on Python syntax, variables, and loops.',
                'questions': [
                    {
                        'text': 'Which of the following is used to define a function in Python?',
                        'choices': [('def', True), ('function', False), ('func', False), ('define', False)]
                    },
                    {
                        'text': 'What is the correct way to create a list in Python?',
                        'choices': [('[]', True), ('{}', False), ('()', False), ('<>', False)]
                    },
                    {
                        'text': 'Which keyword is used for a loop that repeats while a condition is true?',
                        'choices': [('while', True), ('for', False), ('repeat', False), ('loop', False)]
                    }
                ]
            },
            {
                'title': 'JavaScript Fundamentals',
                'description': 'Core concepts of JavaScript, including ES6+ features.',
                'questions': [
                    {
                        'text': 'How do you declare a variable that cannot be reassigned?',
                        'choices': [('const', True), ('let', False), ('var', False), ('immutable', False)]
                    },
                    {
                        'text': 'What does DOM stand for?',
                        'choices': [('Document Object Model', True), ('Data Object Management', False), ('Digital Online Media', False), ('Desktop Object Mode', False)]
                    }
                ]
            },
            {
                'title': 'HTML & CSS Essentials',
                'description': 'The building blocks of the web.',
                'questions': [
                    {
                        'text': 'Which HTML tag is used for the largest heading?',
                        'choices': [('<h1>', True), ('<h6>', False), ('<head>', False), ('<header>', False)]
                    },
                    {
                        'text': 'Which CSS property is used to change the background color?',
                        'choices': [('background-color', True), ('color', False), ('bg-color', False), ('fill-color', False)]
                    }
                ]
            }
        ]

        for t in templates:
            # Check if template already exists
            if Quiz.query.filter_by(title=t['title'], is_template=True).first():
                continue
            
            quiz = Quiz(
                title=t['title'],
                description=t['description'],
                author=system_user,
                is_template=True
            )
            db.session.add(quiz)
            db.session.commit()

            for q in t['questions']:
                question = Question(question_text=q['text'], quiz=quiz)
                db.session.add(question)
                db.session.commit()

                for c_text, is_correct in q['choices']:
                    choice = Choice(choice_text=c_text, is_correct=is_correct, question=question)
                    db.session.add(choice)
                db.session.commit()

        print("✓ Technical quiz templates seeded successfully!")

if __name__ == '__main__':
    seed_templates()
