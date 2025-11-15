import os
import requests


class FaceRecognitionHandler:
    def __init__(self, base_url: str | None = None, timeout: float = 15.0):
        # Default to the compose service name and internal port of the face API
        self.base_url = base_url or os.getenv("FACE_API_URL", "http://face-recognition:8000")
        self.timeout = timeout

    def save_photo_to_db(self, photo_path: str) -> bytes:
        with open(photo_path, "rb") as f:
            return f.read()

    def verify_face(self, image1: bytes, image2: bytes) -> bool:
        url = f"{self.base_url}/verify"
        files = {
            "image1": ("image1.jpg", image1, "image/jpeg"),
            "image2": ("image2.jpg", image2, "image/jpeg"),
        }
        try:
            resp = requests.post(url, files=files, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return bool(data.get("verified", False))
        except requests.RequestException:
            return False

    def get_image_from_database(self):
        pass

    # Camera access removed on purpose to de-bloat the container
    def generate_img(self, save_path: str = "photo1.jpg"):
        raise RuntimeError("Camera access has been removed from the backend container.")