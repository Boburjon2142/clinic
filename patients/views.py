from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import role_required, limit_queryset_for_admin
from .models import Patient
from .forms import PatientForm


@login_required
@role_required(['creator', 'admin', 'admin1', 'staff'])
def patient_list(request):
    patients = Patient.objects.order_by('-created_at')
    patients = limit_queryset_for_admin(patients, request.user)
    patients = patients[:200]
    return render(request, 'patients/patient_list.html', {'patients': patients})


@login_required
@role_required(['creator', 'admin', 'admin1', 'staff'])
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            if request.user.is_authenticated:
                patient.created_by = request.user
            patient.save()
            messages.success(request, 'Bemor qo\'shildi')
            return redirect('patients:list')
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form})

from django.contrib import messages  # duplicate import removed above
from django.shortcuts import redirect  # duplicate import removed above
