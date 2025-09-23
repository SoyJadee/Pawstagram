// realtime_notifications_panel.js
// Este script actualiza el panel de notificaciones en tiempo real
// Debe llamarse DESPUÉS de que el DOM y Supabase estén listos
(function () {
  'use strict';

  const SUPABASE_URL = String(window.SUPABASE_URL || '');
  const SUPABASE_KEY = String(window.SUPABASE_KEY || '');
  const { sanitizeId, throttle } = window.SecurityUtils || {};
  const rawUserId = window.USER_ID;
  const _userId = sanitizeId ? sanitizeId(rawUserId) : (String(rawUserId||'').match(/^\d+$/) ? String(rawUserId) : null);
  const userId = _userId ? parseInt(_userId, 10) : null;

  // Sanitiza userId para evitar interpolaciones inesperadas en el filtro
  const validUser = !!(userId && /^\d+$/.test(String(userId)));
  if (!validUser) return;

  const notifListContainer = document.getElementById('notifListContainer');
  if (!notifListContainer) return;

  if (!window.supabase || !window.supabase.createClient) return;
  const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

  // Throttle para evitar muchas recargas consecutivas
  const _throttle = throttle || ((fn, wait) => { let last=0, t=null; return (...a)=>{ const n=Date.now(); if(n-last>=wait){last=n; fn.apply(null,a);} else if(!t){ t=setTimeout(()=>{ last=Date.now(); t=null; fn.apply(null,a); }, wait-(n-last)); } }; });

  const safeReload = _throttle(() => {
    try {
      if (typeof window.reloadAllNotifications === 'function') {
        window.reloadAllNotifications();
      }
    } catch (e) {
      console.error('Error recargando notificaciones:', e);
    }
  }, 1500);

  const onPayload = () => {
    const notifSidenav = document.getElementById('notifSidenav');
    if (notifSidenav && !notifSidenav.classList.contains('translate-x-full')) {
      safeReload();
    }
  };

  const channels = [];

  // Si hay Supabase y credenciales, usar Realtime; si no, usar SSE como fallback
  const canUseSupabase = !!(SUPABASE_URL && SUPABASE_KEY && window.supabase && window.supabase.createClient);
  if (canUseSupabase) {
    try {
      const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
      // Likes y comentarios (solo del usuario actual)
      const ch1 = supabase
        .channel('public:index_notifications')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'index_notifications', filter: `user_id=eq.${userId}` },
          onPayload
        )
        .subscribe((status) => {
          if (status !== 'SUBSCRIBED') console.warn('Canal index_notifications estado:', status);
        });
      channels.push(ch1);

      // Adopciones (ajusta el filtro a tu esquema real)
      const ch2 = supabase
        .channel('public:adopcion_adoption')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'adopcion_adoption' },
          onPayload
        )
        .subscribe((status) => {
          if (status !== 'SUBSCRIBED') console.warn('Canal adopcion_adoption estado:', status);
        });
      channels.push(ch2);
    } catch (e) {
      console.error('Error creando canales Realtime:', e);
    }
  } else if ('EventSource' in window) {
    try {
      const es = new EventSource('/notificaciones/stream/');
      es.addEventListener('update', () => onPayload());
      es.addEventListener('error', (e) => {
        console.warn('SSE error:', e);
      });
      // limpiar SSE en unload
      window.addEventListener('beforeunload', () => es.close());
      document.addEventListener('visibilitychange', () => { if (document.hidden) es.close(); });
    } catch (e) {
      console.warn('No se pudo iniciar SSE fallback:', e);
    }
  }

  const cleanup = () => {
    try {
      channels.forEach((ch) => supabase.removeChannel(ch));
    } catch (e) {
      console.warn('Error limpiando canales:', e);
    }
  };

  window.addEventListener('beforeunload', cleanup);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cleanup();
  });
})();
