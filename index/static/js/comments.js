// comments.js
// Envía comentarios por AJAX y actualiza la lista de forma segura

document.addEventListener('DOMContentLoaded', function () {
  const { getCSRF, sanitizeId, sanitizeText } = window.SecurityUtils || {};
  const suspicious = (txt) => /(--|;|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)/i.test(txt);

  const inflight = new Map(); // form -> AbortController

  document.querySelectorAll('.comment-form').forEach(function(form) {
    let lastSubmit = 0;
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      const now = Date.now();
      if (now - lastSubmit < 600) return; // throttle 600ms
      lastSubmit = now;

      const postIdRaw = form.querySelector('input[name="comment_post_id"]')?.value;
      const postId = sanitizeId(postIdRaw);
      const contentInput = form.querySelector('input[name="comment_content"]');
      const content = sanitizeText(contentInput?.value || '');

      if (!postId || !content) return;
      if (content.length < 2 || content.length > 300) return; // límites del backend
      if (suspicious(content)) { showToast && showToast('Contenido no permitido'); return; }

  const csrf = getCSRF ? getCSRF(form) : (form.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '');
      if (!csrf) return;

      // Encontrar contenedor del post y caja de comentarios
      let postCard = form;
      while (postCard && !postCard.classList.contains('instagram-card')) {
        postCard = postCard.parentElement;
      }
      let commentsBox = postCard ? postCard.querySelector('.comments-box') : null;
      if (!commentsBox) {
        commentsBox = document.createElement('div');
        commentsBox.className = 'mb-4 comments-box';
        form.parentNode.insertBefore(commentsBox, form);
      }

      // Cancelar request anterior de este form si existe
      try {
        const prev = inflight.get(form);
        if (prev) { prev.abort(); inflight.delete(form); }
      } catch { /* noop */ }

      const controller = new AbortController();
      inflight.set(form, controller);

      fetch('', {
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
        body: `comment_post_id=${encodeURIComponent(postId)}&comment_content=${encodeURIComponent(content)}`,
        signal: controller.signal
      })
      .then(async (r) => {
        if (!r.ok) throw new Error('bad_status');
        const data = await r.json().catch(() => ({}));
        if (data && data.success) {
          // Crear nodo seguro sin innerHTML para evitar XSS
          const p = document.createElement('p');
          p.className = 'text-sm text-gray-800 mb-1';
          const strong = document.createElement('span');
          strong.className = 'font-semibold text-gray-900';
          strong.textContent = String(data.username || '').slice(0, 50);
          const sep = document.createTextNode(' ');
          const text = document.createTextNode(String(data.content || '').slice(0, 400));
          p.appendChild(strong);
          p.appendChild(sep);
          p.appendChild(text);
          commentsBox.appendChild(p);
          if (contentInput) contentInput.value = '';

          // Actualizar contador de comentarios del post de forma segura
          if (postCard) {
            const commentBtn = postCard.querySelector('.fa-comment')?.parentElement;
            const countSpan = commentBtn ? commentBtn.querySelector('span') : null;
            if (countSpan) {
              const m = String(countSpan.textContent || '').match(/\d+/);
              const count = m ? parseInt(m[0], 10) : 0;
              countSpan.textContent = String((Number.isFinite(count) ? count : 0) + 1);
            }
          }
          if (typeof showToast === 'function') showToast('Comentario publicado');
        } else {
          if (typeof showToast === 'function') showToast('Error al publicar');
        }
      })
      .catch(() => {
        if (typeof showToast === 'function') showToast('Error de red');
      })
      .finally(() => {
        const ctrl = inflight.get(form);
        if (ctrl === controller) inflight.delete(form);
      });
    });
  });
});
