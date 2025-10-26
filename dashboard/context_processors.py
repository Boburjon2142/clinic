def clinic_settings(request):
    try:
        from .models import Setting
        return {'setting': Setting.objects.first()}
    except Exception:
        return {'setting': None}

