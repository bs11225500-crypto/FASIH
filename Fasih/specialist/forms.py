from django import forms
from .models import SpecialistCertificate

class SpecialistCertificateForm(forms.ModelForm):

    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = SpecialistCertificate
        fields = [
            "title",
            "description",
            "certificate_file",
            "issue_date",
            "expiry_date",
        ]
