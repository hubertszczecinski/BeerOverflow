from deepface import DeepFace
import cv2

class FaceRecognition:

    def save_photo_to_db(self, photo_path):
        with open(photo_path, 'rb') as file:
            binary_photo = file.read()
        return binary_photo

    def verify_face(self, frame, image):
        try:
            if DeepFace.verify(frame, image)['verified']:
                return True
        except ValueError as e:
            print(e)
        return False

    def blob_to_image_file(self, blob, filename="photo1.jpg"):
        if blob is None:
            print("No image in database")
            return None
        with open(filename, "wb") as f:
            f.write(blob[0])
        return filename

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