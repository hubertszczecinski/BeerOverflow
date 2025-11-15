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
    photo_to_save = face_recognition.save_photo_to_db("images/hubert.jpg")
    user = User(
        username="chujchujchuj",
        email="chujchujchuj@chujchujchuj.com",
        first_name="chujchujchuj",
        last_name="chujchujchuj",
        photo=photo_to_save
    )
    user.set_password("chujchujchuj12345")

    db.session.add(user)
    db.session.commit()

    return "User created!"

@bp.route('/')
def index():
    return render_template('main/index.html', title='Main site')

@bp.route("/face-check")
@login_required
def face_check():
    return render_template("main/test.html")

@bp.route("/verify-face")
@login_required
def verify_face():
    frame = face_recognition.generate_img()
    if frame is None:
        return jsonify({"result": False, "reason": "Could not capture image from camera."})

    print("\n--- Rozpoczęcie weryfikacji twarzy ---")
    print(f"[*] Sprawdzanie użytkownika: {current_user.username} (ID: {current_user.id})")
    db_photo_blob = current_user.photo
    if db_photo_blob:
        db_photo_image = face_recognition.blob_to_cv2_image(db_photo_blob)
        result = face_recognition.verify_face(frame, db_photo_image)

        if result.get("verified"):
            print(f"[+] SUKCES: Twarz zweryfikowana dla {current_user.username} (dystans: {result.get('distance'):.2f})")
            print("--- Zakończenie weryfikacji ---")
            return jsonify({"result": True, "user": current_user.username})
        else:
            print(f"[-] BŁĄD: Brak dopasowania. Powód: {result.get('reason', 'Twarze nie są zgodne')}")

    print("--- Zakończenie weryfikacji: Nie udało się zweryfikować użytkownika ---")
    return jsonify({"result": False, "reason": "No matching user found."})


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html', title='Users dashboard', user=current_user)
