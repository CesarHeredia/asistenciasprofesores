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
      if (currentMin >= start && currentMin <= end) {
        return `${s.materia} en ${s.aula}`;
      }
    }
  }
  return "Hora libre";
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
  "facultad": "Facultad",
  "departamento": "Departamento",
  "edificio": "Edificio"
};

// Mapa de parciales HTML
const viewPartials = {
  'dashboard': 'dashboard/dashboard.html',
  'database-profesores': 'dashboard/profesores.html',
  'database-materias': 'dashboard/materias.html'
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
  navigateView('dashboard');

  if (window.eel) {
    console.log("Eel cargado y listo.");
  } else {
    console.warn("Eel no está disponible. Ejecutando con datos mock.");
  }
});

async function loadModals() {
  try {
    const resp = await fetch('dashboard/modals.html');
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
        alert("Por favor, selecciona un profesor en 'Gestionar Profesores' y haz clic en su botón '📅 Horario' para configurar su grilla.");
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
    loadDashboard();
  } else if (viewName === 'database-profesores') {
    loadCrudTable('profesor');
  } else if (viewName === 'database-materias') {
    loadCrudTable('materia');
  } else if (viewName === 'horarios' && currentSelectedProfesor) {
    renderHorarioView();
  }
}

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
      rawDashboardData = [
        {id_profesor: 1, nombre: "Dr. Carlos Rodríguez", materia: "Algoritmos Avanzados", aula: "101-B", facultad: "Ingeniería", avatar: "🧔🏽", schedule_slots: []},
        {id_profesor: 2, nombre: "Dra. Ana Pérez", materia: "Introducción a la Física", aula: "205", facultad: "Ciencias Exactas", avatar: "👩🏻", schedule_slots: []},
        {id_profesor: 3, nombre: "Lic. Sofía Martínez", materia: "Historia del Arte", aula: "310", facultad: "Humanidades", avatar: "👩🏽", schedule_slots: []},
        {id_profesor: 4, nombre: "Ing. David Chen", materia: "Programación de Sistemas", aula: "G-01", facultad: "Ingeniería", avatar: "👨🏻", schedule_slots: []}
      ];
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
          if (currentMin >= start && currentMin <= end) {
            activeSlot = s;
            break;
          }
        }
      }
    }

    const card = document.createElement('div');
    card.className = 'profesor-card';
    
    let detailsHtml = '';
    if (activeSlot) {
      // Si está impartiendo clase en tiempo real, mostrar esa materia y aula (1 sola)
      detailsHtml = `
        <div class="detail-row">
          <span class="detail-label">Materia:</span>
          <span class="detail-value" style="font-weight: 600; color: var(--primary, #2563eb);">${activeSlot.materia}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Aula:</span>
          <span class="detail-value" style="font-weight: 600; color: var(--primary, #2563eb);">${activeSlot.aula}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Facultad:</span>
          <span class="detail-value">${p.facultad || 'Sin asignar'}</span>
        </div>
        <div class="detail-row" style="margin-top: 8px;">
          <span class="detail-label">Estado:</span>
          <span class="detail-value" style="font-weight: 700; color: #16a34a; background: #f0fdf4; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #bbf7d0;">En Clase</span>
        </div>
      `;
    } else {
      // Si no tiene clase en este momento, no aparece materia ni aula, simplemente "Hora Libre"
      detailsHtml = `
        <div class="detail-row">
          <span class="detail-label">Facultad:</span>
          <span class="detail-value">${p.facultad || 'Sin asignar'}</span>
        </div>
        <div class="detail-row" style="margin-top: 10px;">
          <span class="detail-label">Estado:</span>
          <span class="detail-value" style="font-weight: 700; color: #ef4444; background: #fef2f2; padding: 4px 10px; border-radius: 6px; font-size: 13px; border: 1px solid #fecaca;">Hora Libre</span>
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
function populateFilterDropdowns(data) {
  const selMateria = document.getElementById('filter-materia');
  const selFacultad = document.getElementById('filter-facultad');
  const selEdificio = document.getElementById('filter-edificio');

  const materias = new Set();
  const facultades = new Set();
  const edificios = new Set();

  data.forEach(p => {
    if (p.materia && p.materia !== "Sin Materia Asignada") {
      p.materia.split(', ').forEach(m => materias.add(m));
    }
    if (p.facultad && p.facultad !== "Sin asignar") facultades.add(p.facultad);
    if (p.aula && p.aula !== "Sin Aula") {
      const aulaParts = p.aula.split(', ');
      aulaParts.forEach(a => {
        if (a.includes('-')) {
          edificios.add(a.split('-')[1]);
        } else {
          const letterMatch = a.match(/[a-zA-Z]+/);
          if (letterMatch) edificios.add(letterMatch[0]);
          else edificios.add(a);
        }
      });
    }
  });

  if (selMateria) {
    selMateria.innerHTML = '<option value="">Materia</option>';
    Array.from(materias).sort().forEach(m => {
      selMateria.innerHTML += `<option value="${m}">${m}</option>`;
    });
  }

  if (selFacultad) {
    selFacultad.innerHTML = '<option value="">Facultad</option>';
    Array.from(facultades).sort().forEach(f => {
      selFacultad.innerHTML += `<option value="${f}">${f}</option>`;
    });
  }

  if (selEdificio) {
    selEdificio.innerHTML = '<option value="">Edificio</option>';
    Array.from(edificios).sort().forEach(e => {
      selEdificio.innerHTML += `<option value="${e}">Edificio ${e}</option>`;
    });
  }
}

// Escuchas para filtrado instantáneo en el sidebar derecho
function initFilters() {
  const searchInput = document.getElementById('search-input');
  const selMateria = document.getElementById('filter-materia');
  const selFacultad = document.getElementById('filter-facultad');
  const selEdificio = document.getElementById('filter-edificio');
  const depts = document.querySelectorAll('input[name="dept"]');
  const selAsist1 = document.getElementById('filter-asistencia-1');

  const applyFilters = () => {
    if (currentView !== 'dashboard') return;

    const text = searchInput.value.toLowerCase().trim();
    const mat = selMateria.value;
    const fac = selFacultad.value;
    const edif = selEdificio.value;

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
      if (mat && !(p.materia || '').includes(mat)) return false;
      if (fac && p.facultad !== fac) return false;
      if (edif && !(p.aula || '').includes(edif)) return false;
      if (selectedDepts.length > 0) {
        const dummyDept = `departamento ${(p.id_profesor % 4) + 1}`;
        if (!selectedDepts.includes(dummyDept)) return false;
      }
      return true;
    });

    renderCards(filtered);
  };

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (selMateria) selMateria.addEventListener('change', applyFilters);
  if (selFacultad) selFacultad.addEventListener('change', applyFilters);
  if (selEdificio) selEdificio.addEventListener('change', applyFilters);
  depts.forEach(cb => cb.addEventListener('change', applyFilters));

  if (selAsist1) {
    selAsist1.addEventListener('change', () => {
      alert("Filtrado por asistencia en tiempo real configurado en simulación.");
    });
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
      if (tableName === 'profesor') {
        response = {
          columns: ['id_profesor', 'nb_profesor', 'ap_profesor'],
          rows: [
            { id_profesor: 1, nb_profesor: "Carlos", ap_profesor: "Rodríguez" },
            { id_profesor: 2, nb_profesor: "Ana", ap_profesor: "Pérez" }
          ]
        };
      } else {
        response = {
          columns: ['id_materia', 'nb_materia'],
          rows: [
            { id_materia: 1, nb_materia: "Algoritmos Avanzados" },
            { id_materia: 2, nb_materia: "Introducción a la Física" }
          ]
        };
      }
    }

    activeCrudData = response;

    // Renderizar Cabecera de Tabla
    thead.innerHTML = '';
    const headerRow = document.createElement('tr');
    response.columns.forEach(col => {
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
        const td = document.createElement('td');
        if (col === 'qr_content') {
          // Mostrar el contenido QR como badge visual
          const val = row[col];
          if (val && val.trim() !== '') {
            td.innerHTML = `<span style="display:inline-flex;align-items:center;gap:5px;background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;border-radius:6px;padding:3px 10px;font-size:12px;font-weight:600;">&#x2705; Asignado</span><br><small style="color:#64748b;font-size:11px;word-break:break-all;">${val.length > 30 ? val.slice(0, 30) + '...' : val}</small>`;
          } else {
            td.innerHTML = `<span style="display:inline-flex;align-items:center;gap:5px;background:#f8fafc;color:#94a3b8;border:1px solid #e2e8f0;border-radius:6px;padding:3px 10px;font-size:12px;font-weight:600;">&#x2B1C; Sin QR</span>`;
          }
        } else {
          td.textContent = row[col] !== null ? row[col] : '-';
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
            📅 Horario
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

  const select = document.getElementById('schedule-materia-select');
  select.innerHTML = '<option value="">Cargando materias...</option>';

  try {
    let materias = [];
    if (window.eel) {
      const response = await eel.get_table_data('materia')();
      materias = response.rows || [];
    } else {
      materias = [{ id_materia: 1, nb_materia: "Algoritmos Avanzados" }];
    }

    select.innerHTML = '<option value="">Selecciona una Materia</option>';
    if (materias.length === 0) {
      select.innerHTML = '<option value="">No hay materias registradas. Agrégalas en "Gestionar Materias".</option>';
    } else {
      materias.forEach(m => {
        select.innerHTML += `<option value="${m.id_materia}">${m.nb_materia}</option>`;
      });
    }
  } catch (err) {
    console.error(err);
    select.innerHTML = '<option value="">Error al cargar materias.</option>';
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
  const select = document.getElementById('schedule-materia-select');
  const aulaInput = document.getElementById('schedule-aula-input');

  if (!select.value || !aulaInput.value) {
    alert("Por favor, selecciona una materia e ingresa el aula.");
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
    id_materia: parseInt(select.value),
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
