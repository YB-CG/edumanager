from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import User, School, Student, Course, Attendance
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class SchoolCreationForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('name', 'address', 'phone', 'website')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SchoolCreationForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('name', 'address', 'phone', 'website')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class TeacherCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        self.admin_user = kwargs.pop('admin_user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password("password")
        user.role = 'teacher'
        if self.admin_user:
            user.school = self.admin_user.school
        if commit:
            user.save()
        return user

class StudentForm(forms.ModelForm):
    # Multi-select field for courses
    courses = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
        })
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Enter email address'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            })
        }

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if school:
            # Filter courses by school
            self.fields['courses'].queryset = Course.objects.filter(school=school)
            # Customize the course display to show name and description
            self.fields['courses'].label_from_instance = lambda obj: f"{obj.name} - {obj.description}"

    def save(self, commit=True):
        student = super().save(commit=False)
        if commit:
            student.save()
            # Handle course assignments
            self.save_courses(student)
        return student

    def save_courses(self, student):
        if self.cleaned_data.get('courses'):
            student.courses.set(self.cleaned_data['courses'])

class CourseCreationForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=User.objects.none())
    
    class Meta:
        model = Course
        fields = ('name', 'description', 'teacher')
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='teacher', school=school)

class AttendanceFilterForm(forms.Form):
    PERIOD_CHOICES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('trimester', 'Trimester'),
        ('semester', 'Semester'),
    )
    
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    period = forms.ChoiceField(choices=PERIOD_CHOICES, required=False)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False)
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(school=school)