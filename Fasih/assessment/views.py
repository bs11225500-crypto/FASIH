from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings


def assessment_form(request):
    return render(request, 'assessment/assessment_form.html')


@csrf_exempt
def upload_audio(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        image_index = request.POST.get("image_index")

        if not audio_file:
            return JsonResponse({"error": "No audio"}, status=400)

        # مجلد مؤقت
        save_path = os.path.join(
            settings.MEDIA_ROOT,
            "assessment_audio"
        )
        os.makedirs(save_path, exist_ok=True)

        file_name = f"audio_image_{image_index}.webm"
        full_path = os.path.join(save_path, file_name)

        with open(full_path, "wb+") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        return JsonResponse({
            "status": "success",
            "file": file_name
        })