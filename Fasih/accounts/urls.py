from django.urls import path 
from . import views




app_name = 'accounts'

urlpatterns = [

    path('register/', views.register_account, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('post-login/', views.post_login_redirect, name='post_login_redirect'),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('complete/patient/', views.complete_patient_profile, name='complete_patient_profile'),
    path('complete/specialist/', views.complete_specialist_profile, name='complete_specialist_profile'),
    path('password-reset/',views.password_reset_request,name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/',views.password_reset_confirm,name='password_reset_confirm'),
    path('specialist/rejected/',views.specialist_rejected,name='specialist_rejected'),
    path('specialist/appeal/',views.specialist_appeal,name='specialist_appeal'),
    path('specialist/pending/',views.specialist_pending,name='specialist_pending'),

]

