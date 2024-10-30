from django.contrib import admin
from .models import User, School, Course, Student, Attendance

admin.site.register(User)
admin.site.register(School)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Attendance)
