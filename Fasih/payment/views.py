# payment/views.py

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Payment




def payment_page(request):
    return render(request, "payment/payment_page.html", {
        "moyasar_publishable_key": settings.MOYASAR_PUBLISHABLE_KEY
    })



def payment_callback(request):
    moyasar_payment_id = request.GET.get("id")

    if not moyasar_payment_id:
        return redirect("payment:payment_failed")  

    response = requests.get(
        f"https://api.moyasar.com/v1/payments/{moyasar_payment_id}",
        auth=(settings.MOYASAR_SECRET_KEY, "")
    )

    data = response.json()

    payment = Payment.objects.filter(
        user=request.user
    ).last()  

    if not payment:
        return redirect("payment:payment_failed")  

    payment.moyasar_payment_id = moyasar_payment_id

    if data.get("status") == "paid":
        payment.status = "paid"
        payment.save()
        return redirect("payment:payment_success")
    else:
        payment.status = "failed"
        payment.save()
        return redirect("payment:payment_failed")



def payment_success(request):
    return render(request, "payment/payment_success.html")


def payment_failed(request):
    return render(request, "payment/payment_failed.html")
