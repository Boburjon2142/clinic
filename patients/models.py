from django.db import models
from django.conf import settings


class Patient(models.Model):
    full_name = models.CharField("F.I.Sh.", max_length=255)
    phone = models.CharField("Telefon", max_length=30)
    address = models.CharField("Manzil", max_length=255, blank=True)
    birth_date = models.DateField("Tug'ilgan sana", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_created')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Bemor"
        verbose_name_plural = "Bemorlar"
