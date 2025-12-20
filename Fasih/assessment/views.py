from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Assessment
from patient.models import Patient


def assessment_form(request):
    return render(request, 'assessment/assessment_form.html')



@csrf_exempt
def upload_audio(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        image_index = request.POST.get("image_index")

        if not audio_file:
            return JsonResponse({"error": "No audio"}, status=400)

        file_name = f"assessment_audio/audio_image_{image_index}.webm"


        # يحفظ باستخدام storage (محلي أو R2 حسب settings)
        saved_path = default_storage.save(file_name, ContentFile(audio_file.read()))

        return JsonResponse({
            "status": "success",
            "file": saved_path
        })

    return JsonResponse({"error": "Invalid method"}, status=405)


@login_required
@csrf_exempt
def submit_assessment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    data = json.loads(request.body)

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    assessment = Assessment.objects.create(
        patient=patient,
        assessment_data=data["assessment_data"],
        audio_files=data.get("audio_files", [])
    )

    return JsonResponse({
        "status": "success",
        "assessment_id": assessment.id
    })


def assessment_detail(request, id):
    assessment = get_object_or_404(Assessment, id=id)
    return render(request, "assessment/detail.html", {
        "assessment": assessment
    })

def assessment_detail(request, id):
    assessment = get_object_or_404(Assessment, id=id)

    dt = assessment.created_at

    # لو الوقت naive اعتبريه UTC (غالبًا هذا اللي عندك)
    if timezone.is_naive(dt):
        # نخليه كأنه UTC
        dt = dt.replace(tzinfo=timezone.utc)

    # تحويل إلى توقيت السعودية (UTC+3) بدون settings
    dt_riyadh = dt + timedelta(hours=3)

    context = {
        "assessment": assessment,
        "sent_date": dt_riyadh.strftime("%Y / %m / %d"),
        "sent_time": dt_riyadh.strftime("%I:%M %p"),
    }
    return render(request, "assessment/detail.html", context)