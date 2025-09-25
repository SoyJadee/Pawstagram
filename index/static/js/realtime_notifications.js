// realtime_notifications.js
// Este script actualiza el contador de notificaciones de forma segura en tiempo real
(function () {
  'use strict';



  const SUPABASE_URL = String(window.SUPABASE_URL || '');
  const SUPABASE_KEY = String(window.SUPABASE_KEY || '');
  const { sanitizeId, throttle } = window.SecurityUtils || {};
  const rawUserId = window.USER_ID;
  const _userId = sanitizeId ? sanitizeId(rawUserId) : (String(rawUserId||'').match(/^\d+$/) ? String(rawUserId) : null);
  const userId = _userId ? parseInt(_userId, 10) : null;

  // Sanitiza userId y entorno
  const validUser = !!(userId && /^\d+$/.test(String(userId)));
  const canUseSupabase = !!(
    SUPABASE_URL && SUPABASE_KEY && window.supabase && window.supabase.createClient
  );

  // Función segura para incrementar el badge
  const ensureBadge = () => {
    let el = document.getElementById('notifCount');
    if (!el) {
      const btn = document.getElementById('notifBtn');
      if (!btn) {
        return null;
      }
      el = document.createElement('span');
      el.id = 'notifCount';
      el.className = 'absolute -top-1 -right-1 min-w-[1.2em] px-1 h-5 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center';
      el.textContent = '0';
      btn.appendChild(el);
    }
    return el;
  };

  const _throttle = throttle || ((fn, wait) => {
    let last = 0, timer = null;
    return (...args) => {
      const now = Date.now();
      const run = () => fn.apply(null, args);
      if (now - last >= wait) { last = now; run(); }
      else if (!timer) { const remaining = wait - (now - last); timer = setTimeout(() => { last = Date.now(); timer = null; run(); }, remaining); }
    };
  });
  const safeIncrement = _throttle((inc = 1) => {
    const badge = ensureBadge();
    if (!badge) return;
    const current = parseInt(badge.textContent);
    const base = Number.isFinite(current) ? current : 0;
    const delta = Math.max(1, parseInt(inc));
    badge.textContent = String(base + delta);
    badge.classList.remove('hidden');
  }, 500);

  // Sanitizar IDs de mascotas desde ventana global
  const myPetIds = (function (arr) {
    if (!Array.isArray(arr)) return [];
    const out = []; const seen = new Set();
    for (let i = 0; i < arr.length && out.length < 50; i++) {
      const id = sanitizeId ? sanitizeId(arr[i]) : (String(arr[i]||'').match(/^\d+$/) ? String(arr[i]) : null);
      if (!id) continue; const n = parseInt(id, 10);
      if (Number.isFinite(n) && n > 0 && !seen.has(n)) { seen.add(n); out.push(n); }
    }
    return out;
  })(window.MY_PET_IDS || []);

  // Realtime con Supabase si es posible
  const channels = [];
  let _pollingId = null;
  let _sseCount = null;
  const startSSECount = () => {
    if (_sseCount || !('EventSource' in window) || !validUser) return;
    try {
      const es = new EventSource('/notificaciones/count/stream/');
      _sseCount = es;
      es.addEventListener('count', (evt) => {
        try {
          const payload = JSON.parse(evt.data || '{}');
          const n = parseInt(payload.unread);
          const badge = ensureBadge();
          if (!badge) return;
          const val = Number.isFinite(n) && n > 0 ? n : 0;
          badge.textContent = String(val);
          if (val > 0) badge.classList.remove('hidden');
          else badge.classList.add('hidden');
        } catch (_) { /* noop */ }
      });
      es.addEventListener('error', () => {
        try { es.close(); } catch(_) {}
        _sseCount = null;
        // como último recurso, polling
        startPolling();
      });
      window.addEventListener('beforeunload', () => { try { es.close(); } catch(_) {} });
      document.addEventListener('visibilitychange', () => { if (document.hidden && _sseCount) { try { _sseCount.close(); } catch(_) {} _sseCount = null; } });
    } catch (_) { /* noop */ }
  };
  const startPolling = () => {
    if (_pollingId) return; // ya iniciado
    try {
      const POLL_MS = 15000;
      const poll = () => {
        fetch('/notificaciones/count/', { credentials: 'same-origin' })
          .then(r => r.ok ? r.json() : { unread: 0 })
          .then(({ unread }) => {
            const n = parseInt(unread);
            const badge = ensureBadge();
            if (!badge) return;
            const val = Number.isFinite(n) && n > 0 ? n : 0;
            badge.textContent = String(val);
            if (val > 0) badge.classList.remove('hidden');
            else badge.classList.add('hidden');
          })
          .catch(() => {});
      };
      poll();
      _pollingId = setInterval(poll, POLL_MS);
      window.addEventListener('beforeunload', () => { if (_pollingId) clearInterval(_pollingId); });
      document.addEventListener('visibilitychange', () => { if (document.hidden && _pollingId) { clearInterval(_pollingId); _pollingId = null; } });
    } catch (_) { /* noop */ }
  };
  if (canUseSupabase) {
    try {
      const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

      if (validUser) {
        const ch1 = supabase
          .channel('public:index_notifications')
          .on(
            'postgres_changes',
            { event: 'INSERT', schema: 'public', table: 'index_notifications', filter: `user_id=eq.${userId}` },
            () => safeIncrement(1)
          )
          .subscribe((status) => {
            if (status === 'CLOSED' || status === 'CHANNEL_ERROR') { startSSECount(); }
          });
        channels.push(ch1);
      }

      if (myPetIds.length > 0) {
        // Intentar filtrar por pet_id usando operador in.
        const inList = myPetIds.join(',');
        const filter = `pet_id=in.(${inList})`;
        const ch2 = supabase
          .channel('public:adopcion_adoption')
          .on(
            'postgres_changes',
            { event: 'INSERT', schema: 'public', table: 'adopcion_adoption', filter },
            (payload) => {
              try {
                const petId = payload && payload.new && payload.new.pet_id;
                if (myPetIds.map(String).includes(String(petId))) {
                  safeIncrement(1);
                }
              } catch (_) { /* noop */ }
            }
          )
          .subscribe((status) => {
            if (status === 'CLOSED' || status === 'CHANNEL_ERROR') { startSSECount(); }
          });
        channels.push(ch2);
      }

      // cleanup
      const cleanup = () => {
        try { channels.forEach((ch) => supabase.removeChannel(ch)); } catch (_) {}
      };
      window.addEventListener('beforeunload', cleanup);
      document.addEventListener('visibilitychange', () => { if (document.hidden) cleanup(); });
    } catch (e) {
      startSSECount();
    }
  } else if ('EventSource' in window && validUser) {
    // SSE de conteo dedicado: actualiza el badge cuando cambie el total
    try {
      const esCount = new EventSource('/notificaciones/count/stream/');
      esCount.addEventListener('count', (evt) => {
        try {
          const payload = JSON.parse(evt.data || '{}');
          const n = parseInt(payload.unread);
          const badge = ensureBadge();
          if (!badge) return;
          const val = Number.isFinite(n) && n > 0 ? n : 0;
          badge.textContent = String(val);
          if (val > 0) badge.classList.remove('hidden');
          else badge.classList.add('hidden');
        } catch (_) { /* noop */ }
      });
      esCount.addEventListener('error', () => { /* el navegador reintenta */ });
      window.addEventListener('beforeunload', () => esCount.close());
      document.addEventListener('visibilitychange', () => { if (document.hidden) esCount.close(); });
    } catch (e) {
    }
    // Fallback final: polling periódico al backend
    try {
      const POLL_MS = 15000; // 15s
      const poll = () => {
        fetch('/notificaciones/count/', { credentials: 'same-origin' })
          .then(r => r.ok ? r.json() : { unread: 0 })
          .then(({ unread }) => {
            const n = parseInt(unread);
            if (Number.isFinite(n) && n > 0) {
              const badge = ensureBadge();
              if (badge) {
                badge.textContent = String(n);
                badge.classList.remove('hidden');
              }
            }
          })
          .catch(() => {});
      };
      // primera corrida y luego intervalo
      poll();
      const id = setInterval(poll, POLL_MS);
      window.addEventListener('beforeunload', () => clearInterval(id));
      document.addEventListener('visibilitychange', () => { if (document.hidden) clearInterval(id); });
    } catch (_) { /* noop */ }
  }
})();
