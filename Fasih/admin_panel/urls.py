from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('specialists/', views.specialist_list, name='specialist_list'),
    path('specialists/<int:id>/', views.specialist_review, name='specialist_review'),
    path('specialists/<int:id>/approve/', views.approve_specialist, name='approve_specialist'),
    path('specialists/<int:id>/reject/', views.reject_specialist, name='reject_specialist'),
    path('messages/', views.contact_messages, name='contact_messages'),
    path('messages/<int:message_id>/read/',views.mark_message_read,name='mark_message_read'),



]
