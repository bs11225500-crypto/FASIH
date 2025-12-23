from django.urls import path 
from . import views
from .views import create_treatment_plan
from .views import  treatment_plan_detail
from .views import add_short_term_goal



app_name = 'treatment'

urlpatterns = [
        path("patients/",views.treatment_patients,name="treatment_patients"),
        path( "create/<str:file_number>/",create_treatment_plan,name="create_treatment_plan"),
        path("plan/<int:plan_id>/",treatment_plan_detail, name="treatment_plan_detail" ),
        path("plan/<int:plan_id>/goals/add/", add_short_term_goal, name="add_short_term_goal"),
        path("plan/<int:plan_id>/day/add/",views.add_daily_plan,name="add_daily_plan"),
        path("day/<int:day_id>/task/add/", views.add_daily_task,name="add_daily_task"),


]

