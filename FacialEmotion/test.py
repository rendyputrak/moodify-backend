import cv2
import numpy as np
from keras.models import load_model

# Load the trained model
model = load_model('moodify_fer2013_100.h5')

# Initialize webcam
video = cv2.VideoCapture(0)

# Load the Haar Cascade for face detection
faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Define labels for the emotions
labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 3)

    for x, y, w, h in faces:
        # Extract the region of interest (face) in grayscale
        sub_face_img = gray[y:y + h, x:x + w]
        resized = cv2.resize(sub_face_img, (48, 48))
        normalize = resized / 255.0
        reshaped = np.reshape(normalize, (1, 48, 48, 1))

        # Get the model prediction (probabilities)
        result = model.predict(reshaped)
        
        # Calculate the label and its confidence score
        label = np.argmax(result, axis=1)[0]
        confidence = result[0][label] * 100  # Confidence in percentage

        # Display the prediction label with the highest confidence
        emotion = labels_dict[label]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)
        cv2.putText(frame, f'{emotion} ({confidence:.2f}%)', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Optionally, display the percentages of all emotions
        for i, (emotion, prob) in enumerate(zip(labels_dict.values(), result[0])):
            text = f'{emotion}: {prob * 100:.2f}%'
            cv2.putText(frame, text, (10, 30 + i * 25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show the video frame with the emotion predictions
    cv2.imshow("Emotion Detection", frame)
    
    # Exit condition
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

# Release the resources
video.release()
cv2.destroyAllWindows()
