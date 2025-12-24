from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User
from patient.models import Patient
from specialist.models import Specialist
from specialist.models import SpecialistCertificate


class AccountRegisterForm(forms.Form):
    email = forms.EmailField(label="البريد الإلكتروني")

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
        return User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
        )



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'profile_image',
        ]
        labels = {
            'first_name': 'الاسم الأول',
            'middle_name': 'الاسم الأوسط',
            'last_name': 'اسم العائلة',
            'profile_image': 'صورة الحساب',
        }


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['birth_date', 'gender']
        labels = {
            'birth_date': 'تاريخ الميلاد',
            'gender': 'الجنس',
        }
        widgets = {
            'birth_date': forms.DateInput(
                attrs={
                    'type': 'date',
                }
            )
        }



class SpecialistProfileForm(forms.ModelForm):
    class Meta:
        model = Specialist
        fields = [
            'specialization',
            'license_number',
            'years_of_experience',
             'bio',
        ]
        labels = {
            'specialization': 'التخصص',
            'license_number': 'رقم رخصة مزاولة المهنة',
            'years_of_experience': 'سنوات الخبرة',
            "bio":'نبذة عنك', 
        }

class SpecialistCertificateForm(forms.ModelForm):
    certificate_file = forms.FileField(
        required=False,
        label='ملف الشهادة'
    )

    class Meta:
        model = SpecialistCertificate
        fields = [
            'title',
            'description',
            'certificate_file',
            'issue_date',
            'expiry_date',
        ]
        labels = {
            'title': 'عنوان الشهادة',
            'description': 'وصف الشهادة',
            'certificate_file': 'ملف الشهادة',
            'issue_date': 'تاريخ الإصدار',
            'expiry_date': 'تاريخ الانتهاء',
        }
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

