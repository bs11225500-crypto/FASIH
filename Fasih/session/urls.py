from django.urls import path 
from . import views




app_name = 'session'

urlpatterns = [
  path("create/", views.create_session, name="create_session"),
  path("<int:session_id>/", views.session_detail, name="session_detail"),
  path("<int:session_id>/join/", views.join_session, name="join_session"),
  



]

