import os
import cv2
import base64
import pickle
import numpy as np
from deepface import DeepFace
from django.conf import settings
from django.utils import timezone
from .models import Student, Attendance
import logging

class FaceRecognitionService:
    def __init__(self):
        self.pickle_path = os.path.join(settings.MEDIA_ROOT, 'face_embeddings.pkl')
        self.face_cascade_path = os.path.join(settings.BASE_DIR, 'static', 'haarcascade_frontalface_default.xml')
        
        # Initialize face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_path)
        
        # Create necessary directories
        os.makedirs(os.path.dirname(self.pickle_path), exist_ok=True)
        
        # Initialize embeddings pickle file if it doesn't exist
        if not os.path.exists(self.pickle_path):
            self.save_empty_embeddings()
            
        # Load embeddings at initialization
        with open(self.pickle_path, 'rb') as f:
            self.embeddings = pickle.load(f)

    def save_empty_embeddings(self):
        with open(self.pickle_path, 'wb') as f:
            pickle.dump({}, f)

    def is_valid_image(self, image_path):
        """Check if the image is valid and contains a face"""
        try:
            if not os.path.exists(image_path):
                return False
            
            img = cv2.imread(image_path)
            if img is None:
                return False
            
            # Check if image is too small
            if img.shape[0] < 20 or img.shape[1] < 20:
                return False
            
            return True
        except Exception as e:
            logging.error(f"Error validating image {image_path}: {str(e)}")
            return False

    def process_frame(self, frame_data, course_id, user):
        """Process a frame from the video stream"""
        try:
            # Convert base64 frame to image
            try:
                frame_data = frame_data.split(',')[1]
                frame_bytes = base64.b64decode(frame_data)
                np_arr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    raise ValueError("Failed to decode frame")
            except Exception as e:
                logging.error(f"Error decoding frame: {str(e)}")
                return [], "Error: Invalid frame data"
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_results = []
            attendance_marked = False
            attendance_student = None
            
            # Process each detected face
            for (x, y, w, h) in faces:
                # Ensure face region is within frame bounds
                if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
                    continue
                
                face_img = frame[y:y+h, x:x+w]
                if face_img.size == 0:
                    continue
                
                temp_path = os.path.join(settings.MEDIA_ROOT, f'temp_face_{timezone.now().timestamp()}.jpg')
                try:
                    cv2.imwrite(temp_path, face_img)
                    
                    if not self.is_valid_image(temp_path):
                        logging.warning(f"Invalid face image saved at {temp_path}")
                        continue
                    
                    # Find best match among stored embeddings
                    best_match = None
                    best_confidence = 0
                    min_distance = float('inf')
                    
                    for student_id, data in self.embeddings.items():
                        try:
                            # Validate stored image path
                            if not self.is_valid_image(data['image_path']):
                                logging.warning(f"Invalid stored image for student {student_id}")
                                continue
                            
                            # Configure DeepFace for more robust detection
                            result = DeepFace.verify(
                                img1_path=temp_path,
                                img2_path=data['image_path'],
                                model_name="VGG-Face",
                                distance_metric="cosine",
                                detector_backend="opencv",
                                enforce_detection=False,
                                align=True
                            )
                            
                            logging.info(f"Verification result for student {student_id}: {result}")
                            
                            # Check if the face is verified and the distance is within threshold
                            if result.get("verified", False):  # Using get() to handle missing keys
                                distance = result.get("distance", float('inf'))
                                if distance < min_distance:
                                    min_distance = distance
                                    best_match = student_id
                                    best_confidence = ((0.68 - distance) / 0.68) * 100  # Using DeepFace's default threshold
                        except Exception as e:
                            logging.error(f"Verification error for student {student_id}: {str(e)}")
                            logging.error(f"Stack trace:", exc_info=True)
                            continue
                    
                    # Add face detection result
                    face_result = {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'matched': best_match is not None,
                        'confidence': best_confidence
                    }
                    
                    if best_match:
                        student = Student.objects.get(id=best_match)
                        face_result['student_name'] = f"{student.first_name} {student.last_name}"
                        
                        # Check if attendance already marked today
                        today = timezone.now().date()
                        attendance_exists = Attendance.objects.filter(
                            student=student,
                            course_id=course_id,
                            date=today
                        ).exists()
                        
                        # Mark attendance if not already marked
                        if not attendance_exists:
                            Attendance.objects.create(
                                student=student,
                                course_id=course_id,
                                date=today,
                                status='present',
                                marked_by=user
                            )
                            attendance_marked = True
                            attendance_student = student
                    
                    face_results.append(face_result)
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception as e:
                            logging.error(f"Error removing temp file {temp_path}: {str(e)}")
            
            # Prepare response
            message = None
            if attendance_marked:
                message = f'Attendance marked for {attendance_student.first_name} {attendance_student.last_name}'
            elif len(faces) > 0:
                message = 'Detecting faces...'
            
            return face_results, message
            
        except Exception as e:
            logging.error(f"Error processing frame: {str(e)}")
            logging.error("Stack trace:", exc_info=True)
            return [], f"Error: {str(e)}"

    def update_embeddings(self):
        """Update face embeddings for all students"""
        try:
            embeddings = {}
            students = Student.objects.exclude(profile_picture='')
            
            for student in students:
                try:
                    # Validate student's profile picture
                    if not self.is_valid_image(student.profile_picture.path):
                        logging.warning(f"Invalid profile picture for student {student.id}")
                        continue
                    
                    # Get embedding for student's profile picture
                    embedding = DeepFace.represent(
                        img_path=student.profile_picture.path,
                        model_name="VGG-Face",
                        detector_backend="opencv",
                        enforce_detection=False,
                        align=True
                    )
                    
                    embeddings[student.id] = {
                        'embedding': embedding,
                        'image_path': student.profile_picture.path,
                        'student_name': f"{student.first_name} {student.last_name}"
                    }
                except Exception as e:
                    logging.error(f"Error processing student {student.id}: {str(e)}")
                    logging.error("Stack trace:", exc_info=True)
                    continue
            
            # Save updated embeddings
            with open(self.pickle_path, 'wb') as f:
                pickle.dump(embeddings, f)
            
            self.embeddings = embeddings
            return True
            
        except Exception as e:
            logging.error(f"Error updating embeddings: {str(e)}")
            logging.error("Stack trace:", exc_info=True)
            return False