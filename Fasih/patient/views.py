from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from datetime import date
from .models import Patient
from accounts.models import User
from accounts.forms import UserProfileForm, PatientProfileForm
from django.contrib import messages
from task.models import PatientTask
from session.models import Session



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

    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'patient': patient,
        'edit_mode': edit_mode, 
    }

    return render(request, 'patient/profile.html', context)


@login_required
def patient_sessions(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect('main:home')

    patient = user.patient_profile

    pending_sessions = patient.sessions.filter(
        status=Session.Status.PROPOSED
    ).order_by("start_time")

    confirmed_sessions = patient.sessions.filter(
        status=Session.Status.CONFIRMED
    ).order_by("start_time")

    # هل اختار أخصائي (طلب استشارة)
    has_specialist = patient.sessions.exists()

    # هل أنهى الجلسة الاستشارية المجانية
    has_completed_initial_session = patient.sessions.filter(
        session_type=Session.SessionType.INITIAL,
        status=Session.Status.COMPLETED
    ).exists()

    return render(
        request,
        "patient/sessions.html",
        {
            "pending_sessions": pending_sessions,
            "confirmed_sessions": confirmed_sessions,
            "has_specialist": has_specialist,
            "has_completed_initial_session": has_completed_initial_session,
        }
    )
