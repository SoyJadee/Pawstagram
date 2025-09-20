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
      // Buscar el .instagram-card más cercano y su .comments-box
      let postCard = form;
      while (postCard && !postCard.classList.contains('instagram-card')) {
        postCard = postCard.parentElement;
      }
      let commentsBox = null;
      if (postCard) {
        commentsBox = postCard.querySelector('.comments-box');
      }
      // Si no existe, crearla justo antes del form
      if (!commentsBox) {
        commentsBox = document.createElement('div');
        commentsBox.className = 'mb-4 comments-box';
        form.parentNode.insertBefore(commentsBox, form);
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
          // Actualizar contador de comentarios
          // Buscar el botón de comentarios dentro del mismo post
          let postCard = form;
          while (postCard && !postCard.classList.contains('instagram-card')) {
            postCard = postCard.parentElement;
          }
          if (postCard) {
            const commentBtn = postCard.querySelector('.fa-comment')?.parentElement;
            if (commentBtn) {
              const countSpan = commentBtn.querySelector('span');
              if (countSpan) {
                let count = parseInt(countSpan.textContent) || 0;
                countSpan.textContent = (count + 1);
              }
            }
          }
          showToast('Comentario publicado');
        } else {
          showToast('Error al publicar');
        }
      });
    });
  });
});
