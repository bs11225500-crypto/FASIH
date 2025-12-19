from django.db import models
from django.conf import settings
from datetime import date


class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='patient_profile')
    file_number = models.CharField(max_length=20,unique=True,editable=False)
    birth_date = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'ذكر'), ('F', 'أنثى')]
    )

    @property
    def age(self):
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def save(self, *args, **kwargs):
        if not self.file_number:
            last_patient = Patient.objects.order_by('id').last()
            if last_patient:
                last_number = int(last_patient.file_number.split('-')[1])
                self.file_number = f"P-{last_number + 1:06d}"
            else:
                self.file_number = "P-000001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()
