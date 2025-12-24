from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages




# main/views.py
from django.shortcuts import render, redirect
from .models import ContactMessage

def home(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message'),
        )

        return redirect('main:home')  # أو نفس الصفحة

    return render(request, 'main/home.html')



def about(request):
    return render(request, "main/about.html")




