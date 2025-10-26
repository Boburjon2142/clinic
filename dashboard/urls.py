from django.urls import path
from .views import admin_dashboard, stats_view, settings_view, users_manage, make_admin, make_admin1, make_admin2, make_admin3, remove_admin, toggle_active, reset_doc_counter, user_add, clear_patients

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('stats/', stats_view, name='stats'),
    path('settings/', settings_view, name='settings'),
    path('settings/clear-patients/', clear_patients, name='clear_patients'),
    path('users/add/', user_add, name='user_add'),
    path('users/', users_manage, name='users_manage'),
    path('users/<int:pk>/make_admin/', make_admin, name='make_admin'),
    path('users/<int:pk>/make_admin1/', make_admin1, name='make_admin1'),
    path('users/<int:pk>/make_admin2/', make_admin2, name='make_admin2'),
    path('users/<int:pk>/make_admin3/', make_admin3, name='make_admin3'),
    path('users/<int:pk>/remove_admin/', remove_admin, name='remove_admin'),
    path('users/<int:pk>/toggle_active/', toggle_active, name='toggle_active'),
    path('settings/reset-doc-counter/', reset_doc_counter, name='reset_doc_counter'),
]
