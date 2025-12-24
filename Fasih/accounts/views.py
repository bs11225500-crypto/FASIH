from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from .models import User
from patient.models import Patient
from specialist.models import Specialist,SpecialistAppeal
from .forms import (AccountRegisterForm, PatientProfileForm,SpecialistProfileForm, UserProfileForm,SpecialistCertificateForm)
from main.email_service import send_email 

def register_account(request):
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)

        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return render(request, 'accounts/sign_up.html', {'form': form})


        try:
            with transaction.atomic():
                user = form.save()
                login(request, user)

            messages.success(request, "تم إنشاء الحساب بنجاح")
            return redirect('accounts:choose_role')

        except Exception as e:
            print("REGISTER ERROR:", e)
            messages.error(request,"حدث خطأ غير متوقع أثناء إنشاء الحساب، حاول مرة أخرى")

    else:
        form = AccountRegisterForm()

    return render(request, 'accounts/sign_up.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "الرجاء إدخال البريد الإلكتروني وكلمة المرور")
            return render(request, 'accounts/sign_in.html')

        try:
            user = authenticate(request, email=email, password=password)

            if not user or not user.is_active:
                messages.error(request, "بيانات الدخول غير صحيحة")
                return render(request, 'accounts/sign_in.html')

            login(request, user)
            messages.success(request, "تم تسجيل الدخول بنجاح")
            return post_login_redirect(request)


        except Exception as e:
            print("LOGIN ERROR:", e)
            messages.error(request,"حدث خطأ غير متوقع أثناء تسجيل الدخول، حاول مرة أخرى")

    return render(request, 'accounts/sign_in.html')


def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح")
    return redirect('accounts:login')



@login_required
def choose_role(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect('admin_panel:dashboard')

    if user.role:
        if user.role == User.Role.PATIENT:
            return redirect('accounts:complete_patient_profile')

        if user.role == User.Role.SPECIALIST:
            return redirect('accounts:complete_specialist_profile')

    if request.method == 'POST':
        selected_role = request.POST.get('role')

        if selected_role in [User.Role.PATIENT, User.Role.SPECIALIST]:
            user.role = selected_role
            user.save()

            if selected_role == User.Role.PATIENT:
                return redirect('accounts:complete_patient_profile')
            else:
                return redirect('accounts:complete_specialist_profile')

    return render(request, 'accounts/choose_role.html')


@login_required
def complete_patient_profile(request):
    user = request.user

    if user.role != User.Role.PATIENT:
        return redirect('accounts:choose_role')

    if hasattr(user, 'patient_profile'):
        return redirect('main:home')

    patient = Patient(user=user)

    if request.method == 'POST':
        user_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=user
        )
        patient_form = PatientProfileForm(
            request.POST,
            instance=patient
        )

        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, "تم إكمال بيانات المريض بنجاح")
            return redirect('patient:dashboard')

    else:
        user_form = UserProfileForm(instance=user)
        patient_form = PatientProfileForm()

    return render(request,'accounts/complete_patient_profile.html',{'user_form': user_form,'patient_form': patient_form})

@login_required
def complete_specialist_profile(request):
    user = request.user

    if user.role != User.Role.SPECIALIST:
        return redirect('accounts:choose_role')

    specialist, created = Specialist.objects.get_or_create(user=user)



    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        specialist_form = SpecialistProfileForm(request.POST, instance=specialist)
        certificate_form = SpecialistCertificateForm(request.POST, request.FILES)

        if (user_form.is_valid()and specialist_form.is_valid()and certificate_form.is_valid()):
            user_form.save()

            specialist = specialist_form.save(commit=False)
            specialist.verification_status = Specialist.VerificationStatus.PENDING
            specialist.save()

            cert = certificate_form.save(commit=False)
            cert.specialist = specialist
            cert.save()

            messages.success(request,"تم إرسال بياناتك بنجاح، وسيتم مراجعتها من الإدارة")
            send_email(
                to=user.email,
                subject="تم استلام طلبك | منصة فصيح",
                html_content=render_to_string(
                    "accounts/emails/specialist_request_received.html",
                    {"name": user.get_full_name() or user.username}
                )
            )

            return redirect('accounts:specialist_pending')

        else:
            messages.error(request,"تأكد من إدخال جميع البيانات المطلوبة ورفع ملف الرخصة بشكل صحيح")

    else:
        user_form = UserProfileForm(instance=user)
        specialist_form = SpecialistProfileForm(instance=specialist)
        certificate_form = SpecialistCertificateForm()

    return render(request,'accounts/complete_specialist_profile.html',{'user_form': user_form,'specialist_form': specialist_form,'certificate_form': certificate_form,})




