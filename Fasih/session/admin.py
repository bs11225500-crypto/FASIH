from django.contrib import admin
from .models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "session_type", "status", "start_time")
    list_filter = ("session_type", "status")
