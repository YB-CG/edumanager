# services.py
import os
import pickle
from deepface import DeepFace
from django.conf import settings
from .models import Student, Attendance
from django.utils import timezone

class FaceRecognitionService:
    def __init__(self):
        self.db_path = os.path.join(settings.MEDIA_ROOT, 'student_faces')
        self.pickle_path = os.path.join(settings.MEDIA_ROOT, 'face_embeddings.pkl')
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

    def save_student_face(self, student, image_path):
        """Save student face and update embeddings"""
        # Save face image to database directory
        student_image_path = os.path.join(self.db_path, f'student_{student.id}.jpg')
        os.rename(image_path, student_image_path)
        
        # Update pickle file
        self.update_embeddings_pickle()
        
        return student_image_path

    def update_embeddings_pickle(self):
        """Update the pickle file with all face embeddings"""
        embeddings = {}
        
        # Get all students with profile pictures
        students = Student.objects.exclude(profile_picture='')
        
        for student in students:
            try:
                embedding = DeepFace.represent(
                    img_path=student.profile_picture.path,
                    model_name="VGG-Face"
                )
                embeddings[student.id] = {
                    'embedding': embedding,
                    'student_id': student.id,
                    'name': f"{student.first_name} {student.last_name}"
                }
            except Exception as e:
                print(f"Error processing student {student.id}: {str(e)}")
        
        # Save embeddings to pickle file
        with open(self.pickle_path, 'wb') as f:
            pickle.dump(embeddings, f)

    def find_face_match(self, frame_path, course_id):
        """Find matching face in database and mark attendance if found"""
        try:
            # Load embeddings from pickle
            with open(self.pickle_path, 'rb') as f:
                embeddings = pickle.load(f)
            
            # Get embedding for the captured frame
            frame_embedding = DeepFace.represent(
                img_path=frame_path,
                model_name="VGG-Face"
            )
            
            # Find closest match
            min_distance = float('inf')
            matched_student = None
            
            for student_id, data in embeddings.items():
                distance = DeepFace.verify(
                    img1_representation=frame_embedding,
                    img2_representation=data['embedding'],
                    model_name="VGG-Face",
                    distance_metric="cosine"
                )["distance"]
                
                if distance < min_distance and distance < 0.4:  # Threshold for matching
                    min_distance = distance
                    matched_student = student_id
            
            if matched_student:
                # Check if attendance already marked for today
                today = timezone.now().date()
                attendance_exists = Attendance.objects.filter(
                    student_id=matched_student,
                    course_id=course_id,
                    date=today
                ).exists()
                
                if not attendance_exists:
                    # Mark attendance
                    student = Student.objects.get(id=matched_student)
                    Attendance.objects.create(
                        student=student,
                        course_id=course_id,
                        date=today,
                        status='present'
                    )
                    return student.first_name, student.last_name
            
            return None, None
            
        except Exception as e:
            print(f"Error in face recognition: {str(e)}")
            return None, None