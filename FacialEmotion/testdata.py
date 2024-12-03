import cv2
import numpy as np
import requests
from keras.models import load_model

# Load pre-trained model and face detection classifier
model = load_model('./FacialEmotion/moodify_fer2013_100.h5')
faceDetect = cv2.CascadeClassifier('./FacialEmotion/haarcascade_frontalface_default.xml')

# API endpoint
API_URL = "http://127.0.0.1:8000/expression_analysis/"  # Sesuaikan URL API sesuai kebutuhan

# Dictionary to map label index to emotion
labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

# Placeholder user and image IDs (sesuaikan dengan data nyata)
USER_ID = 12
IMAGE_ID = 6

# Read input image
frame = cv2.imread("./FacialEmotion/angry.jpg")
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Detect faces
faces = faceDetect.detectMultiScale(gray, 1.3, 3)
for x, y, w, h in faces:
    sub_face_img = gray[y:y + h, x:x + w]
    resized = cv2.resize(sub_face_img, (48, 48))  # Resize the image to match input size of the model
    normalize = resized / 255.0  # Normalize pixel values
    reshaped = np.reshape(normalize, (1, 48, 48, 1))  # Reshape to (1, 48, 48, 1) for model input

    # Predict emotion probabilities
    result = model.predict(reshaped)
    
    # Get the class with the highest probability
    label = int(np.argmax(result, axis=1)[0])  # Convert NumPy int64 to Python int
    
    # Get the probability for each class (as percentages)
    emotion_probabilities = result[0]
    total_probability = np.sum(emotion_probabilities)
    percentage_probabilities = (emotion_probabilities / total_probability) * 100

    # Prepare data for API
    analysis_data = {
        "UserID": USER_ID,
        "ImageID": IMAGE_ID,
        "MoodDetected": labels_dict[label],  # Nama label dengan persentase tertinggi
        "SadScore": float(percentage_probabilities[5]),
        "AngryScore": float(percentage_probabilities[0]),
        "HappyScore": float(percentage_probabilities[3]),
        "DisgustScore": float(percentage_probabilities[1]),
        "FearScore": float(percentage_probabilities[2]),
        "SurpriseScore": float(percentage_probabilities[6])
    }

    # Send data to API
    try:
        response = requests.post(API_URL, json=analysis_data)
        if response.status_code == 201:
            print("Data berhasil dikirim ke API:", response.json())
        else:
            print(f"Failed to send data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error saat mengirim data ke API: {e}")

    # Draw bounding box around face
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
    cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)

    # Display predicted emotion
    cv2.putText(frame, labels_dict[label], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# Show the result
cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
