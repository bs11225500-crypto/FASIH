from django.urls import path 
from . import views




app_name = 'patient'

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('profile/', views.patient_profile, name='profile'),


]

