from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone

from accounts.utils import role_required
from appointments.models import Appointment
from .models import Payment, ExpenseRequest, ExpenseStatus
from .forms import PaymentForm, ExpenseRequestForm
from .utils import qr_base64


@login_required
@role_required(['creator', 'admin', 'admin3'])
def payment_create(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    # If payment already exists, send to its receipt (auto-print)
    try:
        if hasattr(ap, 'payment') and ap.payment is not None:
            messages.info(request, "Ushbu qabul uchun to'lov allaqachon mavjud — kvitansiya ochildi")
            return redirect(f"/payments/receipt/{ap.payment.id}/?auto=1")
    except Exception:
        pass
    if ap.service_price is None:
        messages.error(request, "Avval xizmat narxi belgilanishi kerak (Admin 2).")
        return redirect('appointments:set_price', appointment_id=ap.id)
    if request.method == 'POST':
        # Cashier (Admin 3) only selects method; amount comes from appointment
        from .forms import PaymentMethodForm
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.appointment = ap
            payment.cashier = request.user
            payment.amount = ap.service_price
            try:
                payment.save()
            except IntegrityError:
                # In case of race/double submit, fetch existing and proceed
                try:
                    payment = Payment.objects.get(appointment=ap)
                except Payment.DoesNotExist:
                    raise
            messages.success(request, 'To\'lov saqlandi')
            # Open printable receipt in popup (auto=1)
            return redirect(f"/payments/receipt/{payment.id}/?auto=1")
    else:
        from .forms import PaymentMethodForm
        form = PaymentMethodForm()
    return render(request, 'payments/payment_form.html', {'form': form, 'appointment': ap})


@login_required
@role_required(['creator', 'admin', 'admin3'])
def receipt_pdf(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    # Load optional clinic settings
    try:
        from dashboard.models import Setting
        setting = Setting.objects.first()
    except Exception:
        setting = None
    auto = request.GET.get('auto') == '1'
    context = {
        'payment': payment,
        'appointment': payment.appointment,
        'doctor': payment.appointment.doctor,
        'patient': payment.appointment.patient,
        'setting': setting,
        'auto_print': auto,
    }
    # Render HTML
    from django.template.loader import render_to_string
    html = render_to_string('payments/receipt.html', context)
    # If auto requested, return HTML so JS can print and close
    if auto:
        return HttpResponse(html)
    # Otherwise generate PDF inline if possible
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_{payment.receipt_no}.pdf"'
        return response
    except Exception:
        # Fallback: return HTML inline
        return HttpResponse(html)


# Expenses
@login_required
@role_required(['admin', 'admin1', 'admin2', 'admin3', 'staff', 'creator'])
def expenses_request(request):
    if request.method == 'POST':
        form = ExpenseRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.requested_by = request.user
            obj.status = ExpenseStatus.PENDING
            obj.save()
            messages.success(request, "Xarajat so'rovi yuborildi. Tasdiqlash kutilmoqda.")
            return redirect('payments:expenses_request')
    else:
        form = ExpenseRequestForm()
    my_requests = ExpenseRequest.objects.filter(requested_by=request.user).order_by('-created_at')[:100]
    return render(request, 'payments/expenses_request.html', {'form': form, 'items': my_requests})


@login_required
@role_required(['creator'])
def expenses_review(request):
    # Approve/Reject via POST
    if request.method == 'POST':
        exp_id = request.POST.get('id')
        action = request.POST.get('action')
        obj = get_object_or_404(ExpenseRequest, pk=exp_id)
        if obj.status != ExpenseStatus.PENDING:
            messages.info(request, 'Ushbu so\'rov allaqachon ko\'rib chiqilgan')
            return redirect('payments:expenses_review')
        if action == 'approve':
            obj.status = ExpenseStatus.APPROVED
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            obj.save(update_fields=['status', 'approved_by', 'approved_at'])
            messages.success(request, 'Xarajat so\'rovi tasdiqlandi')
        elif action == 'reject':
            obj.status = ExpenseStatus.REJECTED
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            obj.save(update_fields=['status', 'approved_by', 'approved_at'])
            messages.warning(request, 'Xarajat so\'rovi rad etildi')
        return redirect('payments:expenses_review')
    pending = ExpenseRequest.objects.filter(status=ExpenseStatus.PENDING).select_related('requested_by')[:200]
    recent = ExpenseRequest.objects.exclude(status=ExpenseStatus.PENDING).select_related('requested_by')[:200]
    return render(request, 'payments/expenses_review.html', {'pending': pending, 'recent': recent})
