from django.contrib import admin
from .models import (
    TreatmentPlan,
    ShortTermGoal,
    DailyPlan,
    DailyTask,
    ProgressReport
)


@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = (
        'patient',
        'specialist',
        'status',
        'start_date',
        'duration_weeks',
        'created_at',
    )

    list_filter = (
        'status',
        'start_date',
    )

    search_fields = (
        'patient__file_number',
        'patient__user__first_name',
        'patient__user__last_name',
        'specialist__user__first_name',
        'specialist__user__last_name',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )
