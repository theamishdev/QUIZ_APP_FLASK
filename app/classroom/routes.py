from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from app import db
from app.models import Classroom, User

classroom = Blueprint('classroom', __name__)

@classroom.route("/classrooms")
@login_required
def list_classrooms():
    if current_user.role == 'teacher':
        classrooms = current_user.owned_classrooms
    else:
        classrooms = current_user.joined_classrooms
    return render_template('classroom/list.html', classrooms=classrooms, title='My Classrooms')

@classroom.route("/classroom/new", methods=['GET', 'POST'])
@login_required
def new_classroom():
    if current_user.role != 'teacher':
        abort(403)
    if request.method == 'POST':
        name = request.form.get('name')
        classroom_obj = Classroom(name=name, admin=current_user)
        db.session.add(classroom_obj)
        db.session.commit()
        flash('Classroom created!', 'success')
        return redirect(url_for('classroom.list_classrooms'))
    return render_template('classroom/create.html', title='New Classroom')

@classroom.route("/classroom/join", methods=['GET', 'POST'])
@login_required
def join_classroom():
    if current_user.role != 'student':
        abort(403)
    if request.method == 'POST':
        join_code = request.form.get('join_code').strip().upper()
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
    return render_template('classroom/join.html', title='Join Classroom')

@classroom.route("/classroom/<int:classroom_id>")
@login_required
def view_classroom(classroom_id):
    classroom_obj = Classroom.query.get_or_404(classroom_id)
    # Authorization check
    if current_user.role == 'teacher' and classroom_obj.admin != current_user:
        abort(403)
    if current_user.role == 'student' and classroom_obj not in current_user.joined_classrooms:
        abort(403)
        
    return render_template('classroom/view.html', classroom=classroom_obj, title=classroom_obj.name)
