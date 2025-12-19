from django.db import models
from django.conf import settings


class Specialist(models.Model):

    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'قيد المراجعة'
        APPROVED = 'APPROVED', 'معتمد'
        REJECTED = 'REJECTED', 'مرفوض'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField(null=True,blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    rejection_reason = models.TextField(blank=True)


class SpecialistCertificate(models.Model):
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    certificate_file = models.FileField(upload_to='certificates/')
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
