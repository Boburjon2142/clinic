from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models

from accounts.utils import role_required
from .models import Doctor
from .forms import DoctorForm
from django.utils.timezone import localdate
from appointments.models import Appointment


@login_required
def doctor_list(request):
    # Route guard: send Admin2 to "my appointments" instead of 403
    user_role = getattr(request.user, 'role', None)
    if user_role == 'admin2':
        from django.shortcuts import redirect
        return redirect('doctors:my_appointments')
    # Only creator/admin/admin1 can view full list
    if user_role not in ('creator', 'admin', 'admin1') and not request.user.is_superuser:
        from django.contrib.auth import logout
        logout(request)
        from django.shortcuts import redirect
        return redirect('/accounts/login/')
    q = request.GET.get('q', '').strip()
    items = Doctor.objects.all()
    if q:
        items = items.filter(models.Q(full_name__icontains=q) | models.Q(department__icontains=q) | models.Q(phone__icontains=q) | models.Q(room_number__icontains=q))
    today = localdate()
    doctors = (
        items
        .annotate(
            appt_total=models.Count('appointments', distinct=True),
            appt_today=models.Count('appointments', filter=models.Q(appointments__date=today), distinct=True),
        )
        .order_by('full_name')
    )
    return render(request, 'doctors/doctor_list.html', {'doctors': doctors, 'q': q})


@login_required
@role_required(['creator'])
def doctor_create(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.created_by = request.user
            doctor.save()
            messages.success(request, 'Shifokor qo\'shildi')
            return redirect('doctors:list')
    else:
        form = DoctorForm()
    return render(request, 'doctors/doctor_form.html', {'form': form})


@login_required
@role_required(['creator'])
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shifokor ma\'lumotlari yangilandi')
            return redirect('doctors:list')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'doctors/doctor_form.html', {'form': form, 'doctor': doctor})


@login_required
@role_required(['creator'])
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Shifokor o\'chirildi')
        return redirect('doctors:list')
    return render(request, 'doctors/doctor_confirm_delete.html', {'doctor': doctor})


@login_required
@role_required(['creator'])
def doctor_reset_counter(request, pk):
    """Reset a doctor's receipt counter to 0.
    Admin2 may reset only their own profile.
    """
    doc = get_object_or_404(Doctor, pk=pk)
    # Permission: admin2 can only reset their own
    if getattr(request.user, 'role', None) == 'admin2' and doc.created_by_id != request.user.id:
        messages.error(request, "Bu shifokor uchun sanog'ni qayta o'rnatishga ruxsat yo'q")
        return redirect('doctors:list')
    if request.method == 'POST':
        doc.receipt_serial = 0
        doc.save(update_fields=['receipt_serial'])
        messages.success(request, "Kvitansiya sanog'i 0 dan boshlandi")
    # Redirect back to edit page if available, else list
    try:
        return redirect('doctors:edit', pk=doc.pk)
    except Exception:
        return redirect('doctors:list')


@login_required
@role_required(['creator', 'admin', 'admin1', 'admin2', 'admin3'])
def doctor_appointments(request, pk):
    doc = get_object_or_404(Doctor, pk=pk)
    q = request.GET.get('q', '').strip()
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')

    qs = Appointment.objects.select_related('patient', 'complaint').filter(doctor=doc)
    # Date filters (optional)
    from datetime import date
    try:
        if start:
            s = date.fromisoformat(start)
            qs = qs.filter(date__gte=s)
    except Exception:
        start = ''
    try:
        if end:
            e = date.fromisoformat(end)
            qs = qs.filter(date__lte=e)
    except Exception:
        end = ''
    # Search by patient or complaint
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(patient__full_name__icontains=q) | Q(complaint__name__icontains=q))

    export = request.GET.get('export')
    qs = qs.order_by('-date', '-time')

    # Exports (CSV/PDF)
    if export in ('csv', 'pdf'):
        # Clinic name for filename
        from dashboard.models import Setting
        import re
        try:
            clinic_name = (Setting.objects.first().clinic_name or 'Klinika')
        except Exception:
            clinic_name = 'Klinika'
        clinic_slug = re.sub(r'[^A-Za-z0-9_-]+', '_', clinic_name).strip('_') or 'Klinika'
        doc_slug = re.sub(r'[^A-Za-z0-9_-]+', '_', doc.full_name).strip('_') or 'Doctor'

        if export == 'csv':
            from django.http import HttpResponse
            import csv
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = (
                f"attachment; filename={clinic_slug}_{doc_slug}_appointments_{start or 'all'}_{end or 'all'}.csv"
            )
            writer = csv.writer(response)
            writer.writerow(['Sana', 'Vaqt', 'Bemor', 'Shikoyat', 'Narx', 'Holat', 'Kod'])
            for a in qs.iterator():
                code = f"{doc.code_prefix}{(a.doc_no or 0):03d}"
                writer.writerow([
                    a.date.isoformat(),
                    a.time.strftime('%H:%M'),
                    a.patient.full_name,
                    getattr(a.complaint, 'name', ''),
                    f"{a.service_price or ''}",
                    a.get_status_display(),
                    code,
                ])
            return response
        else:
            from django.http import HttpResponse
            from django.template.loader import render_to_string
            context = {
                'clinic_name': clinic_name,
                'doctor': doc,
                'items': qs,
                'start': start,
                'end': end,
            }
            html = render_to_string('doctors/doctor_appointments_export.html', context)
            try:
                from weasyprint import HTML
                pdf = HTML(string=html).write_pdf()
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = (
                    f"attachment; filename={clinic_slug}_{doc_slug}_appointments_{start or 'all'}_{end or 'all'}.pdf"
                )
                return response
            except Exception:
                # Fallback: deliver HTML as download if PDF backend unavailable
                resp = HttpResponse(html, content_type='text/html; charset=utf-8')
                resp['Content-Disposition'] = (
                    f"attachment; filename={clinic_slug}_{doc_slug}_appointments_{start or 'all'}_{end or 'all'}.html"
                )
                return resp

    # Non-export HTML view (limit rows for speed)
    items = qs[:300]
    return render(request, 'doctors/doctor_appointments.html', {
        'doctor': doc,
        'items': items,
        'q': q,
        'start': start,
        'end': end,
    })


@login_required
@role_required(['admin2'])
def my_doctor_appointments(request):
    # Resolve the doctor profile linked to this Admin2
    from django.shortcuts import redirect
    try:
        doc = Doctor.objects.filter(created_by=request.user).first()
        if not doc:
            # Fallback by name
            full_name = (request.user.get_full_name() or request.user.username).strip()
            doc = Doctor.objects.filter(full_name=full_name).first()
        if not doc:
            # Create a doctor profile automatically for this Admin2
            full_name = (request.user.get_full_name() or request.user.username).strip() or request.user.username
            from .utils import next_code_prefix
            doc = Doctor.objects.create(
                full_name=full_name,
                department='Admin 2',
                phone='',
                room_number='',
                created_by=request.user,
                code_prefix=next_code_prefix(),
            )
        return doctor_appointments(request, doc.pk)
    except Exception:
        messages.error(request, "Ma'lumotlarni yuklashda xatolik yuz berdi")
        return redirect('/')



