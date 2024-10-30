from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import User, School, Student, Course, Attendance

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
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set default password as "changeme123"
        user.set_password("changeme123")
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class StudentCreationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'courses')
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['courses'].queryset = Course.objects.filter(school=school)

class CourseCreationForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=User.objects.none())
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Course
        fields = ('name', 'description', 'teacher', 'students')
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='teacher', school=school)
        self.fields['students'].queryset = Student.objects.filter(school=school)

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