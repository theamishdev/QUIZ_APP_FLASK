from datetime import datetime
import secrets
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for Students in Classrooms
classroom_members = db.Table('classroom_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    fullname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False, default='student') # 'teacher' or 'student'
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='author', lazy=True)
    results = db.relationship('Result', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # Classrooms owned by teacher
    owned_classrooms = db.relationship('Classroom', backref='admin', lazy=True, cascade="all, delete-orphan")
    
    # Classrooms joined by student
    joined_classrooms = db.relationship('Classroom', secondary=classroom_members, backref=db.backref('students', lazy='dynamic'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    join_code = db.Column(db.String(10), unique=True, nullable=False, default=lambda: secrets.token_hex(4).upper(), index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quizzes = db.relationship('Quiz', backref='classroom', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Classroom('{self.name}', Join Code: '{self.join_code}')"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=True)
    is_template = db.Column(db.Boolean, default=False)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('Result', backref='quiz', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Quiz('{self.title}', '{self.date_posted}')"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    choices = db.relationship('Choice', backref='question', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Question('{self.question_text[:30]}...')"

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f"Choice('{self.choice_text}', {self.is_correct})"

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    @property
    def percentage(self):
        """Calculate percentage score"""
        return round((self.score / self.total_questions * 100)) if self.total_questions > 0 else 0

    def __repr__(self):
        return f"Result(User {self.user_id}, Quiz {self.quiz_id}, Score {self.score}/{self.total_questions})"

