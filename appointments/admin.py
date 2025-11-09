from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("date", "time", "patient", "doctor", "status")
    list_filter = ("status", "doctor", "date")
    search_fields = ("patient__full_name", "doctor__full_name")
