from django.db import models


class Setting(models.Model):
    clinic_name = models.CharField("Klinika nomi", max_length=200, default='Klinika')
    clinic_address = models.CharField("Manzil", max_length=255, blank=True)
    clinic_phone = models.CharField("Telefon", max_length=50, blank=True)
    receipt_footer = models.CharField("Kvitansiya ost qismi", max_length=255, blank=True)
    receipt_serial = models.PositiveIntegerField("Hujjat ketma-ket raqami", default=0)
    last_cleanup = models.DateField("Oxirgi tozalash kuni", null=True, blank=True)

    def __str__(self):
        return self.clinic_name

    class Meta:
        verbose_name = "Sozlama"
        verbose_name_plural = "Sozlamalar"
