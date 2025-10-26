from datetime import timedelta
from django.utils import timezone


class CleanupOldAppointmentsMiddleware:
    """
    Deletes appointments older than 30 days once per day on first request.
    Lightweight approach that avoids external schedulers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            from dashboard.models import Setting
            from appointments.models import Appointment
            today = timezone.localdate()
            setting, _ = Setting.objects.get_or_create(pk=1)
            if setting.last_cleanup != today:
                cutoff = timezone.now() - timedelta(days=30)
                Appointment.objects.filter(created_at__lt=cutoff).delete()
                setting.last_cleanup = today
                setting.save(update_fields=["last_cleanup"])
        except Exception:
            # Silently continue; never block the request path due to cleanup
            pass

        response = self.get_response(request)
        return response

