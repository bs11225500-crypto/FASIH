from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('specialist/<int:specialist_id>/rate/',views.rate_specialist,name='rate_specialist'),
]
