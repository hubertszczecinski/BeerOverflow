from flask import jsonify
from app.main import bp
from app.FaceRecognitionHandler import FaceRecognitionHandler
from app.models import User
from app.models import db

face_recognition_handler = FaceRecognitionHandler()

@bp.route('/example-data')
def seed():
    """Seed endpoint to create test user - returns JSON"""
    try:
        photo_to_save = face_recognition_handler.save_photo_to_db("images/3-df3eff42.jpg")
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            photo=photo_to_save
        )
        user.set_password("test12345")

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': {
                'username': user.username,
                'email': user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500

