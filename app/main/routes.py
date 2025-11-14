from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.FaceRecognition import FaceRecognition
import cv2
from app.models import User
from app.models import db

face_recognition = FaceRecognition()

@bp.route('/example-data')
def seed():
    photo_to_save = face_recognition.save_photo_to_db("images/3-df3eff42.jpg")
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

    return "User created!"

@bp.route('/')
def index():
    """Home page"""
    return render_template('main/index.html', title='Main site')

@bp.route("/face-check")
def face_check():
    return render_template("main/test.html")

@bp.route("/verify-face")
def verify_face():
    img2 = cv2.imread('images/1-df3eff42.jpg')
    img1 = cv2.imread('images/3-df3eff42.jpg')
    users = User.query.all()
    for user in users:
        print(user.id, user.username, user.email)
    user = User.query.get(2)
    photo = user.get_user_photo(user.id)
    photo = face_recognition.blob_to_cv2_image(photo)
    frame = face_recognition.generate_img()
    print('time check')
    result = face_recognition.verify_face(photo, frame)
    return jsonify({"result": result})


@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('main/dashboard.html', title='Users dashboard', user=current_user)

