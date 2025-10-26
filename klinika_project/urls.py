from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from dashboard.views import home


urlpatterns = [
    # Custom admin-area pages must come BEFORE Django admin include,
    # otherwise they get swallowed by admin's catch-all.
    path('admin/dashboard/', include('dashboard.urls')),
    path('admin/doctors/', include('doctors.urls')),
    path('admin/complaints/', include('appointments.complaint_urls')),

    # Public app routes
    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('payments/', include('payments.urls')),
    # Patients section kept, but hidden from navbar; can be removed if not needed
    path('patients/', include('patients.urls')),

    # Public alias for doctor appointments list (redirect to admin prefix)
    path('doctors/<int:pk>/appointments/',
         RedirectView.as_view(pattern_name='doctors:appointments', permanent=False)),

    # Django admin
    path('admin/', admin.site.urls),

    # Home page
    path('', home, name='home'),
]

# Admin branding in Uzbek
admin.site.site_header = "Klinika administratsiyasi"
admin.site.site_title = "Klinika admin"
admin.site.index_title = "Boshqaruv paneli"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
