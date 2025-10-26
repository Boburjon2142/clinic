from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('new/', views.doctor_create, name='create'),
    path('<int:pk>/edit/', views.doctor_update, name='edit'),
    path('<int:pk>/delete/', views.doctor_delete, name='delete'),
    path('<int:pk>/appointments/', views.doctor_appointments, name='appointments'),
    path('my/appointments/', views.my_doctor_appointments, name='my_appointments'),
    path('<int:pk>/reset_counter/', views.doctor_reset_counter, name='reset_counter'),
]
