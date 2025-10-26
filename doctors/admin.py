from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'code_prefix', 'receipt_serial', 'phone', 'room_number', 'created_at')
    search_fields = ('full_name', 'department', 'phone', 'room_number', 'code_prefix')
