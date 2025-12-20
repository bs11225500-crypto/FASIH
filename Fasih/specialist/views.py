from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from specialist.models import Specialist
from accounts.models import User



def get_new_consultations_count():
    # TODO: Replace with DB query
    return 3

def get_patients_count():
    # TODO: Replace with DB query
    return 12

def get_upcoming_sessions_count():
    # TODO: Replace with DB query
    return 4

def specialist_home(request):
    # Temporary mock data until DB integration
    new_consultations_count = get_new_consultations_count()
    patients_count = get_patients_count()
    sessions_count = get_upcoming_sessions_count()

    context = {
        "new_consultations_count": new_consultations_count,
        "patients_count": patients_count,
        "sessions_count": sessions_count,
    }

    return render(request, "specialist/specialist_home.html", context)

@login_required
def specialist_patients_dashboard(request):

    # 1️⃣ تأكد إن المستخدم أخصائي
    if request.user.role != User.Role.SPECIALIST:
        return redirect("main:home")

    # 2️⃣ جلب سجل الأخصائي بشكل آمن
    specialist = get_object_or_404(Specialist, user=request.user)

    # 3️⃣ تأكد إن الأخصائي معتمد
    if specialist.verification_status != Specialist.VerificationStatus.APPROVED:
        return redirect("accounts:specialist_pending")

    # 4️⃣ جلب المرضى المرتبطين بهذا الأخصائي فقط
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
            "status": "جديد",  # الحالة الوحيدة الآن
        })


    context = {
        "patients": patients_data
    }

    return render(request, "specialist/patients_dashboard.html", context)
