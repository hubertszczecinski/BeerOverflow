from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from deepface import DeepFace
import cv2
import numpy as np
from typing import Tuple
import tempfile
import os

app = FastAPI(title="Face Recognition Service")

def bytes_to_cv2_image(image_bytes: bytes) -> np.ndarray:
    """Convert bytes to OpenCV image"""
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image data")
    return img

@app.post("/verify")
async def verify_faces(
        image1: UploadFile = File(...),
        image2: UploadFile = File(...)
) -> JSONResponse:
    """Compare two face images and return whether they match
       Gracefully handles cases where one or both faces are not detectable.
    """

    # Create temporary files for DeepFace
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp1, \
            tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp2:

        try:
            # Read and write images to temp files
            img1_bytes = await image1.read()
            img2_bytes = await image2.read()

            tmp1.write(img1_bytes)
            tmp2.write(img2_bytes)
            tmp1.flush()
            tmp2.flush()

            try:
                # Verify faces using DeepFace
                # Use enforce_detection=False so DeepFace returns a dict with verified False
                # instead of throwing an exception when a face is not found.
                result = DeepFace.verify(tmp1.name, tmp2.name, enforce_detection=False)
            except Exception as inner_e:
                # Fallback: if DeepFace still raised, respond with a graceful failure
                return JSONResponse(content={
                    "verified": False,
                    "distance": None,
                    "threshold": None,
                    "reason": f"deepface_error: {str(inner_e)}"
                })

            # Additional sanity checks: if distance missing and verified False, likely face not detected.
            reason = None
            if not result.get("verified", False) and result.get("distance") is None:
                reason = "face_not_detected"

            return JSONResponse(content={
                "verified": result.get("verified", False),
                "distance": result.get("distance"),
                "threshold": result.get("threshold"),
                "reason": reason
            })

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Face verification failed: {str(e)}")

        finally:
            # Clean up temp files
            os.unlink(tmp1.name)
            os.unlink(tmp2.name)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
