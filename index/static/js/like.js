// like.js
// Envía el like por AJAX y actualiza el contador sin recargar la página

document.addEventListener('DOMContentLoaded', function () {
  // Utilidades compartidas
  const { getCSRF, sanitizeId, parseIntFromText } = window.SecurityUtils || {};
  const _getCSRF = () => (getCSRF ? getCSRF(document) : (document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || ''));

  // Mapa para abortar peticiones duplicadas por post
  const inflight = new Map(); // postId -> AbortController

  document.querySelectorAll('.instagram-card').forEach(function(card) {
    const likeBtn = card.querySelector('.like-btn');
    const likeCount = card.querySelector('.like-count');
    if (!likeBtn || !likeCount) return;

    // Throttle simple por botón
    let lastClick = 0;

    likeBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const now = Date.now();
      if (now - lastClick < 350) return; // throttle 350ms
      lastClick = now;

      if (likeBtn.classList.contains('disabled')) return;
      const rawId = card.querySelector('input[name="comment_post_id"]')?.value || card.dataset.postId;
      const postId = sanitizeId(rawId);
      if (!postId) return;
      if (navigator.onLine === false) return;

      // Abortar petición previa para este post si sigue en curso
      try {
        const prev = inflight.get(postId);
        if (prev) { prev.abort(); inflight.delete(postId); }
      } catch { /* noop */ }

      const csrf = _getCSRF();
      if (!csrf) {
        // Sin CSRF no enviamos nada
        return;
      }

      // --- Optimistic UI ---
      const wasLiked = likeBtn.classList.contains('text-red-500');
      const currentLikes = parseIntFromText ? parseIntFromText(likeCount.textContent) : (parseInt((likeCount.textContent||'').replace(/\D+/g,'')||'0',10)||0);

      if (!wasLiked) {
        likeBtn.classList.add('like-pop');
        setTimeout(() => likeBtn.classList.remove('like-pop'), 180);
      }

      const setLikes = (n) => {
        const safe = Number.isFinite(n) && n >= 0 ? n : currentLikes;
        likeCount.textContent = safe + ' Me gusta';
      };

      if (wasLiked) {
        likeBtn.classList.remove('text-red-500');
        likeBtn.classList.add('text-gray-500');
        setLikes(currentLikes - 1);
      } else {
        likeBtn.classList.add('text-red-500');
        likeBtn.classList.remove('text-gray-500');
        setLikes(currentLikes + 1);
      }

      likeBtn.classList.add('disabled');

      const controller = new AbortController();
      inflight.set(postId, controller);

      fetch('/like/', {
        method: 'POST',
        credentials: 'same-origin',
        redirect: 'error',
        referrerPolicy: 'same-origin',
        headers: {
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        body: `post_id=${encodeURIComponent(postId)}`,
        signal: controller.signal
      })
      .then(async (r) => {
        // 200 esperado; si no, revertir
        if (!r.ok) throw new Error('bad_status');
        // Forzar JSON seguro y limitar campos
        const data = await r.json().catch(() => ({}));
        if (data && data.success) {
          const likes = Number.isFinite(+data.likes) ? +data.likes : currentLikes;
          setLikes(likes);
          likeBtn.classList.toggle('text-red-500', !!data.liked);
          likeBtn.classList.toggle('text-gray-500', !data.liked);
        } else {
          // casos como not_authenticated, etc.
          if (data && data.error === 'not_authenticated') {
            // opcional: redirigir a login
            // window.location.href = '/login/';
          }
          // revertir estado optimista
          if (wasLiked) {
            likeBtn.classList.add('text-red-500');
            likeBtn.classList.remove('text-gray-500');
            setLikes(currentLikes);
          } else {
            likeBtn.classList.remove('text-red-500');
            likeBtn.classList.add('text-gray-500');
            setLikes(currentLikes);
          }
        }
      })
      .catch(() => {
        // Revertir en error/red abort
        if (wasLiked) {
          likeBtn.classList.add('text-red-500');
          likeBtn.classList.remove('text-gray-500');
          setLikes(currentLikes);
        } else {
          likeBtn.classList.remove('text-red-500');
          likeBtn.classList.add('text-gray-500');
          setLikes(currentLikes);
        }
      })
      .finally(() => {
        likeBtn.classList.remove('disabled');
        // liberar controlador inflight si es el vigente
        const ctrl = inflight.get(postId);
        if (ctrl === controller) inflight.delete(postId);
      });
    });
  });
});
