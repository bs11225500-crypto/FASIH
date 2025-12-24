from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from patient.models import Patient
from specialist.models import Specialist
from assessment.models import Assessment
from .models import SpecialistRating

@login_required
def rate_specialist(request, specialist_id):
    patient = request.user.patient_profile
    specialist = get_object_or_404(Specialist, id=specialist_id)

    if request.method == 'POST':
        rating_value = request.POST.get('rating')

        if not rating_value:
            return redirect('specialist:specialist_detail', specialist_id=specialist.id)

        rating_obj, created = SpecialistRating.objects.update_or_create(
            patient=patient,
            specialist=specialist,
            defaults={'rating': rating_value}
        )

    return redirect('specialist:specialist_detail', specialist_id=specialist.id)