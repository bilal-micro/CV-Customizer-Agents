"""
URL configuration for ats_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .authentication import (
    register_view,
    login_view,
    logout_view,
    profile_view,
    change_password_view
)
from .views import JobViewSet, ProcessRunViewSet, StageResultViewSet

app_name = 'ats_app'

# Create router for ViewSet endpoints
router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'process-runs', ProcessRunViewSet, basename='processrun')
router.register(r'stage-results', StageResultViewSet, basename='stageresult')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', profile_view, name='profile'),
    path('auth/change-password/', change_password_view, name='change_password'),
    # API endpoints (ViewSets)
    path('', include(router.urls)),
]
