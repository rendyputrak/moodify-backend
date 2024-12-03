import cv2
import numpy as np
from keras.models import load_model
# from screeninfo import get_monitors

# # Get the screen resolution (for the primary monitor)
# monitor = get_monitors()[0]
# screen_width = monitor.width
# screen_height = monitor.height

# Load pre-trained model and face detection classifier
model = load_model('./FacialEmotion/moodify_fer2013_100.h5')
faceDetect = cv2.CascadeClassifier('./FacialEmotion/haarcascade_frontalface_default.xml')

# Dictionary to map label index to emotion
labels_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

# Array to store the percentages for each face detected
face_emotion_percentages = []

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
    label = np.argmax(result, axis=1)[0]
    
    # Get the probability for each class (as percentages)
    emotion_probabilities = result[0]
    total_probability = np.sum(emotion_probabilities)
    percentage_probabilities = (emotion_probabilities / total_probability) * 100

    # Save the percentage probabilities for the current face
    face_emotion_percentages.append(percentage_probabilities.tolist())

    # Draw bounding box around face
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
    cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)

    # Display predicted emotion and percentage
    cv2.putText(frame, labels_dict[label], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Start positioning the text to the right of the face
    text_x = x + w + 10  # Start position for the text to the right of the face
    text_y = y

    # Iterate over each emotion and display percentage next to the face
    for i, (emotion, prob) in enumerate(zip(labels_dict.values(), percentage_probabilities)):
        text = f"{emotion}: {prob:.2f}%"
        
        # Adjust font size dynamically based on the length of the text
        font_scale = 0.5 + len(text) * 0.02
        font_thickness = 1
        
        # Ensure text does not go out of bounds on the right side of the image
        if text_x + len(text) * 10 > frame.shape[1]:
            text_x = frame.shape[1] - len(text) * 10 - 10  # Move text to the left if it exceeds the image width
        
        # Measure the size of the text to create a background rectangle
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        
        # Create background rectangle (slightly larger than the text)
        background_top_left = (text_x, text_y + (i * 25) - text_height - 5)
        background_bottom_right = (text_x + text_width, text_y + (i * 25) + 5)
        cv2.rectangle(frame, background_top_left, background_bottom_right, (0, 0, 0), -1)  # Black background
        
        # Put the text on top of the background
        cv2.putText(frame, text, (text_x, text_y + (i * 25)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)

# Show the result
cv2.imshow("Frame", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Print or use the face_emotion_percentages array
print(face_emotion_percentages)
