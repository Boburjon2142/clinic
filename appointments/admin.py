from django.contrib import admin
from .models import Complaint, Appointment


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("date", "time", "patient", "doctor", "complaint", "status")
    list_filter = ("status", "doctor", "date")
    search_fields = ("patient__full_name", "doctor__full_name")

