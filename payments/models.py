from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from appointments.models import Appointment


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Naqd'
    CARD = 'card', 'Karta'


class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, verbose_name='Qabul', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField('Miqdor', max_digits=12, decimal_places=2)
    method = models.CharField("Usul", max_length=20, choices=PaymentMethod.choices)
    created_at = models.DateTimeField("Yaratilgan", auto_now_add=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kassir', on_delete=models.SET_NULL, null=True, blank=True)
    receipt_no = models.CharField('Kvitansiya №', max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            self.receipt_no = get_random_string(10).upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_no} — {self.amount}"

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
