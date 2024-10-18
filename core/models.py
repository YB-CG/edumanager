from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Used to differentiate between teachers and admins (admins will have is_staff=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # These fields will be required when creating a superuser

    def __str__(self):
        return self.email


# Admin Model (Superuser)
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Any additional fields for Admin
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} (Admin)'

# Teacher Model (Normal User)
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Any additional fields for Teacher
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} (Teacher)'

# Study Model
class Study(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

# Student Model
class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='profiles/')
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    face_encoding = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Course Model
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    schedule = models.JSONField()

    def __str__(self):
        return self.name

# Attendance Model
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    marked_by = models.CharField(max_length=20, choices=[('Manual', 'Manual'), ('FaceRecognition', 'FaceRecognition')])

    def __str__(self):
        return f'{self.student} - {self.course} - {self.date}'

# Timetable Model
class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.course} - {self.day_of_week}'