@login_required
def specialist_pending(request):
    user = request.user

    if user.role != User.Role.SPECIALIST:
        return redirect('main:home')

    specialist = getattr(user, 'specialist', None)

    if not specialist:
        return redirect('accounts:complete_specialist_profile')

    if specialist.verification_status == Specialist.VerificationStatus.APPROVED:
        return redirect('specialist:specialist_home') 

    if specialist.verification_status == Specialist.VerificationStatus.REJECTED:
        return redirect('accounts:specialist_rejected')

    messages.info(request,"حسابك قيد المراجعة حاليًا، سيتم إشعارك بعد الموافقة")

    return render(request, 'accounts/specialist_pending.html')


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse(
                    'accounts:password_reset_confirm',
                    kwargs={'uidb64': uid, 'token': token}
                )
            )

            logo_url = request.build_absolute_uri(
                settings.STATIC_URL + "main/img/logo.png"
            )

            html_content = render_to_string("accounts/emails/password_reset.html",{"reset_link": reset_link,"logo_url": logo_url,})

            send_email(
                to=email,
                subject="إعادة تعيين كلمة المرور | منصة فصيح",
                html_content=html_content
            )


        messages.success(request,"إذا كان البريد مسجلاً لدينا، سيتم إرسال رابط إعادة التعيين.")
        return redirect('accounts:login')

    return render(request, 'accounts/password_reset_request.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "الرابط غير صالح أو منتهي.")
        return redirect('accounts:login')

    if request.method == 'POST':
        password1 = request.POST.get('new_password1')
        password2 = request.POST.get('new_password2')

        if not password1 or not password2:
            messages.error(request, "الرجاء إدخال كلمة المرور")
            return render(request, 'accounts/password_reset_confirm.html')

        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين")
            return render(request, 'accounts/password_reset_confirm.html')

        if len(password1) < 8:
            messages.error(request, "كلمة المرور يجب أن تكون 8 أحرف على الأقل")
            return render(request, 'accounts/password_reset_confirm.html')

        user.set_password(password1)
        user.save()
        messages.success(request, "تم تغيير كلمة المرور بنجاح")
        return redirect('accounts:login')


    return render(request,'accounts/password_reset_confirm.html')


@login_required
def post_login_redirect(request):
    user = request.user

    if user.is_staff or user.is_superuser:
        return redirect(request.GET.get('next') or 'admin_panel:dashboard')

    if user.role == User.Role.SPECIALIST:
        specialist = getattr(user, 'specialist', None)

        if not specialist:
            return redirect('accounts:complete_specialist_profile')

        if (specialist.verification_status == Specialist.VerificationStatus.PENDING
            and specialist.specialistcertificate_set.exists()
        ):
            return redirect('accounts:specialist_pending')


        if specialist.verification_status == Specialist.VerificationStatus.REJECTED:
            return redirect('accounts:specialist_rejected')

        
        return redirect('specialist:specialist_home')  

    if not user.role:
        return redirect('accounts:choose_role')

    return redirect(request.GET.get('next', '/'))



@login_required
def specialist_rejected(request):
    specialist = get_object_or_404(Specialist, user=request.user)

    if specialist.verification_status != Specialist.VerificationStatus.REJECTED:
        return redirect('main:home')

    return render(request, 'accounts/specialist_rejected.html', {
        'specialist': specialist
    })


@login_required
def specialist_appeal(request):
    specialist = get_object_or_404(Specialist, user=request.user)

    if specialist.verification_status != Specialist.VerificationStatus.REJECTED:
        return redirect('main:home')

    if request.method == 'POST':
        appeal_reason = request.POST.get('reason')

        user_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        specialist_form = SpecialistProfileForm(
            request.POST,
            instance=specialist
        )
        certificate_form = SpecialistCertificateForm(
            request.POST,
            request.FILES
        )

        if appeal_reason and user_form.is_valid() and specialist_form.is_valid():

            user_form.save()

            specialist = specialist_form.save(commit=False)
            specialist.verification_status = Specialist.VerificationStatus.PENDING
            specialist.rejection_reason = ""
            specialist.save()

            SpecialistAppeal.objects.create(
                specialist=specialist,
                reason=appeal_reason
            )

            if (
                certificate_form.is_valid()
                and certificate_form.cleaned_data.get('certificate_file')
            ):
                cert = certificate_form.save(commit=False)
                cert.specialist = specialist
                cert.save()

            messages.success(request,"تم إرسال الاعتراض وتحديث بياناتك بنجاح")

            send_email(
                to=request.user.email,
                subject="تم استلام اعتراضك | منصة فصيح",
                html_content=render_to_string(
                    "accounts/emails/specialist_appeal_received.html",
                    {
                        "name": request.user.get_full_name()
                        or request.user.username
                    }
                )
            )

            return redirect('accounts:specialist_pending')

        messages.error(request, "تأكد من تعبئة سبب الاعتراض والبيانات المطلوبة")

    else:
        user_form = UserProfileForm(instance=request.user)
        specialist_form = SpecialistProfileForm(instance=specialist)
        certificate_form = SpecialistCertificateForm()

    return render(request,'accounts/specialist_appeal.html',{'specialist': specialist,'user_form': user_form,'specialist_form': specialist_form,'certificate_form': certificate_form,})

@login_required
def role_dashboard_redirect(request):
    user = request.user

    if user.is_staff or user.is_superuser:
        return redirect('admin_panel:dashboard')

    if not user.role:
        return redirect('accounts:choose_role')

    if user.role == user.Role.PATIENT:
        return redirect('patient:dashboard')

    if user.role == user.Role.SPECIALIST:
        return redirect('specialist:specialist_home')

    return redirect('main:home')