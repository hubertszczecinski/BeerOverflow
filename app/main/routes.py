from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.FaceRecognition import FaceRecognition
import cv2

face_recognition = FaceRecognition()

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
    photo = face_recognition.generate_img()
    img1 = cv2.resize(img1, (0, 0), fx=0.5, fy=0.5)
    print('time check')
    result = face_recognition.verify_face(img1, photo)
    return jsonify({"result": result})


@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('main/dashboard.html', title='Users dashboard', user=current_user)

