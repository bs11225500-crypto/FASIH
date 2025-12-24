from django.urls import path 
from . import views




app_name = 'payment'

urlpatterns = [
    
        path("pay/", views.payment_page, name="payment_page"),
        path("callback/", views.payment_callback, name="payment_callback"),
        path("success/", views.payment_success, name="payment_success"),
        path("failed/", views.payment_failed, name="payment_failed"),


]

