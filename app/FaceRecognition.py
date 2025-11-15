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
            if frame is None:
                return {"verified": False, "reason": "Obraz z kamery jest pusty (None)."}
            if image is None:
                return {"verified": False, "reason": "Obraz z bazy danych jest pusty (None)."}

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


            result = DeepFace.verify(img1_path=frame_rgb, img2_path=image_rgb, model_name='SFace', enforce_detection=True)
            return {"verified": result['verified'], "distance": result['distance']}
        except Exception as e:
            return {"verified": False, "reason": str(e)}


    def get_image_from_database(self):
        pass

    def generate_img(self):
        camera = cv2.VideoCapture(0) 
        if not camera.isOpened():
            print("Camera at index 0 failed, trying index 1...")
            camera.release()
            camera = cv2.VideoCapture(1)

        if not camera.isOpened():
            print("Could not open any camera. Please check camera permissions and connections.")
            camera.release()
            return None

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


        frame = None
        for _ in range(15):
            success, frame = camera.read()
        
        if not success or frame is None:
            print("Failed to capture image after multiple attempts.")
            camera.release()
            return None

        camera.release()
        return frame