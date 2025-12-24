from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'full_name',
        'email',
        'phone',
        'created_at',
    )

    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')

    readonly_fields = ('created_at',)

    fieldsets = (
        ('معلومات المرسل', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
            )
        }),
        ('الرسالة', {
            'fields': (
                'message',
            )
        }),
        ('معلومات إضافية', {
            'fields': (
                'created_at',
            )
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "الاسم"
