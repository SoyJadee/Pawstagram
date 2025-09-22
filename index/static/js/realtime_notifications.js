// realtime_notifications.js
// Este script actualiza el contador de notificaciones en tiempo real
(function(){
  const SUPABASE_URL = 'https://arujlmplptyoyppahyhj.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFydWpsbXBscHR5b3lwcGFoeWhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjYwMTIsImV4cCI6MjA3MzcwMjAxMn0.H6YgCIeRpYPWgeP40ag-j53Yl34QAm-xaSUQa1dHqX0';
  var userId = window.USER_ID ? parseInt(window.USER_ID) : null;
  if (SUPABASE_URL !== 'https://<TU-PROYECTO>.supabase.co') {
    const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    // Likes y comentarios solo si hay userId
    if (userId) {
      supabase
        .channel('public:index_notifications')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'index_notifications', filter: `user_id=eq.${userId}` },
          payload => {
            let notifCount = document.getElementById('notifCount');
            if (notifCount) {
              let current = parseInt(notifCount.textContent);
              if (isNaN(current) || notifCount.classList.contains('hidden')) {
                notifCount.textContent = '1';
                notifCount.classList.remove('hidden');
              } else {
                notifCount.textContent = (current + 1).toString();
              }
            } else {
              const notifBtn = document.getElementById('notifBtn');
              if (notifBtn) {
                notifCount = document.createElement('span');
                notifCount.id = 'notifCount';
                notifCount.className = 'absolute -top-1 -right-1 min-w-[1.2em] px-1 h-5 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center';
                notifCount.textContent = '1';
                notifBtn.appendChild(notifCount);
              }
            }
          }
        )
        .subscribe();
    }
    // Adopciones SOLO si hay mascotas
    const myPetIds = window.MY_PET_IDS || [];
    if (myPetIds.length > 0) {
      console.log('[Realtime] Suscribiendo a adopciones para mascotas:', myPetIds);
      supabase
        .channel('public:adopcion_adoption')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'adopcion_adoption' },
          payload => {
            const petId = payload.new.pet_id;
            console.log('[Realtime] Nueva adopción recibida. payload:', payload);
            console.log('[Realtime] pet_id:', petId, '| Mis mascotas:', myPetIds, '| Tipos:', typeof petId, myPetIds.map(x => typeof x));
            if (!myPetIds.map(String).includes(String(petId))) {
              console.log('[Realtime] Adopción ignorada, no es de mis mascotas.');
              return;
            }
            console.log('[Realtime] ¡Adopción contada!');
            let notifCount = document.getElementById('notifCount');
            if (notifCount) {
              let current = parseInt(notifCount.textContent);
              if (isNaN(current) || notifCount.classList.contains('hidden')) {
                notifCount.textContent = '1';
                notifCount.classList.remove('hidden');
              } else {
                notifCount.textContent = (current + 1).toString();
              }
            } else {
              const notifBtn = document.getElementById('notifBtn');
              if (notifBtn) {
                notifCount = document.createElement('span');
                notifCount.id = 'notifCount';
                notifCount.className = 'absolute -top-1 -right-1 min-w-[1.2em] px-1 h-5 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center';
                notifCount.textContent = '1';
                notifBtn.appendChild(notifCount);
              }
            }
          }
        )
        .subscribe();
    }
  }
})();
