from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from specialist.models import Specialist
from accounts.models import User
from assessment.models import Assessment


@login_required
def specialist_home(request):

    if request.user.role != User.Role.SPECIALIST:
        return redirect("main:home")

    specialist = get_object_or_404(Specialist, user=request.user)

    if specialist.verification_status != Specialist.VerificationStatus.APPROVED:
        return redirect("accounts:specialist_pending")

    new_consultations_count = Assessment.objects.filter(
        specialist=specialist,
        status='PENDING'
    ).count()

    patients_count = Patient.objects.filter(
        assessments__specialist=specialist,
        assessments__status='ACCEPTED'
    ).distinct().count()

    sessions_count = 0  

    context = {
        "new_consultations_count": new_consultations_count,
        "patients_count": patients_count,
        "sessions_count": sessions_count,
    }

    return render(request, "specialist/specialist_home.html", context)

@login_required
def specialist_patients_dashboard(request):

    if request.user.role != User.Role.SPECIALIST:
        return redirect("main:home")

    specialist = get_object_or_404(Specialist, user=request.user)


    if specialist.verification_status != Specialist.VerificationStatus.APPROVED:
        return redirect("accounts:specialist_pending")


    patients = Patient.objects.filter(
        assessments__specialist=specialist,
        assessments__status='ACCEPTED'
    ).distinct()

    patients_data = []

    for patient in patients:
        patients_data.append({
            "id": patient.id,
            "name": patient.user.get_full_name(),
            "file_number": patient.file_number,
            "age": patient.age,
        })


    context = {
        "patients": patients_data
    }

    return render(request, "specialist/specialist_patients_dashboard.html", context)

def choose_specialist(request):
    specialists = Specialist.objects.filter(
        verification_status=Specialist.VerificationStatus.APPROVED
    )

    context = {
        "specialists": specialists
    }

    return render(request, "specialist/choose_specialist.html", context)

