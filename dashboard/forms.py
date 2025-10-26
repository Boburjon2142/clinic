from django import forms
from .models import Setting


class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = ['clinic_name', 'clinic_address', 'clinic_phone', 'receipt_footer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clinic_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Klinika nomi'})
        self.fields['clinic_phone'].widget.attrs.update({'class': 'form-control', 'placeholder': '+998...'})
        self.fields['clinic_address'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Manzil'})
        self.fields['receipt_footer'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Kvitansiya ostidagi matn'})
