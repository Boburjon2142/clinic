from datetime import date, timedelta
import json
import re
from django.db.models import Count, Sum, Min
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import role_required
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from payments.models import Payment
try:
    from payments.models import ExpenseRequest, ExpenseStatus
except Exception:
    ExpenseRequest = None
    ExpenseStatus = None
from .models import Setting
from .forms import SettingForm
from accounts.models import User, Roles
from django.db import transaction
from django.utils.timezone import localdate


@login_required
@role_required(['creator', 'admin', 'admin1'])
def admin_dashboard(request):
    from django.utils.timezone import localdate
    # Date range (default: today)
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    today = localdate()
    try:
        start_date = date.fromisoformat(start_param) if start_param else today
    except Exception:
        start_date = today
    try:
        end_date = date.fromisoformat(end_param) if end_param else start_date
    except Exception:
        end_date = start_date

    doctors_count = Doctor.objects.count()
    patients_count = Patient.objects.count()
    range_qs = Appointment.objects.filter(date__gte=start_date, date__lte=end_date)
    range_total = range_qs.count()
    per_doctor = (
        range_qs.values('doctor__id', 'doctor__full_name', 'doctor__department')
        .annotate(total=Count('id'))
        .order_by('-total', 'doctor__full_name')
    )
    total_in_range = sum([row['total'] for row in per_doctor]) if per_doctor else 0
    return render(request, 'dashboard/admin_dashboard.html', {
        'doctors_count': doctors_count,
        'patients_count': patients_count,
        'todays_appointments': range_total,
        'per_doctor': per_doctor,
        'total_today': total_in_range,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    })


def home(request):
    # Simple role-aware landing
    if request.user.is_authenticated and request.user.role in ('creator', 'admin'):
        # Fall through to functional home with cards instead of redirecting
        pass
    # For others, show a basic home with quick links
    today = date.today()
    stats = {
        'patients': Patient.objects.count(),
        'doctors': Doctor.objects.count(),
        'today_appointments': Appointment.objects.filter(date=today).count(),
    }
    try:
        setting = Setting.objects.first()
    except Exception:
        setting = None
    latest = (Appointment.objects
              .select_related('doctor', 'patient')
              .order_by('-date', '-time')[:8])
    return render(request, 'home.html', {
        'stats': stats,
        'setting': setting,
        'latest_appointments': latest,
    })


