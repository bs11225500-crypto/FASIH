from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from main.email_service import send_email
from specialist.models import Specialist 

from .decorators import staff_required
from django.template.loader import render_to_string
from main.models import ContactMessage
from django.core.paginator import Paginator


from main.models import ContactMessage
from specialist.models import Specialist
from .decorators import staff_required
from django.shortcuts import render

from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import datetime
from dateutil.relativedelta import relativedelta
from accounts.models import User


@staff_required
def dashboard(request):
    total_specialists = Specialist.objects.count()
    pending_specialists = Specialist.objects.filter(
        verification_status=Specialist.VerificationStatus.PENDING
    ).count()
    approved_specialists = Specialist.objects.filter(
        verification_status=Specialist.VerificationStatus.APPROVED
    ).count()

    unread_messages_count = ContactMessage.objects.filter(is_read=False).count()

    raw_data = (
        Specialist.objects
        .annotate(month=TruncMonth("user__date_joined"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    patients_raw_data = (
        User.objects
        .filter(role=User.Role.PATIENT)
        .annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    counts_by_month = {
        item["month"].strftime("%Y-%m"): item["count"]
        for item in raw_data
    }

    patients_counts_by_month = {
        item["month"].strftime("%Y-%m"): item["count"]
        for item in patients_raw_data
    }

    today = datetime.today()

    specialists_by_month = []
    patients_by_month = []

    for i in range(5, -1, -1):
        month_date = today - relativedelta(months=i)
        month_key = month_date.strftime("%Y-%m")

        specialists_by_month.append({
            "month": month_date,
            "count": counts_by_month.get(month_key, 0)
        })
        patients_by_month.append({
            "month": month_date,
            "count": patients_counts_by_month.get(month_key, 0)
        })

    return render(
        request,
        'admin_panel/dashboard.html',
        {
            'total_specialists': total_specialists,
            'pending_specialists': pending_specialists,
            'approved_specialists': approved_specialists,
            'unread_messages_count': unread_messages_count,  
            'specialists_by_month': specialists_by_month,
            'patients_by_month': patients_by_month,
        }
    )

@staff_required
def specialist_list(request):
    specialists = (
        Specialist.objects
        .select_related('user')
        .prefetch_related('certificates')
        .order_by('-id')
    )
    paginator = Paginator(specialists, 10)  # ⭐ 10 أخصائيين في الصفحة
    page_number = request.GET.get('page')
    specialists = paginator.get_page(page_number)
    return render(request, 'admin_panel/specialist_list.html', {'specialists': specialists})


@staff_required
def specialist_review(request, id):
    specialist = get_object_or_404(
        Specialist.objects
        .select_related('user')
        .prefetch_related('certificates', 'appeals'),
        id=id
    )

    appeals = specialist.appeals.order_by('-created_at')

    return render(request, 'admin_panel/specialist_review.html', {
        'specialist': specialist,
        'appeals': appeals,
    })

@staff_required
def approve_specialist(request, id):
    specialist = get_object_or_404(Specialist, id=id)

    if specialist.verification_status == Specialist.VerificationStatus.APPROVED:
        messages.warning(request, 'الأخصائي معتمد مسبقًا')
        return redirect('admin_panel:specialist_list')

    specialist.verification_status = Specialist.VerificationStatus.APPROVED
    specialist.rejection_reason = ''
    specialist.save()

    specialist.appeals.filter(reviewed=False).update(
        reviewed=True,
        accepted=True
    )

    messages.success(request, 'تم اعتماد الأخصائي بنجاح')

    send_email(
        to=specialist.user.email,
        subject="تم اعتماد طلبك | منصة فصيح",
        html_content=render_to_string(
            "accounts/emails/specialist_approved.html",
            {
                "name": specialist.user.get_full_name() or specialist.user.username
            }
        )
    )

    return redirect('admin_panel:specialist_list')





@staff_required
def reject_specialist(request, id):
    specialist = get_object_or_404(Specialist, id=id)

    if specialist.verification_status != Specialist.VerificationStatus.PENDING:
        messages.warning(request, 'تمت مراجعة هذا الأخصائي مسبقًا')
        return redirect('admin_panel:specialist_list')

    if request.method == 'POST':
        reason = request.POST.get('reason')

        if not reason:
            messages.error(request, 'سبب الرفض مطلوب')
            return redirect('admin_panel:reject_specialist', id=id)

        specialist.verification_status = Specialist.VerificationStatus.REJECTED
        specialist.rejection_reason = reason
        specialist.save()

        messages.error(request, 'تم رفض الأخصائي')
        send_email(
            to=specialist.user.email,
            subject="حالة طلبك | منصة فصيح",
            html_content=render_to_string(
                "accounts/emails/specialist_rejected.html",
                {
                    "name": specialist.user.get_full_name() or specialist.user.username,
                    "reason": specialist.rejection_reason
                }
            )
        )

        return redirect('admin_panel:specialist_list')

    return render(request, 'admin_panel/reject_specialist.html', {
        'specialist': specialist
    })


@staff_required
def contact_messages(request):
    unread_qs = ContactMessage.objects.filter(is_read=False).order_by('-created_at')
    read_qs = ContactMessage.objects.filter(is_read=True).order_by('-created_at')

    unread_paginator = Paginator(unread_qs, 6)
    read_paginator = Paginator(read_qs, 6)

    unread_page = request.GET.get('unread_page')
    read_page = request.GET.get('read_page')

    unread_messages = unread_paginator.get_page(unread_page)
    read_messages = read_paginator.get_page(read_page)

    return render(
        request,
        'admin_panel/contact_messages.html',
        {
            'unread_messages': unread_messages,
            'read_messages': read_messages,
        }
    )


@staff_required
def mark_message_read(request, message_id):
    msg = get_object_or_404(ContactMessage, id=message_id)
    msg.is_read = True
    msg.save()
    return redirect('admin_panel:contact_messages')