// realtime_notifications_panel.js
// Este script actualiza el panel de notificaciones en tiempo real
(function () {
  'use strict';

  const { throttle } = window.SecurityUtils || {};

  const notifListContainer = document.getElementById('notifListContainer');
  if (!notifListContainer) return;

  // Throttle para evitar muchas recargas consecutivas
  const _throttle = throttle || ((fn, wait) => { let last=0, t=null; return (...a)=>{ const n=Date.now(); if(n-last>=wait){last=n; fn.apply(null,a);} else if(!t){ t=setTimeout(()=>{ last=Date.now(); t=null; fn.apply(null,a); }, wait-(n-last)); } }; });

  const safeReload = _throttle(() => {
    try {
      if (typeof window.reloadAllNotifications === 'function') {
        window.reloadAllNotifications();
      }
    } catch (e) {
    }
  }, 1500);

  const onPayload = () => {
    const notifSidenav = document.getElementById('notifSidenav');
    if (notifSidenav && !notifSidenav.classList.contains('translate-x-full')) {
      safeReload();
    }
  };

  // Usamos SSE; no dependemos de ningún dato global del usuario
  if ('EventSource' in window) {
    try {
      const es = new EventSource('/notificaciones/stream/');
      es.addEventListener('update', () => onPayload());
      es.addEventListener('error', () => {});
      // limpiar SSE en unload
      window.addEventListener('beforeunload', () => es.close());
      document.addEventListener('visibilitychange', () => { if (document.hidden) es.close(); });
    } catch (e) {
    }
  }
})();
