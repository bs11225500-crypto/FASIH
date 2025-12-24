from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.urls import reverse


from patient.models import Patient
from .models import Session,SessionNote
from session.daily import create_daily_room, create_daily_token
from session.email_service import (send_session_confirmed_email,send_session_cancelled_email,send_session_completed_email)



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
        if status == Session.Status.CONFIRMED:
            send_session_confirmed_email(session)

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

    is_specialist = hasattr(request.user, "specialist")
    is_patient = hasattr(request.user, "patient_profile")

    if not is_specialist and not is_patient:
        messages.error(request, "لا تملك صلاحية الدخول لهذه الجلسة")
        return redirect("main:home")

    if session.status == Session.Status.COMPLETED:
        return render(
            request,
            "session/session_ended.html",
            {
                "session": session,
                "is_specialist": is_specialist
            }
        )

    if session.status != Session.Status.CONFIRMED:
        messages.info(request, "الجلسة غير مؤكدة")
        return redirect("patient:sessions")

    if not session.can_join():
        return render(
            request,
            "session/session_not_started.html",
            {"session": session}
        )

    # إنشاء الغرفة
    if not session.meeting_url:
        daily_room = create_daily_room(session.room_name)
        session.meeting_url = daily_room["url"]
        session.save()

    daily_token = create_daily_token(
        session.room_name,
        is_owner=is_specialist
    )

    if is_specialist and not session.specialist_joined:
        session.specialist_joined = True
        session.save()

    if is_patient and not session.specialist_joined:
        messages.info(request, "بانتظار دخول الأخصائي")
        return redirect("patient:sessions")

    return render(
        request,
        "session/meet.html",
        {
            "session": session,
            "daily_token": daily_token,
            "is_specialist": is_specialist,
        }
    )


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
            session.save()
            send_session_confirmed_email(session)


            messages.success(request, "تم تأكيد الجلسة بنجاح")

        elif action == "reject":
            session.status = Session.Status.REJECTED
            session.patient_response_reason = request.POST.get("reason")
            session.patient_suggested_times = request.POST.get("suggested_times")
            session.save()
            send_session_cancelled_email(session)


            messages.info(request,"تم إرسال رفض الموعد واقتراح أوقات بديلة")

        return redirect("patient:sessions")

@login_required
@require_POST
def complete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if session.status != Session.Status.CONFIRMED:
        return JsonResponse({"error": "invalid session state"}, status=400)

    if hasattr(request.user, "specialist"):
        session.status = Session.Status.COMPLETED
        session.save()
        send_session_completed_email(session)
        return JsonResponse({
            "status": "completed",
            "redirect_url": reverse("session:join_session", args=[session.id])
        })

    return JsonResponse({"error": "not allowed"}, status=403)



@login_required
def add_session_note(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    # فقط الأخصائي
    if not hasattr(request.user, "specialist"):
        messages.error(request, "غير مصرح لك")
        return redirect("main:home")

    # الجلسة لازم تكون منتهية
    if session.status != Session.Status.COMPLETED:
        messages.info(request, "لا يمكن إضافة ملاحظات قبل انتهاء الجلسة")
        return redirect("session:session_detail", session.id)

    if hasattr(session, "note"):
        return redirect("session:session_detail", session.id)

    if request.method == "POST":
        notes = request.POST.get("notes")

        SessionNote.objects.create(
            session=session,
            specialist=request.user.specialist,
            notes=notes
        )


        messages.success(request, "تم حفظ ملاحظات الجلسة")
        return redirect("session:session_detail", session.id)

    return render(
        request,
        "session/add_note.html",
        {"session": session}
    )

@login_required
def session_note_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    # الجلسة لازم تكون منتهية
    if session.status != Session.Status.COMPLETED:
        messages.info(request, "ملاحظات الجلسة غير متاحة بعد")
        return redirect("session:session_detail", session.id)

    return render(
        request,
        "session/session_note_detail.html",
        {
            "session": session
        }
    )
