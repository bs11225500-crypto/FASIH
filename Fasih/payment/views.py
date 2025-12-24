# payment/views.py

import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Payment
from treatment.models import TreatmentPlan





def payment_page(request):
    return render(request, "payment/payment_page.html", {
        "moyasar_publishable_key": settings.MOYASAR_PUBLISHABLE_KEY
    })

@login_required
def payment_callback(request):
    moyasar_payment_id = request.GET.get("id")

    if not moyasar_payment_id:
        return redirect("payment:payment_failed")

    response = requests.get(
        f"https://api.moyasar.com/v1/payments/{moyasar_payment_id}",
        auth=(settings.MOYASAR_PUBLISHABLE_KEY, "")
    )

    data = response.json()

    payment = Payment.objects.filter(
        user=request.user,
        status="pending"
    ).order_by("-created_at").first()

    if not payment:
        return redirect("payment:payment_failed")

    payment.moyasar_payment_id = moyasar_payment_id

    if data.get("status") == "paid":
        payment.status = "paid"
        payment.save()
       
        if payment.treatment_plan:
            payment.treatment_plan.status = TreatmentPlan.Status.ACTIVE
            payment.treatment_plan.save(update_fields=["status"])
            return redirect("payment:payment_success")

    payment.status = "failed"
    payment.save()
    return redirect("payment:payment_failed")




@login_required
def payment_success(request):
    if request.user.is_authenticated and hasattr(request.user, "patient_profile"):
        treatment_plan = TreatmentPlan.objects.filter(
            patient=request.user.patient_profile,
            status=TreatmentPlan.Status.DRAFT
        ).order_by("-created_at").first()


        if treatment_plan:
            treatment_plan.status = TreatmentPlan.Status.ACTIVE
            treatment_plan.save()

    return render(request, "payment/payment_success.html")


def payment_failed(request):
    return render(request, "payment/payment_failed.html")
