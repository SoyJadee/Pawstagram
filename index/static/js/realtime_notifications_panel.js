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
    // Likes y comentarios (index_notifications)
    supabase
      .channel('public:index_notifications')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'index_notifications', filter: `user_id=eq.${userId}` },
        payload => {
          const notifSidenav = document.getElementById('notifSidenav');
          if (notifSidenav && !notifSidenav.classList.contains('translate-x-full')) {
            if (typeof window.reloadAllNotifications === 'function') {
              window.reloadAllNotifications();
            }
          }
        }
      )
      .subscribe();
    // Adopciones (adopcion_adoption)
    supabase
      .channel('public:adopcion_adoption')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'adopcion_adoption' },
        payload => {
          const notifSidenav = document.getElementById('notifSidenav');
          if (notifSidenav && !notifSidenav.classList.contains('translate-x-full')) {
            if (typeof window.reloadAllNotifications === 'function') {
              window.reloadAllNotifications();
            }
          }
        }
      )
      .subscribe();
  }
})();
