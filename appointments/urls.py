from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('new/', views.appointment_create, name='create'),
    path('price_receipt/<int:appointment_id>/', views.appointment_price_receipt, name='price_receipt'),
    path('receipt/<int:appointment_id>/', views.appointment_receipt, name='receipt'),
    path('<int:appointment_id>/set_price/', views.appointment_set_price, name='set_price'),
    path('queue/price/', views.appointments_pending_price, name='queue_price'),
    path('queue/cashier/', views.appointments_for_cashier, name='queue_cashier'),
]
