from django.contrib import admin
from django.contrib import admin
from .models import SpecialistRating

# Register your models here.


@admin.register(SpecialistRating)
class SpecialistRatingAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'patient', 'rating', 'created_at')
    list_filter = ('rating',)
