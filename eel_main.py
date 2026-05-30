"""Arranca la UI web con Eel y expone funciones de negocio a JS.
Actúa como un controlador delgado delegando la persistencia y la lógica SQL a backend.py.
"""
import os
import sys

# Asegurar que importamos de forma relativa correcta
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

import backend

try:
    import eel
except Exception as e:
    print("Eel no está instalado. Instálalo con: pip install eel")
    raise

WEB = os.path.join(ROOT, 'front')
DB_PATH = os.path.join(ROOT, 'gestion_academica.db')

# Inicializar Eel con la carpeta de frontend
eel.init(WEB)

# Garantizar que la base de datos y sus tablas estén listas e inicializadas
backend.init_database(DB_PATH)

@eel.expose
def get_dashboard_data():
    """Retorna la lista estructurada de profesores, sus materias y aulas activas para el Dashboard central."""
    return backend.get_dashboard_data(DB_PATH)

@eel.expose
def get_table_data(table_name):
    """Devuelve todas las columnas y filas de una tabla amigable para el panel CRUD de gestión."""
    return backend.get_table_data(DB_PATH, table_name)

@eel.expose
def add_table_row(table_name, row_data):
    """Añade un nuevo registro de forma parametrizada y retorna el estado de éxito."""
    return backend.add_table_row(DB_PATH, table_name, row_data)

@eel.expose
def delete_table_row(table_name, row_id):
    """Elimina una fila específica por su ID y limpia sus relaciones asociadas en cascada."""
    return backend.delete_table_row(DB_PATH, table_name, row_id)

@eel.expose
def get_schedule_data(id_profesor):
    """Obtiene los bloques de horarios asociados a un profesor específico."""
    return backend.get_schedule_data(DB_PATH, id_profesor)

@eel.expose
def save_schedule_slot(data):
    """Guarda bloques de horarios de un docente, reemplazando solapamientos."""
    return backend.save_schedule_slot(DB_PATH, data)

@eel.expose
def delete_schedule_slot(id_horario):
    """Elimina un bloque específico de horario por su ID."""
    return backend.delete_schedule_slot(DB_PATH, id_horario)

@eel.expose
def update_qr_content(id_profesor, qr_content):
    """Actualiza el contenido QR de un docente específico en la base de datos."""
    return backend.update_qr_content(DB_PATH, id_profesor, qr_content)

@eel.expose
def get_stats_count():
    """Devuelve las estadísticas reales de la base de datos (profesores, materias, horas y asistencias)."""
    return backend.get_stats_count(DB_PATH)

@eel.expose
def register_attendance_by_qr(qr_content):
    """Registra la asistencia de un profesor por su QR (entrada o salida)."""
    return backend.register_attendance_by_qr(DB_PATH, qr_content)

@eel.expose
def get_attendance_history():
    """Devuelve el historial completo de asistencias para auditoria."""
    return backend.get_attendance_history(DB_PATH)

if __name__ == '__main__':
    import socket
    import threading
    import webview

    print("Buscando puerto libre...")
    # 1. Encontrar un puerto libre usando socket para evitar conflictos
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()

    print(f"Puerto libre encontrado: {port}")

    # 2. Iniciar Eel de fondo desactivando su apertura de navegador integrada (mode=None)
    def run_eel():
        print(f"Iniciando servidor de Eel en el puerto {port}...")
        eel.start('index.html', mode=None, port=port)

    # 3. Lanzar Eel en un hilo daemon
    eel_thread = threading.Thread(target=run_eel, daemon=True)
    eel_thread.start()

    # 4. Crear e iniciar la ventana nativa de escritorio limpia usando pywebview
    print(f"Abriendo ventana nativa de PyWebView para la aplicación...")
    webview.create_window(
        "Gestión de Asistencia Académica",
        url=f"http://localhost:{port}/index.html",
        width=1300,
        height=800,
        resizable=True
    )
    webview.start(gui='qt')
