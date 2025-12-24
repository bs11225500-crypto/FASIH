from django.urls import path 
from . import views




app_name = 'patient'

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='dashboard'),
    path('profile/', views.patient_profile, name='profile'),
    path("sessions/", views.patient_sessions, name="sessions"),
    path("treatment-plan/",views.patient_treatment_plan,name="treatment_plan"),
    path("session-log/",views.patient_session_log,name="session_log"),
    path("session-notes/<int:session_id>/",views.session_note_detail,name="session_note_detail"),
    path("treatment/start-payment/",views.start_treatment_payment,name="start_treatment_payment"),
]

