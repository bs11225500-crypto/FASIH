from django.shortcuts import render, redirect, get_object_or_404
from .models import TreatmentPlan, ShortTermGoal, ProgressReport
from patient.models import Patient
from specialist.models import Specialist
from django.contrib.auth.decorators import login_required


@login_required
def treatment_patients(request):
    specialist = get_object_or_404(Specialist, user=request.user)

    patients = Patient.objects.filter(
        assessments__specialist=specialist,
        assessments__status='ACCEPTED'
    ).distinct()

    context = {
        "patients": patients
    }

    return render(
        request,
        "treatment/treatment_patients.html",
        context
    )

def create_treatment_plan(request, file_number):
    patient = get_object_or_404(Patient, file_number=file_number)
    specialist = get_object_or_404(Specialist, user=request.user)

    if request.method == "POST":
        plan = TreatmentPlan.objects.create(
            patient=patient,
            specialist=specialist,
            diagnosis=request.POST.get("diagnosis"),
            problem_description=request.POST.get("problem_description"),
            long_term_goal=request.POST.get("long_term_goal"),
            start_date=request.POST.get("start_date"),
            duration_weeks=request.POST.get("duration_weeks"),
            sessions_per_week=request.POST.get("sessions_per_week") or None,
            session_duration_minutes=request.POST.get("session_duration_minutes") or None,
            status="ACTIVE"
        )

        return redirect(
            "treatment:treatment_plan_detail",
            plan_id=plan.id
        )

    return render(
        request,
        "treatment/create_treatment_plan.html",
        {"patient": patient}
    )



def treatment_plan_detail(request, plan_id):
    treatment_plan = get_object_or_404(TreatmentPlan, id=plan_id)

    return render(request, "treatment/treatment_plan_detail.html", {
        "plan": treatment_plan
    })


def add_short_term_goal(request, plan_id):
    treatment_plan = get_object_or_404(TreatmentPlan, id=plan_id)

    if request.method == "POST":
        ShortTermGoal.objects.create(
            treatment_plan=treatment_plan,
            description=request.POST.get("description"),
            target_accuracy=request.POST.get("target_accuracy")
        )
        return redirect("treatment:treatment_plan_detail", plan_id=plan_id)

    return render(request, "treatment/add_short_term_goal.html", {
        "plan": treatment_plan
    })
