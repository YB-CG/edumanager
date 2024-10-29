# authentication/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .forms import SchoolCreationForm


class LandingPageView(TemplateView):
    template_name = 'authentication/landing.html'

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

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

class OnboardingView(CreateView):
    template_name = 'authentication/onboarding.html'
    form_class = SchoolCreationForm
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        form.instance.admin = self.request.user
        return super().form_valid(form)

class DashboardView(TemplateView):
    template_name = 'dashboard/admin/home.html'