// realtime_all_notifications.js
// Recarga la lista unificada de notificaciones (likes, comentarios, adopciones) en tiempo real
(function(){
  const ALL_NOTIF_URL = '/notificaciones/all/fragment/';
  document.addEventListener('DOMContentLoaded', function () {
    const unifiedNotifList = document.getElementById('unifiedNotifList');
    if (!unifiedNotifList) return;
    function reloadAllNotifications() {
      fetch(ALL_NOTIF_URL)
        .then(resp => resp.json())
        .then(data => {
          unifiedNotifList.innerHTML = data.html;
        });
    }
    window.reloadAllNotifications = reloadAllNotifications;
    reloadAllNotifications();
  });
})();