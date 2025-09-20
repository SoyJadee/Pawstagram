// realtime_notifications_panel.js
// Este script actualiza el panel de notificaciones en tiempo real
// Debe llamarse DESPUÉS de que el DOM y Supabase estén listos
(function(){
  const SUPABASE_URL = 'https://arujlmplptyoyppahyhj.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFydWpsbXBscHR5b3lwcGFoeWhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjYwMTIsImV4cCI6MjA3MzcwMjAxMn0.H6YgCIeRpYPWgeP40ag-j53Yl34QAm-xaSUQa1dHqX0';
  console.log('window.USER_ID:', window.USER_ID, typeof window.USER_ID);
  var userId = window.USER_ID ? parseInt(window.USER_ID) : null;
  console.log('Suscribiendo a realtime para user:', userId);

  const notifListContainer = document.getElementById('notifListContainer');

  // Solo agrega notificaciones realtime si el panel está abierto
  if (userId && notifListContainer) {
    const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    supabase
      .channel('public:index_notifications')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'index_notifications', filter: `user_id=eq.${userId}` },
        payload => {
          const notifSidenav = document.getElementById('notifSidenav');
          if (notifSidenav && !notifSidenav.classList.contains('translate-x-full')) {
            const n = payload.new;
            let icon = '<i class="fas fa-bell text-mint"></i>';
            let title = 'Notificación';
            let message = n.message || '';
            if (n.type === 'like') {
              icon = '<i class="fas fa-heart text-rose-500"></i>';
              title = '¡A tu post le dieron like!';
            } else if (n.type === 'comment') {
              icon = '<i class="fas fa-comment text-blue-500"></i>';
              title = '¡Nuevo comentario en tu post!';
            }
            // Formato igual al template: título, mensaje, tiempo
            const notifDiv = document.createElement('div');
            notifDiv.className = 'flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition bg-blue-50';
            notifDiv.innerHTML = `
              <div class="bg-mint/10 rounded-full p-2">${icon}</div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">${title}</p>
                <div class="text-sm text-gray-800">${message}</div>
                <div class="text-xs text-gray-400 mt-1">ahora</div>
              </div>
            `;
            notifListContainer.prepend(notifDiv);
            notifListContainer.scrollTop = 0;
            // Elimina el mensaje vacío si existe
            const emptyMsg = notifListContainer.querySelector('.text-center.text-xs.text-gray-400');
            if (emptyMsg) emptyMsg.remove();
          }
        }
      )
      .subscribe();
  }
})();
