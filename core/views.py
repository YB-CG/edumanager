# views.py
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import CreateView, UpdateView, ListView, TemplateView, View
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
    TeacherCreationForm, StudentCreationForm, CourseCreationForm,
    UserProfileForm, AttendanceFilterForm
)

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
        form.instance.admin = self.request.user
        return super().form_valid(form)

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('dashboard')
    
    def get_object(self):
        return self.request.user

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_template_names(self):
        if self.request.user.role == 'admin':
            return ['dashboard/admin/home.html']
        return ['dashboard/teacher/home.html']

# Teacher Management Views
class TeacherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/teacher_list.html'
    context_object_name = 'teachers'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_queryset(self):
        return User.objects.filter(role='teacher', school=self.request.user.school)

class TeacherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = TeacherCreationForm
    template_name = 'users/teacher_form.html'
    success_url = reverse_lazy('teacher_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

class TeacherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = TeacherCreationForm
    template_name = 'users/teacher_form.html'
    success_url = reverse_lazy('teacher_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

@login_required
def deactivate_teacher(request, pk):
    if request.user.role != 'admin':
        return HttpResponse(status=403)
    
    teacher = User.objects.get(pk=pk)
    teacher.is_active = False
    teacher.save()
    return redirect('teacher_list')

# Student Management Views
class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'teacher']
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Student.objects.filter(school=self.request.user.school)
        return Student.objects.filter(courses__teacher=self.request.user).distinct()

class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Student
    form_class = StudentCreationForm
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
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentCreationForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = self.request.user.school
        return kwargs

# Course Management Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Course.objects.filter(school=self.request.user.school)
        return Course.objects.filter(teacher=self.request.user)

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

# Attendance Management Views
class AttendanceMarkView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Attendance
    fields = ['student', 'status']
    template_name = 'attendance/mark_attendance.html'
    
    def test_func(self):
        return self.request.user.role == 'teacher'
    
    def form_valid(self, form):
        form.instance.course_id = self.kwargs['course_id']
        form.instance.date = timezone.now().date()
        form.instance.marked_by = self.request.user
        return super().form_valid(form)

class AttendanceCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now().date()
        
        if self.request.user.role == 'admin':
            courses = Course.objects.filter(school=self.request.user.school)
        else:
            courses = Course.objects.filter(teacher=self.request.user)
        
        attendance_data = Attendance.objects.filter(
            course__in=courses,
            date__month=current_date.month,
            date__year=current_date.year
        ).select_related('course', 'student')
        
        context.update({
            'courses': courses,
            'attendance_data': attendance_data,
            'current_date': current_date
        })
        return context

class DailyAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/daily_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get('date', timezone.now().date())
        
        if self.request.user.role == 'admin':
            courses = Course.objects.filter(school=self.request.user.school)
        else:
            courses = Course.objects.filter(teacher=self.request.user)
        
        attendance_data = Attendance.objects.filter(
            course__in=courses,
            date=date
        ).select_related('course', 'student')
        
        context.update({
            'attendance_data': attendance_data,
            'date': date,
            'courses': courses
        })
        return context

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
            
            if 'student_id' in kwargs:
                queryset = queryset.filter(student_id=kwargs['student_id'])
            
            context = {
                'attendance_records': queryset,
                'start_date': start_date,
                'end_date': end_date,
                'school': request.user.school,
                'generated_at': timezone.now(),
            }
            
            return render_to_pdf('reports/attendance_report.html', context)
        
        return HttpResponse("Invalid form data", status=400)