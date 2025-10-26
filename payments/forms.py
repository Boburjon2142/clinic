from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method']


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method']
