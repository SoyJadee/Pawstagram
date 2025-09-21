// historias.js
// Lógica para subir historias y mostrar el modal tipo Instagram

document.addEventListener('DOMContentLoaded', function () {
  // [Código existente para subir historias...]
  // Abrir modal de subir historia
  const addBtn = document.getElementById('add-historia-btn');
  const modalSubir = document.getElementById('modal-subir-historia');
  if (addBtn && modalSubir) {
    addBtn.addEventListener('click', function () {
      modalSubir.classList.remove('hidden');
    });
  }

  // Cerrar modal de subir historia
  window.cerrarModalSubirHistoria = function () {
    modalSubir.classList.add('hidden');
    document.getElementById('form-subir-historia').reset();
  };

  // Subir historia por AJAX
  const form = document.getElementById('form-subir-historia');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const fileInput = form.querySelector('input[name="foto_historia"]');
      const file = fileInput.files[0];
      if (!file) return;
      // Mostrar modal de cargando
      const modalCargando = document.getElementById('modal-cargando-historia');
      const btnSubir = document.getElementById('btn-subir-historia');
      if (modalCargando) modalCargando.classList.remove('hidden');
      if (btnSubir) btnSubir.disabled = true;
      const formData = new FormData();
      formData.append('foto_historia', file);
      fetch('/historias/subir/', {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            setTimeout(() => window.location.reload(), 600);
          } else {
            if (modalCargando) modalCargando.classList.add('hidden');
            if (btnSubir) btnSubir.disabled = false;
            alert('Error al subir la historia: ' + (data.error || ''));
          }
        })
        .catch(() => {
          if (modalCargando) modalCargando.classList.add('hidden');
          if (btnSubir) btnSubir.disabled = false;
          alert('Error de red al subir la historia. Si ves tu historia al recargar, se subió correctamente.');
        });
    });
  }

  // Preview de la historia antes de subir
  window.previewHistoria = function(input) {
    const previewDiv = document.getElementById('preview-historia');
    const img = previewDiv.querySelector('img');
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function(e) {
        img.src = e.target.result;
        previewDiv.classList.remove('hidden');
      };
      reader.readAsDataURL(input.files[0]);
    } else {
      img.src = '#';
      previewDiv.classList.add('hidden');
    }
  };

  // Modal para ver historias agrupadas por usuario
  const modalHistoria = document.getElementById('modal-historia');
  // Nuevo modal estilo Instagram/WhatsApp
  const modalAvatar = document.getElementById('modal-historia-avatar');
  const modalUsername = document.getElementById('modal-historia-username');
  const modalTime = document.getElementById('modal-historia-time');
  const modalProgress = document.getElementById('modal-historia-progress');
  // const prevArea = document.getElementById('modal-historia-prev-area');
  // const nextArea = document.getElementById('modal-historia-next-area');
  // const pauseArea = document.getElementById('modal-historia-pause-area');

  // Construir estructura de historias agrupadas por usuario desde el DOM
  const historiasPorUsuario = {};
  document.querySelectorAll('.historia-slide').forEach(function (slide) {
    const usuario = slide.getAttribute('data-usuario');
    if (!usuario) return;
    // Recopilar todas las historias de este usuario desde el backend (inyectadas en window.historiasPorUsuario)
    slide.addEventListener('click', function () {
      if (window.historiasPorUsuario && window.historiasPorUsuario[usuario]) {
        abrirModalHistoriasUsuario(usuario);
      }
    });
  });

  // Estado del modal de historias
  let historiasActuales = [];
  let idxHistoriaActual = 0;
  let usuarioActual = '';
  let historiaTimer = null;
  let historiaPausada = false;
  let historiaStartTime = null;
  let historiaElapsed = 0;
  let historiaFill = null;

  // Función para abrir el modal de historias
  function abrirModalHistoriasUsuario(usuario) {
    usuarioActual = usuario;
    historiasActuales = (window.historiasPorUsuario && window.historiasPorUsuario[usuario]) ? window.historiasPorUsuario[usuario].historias : [];
    idxHistoriaActual = 0;
    if (modalHistoria) modalHistoria.classList.remove('hidden');
    mostrarHistoriaActual();
    // --- Pausa con mantener presionado en el área central ---
    const pauseArea = document.getElementById('modal-historia-pause-area');
    if (pauseArea) {
      // Elimina listeners previos
      pauseArea.onmousedown = null;
      pauseArea.onmouseup = null;
      pauseArea.onmouseleave = null;
      pauseArea.ontouchstart = null;
      pauseArea.ontouchend = null;
      pauseArea.ontouchcancel = null;
      // Pausar
      pauseArea.addEventListener('mousedown', function(e) {
        console.log('mousedown: PAUSA');
        if (!historiasActuales.length || historiaPausada) return;
        historiaPausada = true;
        clearTimeout(historiaTimer);
        if (historiaFill) {
          const elapsed = Date.now() - historiaStartTime;
          historiaElapsed += elapsed;
          const percent = Math.min(historiaElapsed / 3500, 1) * 100;
          historiaFill.style.transition = 'none';
          historiaFill.style.width = percent + '%';
        }
      });
      // Reanudar
      pauseArea.addEventListener('mouseup', function(e) {
        console.log('mouseup: REANUDAR');
        if (!historiasActuales.length || !historiaPausada) return;
        historiaPausada = false;
        historiaStartTime = Date.now();
        if (historiaFill) {
          const percent = Math.min(historiaElapsed / 3500, 1) * 100;
          historiaFill.style.transition = `width ${(3500 - historiaElapsed) / 1000}s linear`;
          historiaFill.style.width = '100%';
        }
        historiaTimer = setTimeout(() => {
          if (!historiaPausada) {
            if (idxHistoriaActual < historiasActuales.length - 1) {
              idxHistoriaActual++;
              historiaElapsed = 0;
              mostrarHistoriaActual();
            } else {
              cerrarModalHistoria();
            }
          }
        }, 3500 - historiaElapsed);
      });
      pauseArea.addEventListener('mouseleave', function(e) {
        console.log('mouseleave: REANUDAR');
        if (!historiasActuales.length || !historiaPausada) return;
        historiaPausada = false;
        historiaStartTime = Date.now();
        if (historiaFill) {
          const percent = Math.min(historiaElapsed / 3500, 1) * 100;
          historiaFill.style.transition = `width ${(3500 - historiaElapsed) / 1000}s linear`;
          historiaFill.style.width = '100%';
        }
        historiaTimer = setTimeout(() => {
          if (!historiaPausada) {
            if (idxHistoriaActual < historiasActuales.length - 1) {
              idxHistoriaActual++;
              historiaElapsed = 0;
              mostrarHistoriaActual();
            } else {
              cerrarModalHistoria();
            }
          }
        }, 3500 - historiaElapsed);
      });
      // Touch
      pauseArea.addEventListener('touchstart', function(e) {
        e.preventDefault();
        console.log('touchstart: PAUSA');
        if (!historiasActuales.length || historiaPausada) return;
        historiaPausada = true;
        clearTimeout(historiaTimer);
        if (historiaFill) {
          const elapsed = Date.now() - historiaStartTime;
          historiaElapsed += elapsed;
          const percent = Math.min(historiaElapsed / 3500, 1) * 100;
          historiaFill.style.transition = 'none';
          historiaFill.style.width = percent + '%';
        }
      });
      pauseArea.addEventListener('touchend', function(e) {
        e.preventDefault();
        console.log('touchend: REANUDAR');
        if (!historiasActuales.length || !historiaPausada) return;
        historiaPausada = false;
        historiaStartTime = Date.now();
        if (historiaFill) {
          const percent = Math.min(historiaElapsed / 3500, 1) * 100;
          historiaFill.style.transition = `width ${(3500 - historiaElapsed) / 1000}s linear`;
          historiaFill.style.width = '100%';
        }
        historiaTimer = setTimeout(() => {
          if (!historiaPausada) {
            if (idxHistoriaActual < historiasActuales.length - 1) {
              idxHistoriaActual++;
              historiaElapsed = 0;
              mostrarHistoriaActual();
            } else {
              cerrarModalHistoria();
            }
          }
        }, 3500 - historiaElapsed);
      });
      pauseArea.addEventListener('touchcancel', function(e) {
        e.preventDefault();
        console.log('touchcancel: REANUDAR');
        if (!historiasActuales.length || !historiaPausada) return;
        historiaPausada = false;
        historiaStartTime = Date.now();
        if (historiaFill) {
          const percent = Math.min(historiaElapsed / 3500, 1) * 100;
          historiaFill.style.transition = `width ${(3500 - historiaElapsed) / 1000}s linear`;
          historiaFill.style.width = '100%';
        }
        historiaTimer = setTimeout(() => {
          if (!historiaPausada) {
            if (idxHistoriaActual < historiasActuales.length - 1) {
              idxHistoriaActual++;
              historiaElapsed = 0;
              mostrarHistoriaActual();
            } else {
              cerrarModalHistoria();
            }
          }
        }, 3500 - historiaElapsed);
      });
    }
  }

  // Configurar eventos de navegación


  // Función para navegar a la historia anterior


  function mostrarHistoriaActual() {
    // Botón de pausa/reanudar
    const btnPausa = document.getElementById('historia-pause-btn');
    if (btnPausa) {
      btnPausa.onclick = function(e) {
        e.stopPropagation();
        if (historiaPausada) {
          // Reanudar
          historiaPausada = false;
          historiaStartTime = Date.now();
          if (historiaFill) {
            const percent = Math.min(historiaElapsed / 3500, 1) * 100;
            historiaFill.style.transition = `width ${(3500 - historiaElapsed) / 1000}s linear`;
            historiaFill.style.width = '100%';
          }
          historiaTimer = setTimeout(() => {
            if (!historiaPausada) {
              if (idxHistoriaActual < historiasActuales.length - 1) {
                idxHistoriaActual++;
                historiaElapsed = 0;
                mostrarHistoriaActual();
              } else {
                cerrarModalHistoria();
              }
            }
          }, 3500 - historiaElapsed);
          btnPausa.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
          // Pausar
          historiaPausada = true;
          clearTimeout(historiaTimer);
          if (historiaFill) {
            const elapsed = Date.now() - historiaStartTime;
            historiaElapsed += elapsed;
            const percent = Math.min(historiaElapsed / 3500, 1) * 100;
            historiaFill.style.transition = 'none';
            historiaFill.style.width = percent + '%';
          }
          btnPausa.innerHTML = '<i class="fas fa-play"></i>';
        }
      };
      // Estado inicial
      btnPausa.innerHTML = historiaPausada ? '<i class="fas fa-play"></i>' : '<i class="fas fa-pause"></i>';
    }
    if (!historiasActuales.length) return;
    clearTimeout(historiaTimer);
    historiaPausada = false;
    historiaElapsed = 0;
    historiaStartTime = Date.now();
    const historia = historiasActuales[idxHistoriaActual];

    // Avatar: foto de perfil o logo por defecto
    if (modalAvatar) {
      let fotoPerfil = null;
      if (window.historiasPorUsuario && window.historiasPorUsuario[usuarioActual] && window.historiasPorUsuario[usuarioActual].user && window.historiasPorUsuario[usuarioActual].user.profile_photo_url) {
        fotoPerfil = window.historiasPorUsuario[usuarioActual].user.profile_photo_url;
      }
      if (fotoPerfil) {
        modalAvatar.innerHTML = `<img src="${fotoPerfil}" alt="avatar" class="w-10 h-10 rounded-full object-cover" style="background:#fff;">`;
      } else {
        modalAvatar.innerHTML = `<img src="/static/img/logo1.png" alt="avatar" class="w-10 h-10 rounded-full object-cover" style="background:#fff;">`;
      }
    }

    // Nombre usuario
    if (modalUsername) modalUsername.textContent = usuarioActual;

    // Tiempo (formato tipo Instagram)
    if (modalTime && historia.created_at) {
      const fecha = new Date(historia.created_at);
      const ahora = new Date();
      const diffMs = ahora - fecha;
      const diffMin = Math.floor(diffMs / (1000 * 60));
      const diffH = Math.floor(diffMs / (1000 * 60 * 60));
      const diffD = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      let texto = '';
      if (diffMin < 1) {
        texto = 'recién';
      } else if (diffMin < 60) {
        texto = `hace ${diffMin} min`;
      } else if (diffH < 24) {
        texto = `hace ${diffH} h`;
      } else {
        texto = `hace ${diffD} d`;
      }
      modalTime.textContent = texto;
    }

    // Progreso animado
    if (modalProgress) {
      modalProgress.innerHTML = '';
      for (let i = 0; i < historiasActuales.length; i++) {
        const bar = document.createElement('div');
        bar.className = 'flex-1 h-1 bg-white/30 rounded overflow-hidden relative';
        const fill = document.createElement('div');
        fill.className = 'h-full bg-white rounded absolute left-0 top-0 transition-all duration-200';
        if (i < idxHistoriaActual) {
          fill.style.width = '100%';
          fill.style.opacity = '1';
        } else if (i === idxHistoriaActual) {
          fill.style.width = '0%';
          fill.style.opacity = '1';
          historiaFill = fill;
          setTimeout(() => {
            fill.style.transition = `width 3.5s linear`;
            fill.style.width = '100%';
          }, 10);
        } else {
          fill.style.width = '0%';
          fill.style.opacity = '0.5';
        }
        bar.appendChild(fill);
        modalProgress.appendChild(bar);
      }
    }

    // Contenido (solo imagen, si hay; si no, solo fondo negro) y flechas
    const modalContent = document.getElementById('modal-historia-content');
    if (modalContent) {
      // Asegura que los botones de flecha existan siempre
      let prevBtn = document.getElementById('historia-flecha-prev');
      let nextBtn = document.getElementById('historia-flecha-next');
      if (!prevBtn) {
        prevBtn = document.createElement('button');
        prevBtn.id = 'historia-flecha-prev';
        prevBtn.type = 'button';
        prevBtn.innerHTML = '&#8592;';
        prevBtn.style.display = 'none';
        prevBtn.style.position = 'absolute';
        prevBtn.style.left = '10px';
        prevBtn.style.top = '50%';
        prevBtn.style.transform = 'translateY(-50%)';
        prevBtn.style.background = 'rgba(0,0,0,0.4)';
        prevBtn.style.border = 'none';
        prevBtn.style.borderRadius = '50%';
        prevBtn.style.width = '40px';
        prevBtn.style.height = '40px';
        prevBtn.style.color = 'white';
        prevBtn.style.fontSize = '2rem';
        prevBtn.style.zIndex = '30';
        prevBtn.style.alignItems = 'center';
        prevBtn.style.justifyContent = 'center';
        modalContent.appendChild(prevBtn);
      }
      if (!nextBtn) {
        nextBtn = document.createElement('button');
        nextBtn.id = 'historia-flecha-next';
        nextBtn.type = 'button';
        nextBtn.innerHTML = '&#8594;';
        nextBtn.style.display = 'none';
        nextBtn.style.position = 'absolute';
        nextBtn.style.right = '10px';
        nextBtn.style.top = '50%';
        nextBtn.style.transform = 'translateY(-50%)';
        nextBtn.style.background = 'rgba(0,0,0,0.4)';
        nextBtn.style.border = 'none';
        nextBtn.style.borderRadius = '50%';
        nextBtn.style.width = '40px';
        nextBtn.style.height = '40px';
        nextBtn.style.color = 'white';
        nextBtn.style.fontSize = '2rem';
        nextBtn.style.zIndex = '30';
        nextBtn.style.alignItems = 'center';
        nextBtn.style.justifyContent = 'center';
        modalContent.appendChild(nextBtn);
      }
      // Borra solo los hijos que sean imagen o p
      Array.from(modalContent.children).forEach(child => {
        if (child.tagName === 'IMG' || child.tagName === 'P') modalContent.removeChild(child);
      });
      if (historia.photo_url) {
        const img = document.createElement('img');
        img.src = historia.photo_url;
        img.alt = 'Historia';
        img.className = 'max-h-[400px] max-w-full rounded-xl shadow-lg object-contain bg-black';
        modalContent.insertBefore(img, prevBtn || nextBtn || null);
      } else {
        const p = document.createElement('p');
        p.textContent = '';
        modalContent.insertBefore(p, prevBtn || nextBtn || null);
      }
      // SIEMPRE re-asigna y muestra/oculta flechas
      prevBtn.onclick = null;
      if (historiasActuales.length > 1 && idxHistoriaActual > 0) {
        prevBtn.style.display = 'flex';
        prevBtn.onclick = function(e) {
          e.stopPropagation();
          if (idxHistoriaActual > 0) {
            idxHistoriaActual--;
            mostrarHistoriaActual();
          }
        };
      } else {
        prevBtn.style.display = 'none';
      }
      nextBtn.onclick = null;
      if (historiasActuales.length > 1 && idxHistoriaActual < historiasActuales.length - 1) {
        nextBtn.style.display = 'flex';
        nextBtn.onclick = function(e) {
          e.stopPropagation();
          if (idxHistoriaActual < historiasActuales.length - 1) {
            idxHistoriaActual++;
            mostrarHistoriaActual();
          }
        };
      } else {
        nextBtn.style.display = 'none';
      }
    }



    // Cambio automático de historia
    historiaTimer = setTimeout(() => {
      if (!historiaPausada) {
        if (idxHistoriaActual < historiasActuales.length - 1) {
          idxHistoriaActual++;
          mostrarHistoriaActual();
        } else {
          cerrarModalHistoria();
        }
      }
    }, 3500);
  }



  window.cerrarModalHistoria = function () {
    if (historiaTimer) clearTimeout(historiaTimer);
    if (modalHistoria) modalHistoria.classList.add('hidden');
    if (modalAvatar) modalAvatar.textContent = '';
    if (modalUsername) modalUsername.textContent = '';
    if (modalTime) modalTime.textContent = '';
    if (document.getElementById('modal-historia-content')) {
      document.getElementById('modal-historia-content').innerHTML = '';
    }
    if (modalProgress) modalProgress.innerHTML = '';
    historiasActuales = [];
    idxHistoriaActual = 0;
    usuarioActual = '';
    historiaPausada = false;
  };
  // --- Siempre mostrar 'Agregar historia' de primero ---
  // Ajusta los selectores según tu HTML real
  document.addEventListener('DOMContentLoaded', function () {
    const contenedor = document.querySelector('.historias-contenedor, .historias-list, .historias, .row'); // Ajusta el selector al de tu contenedor real
    const agregar = document.getElementById('add-historia-btn')?.parentElement;
    if (contenedor && agregar) {
      contenedor.insertBefore(agregar, contenedor.firstChild);
    }
  });
});