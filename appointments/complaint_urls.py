from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='list'),
    path('new/', views.complaint_create, name='create'),
    path('<int:pk>/edit/', views.complaint_update, name='edit'),
    path('<int:pk>/delete/', views.complaint_delete, name='delete'),
]

