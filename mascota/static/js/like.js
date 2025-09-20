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
        }
      });
    });
  });
});
