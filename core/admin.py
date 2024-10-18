from django.contrib import admin
from .models import Admin, Teacher, Student, Study, Course, Attendance, Timetable

admin.site.register(Admin)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Study)
admin.site.register(Course)
admin.site.register(Attendance)
admin.site.register(Timetable)
