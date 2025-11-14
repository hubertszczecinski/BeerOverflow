from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import bp
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not username or not password:
            flash('Wypełnij wszystkie pola.', 'danger')
        else:
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember_me)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.dashboard')
                return redirect(next_page)
            
            flash('Uncorrect username or password.', 'danger')
    
    return render_template('auth/login.html', title='Login')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        
        
        errors = []
        if not username or len(username) < 4 or len(username) > 20:
            errors.append('Username must be between 4 and 20 characters.')
        if not email or '@' not in email:
            errors.append('Give correct email address.')
        if not first_name or not last_name:
            errors.append('File in name and secondname fields.')
        if not password or len(password) < 6:
            errors.append('Password must have at least 6 characters.')
        if password != password2:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            if User.query.filter_by(username=username).first():
                flash('This username is already taken.', 'danger')
            elif User.query.filter_by(email=email).first():
                flash('This email is already taken.', 'danger')
            else:
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('Registration successful. You can now log in.', 'success')
                return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Rejestracja')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

