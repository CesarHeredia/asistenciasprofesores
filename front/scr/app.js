// app.js - Gestión de Asistencia Desktop Frontend (SPA con carga de parciales)

// 1. Configuración de Tiempos y Variables de Estado
const timeSlots = [
  { start: "07:00", end: "07:45" },
  { start: "07:45", end: "08:30" },
  { start: "08:30", end: "09:15" },
  { start: "09:15", end: "10:00" },
  { start: "10:00", end: "10:45" },
  { start: "10:45", end: "11:30" },
  { start: "11:30", end: "12:15" },
  { start: "12:15", end: "13:00" },
  { start: "13:00", end: "13:45" },
  { start: "13:45", end: "14:30" },
  { start: "14:30", end: "15:15" },
  { start: "15:15", end: "16:00" },
  { start: "16:00", end: "16:45" },
  { start: "16:45", end: "17:30" }
];

/* Utility Functions */
function timeToMinutes(t) {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
}

function getCurrentStatus(slots) {
  const now = new Date();
  const dayNames = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  const currentDay = dayNames[now.getDay()];
  const currentMin = now.getHours() * 60 + now.getMinutes();
  for (const s of slots) {
    if (s.dia === currentDay) {
      const start = timeToMinutes(s.hora_inicio);
      const end = timeToMinutes(s.hora_fin);
      if (currentMin >= start && currentMin < end) {
        return `${s.materia} en ${s.aula}`;
      }
    }
  }
  return "Hora libre";
}

function getProfessorStatus(horaEntrada, horaSalida, scheduleSlots, evalDate = new Date(), evalTimeStr = null) {
  if (!horaEntrada || horaEntrada.trim() === '') {
    return {
      code: "Ausente",
      label: "Ausente",
      colorClass: "gray",
      style: 'font-weight: 700; color: #64748b; background: #f1f5f9; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #cbd5e1;'
    };
  }

  const dayNames = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  const currentDay = dayNames[evalDate.getDay()];
  const todaySlots = (scheduleSlots || []).filter(s => s.dia === currentDay);

  let lastClassEndMin = 0;
  let inClass = false;
  
  let currentMin = evalDate.getHours() * 60 + evalDate.getMinutes();
  if (evalTimeStr) {
    const [h, m] = evalTimeStr.split(':').map(Number);
    currentMin = h * 60 + m;
  }

  todaySlots.forEach(s => {
    const start = timeToMinutes(s.hora_inicio);
    const end = timeToMinutes(s.hora_fin);
    if (end > lastClassEndMin) {
      lastClassEndMin = end;
    }
    if (currentMin >= start && currentMin < end) {
      inClass = true;
    }
  });

  const hasExit = horaSalida && horaSalida.trim() !== '';

  if (!hasExit) {
    if (todaySlots.length > 0 && currentMin > lastClassEndMin) {
      return {
        code: "SinMarcarSalida",
        label: "Sin Marcar Salida",
        colorClass: "red",
        style: 'font-weight: 700; color: #dc2626; background: #fef2f2; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #fecaca;'
      };
    } else {
      if (inClass) {
        return {
          code: "ActivoEnClase",
          label: "Activo - En clase",
          colorClass: "yellow",
          style: 'font-weight: 700; color: #ca8a04; background: #fef9c3; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #fef08a;'
        };
      } else {
        return {
          code: "ActivoHoraLibre",
          label: "Activo - Hora Libre",
          colorClass: "yellow",
          style: 'font-weight: 700; color: #ca8a04; background: #fef9c3; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #fef08a;'
        };
      }
    }
  } else {
    const exitMin = timeToMinutes(horaSalida);
    if (todaySlots.length > 0 && exitMin < lastClassEndMin) {
      return {
        code: "SalidaTemprana",
        label: "Salida Temprana",
        colorClass: "red",
        style: 'font-weight: 700; color: #dc2626; background: #fef2f2; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #fecaca;'
      };
    } else {
      return {
        code: "Completado",
        label: "Completado",
        colorClass: "green",
        style: 'font-weight: 700; color: #16a34a; background: #f0fdf4; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #bbf7d0;'
      };
    }
  }
}

function initClock() {
  const timeEl = document.getElementById('sidebar-time');
  const dateEl = document.getElementById('sidebar-date');
  if (!timeEl || !dateEl) return;
  const update = () => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    const dateStr = now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    timeEl.textContent = timeStr;
    dateEl.textContent = dateStr;
  };
  update();
  setInterval(update, 1000);
}


const diasSemana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];

let rawDashboardData = [];
let auditFullHistory = [];  // Cache del historial completo de auditoría
let currentView = 'dashboard';
let currentSelectedProfesor = null;
let dashboardRefreshInterval = null; // Intervalo de refresco de tarjetas en tiempo real

// Estado para arrastrar y seleccionar en el horario
let isDraggingSchedule = false;
let dragStartRow = null;
let dragEndRow = null;
let dragCol = null;

// Columnas amigables para renderizado dinámico en CRUD
const friendlyNames = {
  "id_profesor": "ID Profesor",
  "id_materia": "ID Materia",
  "nb_profesor": "Nombre",
  "ap_profesor": "Apellidos",
  "nb_materia": "Nombre de la Materia",
  "qr_content": "Código QR",
  "departamento": "Departamento",
  "edificio": "Edificio",
  "telefono_personal": "Teléfono Personal",
  "telefono_emergencia": "Teléfono de Emergencia",
  "cedula": "Cédula"
};

// Mapa de parciales HTML
const viewPartials = {
  'dashboard': 'scr/dashboard/dashboard.html',
  'database-profesores': 'scr/dashboard/profesores.html',
  'database-materias': 'scr/dashboard/materias.html',
  'auditoria': 'scr/dashboard/auditoria.html',
  'perfil': 'scr/dashboard/perfil.html',
  'chat-ia': 'scr/dashboard/chat-ia.html'
};

// ==========================================================================
// 2. Carga de Vistas Parciales (SPA)
// ==========================================================================
async function loadPartial(viewName) {
  const url = viewPartials[viewName];
  if (!url) return null;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.text();
  } catch (err) {
    console.error(`Error cargando parcial ${url}:`, err);
    return `<div class="error-state">Error al cargar la vista. (${err.message})</div>`;
  }
}

// ==========================================================================
// 3. Eventos Iniciales y Enrutador SPA
// ==========================================================================
window.addEventListener('DOMContentLoaded', async () => {
  await loadModals();
  initNavigation();
  initClock();
  initLandingAndLoginEvents();

  // Iniciar con el lector QR de profesores en la landing page
  startLandingQrScanner();

  if (window.eel) {
    console.log("Eel cargado y listo.");
  } else {
    console.warn("Eel no está disponible. Ejecutando con datos mock.");
  }
});

function initLandingAndLoginEvents() {
  // Navegación: Ir a Administrador
  document.getElementById('btn-go-to-admin').addEventListener('click', () => {
    stopLandingQrScanner();
    document.getElementById('landing-layout').classList.add('hidden');
    document.getElementById('login-layout').classList.remove('hidden');
    document.getElementById('login-error-msg').classList.add('hidden');
    document.getElementById('login-username').value = '';
    document.getElementById('login-password').value = '';
  });

  // Navegación: Volver a Lector
  document.getElementById('btn-back-to-scanner').addEventListener('click', () => {
    document.getElementById('login-layout').classList.add('hidden');
    document.getElementById('landing-layout').classList.remove('hidden');
    startLandingQrScanner();
  });

  // Formulario de Login Admin (credenciales dinámicas de la base de datos)
  document.getElementById('admin-login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('login-username').value.trim();
    const pass = document.getElementById('login-password').value.trim();

    try {
      let config = { username: 'admin', password: 'admin' };
      if (window.eel) {
        config = await eel.get_admin_config()();
      }

      if (user === config.username && pass === config.password) {
        // Éxito: Entrar a la app de admin
        document.getElementById('login-layout').classList.add('hidden');
        document.getElementById('admin-layout').classList.remove('hidden');

        // Iniciar el dashboard admin
        initFilters();
        navigateView('dashboard');
      } else {
        // Error
        document.getElementById('login-error-msg').classList.remove('hidden');
      }
    } catch (err) {
      console.error("Error validando credenciales:", err);
      document.getElementById('login-error-msg').classList.remove('hidden');
    }
  });

  // Navegación: Cerrar Sesión
  document.getElementById('btn-admin-logout').addEventListener('click', () => {
    // Detener auto-refrescos
    if (dashboardRefreshInterval) {
      clearInterval(dashboardRefreshInterval);
      dashboardRefreshInterval = null;
    }

    // Ocultar layout de administrador, mostrar landing
    document.getElementById('admin-layout').classList.add('hidden');
    document.getElementById('landing-layout').classList.remove('hidden');

    // Volver a iniciar el escáner del landing
    startLandingQrScanner();
  });
}

async function loadModals() {
  try {
    const resp = await fetch('scr/dashboard/modals.html');
    if (resp.ok) {
      const html = await resp.text();
      document.getElementById('modals-container').innerHTML = html;

      // Bindear eventos de modales que antes estaban inline, si fuera necesario.
      // (Los eventos inline onclick= ya funcionan si se insertan con innerHTML)
      document.getElementById('modal-submit-btn').addEventListener('click', handleCrudSubmit);
      document.getElementById('schedule-submit-btn').addEventListener('click', handleScheduleSubmit);
    }
  } catch (err) {
    console.error("Error cargando modales:", err);
  }
}

// Inicializar navegación por pestañas en el sidebar
function initNavigation() {
  document.querySelectorAll('.menu-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetView = btn.getAttribute('data-view');

      if (targetView === 'horarios' && !currentSelectedProfesor) {
        alert("Por favor, selecciona un profesor en 'Ver Docentes' y haz clic en su botón ' Horario' para configurar su grilla.");
        return;
      }

      navigateView(targetView);
    });
  });
}