@login_required
@role_required(['creator'])
def stats_view(request):
    # Last 12 months appointments per month
    start_month = (date.today().replace(day=1) - timedelta(days=330)).replace(day=1)
    monthly = (
        Appointment.objects.filter(date__gte=start_month)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    monthly_labels = [m['month'].strftime('%Y-%m') for m in monthly]
    monthly_data = [m['total'] for m in monthly]

    # Department popularity (last 30 days)
    since = date.today() - timedelta(days=30)
    by_department = (
        Appointment.objects.filter(date__gte=since)
        .values('doctor__department')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    dept_labels = [d['doctor__department'] or 'Noma’lum' for d in by_department]
    dept_data = [d['total'] for d in by_department]

    # Daily patients (last 14 days)
    daily = (
        Appointment.objects.filter(date__gte=date.today() - timedelta(days=14))
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    daily_labels = [d['day'].strftime('%Y-%m-%d') for d in daily]
    daily_data = [d['total'] for d in daily]

    # Payments by method (last 30 days)
    pay = (
        Payment.objects.filter(created_at__date__gte=since)
        .values('method')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    pay_labels = [p['method'] for p in pay]
    pay_data = [float(p['total'] or 0) for p in pay]

    # Per-patient appointment counts (last 30 days)
    per_patient = (
        Appointment.objects.filter(date__gte=since)
        .values('patient__full_name')
        .annotate(total=Count('id'))
        .order_by('-total', 'patient__full_name')
    )
    # Limit to top 15 to keep chart readable
    per_patient = list(per_patient[:15])
    patient_labels = [r['patient__full_name'] or "Noma’lum" for r in per_patient]
    patient_data = [r['total'] for r in per_patient]

    ctx = {
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'dept_labels': json.dumps(dept_labels),
        'dept_data': json.dumps(dept_data),
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'pay_labels': json.dumps(pay_labels),
        'pay_data': json.dumps(pay_data),
        'patient_labels': json.dumps(patient_labels),
        'patient_data': json.dumps(patient_data),
    }
    return render(request, 'dashboard/stats.html', ctx)


@login_required
@role_required(['creator'])
def settings_view(request):
    setting, _ = Setting.objects.get_or_create(pk=1)
    # Inline per-doctor prefix/room update from settings table
    if request.method == 'POST' and request.POST.get('update_doctor_id'):
        try:
            doc_id = int(request.POST.get('update_doctor_id'))
            doc = Doctor.objects.get(pk=doc_id)
            code = (request.POST.get('code_prefix') or '').strip().upper()[:2]
            room = (request.POST.get('room_number') or '').strip()
            dept = (request.POST.get('department') or '').strip()
            updates = []
            if code and code != doc.code_prefix:
                doc.code_prefix = code
                updates.append('code_prefix')
            if room != doc.room_number:
                doc.room_number = room
                updates.append('room_number')
            if dept != doc.department:
                doc.department = dept
                updates.append('department')
            if updates:
                doc.save(update_fields=updates)
                messages.success(request, 'Shifokor sozlamalari saqlandi')
            else:
                messages.info(request, "O'zgarish topilmadi")
        except Exception as e:
            messages.error(request, f'Saqlashda xatolik: {e}')
        return redirect('/admin/dashboard/settings/')
    if request.method == 'POST':
        form = SettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, "Sozlamalar saqlandi")
            return redirect('/admin/dashboard/settings/')
    else:
        form = SettingForm(instance=setting)
    # Doctors list for per-doctor counter reset
    doctors = Doctor.objects.all().order_by('full_name')
    return render(request, 'dashboard/settings_form.html', {'form': form, 'setting': setting, 'doctors': doctors})


@login_required
@role_required(['creator'])
def clear_patients(request):
    """Dangerous action: remove all patients and their related appointments/payments.
    Only accessible from settings via POST.
    """
    if request.method != 'POST':
        return redirect('settings')
    from patients.models import Patient
    from appointments.models import Appointment
    from payments.models import Payment
    try:
        with transaction.atomic():
            p_count = Patient.objects.count()
            a_count = Appointment.objects.count()
            pay_count = Payment.objects.count()
            # Deleting patients cascades to appointments and payments via FK
            Patient.objects.all().delete()
        messages.success(request, f"Bemorlar bazasi tozalandi. O'chirildi: bemorlar {p_count} ta, qabul {a_count} ta, to'lov {pay_count} ta.")
    except Exception as e:
        messages.error(request, f"Tozalashda xatolik: {e}")
    return redirect('settings')


# Users list (creator and admin can view)
@login_required
@role_required(['creator'])
def users_manage(request):
    users = User.objects.all().order_by('username')
    return render(request, 'dashboard/users_manage.html', {'users': users})


@login_required
@role_required(['creator'])
def make_admin(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.role = Roles.ADMIN
        user.is_staff = True
        user.save()
        messages.success(request, f"{user.username} — admin qilib qo'yildi")
    return redirect('users_manage')


@login_required
@role_required(['creator'])
def remove_admin(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        # Prevent acting on older or creator accounts
        try:
            if user.role == Roles.CREATOR or (hasattr(user, "date_joined") and hasattr(request.user, "date_joined") and user.date_joined < request.user.date_joined):
                messages.error(request, "Sizdan oldin yaratilgan yoki Creator foydalanuvchini o'chira olmaysiz")
                return redirect('users_manage')
        except Exception:
            pass
        if user.role == Roles.ADMIN:
            user.role = Roles.STAFF
        user.is_staff = False
        user.save()
        messages.success(request, f"{user.username} dan admin huquqlari olib tashlandi")
    return redirect('users_manage')


# Data cleanup: remove patients, their appointments and payments, keep expenses
@login_required
@role_required(['creator'])
def clear_patients(request):
    # Summaries for confirmation
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_payments = Payment.objects.count()
    try:
        total_expenses = ExpenseRequest.objects.count()
    except Exception:
        total_expenses = 0

    if request.method == 'POST':
        with transaction.atomic():
            # Delete payments first (redundant, but clearer) then appointments and patients
            Payment.objects.all().delete()
            Appointment.objects.all().delete()
            Patient.objects.all().delete()
            # Mark cleanup date in settings
            try:
                s = Setting.objects.first()
                if s:
                    s.last_cleanup = localdate()
                    s.save(update_fields=['last_cleanup'])
            except Exception:
                pass
        messages.success(request, "Bemorlar bazasi tozalandi. Xarajatlar saqlab qolindi.")
        return redirect('/admin/dashboard/settings/')

    return render(request, 'dashboard/confirm_clear_patients.html', {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_payments': total_payments,
        'total_expenses': total_expenses,
    })


@login_required
@role_required(['creator'])
def toggle_active(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        # Prevent changing older or Creator accounts
        try:
            if user.role == Roles.CREATOR or (hasattr(user, "date_joined") and hasattr(request.user, "date_joined") and user.date_joined < request.user.date_joined):
                messages.error(request, "Sizdan oldin yaratilgan yoki Creator foydalanuvchini o'zgartira olmaysiz")
                return redirect('users_manage')
        except Exception:
            pass
        user.is_active = not user.is_active
        user.save()
        state = 'faollashtirildi' if user.is_active else 'bloklandi'
        messages.success(request, f"{user.username} {state}")
    return redirect('users_manage')


# Add user (admin only)
@login_required
@role_required(['creator'])
def user_add(request):
    from accounts.forms import AdminCreateUserForm
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If role is Admin2, ensure Doctor record exists so it appears in lists
            try:
                from accounts.models import Roles
                if user.role == Roles.ADMIN2:
                    from doctors.models import Doctor
                    from doctors.utils import next_code_prefix
                    full_name = (user.get_full_name() or user.username).strip()
                    prefix = next_code_prefix()
                    Doctor.objects.get_or_create(
                        created_by=user,
                        defaults={
                            'full_name': full_name or user.username,
                            'department': 'Admin 2',
                            'phone': '',
                            'room_number': '',
                            'code_prefix': prefix,
                        }
                    )
            except Exception:
                pass
            messages.success(request, f"Foydalanuvchi yaratildi: {user.username}")
            return redirect('users_manage')
    else:
        form = AdminCreateUserForm()
    return render(request, 'dashboard/user_add.html', {'form': form})


@login_required
@role_required(['creator'])
def reset_doc_counter(request):
    setting, _ = Setting.objects.get_or_create(pk=1)
    if request.method == 'POST':
        setting.receipt_serial = 0
        setting.save()
        messages.success(request, 'Hujjat raqami 0 dan boshlashga qayta o‘rnatildi')
        return redirect('/admin/dashboard/settings/')
    # Safety fallback
    messages.info(request, f"Joriy hujjat raqami: {setting.receipt_serial}")
    return redirect('/admin/dashboard/settings/')
# Override older stats_view implementation with an improved version
@login_required
@role_required(['creator'])
def stats_view(request):
    today = date.today()

    # 30 kunlik qabul soni (har kun)
    since_30 = today - timedelta(days=29)
    agg30 = (
        Appointment.objects.filter(date__gte=since_30)
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(total=Count('id'))
    )
    # On some DB backends TruncDay returns date, on others datetime
    counts30 = {
        (row['day'].date() if hasattr(row['day'], 'date') else row['day']): row['total']
        for row in agg30
    }
    days30 = [since_30 + timedelta(days=i) for i in range(30)]
    last30_labels = [d.strftime('%Y-%m-%d') for d in days30]
    last30_data = [counts30.get(d, 0) for d in days30]

    # Bo'limlar bo'yicha tashriflar (oxirgi 30 kun) — pie chart ma'lumotlari
    by_department = (
        Appointment.objects.filter(date__gte=since_30)
        .values('doctor__department')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    dept_labels = [d['doctor__department'] or "Noma'lum" for d in by_department]
    dept_data = [d['total'] for d in by_department]

    # 1 hafta davomida noyob bemorlar soni (har kun)
    since_7 = today - timedelta(days=6)
    weekly = (
        Appointment.objects.filter(date__gte=since_7)
        .values('date')
        .annotate(total=Count('patient', distinct=True))
        .order_by('date')
    )
    w_counts = {row['date']: row['total'] for row in weekly}
    week_days = [since_7 + timedelta(days=i) for i in range(7)]
    week_labels = [d.strftime('%Y-%m-%d') for d in week_days]
    week_data = [w_counts.get(d, 0) for d in week_days]

    # Har bir shifokorning (oxirgi 30 kun) JAMI QABULLARI soni
    per_doctor_week = (
        Appointment.objects.filter(date__gte=since_30)
        .values('doctor__id', 'doctor__full_name')
        .annotate(total=Count('id'))
        .order_by('doctor__full_name')
    )

    # Admin 3 (Kassir) tasdiqlagan to'lovlar uchun sana oralig'i (default: oxirgi 30 kun)
    pay_start_param = request.GET.get('pay_start')
    pay_end_param = request.GET.get('pay_end')
    try:
        pay_start = date.fromisoformat(pay_start_param) if pay_start_param else since_30
    except Exception:
        pay_start = since_30
    try:
        pay_end = date.fromisoformat(pay_end_param) if pay_end_param else today
    except Exception:
        pay_end = today
    if pay_end < pay_start:
        pay_start, pay_end = pay_end, pay_start

    admin3_qs = Payment.objects.select_related('appointment__patient', 'appointment__doctor', 'cashier') \
        .filter(created_at__date__gte=pay_start, created_at__date__lte=pay_end, cashier__role=Roles.ADMIN3) \
        .order_by('-created_at')

    # Jami summa (filtr bo'yicha)
    from django.db.models import Sum as _Sum
    total_row = admin3_qs.aggregate(total=_Sum('amount'))
    admin3_total = float(total_row.get('total') or 0)

    # Export handlers (CSV/PDF)
    export = request.GET.get('export')
    # Klinik nomi slugini fayl nomi uchun tayyorlash
    try:
        clinic_name = Setting.objects.first().clinic_name or 'Klinika'
    except Exception:
        clinic_name = 'Klinika'
    clinic_slug = re.sub(r'[^A-Za-z0-9_-]+', '_', clinic_name).strip('_') or 'Klinika'

    if export == 'csv':
        from django.http import HttpResponse
        import csv
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = (
            f"attachment; filename={clinic_slug}_admin3_payments_{pay_start.isoformat()}_{pay_end.isoformat()}.csv"
        )
        writer = csv.writer(response)
        writer.writerow(['Sana', 'Bemor', 'Shifokor', 'Miqdor', 'Usul', 'Kassir', 'Kvitansiya'])
        for p in admin3_qs:
            writer.writerow([
                p.created_at.strftime('%Y-%m-%d %H:%M'),
                getattr(p.appointment.patient, 'full_name', ''),
                getattr(p.appointment.doctor, 'full_name', ''),
                f"{p.amount}",
                p.get_method_display(),
                getattr(p.cashier, 'username', ''),
                p.receipt_no,
            ])
        # Jami qator
        writer.writerow([])
        writer.writerow(['Jami', '', '', f"{admin3_total}", '', '', ''])
        return response
    elif export == 'pdf':
        from django.http import HttpResponse
        from django.template.loader import render_to_string
        export_ctx = {
            'items': admin3_qs,
            'pay_start': pay_start,
            'pay_end': pay_end,
            'clinic_name': clinic_name,
            'total': admin3_total,
        }
        html = render_to_string('dashboard/admin3_payments_export.html', export_ctx)
        try:
            from weasyprint import HTML
            pdf = HTML(string=html).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = (
                f"attachment; filename={clinic_slug}_admin3_payments_{pay_start.isoformat()}_{pay_end.isoformat()}.pdf"
            )
            return response
        except Exception:
            # Fallback: build a minimal PDF without external libs
            def _esc(s: str) -> str:
                return (s or '').replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')

            def build_simple_pdf(title: str, subtitle: str, rows):
                # Basic A4 page
                width, height = 595, 842
                margin = 36
                lh = 14
                max_lines = int((height - margin*2) / lh) - 2

                pages = []
                lines = []
                lines.append(title)
                lines.append(subtitle)
                header = 'Sana | Bemor | Shifokor | Miqdor | Usul | Kassir | Kvitansiya'
                lines.append(header)
                lines.append('-' * min(len(header), 120))
                for r in rows:
                    line = ' | '.join([
                        r.get('date',''), r.get('patient',''), r.get('doctor',''),
                        r.get('amount',''), r.get('method',''), r.get('cashier',''), r.get('receipt','')
                    ])
                    lines.append(line)

                # Paginate
                for i in range(0, len(lines), max_lines):
                    page_lines = lines[i:i+max_lines]
                    y = height - margin
                    text = []
                    text.append('BT')
                    text.append('/F1 10 Tf')
                    text.append(f'{margin} {y} Td')
                    text.append(f'{lh} TL')
                    for idx, ln in enumerate(page_lines):
                        if idx == 0:
                            text.append('/F1 12 Tf')
                        elif idx == 1:
                            text.append('/F1 10 Tf')
                        esc = _esc(ln)[:180]
                        text.append(f'({esc}) Tj')
                        text.append('T*')
                    text.append('ET')
                    stream = '\n'.join(text).encode('utf-8')
                    pages.append(stream)

                # Build PDF objects
                objects = []
                xref = []
                def add_obj(data: bytes) -> int:
                    offset = sum(len(o) for o in objects)
                    xref.append(offset)
                    objects.append(data)
                    return len(xref)  # object number (1-based)

                # Font
                font_obj_num = add_obj(b"1 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
                # Pages container (placeholder; we will fill kids later)
                kids_refs = []
                # Build page + content objects
                page_nums = []
                for stream in pages:
                    contents_str = b"stream\n" + stream + b"\nendstream"
                    cont_obj_num = add_obj((f"{0} 0 obj\n<< /Length {len(stream)} >>\n".encode('ascii') + contents_str + b"\nendobj\n"))
                    page_dict = (
                        f"{0} 0 obj\n<< /Type /Page /Parent {0} 0 R /MediaBox [0 0 595 842] ".encode('ascii') +
                        f"/Resources << /Font << /F1 {font_obj_num} 0 R >> >> ".encode('ascii') +
                        f"/Contents {cont_obj_num} 0 R >>\nendobj\n".encode('ascii')
                    )
                    page_num = add_obj(page_dict)
                    kids_refs.append(f"{page_num} 0 R")
                    page_nums.append(page_num)

                # Now add Pages object
                pages_obj_num = add_obj((
                    f"{0} 0 obj\n<< /Type /Pages /Count {len(page_nums)} /Kids [".encode('ascii') +
                    ' '.join(kids_refs).encode('ascii') + b"] >>\nendobj\n"
                ))

                # Patch parent refs in page dicts (not fully patching; rebuild pages with correct parent)
                objects_fixed = []
                xref = []
                def add_obj2(s: bytes) -> int:
                    offset = sum(len(o) for o in objects_fixed)
                    xref.append(offset)
                    objects_fixed.append(s)
                    return len(xref)

                font_obj_num = add_obj2(b"1 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
                page_nums = []
                for stream in pages:
                    cont_num = add_obj2((
                        f"{0} 0 obj\n<< /Length {len(stream)} >>\n".encode('ascii') + b"stream\n" + stream + b"\nendstream\nendobj\n"
                    ))
                    page_num = add_obj2((
                        f"{0} 0 obj\n<< /Type /Page /Parent {0} 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_obj_num} 0 R >> >> /Contents {cont_num} 0 R >>\nendobj\n".encode('ascii')
                    ))
                    page_nums.append(page_num)
                pages_obj_num = add_obj2((
                    f"{0} 0 obj\n<< /Type /Pages /Count {len(page_nums)} /Kids [".encode('ascii') +
                    ' '.join([f"{n} 0 R" for n in page_nums]).encode('ascii') + b"] >>\nendobj\n"
                ))
                catalog_num = add_obj2((
                    f"{0} 0 obj\n<< /Type /Catalog /Pages {pages_obj_num} 0 R >>\nendobj\n".encode('ascii')
                ))

                # Assemble file
                pdf = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
                pdf.extend(objects_fixed)
                xref_offset = sum(len(p) for p in pdf)
                pdf.append(b"xref\n0 " + str(len(objects_fixed)+1).encode('ascii') + b"\n")
                pdf.append(b"0000000000 65535 f \n")
                pos = 0
                for o in objects_fixed:
                    pdf.append(str(pos).zfill(10).encode('ascii') + b" 00000 n \n")
                    pos += len(o)
                pdf.append(b"trailer\n<< /Size " + str(len(objects_fixed)+1).encode('ascii') + b" /Root " + str(catalog_num).encode('ascii') + b" 0 R >>\nstartxref\n" + str(xref_offset).encode('ascii') + b"\n%%EOF")
                return b''.join(pdf)

            # Build rows from queryset
            rows = []
            for p in admin3_qs:
                rows.append({
                    'date': p.created_at.strftime('%Y-%m-%d %H:%M'),
                    'patient': getattr(p.appointment.patient, 'full_name', ''),
                    'doctor': getattr(p.appointment.doctor, 'full_name', ''),
                    'amount': f"{p.amount}",
                    'method': p.get_method_display(),
                    'cashier': getattr(p.cashier, 'username', ''),
                    'receipt': p.receipt_no,
                })
            title = f"{clinic_name} — Admin 3 tasdiqlagan to'lovlar"
            subtitle = f"{pay_start.isoformat()} — {pay_end.isoformat()}  |  Jami: {admin3_total}"
            pdf_bytes = build_simple_pdf(title, subtitle, rows)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = (
                f"attachment; filename={clinic_slug}_admin3_payments_{pay_start.isoformat()}_{pay_end.isoformat()}.pdf"
            )
            return response

    # Finance range: revenue (payments) vs expenses (approved requests)
    try:
        fin_start_param = request.GET.get('fin_start')
        fin_end_param = request.GET.get('fin_end')
    except Exception:
        fin_start_param = fin_end_param = None
    from datetime import timedelta as _td
    today = date.today()
    # Default to full history: earliest of payments/expenses -> today
    if not fin_start_param:
        try:
            pmin = Payment.objects.aggregate(m=Min('created_at'))['m']
        except Exception:
            pmin = None
        try:
            emin = ExpenseRequest.objects.aggregate(m=Min('approved_at'))['m'] if ExpenseRequest else None
        except Exception:
            emin = None
        first = None
        for d in [pmin, emin]:
            if d and (first is None or d.date() < first):
                first = d.date()
        fin_start = first or (today - _td(days=30))
    else:
        fin_start = date.fromisoformat(fin_start_param)
    fin_end = date.fromisoformat(fin_end_param) if fin_end_param else today

    # Aggregate daily
    from collections import defaultdict
    rev_daily = defaultdict(float)
    for row in (Payment.objects
                .filter(created_at__date__gte=fin_start, created_at__date__lte=fin_end)
                .annotate(day=TruncDay('created_at'))
                .values('day')
                .annotate(total=Sum('amount'))
                .order_by('day')):
        rev_daily[row['day'].date()] = float(row['total'] or 0)

    exp_daily = defaultdict(float)
    if ExpenseRequest and ExpenseStatus:
        for row in (ExpenseRequest.objects
                    .filter(status=ExpenseStatus.APPROVED,
                            approved_at__date__gte=fin_start,
                            approved_at__date__lte=fin_end)
                    .annotate(day=TruncDay('approved_at'))
                    .values('day')
                    .annotate(total=Sum('amount'))
                    .order_by('day')):
            exp_daily[row['day'].date()] = float(row['total'] or 0)

    # Build cumulative series
    labels = []
    rev_series = []
    exp_series = []
    rows = []
    r_sum = 0.0
    e_sum = 0.0
    d = fin_start
    while d <= fin_end:
        labels.append(d.strftime('%Y-%m-%d'))
        day_rev = round(rev_daily.get(d, 0.0), 2)
        day_exp = round(exp_daily.get(d, 0.0), 2)
        day_profit = round(day_rev - day_exp, 2)
        r_sum = round(r_sum + day_rev, 2)
        e_sum = round(e_sum + day_exp, 2)
        rev_series.append(r_sum)
        exp_series.append(e_sum)
        rows.append({
            'date': d.strftime('%Y-%m-%d'),
            'rev': day_rev,
            'exp': day_exp,
            'profit': day_profit,
            'rev_cum': r_sum,
            'exp_cum': e_sum,
            'profit_cum': round(r_sum - e_sum, 2),
        })
        d += _td(days=1)

    finance = {
        'labels': labels,
        'revenue': rev_series,
        'expenses': exp_series,
        'revenue_total': round(r_sum, 2),
        'expenses_total': round(e_sum, 2),
        'profit_total': round(r_sum - e_sum, 2),
        'fin_start': fin_start.isoformat(),
        'fin_end': fin_end.isoformat(),
    }

    # Finance exports (CSV / PDF)
    fin_export = request.GET.get('fin_export')
    if fin_export == 'csv':
        import csv
        from io import StringIO
        sio = StringIO()
        writer = csv.writer(sio)
        writer.writerow(['Sana', 'Tushum', 'Xarajat', 'Foyda', 'Tushum (kumul.)', 'Xarajat (kumul.)', 'Foyda (kumul.)'])
        for r in rows:
            writer.writerow([r['date'], r['rev'], r['exp'], r['profit'], r['rev_cum'], r['exp_cum'], r['profit_cum']])
        from django.http import HttpResponse
        resp = HttpResponse(sio.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f"attachment; filename=finance_{finance['fin_start']}_{finance['fin_end']}.csv"
        return resp
    if fin_export == 'pdf':
        # Try WeasyPrint first; if not available, generate a minimal PDF bytes fallback
        try:
            from weasyprint import HTML
            # Simple HTML rendering via WeasyPrint
            table_rows = ''.join([
                f"<tr><td>{r['date']}</td><td style='text-align:right'>{r['rev']}</td><td style='text-align:right'>{r['exp']}</td><td style='text-align:right'>{r['profit']}</td>"
                f"<td style='text-align:right'>{r['rev_cum']}</td><td style='text-align:right'>{r['exp_cum']}</td><td style='text-align:right'>{r['profit_cum']}</td></tr>"
                for r in rows
            ])
            html = f"""
            <html><head><meta charset='utf-8'><style>
            body{{ font-family: DejaVu Sans, Arial, sans-serif; font-size:12px; }}
            h3{{ margin:0 0 8px 0; }} table{{ width:100%; border-collapse:collapse; }}
            th,td{{ border:1px solid #000; padding:4px; }} th{{ background:#f2f2f2; }}
            </style></head><body>
            <h3>Tushum va xarajatlar: {finance['fin_start']} — {finance['fin_end']}</h3>
            <table>
              <thead><tr>
                <th>Sana</th><th>Tushum</th><th>Xarajat</th><th>Foyda</th>
                <th>Tushum (kumul.)</th><th>Xarajat (kumul.)</th><th>Foyda (kumul.)</th>
              </tr></thead>
              <tbody>{table_rows}</tbody>
            </table>
            <p><strong>Jami tushum:</strong> {finance['revenue_total']} &nbsp; 
               <strong>Jami xarajat:</strong> {finance['expenses_total']} &nbsp; 
               <strong>Foyda:</strong> {finance['profit_total']}</strong></p>
            </body></html>
            """
            pdf = HTML(string=html).write_pdf()
            from django.http import HttpResponse
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f"attachment; filename=finance_{finance['fin_start']}_{finance['fin_end']}.pdf"
            return response
        except Exception:
            pass

        # Minimal PDF fallback (no external dependencies)
        def _esc(s: str) -> str:
            # Escape for PDF string syntax and force ASCII-friendly characters
            s = (s or '').replace('\u2014', '-').replace('\u2013', '-')  # dashes
            s = s.replace('—', '-').replace('–', '-')
            return s.replace('\\', r'\\\\').replace('(', r'\\(').replace(')', r'\\)')

        # Build fixed-width table in plain text
        def fmt_row(d):
            return f"{d['date']:<12} {d['rev']:>12} {d['exp']:>12} {d['profit']:>12} {d['rev_cum']:>14} {d['exp_cum']:>14} {d['profit_cum']:>14}"

        lines = [
            f"Tushum va xarajatlar: {finance['fin_start']} - {finance['fin_end']}",
            "",
            "Sana         Tushum       Xarajat       Foyda       Tushum(k)     Xarajat(k)      Foyda(k)",
            "---------------------------------------------------------------------------------------------",
        ]
        lines += [fmt_row(r) for r in rows[:800]]  # cap
        lines += [
            "",
            f"Jami tushum: {finance['revenue_total']}    Jami xarajat: {finance['expenses_total']}    Foyda: {finance['profit_total']}",
        ]

        # Create a simple one-page PDF with Helvetica
        width, height = 595, 842  # A4 portrait
        y = height - 60
        leading = 14
        # Use monospaced font for neat columns
        content_lines = ["BT /F1 11 Tf {} TL 40 {} Td".format(leading, y)]
        for i, text in enumerate(lines):
            content_lines.append(f"({_esc(text)}) Tj")
            content_lines.append("T*")
        content_lines.append("ET")
        content = "\n".join(content_lines).encode('latin-1', 'replace')

        objects = []
        def obj(data):
            objects.append(data)
            return len(objects)

        # 1. Font
        font_obj = obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
        # 2. Contents
        stream = b"<< /Length " + str(len(content)).encode('ascii') + b" >>\nstream\n" + content + b"\nendstream"
        contents_obj = obj(stream)
        # 3. Page
        page_obj = obj(b"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 595 842] /Contents " + str(contents_obj).encode('ascii') + b" 0 R /Resources << /Font << /F1 " + str(font_obj).encode('ascii') + b" 0 R >> >> >>")
        # 4. Pages
        pages_obj = obj(b"<< /Type /Pages /Kids [ " + str(page_obj).encode('ascii') + b" 0 R ] /Count 1 >>")
        # 5. Catalog
        catalog_obj = obj(b"<< /Type /Catalog /Pages " + str(pages_obj).encode('ascii') + b" 0 R >>")

        # Assemble PDF
        xref = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
        offsets = [0]
        for i, o in enumerate(objects, 1):
            offsets.append(sum(len(p) for p in xref))
            xref.append(f"{i} 0 obj\n".encode('ascii'))
            xref.append(o + b"\nendobj\n")
        xref_pos = sum(len(p) for p in xref)
        xref.append(b"xref\n0 " + str(len(objects)+1).encode('ascii') + b"\n")
        xref.append(b"0000000000 65535 f \n")
        pos = 0
        for i in range(1, len(objects)+1):
            # simple incremental; we already captured offsets above, but compute now
            xref.append(str(offsets[i]).zfill(10).encode('ascii') + b" 00000 n \n")
        xref.append(b"trailer\n<< /Size " + str(len(objects)+1).encode('ascii') + b" /Root " + str(catalog_obj).encode('ascii') + b" 0 R >>\nstartxref\n" + str(xref_pos).encode('ascii') + b"\n%%EOF")
        pdf_bytes = b"".join(xref)
        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f"attachment; filename=finance_{finance['fin_start']}_{finance['fin_end']}.pdf"
        return response

    ctx = {
        'last30_labels': json.dumps(last30_labels),
        'last30_data': json.dumps(last30_data),
        'dept_labels': json.dumps(dept_labels),
        'dept_data': json.dumps(dept_data),
        'week_labels': json.dumps(week_labels),
        'week_data': json.dumps(week_data),
        'per_doctor_week': list(per_doctor_week),
        'admin3_payments': admin3_qs,
        'pay_start': pay_start.isoformat(),
        'pay_end': pay_end.isoformat(),
        'admin3_total': admin3_total,
        'finance_labels': json.dumps(finance['labels']),
        'finance_rev': json.dumps(finance['revenue']),
        'finance_exp': json.dumps(finance['expenses']),
        'finance_rev_total': finance['revenue_total'],
        'finance_exp_total': finance['expenses_total'],
        'finance_profit_total': finance['profit_total'],
        'fin_start': finance['fin_start'],
        'fin_end': finance['fin_end'],
        'finance_rows': rows,
    }
    return render(request, 'dashboard/stats.html', ctx)


# Additional role assignment helpers for Creator
@login_required
@role_required(['creator'])
def make_admin1(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.role = Roles.ADMIN1
        user.is_staff = True
        user.save()
        messages.success(request, f"{user.username} ga Admin 1 (Menejer) huquqi berildi")
    return redirect('users_manage')


@login_required
@role_required(['creator'])
def make_admin2(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.role = Roles.ADMIN2
        user.is_staff = True
        user.save()
        # Ensure Admin2 appears in doctors list
        try:
            from doctors.models import Doctor
            from doctors.utils import next_code_prefix
            full_name = (user.get_full_name() or user.username).strip()
            # Allocate unique code prefix
            prefix = next_code_prefix()
            Doctor.objects.get_or_create(
                created_by=user,
                defaults={
                    'full_name': full_name or user.username,
                    'department': "Admin 2",
                    'phone': '',
                    'room_number': '',
                    'code_prefix': prefix,
                }
            )
        except Exception:
            pass
        messages.success(request, f"{user.username} ga Admin 2 (Narx) huquqi berildi va shifokorlar ro'yxatiga qo'shildi")
    return redirect('users_manage')


@login_required
@role_required(['creator'])
def make_admin3(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.role = Roles.ADMIN3
        user.is_staff = True
        user.save()
        messages.success(request, f"{user.username} ga Admin 3 (Kassir) huquqi berildi")
    return redirect('users_manage')

@login_required
@role_required(['creator'])
def remove_admin(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        # Prevent acting on older or creator accounts
        try:
            if user.role == Roles.CREATOR or (hasattr(user, "date_joined") and hasattr(request.user, "date_joined") and user.date_joined < request.user.date_joined):
                messages.error(request, "Sizdan oldin yaratilgan yoki Creator foydalanuvchini o'chira olmaysiz")
                return redirect('users_manage')
        except Exception:
            pass
        if user.role == Roles.ADMIN:
            user.role = Roles.STAFF
        user.is_staff = False
        user.save()
        messages.success(request, f"{user.username} dan admin huquqlari olib tashlandi")
    return redirect('users_manage')




