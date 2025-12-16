from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User
from patient.models import Patient
from specialist.models import Specialist



class AccountRegisterForm(forms.Form):
    email = forms.EmailField(
        label="البريد الإلكتروني"
    )

    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput,
        min_length=8
    )

    password2 = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مستخدم مسبقًا")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("كلمتا المرور غير متطابقتين")

        return cleaned_data

    def save(self):
        """
        Create User only (no role yet)
        """
        return User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )



class PatientRegisterForm(forms.Form):
    child_name = forms.CharField(
        label="اسم الطفل",
        max_length=255
    )

    birth_date = forms.DateField(
        label="تاريخ الميلاد",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def save(self, user):
        """
        Create Patient profile for existing User
        Prevent duplicate Patient creation
        """
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'child_name': self.cleaned_data['child_name'],
                'birth_date': self.cleaned_data['birth_date']
            }
        )
        return patient



class SpecialistRegisterForm(forms.Form):
    specialization = forms.CharField(
        label="التخصص",
        max_length=255
    )

    license_number = forms.CharField(
        label="رقم الرخصة",
        max_length=100
    )

    years_of_experience = forms.IntegerField(
        label="سنوات الخبرة",
        min_value=0
    )

    certificate_file = forms.FileField(
        label="شهادة الأخصائي",
        required=False
    )

    def save(self, user):
        specialist, created = Specialist.objects.get_or_create(
            user=user,
            defaults={
                'specialization': self.cleaned_data['specialization'],
                'license_number': self.cleaned_data['license_number'],
                'years_of_experience': self.cleaned_data['years_of_experience'],
                'certificate_file': self.cleaned_data.get('certificate_file'),
            }
        )
        return specialist
