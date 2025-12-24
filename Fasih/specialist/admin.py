from django.contrib import admin
from .models import Specialist, SpecialistCertificate, SpecialistAppeal



@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'specialization',
        'verification_status',
        'years_of_experience',
        'average_rating',
        'ratings_count',
    )

    list_filter = (
        'verification_status',
        'specialization',
    )

    search_fields = (
        'user__username',
        'user__email',
        'specialization',
        'license_number',
    )

    readonly_fields = (
        'average_rating',
        'ratings_count',
    )

    fieldsets = (
        ('بيانات المستخدم', {
            'fields': ('user',)
        }),
        ('المعلومات المهنية', {
            'fields': (
                'specialization',
                'license_number',
                'years_of_experience',
                'bio',
            )
        }),
        ('حالة التحقق', {
            'fields': (
                'verification_status',
                'rejection_reason',
            )
        }),
        ('التقييمات', {
            'fields': (
                'average_rating',
                'ratings_count',
            )
        }),
    )

    def average_rating(self, obj):
        return obj.average_rating()
    average_rating.short_description = "متوسط التقييم"

    def ratings_count(self, obj):
        return obj.ratings_count()
    ratings_count.short_description = "عدد التقييمات"


@admin.register(SpecialistCertificate)
class SpecialistCertificateAdmin(admin.ModelAdmin):
    list_display = (
        'specialist',
        'title',
        'issue_date',
        'expiry_date',
        'added_at',
    )

    list_filter = (
        'issue_date',
        'expiry_date',
    )

    search_fields = (
        'specialist__user__username',
        'title',
    )



@admin.register(SpecialistAppeal)
class SpecialistAppealAdmin(admin.ModelAdmin):
    list_display = (
        'specialist',
        'created_at',
        'reviewed',
        'accepted',
    )

    list_filter = (
        'reviewed',
        'accepted',
    )

    search_fields = (
        'specialist__user__username',
        'reason',
    )

    readonly_fields = (
        'created_at',
    )
