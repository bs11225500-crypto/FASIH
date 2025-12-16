from django.db import models
from django.conf import settings

class Specialist(models.Model):

    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'قيد المراجعة'
        APPROVED = 'APPROVED', 'معتمد'
        REJECTED = 'REJECTED', 'مرفوض'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    years_of_experience = models.IntegerField()
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    def __str__(self):
        return self.user.email
