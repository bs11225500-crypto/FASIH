
from django.db import models
from django.conf import settings
from datetime import date


class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    child_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(
    max_length=10,
    choices=[('M','ذكر'),('F','أنثى')],
    blank=True)
    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year

    def __str__(self):
        return self.child_name
