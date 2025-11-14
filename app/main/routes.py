from flask import render_template
from flask_login import login_required, current_user
from app.main import bp


@bp.route('/')
def index():
    """Home page"""
    return render_template('main/index.html', title='Main site')


@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('main/dashboard.html', title='Users dashboard', user=current_user)

