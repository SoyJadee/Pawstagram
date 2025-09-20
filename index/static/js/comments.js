// comments.js
// Envía comentarios por AJAX y actualiza la lista sin recargar la página

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.comment-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const postId = form.querySelector('input[name="comment_post_id"]').value;
      const contentInput = form.querySelector('input[name="comment_content"]');
      const content = contentInput.value.trim();
      if (!content) return;
      const csrf = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
      // Buscar el .comments-box más cercano hacia arriba
      let commentsBox = null;
      let parent = form.parentElement;
      while (parent && !commentsBox) {
        commentsBox = parent.querySelector('.comments-box');
        parent = parent.parentElement;
      }
      if (!commentsBox) {
        // Si no se encuentra, buscar en todo el documento el más cercano por el postId
        commentsBox = document.querySelector('.comments-box');
      }
      fetch('', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `comment_post_id=${encodeURIComponent(postId)}&comment_content=${encodeURIComponent(content)}`
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          // Agrega el nuevo comentario abajo, crea .comments-box si no existe
          let box = commentsBox;
          if (!box) {
            box = document.createElement('div');
            box.className = 'mb-4 comments-box';
            form.parentNode.insertBefore(box, form);
          }
          const p = document.createElement('p');
          p.className = 'text-sm text-gray-800 mb-1';
          p.innerHTML = `<span class=\"font-semibold text-gray-900\">${data.username}</span> ${data.content}`;
          box.appendChild(p);
          contentInput.value = '';
          showToast('Comentario publicado');
        } else {
          showToast('Error al publicar');
        }
      });
    });
  });
});
