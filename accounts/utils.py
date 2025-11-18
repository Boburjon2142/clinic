from functools import wraps
from django.db.models import Q


def role_required(allowed_roles):
    expanded_roles = set(allowed_roles)
    if 'creator' in expanded_roles:
        expanded_roles.add('admin')

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if request.user.role in expanded_roles or request.user.is_superuser:
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


def get_admin_scope_user_ids(user):
    """Return list of user IDs (self + invited users) visible to a full admin."""
    try:
        from .models import Roles, User
    except Exception:
        return None
    if not getattr(user, 'is_authenticated', False) or getattr(user, 'role', None) != Roles.ADMIN:
        return None
    cached = getattr(user, '_admin_scope_ids', None)
    if cached is not None:
        return cached
    qs = User.objects.filter(Q(pk=user.pk) | Q(created_by=user))
    ids = list(qs.values_list('pk', flat=True))
    if user.pk and user.pk not in ids:
        ids.append(user.pk)
    user._admin_scope_ids = ids
    return ids


def limit_queryset_for_admin(queryset, user, field_name='created_by'):
    """Limit queryset to records created by admin or their invited users."""
    ids = get_admin_scope_user_ids(user)
    if not ids or not field_name:
        return queryset
    return queryset.filter(**{f"{field_name}__in": ids})
