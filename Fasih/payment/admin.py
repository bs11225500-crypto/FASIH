from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'amount',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'moyasar_payment_id',
    )

    readonly_fields = (
        'created_at',
        'moyasar_payment_id',
    )

    fieldsets = (
        ('معلومات الدفع', {
            'fields': (
                'user',
                'treatment_plan',
                'amount',
                'status',
            )
        }),
        ('معلومات البوابة', {
            'fields': (
                'moyasar_payment_id',
                'created_at',
            )
        }),
    )
