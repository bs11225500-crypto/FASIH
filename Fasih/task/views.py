from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PatientTask


# Create your views here.
@login_required
def daily_tasks(request):
    patient = getattr(request.user, 'patient_profile', None)

    tasks = []
    if patient:
        tasks = PatientTask.objects.filter(
            patient=patient,
            due_date=date.today()
        )

    return render(request, 'task/daily_tasks.html', {
        'tasks': tasks
    })

@login_required
def task_detail(request, pk):
    patient = request.user.patient_profile
    patient_task = PatientTask.objects.get(
        pk=pk,
        patient=patient
    )

    return render(request, 'task/task_detail.html', {
        'patient_task': patient_task
    })
