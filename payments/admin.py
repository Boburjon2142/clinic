from django.contrib import admin
from .models import Payment, ExpenseRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "amount", "method", "cashier", "created_at")
    list_filter = ("method", "created_at")
    search_fields = ("receipt_no", "appointment__patient__full_name", "appointment__doctor__full_name")


@admin.register(ExpenseRequest)
class ExpenseRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "requested_by", "amount", "status")
    list_filter = ("status", "created_at")
    search_fields = ("requested_by__username", "comment")

