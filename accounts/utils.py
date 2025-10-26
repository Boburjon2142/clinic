from functools import wraps


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            # If user is authenticated but not allowed:
            # log them out and redirect to login page instead of 403
            try:
                from django.contrib.auth import logout
                from django.conf import settings
                from django.shortcuts import redirect
                logout(request)
                return redirect(getattr(settings, 'LOGIN_URL', '/accounts/login/'))
            except Exception:
                from django.shortcuts import redirect
                return redirect('/accounts/login/')
        return _wrapped
    return decorator
