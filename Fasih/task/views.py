from datetime import date
from django.shortcuts import render, get_object_or_404 ,redirect
from django.contrib.auth.decorators import login_required
from treatment.models import DailyTask,TreatmentPlan
from treatment.models import DailyPlan
from django.conf import settings
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from treatment.models import DailyTask
from .storage import TaskExecutionStorage



# Create your views here.
@login_required
def daily_tasks(request):
    patient = getattr(request.user, "patient_profile", None)

    plan = None
    daily_plans = []

    if patient:
        plan = TreatmentPlan.objects.filter(
            patient=patient
        ).order_by("-created_at").first()
  
        if plan and plan.status != TreatmentPlan.Status.ACTIVE:
            return redirect("patient:treatment_plan")
        
        if plan:
            days = DailyPlan.objects.filter(
                treatment_plan=plan
            ).prefetch_related("tasks")

            paginator = Paginator(days, 7)  
            page_number = request.GET.get("page")
            daily_plans = paginator.get_page(page_number)

    return render(request, 'task/daily_tasks.html', {
        "plan": plan,
        "daily_plans": daily_plans
    })




@login_required
def task_preview(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)

    if task.daily_plan.treatment_plan.status != TreatmentPlan.Status.ACTIVE:
        return redirect("patient:treatment_plan")

    video_url = f"{settings.R2_TRAINING_VIDEOS_URL}/letters/{task.target_letter}.mp4"

    return render(request, "task/task_preview.html", {
        "task": task,
        "video_url": video_url
    })

@login_required
def task_execute(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)
 
    if task.daily_plan.treatment_plan.status != TreatmentPlan.Status.ACTIVE:
        return redirect("patient:treatment_plan")
    
    if task.status == DailyTask.Status.COMPLETED:
        return redirect("task:task_preview", task_id=task.id)

    return render(request, "task/task_execute.html", {
        "task": task
    })


@csrf_exempt
@login_required
def finish_task(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)
 
    if task.daily_plan.treatment_plan.status != TreatmentPlan.Status.ACTIVE:
        return redirect("patient:treatment_plan")

    if task.status == DailyTask.Status.COMPLETED:
        return JsonResponse({"error": "Task already completed"}, status=403)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    video = request.FILES.get("video")
    if not video:
        return JsonResponse({"error": "No video"}, status=400)

    file_name = f"task_execution/task_{task.id}.webm"
    saved_path = default_storage.save(file_name, ContentFile(video.read()))
    video_url = default_storage.url(saved_path)

    task.execution_video_url = video_url
    task.status = DailyTask.Status.COMPLETED
    task.completed_at = timezone.now()
    task.save()

    return JsonResponse({"status": "success"})


