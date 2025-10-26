from django.db import models


class Patient(models.Model):
    full_name = models.CharField("F.I.Sh.", max_length=255)
    phone = models.CharField("Telefon", max_length=30)
    address = models.CharField("Manzil", max_length=255, blank=True)
    birth_date = models.DateField("Tug'ilgan sana", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Bemor"
        verbose_name_plural = "Bemorlar"
