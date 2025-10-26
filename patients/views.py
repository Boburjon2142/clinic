from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import role_required
from .models import Patient
from .forms import PatientForm


@login_required
@role_required(['creator', 'admin', 'admin1', 'staff'])
def patient_list(request):
    patients = Patient.objects.order_by('-created_at')[:200]
    return render(request, 'patients/patient_list.html', {'patients': patients})


@login_required
@role_required(['creator', 'admin', 'admin1', 'staff'])
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bemor qo\'shildi')
            return redirect('patients:list')
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form})
