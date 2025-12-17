from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction

from django.contrib.auth.decorators import login_required
from .models import User


from .models import User
from .forms import (
    AccountRegisterForm,
    PatientRegisterForm,
    SpecialistRegisterForm
)

def register_patient_account(request):
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                login(request, user)
                messages.success(request, "تم إنشاء الحساب بنجاح")

            # 👇 مباشرة لاختيار الدور
            return redirect('accounts:choose_role')

        else:
            messages.error(request, "تأكدي من صحة البيانات")

    # أي وصول غير POST يرجع لصفحة الدخول
    return redirect('accounts:sign_in')




def complete_patient_profile(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    if user.role is not None:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user.role = User.Role.PATIENT
                    user.save()
                    form.save(user=user)

                messages.success(request, "تم إكمال البيانات بنجاح")
                return redirect('patient_dashboard')

            except Exception:
                messages.error(request, "حدث خطأ أثناء حفظ البيانات")
    else:
        form = PatientRegisterForm()

    return render(
        request,
        'accounts/complete_patient_profile.html',
        {'form': form}
    )


def register_specialist_account(request):
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, "تم إنشاء الحساب بنجاح")
                return redirect('complete_specialist_profile')
            except Exception:
                messages.error(request, "حدث خطأ أثناء إنشاء الحساب")
    else:
        form = AccountRegisterForm()

    return render(
        request,
        'accounts/register_specialist_account.html',
        {'form': form}
    )


def complete_specialist_profile(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    if user.role is not None:
        return redirect('specialist_dashboard')

    if request.method == 'POST':
        form = SpecialistRegisterForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user.role = User.Role.SPECIALIST
                    user.save()
                    form.save(user=user)

                messages.success(request, "تم إكمال البيانات بنجاح")
                return redirect('specialist_dashboard')

            except Exception:
                messages.error(request, "حدث خطأ أثناء حفظ البيانات")
    else:
        form = SpecialistRegisterForm()

    return render(
        request,
        'accounts/complete_specialist_profile.html',
        {'form': form}
    )
    
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if not user or not user.is_active:
            messages.error(request, "بيانات الدخول غير صحيحة")
            return redirect('accounts:sign_in')

        login(request, user)
        messages.success(request, "تم تسجيل الدخول بنجاح")

        if not user.role:
            return redirect('accounts:choose_role')

        if user.role == User.Role.PATIENT:
            if not hasattr(user, 'patient'):
                return redirect('accounts:complete_patient_profile')
            return redirect('home')

        if user.role == User.Role.SPECIALIST:
            if not hasattr(user, 'specialist'):
                return redirect('accounts:complete_specialist_profile')
            return redirect('home')

    return render(request, 'accounts/sign_in.html')


def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح")
    return redirect('login')


def specialist_pending(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != User.Role.SPECIALIST:
        return redirect('/')

    return render(request, 'accounts/specialist_pending.html')


#اختيار الدور مريض او اخصائي 
@login_required
def choose_role(request):
    user = request.user

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

        elif selected_role == User.Role.SPECIALIST:
            user.role = User.Role.SPECIALIST
            user.save()
            return redirect('accounts:complete_specialist_profile')

    return render(request, 'accounts/choose_role.html')

