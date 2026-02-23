# Quick Start Guide - Quizify

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

## Installation & Running

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run.py
```

The app will start at: **http://127.0.0.1:5000**

### Step 3: Access the App
- Open your browser and go to `http://127.0.0.1:5000`
- Click "Register" to create an account
- Choose role: **Teacher** or **Student**

---

## Quick Test

### For Teachers:
1. Register as a teacher
2. Go to "Classrooms" → "Create Classroom"
3. Create a classroom (you'll get a join code)
4. Click "Create New Quiz"
5. Add questions and choices

### For Students:
1. Register as a student
2. Go to "Classrooms" → "Join Classroom"
3. Enter the join code from your teacher
4. Take available quizzes

---

## Database Management

### Initialize Database:
```bash
python manage_db.py init
```

### Add Sample Data:
```bash
python manage_db.py seed
```

### Reset Database (Warning: Deletes all data):
```bash
python manage_db.py reset
```

---

## Environment Variables

Edit `.env` file to customize:
```
FLASK_ENV=development
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///site.db
```

---

## Key Features Now Working

✓ User authentication (Teachers & Students)
✓ Classroom management with join codes
✓ Quiz creation and management
✓ Multiple-choice questions
✓ Instant results with feedback
✓ Input validation and error handling
✓ Responsive UI with glassmorphism design
✓ Database management tools
✓ Security improvements

---

## Troubleshooting

### Port Already in Use
- Change FLASK_PORT in .env file
- Or run: `python manage_db.py init` then `python run.py` on different terminal

### Database Issues
- Reset with: `python manage_db.py reset`
- Then seed: `python manage_db.py seed`

### Missing Dependencies
- Run: `pip install -r requirements.txt`

---

## Project Structure

```
PEP_PRO/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── utils.py
│   ├── auth/routes.py
│   ├── quiz/routes.py
│   ├── classroom/routes.py
│   ├── main/routes.py
│   ├── static/ (CSS, JS)
│   └── templates/ (HTML)
├── instance/ (Database)
├── run.py
├── config.py
├── manage_db.py
├── requirements.txt
└── README.md
```

---

## Need Help?

See `README.md` for detailed documentation.
Check `FIXES_SUMMARY.md` for all improvements made.

---

**Ready to run!** Execute `python run.py` now! 🚀
