from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    patient_name = forms.CharField(label="Bemor ism familiyasi")

    class Meta:
        model = Appointment
        fields = ['doctor', 'patient_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs.update({'class': 'form-select'})
        self.fields['patient_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ism familiya kiriting',
            'autocomplete': 'off',
            'list': 'patients_suggest',
        })

