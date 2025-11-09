from __future__ import annotations

from django.templatetags.static import static


class UiPatchMiddleware:
    """Inject a small JS to remove the "Rejim" toggle and ensure default avatar.

    This avoids editing templates directly. It appends a script tag before
    </body> for text/html responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.script_tag = (
            f'<script src="{static("js/ui-patches.js")}" defer></script>'
        )

    def __call__(self, request):
        response = self.get_response(request)
        try:
            ctype = response.get("Content-Type", "")
            if response.status_code == 200 and "text/html" in ctype:
                content = response.content.decode(response.charset)
                lower = content.lower()
                insert_at = lower.rfind("</body>")
                if insert_at != -1 and self.script_tag not in content:
                    content = (
                        content[:insert_at] + self.script_tag + content[insert_at:]
                    )
                    response.content = content.encode(response.charset)
        except Exception:
            # Fail-safe: never break the response rendering
            return response
        return response

