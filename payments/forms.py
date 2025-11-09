from django import forms
from .models import Payment, ExpenseRequest


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method']


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method']


class ExpenseRequestForm(forms.ModelForm):
    class Meta:
        model = ExpenseRequest
        fields = ['amount', 'comment']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'Miqdor'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Izoh'}),
        }
