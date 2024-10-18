import cv2
from deepface import DeepFace
import numpy as np

# Load the target image and set age and gender
target_image_path = "test.png"
target_age = 22  # Set the actual age of the target person
target_gender = "Man"  # Set to "Man" or "Woman"

# Load the target image
target_img = cv2.imread(target_image_path)

# Initialize the video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect faces in the frame
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        
        try:
            # Perform facial recognition
            result = DeepFace.verify(face, target_img, model_name="VGG-Face")
            
            # Analyze age and gender
            analysis = DeepFace.analyze(face, actions=['age', 'gender', 'emotion'])
            
            # Get the predicted age and gender
            predicted_age = analysis[0]['age']
            predicted_gender = analysis[0]['dominant_gender']
            predicted_emotion = analysis[0]['dominant_emotion']
            
            # Determine if it's a match
            is_match = result['verified']
            
            # Draw rectangle around the face
            color = (0, 255, 0) if is_match else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Prepare text to display
            text = f"Match: {is_match}"
            cv2.putText(frame, text, (x, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            text = f"Age: {predicted_age:.0f} (Target: {target_age})"
            cv2.putText(frame, text, (x, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            text = f"Gender: {predicted_gender} (Target: {target_gender})"
            cv2.putText(frame, text, (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            text = f"Emotion: {predicted_emotion}"
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
        except Exception as e:
            print(f"Error processing face: {str(e)}")

    # Display the resulting frame
    cv2.imshow('Facial Recognition', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy windows
cap.release()
cv2.destroyAllWindows()