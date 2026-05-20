import React from 'react';
import { Calendar, Download, Users, UserCheck, UserX, Clock, Search } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const tableData = [
    { name: "María González", department: "Recursos Humanos", in: "08:00", out: "17:00", status: "Presente" },
    { name: "Juan Pérez", department: "Desarrollo", in: "09:15", out: "18:15", status: "Tardanza" },
    { name: "Ana Martínez", department: "Ventas", in: "-", out: "-", status: "Ausente" },
    { name: "Carlos López", department: "Marketing", in: "08:30", out: "17:30", status: "Presente" },
    { name: "Laura Rodríguez", department: "Finanzas", in: "-", out: "-", status: "Permiso" },
    { name: "Pedro Sánchez", department: "Desarrollo", in: "08:05", out: "17:05", status: "Presente" },
    { name: "Sofía Torres", department: "Diseño", in: "08:45", out: "17:45", status: "Presente" },
    { name: "Diego Ramírez", department: "Operaciones", in: "09:30", out: "-", status: "Tardanza" },
  ];

  const handleExport = async () => {
    if (window.eel) {
      try {
        const response = await window.eel.export_data()();
        alert("Respuesta de Python: " + response);
      } catch (e) {
        console.error("Error comunicándose con Python:", e);
      }
    } else {
      alert("Eel API no encontrada. Asegúrate de correr la app a través de Python.");
    }
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-title">
          <h1>Sistema de Gestión de Asistencias USM</h1>
          <p>Martes, 20 de Mayo 2026</p>
        </div>
        <div className="header-actions">
          <button className="btn">
            <Calendar size={18} />
            Hoy
          </button>
          <button className="btn btn-export" onClick={handleExport}>
            <Download size={18} />
            Exportar
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="tabs">
          <div className="tab active">
            <Calendar size={18} />
            Asistencias
          </div>
          <div className="tab">
            <Users size={18} />
            Gestión de Empleados
          </div>
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-header">
              Total Empleados
              <Users size={20} className="metric-icon" />
            </div>
            <div className="metric-value">200</div>
            <div className="metric-subtitle blue">Empleados registrados</div>
            <div className="metric-change positive">+5% vs mes anterior</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              Presentes Hoy
              <UserCheck size={20} className="metric-icon" />
            </div>
            <div className="metric-value">186</div>
            <div className="metric-subtitle blue">93% de asistencia</div>
            <div className="metric-change positive">+2% vs mes anterior</div>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              Ausentes
              <UserX size={20} className="metric-icon" />
            </div>
            <div className="metric-value">8</div>
            <div className="metric-subtitle blue">4% del total</div>
            <div className="metric-change negative">-1% vs mes anterior</div>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              Tardanzas
              <Clock size={20} className="metric-icon" />
            </div>
            <div className="metric-value">6</div>
            <div className="metric-subtitle blue">3% del total</div>
            <div className="metric-change negative">-3% vs mes anterior</div>
          </div>
        </div>

        <section className="table-section">
          <div className="table-header">
            <h2>Registro de Asistencias - Hoy</h2>
            <div className="search-bar">
              <Search size={18} color="#6c757d" />
              <input type="text" placeholder="Buscar por nombre o departamento..." />
            </div>
          </div>

          <table className="attendance-table">
            <thead>
              <tr>
                <th>Empleado</th>
                <th>Departamento</th>
                <th>Entrada</th>
                <th>Salida</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, index) => (
                <tr key={index}>
                  <td>{row.name}</td>
                  <td>{row.department}</td>
                  <td>{row.in}</td>
                  <td>{row.out}</td>
                  <td>
                    <span className={`badge badge-${row.status.toLowerCase()}`}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
