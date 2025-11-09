// Remove the "Rejim" toggle and ensure default avatar appears
(function () {
  function removeRejimButtons() {
    const candidates = Array.from(
      document.querySelectorAll('button, a, .btn, [role="button"], .toggle, .switch, li, span, div')
    );
    const isRejim = (el) => /\bRejim\b/i.test((el.textContent || '').trim());
    candidates.forEach((el) => {
      if (isRejim(el)) {
        // remove the clickable parent if text is wrapped
        const clickable = el.closest('button, a, .btn, [role="button"]') || el;
        try { clickable.remove(); } catch (e) {}
      }
    });
  }

  function ensureDefaultAvatar() {
    const fallback = '/static/img/default-avatar.svg';
    const looksLikeAvatar = (img) => {
      const alt = (img.getAttribute('alt') || '').toLowerCase();
      const cls = (img.getAttribute('class') || '').toLowerCase();
      return /profil|avatar|user|account/.test(alt + ' ' + cls);
    };

    document.querySelectorAll('img').forEach((img) => {
      const setFallback = () => { if (img.src !== fallback) img.src = fallback; };
      img.addEventListener('error', setFallback, { once: true });
      if (!img.complete) return; // wait for load/error
      if ((img.naturalWidth === 0 || img.naturalHeight === 0) || !img.src) {
        setFallback();
      } else if (looksLikeAvatar(img) && /(data:|blob:)/.test(img.src) === false && /\.(png|jpe?g|gif|svg)$/i.test(img.src) === false) {
        // If it doesn't look like a valid image url and is avatar-like, fallback
        setFallback();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      removeRejimButtons();
      ensureDefaultAvatar();
    });
  } else {
    removeRejimButtons();
    ensureDefaultAvatar();
  }
})();

