from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from main.email_service import send_email
from specialist.models import Specialist
from .decorators import staff_required
from django.template.loader import render_to_string



# Create your views here.

@staff_required
def dashboard(request):
    total_specialists = Specialist.objects.count()
    pending_specialists = Specialist.objects.filter(
        verification_status=Specialist.VerificationStatus.PENDING
    ).count()
    approved_specialists = Specialist.objects.filter(
        verification_status=Specialist.VerificationStatus.APPROVED
    ).count()

    return render(
        request,
        'admin_panel/dashboard.html',
        {
            'total_specialists': total_specialists,
            'pending_specialists': pending_specialists,
            'approved_specialists': approved_specialists,
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

    return render(request, 'admin_panel/specialist_list.html', {
        'specialists': specialists
    })


@staff_required
def specialist_review(request, id):
    specialist = get_object_or_404(
        Specialist.objects
        .select_related('user')
        .prefetch_related('certificates'),
        id=id
    )

    return render(request, 'admin_panel/specialist_review.html', {
        'specialist': specialist
    })
@staff_required
def approve_specialist(request, id):
    specialist = get_object_or_404(Specialist, id=id)

    if specialist.verification_status != Specialist.VerificationStatus.PENDING:
        messages.warning(request, 'تمت مراجعة هذا الأخصائي مسبقًا')
        return redirect('admin_panel:specialist_list')

    specialist.verification_status = Specialist.VerificationStatus.APPROVED
    specialist.rejection_reason = ''
    specialist.save()

    messages.success(request, 'تم اعتماد الأخصائي بنجاح')
    send_email(
        to=specialist.user.email,
        subject="تم اعتماد طلبك | منصة فصيح",
        html_content=render_to_string(
            "accounts/emails/specialist_approved.html",
            {"name": specialist.user.get_full_name() or specialist.user.username}
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

