from django.urls import path 
from . import views


app_name = 'specialist'

urlpatterns = [
    path("specialist_home/", views.specialist_home, name="specialist_home"),
    path("specialist_patients_dashboard/", views.specialist_patients_dashboard, name="specialist_patients_dashboard"),
    path("specialist_consultations_dashboard/",views.specialist_consultations_dashboard,name="specialist_consultations_dashboard"),
    path("choose-specialist/", views.choose_specialist, name="choose_specialist"),
    path("specialist_profile/", views.specialist_profile, name="specialist_profile"),
    path("certificates/add/",views.add_certificate,name="add_certificate"),
    path("certificates/<int:cert_id>/edit/", views.edit_certificate, name="edit_certificate"),
    path("certificates/<int:cert_id>/delete/", views.delete_certificate, name="delete_certificate"),
    path("specialist_sessions/",views.specialist_sessions,name="specialist_sessions"),
    
]

