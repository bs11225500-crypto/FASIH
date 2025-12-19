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

from .models import User
from .forms import ( AccountRegisterForm,PatientRegisterForm,SpecialistRegisterForm)
from main.email_service import send_email 

def register_account(request):
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)

        if not form.is_valid():
            messages.error(request, "البيانات المدخلة غير صحيحة")
            return render(request, 'accounts/sign_up.html', {'form': form})

        try:
            with transaction.atomic():
                user = form.save()
                login(request, user)

            messages.success(request, "تم إنشاء الحساب بنجاح")

            if user.is_staff or user.is_superuser:
                return redirect('main:home')

            return redirect('accounts:choose_role')

        except Exception as e:
            print("REGISTER ERROR:", e)
            messages.error(
                request,
                "حدث خطأ غير متوقع أثناء إنشاء الحساب، حاول مرة أخرى"
            )

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

            if user.is_staff or user.is_superuser:
                return redirect('main:home')

            if not user.role:
                return redirect('accounts:choose_role')

            if user.role == User.Role.PATIENT:
                if not hasattr(user, 'patient'):
                    return redirect('accounts:complete_patient_profile')
                return redirect('main:home')

            if user.role == User.Role.SPECIALIST:
                if not hasattr(user, 'specialist'):
                    return redirect('accounts:complete_specialist_profile')
                return redirect('main:home')

        except Exception as e:
            print("LOGIN ERROR:", e)
            messages.error(
                request,
                "حدث خطأ غير متوقع أثناء تسجيل الدخول، حاول مرة أخرى"
            )

    return render(request, 'accounts/sign_in.html')


def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح")
    return redirect('accounts:login')



@login_required
def choose_role(request):
    user = request.user

    if user.is_staff or user.is_superuser:
        return redirect('main:home')

    if user.role == User.Role.PATIENT:
        return redirect('accounts:complete_patient_profile')

    if user.role == User.Role.SPECIALIST:
        return redirect('accounts:complete_specialist_profile')

    if request.method == 'POST':
        selected_role = request.POST.get('role')

        if selected_role == User.Role.PATIENT:
            user.role = User.Role.PATIENT
            user.save()
            return redirect('accounts:complete_patient_profile')

        if selected_role == User.Role.SPECIALIST:
            user.role = User.Role.SPECIALIST
            user.save()
            return redirect('accounts:complete_specialist_profile')

    return render(request, 'accounts/choose_role.html')



@login_required
def complete_patient_profile(request):
    user = request.user

    if user.is_staff or user.is_superuser:
        return redirect('main:home')

    if user.role != User.Role.PATIENT:
        return redirect('accounts:choose_role')

    if hasattr(user, 'patient'):
        return redirect('main:home')

    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)

        if form.is_valid():
            form.save(user=user)
            messages.success(request, "تم إكمال بيانات المريض بنجاح")
            return redirect('main:home')

    else:
        form = PatientRegisterForm()

    return render(
        request,
        'accounts/complete_patient_profile.html',
        {'form': form}
    )



@login_required
def complete_specialist_profile(request):
    user = request.user

    if user.is_staff or user.is_superuser:
        return redirect('main:home')

    if user.role != User.Role.SPECIALIST:
        return redirect('accounts:choose_role')

    if hasattr(user, 'specialist'):
        return redirect('main:home')

    if request.method == 'POST':
        form = SpecialistRegisterForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save(user=user)

                messages.success(request, "تم إكمال بيانات الأخصائي بنجاح")
                return redirect('main:home')

            except Exception:
                messages.error(request, "حدث خطأ أثناء حفظ البيانات")

    else:
        form = SpecialistRegisterForm()

    return render(
        request,
        'accounts/complete_specialist_profile.html',
        {'form': form}
    )


@login_required
def specialist_pending(request):
    if request.user.role != User.Role.SPECIALIST:
        return redirect('main:home')

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

            html_content = render_to_string(
                "accounts/emails/password_reset.html",
                {
                    "reset_link": reset_link,
                    "logo_url": logo_url,
                }
            )

            send_email(
                to=email,
                subject="إعادة تعيين كلمة المرور | منصة فصيح",
                html_content=html_content
            )


        messages.success(
            request,
            "إذا كان البريد مسجلاً لدينا، سيتم إرسال رابط إعادة التعيين."
        )
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
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين")
        elif len(password1) < 8:
            messages.error(request, "كلمة المرور يجب أن تكون 8 أحرف على الأقل")
        else:
            user.set_password(password1)
            user.save()
            messages.success(request, "تم تغيير كلمة المرور بنجاح")
            return redirect('accounts:login')

    return render(
        request,
        'accounts/password_reset_confirm.html'
    )
