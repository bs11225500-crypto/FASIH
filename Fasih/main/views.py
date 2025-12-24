from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
from main.email_service import send_email


from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ContactMessage

def home(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message_text = request.POST.get('message')

        ContactMessage.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            message=message_text,
        )

        user_html = render_to_string(
            "main/emails/contact_confirmation.html",
            {
                "name": f"{first_name} {last_name}"
            }
        )

        send_email(
            to=email,
            subject="شكرًا لتواصلك معنا | منصة فصيح",
            html_content=user_html
        )

        messages.success(request, "تم إرسال رسالتك بنجاح ")
        return redirect('main:home')

    return render(request, 'main/home.html')



def about(request):
    return render(request, "main/about.html")




