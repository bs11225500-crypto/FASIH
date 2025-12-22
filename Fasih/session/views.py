from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.utils import timezone


from patient.models import Patient
from .models import Session


@login_required
def create_session(request, file_number):
    if not hasattr(request.user, "specialist"):
        return redirect("main:home")

    patient = get_object_or_404(Patient, file_number=file_number)

    if request.method == "POST":
        title = request.POST.get("title")
        session_type = request.POST.get("session_type")

        start_time = timezone.make_aware(
            datetime.fromisoformat(request.POST.get("start_time"))
        )
        end_time = timezone.make_aware(
            datetime.fromisoformat(request.POST.get("end_time"))
        )

        # جلسة استشارية
        if session_type == Session.SessionType.INITIAL:
            status = Session.Status.PROPOSED

        # جلسة علاجية
        elif session_type == Session.SessionType.TREATMENT:
            from treatment.models import TreatmentPlan

            treatment_plan = TreatmentPlan.objects.filter(
                patient=patient,
                status=TreatmentPlan.Status.ACTIVE
            ).first()

            if not treatment_plan:
                messages.error(
                    request,
                    "لا يمكن إنشاء جلسة علاجية قبل اعتماد الخطة العلاجية"
                )
                return redirect(request.path)

            status = Session.Status.CONFIRMED

        else:
            messages.error(request, "نوع جلسة غير صالح")
            return redirect(request.path)

        session = Session.objects.create(
            patient=patient,
            specialist=request.user.specialist,
            title=title,
            start_time=start_time,
            end_time=end_time,
            session_type=session_type,
            status=status
        )

        messages.success(request, "تم إنشاء الجلسة بنجاح ")
        return redirect("session:session_detail", session.id)

    return render(
        request,
        "session/create_session.html",
        {
            "patient": patient
        }
    )


@login_required
def session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    return render(
        request,
        "session/session_detail.html",
        {
            "session": session,
            "can_join": session.can_join(),
        }
    )



@login_required
def join_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    # لازم الجلسة مؤكدة
    if session.status != Session.Status.CONFIRMED:
        return render(
            request,
            "session/session_not_started.html",
            {"session": session}
        )

    # إذا المستخدم أخصائي
    if hasattr(request.user, "specialist"):
        session.specialist_joined = True
        session.save()

        return render(
            request,
            "session/meet.html",
            {"session": session}
        )

    # إذا المستخدم مريض
    if hasattr(request.user, "patient"):
        if not session.specialist_joined:
            messages.info(
                request,
                "يرجى انتظار دخول الأخصائي لبدء الجلسة"
            )
            return redirect("patient:sessions")

        return render(
            request,
            "session/meet.html",
            {"session": session}
        )

    return redirect("main:home")


@login_required
def respond_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if not hasattr(request.user, "patient_profile"):
        return redirect("main:home")

    if request.user.patient_profile != session.patient:
        return redirect("main:home")

    if session.status != Session.Status.PROPOSED:
        messages.error(request, "تم التعامل مع هذه الجلسة مسبقًا")
        return redirect("patient:sessions")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            session.status = Session.Status.CONFIRMED
            messages.success(request, "تم تأكيد الجلسة بنجاح ")

        elif action == "reject":
            session.status = Session.Status.REJECTED
            session.patient_response_reason = request.POST.get("reason")
            session.patient_suggested_times = request.POST.get("suggested_times")
            messages.info(
                request,
                "تم إرسال رفض الموعد واقتراح أوقات بديلة"
            )

        session.save()
        return redirect("patient:sessions")
