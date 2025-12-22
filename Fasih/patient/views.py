from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from datetime import date
from .models import Patient
from accounts.models import User
from accounts.forms import UserProfileForm, PatientProfileForm
from django.contrib import messages
from task.models import PatientTask
from session.models import Session
from treatment.models import TreatmentPlan
from assessment.models import Assessment




@login_required
def patient_dashboard(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect('main:home')

    try:
        patient = user.patient_profile
    except Patient.DoesNotExist:
        return redirect('accounts:complete_patient_profile')

    today_tasks_count = PatientTask.objects.filter(
        patient=patient,
        due_date=date.today(),
        status='pending'
    ).count()

    # جلسات بانتظار موافقة المريض
    pending_sessions = patient.sessions.filter(
        status=Session.Status.PROPOSED
    ).order_by("start_time")

    # جلسات مؤكدة
    confirmed_sessions = patient.sessions.filter(
        status=Session.Status.CONFIRMED
    ).order_by("start_time")

    # هل لدى المريض أي جلسات)
    has_sessions = pending_sessions.exists() or confirmed_sessions.exists()

    # أقرب جلسة مؤكدة 
    next_session = confirmed_sessions.first() if confirmed_sessions.exists() else None

    # الخطة العلاجية
    treatment_plan = TreatmentPlan.objects.filter(
        patient=patient
    ).order_by("-created_at").first()
    assessment = Assessment.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    # ✅ context يتعرّف مرة وحدة فقط
    context = {
        'patient': patient,
        'user': user,

        # مهام
        'today_tasks_count': today_tasks_count,
        'has_tasks': today_tasks_count > 0,

        # جلسات
        'pending_sessions': pending_sessions,
        'confirmed_sessions': confirmed_sessions,
        'has_sessions': has_sessions,
        'next_session': next_session,

        # خطة علاجية
        'treatment_plan': treatment_plan,
        'assessment': assessment,


        # نتركها للمستقبل
        'has_specialist': False,
    }

    return render(request, 'patient/dashboard.html', context)





@login_required
def patient_profile(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect('main:home')

    try:
        patient = user.patient_profile
    except Patient.DoesNotExist:
        return redirect('accounts:complete_patient_profile')

    edit_mode = request.GET.get("edit") == "1"
    latest_assessment = Assessment.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    if request.method == 'POST':
        user_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=user
        )
        patient_form = PatientProfileForm(
            request.POST,
            instance=patient
        )

        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, "تم تحديث البيانات بنجاح")
            return redirect('patient:profile')

        messages.error(request, "تأكد من صحة البيانات المدخلة")
        edit_mode = True  
    else:
        user_form = UserProfileForm(instance=user)
        patient_form = PatientProfileForm(instance=patient)
    assessment = Assessment.objects.filter(
    patient=patient
    ).order_by("-created_at").first()

    assessment_answers = assessment.assessment_data.get("sections_answers", {}) if assessment else {}
    assessment_images = assessment.assessment_data.get("images", []) if assessment else []


    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'patient': patient,
        'edit_mode': edit_mode, 
        'assessment': latest_assessment,
        "assessment": assessment,
        "assessment_answers": assessment_answers,
        "assessment_images": assessment_images,

    }

    return render(request, 'patient/profile.html', context)

@login_required
def patient_sessions(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect('main:home')

    patient = user.patient_profile

    assessment = Assessment.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    treatment_plan = TreatmentPlan.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    # ✅ الجلسة الاستشارية (تشمل PROPOSED و CONFIRMED)
    consultation_sessions = patient.sessions.filter(
        session_type=Session.SessionType.INITIAL
    ).order_by("start_time")

    # ✅ الجلسات العلاجية (غير الاستشارة)
    therapy_sessions = patient.sessions.exclude(
        session_type=Session.SessionType.INITIAL
    ).order_by("start_time")

    can_access_therapy_sessions = (
        treatment_plan is not None
        and treatment_plan.status == TreatmentPlan.Status.ACTIVE
    )

    context = {
        "assessment": assessment,
        "treatment_plan": treatment_plan,
        "consultation_sessions": consultation_sessions,
        "therapy_sessions": therapy_sessions,
        "can_access_therapy_sessions": can_access_therapy_sessions,
    }

    return render(request, "patient/sessions.html", context)


@login_required
def patient_treatment_plan(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect("main:home")

    patient = user.patient_profile

    treatment_plan = TreatmentPlan.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    assessment = Assessment.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    context = {
        "treatment_plan": treatment_plan,
        "assessment": assessment,   # ⭐ هذا السطر هو الحل
    }

    return render(
        request,
        "patient/treatment_plan.html",
        context
    )