async function navigateView(viewName) {
  currentView = viewName;
  const contentEl = document.getElementById('content');

  // Limpiar refresco automático del dashboard si navegamos a otra vista
  if (dashboardRefreshInterval && viewName !== 'dashboard') {
    clearInterval(dashboardRefreshInterval);
    dashboardRefreshInterval = null;
  }

  // Ocultar todas las vistas previas con animación
  document.querySelectorAll('.menu-btn').forEach(btn => btn.classList.remove('active'));

  // Mapear la pestaña activa del sidebar
  let activeBtn = document.querySelector(`.menu-btn[data-view="${viewName}"]`);
  if (viewName === 'database-profesores') {
    activeBtn = document.querySelector('.menu-btn[data-view="dashboard"]');
  }
  if (activeBtn) activeBtn.classList.add('active');

  // Si es un parcial, cargarlo
  if (viewPartials[viewName]) {
    const html = await loadPartial(viewName);
    contentEl.innerHTML = html;
    // Re-bindear eventos de botones de acción dentro de los parciales
    bindPartialActions();
  }

  // Cargar datos para la vista
  if (viewName === 'dashboard') {
    // Restaurar sidebar default si veníamos de auditoría
    const defaultSidebar = document.getElementById('default-sidebar-content');
    const auditSidebar = document.getElementById('audit-sidebar-content');
    if (defaultSidebar) defaultSidebar.style.display = 'block';
    if (auditSidebar) auditSidebar.style.display = 'none';
    loadDashboard();
  } else if (viewName === 'database-profesores') {
    const defaultSidebar = document.getElementById('default-sidebar-content');
    const auditSidebar = document.getElementById('audit-sidebar-content');
    if (defaultSidebar) defaultSidebar.style.display = 'block';
    if (auditSidebar) auditSidebar.style.display = 'none';
    loadCrudTable('profesor');
  } else if (viewName === 'database-materias') {
    const defaultSidebar = document.getElementById('default-sidebar-content');
    const auditSidebar = document.getElementById('audit-sidebar-content');
    if (defaultSidebar) defaultSidebar.style.display = 'block';
    if (auditSidebar) auditSidebar.style.display = 'none';
    loadCrudTable('materia');
  } else if (viewName === 'horarios' && currentSelectedProfesor) {
    renderHorarioView();
  } else if (viewName === 'auditoria') {
    // Mostrar sidebar de auditoría, ocultar el default
    const defaultSidebar = document.getElementById('default-sidebar-content');
    const auditSidebar = document.getElementById('audit-sidebar-content');
    if (defaultSidebar) defaultSidebar.style.display = 'none';
    if (auditSidebar) auditSidebar.style.display = 'block';
    loadAuditTable();
  } else if (viewName === 'perfil') {
    // Ocultar ambos sidebars en la vista de perfil
    const defaultSidebar = document.getElementById('default-sidebar-content');
    const auditSidebar = document.getElementById('audit-sidebar-content');
    if (defaultSidebar) defaultSidebar.style.display = 'none';
    if (auditSidebar) auditSidebar.style.display = 'none';
    loadAdminProfile();
  } else if (viewName === 'chat-ia') {
    // Ocultar ambos sidebars en la vista del asistente IA
    const defaultSidebar = document.getElementById('default-sidebar-content');
    const auditSidebar = document.getElementById('audit-sidebar-content');
    if (defaultSidebar) defaultSidebar.style.display = 'none';
    if (auditSidebar) auditSidebar.style.display = 'none';
    initChatIA();
  }
}

async function loadAdminProfile() {
  const form = document.getElementById('admin-profile-form');
  const usernameInput = document.getElementById('profile-username');
  const passwordInput = document.getElementById('profile-password');
  const keyInput = document.getElementById('profile-gemini-key');
  const toggleBtn = document.getElementById('btn-toggle-profile-pass');
  const toggleKeyBtn = document.getElementById('btn-toggle-profile-key');
  if (!usernameInput || !passwordInput) return;

  try {
    let config = { username: 'admin', password: 'admin', gemini_api_key: '' };
    if (window.eel) {
      config = await eel.get_admin_config()();
    }
    usernameInput.value = config.username;
    passwordInput.value = config.password;
    if (keyInput) keyInput.value = config.gemini_api_key || '';
  } catch (err) {
    console.error("Error cargando configuración de administrador:", err);
  }

  if (toggleBtn) {
    toggleBtn.onclick = () => {
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = '🔒';
      } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = '👁️';
      }
    };
  }

  if (toggleKeyBtn && keyInput) {
    toggleKeyBtn.onclick = () => {
      if (keyInput.type === 'password') {
        keyInput.type = 'text';
        toggleKeyBtn.textContent = '🔒';
      } else {
        keyInput.type = 'password';
        toggleKeyBtn.textContent = '👁️';
      }
    };
  }

  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const newUsername = usernameInput.value.trim();
      const newPassword = passwordInput.value.trim();
      const newKey = keyInput ? keyInput.value.trim() : '';
      if (!newUsername || !newPassword) {
        alert("El usuario y la contraseña no pueden estar vacíos.");
        return;
      }

      try {
        let res = { success: true };
        if (window.eel) {
          res = await eel.update_admin_config(newUsername, newPassword, newKey)();
        }
        if (res && res.success) {
          if (typeof _showQrToast === 'function') {
            _showQrToast("Perfil de administrador actualizado exitosamente.");
          } else {
            alert("Perfil de administrador actualizado exitosamente.");
          }
        } else {
          alert("Error al actualizar perfil: " + (res ? res.error : "Error desconocido"));
        }
      } catch (err) {
        console.error("Error al guardar perfil de admin:", err);
        alert("Error al guardar perfil de administrador.");
      }
    };
  }
}

async function initChatIA() {
  const alertEl = document.getElementById('api-key-alert');
  if (!alertEl) return;

  try {
    let config = { username: 'admin', password: 'admin', gemini_api_key: '' };
    if (window.eel) {
      config = await eel.get_admin_config()();
    }
    if (!config.gemini_api_key) {
      alertEl.style.display = 'flex';
    } else {
      alertEl.style.display = 'none';
    }
  } catch (err) {
    console.error("Error al verificar API Key:", err);
  }

  const msgsEl = document.getElementById('chat-messages');
  if (msgsEl) {
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }
}

async function sendChatMessage() {
  const inputEl = document.getElementById('chat-input');
  if (!inputEl) return;
  const question = inputEl.value.trim();
  if (!question) return;

  inputEl.value = '';
  await appendAndProcessChat(question);
}

async function sendQuickSuggestion(text) {
  await appendAndProcessChat(text);
}

async function appendAndProcessChat(text) {
  const msgsEl = document.getElementById('chat-messages');
  const indicatorEl = document.getElementById('chat-typing-indicator');
  if (!msgsEl) return;

  const userMsg = document.createElement('div');
  userMsg.className = 'message user';
  userMsg.innerHTML = `
    <div class="message-avatar">👤</div>
    <div class="message-content">${escapeHTML(text)}</div>
  `;
  msgsEl.appendChild(userMsg);
  msgsEl.scrollTop = msgsEl.scrollHeight;

  if (indicatorEl) indicatorEl.style.display = 'block';

  try {
    let reply = "Lo siento, la comunicación con el backend no está disponible.";
    if (window.eel) {
      const res = await eel.ask_ai_assistant(text)();
      if (res && res.success) {
        reply = res.reply;
      } else {
        reply = `❌ Error: ${res ? res.error : "Error desconocido"}`;
      }
    }
    
    const assistantMsg = document.createElement('div');
    assistantMsg.className = 'message assistant';
    assistantMsg.innerHTML = `
      <div class="message-avatar">🤖</div>
      <div class="message-content">${formatMarkdown(reply)}</div>
    `;
    msgsEl.appendChild(assistantMsg);
  } catch (err) {
    console.error("Error al preguntar al asistente:", err);
    const errorMsg = document.createElement('div');
    errorMsg.className = 'message assistant';
    errorMsg.innerHTML = `
      <div class="message-avatar">🤖</div>
      <div class="message-content">❌ Error al comunicarse con el asistente IA. Por favor, asegúrate de que tienes conexión a internet y tu API Key es válida.</div>
    `;
    msgsEl.appendChild(errorMsg);
  } finally {
    if (indicatorEl) indicatorEl.style.display = 'none';
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }
}

function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}

function formatMarkdown(text) {
  let formatted = escapeHTML(text);
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
  formatted = formatted.replace(/\n/g, '<br />');
  return formatted;
}

window.sendQuickSuggestion = sendQuickSuggestion;
window.sendChatMessage = sendChatMessage;

// Bindear eventos de acción dentro de los parciales cargados dinámicamente
function bindPartialActions() {
  // Botón toggle view
  const toggleBtn = document.querySelector('[data-action="toggle-view"]');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => toggleProfesorView());
  }

  // Botón load more
  const loadMoreBtn = document.getElementById('load-more-btn');
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
      alert("Todos los profesores activos de la base de datos ya han sido cargados.");
    });
  }
}

// Alternar entre vista de tarjetas del dashboard y vista de tabla CRUD para profesores
function toggleProfesorView() {
  if (currentView === 'dashboard') {
    navigateView('database-profesores');
  } else {
    navigateView('dashboard');
  }
}

