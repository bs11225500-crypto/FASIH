from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from patient.models import Patient
from specialist.models import Specialist
from assessment.models import Assessment
from .models import SpecialistRating


@login_required
def rate_specialist(request, specialist_id):
    # لازم يكون Patient
    if request.user.role != "PATIENT":
        return HttpResponseForbidden("غير مسموح")

    patient = request.user.patient_profile
    specialist = get_object_or_404(Specialist, id=specialist_id)

    # ✅ الشرط: لازم يكون بينهم ربط (Assessment مقبول)
    is_linked = Assessment.objects.filter(
        patient=patient,
        specialist=specialist,
        status="ACCEPTED"
    ).exists()

    if not is_linked:
        return HttpResponseForbidden("لا يمكنك تقييم هذا الأخصائي إلا بعد بدء التعامل معه")

    # بعدها فقط نسمح بالتقييم
    rating_obj, created = SpecialistRating.objects.get_or_create(
        patient=patient,
        specialist=specialist
    )

    if request.method == "POST":
        rating = request.POST.get("rating")
        if rating in ["1", "2", "3", "4", "5"]:
            rating_obj.rating = int(rating)
            rating_obj.save()

    # رجّعيه لصفحة التفاصيل (عدّلي الاسم حسب url عندك)
    return redirect("specialist:specialist_detail", specialist_id=specialist.id)
