from django.db import models
from patient.models import Patient
from specialist.models import Specialist

class Assessment(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="assessments"
    )

    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assessments"
    )

    STATUS_CHOICES = [
        ('PENDING', 'قيد المراجعة'),
        ('ACCEPTED', 'مقبول'),
        ('REJECTED', 'مرفوض'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    REJECTION_REASONS = [
        (
            'SPECIALIST_BUSY',
            'لدى الأخصائي عدد من الحالات الحالية ولا يمكنه إضافة حالة جديدة في الوقت الحالي، اختر أخصائي آخر'
        ),
        (
            'NEEDS_INPERSON',
            'الحالة تحتاج تقييم حضوري مباشر'
        ),
        (
            'NOT_REQUIRED',
            'الحالة لا تحتاج تدخل أخصائي تخاطب في الوقت الحالي'
        ),
    ]

    rejection_reason = models.CharField(
        max_length=120,
        choices=REJECTION_REASONS,
        null=True,
        blank=True
    )

    assessment_data = models.JSONField()
    audio_files = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment #{self.id}"