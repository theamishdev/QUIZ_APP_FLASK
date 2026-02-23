from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from app import db
from app.models import Quiz, Question, Choice, Result, Classroom
from app.utils import sanitize_string

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
        title = sanitize_string(request.form.get('title', ''), 100)
        description = sanitize_string(request.form.get('description', ''), 1000)
        
        if not title:
            flash('Quiz title is required', 'danger')
            return render_template('quiz/create.html', title='New Quiz', classroom=classroom_obj)
        
        try:
            quiz_obj = Quiz(title=title, description=description, author=current_user, classroom=classroom_obj)
            db.session.add(quiz_obj)
            db.session.commit()
            
            flash('Quiz header created! Now add your questions.', 'success')
            return redirect(url_for('quiz.add_question', quiz_id=quiz_obj.id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating quiz. Please try again.', 'danger')
            
    return render_template('quiz/create.html', title='New Quiz', classroom=classroom_obj)

@quiz.route("/quiz/<int:quiz_id>/add_question", methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    if quiz_obj.author != current_user:
        abort(403)
        
    if request.method == 'POST':
        question_text = sanitize_string(request.form.get('question_text', ''), 500)
        if not question_text:
            flash('Question text is required', 'danger')
            return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)
        
        try:
            question = Question(question_text=question_text, quiz=quiz_obj)
            db.session.add(question)
            
            # Add choices
            choices = request.form.getlist('choices')
            correct_choice_index = request.form.get('correct_choice')
            
            # Validate choices
            if not choices or len(choices) < 2:
                flash('Please provide at least 2 choices', 'danger')
                return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)
            
            # Remove empty choices
            choices = [sanitize_string(c, 200) for c in choices if sanitize_string(c, 200)]
            
            if not choices:
                flash('Please provide valid choices', 'danger')
                return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)
            
            try:
                correct_choice_index = int(correct_choice_index)
                if correct_choice_index < 0 or correct_choice_index >= len(choices):
                    flash('Invalid correct choice selection', 'danger')
                    return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)
            except (ValueError, TypeError):
                flash('Please select a correct answer', 'danger')
                return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)
            
            # Add choices to database
            for i, choice_text in enumerate(choices):
                is_correct = (i == correct_choice_index)
                choice = Choice(choice_text=choice_text, is_correct=is_correct, question=question)
                db.session.add(choice)
                
            db.session.commit()
            flash('Question added!', 'success')
            
            if 'done' in request.form:
                return redirect(url_for('main.home'))
            return redirect(url_for('quiz.add_question', quiz_id=quiz_id))
        except Exception as e:
            db.session.rollback()
            flash('Error adding question. Please try again.', 'danger')
            
    return render_template('quiz/add_question.html', title='Add Question', quiz=quiz_obj)

@quiz.route("/quiz/<int:quiz_id>")
@login_required
def take_quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has access via classroom
    if quiz_obj.classroom:
        if current_user.role == 'teacher':
            if quiz_obj.classroom.admin != current_user:
                abort(403)
        else: # student
            if quiz_obj.classroom not in current_user.joined_classrooms:
                flash('You must be a member of the classroom to take this quiz.', 'danger')
                return redirect(url_for('classroom.view_classroom', classroom_id=quiz_obj.classroom.id))
    
    # Check if quiz has questions
    if not quiz_obj.questions:
        flash('This quiz has no questions yet.', 'warning')
        if quiz_obj.classroom:
            return redirect(url_for('classroom.view_classroom', classroom_id=quiz_obj.classroom.id))
        return redirect(url_for('main.home'))
    
    return render_template('quiz/take_quiz.html', title=quiz_obj.title, quiz=quiz_obj)

