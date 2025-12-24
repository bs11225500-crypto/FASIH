from django.db import models
from django.conf import settings
from django.db.models import Avg



class Specialist(models.Model):

    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'قيد المراجعة'
        APPROVED = 'APPROVED', 'معتمد'
        REJECTED = 'REJECTED', 'مرفوض'
        APPEALED = 'APPEALED', 'تم الاعتراض'


    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField(null=True,blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    bio = models.TextField(blank=True,verbose_name="نبذة عن الأخصائي")


    rejection_reason = models.TextField(blank=True)
    def average_rating(self):
        return round(self.ratings.aggregate(avg=Avg('rating'))['avg'] or 0,1)

    def ratings_count(self):
        return self.ratings.count()

    def stars_range(self):
        return range(int(self.average_rating()))





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

class SpecialistAppeal(models.Model):
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name='appeals'
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    accepted = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Appeal - {self.specialist.user}"
