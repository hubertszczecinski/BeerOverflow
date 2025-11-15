from flask import jsonify, request, send_file
import io
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import bp
from app.models import User
from app.FaceRecognitionHandler import FaceRecognitionHandler
from datetime import datetime

face_recognition_handler = FaceRecognitionHandler()


@bp.route('/login', methods=['POST'])
def login():
    """API endpoint for user login - returns JSON"""
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user :
        return jsonify({'message': 'User doesn`t exist'}), 401
    if not user.check_password(password):
        return jsonify({'message': 'Invalid password'}), 401

    login_user(user, remember=remember_me)

    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    }), 200


@bp.route('/register', methods=['POST'])
def register():
    """API endpoint for user registration - accepts FormData (with photo)"""

    # Check if request is multipart (contains file upload)
    if request.content_type and 'multipart/form-data' in request.content_type:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        photo_file = request.files.get('photo')
    else:
        return jsonify({'message': 'No valid data provided'}), 400


    # Validation
    errors = []
    if not username or len(username) < 4 or len(username) > 20:
        errors.append('Username must be between 4 and 20 characters.')
    if not email or '@' not in email:
        errors.append('Please provide a valid email address.')
    if not first_name or not last_name:
        errors.append('First name and last name are required.')
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters long.')

    if errors:
        return jsonify({'message': '; '.join(errors)}), 400

    # Check for existing user
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'This username is already taken.'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'This email is already registered.'}), 409

    # Create new user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)

    # Handle photo
    try:
        photo_data = photo_file.read()
        user.photo = photo_data
    except Exception as e:
        return jsonify({'message': f'Error processing photo: {str(e)}'}), 400

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """API endpoint for user logout - returns JSON"""
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """API endpoint to get current authenticated user info"""
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name
        }
    }), 200

@bp.route('/photo', methods=['GET'])
@login_required
def get_my_photo():
    """Return the authenticated user's photo (requires login)."""
    if not current_user.photo:
        return jsonify({'message': 'Photo not found'}), 404
    return send_file(
        io.BytesIO(current_user.photo),
        mimetype='image/jpeg',
        as_attachment=False,
        download_name=f'{current_user.username}_photo.jpg'
    )