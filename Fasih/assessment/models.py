from django.db import models

class Assessment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    assessment_data = models.JSONField()

    def __str__(self):
        return f"Assessment #{self.id}"


