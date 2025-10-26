from django import forms
from .models import Doctor


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['full_name', 'department', 'phone', 'room_number', 'code_prefix']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code_prefix'].widget.attrs.update({
            'class': 'form-control',
            'maxlength': 2,
            'placeholder': 'Masalan: A yoki B',
        })
