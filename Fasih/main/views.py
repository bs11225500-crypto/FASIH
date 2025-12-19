from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages



def home(request):
    return render(request, "main/home.html")

def home(request):
    if request.method == 'POST':
        # نقدر نستخدم البيانات لاحقًا
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        messages.success(request, "تم إرسال رسالتك بنجاح، سنعود لك قريبًا")
        return redirect('home')

    return render(request, 'main/home.html')



def about(request):
    return render(request, "main/about.html")
