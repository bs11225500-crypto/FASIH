from django.urls import path 
from . import views




app_name = 'specialist'

urlpatterns = [
    path("dashboard/", views.specialist_dashboard, name="dashboard"),

]

