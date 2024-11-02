# urls.py - Complete URL Patterns
from django.urls import path
from .views import (
    LandingPageView, CustomLoginView, SignUpView, OnboardingView, DashboardView,
    CustomPasswordResetView, CustomPasswordResetConfirmView, sign_out, deactivate_teacher,
    UserProfileView, TeacherListView, TeacherCreateView, TeacherUpdateView, TeacherDeleteView,
    StudentListView, StudentCreateView, StudentUpdateView, StudentDeleteView,
    CourseListView, CourseCreateView, CourseUpdateView, CourseDetailView, CourseDeleteView,
    AttendanceMarkView, AttendanceCalendarView, DailyAttendanceView,
    AttendanceReportView, process_frame, update_embeddings,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication URLs
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', sign_out, name='logout'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Teacher Management URLs
    path('teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/update/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/<int:pk>/deactivate/', deactivate_teacher, name='teacher_deactivate'),
    path('teachers/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),
    
    # Student Management URLs
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    
    # Course Management URLs
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/create/', CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/update/', CourseUpdateView.as_view(), name='course_update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    
    # Attendance Management URLs
    path('attendance/calendar/', AttendanceCalendarView.as_view(), name='attendance_calendar'),
    path('attendance/daily/', DailyAttendanceView.as_view(), name='daily_attendance'),
    path('courses/<int:course_id>/attendance/', AttendanceMarkView.as_view(), name='mark_attendance'),
       path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),

    # Report URLs
    path('reports/attendance/', AttendanceReportView.as_view(), name='attendance_report'),
    path('reports/attendance/course/<int:course_id>/', 
         AttendanceReportView.as_view(), name='course_attendance_report'),
    path('reports/attendance/student/<int:student_id>/', 
         AttendanceReportView.as_view(), name='student_attendance_report'),
    path('reports/attendance/student/<int:student_id>/course/<int:course_id>/', 
         AttendanceReportView.as_view(), name='student_course_attendance_report'),
     path('process-frame/<int:course_id>/', process_frame, name='process_frame'),
     path('update-embeddings/', update_embeddings, name='update_embeddings'),
]