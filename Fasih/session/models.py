from django.db import models
from patient.models import Patient
from specialist.models import Specialist
import uuid
from django.utils import timezone


class Session(models.Model):

    class Status(models.TextChoices):
        UPCOMING = "UPCOMING", "قادمة"
        COMPLETED = "COMPLETED", "منتهية"
        CANCELED = "CANCELED", "ملغاة"

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
        default=Status.UPCOMING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_name:
            self.room_name = f"fasih-{uuid.uuid4()}"
            self.meeting_url = f"https://meet.jit.si/{self.room_name}"
        super().save(*args, **kwargs)

    def can_join(self):
        return timezone.now() >= self.start_time

    def __str__(self):
        return f"{self.title} | {self.patient.file_number}"
