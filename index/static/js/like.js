// like.js
// Envía el like por AJAX y actualiza el contador sin recargar la página

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.instagram-card').forEach(function(card) {
    const likeBtn = card.querySelector('.like-btn');
    const likeCount = card.querySelector('.like-count');
    if (!likeBtn || !likeCount) return;
    likeBtn.addEventListener('click', function(e) {
      e.preventDefault();
      if (likeBtn.classList.contains('disabled')) return;
      const postId = card.querySelector('input[name="comment_post_id"]')?.value || card.dataset.postId;
      if (!postId) return;
      const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
      // --- Optimistic UI ---
      const wasLiked = likeBtn.classList.contains('text-red-500');
      let currentLikes = parseInt(likeCount.textContent) || 0;
      // Animación pop rápida al dar like
      if (!wasLiked) {
        likeBtn.classList.add('like-pop');
        setTimeout(() => likeBtn.classList.remove('like-pop'), 180); // duración igual al CSS
      }
      // Cambia visualmente al instante
      if (wasLiked) {
        likeBtn.classList.remove('text-red-500');
        likeBtn.classList.add('text-gray-500');
        likeCount.textContent = (currentLikes - 1) + ' Me gusta';
      } else {
        likeBtn.classList.add('text-red-500');
        likeBtn.classList.remove('text-gray-500');
        likeCount.textContent = (currentLikes + 1) + ' Me gusta';
      }
      likeBtn.classList.add('disabled');
      fetch('/like/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `post_id=${encodeURIComponent(postId)}`
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          likeCount.textContent = data.likes + ' Me gusta';
          likeBtn.classList.toggle('text-red-500', data.liked);
          likeBtn.classList.toggle('text-gray-500', !data.liked);
        } else {
          if (wasLiked) {
            likeBtn.classList.add('text-red-500');
            likeBtn.classList.remove('text-gray-500');
            likeCount.textContent = (currentLikes) + ' Me gusta';
          } else {
            likeBtn.classList.remove('text-red-500');
            likeBtn.classList.add('text-gray-500');
            likeCount.textContent = (currentLikes) + ' Me gusta';
          }
        }
      })
      .catch(() => {
        if (wasLiked) {
          likeBtn.classList.add('text-red-500');
          likeBtn.classList.remove('text-gray-500');
          likeCount.textContent = (currentLikes) + ' Me gusta';
        } else {
          likeBtn.classList.remove('text-red-500');
          likeBtn.classList.add('text-gray-500');
          likeCount.textContent = (currentLikes) + ' Me gusta';
        }
      })
      .finally(() => {
        likeBtn.classList.remove('disabled');
      });
    });
  });
});
