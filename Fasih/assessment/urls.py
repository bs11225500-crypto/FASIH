from django.urls import path 
from . import views

app_name = 'assessment'

urlpatterns = [
    path('form/', views.assessment_form, name='form'),
    path("upload-audio/", views.upload_audio, name="upload_audio"),
    path("submit/", views.submit_assessment, name="submit_assessment"),
    path("detail/<int:id>/", views.assessment_detail, name="assessment_detail"),

]

