from django.contrib import admin
from .models import Task, PatientTask


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'letter',
        'duration',
    )

    search_fields = (
        'title',
        'letter',
    )

    
