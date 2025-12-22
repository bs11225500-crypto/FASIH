from django.db import models
from patient.models import Patient
from specialist.models import Specialist
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError



class Session(models.Model):

    class Status(models.TextChoices):
        PROPOSED = "PROPOSED", "بانتظار موافقة المريض"
        CONFIRMED = "CONFIRMED", "مؤكدة"
        REJECTED = "REJECTED", "مرفوضة"
        COMPLETED = "COMPLETED", "منتهية"
        CANCELED = "CANCELED", "ملغاة"
    class SessionType(models.TextChoices):
        INITIAL = "INITIAL", "جلسة أولى"
        TREATMENT = "TREATMENT", "جلسة علاجية"


    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    title = models.CharField(max_length=255)

    room_name = models.CharField(
        max_length=255,
        unique=True,
        editable=False
    )

    meeting_url = models.URLField(editable=False)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROPOSED
    )
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.TREATMENT
    )

    patient_response_reason = models.TextField(
    blank=True,
    null=True)

    patient_suggested_times = models.TextField(
        blank=True,
        null=True
    )


    created_at = models.DateTimeField(auto_now_add=True)


    def can_join(self):
        return self.status == self.Status.CONFIRMED and timezone.now() >= self.start_time
    
    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("وقت نهاية الجلسة يجب أن يكون بعد وقت البداية")
        
    def save(self, *args, **kwargs):
        self.full_clean() 
        
        if not self.room_name:
            self.room_name = f"fasih-{uuid.uuid4()}"
            self.meeting_url = f"https://meet.jit.si/{self.room_name}"
            
        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.title} | {self.patient.file_number} | {self.get_status_display()}"
