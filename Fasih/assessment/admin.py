from django.contrib import admin
from .models import Assessment


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'patient_name',
        'specialist_name',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'patient__user__first_name',
        'patient__user__last_name',
        'specialist__user__first_name',
        'specialist__user__last_name',
    )

    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'patient',
                'specialist',
                'status',
            )
        }),
        ('تفاصيل التقييم', {
            'fields': (
                'assessment_data',
                'audio_files',
            )
        }),
        ('سبب الرفض (إن وجد)', {
            'fields': (
                'rejection_reason',
            )
        }),
        ('معلومات إضافية', {
            'fields': (
                'created_at',
            )
        }),
    )

    def patient_name(self, obj):
        if obj.patient:
            return obj.patient.user.get_full_name()
        return "-"

    patient_name.short_description = "المريض"

    def specialist_name(self, obj):
        if obj.specialist:
            return obj.specialist.user.get_full_name()
        return "-"

    specialist_name.short_description = "الأخصائي"
