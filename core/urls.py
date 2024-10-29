# urls.py
from django.urls import path
from .views import LandingPageView, CustomLoginView, SignUpView, OnboardingView, DashboardView

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]