// ==========================================================================
// 4. Vista de Horarios (se genera dinámicamente, no desde parcial)
// ==========================================================================
function renderHorarioView() {
  const contentEl = document.getElementById('content');
  contentEl.innerHTML = `
    <section id="view-horarios" class="content-view">
      <header class="panel-header flex-header">
        <div class="title-meta-group">
          <h1 class="main-title" id="schedule-title">HORARIO SEMANAL</h1>
          <span class="schedule-subtitle" id="schedule-subtitle">Selecciona un profesor para configurar su horario</span>
        </div>
        <button class="action-btn secondary-btn" id="btn-volver-profesores">
          <span>Volver a Profesores</span>
        </button>
      </header>

      <div class="schedule-tip">
        <svg class="tip-icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
        <span>Haz clic y arrastra sobre celdas vacías del mismo día para asignar una materia y aula, o haz clic sobre una asignación existente para borrarla.</span>
      </div>

      <div class="scroll-container schedule-scroll">
        <div class="schedule-table-container">
          <table class="schedule-table" id="schedule-grid">
            <thead>
              <tr>
                <th class="time-header">Horario</th>
                <th>Lunes</th>
                <th>Martes</th>
                <th>Miércoles</th>
                <th>Jueves</th>
                <th>Viernes</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </section>
  `;

  document.getElementById('btn-volver-profesores').addEventListener('click', () => {
    toggleProfesorView();
  });

  renderScheduleGrid();
  initDragSelection();
  loadScheduleData(currentSelectedProfesor.id_profesor);
}

// ==========================================================================
// 5. Lógica del Dashboard y Filtros en Tiempo Real
// ==========================================================================
async function loadDashboard() {
  const container = document.getElementById('profesores-list');
  if (!container) return;
  container.innerHTML = '<div class="loading-state">Cargando profesores desde la BD...</div>';

  try {
    if (window.eel) {
      rawDashboardData = await eel.get_dashboard_data()();
    } else {
      rawDashboardData = [];
    }

    // Actualizar stat cards
    updateStatCards(rawDashboardData);
    populateFilterDropdowns(rawDashboardData);
    renderCards(rawDashboardData);

    // Activar auto-refresco de tarjetas cada 60 segundos para actualizar el estado en tiempo real
    if (dashboardRefreshInterval) clearInterval(dashboardRefreshInterval);
    dashboardRefreshInterval = setInterval(() => {
      if (currentView === 'dashboard' && rawDashboardData.length > 0) {
        renderCards(rawDashboardData);
      }
    }, 60000);

  } catch (err) {
    console.error("Error al cargar dashboard:", err);
    container.innerHTML = '<div class="error-state">Error al conectar con la base de datos. Asegúrate de ejecutar eel_main.py.</div>';
  }
}

// Actualizar las tarjetas de estadísticas
async function updateStatCards(data) {
  const elProf = document.getElementById('total-profesores');
  const elMat = document.getElementById('total-materias');
  const elHoras = document.getElementById('total-horas');
  const elAsist = document.getElementById('total-asistencias');

  if (elProf) elProf.textContent = data.length;

  // Contar materias únicas
  const materiasSet = new Set();
  data.forEach(p => {
    if (p.materia && p.materia !== "Sin Materia Asignada") {
      p.materia.split(', ').forEach(m => materiasSet.add(m));
    }
  });
  if (elMat) elMat.textContent = materiasSet.size;

  // Contar horas (cada profesor con horario = al menos 1 hora)
  let totalHoras = 0;
  data.forEach(p => {
    if (p.horario && p.horario !== "No programado") {
      totalHoras += p.horario.split(', ').length;
    }
  });
  if (elHoras) elHoras.textContent = totalHoras;

  // Asistencias - intentar desde el backend
  if (elAsist) {
    if (window.eel && typeof eel.get_stats_count === 'function') {
      try {
        const stats = await eel.get_stats_count()();
        elAsist.textContent = stats.asistencias || 0;
      } catch (e) {
        elAsist.textContent = '0';
      }
    } else {
      elAsist.textContent = '0';
    }
  }
}

