from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from app import db
from app.models import Quiz, Question, Choice, Result, Classroom

quiz = Blueprint('quiz', __name__)

@quiz.route("/quiz/new", methods=['GET', 'POST'])
@login_required
def new_quiz():
    if current_user.role != 'teacher':
        abort(403)
        
    classroom_id = request.args.get('classroom_id', type=int)
    if not classroom_id:
        flash('You must create a quiz within a classroom.', 'warning')
        return redirect(url_for('classroom.list_classrooms'))
        
    classroom_obj = Classroom.query.get_or_404(classroom_id)
    if classroom_obj.admin != current_user:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        quiz_obj = Quiz(title=title, description=description, author=current_user, classroom=classroom_obj)
        db.session.add(quiz_obj)
        db.session.commit()
        
        flash('Quiz header created! Now add your questions.', 'success')
        return redirect(url_for('quiz.add_question', quiz_id=quiz_obj.id))
        
    return render_template('quiz/create.html', title='New Quiz', classroom=classroom_obj)

@quiz.route("/quiz/<int:quiz_id>/add_question", methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    if quiz_obj.author != current_user:
        abort(403)
        
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question = Question(question_text=question_text, quiz=quiz_obj)
        db.session.add(question)
        
        # Add choices
        choices = request.form.getlist('choices')
        correct_choice_index = int(request.form.get('correct_choice'))
        
        for i, choice_text in enumerate(choices):
            is_correct = (i == correct_choice_index)
            choice = Choice(choice_text=choice_text, is_correct=is_correct, question=question)
            db.session.add(choice)
            
        db.session.commit()
        flash('Question added!', 'success')
        if 'done' in request.form:
             return redirect(url_for('main.home'))
        return redirect(url_for('quiz.add_question', quiz_id=quiz_id))
        
    return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)

@quiz.route("/quiz/<int:quiz_id>")
def take_quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz/take_quiz.html', title=quiz_obj.title, quiz=quiz_obj)

@quiz.route("/quiz/<int:quiz_id>/submit", methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    score = 0
    total = len(quiz_obj.questions)
    results_breakdown = []
    
    for question in quiz_obj.questions:
        selected_choice_id = request.form.get(f'question_{question.id}')
        selected_choice = None
        correct_choice = next((c for c in question.choices if c.is_correct), None)
        
        if selected_choice_id:
            selected_choice = Choice.query.get(int(selected_choice_id))
            if selected_choice and selected_choice.is_correct:
                score += 1
        
        results_breakdown.append({
            'question': question.question_text,
            'selected_choice': selected_choice.choice_text if selected_choice else 'No answer',
            'correct_choice': correct_choice.choice_text if correct_choice else 'N/A',
            'is_correct': selected_choice.is_correct if selected_choice else False
        })
                
    result = Result(score=score, total_questions=total, user=current_user, quiz=quiz_obj)
    db.session.add(result)
    db.session.commit()
    
    return render_template('quiz/result.html', title='Result', score=score, total=total, quiz=quiz_obj, results_breakdown=results_breakdown)

@quiz.route("/quiz/<int:quiz_id>/delete", methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    if quiz_obj.author != current_user:
        abort(403)
    
    classroom_id = quiz_obj.classroom_id
    db.session.delete(quiz_obj)
    db.session.commit()
    flash('Your quiz has been deleted!', 'success')
    if classroom_id:
        return redirect(url_for('classroom.view_classroom', classroom_id=classroom_id))
    return redirect(url_for('main.home'))
