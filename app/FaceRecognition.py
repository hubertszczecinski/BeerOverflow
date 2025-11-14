from deepface import DeepFace
import cv2
import numpy as np

class FaceRecognition:

    def save_photo_to_db(self, photo_path):
        with open(photo_path, 'rb') as file:
            binary_photo = file.read()
        return binary_photo

    def blob_to_cv2_image(self,blob):

        if blob is None:
            return None
        np_array = np.frombuffer(blob, dtype=np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img

    def verify_face(self, frame, image):
        try:
            if DeepFace.verify(frame, image)['verified']:
                return True
        except ValueError as e:
            print(e)
        return False

    def get_image_from_database(self):
        pass

    def generate_img(self, save_path="photo1.jpg"):
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not camera.isOpened():
            print("Camera is already in use or cannot be opened")
            camera.release()
            return None

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        success, frame = camera.read()

        if not success:
            print("Failed to capture image")
            camera.release()
            return None

        cv2.imwrite(save_path, frame)
        camera.release()

        return frame