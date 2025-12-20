from django.shortcuts import render,get_object_or_404
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


@csrf_exempt
def submit_assessment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    data = json.loads(request.body)

    patient = Patient.objects.get(id=data["patient_id"])

    assessment = Assessment.objects.create(
    patient=patient,
    assessment_data=data["assessment_data"]
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
