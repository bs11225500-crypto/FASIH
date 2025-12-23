from django.urls import path 
from . import views




app_name = 'task'

urlpatterns = [
    path('', views.daily_tasks, name='daily_tasks'),
    path("preview/<int:task_id>/", views.task_preview, name="task_preview"),
    path("task/<int:task_id>/execute/", views.task_execute, name="task_execute"),
    path("finish/<int:task_id>/", views.finish_task, name="finish_task"),
   

]

