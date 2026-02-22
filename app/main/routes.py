from flask import render_template, Blueprint
from app.models import Quiz

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    quizzes = Quiz.query.order_by(Quiz.date_posted.desc()).all()
    return render_template('home.html', quizzes=quizzes)

@main.route("/about")
def about():
    return render_template('about.html', title='About')
