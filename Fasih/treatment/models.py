from django.db import models
from patient.models import Patient
from specialist.models import Specialist


class TreatmentPlan(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "مسودة"
        ACTIVE = "ACTIVE", "نشطة"
        COMPLETED = "COMPLETED", "مكتملة"
        CANCELED = "CANCELED", "ملغاة"

    # العلاقات
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="treatment_plans"
    )

    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name="treatment_plans"
    )

    # البيانات العامة
    diagnosis = models.CharField(max_length=255)
    start_date = models.DateField()
    duration_weeks = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # المشكلة والهدف
    problem_description = models.TextField()
    long_term_goal = models.TextField()

    # إعدادات الجلسات (اختيارية)
    sessions_per_week = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    session_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    # متابعة عامة
    progress_summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Treatment Plan - {self.patient.file_number}"


class ShortTermGoal(models.Model):
    treatment_plan = models.ForeignKey(
        TreatmentPlan,
        on_delete=models.CASCADE,
        related_name="short_term_goals"
    )

    description = models.TextField()
    target_accuracy = models.PositiveIntegerField(
        help_text="Percentage like 80"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


# بدون تاسك حاليًا  
class ProgressReport(models.Model):
    treatment_plan = models.ForeignKey(
        TreatmentPlan,
        on_delete=models.CASCADE,
        related_name="progress_reports"
    )

    week_number = models.PositiveIntegerField()
    accuracy = models.PositiveIntegerField(null=True, blank=True)
    specialist_notes = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Week {self.week_number}"
