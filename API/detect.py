from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import Image, ExpressionAnalysis
from database import get_db
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import requests

# Load pre-trained model and face detector
model = load_model('./FacialEmotion/moodify_fer2013_100.h5')
faceDetect = cv2.CascadeClassifier('./FacialEmotion/haarcascade_frontalface_default.xml')

# Dictionary to map index to emotion label
labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

detect_router = APIRouter()

# Helper function to detect emotions from an image URL
def detect_emotion_from_url(image_url: str) -> dict:
    try:
        # Mengunduh gambar dari URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Image URL is not reachable")
        
        # Membaca gambar dari konten yang diunduh
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # Decode image from bytes
        if frame is None:
            raise HTTPException(status_code=404, detail="Failed to read image from URL")
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale for face detection
        
        # Detect faces in the image
        faces = faceDetect.detectMultiScale(gray, 1.3, 3)
        if len(faces) == 0:  # No faces found in the image
            raise HTTPException(status_code=404, detail="No faces detected")
        
        results = []
        for (x, y, w, h) in faces:  # For each detected face
            sub_face_img = gray[y:y + h, x:x + w]
            resized = cv2.resize(sub_face_img, (48, 48))  # Resize to model input size
            normalize = resized / 255.0  # Normalize the image
            reshaped = np.reshape(normalize, (1, 48, 48, 1))  # Reshape for model input
            
            # Predict emotion probabilities
            result = model.predict(reshaped)
            label = int(np.argmax(result, axis=1)[0])  # Get the label with the highest probability
            
            emotion_probabilities = result[0]
            total_probability = np.sum(emotion_probabilities)
            percentage_probabilities = (emotion_probabilities / total_probability) * 100

            # Prepare emotion data
            emotion_data = {
                "MoodDetected": labels_dict[label],
                "SadScore": float(percentage_probabilities[5]),
                "AngryScore": float(percentage_probabilities[0]),
                "HappyScore": float(percentage_probabilities[3]),
                "DisgustScore": float(percentage_probabilities[1]),
                "FearScore": float(percentage_probabilities[2]),
                "SurpriseScore": float(percentage_probabilities[6]),
            }
            results.append(emotion_data)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image from URL: {str(e)}")

# Endpoint untuk mendeteksi emosi berdasarkan gambar dari ImageID
@detect_router.get("/detect_emotions/{image_id}")
def detect_image_emotion(image_id: int, db: Session = Depends(get_db)):
    # Fetch the image from the database
    image = db.query(Image).filter(Image.ImageID == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found in database")

    # Get the image URL from the database (assuming ImagePath stores the filename)
    image_url = f"http://127.0.0.1:8000/images/{image.ImagePath.split('/')[-1]}"  # Build the full image URL
    
    # Detect emotions from the image URL
    emotion_results = detect_emotion_from_url(image_url)

    # Save analysis in the database
    analysis = ExpressionAnalysis(
        UserID=image.UserID,
        ImageID=image.ImageID,
        MoodDetected=emotion_results[0]['MoodDetected'],
        SadScore=emotion_results[0]['SadScore'],
        AngryScore=emotion_results[0]['AngryScore'],
        HappyScore=emotion_results[0]['HappyScore'],
        DisgustScore=emotion_results[0]['DisgustScore'],
        FearScore=emotion_results[0]['FearScore'],
        SurpriseScore=emotion_results[0]['SurpriseScore'],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {"message": "Emotion detection successful", "analysis": analysis}

# Endpoint untuk mendeteksi emosi berdasarkan gambar terbaru dari ImageID
@detect_router.get("/detect_emotions/latest/{user_id}")
def detect_image_emotion(user_id: int, db: Session = Depends(get_db)):
    # Fetch the latest image for the user
    latest_image = db.query(Image).filter(Image.UserID == user_id).order_by(desc(Image.CreatedAt)).first()
    if not latest_image:
        raise HTTPException(status_code=404, detail="No image found for the user")

    # Get the image URL from the database (assuming ImagePath stores the filename)
    image_url = f"http://127.0.0.1:8000/images/{latest_image.ImagePath.split('/')[-1]}"  # Build the full image URL
    
    # Detect emotions from the image URL
    emotion_results = detect_emotion_from_url(image_url)

    # Save analysis in the database
    analysis = ExpressionAnalysis(
        UserID=latest_image.UserID,
        ImageID=latest_image.ImageID,
        MoodDetected=emotion_results[0]['MoodDetected'],
        SadScore=emotion_results[0]['SadScore'],
        AngryScore=emotion_results[0]['AngryScore'],
        HappyScore=emotion_results[0]['HappyScore'],
        DisgustScore=emotion_results[0]['DisgustScore'],
        FearScore=emotion_results[0]['FearScore'],
        SurpriseScore=emotion_results[0]['SurpriseScore'],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {"message": "Emotion detection successful", "analysis": analysis}
