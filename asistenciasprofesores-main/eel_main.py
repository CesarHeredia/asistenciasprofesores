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
def get_stats_count():
    """Devuelve las estadísticas reales de la base de datos (profesores, materias, horas y asistencias)."""
    return backend.get_stats_count(DB_PATH)

if __name__ == '__main__':
    # Arranca en modo de escritorio optimizado usando Edge (Chromium)
    # y el tamaño panorámico del panel original.
    print("Iniciando aplicación de asistencia académica...")
    eel.start('index.html', size=(1300, 800), mode='edge', port=8080)
