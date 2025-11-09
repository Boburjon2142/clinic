from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('new/<int:appointment_id>/', views.payment_create, name='create'),
    path('receipt/<int:payment_id>/', views.receipt_pdf, name='receipt'),
    # Expenses
    path('expenses/', views.expenses_request, name='expenses_request'),
    path('expenses/review/', views.expenses_review, name='expenses_review'),
]
