from django.urls import path 
from . import views

app_name = 'assessment'

urlpatterns = [
    path('form/', views.assessment_form, name='form'),
]

