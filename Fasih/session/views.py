from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.core.exceptions import ValidationError
from patient.models import Patient
from .models import Session
from specialist.models import Specialist
from datetime import datetime





@login_required
def create_session(request):
    # السماح للأخصائي فقط
    if not hasattr(request.user, "specialist"):
        return redirect("main:home")

    if request.method == "POST":
        file_number = request.POST.get("file_number")
        title = request.POST.get("title")

        try:
            patient = get_object_or_404(Patient, file_number=file_number)

            start_time = datetime.fromisoformat(request.POST.get("start_time"))
            end_time = datetime.fromisoformat(request.POST.get("end_time"))

            session = Session(
                patient=patient,
                specialist=request.user.specialist,
                title=title,
                start_time=start_time,
                end_time=end_time,
            )

            session.save()  # هنا ينفذ clean()

            messages.success(request, "تم اقتراح الجلسة بنجاح 🕒")
            return redirect("session:session_detail", session.id)

        except ValidationError as e:
            messages.error(request, e.message)

        except Exception:
            messages.error(request, "حدث خطأ، تأكدي من البيانات")

    return render(request, "session/create_session.html")





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


def join_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if not session.can_join():
        return render(
            request,
            "session/session_not_started.html",
            {"session": session}
        )

    return render(request, "session/meet.html", {
        "session": session
    })

        

@login_required
def respond_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if not hasattr(request.user, "patient") or request.user.patient != session.patient:
        return redirect("main:home")

    if session.status != Session.Status.PROPOSED:
        messages.error(request, "تم التعامل مع هذه الجلسة مسبقًا")
        return redirect("session:session_detail", session.id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            session.status = Session.Status.CONFIRMED
            messages.success(request, "تم تأكيد الجلسة بنجاح ✅")

        elif action == "reject":
            session.status = Session.Status.REJECTED
            session.patient_response_reason = request.POST.get("reason")
            session.patient_suggested_times = request.POST.get("suggested_times")
            messages.info(
                request,
                "تم إرسال رفض الموعد واقتراح أوقات بديلة 📝"
            )

        session.save()
        return redirect("session:session_detail", session.id)


