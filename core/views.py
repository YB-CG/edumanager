# views.py
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, ListView, TemplateView, DetailView, DeleteView, View
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import timedelta
import io
from .models import User, Student, Course, Attendance
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, SchoolCreationForm,
    TeacherCreationForm, StudentForm, CourseCreationForm,
    UserProfileForm, AttendanceFilterForm
)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import FaceRecognitionService
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages

# Authentication Views
class LandingPageView(TemplateView):
    template_name = 'authentication/landing.html'

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')

class SignUpView(CreateView):
    template_name = 'authentication/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('onboarding')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.role = 'admin'
        self.object.save()
        login(self.request, self.object)
        return response

def sign_out(request):
    logout(request)
    return redirect('login')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'authentication/password_reset.html'
    email_template_name = 'authentication/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('login')

class OnboardingView(LoginRequiredMixin, CreateView):
    template_name = 'authentication/onboarding.html'
    form_class = SchoolCreationForm
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        school = form.save(commit=False)
        school.save()
        self.request.user.school = school
        self.request.user.save()
        return super().form_valid(form)

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_template_names(self):
        if self.request.user.role == 'admin':
            return ['dashboard/admin/home.html']
        return ['dashboard/teacher/home.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'admin':
            # Context data for admin dashboard
            school = user.school
            
            # Get base counts
            context['total_students'] = Student.objects.filter(school=school).count()
            context['total_teachers'] = User.objects.filter(
                school=school,
                role='teacher'
            ).count()
            context['total_courses'] = Course.objects.filter(school=school).count()
            
            # Get recent activities by combining latest users, courses, and students
            recent_teachers = User.objects.filter(
                school=school,
                role='teacher'
            ).order_by('-date_joined').values(
                'first_name', 'last_name', 'date_joined', 'email'
            )[:5]

            recent_courses = Course.objects.filter(
                school=school
            ).order_by('-created_at').values(
                'name', 'created_at', 'teacher__first_name', 'teacher__last_name'
            )[:5]

            recent_students = Student.objects.filter(
                school=school
            ).order_by('-created_at').values(
                'first_name', 'last_name', 'created_at', 'email'
            )[:5]

            # Combine all activities into a single list
            activities = []
            
            for teacher in recent_teachers:
                activities.append({
                    'type': 'teacher',
                    'description': f"New teacher {teacher['first_name']} {teacher['last_name']} ({teacher['email']}) joined",
                    'timestamp': teacher['date_joined'],
                    'user': {
                        'get_initials': f"{teacher['first_name'][0]}{teacher['last_name'][0]}",
                        'get_full_name': f"{teacher['first_name']} {teacher['last_name']}"
                    }
                })

            for course in recent_courses:
                teacher_name = (f"{course['teacher__first_name']} {course['teacher__last_name']}" 
                              if course['teacher__first_name'] and course['teacher__last_name'] 
                              else "Unassigned")
                activities.append({
                    'type': 'course',
                    'description': f"New course {course['name']} was created and assigned to {teacher_name}",
                    'timestamp': course['created_at'],
                    'user': {
                        'get_initials': 'C',
                        'get_full_name': course['name']
                    }
                })

            for student in recent_students:
                activities.append({
                    'type': 'student',
                    'description': f"New student {student['first_name']} {student['last_name']} ({student['email']}) was enrolled",
                    'timestamp': student['created_at'],
                    'user': {
                        'get_initials': f"{student['first_name'][0]}{student['last_name'][0]}",
                        'get_full_name': f"{student['first_name']} {student['last_name']}"
                    }
                })

            # Sort activities by timestamp and get the 10 most recent
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            context['recent_activities'] = activities[:10]
            
        else:
            # Teacher dashboard context (unchanged)
            today = timezone.now().date()
            teacher_courses = Course.objects.filter(teacher=user)
            
            teacher_students = Student.objects.filter(
                courses__in=teacher_courses
            ).distinct()
            
            context['my_students_count'] = teacher_students.count()
            context['my_courses_count'] = teacher_courses.count()
            
            context['todays_attendance_count'] = Attendance.objects.filter(
                course__in=teacher_courses,
                date=today
            ).count()
            
            context['recent_attendance'] = Attendance.objects.filter(
                course__in=teacher_courses
            ).select_related('student', 'course').order_by('-date')[:10]
            
        return context
    
# Teacher Management Views
class TeacherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/teacher_list.html'
    context_object_name = 'teachers'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_queryset(self):
        queryset = User.objects.filter(
            role='teacher',
            school=self.request.user.school
        )
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '')
        status = self.request.GET.get('status', 'all')
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Apply status filter
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', 'all')
        return context

class TeacherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = TeacherCreationForm
    template_name = 'users/teacher_form.html'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['admin_user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse('teacher_list') 

class TeacherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = TeacherCreationForm
    template_name = 'users/teacher_form.html'
    success_url = reverse_lazy('teacher_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

class TeacherDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('teacher_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

@login_required
def deactivate_teacher(request, pk):
    if request.user.role != 'admin':
        return HttpResponse(status=403)
    
    teacher = User.objects.get(pk=pk)
    teacher.is_active = not teacher.is_active 
    teacher.save()
    return redirect('teacher_list')

# Student Management Views
class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 9  # Show 9 students per page

    def test_func(self):
        return self.request.user.role in ['admin', 'teacher']

    def get_queryset(self):
        queryset = Student.objects.filter(school=self.request.user.school)
        
        # Filter by teacher's courses if user is a teacher
        if self.request.user.role == 'teacher':
            queryset = queryset.filter(courses__teacher=self.request.user).distinct()

        # Handle search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Handle course filter
        course_id = self.request.GET.get('course')
        if course_id:
            queryset = queryset.filter(courses__id=course_id)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add courses for filtering
        context['courses'] = Course.objects.filter(school=self.request.user.school)
        return context

class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs

    def form_valid(self, form):
        form.instance.school = self.request.user.school
        response = super().form_valid(form)
        messages.success(self.request, 'Student created successfully.')
        return response

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Student updated successfully.')
        return response

class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    success_url = reverse_lazy('student_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Student deleted successfully.')
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Override get method to prevent confirmation page
        return self.post(request, *args, **kwargs) 

# Course Management Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9  # Add pagination
    
    def get_queryset(self):
        queryset = Course.objects.filter(school=self.request.user.school)
        if self.request.user.role != 'admin':
            queryset = queryset.filter(teacher=self.request.user)
            
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # Teacher filter
        teacher_id = self.request.GET.get('teacher')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
            
        return queryset.select_related('teacher')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = User.objects.filter(
            school=self.request.user.school,
            role='teacher'
        )
        return context
    
class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseCreationForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs
    
    def form_valid(self, form):
        form.instance.school = self.request.user.school
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseCreationForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = self.object.students.all()
        return context

class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'base/confirm_delete.html'
    success_url = reverse_lazy('course_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

# Attendance Management Views

class AttendanceCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now().date()
        
        # Get courses based on user role
        if self.request.user.role == 'admin':
            courses = Course.objects.filter(school=self.request.user.school)
        else:
            courses = Course.objects.filter(teacher=self.request.user)
        
        # Get attendance data for the current month
        attendance_data = Attendance.objects.filter(
            course__in=courses,
            date__month=current_date.month,
            date__year=current_date.year
        ).select_related('course', 'student')
        
        # Format attendance data for the calendar
        calendar_data = {}
        for attendance in attendance_data:
            date_str = attendance.date.strftime('%Y-%m-%d')
            if date_str not in calendar_data:
                calendar_data[date_str] = {
                    'present': 0,
                    'total': 0,
                    'course_id': str(attendance.course.id),
                    'students': []
                }
            
            calendar_data[date_str]['total'] += 1
            if attendance.status == 'present':
                calendar_data[date_str]['present'] += 1
            
            calendar_data[date_str]['students'].append({
                'name': attendance.student.get_full_name(),
                'status': attendance.status,
                'attendance_id': attendance.id
            })
        
        context.update({
            'courses': courses,
            'attendance_data': calendar_data,
            'current_date': current_date
        })
        return context
    

class UpdateAttendanceView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ['teacher', 'admin']
    
    def post(self, request, attendance_id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status not in ['present', 'absent']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid status value'
                }, status=400)
            
            attendance = Attendance.objects.get(id=attendance_id)
            attendance.status = new_status
            attendance.save()
            
            return JsonResponse({
                'success': True,
                'status': attendance.status
            })
            
        except Attendance.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Attendance record not found'
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
                

# Report Generation Views
def get_date_range(period, start_date=None, end_date=None):
    today = timezone.now().date()
    
    if start_date and end_date:
        return start_date, end_date
    
    if period == 'weekly':
        start_date = today - timedelta(days=7)
    elif period == 'monthly':
        start_date = today.replace(day=1)
    elif period == 'trimester':
        start_date = today - timedelta(days=90)
    elif period == 'semester':
        start_date = today - timedelta(days=180)
    else:
        start_date = today
    
    return start_date, today

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class AttendanceReportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = AttendanceFilterForm(request.user.school, request.GET)
        
        if form.is_valid():
            start_date, end_date = get_date_range(
                form.cleaned_data['period'],
                form.cleaned_data['start_date'],
                form.cleaned_data['end_date']
            )
            
            queryset = Attendance.objects.filter(
                date__range=[start_date, end_date]
            )
            
            if 'course_id' in kwargs:
                queryset = queryset.filter(course_id=kwargs['course_id'])
            
            context = {
                'attendance_records': queryset,
                'start_date': start_date,
                'end_date': end_date,
                'school': request.user.school,
                'generated_at': timezone.now(),
            }
            
            return render_to_pdf('reports/attendance_report.html', context)
        
        return HttpResponse("Invalid form data", status=400)
    

@csrf_exempt
@login_required
def process_frame(request, course_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            frame_data = data.get('frame')
            
            face_service = FaceRecognitionService()
            face_results, message = face_service.process_frame(
                frame_data, 
                course_id,
                request.user
            )
            
            if message and "marked" in message: 
                messages.success(request, message)
            
            return JsonResponse({
                'success': True,
                'face_boxes': face_results,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def update_embeddings(request):
    """Endpoint to update all student face embeddings"""
    if request.method == 'POST':
        try:
            face_service = FaceRecognitionService()
            success = face_service.update_embeddings()
            
            if success:
                messages.success(request, 'Face embeddings updated successfully')
                return JsonResponse({
                    'success': True,
                    'message': 'Face embeddings updated successfully'
                })
            else:
                messages.error(request, 'Error updating face embeddings')
                return JsonResponse({
                    'success': False,
                    'message': 'Error updating face embeddings'
                })
        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })
