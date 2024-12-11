from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from models import Image, ExpressionAnalysis
from database import get_db
from API.user import get_current_user  # Fungsi untuk mendapatkan user dari token
import cv2
import numpy as np
import tensorflow as tf
import os
import shutil
from uuid import uuid4

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"

# Load the TensorFlow Lite model and face detector
interpreter = tf.lite.Interpreter(model_path='./FacialEmotion/model.tflite')
interpreter.allocate_tensors()

faceDetect = cv2.CascadeClassifier('./FacialEmotion/haarcascade_frontalface_default.xml')

# Directory for saving uploaded images
UPLOAD_DIR = "images/user-faces"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

detect_router = APIRouter()

@detect_router.post("/detect_and_upload", status_code=status.HTTP_201_CREATED)
async def detect_and_upload(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Ambil user dari token
):
    try:
        # Extract UserID from the current user
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")

        # Save the uploaded file to server disk
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Load the image and detect emotions
        frame = cv2.imread(file_path)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3, 3)
        if len(faces) == 0:
            os.remove(file_path)  # Remove the image if no face is detected
            raise HTTPException(status_code=404, detail="No faces detected")

        # Process the first detected face for simplicity
        (x, y, w, h) = faces[0]
        sub_face_img = gray[y:y + h, x:x + w]
        resized = cv2.resize(sub_face_img, (48, 48))
        normalize = resized / 255.0
        reshaped = np.reshape(normalize, (1, 48, 48, 1))

        # Use TensorFlow Lite to make predictions
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], reshaped.astype(np.float32))

        # Run inference
        interpreter.invoke()

        # Get the output tensor
        result = interpreter.get_tensor(output_details[0]['index'])
        label = int(np.argmax(result, axis=1)[0])
        emotion_probabilities = result[0]
        total_probability = np.sum(emotion_probabilities)
        percentage_probabilities = (emotion_probabilities / total_probability) * 100

        # Save the image information in the database
        db_image = Image(
            UserID=user_id,
            ImagePath=f"images/user-faces/{unique_filename}"
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        # Save emotion analysis in the database
        analysis = ExpressionAnalysis(
            UserID=user_id,
            ImageID=db_image.ImageID,
            MoodDetected=labels_dict[label],
            SadScore=float(percentage_probabilities[5]),
            AngryScore=float(percentage_probabilities[0]),
            HappyScore=float(percentage_probabilities[3]),
            DisgustScore=float(percentage_probabilities[1]),
            FearScore=float(percentage_probabilities[2]),
            SurpriseScore=float(percentage_probabilities[6]),
            NeutralScore=float(percentage_probabilities[4]),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "message": "Image uploaded and emotion detected successfully",
            "image": {"UserID": user_id, "ImagePath": db_image.ImagePath},
            "analysis": analysis,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
