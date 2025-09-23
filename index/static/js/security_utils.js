(function (w) {
  'use strict';
  if (w.SecurityUtils) return;

  const getCookie = (name) => {
    try {
      const v = document.cookie
        .split(';')
        .map((s) => s.trim())
        .find((s) => s.startsWith(name + '='));
      return v ? decodeURIComponent(v.split('=')[1]) : null;
    } catch {
      return null;
    }
  };

  const getCSRF = (form) =>
    form?.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
    getCookie('csrftoken') ||
    '';

  const sanitizeId = (val) => {
    const s = String(val || '').trim();
    if (!/^\d+$/.test(s)) return null;
    const n = parseInt(s, 10);
    return Number.isFinite(n) && n > 0 ? String(n) : null;
  };

  const sanitizeText = (txt) => String(txt || '').replace(/[\u0000-\u001F]/g, '').trim();

  const throttle = (fn, wait) => {
    let last = 0;
    let timer = null;
    return (...args) => {
      const now = Date.now();
      const run = () => fn.apply(null, args);
      if (now - last >= wait) {
        last = now;
        run();
      } else if (!timer) {
        const remaining = wait - (now - last);
        timer = setTimeout(() => {
          last = Date.now();
          timer = null;
          run();
        }, remaining);
      }
    };
  };

  const parseIntFromText = (text) => {
    const m = String(text || '').match(/\d+/);
    const num = m ? parseInt(m[0], 10) : 0;
    return Number.isFinite(num) ? num : 0;
  };

  w.SecurityUtils = {
    getCookie,
    getCSRF,
    sanitizeId,
    sanitizeText,
    throttle,
    parseIntFromText,
  };
})(window);
