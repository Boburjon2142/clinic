import string


def next_code_prefix(used_prefixes=None):
    """Return a new, unused code prefix for Doctor.code_prefix.

    Prefers single letters A–Z, then falls back to letter+digit (A2, B2, ...).
    """
    if used_prefixes is None:
        try:
            from .models import Doctor
            used_prefixes = set(Doctor.objects.values_list('code_prefix', flat=True))
        except Exception:
            used_prefixes = set()
    else:
        used_prefixes = set(used_prefixes)

    for ch in string.ascii_uppercase:
        if ch not in used_prefixes:
            return ch

    n = 2
    while True:
        for ch in string.ascii_uppercase:
            cand = f"{ch}{n}"
            if cand not in used_prefixes:
                return cand
        n += 1

