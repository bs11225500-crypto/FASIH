from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime
from patient.models import Patient
from .models import Session
from specialist.models import Specialist




def create_session(request):
    # السماح للأخصائي فقط
    #if not hasattr(request.user, "specialist"):
        #return redirect("home")

    if request.method == "POST":
        file_number = request.POST.get("file_number")

        patient = get_object_or_404(Patient, file_number=file_number)

        start_time = datetime.fromisoformat(request.POST.get("start_time"))
        end_time = datetime.fromisoformat(request.POST.get("end_time"))

        session = Session.objects.create(
            patient=patient,
            specialist=request.user.specialist,
            title=request.POST.get("title"),
            start_time=start_time,
            end_time=end_time,
        )

        return redirect("session:session_detail", session.id)

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
        return render(request, "session/session_not_started.html", {
            "session": session
        })

    return render(request, "session/meet.html", {
        "room_name": session.room_name
    })