@quiz.route("/quiz/<int:quiz_id>/submit", methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has access via classroom
    if quiz_obj.classroom:
        if current_user.role == 'student' and quiz_obj.classroom not in current_user.joined_classrooms:
            abort(403)
        elif current_user.role == 'teacher' and quiz_obj.classroom.admin != current_user:
            abort(403)

    if not quiz_obj.questions:
        flash('This quiz has no questions.', 'danger')
        if quiz_obj.classroom:
            return redirect(url_for('classroom.view_classroom', classroom_id=quiz_obj.classroom.id))
        return redirect(url_for('main.home'))
    
    try:
        score = 0
        total = len(quiz_obj.questions)
        results_breakdown = []
        
        for question in quiz_obj.questions:
            selected_choice_id = request.form.get(f'question_{question.id}')
            selected_choice = None
            correct_choice = next((c for c in question.choices if c.is_correct), None)
            
            if selected_choice_id:
                try:
                    selected_choice = Choice.query.get(int(selected_choice_id))
                    if selected_choice and selected_choice.is_correct:
                        score += 1
                except (ValueError, TypeError):
                    pass
            
            results_breakdown.append({
                'question': question.question_text,
                'selected_choice': selected_choice.choice_text if selected_choice else 'No answer',
                'correct_choice': correct_choice.choice_text if correct_choice else 'N/A',
                'is_correct': selected_choice.is_correct if selected_choice else False
            })
        
        # Save result to database
        result = Result(score=score, total_questions=total, user=current_user, quiz=quiz_obj)
        db.session.add(result)
        db.session.commit()
        
        return render_template('quiz/result.html', title='Result', score=score, total=total, quiz=quiz_obj, results_breakdown=results_breakdown)
    except Exception as e:
        db.session.rollback()
        flash('Error submitting quiz. Please try again.', 'danger')
        return redirect(url_for('quiz.take_quiz', quiz_id=quiz_id))

@quiz.route("/quiz/<int:quiz_id>/delete", methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz_obj = Quiz.query.get_or_404(quiz_id)
    if quiz_obj.author != current_user:
        abort(403)
    
    try:
        classroom_id = quiz_obj.classroom_id
        db.session.delete(quiz_obj)
        db.session.commit()
        flash('Your quiz has been deleted!', 'success')
        if classroom_id:
            return redirect(url_for('classroom.view_classroom', classroom_id=classroom_id))
        return redirect(url_for('main.home'))
    except Exception as e:
        db.session.rollback()
        flash('Error deleting quiz. Please try again.', 'danger')
        if classroom_id:
            return redirect(url_for('classroom.view_classroom', classroom_id=classroom_id))
        return redirect(url_for('main.home'))


@quiz.route("/library")
@login_required
def library():
    if current_user.role != 'teacher':
        abort(403)
        
    classroom_id = request.args.get('classroom_id', type=int)
    classroom = None
    if classroom_id:
        classroom = Classroom.query.get_or_404(classroom_id)
        if classroom.admin != current_user:
            abort(403)
            
    templates = Quiz.query.filter_by(is_template=True).all()
    return render_template('quiz/library.html', title='Quiz Library', templates=templates, classroom=classroom)

@quiz.route("/quiz/import/<int:quiz_id>", methods=['POST'])
@login_required
def import_quiz(quiz_id):
    if current_user.role != 'teacher':
        abort(403)
        
    template_quiz = Quiz.query.get_or_404(quiz_id)
    if not template_quiz.is_template:
        flash('Invalid template quiz.', 'danger')
        return redirect(url_for('quiz.library'))
        
    classroom_id = request.form.get('classroom_id', type=int)
    if not classroom_id:
        flash('Please select a classroom to import the quiz to.', 'warning')
        return redirect(url_for('quiz.library'))
        
    classroom = Classroom.query.get_or_404(classroom_id)
    if classroom.admin != current_user:
        abort(403)
        
    try:
        # Clone the quiz
        new_quiz = Quiz(
            title=template_quiz.title,
            description=template_quiz.description,
            author=current_user,
            classroom=classroom,
            is_template=False
        )
        db.session.add(new_quiz)
        db.session.flush() # Get the new_quiz.id
        
        # Clone questions and choices
        for template_q in template_quiz.questions:
            new_q = Question(question_text=template_q.question_text, quiz=new_quiz)
            db.session.add(new_q)
            db.session.flush()
            
            for template_c in template_q.choices:
                new_c = Choice(
                    choice_text=template_c.choice_text,
                    is_correct=template_c.is_correct,
                    question=new_q
                )
                db.session.add(new_c)
        
        db.session.commit()
        flash(f'Successfully imported "{new_quiz.title}" to {classroom.name}!', 'success')
        return redirect(url_for('classroom.view_classroom', classroom_id=classroom.id))
        
    except Exception as e:
        db.session.rollback()
        flash('Error importing quiz. Please try again.', 'danger')
        return redirect(url_for('quiz.library', classroom_id=classroom_id))

