from django.urls import path 
from . import views




app_name = 'accounts'

urlpatterns = [
    path('register/patient/',views.register_patient_account,name='register_patient_account'),
    path('register/patient/complete/',views.complete_patient_profile,name='complete_patient_profile'),
    path('register/specialist/',views.register_specialist_account,name='register_specialist_account'),
    path('register/specialist/complete/',views.complete_specialist_profile,name='complete_specialist_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('specialist/pending/', views.specialist_pending, name='specialist_pending'),
]

