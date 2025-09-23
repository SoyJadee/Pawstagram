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
      if (!btn) return null;
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
            if (status !== 'SUBSCRIBED') console.warn('Canal index_notifications estado:', status);
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
            if (status !== 'SUBSCRIBED') console.warn('Canal adopcion_adoption estado:', status);
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
      console.error('Error creando canales Realtime:', e);
    }
  } else if ('EventSource' in window && validUser) {
    // Fallback SSE: usa el proxy backend autenticado
    try {
      const es = new EventSource('/notificaciones/stream/');
      es.addEventListener('update', (evt) => {
        try {
          const data = JSON.parse(evt.data || '{}');
          const dn = Array.isArray(data.notifications) ? data.notifications.length : 0;
          const da = Array.isArray(data.adoptions) ? data.adoptions.length : 0;
          const delta = dn + da;
          if (delta > 0) safeIncrement(delta);
        } catch (_) { /* noop */ }
      });
      es.addEventListener('error', () => {
        // Silencioso: el navegador reintenta automáticamente
      });
      window.addEventListener('beforeunload', () => es.close());
      document.addEventListener('visibilitychange', () => { if (document.hidden) es.close(); });
    } catch (e) {
      console.warn('No se pudo iniciar SSE fallback:', e);
    }
  }
})();
