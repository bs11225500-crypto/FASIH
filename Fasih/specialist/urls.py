from django.urls import path 
from . import views


app_name = 'specialist'

urlpatterns = [
    path("specialist_home/", views.specialist_home, name="specialist_home"),
    path("specialist_patients_dashboard/", views.specialist_patients_dashboard, name="specialist_patients_dashboard"),
    path("choose-specialist/", views.choose_specialist, name="choose_specialist"),
]