// Renderizar tarjetas del panel central
function renderCards(data) {
  const container = document.getElementById('profesores-list');
  if (!container) return;
  container.innerHTML = '';

  if (!data || data.length === 0) {
    container.innerHTML = '<div class="loading-state">No se encontraron profesores con los filtros aplicados.</div>';
    return;
  }

  data.forEach(p => {
    // Calcular asignación activa en tiempo real
    const now = new Date();
    const dayNames = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
    const currentDay = dayNames[now.getDay()];
    const currentMin = now.getHours() * 60 + now.getMinutes();

    let activeSlot = null;
    if (p.schedule_slots && p.schedule_slots.length > 0) {
      for (const s of p.schedule_slots) {
        if (s.dia === currentDay) {
          const start = timeToMinutes(s.hora_inicio);
          const end = timeToMinutes(s.hora_fin);
          if (currentMin >= start && currentMin < end) {
            activeSlot = s;
            break;
          }
        }
      }
    }

    const card = document.createElement('div');
    card.className = 'profesor-card';

    const statusInfo = getProfessorStatus(p.hora_entrada, p.hora_salida, p.schedule_slots, now);

    let detailsHtml = '';
    if (statusInfo.code === "ActivoEnClase" && activeSlot) {
      detailsHtml = `
        <div class="detail-row">
          <span class="detail-label">Materia:</span>
          <span class="detail-value" style="font-weight: 600; color: var(--primary, #2563eb);">${activeSlot.materia}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Aula:</span>
          <span class="detail-value" style="font-weight: 600; color: var(--primary, #2563eb);">${activeSlot.aula}</span>
        </div>
        <div class="detail-row" style="margin-top: 8px;">
          <span class="detail-label">Estado:</span>
          <span class="detail-value" style="${statusInfo.style}">${statusInfo.label}</span>
        </div>
      `;
    } else {
      detailsHtml = `
        <div class="detail-row" style="margin-top: 10px;">
          <span class="detail-label">Estado:</span>
          <span class="detail-value" style="${statusInfo.style}">${statusInfo.label}</span>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="card-header">
        <div class="avatar-container">${p.avatar || '🧔🏽'}</div>
        <div class="name-container">
          <span class="label-profesor-title">Profesor Name:</span>
          <span class="profesor-name">${p.nombre}</span>
        </div>
      </div>
      <div class="card-details">
        ${detailsHtml}
      </div>
    `;
    container.appendChild(card);
  });
}

// Rellenar dinámicamente selectores del sidebar derecho según los datos leídos

function setupAutocomplete(inputId, listId, dataArray, onSelectCallback) {
  const input = document.getElementById(inputId);
  const list = document.getElementById(listId);
  if (!input || !list) return;

  const renderList = (filterText) => {
    list.innerHTML = '';
    const text = (filterText || '').toLowerCase().trim();
    let matches = dataArray.filter(item => item.toLowerCase().includes(text));
    
    if (matches.length === 0) {
      list.classList.add('hidden');
      return;
    }

    matches.forEach(match => {
      const div = document.createElement('div');
      div.textContent = match;
      div.onclick = (e) => {
        input.value = match;
        list.classList.add('hidden');
        if (onSelectCallback) onSelectCallback(match);
      };
      list.appendChild(div);
    });
    list.classList.remove('hidden');
  };

  input.addEventListener('input', () => renderList(input.value));
  input.addEventListener('focus', () => renderList(input.value));

  document.addEventListener('click', (e) => {
    if (e.target !== input && !list.contains(e.target)) {
      list.classList.add('hidden');
    }
  });
}

function populateFilterDropdowns(data) {
  const inputMateria = document.getElementById('filter-materia');

  const materias = new Set();

  data.forEach(p => {
    if (p.materia && p.materia !== "Sin Materia Asignada") {
      p.materia.split(', ').forEach(m => materias.add(m));
    }
  });

  const materiasArray = Array.from(materias).sort();
  setupAutocomplete('filter-materia', 'autocomplete-list-filter', materiasArray, () => {
    // Disparar evento input para que el listener de initFilters lo atrape
    if (inputMateria) inputMateria.dispatchEvent(new Event('input'));
  });
}

// Escuchas para filtrado instantáneo en el sidebar derecho
function initFilters() {
  const searchInput = document.getElementById('search-input');
  const inputMateria = document.getElementById('filter-materia');
  const selEdificio = document.getElementById('filter-edificio');
  const inputAula = document.getElementById('filter-aula');
  const depts = document.querySelectorAll('input[name="dept"]');
  const selAsist1 = document.getElementById('filter-asistencia-1');

  const applyFilters = () => {
    if (currentView !== 'dashboard') return;

    const text = searchInput.value.toLowerCase().trim();
    const mat = inputMateria ? inputMateria.value.toLowerCase().trim() : '';
    const edif = selEdificio.value;
    const aulaSearch = inputAula ? inputAula.value.trim() : '';
    const asist = selAsist1 ? selAsist1.value : '';

    const selectedDepts = Array.from(depts)
      .filter(cb => cb.checked)
      .map(cb => cb.value.toLowerCase());

    const filtered = rawDashboardData.filter(p => {
      if (text) {
        const matchName = p.nombre.toLowerCase().includes(text);
        const matchMateria = (p.materia || '').toLowerCase().includes(text);
        const matchAula = (p.aula || '').toLowerCase().includes(text);
        if (!matchName && !matchMateria && !matchAula) return false;
      }
      if (mat && !(p.materia || '').toLowerCase().includes(mat)) return false;
      if (edif || aulaSearch) {
        if (!p.aula || p.aula === "Sin Aula") return false;
        
        const aulaParts = p.aula.split(', ').map(a => a.trim());
        
        if (edif) {
          const matchModulo = aulaParts.some(a => a[0] === edif);
          if (!matchModulo) return false;
        }
        
        if (aulaSearch) {
          const matchAula = aulaParts.some(a => a.endsWith(aulaSearch));
          if (!matchAula) return false;
        }
      }
      if (selectedDepts.length > 0) {
        const dummyDept = `departamento ${(p.id_profesor % 4) + 1}`;
        if (!selectedDepts.includes(dummyDept)) return false;
      }
      
      if (asist) {
        const statusObj = getProfessorStatus(p.hora_entrada, p.hora_salida, p.schedule_slots);
        let st = statusObj.label;
        if (st.includes('Activo')) st = 'Activo';
        if (st === 'Sin Marcar Salida') st = 'No marcó salida';
        if (st.toLowerCase() !== asist.toLowerCase()) return false;
      }
      
      return true;
    });

    renderCards(filtered);
  };

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (inputMateria) inputMateria.addEventListener('input', applyFilters);
  if (selEdificio) selEdificio.addEventListener('change', applyFilters);
  if (inputAula) {
    inputAula.addEventListener('input', function() {
      let val = this.value.replace(/[^0-9]/g, '');
      if (val.length >= 1 && !/^[1-9]$/.test(val[0])) val = '';
      if (val.length >= 2 && !/^[0-4]$/.test(val[1])) val = val.slice(0, 1);
      if (val.length >= 3 && !/^[1-4]$/.test(val[2])) val = val.slice(0, 2);
      this.value = val;
      applyFilters();
    });
  }
  depts.forEach(cb => cb.addEventListener('change', applyFilters));

  if (selAsist1) {
    selAsist1.addEventListener('change', applyFilters);
  }
}

// ==========================================================================
// 6. Lógica de Bases de Datos (CRUD Completo de Profesores y Materias)
// ==========================================================================
let activeCrudTable = null;
let activeCrudData = null;

async function loadCrudTable(tableName) {
  activeCrudTable = tableName;
  const thead = document.querySelector(`#table-${tableName === 'profesor' ? 'profesores' : 'materias'} thead`);
  const tbody = document.querySelector(`#table-${tableName === 'profesor' ? 'profesores' : 'materias'} tbody`);

  if (!thead || !tbody) return;

  thead.innerHTML = '<tr><td colspan="5">Cargando datos de la tabla...</td></tr>';
  tbody.innerHTML = '';

  try {
    let response;
    if (window.eel) {
      response = await eel.get_table_data(tableName)();
    } else {
      response = { columns: [], rows: [] };
    }

    activeCrudData = response;

    // Renderizar Cabecera de Tabla
    thead.innerHTML = '';
    const headerRow = document.createElement('tr');
    response.columns.forEach(col => {
      if (col.startsWith('id_')) return; // Ocultar columnas de ID
      const th = document.createElement('th');
      th.textContent = friendlyNames[col] || col.toUpperCase();
      headerRow.appendChild(th);
    });
    const thActions = document.createElement('th');
    thActions.textContent = 'Acciones';
    headerRow.appendChild(thActions);
    thead.appendChild(headerRow);

    // Renderizar Filas
    tbody.innerHTML = '';
    if (!response.rows || response.rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="${response.columns.length + 1}" style="text-align:center;">No hay registros en la tabla.</td></tr>`;
      return;
    }

    response.rows.forEach(row => {
      const tr = document.createElement('tr');

      response.columns.forEach(col => {
        if (col.startsWith('id_')) return; // Ocultar columnas de ID
        const td = document.createElement('td');
        if (col === 'qr_content') {
          // Celda de QR clicable con menú de acción
          const val = row[col];
          const idCol = tableName === 'profesor' ? 'id_profesor' : 'id_materia';
          const rowId = row[idCol];
          const profName = tableName === 'profesor' ? `${row['nb_profesor']} ${row['ap_profesor']}`.trim() : '';
          const tieneQr = val && val.trim() !== '';
          const accionLabel = tieneQr ? 'Reemplazar QR' : 'Agregar QR';

          td.className = 'qr-cell-td';
          td.innerHTML = tieneQr
            ? `<div class="qr-badge assigned" title="${val}">
                <span class="qr-badge-icon"></span>
                <span class="qr-badge-text">Asignado</span>
               </div>
               <small class="qr-value-preview">${val.length > 35 ? val.slice(0, 35) + '…' : val}</small>`
            : `<div class="qr-badge empty">
                <span class="qr-badge-icon"></span>
                <span class="qr-badge-text">Sin QR</span>
               </div>`;

          // Botón de acción superpuesto al hacer hover (añadido como elemento separado)
          const qrBtn = document.createElement('button');
          qrBtn.className = 'qr-action-trigger';
          qrBtn.textContent = accionLabel;
          qrBtn.onclick = (e) => {
            e.stopPropagation();
            openQrScannerModal(rowId, profName, tieneQr);
          };
          td.appendChild(qrBtn);
        } else {
          let val = row[col] !== null && row[col] !== '' ? row[col] : '-';
          td.textContent = val;
          if (tableName === 'profesor' && ['telefono_personal', 'telefono_emergencia', 'cedula'].includes(col)) {
              if (val === '-') {
                  td.classList.add('editable-empty');
                  td.style.cursor = 'pointer';
                  td.style.color = '#3b82f6';
                  td.style.textDecoration = 'underline';
                  td.textContent = 'Añadir';
              } else {
                  td.style.cursor = 'pointer';
              }
              td.onclick = (e) => handleInlineEdit(tableName, rowId, col, td);
          }
        }
        tr.appendChild(td);
      });

      const tdActions = document.createElement('td');
      tdActions.className = 'action-group';

      const idCol = tableName === 'profesor' ? 'id_profesor' : 'id_materia';
      const rowId = row[idCol];

      let htmlActions = '';
      if (tableName === 'profesor') {
        const profName = `${row['nb_profesor']} ${row['ap_profesor']}`.trim();
        htmlActions += `
          <button class="table-btn schedule" onclick="viewSchedule(${rowId}, '${profName.replace(/'/g, "\\'")}')">
            Horario
          </button>
        `;
      }

      htmlActions += `
        <button class="table-btn delete" onclick="deleteRow('${tableName}', ${rowId})">
          🗑️ Eliminar
        </button>
      `;

      tdActions.innerHTML = htmlActions;
      tr.appendChild(tdActions);
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error al cargar tabla CRUD:", err);
    if (thead) thead.innerHTML = '<tr><td colspan="5">Error al leer la base de datos.</td></tr>';
  }
}

// Editar en línea campos específicos
async function handleInlineEdit(tableName, rowId, col, tdElement) {
    const isTelefono = col.startsWith('telefono');
    const isCedula = col === 'cedula';
    const label = friendlyNames[col] || col;

    let currentValue = tdElement.textContent;
    if (currentValue === 'Añadir' || currentValue === '-') currentValue = '';

    const newValue = prompt(`Ingresa nuevo valor para ${label}:`, currentValue);
    if (newValue === null) return; // User cancelled

    const val = newValue.trim();

    // Validations
    if (val !== '') {
        if (isCedula) {
            // Validation: 7 or 8 digits
            if (!/^\d{7,8}$/.test(val)) {
                alert("La cédula debe contener 7 u 8 dígitos.");
                return;
            }
        }
        if (isTelefono) {
            // Validation: Exactly 11 digits OR 13 if starts with +58 (e.g. +584141234567)
            if (!/^(\d{11}|\+58\d{10})$/.test(val)) {
                alert("El teléfono debe contener exactamente 11 dígitos, o 13 si inicia con +58.");
                return;
            }
        }
    }

    try {
        let res = { success: false };
        const idColName = tableName === 'profesor' ? 'id_profesor' : 'id_materia';
        if (window.eel) {
            res = await eel.update_table_field(tableName, idColName, rowId, col, val)();
        } else {
            res = { success: true };
        }

        if (res.success) {
            loadCrudTable(tableName);
        } else {
            alert("Error al actualizar: " + res.error);
        }
    } catch (err) {
        console.error(err);
        alert("Error de comunicación con el backend.");
    }
}

// Ventanas Modales dinámicas
function openAddModal(tableName) {
  activeCrudTable = tableName;
  const modal = document.getElementById('crud-modal');
  const title = document.getElementById('modal-title');
  const form = document.getElementById('crud-form');

  title.textContent = `Añadir a ${tableName.charAt(0).toUpperCase() + tableName.slice(1)}`;
  form.innerHTML = '';

  if (!activeCrudData) return;

  activeCrudData.columns.forEach(col => {
    if (col.startsWith('id_')) return;
    // El campo QR no se edita manualmente, lo asigna el escáner
    if (col === 'qr_content') return;
    const div = document.createElement('div');
    div.className = 'form-group';
    const label = document.createElement('label');
    label.className = 'form-label';
    label.textContent = friendlyNames[col] || col;
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-input';
    input.name = col;
    input.required = true;
    input.placeholder = `Ingresa ${friendlyNames[col] || col}`;
    div.appendChild(label);
    div.appendChild(input);
    form.appendChild(div);
  });

  // Campo QR oculto con valor vacío por defecto (será asignado por el escáner)
  const hiddenQr = document.createElement('input');
  hiddenQr.type = 'hidden';
  hiddenQr.name = 'qr_content';
  hiddenQr.value = '';
  form.appendChild(hiddenQr);

  modal.classList.remove('hidden');
}

function closeCrudModal() {
  document.getElementById('crud-modal').classList.add('hidden');
}

// Enviar datos del formulario
async function handleCrudSubmit(e) {
  e.preventDefault();
  const form = document.getElementById('crud-form');
  if (!form.reportValidity()) return;

  const formData = new FormData(form);
  const data = {};
  formData.forEach((value, key) => { data[key] = value; });

  try {
    let res = { success: false };
    if (window.eel) {
      res = await eel.add_table_row(activeCrudTable, data)();
    } else {
      res = { success: true };
    }

    if (res.success) {
      closeCrudModal();
      loadCrudTable(activeCrudTable);
      alert("Registro guardado con éxito.");
    } else {
      alert("Error al guardar: " + res.error);
    }
  } catch (err) {
    console.error(err);
    alert("Error de comunicación con el backend.");
  }
}

// Eliminar Fila con confirmación
async function deleteRow(tableName, id) {
  const confirmMsg = tableName === 'profesor'
    ? "¿Estás seguro de que deseas eliminar este profesor? Al hacerlo se borrarán todos sus horarios semanales asociados de forma permanente."
    : "¿Estás seguro de que deseas eliminar esta materia? Se eliminará del registro general.";

  if (!confirm(confirmMsg)) return;

  try {
    let res = { success: false };
    if (window.eel) {
      res = await eel.delete_table_row(tableName, id)();
    } else {
      res = { success: true };
    }

    if (res.success) {
      loadCrudTable(tableName);
      alert("Registro eliminado correctamente.");
    } else {
      alert("Error al eliminar: " + res.error);
    }
  } catch (err) {
    console.error(err);
    alert("Error al conectar con la base de datos.");
  }
}

// ==========================================================================
// 7. Lógica del Horario Semanal (Grilla Interactiva de 14x5)
// ==========================================================================

function renderScheduleGrid() {
  const tbody = document.querySelector('#schedule-grid tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  timeSlots.forEach((slot, index) => {
    const tr = document.createElement('tr');

    const tdTime = document.createElement('td');
    tdTime.className = 'time-label';
    tdTime.textContent = `${slot.start} - ${slot.end}`;
    tr.appendChild(tdTime);

    diasSemana.forEach((dia, dayIdx) => {
      const td = document.createElement('td');
      td.className = 'schedule-cell';
      td.setAttribute('data-day', dia);
      td.setAttribute('data-day-idx', dayIdx);
      td.setAttribute('data-slot-idx', index);
      td.setAttribute('data-start', slot.start);
      td.setAttribute('data-end', slot.end);
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });
}

function viewSchedule(idProfesor, nombreProfesor) {
  currentSelectedProfesor = {
    id_profesor: idProfesor,
    nombre: nombreProfesor
  };

  const menuBtn = document.getElementById('menu-btn-horario');
  if (menuBtn) menuBtn.removeAttribute('disabled');

  navigateView('horarios');
}

async function loadScheduleData(idProfesor) {
  const title = document.getElementById('schedule-title');
  const subtitle = document.getElementById('schedule-subtitle');

  if (title) title.textContent = `HORARIO SEMANAL - ${currentSelectedProfesor.nombre.toUpperCase()}`;
  if (subtitle) subtitle.textContent = `Configurando las asignaciones horarias para el profesor ID: ${idProfesor}`;

  document.querySelectorAll('.schedule-cell').forEach(cell => {
    cell.innerHTML = '';
    cell.classList.remove('selected-drag');
  });

  try {
    let assignments = [];
    if (window.eel) {
      assignments = await eel.get_schedule_data(idProfesor)();
    }

    assignments.forEach(asig => {
      const dia = asig.dia_semana;
      const slotIdx = timeSlots.findIndex(s => s.start === asig.hora_inicio && s.end === asig.hora_fin);
      if (slotIdx === -1) return;

      const cell = document.querySelector(`.schedule-cell[data-day="${dia}"][data-slot-idx="${slotIdx}"]`);
      if (cell) {
        cell.innerHTML = `
          <div class="schedule-block-assigned" data-horario-id="${asig.id_horario}" onclick="deleteScheduleBlock(event, ${asig.id_horario}, '${(asig.nb_materia || '').replace(/'/g, "\\'")}')">
            <span class="block-materia">${asig.nb_materia}</span>
            <span class="block-aula">${asig.num_aula || '-'}</span>
          </div>
        `;
      }
    });
  } catch (err) {
    console.error("Error al cargar horarios:", err);
  }
}

async function deleteScheduleBlock(event, idHorario, materiaNombre) {
  event.stopPropagation();
  if (!confirm(`¿Deseas desvincular el horario asignado de '${materiaNombre}'?`)) return;

  try {
    let res = { success: false };
    if (window.eel) {
      res = await eel.delete_schedule_slot(idHorario)();
    } else {
      res = { success: true };
    }

    if (res.success) {
      loadScheduleData(currentSelectedProfesor.id_profesor);
    } else {
      alert("Error al borrar horario.");
    }
  } catch (err) {
    console.error(err);
  }
}

// Arrastrar y Seleccionar Celdas Verticalmente
function initDragSelection() {
  const table = document.getElementById('schedule-grid');
  if (!table) return;

  table.addEventListener('mousedown', (e) => {
    const cell = e.target.closest('.schedule-cell');
    if (!cell) return;
    if (e.target.closest('.schedule-block-assigned')) return;

    isDraggingSchedule = true;
    dragCol = parseInt(cell.getAttribute('data-day-idx'));
    dragStartRow = parseInt(cell.getAttribute('data-slot-idx'));
    dragEndRow = dragStartRow;

    clearDragHighlight();
    cell.classList.add('selected-drag');
  });

  table.addEventListener('mouseover', (e) => {
    if (!isDraggingSchedule) return;
    const cell = e.target.closest('.schedule-cell');
    if (!cell) return;

    const currentCol = parseInt(cell.getAttribute('data-day-idx'));
    const currentRow = parseInt(cell.getAttribute('data-slot-idx'));

    if (currentCol !== dragCol) return;

    dragEndRow = currentRow;
    highlightDraggedCells();
  });

  window.addEventListener('mouseup', () => {
    if (!isDraggingSchedule) return;
    isDraggingSchedule = false;
    openScheduleAssignmentModal();
  });
}

function clearDragHighlight() {
  document.querySelectorAll('.schedule-cell').forEach(cell => {
    cell.classList.remove('selected-drag');
  });
}

function highlightDraggedCells() {
  clearDragHighlight();
  const minRow = Math.min(dragStartRow, dragEndRow);
  const maxRow = Math.max(dragStartRow, dragEndRow);

  for (let r = minRow; r <= maxRow; r++) {
    const cell = document.querySelector(`.schedule-cell[data-day-idx="${dragCol}"][data-slot-idx="${r}"]`);
    if (cell && !cell.querySelector('.schedule-block-assigned')) {
      cell.classList.add('selected-drag');
    }
  }
}

// ==========================================================================
// 8. Modal de Asignación de Horario
// ==========================================================================
async function openScheduleAssignmentModal() {
  const selectedCells = document.querySelectorAll('.schedule-cell.selected-drag');
  if (selectedCells.length === 0) return;

  const dia = diasSemana[dragCol];
  const minRow = Math.min(dragStartRow, dragEndRow);
  const maxRow = Math.max(dragStartRow, dragEndRow);

  const startHour = timeSlots[minRow].start;
  const endHour = timeSlots[maxRow].end;

  document.getElementById('schedule-details-text').textContent = `Día: ${dia} | Horario: ${startHour} - ${endHour}`;

  const inputMateria = document.getElementById('schedule-materia-input');
  const listContainer = document.getElementById('autocomplete-list-schedule');
  inputMateria.value = '';
  if (listContainer) listContainer.innerHTML = '';

  try {
    let materias = [];
    if (window.eel) {
      const response = await eel.get_table_data('materia')();
      materias = response.rows || [];
    } else {
      materias = [];
    }

    window.currentMateriasList = materias;

    if (materias.length === 0) {
      inputMateria.placeholder = 'No hay materias registradas.';
      inputMateria.disabled = true;
    } else {
      inputMateria.placeholder = 'Buscar y seleccionar Materia...';
      inputMateria.disabled = false;
      const materiaNames = materias.map(m => m.nb_materia);
      setupAutocomplete('schedule-materia-input', 'autocomplete-list-schedule', materiaNames);
    }
  } catch (err) {
    console.error(err);
    inputMateria.placeholder = 'Error al cargar materias.';
    inputMateria.disabled = true;
  }

  document.getElementById('schedule-aula-input').value = '';
  document.getElementById('schedule-modal').classList.remove('hidden');
}

function closeScheduleModal() {
  document.getElementById('schedule-modal').classList.add('hidden');
  clearDragHighlight();
}

// Guardar Asignación de Horario
async function handleScheduleSubmit(e) {
  e.preventDefault();
  const inputMateria = document.getElementById('schedule-materia-input');
  const aulaInput = document.getElementById('schedule-aula-input');

  const selectedMateriaName = inputMateria.value.trim();
  const foundMateria = (window.currentMateriasList || []).find(m => m.nb_materia === selectedMateriaName);

  if (!foundMateria || !aulaInput.value) {
    alert("Por favor, busca y selecciona una materia válida de la lista e ingresa el aula.");
    return;
  }

  const aulaVal = aulaInput.value.trim();
  if (!/^[1-9][0-4][1-4]$/.test(aulaVal)) {
    alert("El número de aula es inválido. Debe tener exactamente 3 dígitos:\n- Módulo: 1 al 9\n- Piso: 0 al 4 (0 es PB)\n- Aula: 1 al 4\nEjemplo: 101");
    return;
  }

  const minRow = Math.min(dragStartRow, dragEndRow);
  const maxRow = Math.max(dragStartRow, dragEndRow);
  const dia = diasSemana[dragCol];

  const slotsToSave = [];
  for (let r = minRow; r <= maxRow; r++) {
    slotsToSave.push({
      hora_inicio: timeSlots[r].start,
      hora_fin: timeSlots[r].end
    });
  }

  const payload = {
    id_profesor: currentSelectedProfesor.id_profesor,
    id_materia: foundMateria.id_materia,
    num_aula: aulaInput.value.trim(),
    dia_semana: dia,
    slots: slotsToSave
  };

  try {
    let res = { success: false };
    if (window.eel) {
      res = await eel.save_schedule_slot(payload)();
    } else {
      res = { success: true };
    }

    if (res.success) {
      closeScheduleModal();
      loadScheduleData(currentSelectedProfesor.id_profesor);
    } else {
      alert("Error al guardar horario: " + (res.error || "Desconocido"));
    }
  } catch (err) {
    console.error(err);
    alert("Error de comunicación con el backend.");
  }
}

// ==========================================================================
// 9. Módulo de Escáner de Código QR con Cámara
// ==========================================================================
let qrStream = null;
let qrAnimFrame = null;
let qrCurrentProfesorId = null;
let qrCurrentProfesorNombre = '';
let qrDetectedData = null;
let qrScanning = false;

/**
 * Abre el modal del escáner de QR e inicia la cámara.
 * @param {number} idProfesor
 * @param {string} nombreProfesor
 * @param {boolean} tieneQr - true si ya existe un QR asignado
 */
async function openQrScannerModal(idProfesor, nombreProfesor, tieneQr) {
  qrCurrentProfesorId = idProfesor;
  qrCurrentProfesorNombre = nombreProfesor;
  qrDetectedData = null;

  // Actualizar textos del modal
  const titleEl = document.getElementById('qr-modal-title');
  const subtitleEl = document.getElementById('qr-profesor-name');
  if (titleEl) titleEl.textContent = tieneQr ? 'Reemplazar Código QR' : 'Agregar Código QR';
  if (subtitleEl) subtitleEl.textContent = `Docente: ${nombreProfesor}`;

  // Resetear UI al estado inicial
  _qrResetUI();

  // Mostrar modal
  document.getElementById('qr-scanner-modal').classList.remove('hidden');

  // Iniciar cámara
  await _qrStartCamera();
}

/** Inicia el stream de cámara y el loop de detección */
async function _qrStartCamera() {
  const video = document.getElementById('qr-video');
  const statusText = document.getElementById('qr-status-text');
  const statusDot = document.getElementById('qr-status-dot');

  try {
    // Detener stream previo si existe
    _qrStopCamera();

    const constraints = {
      video: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 },
        advanced: [{ focusMode: 'continuous' }]
      }
    };

    qrStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = qrStream;

    video.onloadedmetadata = () => {
      video.play();
      if (statusText) statusText.textContent = 'Cámara activa — Apunta al código QR';
      if (statusDot) statusDot.className = 'qr-status-dot scanning';
      qrScanning = true;
      _qrScanLoop();
    };
  } catch (err) {
    console.error('Error al acceder a la cámara:', err);
    if (statusText) statusText.textContent = `No se pudo acceder a la cámara: ${err.message}`;
    if (statusDot) statusDot.className = 'qr-status-dot error';
  }
}

/** Loop principal de detección QR — throttled a ~15fps con resolución reducida */
function _qrScanLoop() {
  if (!qrScanning) return;

  const video = document.getElementById('qr-video');
  const canvas = document.getElementById('qr-canvas');
  if (!video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
    qrAnimFrame = requestAnimationFrame(_qrScanLoop);
    return;
  }

  // Escanear a 640x480 para mantener el detalle necesario para QRs pequeños o densos
  const SCAN_W = 640;
  const SCAN_H = 480;
  canvas.width = SCAN_W;
  canvas.height = SCAN_H;
  // willReadFrequently evita que el navegador mueva el canvas a la GPU
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(video, 0, 0, SCAN_W, SCAN_H);

  const imageData = ctx.getImageData(0, 0, SCAN_W, SCAN_H);

  // Decodificar con jsQR
  if (typeof jsQR !== 'undefined') {
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: 'dontInvert'
    });

    if (code && code.data) {
      qrScanning = false;
      qrDetectedData = code.data;
      _qrOnDetected(code.data);
      return;
    }
  }

  // Frecuencia nativa (~60fps) para máxima velocidad de lectura
  qrAnimFrame = requestAnimationFrame(_qrScanLoop);
}

/** Maneja la detección exitosa de un QR */
function _qrOnDetected(data) {
  const statusText = document.getElementById('qr-status-text');
  const statusDot = document.getElementById('qr-status-dot');
  const resultBox = document.getElementById('qr-result-box');
  const resultValue = document.getElementById('qr-result-value');
  const rescanBtn = document.getElementById('qr-rescan-btn');
  const confirmBtn = document.getElementById('qr-confirm-btn');
  const scanLine = document.getElementById('qr-scan-line');

  // Pausar video
  const video = document.getElementById('qr-video');
  if (video) video.pause();

  // Actualizar estado
  if (statusText) statusText.textContent = 'Código QR detectado correctamente';
  if (statusDot) statusDot.className = 'qr-status-dot detected';
  if (scanLine) scanLine.style.animationPlayState = 'paused';

  // Mostrar resultado
  if (resultValue) resultValue.textContent = data;
  if (resultBox) resultBox.classList.remove('hidden');

  // Mostrar botones de acción
  if (rescanBtn) rescanBtn.classList.remove('hidden');
  if (confirmBtn) confirmBtn.classList.remove('hidden');
}

/** Reinicia el escáner para escanear de nuevo */
function restartQrScan() {
  qrDetectedData = null;
  _qrResetUI();
  const video = document.getElementById('qr-video');
  if (video && qrStream) {
    video.play();
    qrScanning = true;
    _qrScanLoop();
    const statusText = document.getElementById('qr-status-text');
    const statusDot = document.getElementById('qr-status-dot');
    if (statusText) statusText.textContent = 'Cámara activa - Apunta al código QR';
    if (statusDot) statusDot.className = 'qr-status-dot scanning';
  } else {
    _qrStartCamera();
  }
}

/** Guarda el QR detectado en la base de datos */
async function confirmQrSave() {
  if (!qrDetectedData || !qrCurrentProfesorId) return;

  const confirmBtn = document.getElementById('qr-confirm-btn');
  if (confirmBtn) { confirmBtn.textContent = 'Guardando...'; confirmBtn.disabled = true; }

  try {
    let res = { success: false };
    if (window.eel) {
      res = await eel.update_qr_content(qrCurrentProfesorId, qrDetectedData)();
    } else {
      res = { success: true };
    }

    if (res.success) {
      closeQrScannerModal();
      loadCrudTable('profesor');
      _showQrToast(`QR guardado correctamente para ${qrCurrentProfesorNombre}`);
    } else {
      alert('Error al guardar el QR: ' + (res.error || 'Desconocido'));
      if (confirmBtn) { confirmBtn.textContent = 'Guardar QR'; confirmBtn.disabled = false; }
    }
  } catch (err) {
    console.error(err);
    alert('Error de comunicación con el backend.');
    if (confirmBtn) { confirmBtn.textContent = 'Guardar QR'; confirmBtn.disabled = false; }
  }
}

/** Cierra el modal y detiene la cámara */
function closeQrScannerModal() {
  qrScanning = false;
  _qrStopCamera();
  document.getElementById('qr-scanner-modal').classList.add('hidden');
  _qrResetUI();
}

/** Detiene el stream de cámara y cancela el animation frame */
function _qrStopCamera() {
  qrScanning = false;
  if (qrAnimFrame) { cancelAnimationFrame(qrAnimFrame); qrAnimFrame = null; }
  if (qrStream) {
    qrStream.getTracks().forEach(track => track.stop());
    qrStream = null;
  }
  const video = document.getElementById('qr-video');
  if (video) video.srcObject = null;
}

/** Resetea la UI del modal al estado inicial */
function _qrResetUI() {
  const resultBox = document.getElementById('qr-result-box');
  const rescanBtn = document.getElementById('qr-rescan-btn');
  const confirmBtn = document.getElementById('qr-confirm-btn');
  const statusText = document.getElementById('qr-status-text');
  const statusDot = document.getElementById('qr-status-dot');
  const scanLine = document.getElementById('qr-scan-line');

  if (resultBox) resultBox.classList.add('hidden');
  if (rescanBtn) rescanBtn.classList.add('hidden');
  if (confirmBtn) { confirmBtn.classList.add('hidden'); confirmBtn.textContent = 'Guardar QR'; confirmBtn.disabled = false; }
  if (statusText) statusText.textContent = 'Iniciando cámara... Apunta al código QR';
  if (statusDot) statusDot.className = 'qr-status-dot scanning';
  if (scanLine) scanLine.style.animationPlayState = 'running';
}

/** Muestra un toast de notificación temporal */
function _showQrToast(message) {
  const existing = document.getElementById('qr-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'qr-toast';
  toast.className = 'qr-toast';
  toast.textContent = message;
  document.body.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('visible'));

  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// ==========================================================================
// 10. Módulo de Escáner de Asistencias en Landing Page
// ==========================================================================
let landingQrStream = null;
let landingQrAnimFrame = null;
let landingQrScanning = false;
let landingResultTimeout = null;

async function startLandingQrScanner() {
  landingQrScanning = false;
  _stopLandingQrStream();

  const video = document.getElementById('landing-qr-video');
  const statusText = document.getElementById('landing-status-text');
  const statusDot = document.getElementById('landing-status-dot');

  if (!video) return;

  // Cargar feed de asistencia en la landing
  loadRecentFeed();

  try {
    const constraints = {
      video: {
        facingMode: 'environment',
        width: { ideal: 1280 },
        height: { ideal: 720 },
        advanced: [{ focusMode: 'continuous' }]
      }
    };

    landingQrStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = landingQrStream;

    video.onloadedmetadata = () => {
      video.play();
      if (statusText) statusText.textContent = 'Lector activo — Apunta tu código QR';
      if (statusDot) statusDot.className = 'qr-status-dot scanning';
      landingQrScanning = true;
      landingQrScanLoop();
    };
  } catch (err) {
    console.error('Error al acceder a la cámara de landing:', err);
    if (statusText) statusText.textContent = `❌ No se pudo activar el lector: ${err.message}`;
    if (statusDot) statusDot.className = 'qr-status-dot error';
  }
}

function stopLandingQrScanner() {
  landingQrScanning = false;
  _stopLandingQrStream();
}

function _stopLandingQrStream() {
  if (landingQrAnimFrame) {
    cancelAnimationFrame(landingQrAnimFrame);
    landingQrAnimFrame = null;
  }
  if (landingQrStream) {
    landingQrStream.getTracks().forEach(track => track.stop());
    landingQrStream = null;
  }
  const video = document.getElementById('landing-qr-video');
  if (video) video.srcObject = null;
}

function landingQrScanLoop() {
  if (!landingQrScanning) return;

  const video = document.getElementById('landing-qr-video');
  const canvas = document.getElementById('landing-qr-canvas');

  if (!video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
    landingQrAnimFrame = requestAnimationFrame(landingQrScanLoop);
    return;
  }

  // Escanear a 640x480 para asegurar que QRs densos o pequeños se puedan leer bien
  const SCAN_W = 640;
  const SCAN_H = 480;
  canvas.width = SCAN_W;
  canvas.height = SCAN_H;
  // willReadFrequently optimiza las lecturas repetidas de píxeles
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(video, 0, 0, SCAN_W, SCAN_H);

  const imageData = ctx.getImageData(0, 0, SCAN_W, SCAN_H);

  if (typeof jsQR !== 'undefined') {
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: 'dontInvert'
    });

    if (code && code.data) {
      landingQrScanning = false;
      handleLandingQrResult(code.data);
      return;
    }
  }

  // Frecuencia nativa (~60fps)
  landingQrAnimFrame = requestAnimationFrame(landingQrScanLoop);
}

async function handleLandingQrResult(qrData) {
  const statusText = document.getElementById('landing-status-text');
  const statusDot = document.getElementById('landing-status-dot');
  const resultBox = document.getElementById('landing-scan-result');

  if (statusText) statusText.textContent = 'Procesando código QR...';
  if (statusDot) statusDot.className = 'qr-status-dot scanning';

  try {
    let res = { success: false, error: 'Sin conexión' };
    if (window.eel) {
      res = await eel.register_attendance_by_qr(qrData)();
    } else {
      res = { success: false, error: "Servidor desconectado" };
    }

    if (res.success) {
      // Mostrar alerta de ÉXITO
      if (statusText) statusText.textContent = '✅ ¡Lectura exitosa!';
      if (statusDot) statusDot.className = 'qr-status-dot detected';

      const isEntrada = res.tipo === 'entrada';
      const actionTitle = isEntrada ? '🟢 ENTRADA REGISTRADA' : '🔵 SALIDA REGISTRADA';
      const actionColorClass = isEntrada ? 'success' : 'info';

      resultBox.className = `scan-result-card ${actionColorClass}`;
      resultBox.innerHTML = `
        <div class="result-header">
          <span class="result-icon">${isEntrada ? '📥' : '📤'}</span>
          <span class="result-title">${actionTitle}</span>
        </div>
        <div class="result-body">
          <span class="result-prof-name">${res.profesor}</span>
          <span class="result-meta">Hora de registro: <strong>${res.hora}</strong></span>
        </div>
      `;
      resultBox.classList.remove('hidden');

      // Recargar feed
      loadRecentFeed();
    } else {
      // Mostrar alerta de ERROR
      if (statusText) statusText.textContent = 'Fallo en la lectura';
      if (statusDot) statusDot.className = 'qr-status-dot error';

      resultBox.className = 'scan-result-card error';
      resultBox.innerHTML = `
        <div class="result-header">
          <span class="result-icon">⚠️</span>
          <span class="result-title">ERROR DE LECTURA</span>
        </div>
        <div class="result-body">
          <span class="result-meta">${res.error}</span>
        </div>
      `;
      resultBox.classList.remove('hidden');
    }

    // Reproducir un sonido de beep sutil si es posible
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      oscillator.frequency.setValueAtTime(res.success ? 880 : 440, audioCtx.currentTime); // Beep high for success, low for error
      gainNode.gain.setValueAtTime(0.08, audioCtx.currentTime);
      oscillator.start();
      oscillator.stop(audioCtx.currentTime + (res.success ? 0.15 : 0.3));
    } catch (e) { }

  } catch (err) {
    console.error('Error al procesar asistencia:', err);
  }

  // Limpiar temporizadores anteriores si existen
  if (landingResultTimeout) clearTimeout(landingResultTimeout);

  // Ocultar la tarjeta de resultado en 5 segundos
  landingResultTimeout = setTimeout(() => {
    resultBox.classList.add('hidden');
  }, 5000);

  // Reactivar escáner tras 3 segundos
  setTimeout(() => {
    const isLandingVisible = document.getElementById('landing-layout') && !document.getElementById('landing-layout').classList.contains('hidden');
    if (isLandingVisible) {
      landingQrScanning = true;
      if (statusText) statusText.textContent = 'Lector activo — Apunta tu código QR';
      if (statusDot) statusDot.className = 'qr-status-dot scanning';
      landingQrScanLoop();
    }
  }, 3000);
}

async function loadRecentFeed() {
  const container = document.getElementById('landing-recent-feed');
  if (!container) return;

  try {
    let history = [];
    if (window.eel) {
      history = await eel.get_attendance_history()();
    } else {
      history = [];
    }

    // Obtener fecha actual YYYY-MM-DD en zona horaria local
    const now = new Date();
    const offset = now.getTimezoneOffset();
    const localDate = new Date(now.getTime() - (offset * 60 * 1000));
    const todayStr = localDate.toISOString().split('T')[0];

    // Filtrar para hoy y ordenar por más reciente
    const todayLogs = history.filter(log => log.fecha_asistencia === todayStr).slice(0, 5);

    container.innerHTML = '';
    if (todayLogs.length === 0) {
      container.innerHTML = '<div class="feed-empty-state">No se registran asistencias hoy todavía.</div>';
      return;
    }

    todayLogs.forEach(log => {
      const profName = `${log.nb_profesor} ${log.ap_profesor}`.trim();
      const hasExit = log.hora_salida && log.hora_salida.trim() !== '';

      const item = document.createElement('div');
      item.className = 'feed-item';

      const timeDisplay = hasExit
        ? `<span class="feed-badge exit">Salida ${log.hora_salida}</span>`
        : `<span class="feed-badge entry">Entrada ${log.hora_entrada}</span>`;

      item.innerHTML = `
        <div class="feed-item-header">
          <span class="feed-prof-name">${profName}</span>
          ${timeDisplay}
        </div>
      `;
      container.appendChild(item);
    });
  } catch (err) {
    console.error("Error al cargar feed reciente:", err);
  }
}

function parseLocalDate(dateStr) {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day);
}

function getSpanishWeekday(date) {
  const dayNames = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  return dayNames[date.getDay()];
}

async function loadAuditTable() {
  const tbody = document.querySelector('#audit-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: var(--text-muted);">Cargando historial de asistencias...</td></tr>';

  try {
    if ((!rawDashboardData || rawDashboardData.length === 0) && window.eel) {
      rawDashboardData = await eel.get_dashboard_data()();
    }
    let history = [];
    if (window.eel) {
      history = await eel.get_attendance_history()();
    } else {
      history = [];
    }

    auditFullHistory = history || [];  // Guardar copia completa para filtros

    // Inicializar el filtro de fecha con el día actual si no hay ningún filtro de fecha o mes activo
    const dateInput = document.getElementById('audit-filter-date');
    const monthInput = document.getElementById('audit-filter-month');
    if (dateInput && !dateInput.value && monthInput && !monthInput.value) {
      const now = new Date();
      const offset = now.getTimezoneOffset();
      const localDate = new Date(now.getTime() - (offset * 60 * 1000));
      const todayStr = localDate.toISOString().split('T')[0];
      dateInput.value = todayStr;
    }

    applyAuditDateFilter();
  } catch (err) {
    console.error("Error cargando tabla de auditoria:", err);
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #ef4444;">Error al conectar con la base de datos.</td></tr>';
  }
}

function renderAuditRows(history) {
  const tbody = document.querySelector('#audit-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  if (!history || history.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: var(--text-muted);">No hay asistencias que coincidan con el filtro.</td></tr>';
    return;
  }

  history.forEach(log => {
    const tr = document.createElement('tr');
    const profName = `${log.nb_profesor} ${log.ap_profesor}`.trim();
    const hasExit = log.hora_salida && log.hora_salida.trim() !== '';
    const hasEntry = log.hora_entrada && log.hora_entrada.trim() !== '';

    const profData = rawDashboardData.find(p => p.id_profesor === log.id_profesor);
    const scheduleSlots = profData ? profData.schedule_slots : [];

    const logDate = new Date(log.fecha_asistencia + 'T00:00:00');
    const todayStr = new Date().toISOString().split('T')[0];
    const isToday = log.fecha_asistencia === todayStr;
    const evalTimeStr = isToday ? null : '23:59:59';

    const statusInfo = getProfessorStatus(log.hora_entrada, log.hora_salida, scheduleSlots, logDate, evalTimeStr);
    let label = statusInfo.label;
    if (statusInfo.code === "ActivoEnClase" || statusInfo.code === "ActivoHoraLibre") {
      label = "Activo";
    }
    const estadoBadge = `<span style="${statusInfo.style}">${label}</span>`;

    tr.innerHTML = `
      <td style="font-weight:600;">${profName}</td>
      <td>${log.fecha_asistencia}</td>
      <td style="color:${hasEntry ? '#16a34a' : '#64748b'}; font-weight:600;">${hasEntry ? log.hora_entrada : '—'}</td>
      <td style="color:${hasExit ? '#2563eb' : '#64748b'}; font-weight:600;">${hasExit ? log.hora_salida : '—'}</td>
      <td>${estadoBadge}</td>
    `;
    tbody.appendChild(tr);
  });
}

function applyAuditDateFilter() {
  const dateInput = document.getElementById('audit-filter-date');
  const monthInput = document.getElementById('audit-filter-month');
  const profesorInput = document.getElementById('audit-filter-profesor');

  const selectedDate = dateInput ? dateInput.value : '';
  const selectedMonth = monthInput ? monthInput.value : '';
  const searchProfesor = profesorInput ? profesorInput.value.trim().toLowerCase() : '';

  let filtered = [];

  // Determinar el rango de fechas para el cual calcularemos inasistencias
  let targetDates = [];
  if (selectedDate) {
    targetDates = [selectedDate];
  } else if (selectedMonth) {
    const [year, month] = selectedMonth.split('-').map(Number);
    let currentDate = new Date(year, month - 1, 1);
    const lastDayOfMonth = new Date(year, month, 0);
    const today = new Date();
    const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    
    let endDate = lastDayOfMonth;
    if (lastDayOfMonth > todayMidnight) {
      endDate = todayMidnight; // No calcular inasistencias futuras
    }
    
    while (currentDate <= endDate) {
      const y = currentDate.getFullYear();
      const m = String(currentDate.getMonth() + 1).padStart(2, '0');
      const d = String(currentDate.getDate()).padStart(2, '0');
      targetDates.push(`${y}-${m}-${d}`);
      currentDate.setDate(currentDate.getDate() + 1);
    }
  }

  // 1. Obtener registros reales de asistencia que coincidan con la fecha o el mes
  let actualRecords = [...auditFullHistory];
  
  if (selectedDate) {
    actualRecords = actualRecords.filter(log => log.fecha_asistencia === selectedDate);
  } else if (selectedMonth) {
    actualRecords = actualRecords.filter(log => log.fecha_asistencia.startsWith(selectedMonth));
  }

  // Filtrar por nombre del profesor
  if (searchProfesor) {
    actualRecords = actualRecords.filter(log => {
      const fullName = `${log.nb_profesor} ${log.ap_profesor}`.toLowerCase();
      return fullName.includes(searchProfesor);
    });
  }

  // 2. Generar registros sintéticos de "Inasistente/Ausente" para los profesores programados que no asistieron
  let generatedAbsences = [];
  const todayStr2 = new Date().toISOString().split('T')[0];
  const nowMinutes = new Date().getHours() * 60 + new Date().getMinutes();

  if (targetDates.length > 0 && rawDashboardData && rawDashboardData.length > 0) {
    targetDates.forEach(dateStr => {
      const localDate = parseLocalDate(dateStr);
      const weekdayName = getSpanishWeekday(localDate);
      const isToday = dateStr === todayStr2;

      rawDashboardData.forEach(prof => {
        // Obtener slots del profesor para este día de la semana
        const slotsOnThisDay = (prof.schedule_slots || []).filter(slot => slot.dia === weekdayName);
        if (slotsOnThisDay.length === 0) return;

        // Para HOY: solo marcar como ausente si ya terminó la ÚLTIMA clase del día
        if (isToday) {
          const lastEndMin = Math.max(...slotsOnThisDay.map(s => timeToMinutes(s.hora_fin)));
          if (nowMinutes < lastEndMin) return; // Aún hay clases en curso o por comenzar → no ausente todavía
        }

        // ¿Registró asistencia este día?
        const checkedIn = auditFullHistory.some(log => log.id_profesor === prof.id_profesor && log.fecha_asistencia === dateStr);
        if (!checkedIn) {
          const fullName = prof.nombre.toLowerCase();
          if (!searchProfesor || fullName.includes(searchProfesor)) {
            const parts = prof.nombre.split(' ');
            const nb_profesor = parts[0] || '';
            const ap_profesor = parts.slice(1).join(' ') || '';

            generatedAbsences.push({
              id_asistencia: null,
              fecha_asistencia: dateStr,
              hora_entrada: "",
              hora_salida: "",
              id_profesor: prof.id_profesor,
              nb_profesor: nb_profesor,
              ap_profesor: ap_profesor,
              estado: "Ausente"
            });
          }
        }
      });
    });
  }

  filtered = [...actualRecords, ...generatedAbsences];

  // Ordenar por fecha desc, luego registros reales primero (tienen hora entrada), y luego inasistentes
  filtered.sort((a, b) => {
    if (a.fecha_asistencia !== b.fecha_asistencia) {
      return b.fecha_asistencia.localeCompare(a.fecha_asistencia);
    }
    const timeA = a.hora_entrada || '';
    const timeB = b.hora_entrada || '';
    if (timeA && timeB) {
      return timeB.localeCompare(timeA);
    }
    return timeA ? -1 : (timeB ? 1 : 0);
  });

  // Guardar en variable global para exportación
  window.auditFilteredHistory = filtered;

  renderAuditRows(filtered);
}

function clearAuditDateFilter() {
  const dateInput = document.getElementById('audit-filter-date');
  const monthInput = document.getElementById('audit-filter-month');
  const profesorInput = document.getElementById('audit-filter-profesor');
  if (dateInput) dateInput.value = '';
  if (monthInput) monthInput.value = '';
  if (profesorInput) profesorInput.value = '';
  
  applyAuditDateFilter();
}

async function exportAuditToPDF() {
  try {
    const { jsPDF } = window.jspdf;
    if (!jsPDF) {
      alert("La biblioteca PDF no se ha cargado correctamente.");
      return;
    }

    const history = window.auditFilteredHistory || [];

    if (!history || history.length === 0) {
      alert("No hay registros de asistencia para exportar con los filtros actuales.");
      return;
    }

    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.setTextColor(37, 99, 235);
    doc.text("HISTORIAL DE ASISTENCIA - AUDITORÍA", 14, 20);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(100, 116, 139);
    const nowStr = new Date().toLocaleString();
    
    // Obtener información de filtros activos
    const dateInput = document.getElementById('audit-filter-date');
    const monthInput = document.getElementById('audit-filter-month');
    const profesorInput = document.getElementById('audit-filter-profesor');
    const selectedDate = dateInput ? dateInput.value : '';
    const selectedMonth = monthInput ? monthInput.value : '';
    const searchProfesor = profesorInput ? profesorInput.value.trim() : '';

    let filterText = '';
    if (selectedDate || selectedMonth || searchProfesor) {
      const parts = [];
      if (selectedDate) parts.push(`Fecha: ${selectedDate}`);
      if (selectedMonth) parts.push(`Mes: ${selectedMonth}`);
      if (searchProfesor) parts.push(`Profesor: "${searchProfesor}"`);
      filterText = ` | Filtros: ${parts.join(', ')}`;
    }
    doc.text(`Generado el: ${nowStr} | Total registros: ${history.length}${filterText}`, 14, 27);

    doc.setDrawColor(226, 232, 240);
    doc.line(14, 32, 196, 32);

    const tableBody = history.map(log => {
      const profName = `${log.nb_profesor} ${log.ap_profesor}`.trim();
      const hasExit = log.hora_salida && log.hora_salida.trim() !== '';
      const hasEntry = log.hora_entrada && log.hora_entrada.trim() !== '';

      const profData = rawDashboardData.find(p => p.id_profesor === log.id_profesor);
      const scheduleSlots = profData ? profData.schedule_slots : [];

      const logDate = new Date(log.fecha_asistencia + 'T00:00:00');
      const todayStr = new Date().toISOString().split('T')[0];
      const isToday = log.fecha_asistencia === todayStr;
      const evalTimeStr = isToday ? null : '23:59:59';

      const statusInfo = getProfessorStatus(log.hora_entrada, log.hora_salida, scheduleSlots, logDate, evalTimeStr);
      let label = statusInfo.label;
      if (statusInfo.code === "ActivoEnClase" || statusInfo.code === "ActivoHoraLibre") {
        label = "Activo";
      }

      return [
        profName,
        log.fecha_asistencia,
        hasEntry ? log.hora_entrada : '—',
        hasExit ? log.hora_salida : '—',
        label
      ];
    });

    doc.autoTable({
      startY: 38,
      head: [['Profesor', 'Fecha', 'Hora Entrada', 'Hora Salida', 'Estado']],
      body: tableBody,
      headStyles: { fillColor: [37, 99, 235], textColor: [255, 255, 255], fontStyle: 'bold', fontSize: 10 },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      styles: { font: "helvetica", fontSize: 9, cellPadding: 4 },
      margin: { top: 38, left: 14, right: 14 }
    });

    const filename = `auditoria-asistencia-${new Date().toISOString().split('T')[0]}.pdf`;
    if (window.eel && typeof eel.save_pdf_file === 'function') {
      const pdfBase64 = doc.output('datauristring');
      const base64Data = pdfBase64.split(',')[1];

      const res = await eel.save_pdf_file(base64Data, filename)();
      if (res && res.success) {
        if (typeof _showQrToast === 'function') {
          _showQrToast("Reporte PDF guardado exitosamente en Descargas.", "success");
        }
        alert(`PDF Guardado Exitosamente!\n\nSe ha guardado en tu carpeta de Descargas:\n${res.path}`);
      } else {
        alert("Error al guardar el PDF en el sistema: " + (res ? res.error : "Error desconocido"));
      }
    } else {
      doc.save(filename);
    }
  } catch (err) {
    console.error("Error al exportar PDF:", err);
    alert("Hubo un error al generar el archivo PDF.");
  }
}
