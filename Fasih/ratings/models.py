from django.db import models
from patient.models import Patient
from specialist.models import Specialist

class SpecialistRating(models.Model):
    RATING_CHOICES = [
        (1, 'أقل من المتوسط'),
        (2, 'متوسط'),
        (3, 'جيد'),
        (4, 'جيد جدًا'),
        (5, 'ممتاز'),
    ]

    patient = models.ForeignKey(Patient,on_delete=models.CASCADE,related_name='specialist_ratings')
    specialist = models.ForeignKey(Specialist,on_delete=models.CASCADE,related_name='ratings')

    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('patient', 'specialist')

    def __str__(self):
        return f"{self.specialist} - {self.get_rating_display()}"
