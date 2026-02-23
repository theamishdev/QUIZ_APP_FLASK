# Quizify - Classroom Quiz Platform

A Flask-based web application for creating and managing classroom quizzes with role-based access (Teachers and Students).

## Features

- **User Authentication**: Secure login and registration with role-based access
- **Classroom Management**: Teachers can create classrooms and share join codes with students
- **Quiz Creation**: Easy-to-use interface for creating multiple-choice quizzes
- **Quiz Taking**: Students can take quizzes and get instant results with detailed feedback
- **Result Tracking**: View detailed results with correct/incorrect answers
- **Responsive Design**: Beautiful glassmorphism-style UI
- **Database**: SQLite (default) or other SQL databases

## Project Structure

```
PEP_PRO/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # Database models
│   ├── forms.py              # WTForms (for future use)
│   ├── auth/                 # Authentication routes
│   ├── quiz/                 # Quiz routes
│   ├── classroom/            # Classroom routes
│   ├── main/                 # Main routes
│   ├── static/               # CSS, JS, images
│   └── templates/            # HTML templates
├── instance/                 # Instance folder (database, etc.)
├── run.py                    # Application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── imp.txt                   # Documentation
```

## Setup Instructions

### 1. Prerequisites

- Python 3.7+
- pip (Python package manager)

### 2. Clone or Download Project

```bash
cd PEP_PRO
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and set your values (optional for development)
# FLASK_ENV=development
# SECRET_KEY=your-secret-key-here
```

### 6. Run the Application

```bash
python run.py
```

The application will be available at: `http://127.0.0.1:5000`

## Usage

### For Teachers

1. **Register**: Sign up with username, email, password, and select the "teacher" role
2. **Create Classroom**: Go to Classrooms → Create Classroom and enter a classroom name
3. **Share Join Code**: Copy the automatically generated join code and share with students
4. **Create Quizzes**: Enter the classroom and create quizzes with multiple-choice questions
5. **View Results**: Monitor student quiz submissions and view detailed results

### For Students

1. **Register**: Sign up with username, email, password, and select the "student" role
2. **Join Classroom**: Go to Classrooms → Join Classroom and enter the join code
3. **Take Quizzes**: View available quizzes in the classroom and take them
4. **View Results**: See immediate feedback with score and answer breakdowns

## Database Schema

### Users
- Stores user information with authentication
- Role-based access (teacher/student)
- Relationships to quizzes, results, and classrooms

### Classrooms
- Created by teachers
- Contains unique join codes for students
- Stores quizzes

### Quizzes
- Created by teachers within classrooms
- Contains multiple questions
- Linked to classrooms

### Questions & Choices
- Multiple-choice format
- One correct answer per question

### Results
- Stores student quiz attempts
- Contains score and date taken
- Links to user and quiz

## Important Notes

- **Security**: In production, always set a strong `SECRET_KEY` via environment variable
- **Database**: Default uses SQLite. For production, use PostgreSQL or MySQL
- **Session Security**: HTTP-only cookies enabled, CORS configured
- **Error Handling**: Comprehensive error handling for database and server errors

## Troubleshooting

### Database Issues
- Delete `instance/site.db` to reset the database
- Ensure `instance/` folder exists

### Port Already in Use
```bash
# Change the port in .env
FLASK_PORT=5001
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Development

### Enable Debug Mode
```bash
# In .env
FLASK_ENV=development
```

### Run Database Shell
```bash
python run.py shell
```

### Access Models in Shell
```python
from app.models import User, Quiz, Classroom
from app import db
```

## Production Deployment

1. Set `FLASK_ENV=production`
2. Use a production database (PostgreSQL/MySQL)
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set strong `SECRET_KEY`
5. Enable SSL/HTTPS

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Security Best Practices

- ✓ Password hashing with Werkzeug
- ✓ CSRF protection on forms
- ✓ SQL injection protection via SQLAlchemy ORM
- ✓ Session cookie security settings
- ✓ Role-based access control
- ✓ Authorization checks on protected routes

## Dependencies

- Flask: Web framework
- Flask-SQLAlchemy: ORM and database
- Flask-Login: User session management
- Werkzeug: Password hashing
- python-dotenv: Environment variable management

## License

This project is open-source and available for educational purposes.

## Support

For issues or questions, please refer to the project documentation or create an issue on GitHub.

---

**Version**: 1.0.0  
**Last Updated**: February 2026
