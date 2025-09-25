// realtime_notifications.js
// Actualiza el contador de notificaciones en tiempo real sin exponer datos del usuario
(function () {
  'use strict';

  const { throttle } = window.SecurityUtils || {};

  function ensureBadge() {
    let el = document.getElementById('notifCount');
    if (!el) {
      const btn = document.getElementById('notifBtn');
      if (!btn) return null;
      el = document.createElement('span');
      el.id = 'notifCount';
      el.className = 'absolute -top-1 -right-1 min-w-[1.2em] px-1 h-5 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center';
      el.textContent = '0';
      btn.appendChild(el);
    }
    return el;
  }

  const _throttle = throttle || ((fn, wait) => { let last=0, t=null; return (...a)=>{ const n=Date.now(); if(n-last>=wait){ last=n; fn.apply(null,a);} else if(!t){ t=setTimeout(()=>{ last=Date.now(); t=null; fn.apply(null,a); }, wait-(n-last)); } }; });

  function setBadgeValue(n) {
    const badge = ensureBadge();
    if (!badge) return;
    const val = Number.isFinite(n) && n > 0 ? n : 0;
    badge.textContent = String(val);
    if (val > 0) badge.classList.remove('hidden');
    else badge.classList.add('hidden');
  }

  function init() {
    // Si no hay botón, asumimos que no está logueado o no hay UI de notificaciones
    if (!document.getElementById('notifBtn')) return;

    // SSE para actualizar el contador
    if ('EventSource' in window) {
      try {
        const es = new EventSource('/notificaciones/count/stream/');
        es.addEventListener('count', (evt) => {
          try {
            const payload = JSON.parse(evt.data || '{}');
            setBadgeValue(parseInt(payload.unread));
          } catch (_) {}
        });
        es.addEventListener('error', () => { /* el navegador reintenta automáticamente */ });
        window.addEventListener('beforeunload', () => { try { es.close(); } catch(_){} });
        document.addEventListener('visibilitychange', () => { if (document.hidden) { try { es.close(); } catch(_){} } });
      } catch (_) {}
    }

    // Fallback a polling periódico
    try {
      const POLL_MS = 15000;
      const poll = () => {
        fetch('/notificaciones/count/', { credentials: 'same-origin' })
          .then(r => r.ok ? r.json() : { unread: 0 })
          .then(({ unread }) => setBadgeValue(parseInt(unread)))
          .catch(() => {});
      };
      poll();
      const id = setInterval(poll, POLL_MS);
      window.addEventListener('beforeunload', () => clearInterval(id));
      document.addEventListener('visibilitychange', () => { if (document.hidden) clearInterval(id); });
    } catch (_) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
