from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from specialist.models import Specialist, SpecialistCertificate
from accounts.models import User
from assessment.models import Assessment
from accounts.models import User
from accounts.forms import UserProfileForm, SpecialistProfileForm
from django.contrib import messages


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

@login_required
def specialist_consultations_dashboard(request):
    specialist = get_object_or_404(Specialist, user=request.user)
    assessments = Assessment.objects.filter(
        status="PENDING",
        specialist=specialist
    ).select_related("patient", "patient__user")

    return render(request, "specialist/specialist_consultations_dashboard.html", {
        "assessments": assessments
    })


def choose_specialist(request):
    specialists = Specialist.objects.filter(
        verification_status=Specialist.VerificationStatus.APPROVED
    )

    context = {
        "specialists": specialists
    }

    return render(request, "specialist/choose_specialist.html", context)
@login_required
def specialist_profile(request):
    user = request.user

    if user.role != User.Role.SPECIALIST:
        return redirect('main:home')

    try:
        specialist = Specialist.objects.get(user=user)
    except Specialist.DoesNotExist:
        return redirect('main:home')

    edit_mode = request.GET.get("edit") == "1"

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        specialist_form = SpecialistProfileForm(request.POST, instance=specialist)

        if user_form.is_valid() and specialist_form.is_valid():
            user_form.save()
            specialist_form.save()
            messages.success(request, "تم تحديث البيانات بنجاح")
            return redirect('specialist:specialist_profile')
        else:
            messages.error(request, "تأكد من صحة البيانات المدخلة")
            edit_mode = True   
    else:
        user_form = UserProfileForm(instance=user)
        specialist_form = SpecialistProfileForm(instance=specialist)

    context = {
        'user': user,
        'specialist': specialist,
        'user_form': user_form,
        'specialist_form': specialist_form,
        'edit_mode': edit_mode,
    }

    return render(request, 'specialist/specialist_profile.html', context)




@login_required
def add_certificate(request):

    if request.user.role != User.Role.SPECIALIST:
        return redirect("main:home")

    specialist = get_object_or_404(Specialist, user=request.user)

    if request.method == "POST":
        form = SpecialistCertificate(request.POST, request.FILES)

        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.specialist = specialist
            certificate.save()

            messages.success(request, "تمت إضافة الشهادة بنجاح")
            return redirect("specialist:specialist_profile")

    else:
        form = SpecialistCertificate()

    return render(
        request,
        "specialist/add_certificate.html",
        {"form": form}
    )



