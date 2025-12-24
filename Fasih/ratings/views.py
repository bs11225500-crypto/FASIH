from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from specialist.models import Specialist
from .models import SpecialistRating

@login_required
def rate_specialist(request, specialist_id):
    patient = request.user.patient_profile
    specialist = get_object_or_404(Specialist, id=specialist_id)

    rating_obj, created = SpecialistRating.objects.get_or_create(
        patient=patient,
        specialist=specialist
    )

    if request.method == 'POST':
        rating = request.POST.get('rating')
        rating_obj.rating = rating
        rating_obj.save()
        return redirect('specialist:profile', specialist_id=specialist.id)

    return redirect('specialist:profile', specialist_id=specialist.id)
