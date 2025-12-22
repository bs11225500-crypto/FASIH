from django.urls import path 
from . import views
from .views import create_treatment_plan
from .views import  treatment_plan_detail
from .views import add_short_term_goal



app_name = 'treatment'

urlpatterns = [
    
        path( "create/<str:file_number>/",create_treatment_plan,name="create_treatment_plan"),
        path("plan/<int:plan_id>/",treatment_plan_detail, name="treatment_plan_detail" ),
        path("plan/<int:plan_id>/goals/add/", add_short_term_goal, name="add_short_term_goal"),



]

