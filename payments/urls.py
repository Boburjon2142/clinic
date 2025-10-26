from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('new/<int:appointment_id>/', views.payment_create, name='create'),
    path('receipt/<int:payment_id>/', views.receipt_pdf, name='receipt_pdf'),
]

