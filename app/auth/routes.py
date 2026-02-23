from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User
from app.utils import sanitize_string
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = sanitize_string(request.form.get('username', ''), 20).strip()
        email = sanitize_string(request.form.get('email', ''), 120).strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')

        # Validate role
        if role not in ['teacher', 'student']:
            role = 'student'

        # Validate inputs
        if not username:
            flash('Username is required', 'danger')
            return render_template('auth/register.html', title='Register')
        
        if len(username) < 2:
            flash('Username must be at least 2 characters', 'danger')
            return render_template('auth/register.html', title='Register')
        
        if not email:
            flash('Email is required', 'danger')
            return render_template('auth/register.html', title='Register')
        
        # Simple email validation
        if '@' not in email or '.' not in email:
            flash('Invalid email format', 'danger')
            return render_template('auth/register.html', title='Register')

        if not password:
            flash('Password is required', 'danger')
            return render_template('auth/register.html', title='Register')

        if len(password) < 4:
            flash('Password must be at least 4 characters', 'danger')
            return render_template('auth/register.html', title='Register')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html', title='Register')

        # Check for uniqueness
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template('auth/register.html', title='Register')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', title='Register')

        try:
            hashed_password = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_password, role=role)
            db.session.add(user)
            db.session.commit()
            print(f"✓ User created: {username} ({email})")
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError as e:
            db.session.rollback()
            print(f"✗ IntegrityError: {str(e)}")
            flash('Username or email already exists', 'danger')
            return render_template('auth/register.html', title='Register')
        except Exception as e:
            db.session.rollback()
            print(f"✗ Registration error: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('auth/register.html', title='Register')
            
    return render_template('auth/register.html', title='Register')

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        email = sanitize_string(request.form.get('email', ''), 120).strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return render_template('auth/login.html', title='Login')
        
        try:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user, remember=request.form.get('remember'))
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            flash('Error during login. Please try again.', 'danger')
    return render_template('auth/login.html', title='Login')

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        new_username = sanitize_string(request.form.get('username', ''), 20).strip()
        new_email = sanitize_string(request.form.get('email', ''), 120).strip().lower()
        new_fullname = sanitize_string(request.form.get('fullname', ''), 100)
        
        if not new_username:
            flash('Username is required', 'danger')
            return redirect(url_for('auth.account'))
        
        if not new_email:
            flash('Email is required', 'danger')
            return redirect(url_for('auth.account'))
        
        # Check if new username/email is already taken by others
        if new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username already taken', 'danger')
                return redirect(url_for('auth.account'))
        
        if new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('auth.account'))

        try:
            current_user.username = new_username
            current_user.email = new_email
            current_user.fullname = new_fullname
            db.session.commit()
            flash('Your account has been updated!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            print(f"✗ IntegrityError: {str(e)}")
            flash('Update failed. Username or email already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"✗ Account update error: {str(e)}")
            flash('Update failed. Please try again.', 'danger')
            
        return redirect(url_for('auth.account'))
    return render_template('auth/account.html', title='Account')
