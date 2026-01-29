# backend/api/urls.py
"""
URL routing for the API endpoints.
Maps URLs to view functions.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dataset endpoints
    path('upload/', views.upload_csv, name='upload_csv'),
    path('dataset/<int:pk>/', views.get_dataset, name='get_dataset'),
    path('dataset/latest/', views.get_latest_dataset, name='get_latest_dataset'),
    path('dataset/<int:pk>/delete/', views.delete_dataset, name='delete_dataset'),
    
    # Summary and history
    path('summary/<int:pk>/', views.get_summary, name='get_summary'),
    path('history/', views.get_history, name='get_history'),
    
    # PDF generation
    path('pdf/<int:pk>/', views.download_pdf, name='download_pdf'),
    
    # Authentication
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/profile/', views.get_user_profile, name='profile'),
]