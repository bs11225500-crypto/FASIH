from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .models import Patient
from accounts.models import User
from accounts.forms import UserProfileForm, PatientProfileForm
from django.contrib import messages
from task.models import PatientTask
from session.models import Session
from treatment.models import TreatmentPlan
from assessment.models import Assessment
from django.core.paginator import Paginator
from payment.models import Payment
from treatment.models import calculate_treatment_price





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
    last_completed_session = patient.sessions.filter(status=Session.Status.COMPLETED).order_by("-start_time").first()


    # الخطة العلاجية
    treatment_plan = TreatmentPlan.objects.filter(
        patient=patient
    ).order_by("-created_at").first()
    assessment = Assessment.objects.filter(patient=patient).order_by("-created_at").first()
    linked_specialist = None

    has_active_treatment = (treatment_plan
    and treatment_plan.status == TreatmentPlan.Status.ACTIVE)


    first_session = patient.sessions.order_by("created_at").first()
    if first_session:
        linked_specialist = first_session.specialist

    elif assessment and hasattr(assessment, "specialist"):
        linked_specialist = assessment.specialist


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
        "linked_specialist": linked_specialist,
        "last_completed_session": last_completed_session,
        "has_active_treatment": has_active_treatment,
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
    assessment = Assessment.objects.filter(
    patient=patient
    ).order_by("-created_at").first()

    assessment_answers = assessment.assessment_data.get("sections_answers", {}) if assessment else {}
    assessment_images = assessment.assessment_data.get("images", []) if assessment else []
    last_completed_session = Session.objects.filter(patient=patient,session_type=Session.SessionType.INITIAL,status=Session.Status.COMPLETED).order_by("-start_time").first()



    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'patient': patient,
        'edit_mode': edit_mode, 
        "assessment": assessment,
        "assessment_answers": assessment_answers,
        "assessment_images": assessment_images,
        "last_completed_session": last_completed_session,


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

    #  الجلسة الاستشارية (تشمل PROPOSED و CONFIRMED)
    consultation_sessions = patient.sessions.filter(
        session_type=Session.SessionType.INITIAL
    ).order_by("start_time")

    #  الجلسات العلاجية (غير الاستشارة)
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

    treatment_price = None

    if treatment_plan and treatment_plan.status != TreatmentPlan.Status.ACTIVE:
        treatment_price = calculate_treatment_price(
            treatment_plan.duration_weeks
        )

    context = {
        "treatment_plan": treatment_plan,
        "assessment": assessment,
        "treatment_price": treatment_price,
    }

    return render(
        request,
        "patient/treatment_plan.html",
        context
    )



@login_required
def patient_session_log(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect("main:home")

    patient = user.patient_profile

    sessions_qs = patient.sessions.select_related(
        "specialist", "specialist__user"
    ).order_by("-start_time")

    paginator = Paginator(sessions_qs, 10)
    page_number = request.GET.get("page")
    sessions = paginator.get_page(page_number)

    context = {
        "sessions": sessions,  
    }

    return render(
        request,
        "patient/session_log.html",
        context
    )



@login_required
def session_note_detail(request, session_id):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect("main:home")

    patient = user.patient_profile

    session = get_object_or_404(
        Session,
        id=session_id,
        patient=patient,
        status=Session.Status.COMPLETED
    )

    if not hasattr(session, "note"):
        messages.info(request, "لم يتم إضافة ملاحظات لهذه الجلسة بعد")
        return redirect("patient:session_log")

    context = {
        "session": session,
        "note": session.note,
    }

    return render(
        request,
        "patient/session_note_detail.html",
        context
    )

@login_required
def start_treatment_payment(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect("main:home")

    patient = user.patient_profile

    treatment_plan = TreatmentPlan.objects.filter(
        patient=patient
    ).order_by("-created_at").first()

    if not treatment_plan or treatment_plan.status == TreatmentPlan.Status.ACTIVE:
        return redirect("patient:treatment_plan")

    amount = calculate_treatment_price(
        treatment_plan.duration_weeks
    )

    Payment.objects.create(
        user=user,
        amount=amount,
        status="pending"
    )

    return redirect("payment:payment_page")
