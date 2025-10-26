from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounts.utils import role_required
 
from patients.models import Patient
from .models import Appointment, AppointmentStatus, Complaint
# from payments.models import Payment, PaymentMethod
from .forms import AppointmentForm, ComplaintForm
from django import forms


@login_required
@role_required(['creator', 'admin', 'admin1', 'staff'])
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            ap = form.save(commit=False)
            ap.created_by = request.user
            ap.status = AppointmentStatus.WAITING
            # Map patient_name -> Patient record (create if not exists)
            full_name = form.cleaned_data.get('patient_name').strip()
            patient, _ = Patient.objects.get_or_create(full_name=full_name, defaults={'phone': ''})
            ap.patient = patient
            # Auto date/time: today + now (local time)
            ap.date = timezone.localdate()
            ap.time = timezone.localtime(timezone.now()).time()
            # Assign sequential document number per doctor
            doc = ap.doctor
            try:
                doc.receipt_serial = (doc.receipt_serial or 0) + 1
            except Exception:
                doc.receipt_serial = 1
            ap.doc_no = doc.receipt_serial
            try:
                doc.save(update_fields=['receipt_serial'])
            except Exception:
                doc.save()
            ap.save()
            messages.success(request, 'Qabul saqlandi (sana/vaqt avtomatik). Kvitansiya tayyor.')
            return redirect(f"/appointments/receipt/{ap.id}/?auto=1")
    else:
        form = AppointmentForm()
    # Patient name suggestions (last 50)
    suggestions = list(Patient.objects.order_by('-created_at').values_list('full_name', flat=True)[:50])
    return render(request, 'appointments/appointment_form.html', {'form': form, 'patient_suggestions': suggestions})


@login_required
@role_required(['creator', 'admin', 'admin1', 'doctor', 'staff', 'admin2', 'admin3'])
def appointment_receipt(request, appointment_id):
    ap = get_object_or_404(Appointment.objects.select_related('doctor', 'patient', 'complaint'), pk=appointment_id)
    # Optional clinic settings
    try:
        from dashboard.models import Setting
        setting = Setting.objects.first()
    except Exception:
        setting = None
    auto = request.GET.get('auto') == '1'
    context = {
        'appointment': ap,
        'doctor': ap.doctor,
        'patient': ap.patient,
        'setting': setting,
        'auto_print': auto,
    }
    from django.template.loader import render_to_string
    html = render_to_string('appointments/receipt.html', context)
    # If auto print requested, return HTML (JS can trigger print dialog)
    if auto:
        from django.http import HttpResponse
        return HttpResponse(html)
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        from django.http import HttpResponse
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="appointment_{ap.id}.pdf"'
        return response
    except Exception:
        from django.http import HttpResponse
        return HttpResponse(html)


@login_required
@role_required(['creator', 'admin', 'doctor', 'staff', 'admin2', 'admin3'])
def appointment_list(request):
    role = getattr(request.user, 'role', None)
    if role == 'admin2':
        return redirect('appointments:queue_price')
    if role == 'admin3':
        return redirect('appointments:queue_cashier')
    items = Appointment.objects.select_related('doctor', 'patient').order_by('-date', '-time')[:100]
    return render(request, 'appointments/appointment_list.html', {'appointments': items})


class SetPriceForm(forms.Form):
    amount = forms.DecimalField(label="Xizmat narxi (so'm)", max_digits=12, decimal_places=2, min_value=0)


@login_required
@role_required(['creator', 'admin', 'admin2'])
def appointment_set_price(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    # Admin2 can only set price for appointments under their doctor profile
    try:
        user_role = getattr(request.user, 'role', None)
    except Exception:
        user_role = None
    if user_role == 'admin2':
        try:
            if not ap.doctor or ap.doctor.created_by_id != request.user.id:
                messages.error(request, "Bu qabul uchun narx belgilashga ruxsat yo'q")
                return redirect('appointments:list')
        except Exception:
            messages.error(request, "Ruxsat tekshiruvida xatolik")
            return redirect('appointments:list')
    if request.method == 'POST':
        form = SetPriceForm(request.POST)
        if form.is_valid():
            ap.service_price = form.cleaned_data['amount']
            ap.save(update_fields=['service_price'])
            messages.success(request, 'Xizmat narxi belgilandi')
            return redirect('appointments:queue_price')
    else:
        form = SetPriceForm(initial={'amount': ap.service_price or 0})
    return render(request, 'appointments/set_price_form.html', {'form': form, 'appointment': ap})


@login_required
@role_required(['creator', 'admin', 'doctor'])
def advance_queue(request, appointment_id, action):
    # This view is deprecated since the doctor queue page was removed.
    # Redirect to appointments list to avoid broken links.
    return redirect('appointments:list')


# Complaint CRUD (creator-only)
@login_required
@role_required(['creator'])
def complaint_list(request):
    q = request.GET.get('q', '').strip()
    items = Complaint.objects.all()
    if q:
        items = items.filter(name__icontains=q)
    items = items.order_by('name')
    return render(request, 'appointments/complaints_list.html', {'items': items, 'q': q})


@login_required
@role_required(['creator'])
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shikoyat qo\'shildi')
            return redirect('complaints:list')
    else:
        form = ComplaintForm()
    return render(request, 'appointments/complaint_form.html', {'form': form})


@login_required
@role_required(['creator'])
def complaint_update(request, pk):
    obj = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shikoyat yangilandi')
            return redirect('complaints:list')
    else:
        form = ComplaintForm(instance=obj)
    return render(request, 'appointments/complaint_form.html', {'form': form, 'obj': obj})


@login_required
@role_required(['creator'])
def complaint_delete(request, pk):
    obj = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Shikoyat o\'chirildi')
        return redirect('complaints:list')
    return render(request, 'appointments/complaint_confirm_delete.html', {'obj': obj})


@login_required
@role_required(['creator', 'admin', 'admin2'])
def appointments_pending_price(request):
    items = (Appointment.objects
             .select_related('doctor', 'patient')
             .filter(service_price__isnull=True)
             .order_by('-date', '-time')[:200])
    ctx = {
        'appointments': items,
        'page_title': "Narx belgilash uchun (Admin 2)",
    }
    return render(request, 'appointments/appointment_list.html', ctx)


@login_required
@role_required(['creator', 'admin', 'admin3'])
def appointments_for_cashier(request):
    items = (Appointment.objects
             .select_related('doctor', 'patient')
             .filter(service_price__isnull=False, payment__isnull=True)
             .order_by('-date', '-time')[:200])
    ctx = {
        'appointments': items,
        'page_title': "To'lov qabul qilish uchun (Admin 3)",
    }
    return render(request, 'appointments/appointment_list.html', ctx)


@login_required
@role_required(['creator', 'admin', 'admin2'])
def appointment_price_receipt(request, appointment_id):
    ap = get_object_or_404(Appointment.objects.select_related('doctor', 'patient', 'complaint'), pk=appointment_id)
    try:
        from dashboard.models import Setting
        setting = Setting.objects.first()
    except Exception:
        setting = None
    auto = request.GET.get('auto') == '1'
    context = {
        'appointment': ap,
        'doctor': ap.doctor,
        'patient': ap.patient,
        'setting': setting,
        'auto_print': auto,
    }
    from django.template.loader import render_to_string
    html = render_to_string('appointments/price_receipt.html', context)
    if auto:
        from django.http import HttpResponse
        return HttpResponse(html)
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        from django.http import HttpResponse
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="appointment_price_{ap.id}.pdf"'
        return response
    except Exception:
        from django.http import HttpResponse
        return HttpResponse(html)
