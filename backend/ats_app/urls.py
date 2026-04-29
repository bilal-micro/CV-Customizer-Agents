"""
URL configuration for ats_app
"""
from django.urls import path
from .authentication import (
    register_view,
    login_view,
    logout_view,
    profile_view,
    change_password_view
)

app_name = 'ats_app'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', profile_view, name='profile'),
    path('auth/change-password/', change_password_view, name='change_password'),
]