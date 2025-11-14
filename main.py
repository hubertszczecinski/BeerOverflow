from flask import Flask, render_template, jsonify
import cv2
from FaceRecognition import FaceRecognition

app = Flask(__name__)
face_recognition = FaceRecognition()

@app.route("/face-check")
def face_check():
    return render_template("test.html")

@app.route("/verify-face")
def verify_face():
    img1 = cv2.imread('images/1-df3eff42.jpg')
    img2 = cv2.imread('images/4-df3eff42.jpg')

    img1 = cv2.resize(img1, (0, 0), fx=0.5, fy=0.5)
    img2 = cv2.resize(img2, (0, 0), fx=0.5, fy=0.5)
    print('time check')
    result = face_recognition.verify_face(img1, img2)
    return jsonify({"result": result})

@app.route("/")
def index():
    return "Hello World"

if __name__ == "__main__":
    app.run(debug=True)