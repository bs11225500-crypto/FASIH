from django.db import models
from patient.models import Patient
from specialist.models import Specialist


class TreatmentPlan(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "بانتظار الدفع"
        ACTIVE = "ACTIVE", "نشطة"
        COMPLETED = "COMPLETED", "مكتملة"
        CANCELED = "CANCELED", "ملغاة"

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


    diagnosis = models.CharField(max_length=255)
    start_date = models.DateField()
    duration_weeks = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

  
    problem_description = models.TextField()


    sessions_per_week = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    session_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

   
    progress_summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Treatment Plan - {self.patient.file_number}"

def calculate_treatment_price(duration_weeks):
    BASE_PRICE = 100
    WEEKLY_PRICE = 20
    return BASE_PRICE + max(0, duration_weeks - 1) * WEEKLY_PRICE

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

class DailyPlan(models.Model):
    treatment_plan = models.ForeignKey(
        TreatmentPlan,
        on_delete=models.CASCADE,
        related_name="daily_plans"
    )

    date = models.DateField()
    day_name = models.CharField(max_length=20)
    goal_of_day = models.TextField(blank=True)

    def week_number(self):
        delta = (self.date - self.treatment_plan.start_date).days
        return (delta // 7) + 1
    
class DailyTask(models.Model):
    daily_plan = models.ForeignKey(
        DailyPlan,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    task_name = models.CharField(max_length=255)
    target_letter = models.CharField(
        max_length=1,
        help_text="الحرف المستهدف في المهمة"
    )

    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "تمت"
        NOT_COMPLETED = "NOT_COMPLETED", "لم تتم"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        null=True,
        blank=True
    )
  
    execution_video_url = models.URLField(
        blank=True,
        null=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    specialist_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات الأخصائي"
    )
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
