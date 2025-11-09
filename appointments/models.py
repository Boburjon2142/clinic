from django.db import models
from django.conf import settings
from doctors.models import Doctor
from patients.models import Patient


class AppointmentStatus(models.TextChoices):
    WAITING = 'waiting', 'Navbatda'
    IN_PROGRESS = 'in_progress', 'Qabulda'
    DONE = 'done', 'Tugallangan'


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, verbose_name='Shifokor', on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, verbose_name='Bemor', on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField('Sana')
    time = models.TimeField('Vaqt')
    status = models.CharField('Holat', max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.WAITING)
    doc_no = models.PositiveIntegerField('Hujjat raqami', null=True, blank=True)
    service_price = models.DecimalField('Xizmat narxi', max_digits=12, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.date} {self.time} - {self.patient} -> {self.doctor}"

    class Meta:
        verbose_name = "Qabul"
        verbose_name_plural = "Qabullar"
