from django.contrib import admin
from .models import Task, PatientTask

admin.site.register(Task)
admin.site.register(PatientTask)

