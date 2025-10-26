from django.db import models
from django.conf import settings


class Doctor(models.Model):
    full_name = models.CharField("F.I.Sh.", max_length=255)
    department = models.CharField("Bo'lim", max_length=255)
    phone = models.CharField("Telefon", max_length=30)
    room_number = models.CharField("Xona", max_length=30)
    code_prefix = models.CharField("Kvitansiya prefiksi", max_length=2, default='A')
    receipt_serial = models.PositiveIntegerField("Kvitansiya ketma-ket raqami", default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.department})"

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"
