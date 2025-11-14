from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from app.main import bp
from app.FaceRecognition import FaceRecognition
import cv2
from app.models import User, Forms
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

@bp.route('/forms')
def get_forms():
    return render_template('main/forms.html')

@bp.route("/autosave", methods=["POST"])
def autosave():
    data = request.get_json()
    entry = Forms.query.first()
    if not entry:
        entry = Forms()
        db.session.add(entry)

    for key, value in data.items():
        if hasattr(entry, key):
            setattr(entry, key, value)
    db.session.commit()
    return jsonify({"status": "saved"})

@bp.route("/load", methods=["GET"])
def load():
    entry = Forms.query.first()

    if not entry:
        return jsonify({})
    data = {
        "name": entry.name,
        "surname": entry.surname,
        "id_number": entry.id_number,
        "job": entry.job,
        "birthday": entry.birthday,
        "income": entry.income,
        "address": entry.address,
        "phone_number": entry.phone_number,
        "email": entry.email
    }
    return jsonify(data)

@bp.route("/delete", methods=["POST"])
def delete_data():
    data = request.get_json()
    id_number = data.get("id_number")

    if not id_number:
        return jsonify({"status": "error", "message": "id_number required"}), 400

    entry = Forms.query.filter_by(id_number=id_number).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"status": "deleted", "id_number": id_number})
    else:
        return jsonify({"status": "not found", "id_number": id_number}), 404