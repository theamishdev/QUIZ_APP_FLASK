from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from app import db
from app.models import Classroom, User
from app.utils import sanitize_string

classroom = Blueprint('classroom', __name__)

@classroom.route("/classrooms")
@login_required
def list_classrooms():
    try:
        if current_user.role == 'teacher':
            classrooms = current_user.owned_classrooms
        else:
            classrooms = current_user.joined_classrooms
        return render_template('classroom/list.html', classrooms=classrooms, title='My Classrooms')
    except Exception as e:
        flash('Error loading classrooms.', 'danger')
        return redirect(url_for('main.home'))

@classroom.route("/classroom/new", methods=['GET', 'POST'])
@login_required
def new_classroom():
    if current_user.role != 'teacher':
        abort(403)
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name', ''), 100)
        
        if not name:
            flash('Classroom name is required', 'danger')
            return render_template('classroom/create.html', title='New Classroom')
        
        try:
            classroom_obj = Classroom(name=name, admin=current_user)
            db.session.add(classroom_obj)
            db.session.commit()
            flash(f'Classroom "{name}" created! Share the code: {classroom_obj.join_code}', 'success')
            return redirect(url_for('classroom.list_classrooms'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating classroom. Please try again.', 'danger')
            
    return render_template('classroom/create.html', title='New Classroom')

@classroom.route("/classroom/join", methods=['GET', 'POST'])
@login_required
def join_classroom():
    if current_user.role != 'student':
        abort(403)
    if request.method == 'POST':
        join_code = sanitize_string(request.form.get('join_code', ''), 10).strip().upper()
        
        if not join_code:
            flash('Please enter a join code', 'danger')
            return render_template('classroom/join.html', title='Join Classroom')
        
        try:
            classroom_obj = Classroom.query.filter_by(join_code=join_code).first()
            if classroom_obj:
                if classroom_obj in current_user.joined_classrooms:
                    flash('You are already a member of this classroom.', 'info')
                else:
                    current_user.joined_classrooms.append(classroom_obj)
                    db.session.commit()
                    flash(f'Joined {classroom_obj.name}!', 'success')
                return redirect(url_for('classroom.list_classrooms'))
            else:
                flash('Invalid Join Code', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Error joining classroom. Please try again.', 'danger')
            
    return render_template('classroom/join.html', title='Join Classroom')

@classroom.route("/classroom/<int:classroom_id>")
@login_required
def view_classroom(classroom_id):
    classroom_obj = Classroom.query.get_or_404(classroom_id)
    
    # Authorization check
    if current_user.role == 'teacher':
        if classroom_obj.admin != current_user:
            abort(403)
    elif current_user.role == 'student':
        if classroom_obj not in current_user.joined_classrooms:
            abort(403)
    else:
        abort(403)
        
    return render_template('classroom/view.html', classroom=classroom_obj, title=classroom_obj.name)

