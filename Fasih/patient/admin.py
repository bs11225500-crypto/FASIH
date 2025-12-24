from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        'file_number',
        'full_name',
        'age',
        'gender',
    )

    list_filter = ('gender',)
    search_fields = (
        'file_number',
        'user__first_name',
        'user__last_name',
        'user__email',
    )

    readonly_fields = ('file_number',)

    fieldsets = (
        ('بيانات المستخدم', {
            'fields': (
                'user',
                'file_number',
            )
        }),
        ('بيانات المريض', {
            'fields': (
                'birth_date',
                'gender',
            )
        }),
    )

    def full_name(self, obj):
        return obj.user.get_full_name()

    full_name.short_description = "اسم المريض"
