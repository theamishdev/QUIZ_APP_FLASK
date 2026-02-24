#!/usr/bin/env python
"""
Database management utility for Quizify
Provides commands for resetting, initializing, and managing the database
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import User, Classroom, Quiz, Question, Choice, Result

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def reset_db():
    """Drop all tables and recreate them"""
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        print("✓ Database reset successfully!")

def init_db():
    """Create database if it doesn't exist and run migrations."""
    print("Checking database configuration...")
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("✗ Error: DATABASE_URL not set")
        return

    from urllib.parse import urlparse, unquote
    p = urlparse(db_url)
    
    # Handle PostgreSQL creation
    if db_url.startswith('postgresql'):
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        username = unquote(p.username) if p.username else 'postgres'
        password = unquote(p.password) if p.password else 'postgres'
        host = p.hostname or 'localhost'
        port = p.port or 5432
        dbname = p.path.lstrip('/')
        
        print(f"Ensuring database '{dbname}' exists on {host}:{port}...")
        
        conn = None
        try:
            # Connect to default 'postgres' database
            conn = psycopg2.connect(
                user=username, 
                password=password, 
                host=host, 
                port=port, 
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            # Check if DB exists
            cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE \"{dbname}\"")
                print(f"✓ Database '{dbname}' created successfully")
            else:
                print(f"✓ Database '{dbname}' already exists")
            
        except Exception as e:
            print(f"✗ Database check/creation failed: {e}")
        finally:
            if conn:
                conn.close()

    print("Initializing tables...")
    from app import create_app, db
    import traceback
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database tables initialized successfully!")
        except Exception as e:
            print(f"✗ Error initializing tables: {e}")
            traceback.print_exc()
            raise e

def seed_db():
    """Add sample data for testing"""
    app = create_app()
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("Database already contains data. Skipping seed.")
            return
        
        from werkzeug.security import generate_password_hash
        
        print("Seeding database with sample data...")
        
        # Create sample users
        teacher = User(
            username='teacher1',
            email='teacher@example.com',
            password=generate_password_hash('password123'),
            fullname='John Teacher',
            role='teacher'
        )
        
        student = User(
            username='student1',
            email='student@example.com',
            password=generate_password_hash('password123'),
            fullname='Jane Student',
            role='student'
        )
        
        db.session.add_all([teacher, student])
        db.session.commit()
        
        # Create sample classroom
        classroom = Classroom(
            name='Python Basics',
            admin=teacher
        )
        db.session.add(classroom)
        db.session.commit()
        
        # Add student to classroom
        student.joined_classrooms.append(classroom)
        db.session.commit()
        
        # Create sample quiz
        quiz = Quiz(
            title='Python Fundamentals',
            description='A beginner-level quiz on Python basics',
            author=teacher,
            classroom=classroom
        )
        db.session.add(quiz)
        db.session.commit()
        
        # Add sample questions
        for i in range(2):
            question = Question(
                question_text=f'Sample Question {i+1}?',
                quiz=quiz
            )
            db.session.add(question)
            db.session.commit()
            
            # Add choices
            for j in range(4):
                choice = Choice(
                    choice_text=f'Option {j+1}',
                    is_correct=(j == 0),  # First option is correct
                    question=question
                )
                db.session.add(choice)
            db.session.commit()
        
        print("✓ Database seeded with sample data!")
        print(f"\nTest Credentials:")
        print(f"Teacher - Email: {teacher.email}, Password: password123")
        print(f"Student - Email: {student.email}, Password: password123")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [command]")
        print("\nAvailable commands:")
        print("  init    - Initialize database (create tables)")
        print("  reset   - Reset database (drop and recreate)")
        print("  seed    - Add sample data to database")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'init':
        init_db()
    elif command == 'reset':
        confirm = input("Are you sure you want to reset the database? (y/N): ")
        if confirm.lower() == 'y':
            reset_db()
        else:
            print("Cancelled.")
    elif command == 'seed':
        seed_db()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
