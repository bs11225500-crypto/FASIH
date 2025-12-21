from django.urls import path 
from . import views




app_name = 'task'

urlpatterns = [
path('', views.daily_tasks, name='daily_tasks'),


]

