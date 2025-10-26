from django import forms
from .models import Appointment, Complaint


class AppointmentForm(forms.ModelForm):
    patient_name = forms.CharField(label="Bemor ism familiyasi")
    complaint = forms.ModelChoiceField(
        queryset=Complaint.objects.filter(is_active=True).order_by('name'),
        label='Shikoyat',
        required=False,
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'complaint', 'patient_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs.update({'class': 'form-select'})
        self.fields['complaint'].widget.attrs.update({'class': 'form-select'})
        self.fields['patient_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ism familiya kiriting',
            'autocomplete': 'off',
            'list': 'patients_suggest',
        })


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['name', 'is_active']

