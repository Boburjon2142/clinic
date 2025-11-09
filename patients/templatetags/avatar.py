from django import template
from django.templatetags.static import static


register = template.Library()


@register.filter(name="avatar_url")
def avatar_url(user):
    """Return user's avatar URL or a default static icon.

    Usage in templates:
        {% load static avatar %}
        <img src="{{ request.user|avatar_url }}" alt="Profil" />
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return static("img/default-avatar.svg")

    # Try common attribute paths safely
    for path in (
        "profile.image.url",
        "image.url",
        "avatar.url",
    ):
        try:
            obj = user
            for part in path.split("."):
                obj = getattr(obj, part)
            if obj:
                return obj
        except Exception:
            pass

    return static("img/default-avatar.svg")

