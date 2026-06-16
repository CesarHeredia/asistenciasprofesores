"""Módulo backend de Python para la gestión de asistencia y persistencia de datos.
Maneja la inicialización, consultas y operaciones CRUD sobre la base de datos gestion_academica.db.
"""
import os
import sqlite3

def get_db_connection(db_path):
    """Abre y retorna una conexión a la base de datos SQLite con soporte para claves foráneas y factory de filas."""
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    con.row_factory = sqlite3.Row
    return con

def init_database(db_path):
    """Crea la estructura de tablas necesarias e inicializa datos semilla si la base de datos no existe o está vacía."""
    con = get_db_connection(db_path)
    cur = con.cursor()

    # 2. Tabla Profesor
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profesor (
            id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
            nb_profesor TEXT NOT NULL,
            ap_profesor TEXT NOT NULL,
            qr_content TEXT DEFAULT '' NOT NULL,
            telefono_personal TEXT DEFAULT '',
            telefono_emergencia TEXT DEFAULT '',
            cedula TEXT DEFAULT ''
        );
    """)

    # Migración: agregar qr_content si ya existe la tabla sin esa columna
    cur.execute("PRAGMA table_info(profesor);")
    col_names = [row[1] for row in cur.fetchall()]
    if 'qr_content' not in col_names:
        cur.execute("ALTER TABLE profesor ADD COLUMN qr_content TEXT DEFAULT '' NOT NULL;")
    if 'telefono_personal' not in col_names:
        cur.execute("ALTER TABLE profesor ADD COLUMN telefono_personal TEXT DEFAULT '';")
    if 'telefono_emergencia' not in col_names:
        cur.execute("ALTER TABLE profesor ADD COLUMN telefono_emergencia TEXT DEFAULT '';")
    if 'cedula' not in col_names:
        cur.execute("ALTER TABLE profesor ADD COLUMN cedula TEXT DEFAULT '';")

    # 3. Tabla Materia
    cur.execute("""
        CREATE TABLE IF NOT EXISTS materia (
            id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
            nb_materia TEXT NOT NULL
        );
    """)

    # 4. Tabla Aula
    cur.execute("""
        CREATE TABLE IF NOT EXISTS aula (
            id_aula INTEGER PRIMARY KEY AUTOINCREMENT,
            num_aula TEXT NOT NULL
        );
    """)

    # 5. Tabla Asistencias
    cur.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_profesor INTEGER NOT NULL,
            fecha_asistencia TEXT NOT NULL,  -- YYYY-MM-DD
            hora_entrada TEXT NOT NULL,      -- HH:MM:SS
            hora_salida TEXT,
            FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor) ON DELETE RESTRICT
        );
    """)

    # 6. Tabla Horario
    cur.execute("""
        CREATE TABLE IF NOT EXISTS horario (
            id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
            id_profesor INTEGER NOT NULL,
            id_materia INTEGER NOT NULL,
            dia_semana TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            num_aula TEXT,
            FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor) ON DELETE CASCADE,
            FOREIGN KEY (id_materia) REFERENCES materia(id_materia) ON DELETE CASCADE
        );
    """)

    # 7. Tabla Configuración Admin (credenciales editables y api key)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            username TEXT NOT NULL DEFAULT 'admin',
            password TEXT NOT NULL DEFAULT 'admin',
            gemini_api_key TEXT DEFAULT ''
        );
    """)

    # Migración para agregar columna gemini_api_key si no existe
    cur.execute("PRAGMA table_info(admin_config);")
    config_cols = [row[1] for row in cur.fetchall()]
    if 'gemini_api_key' not in config_cols:
        cur.execute("ALTER TABLE admin_config ADD COLUMN gemini_api_key TEXT DEFAULT '';")

    # Insertar credenciales por defecto si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM admin_config;")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO admin_config (id, username, password, gemini_api_key) VALUES (1, 'admin', 'admin', '');")

    con.commit()
    con.close()

def get_dashboard_data(db_path):
    """Devuelve la lista de profesores combinada con sus materias y aulas activas para el Dashboard central."""
    if not os.path.exists(db_path):
        return []
    try:
        import datetime
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        # Obtener el estado actual de asistencia de hoy para todos los profesores
        today_str = datetime.date.today().isoformat()
        cur.execute("""
            SELECT id_profesor, hora_entrada, hora_salida 
            FROM asistencias 
            WHERE fecha_asistencia = ? 
            ORDER BY id_asistencia ASC
        """, (today_str,))
        attendance_rows = cur.fetchall()
        
        estado_profesores = {}
        for r in attendance_rows:
            pid = r["id_profesor"]
            h_in = r["hora_entrada"]
            h_out = r["hora_salida"]
            estado_profesores[pid] = {
                "hora_entrada": h_in,
                "hora_salida": h_out
            }
        
        # JOIN query to load complete teachers and schedule/subject information
        query = """
            SELECT 
                p.id_profesor, 
                p.nb_profesor, 
                p.ap_profesor,
                m.nb_materia,
                h.num_aula,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin
            FROM profesor p
            LEFT JOIN horario h ON p.id_profesor = h.id_profesor
            LEFT JOIN materia m ON h.id_materia = m.id_materia
        """
        cur.execute(query)
        rows = cur.fetchall()
        con.close()
        
        # Group database items by teacher ID
        profesores_dict = {}
        for r in rows:
            id_prof, nb, ap, materia, aula, dia, h_ini, h_fin = r
            nombre_completo = f"{nb} {ap}".strip()
            
            if id_prof not in profesores_dict:
                profesores_dict[id_prof] = {
                    "id_profesor": id_prof,
                    "nombre": nombre_completo,
                    "materias": [],
                    "aulas": [],
                    "horarios": [],
                    "schedule_slots": []
                }
            
            if materia and materia not in profesores_dict[id_prof]["materias"]:
                profesores_dict[id_prof]["materias"].append(materia)
            if aula and aula not in profesores_dict[id_prof]["aulas"]:
                profesores_dict[id_prof]["aulas"].append(str(aula))
            if dia:
                profesores_dict[id_prof]["horarios"].append(f"{dia} ({h_ini}-{h_fin})")
                profesores_dict[id_prof]["schedule_slots"].append({
                    "dia": dia,
                    "hora_inicio": h_ini,
                    "hora_fin": h_fin,
                    "materia": materia if materia else "Sin Materia",
                    "aula": str(aula) if aula else "-"
                })
        
        result = []
        for id_prof, info in profesores_dict.items():
            materia_str = ", ".join(info["materias"]) if info["materias"] else "Sin Materia Asignada"
            aula_str = ", ".join(info["aulas"]) if info["aulas"] else "Sin Aula"
            
            # Smart avatar assignment
            avatar = "🧔🏽"
            nombre_lower = info["nombre"].lower()
            if any(x in nombre_lower for x in ["ana", "sofia", "maria", "dra.", "lic. sofia", "laura", "gabriela"]):
                avatar = "👩🏽" if "sofia" in nombre_lower else "👩🏻"
            elif any(x in nombre_lower for x in ["carlos", "alexander", "jose", "pedro"]):
                avatar = "🧔🏽"
            elif any(x in nombre_lower for x in ["david", "chen", "luis", "juan"]):
                avatar = "👨🏻"
            else:
                avatar = "🧔🏽" if id_prof % 2 == 0 else "👨🏼"
            
            attendance_info = estado_profesores.get(id_prof, {"hora_entrada": None, "hora_salida": None})
            result.append({
                "id_profesor": id_prof,
                "nombre": info["nombre"],
                "materia": materia_str,
                "aula": aula_str,
                "avatar": avatar,
                "horario": ", ".join(info["horarios"]) if info["horarios"] else "No programado",
                "schedule_slots": info["schedule_slots"],
                "hora_entrada": attendance_info["hora_entrada"],
                "hora_salida": attendance_info["hora_salida"]
            })
            
        return result
    except Exception as e:
        print('Error leyendo datos de dashboard en backend:', e)
        return []

def get_table_data(db_path, table_name):
    """Devuelve todas las columnas y registros de la tabla especificada (profesor o materia)."""
    if not os.path.exists(db_path) or table_name not in ["profesor", "materia"]:
        return {"columns": [], "rows": []}
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        con.close()
        
        if not rows:
            # Obtener las columnas si la tabla está vacía
            con = get_db_connection(db_path)
            cur = con.cursor()
            cur.execute(f"PRAGMA table_info({table_name})")
            cols = [col[1] for col in cur.fetchall()]
            con.close()
            return {"columns": cols, "rows": []}
            
        cols = list(rows[0].keys())
        rows_list = [dict(r) for r in rows]
        return {"columns": cols, "rows": rows_list}
    except Exception as e:
        print(f"Error cargando tabla {table_name} en backend:", e)
        return {"columns": [], "rows": []}

def add_table_row(db_path, table_name, row_data):
    """Inserta un nuevo registro en la tabla especificada de forma parametrizada y segura."""
    if not os.path.exists(db_path) or table_name not in ["profesor", "materia"]:
        return {"success": False, "error": "Tabla no válida"}
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        columns = list(row_data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        values = list(row_data.values())
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        cur.execute(query, values)
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print(f"Error insertando en {table_name} en backend:", e)
        return {"success": False, "error": str(e)}

def update_table_field(db_path, table_name, id_col_name, row_id, field_name, new_value):
    """Actualiza un solo campo de una tabla específica."""
    if not os.path.exists(db_path):
        return {"success": False, "error": "BD no encontrada"}
    
    # Validar nombres de tabla y columnas para evitar inyecciones SQL
    if table_name not in ["profesor", "materia"]:
        return {"success": False, "error": "Tabla no válida"}
        
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        query = f"UPDATE {table_name} SET {field_name} = ? WHERE {id_col_name} = ?"
        cur.execute(query, (new_value, row_id))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print(f"Error actualizando {field_name} en {table_name}:", e)
        return {"success": False, "error": str(e)}

def delete_table_row(db_path, table_name, row_id):
    """Elimina un registro por ID y limpia sus relaciones en cascada (horarios/asistencias)."""
    if not os.path.exists(db_path) or table_name not in ["profesor", "materia"]:
        return {"success": False, "error": "Tabla no válida"}
    try:
        id_col = "id_profesor" if table_name == "profesor" else "id_materia"
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        # Limpieza manual adicional por seguridad
        if table_name == "profesor":
            cur.execute("DELETE FROM horario WHERE id_profesor = ?", (row_id,))
            cur.execute("DELETE FROM asistencias WHERE id_profesor = ?", (row_id,))
        elif table_name == "materia":
            cur.execute("DELETE FROM horario WHERE id_materia = ?", (row_id,))
            
        query = f"DELETE FROM {table_name} WHERE {id_col} = ?"
        cur.execute(query, (row_id,))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print(f"Error eliminando en {table_name} en backend:", e)
        return {"success": False, "error": str(e)}

def get_schedule_data(db_path, id_profesor):
    """Obtiene los bloques de horarios asignados a un docente específico."""
    if not os.path.exists(db_path):
        return []
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        query = """
            SELECT 
                h.id_horario, 
                h.dia_semana, 
                h.hora_inicio, 
                h.hora_fin, 
                m.nb_materia, 
                h.id_materia, 
                h.num_aula
            FROM horario h 
            JOIN materia m ON h.id_materia = m.id_materia 
            WHERE h.id_profesor = ?
        """
        cur.execute(query, (id_profesor,))
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows
    except Exception as e:
        print(f"Error cargando horarios del profesor {id_profesor} en backend:", e)
        return []

def save_schedule_slot(db_path, data):
    """Guarda o actualiza un conjunto de bloques de horarios asignados."""
    if not os.path.exists(db_path):
        return {"success": False, "error": "BD no encontrada"}
    try:
        id_profesor = int(data.get("id_profesor"))
        id_materia = int(data.get("id_materia"))
        num_aula = data.get("num_aula")
        dia_semana = data.get("dia_semana")
        slots = data.get("slots", [])
        
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        for slot in slots:
            h_inicio = slot.get("hora_inicio")
            h_fin = slot.get("hora_fin")
            
            # Borrar cualquier colisión existente para este docente en este bloque horario exacto
            cur.execute("""
                DELETE FROM horario 
                WHERE id_profesor = ? AND dia_semana = ? AND hora_inicio = ? AND hora_fin = ?
            """, (id_profesor, dia_semana, h_inicio, h_fin))
            
            # Insertar el nuevo bloque de horario
            cur.execute("""
                INSERT INTO horario (id_profesor, id_materia, dia_semana, hora_inicio, hora_fin, num_aula)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_profesor, id_materia, dia_semana, h_inicio, h_fin, num_aula))
            
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print("Error guardando horario en backend:", e)
        return {"success": False, "error": str(e)}

def delete_schedule_slot(db_path, id_horario):
    """Elimina una celda horaria específica del calendario."""
    if not os.path.exists(db_path):
        return {"success": False, "error": "BD no encontrada"}
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        cur.execute("DELETE FROM horario WHERE id_horario = ?", (id_horario,))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print("Error eliminando horario en backend:", e)
        return {"success": False, "error": str(e)}

def update_qr_content(db_path, id_profesor, qr_content):
    """Actualiza el contenido QR escaneado de un profesor específico en la base de datos."""
    if not os.path.exists(db_path):
        return {"success": False, "error": "BD no encontrada"}
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        cur.execute(
            "UPDATE profesor SET qr_content = ? WHERE id_profesor = ?",
            (qr_content, id_profesor)
        )
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print(f"Error actualizando QR del profesor {id_profesor} en backend:", e)
        return {"success": False, "error": str(e)}

def get_stats_count(db_path):
    """Obtiene el recuento real de estadísticas agregadas del sistema."""
    stats = {"profesores": 0, "materias": 0, "horas": 0, "asistencias": 0}
    if not os.path.exists(db_path):
        return stats
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        # 1. Total profesores
        cur.execute("SELECT COUNT(*) FROM profesor;")
        stats["profesores"] = cur.fetchone()[0]
        
        # 2. Total materias registradas
        cur.execute("SELECT COUNT(*) FROM materia;")
        stats["materias"] = cur.fetchone()[0]
        
        # 3. Total bloques horarios asignados
        cur.execute("SELECT COUNT(*) FROM horario;")
        stats["horas"] = cur.fetchone()[0]
        
        # 4. Total asistencias registradas
        cur.execute("SELECT COUNT(*) FROM asistencias;")
        stats["asistencias"] = cur.fetchone()[0]
        
        con.close()
        return stats
    except Exception as e:
        print("Error obteniendo estadísticas agregadas en backend:", e)
        return stats

def register_attendance_by_qr(db_path, qr_content):
    """Busca al profesor por su código QR y registra su entrada o salida en la tabla de asistencias.
    Retorna un diccionario con el estado y los detalles.
    """
    import datetime
    if not os.path.exists(db_path):
        return {"success": False, "error": "Base de datos no encontrada"}
    if not qr_content or not qr_content.strip():
        return {"success": False, "error": "Contenido QR vacío"}
        
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        # 1. Buscar profesor por QR
        cur.execute("SELECT id_profesor, nb_profesor, ap_profesor FROM profesor WHERE qr_content = ?", (qr_content.strip(),))
        row = cur.fetchone()
        if not row:
            con.close()
            return {"success": False, "error": "El código QR escaneado no está registrado a ningún profesor."}
            
        id_profesor = row["id_profesor"]
        nombre_completo = f"{row['nb_profesor']} {row['ap_profesor']}".strip()
        
        # 2. Determinar si es entrada o salida hoy
        today_str = datetime.date.today().isoformat() # YYYY-MM-DD
        current_time_str = datetime.datetime.now().strftime("%H:%M:%S") # HH:MM:SS
        
        # Buscar el último registro de hoy para este profesor
        cur.execute("""
            SELECT id_asistencia, hora_entrada, hora_salida 
            FROM asistencias 
            WHERE id_profesor = ? AND fecha_asistencia = ? 
            ORDER BY id_asistencia DESC LIMIT 1
        """, (id_profesor, today_str))
        
        last_attendance = cur.fetchone()
        
        if last_attendance and (last_attendance["hora_salida"] is None or last_attendance["hora_salida"] == ""):
            # Registrar SALIDA (actualizar registro)
            id_asistencia = last_attendance["id_asistencia"]
            cur.execute("""
                UPDATE asistencias 
                SET hora_salida = ? 
                WHERE id_asistencia = ?
            """, (current_time_str, id_asistencia))
            tipo = "salida"
        else:
            # Registrar ENTRADA (nuevo registro)
            cur.execute("""
                INSERT INTO asistencias (id_profesor, fecha_asistencia, hora_entrada, hora_salida)
                VALUES (?, ?, ?, NULL)
            """, (id_profesor, today_str, current_time_str))
            tipo = "entrada"
            
        con.commit()
        con.close()
        
        return {
            "success": True,
            "profesor_id": id_profesor,
            "profesor": nombre_completo,
            "tipo": tipo,
            "hora": current_time_str,
            "fecha": today_str
        }
    except Exception as e:
        print("Error registrando asistencia por QR:", e)
        return {"success": False, "error": f"Error en la base de datos: {str(e)}"}

def get_attendance_history(db_path):
    """Retorna el historial completo de entradas y salidas de los profesores, ordenado por fecha y hora descendente."""
    if not os.path.exists(db_path):
        return []
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        query = """
            SELECT 
                a.id_asistencia,
                a.fecha_asistencia,
                a.hora_entrada,
                a.hora_salida,
                p.id_profesor,
                p.nb_profesor,
                p.ap_profesor
            FROM asistencias a
            JOIN profesor p ON a.id_profesor = p.id_profesor
            ORDER BY a.fecha_asistencia DESC, a.hora_entrada DESC
        """
        cur.execute(query)
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows
    except Exception as e:
        print("Error obteniendo historial de asistencias:", e)
        return []

def get_admin_config(db_path):
    """Obtiene el usuario, contraseña y API Key de Gemini del administrador desde la tabla admin_config."""
    if not os.path.exists(db_path):
        return {"username": "admin", "password": "admin", "gemini_api_key": ""}
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        cur.execute("SELECT username, password, gemini_api_key FROM admin_config WHERE id = 1")
        row = cur.fetchone()
        con.close()
        if row:
            return dict(row)
        return {"username": "admin", "password": "admin", "gemini_api_key": ""}
    except Exception as e:
        print("Error obteniendo configuración de admin:", e)
        return {"username": "admin", "password": "admin", "gemini_api_key": ""}

def update_admin_config(db_path, username, password, gemini_api_key=""):
    """Actualiza el usuario, contraseña y API Key de Gemini del administrador en la tabla admin_config."""
    if not os.path.exists(db_path):
        return {"success": False, "error": "Base de datos no encontrada"}
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        cur.execute("UPDATE admin_config SET username = ?, password = ?, gemini_api_key = ? WHERE id = 1", (username, password, gemini_api_key))
        con.commit()
        con.close()
        return {"success": True}
    except Exception as e:
        print("Error actualizando configuración de admin:", e)
        return {"success": False, "error": str(e)}

def get_all_system_context(db_path):
    """Compila toda la información de la base de datos para servir como contexto a la IA."""
    import datetime
    
    if not os.path.exists(db_path):
        return "No hay base de datos disponible."
    
    con = get_db_connection(db_path)
    cur = con.cursor()
    
    # Profesores
    cur.execute("SELECT id_profesor, nb_profesor, ap_profesor, telefono_personal, telefono_emergencia, cedula FROM profesor")
    profesores = [dict(r) for r in cur.fetchall()]
    
    # Materias
    cur.execute("SELECT id_materia, nb_materia FROM materia")
    materias = [dict(r) for r in cur.fetchall()]
    
    # Aulas
    cur.execute("SELECT id_aula, num_aula FROM aula")
    aulas = [dict(r) for r in cur.fetchall()]
    
    # Horarios
    cur.execute("""
        SELECT h.id_horario, p.nb_profesor, p.ap_profesor, m.nb_materia, h.dia_semana, h.hora_inicio, h.hora_fin, h.num_aula
        FROM horario h
        JOIN profesor p ON h.id_profesor = p.id_profesor
        JOIN materia m ON h.id_materia = m.id_materia
    """)
    horarios = [dict(r) for r in cur.fetchall()]
    
    # Asistencias recientes (últimas 100 filas)
    cur.execute("""
        SELECT a.fecha_asistencia, a.hora_entrada, a.hora_salida, p.nb_profesor, p.ap_profesor
        FROM asistencias a
        JOIN profesor p ON a.id_profesor = p.id_profesor
        ORDER BY a.fecha_asistencia DESC, a.hora_entrada DESC
        LIMIT 100
    """)
    asistencias = [dict(r) for r in cur.fetchall()]
    
    con.close()
    
    # Obtener fecha y hora actuales del sistema para dárselas a la IA
    now = datetime.datetime.now()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_semana_actual = dias[now.weekday()]
    fecha_actual = now.strftime("%Y-%m-%d")
    hora_actual = now.strftime("%H:%M:%S")
    
    context = []
    
    context.append("--- FECHA Y HORA ACTUAL DEL SISTEMA (USA ESTO PARA UBICAR 'HOY' O EL DIA ACTUAL) ---")
    context.append(f"Fecha de hoy: {fecha_actual}")
    context.append(f"Día de la semana de hoy: {dia_semana_actual}")
    context.append(f"Hora actual: {hora_actual}\n")
    
    context.append("--- DATOS DE PROFESORES ---")
    for p in profesores:
        context.append(f"Profesor ID {p['id_profesor']}: {p['nb_profesor']} {p['ap_profesor']} | Cédula: {p['cedula']} | Teléfono: {p['telefono_personal']} | Emergencia: {p['telefono_emergencia']}")
        
    context.append("\n--- MATERIAS DISPONIBLES ---")
    for m in materias:
        context.append(f"Materia ID {m['id_materia']}: {m['nb_materia']}")
        
    context.append("\n--- AULAS REGISTRADAS ---")
    for a in aulas:
        context.append(f"Aula ID {a['id_aula']}: {a['num_aula']}")
        
    context.append("\n--- HORARIOS Y ASIGNACIONES ---")
    for h in horarios:
        context.append(f"El profesor {h['nb_profesor']} {h['ap_profesor']} enseña la materia '{h['nb_materia']}' el día {h['dia_semana']} de {h['hora_inicio']} a {h['hora_fin']} en el aula '{h['num_aula']}'")
        
    context.append("\n--- HISTORIAL DE ASISTENCIAS (ÚLTIMOS REGISTROS) ---")
    for a in asistencias:
        salida_str = f" a las {a['hora_salida']}" if a['hora_salida'] else " (No ha marcado salida aún)"
        context.append(f"Fecha: {a['fecha_asistencia']} | {a['nb_profesor']} {a['ap_profesor']} entró a las {a['hora_entrada']}{salida_str}")

    # Calcular inasistentes confirmados de HOY (clases que ya terminaron y el profesor no se presentó)
    now_minutes = now.hour * 60 + now.minute
    profesores_asistieron_hoy = set(
        a['nb_profesor'] + ' ' + a['ap_profesor']
        for a in asistencias if a['fecha_asistencia'] == fecha_actual
    )

    ausentes_hoy = []
    # Agrupar horarios por profesor y verificar si todas sus clases de hoy ya terminaron
    prof_slots_hoy = {}
    for h in horarios:
        if h['dia_semana'] == dia_semana_actual:
            nombre = f"{h['nb_profesor']} {h['ap_profesor']}"
            if nombre not in prof_slots_hoy:
                prof_slots_hoy[nombre] = []
            prof_slots_hoy[nombre].append(h)

    for nombre_prof, slots in prof_slots_hoy.items():
        if nombre_prof in profesores_asistieron_hoy:
            continue  # Ya asistió, no es ausente
        def slot_end_min(s):
            parts = s['hora_fin'].split(':')
            return int(parts[0]) * 60 + int(parts[1])
        last_end = max(slot_end_min(s) for s in slots)
        if now_minutes >= last_end:
            ausentes_hoy.append(nombre_prof)

    if ausentes_hoy:
        context.append(f"\n--- INASISTENCIAS CONFIRMADAS DE HOY ({fecha_actual}) ---")
        context.append("Los siguientes profesores tenían clases programadas para hoy, sus horarios ya terminaron, y NO se presentaron (INASISTENTES):")
        for nombre in ausentes_hoy:
            context.append(f"  - {nombre}")
    else:
        context.append(f"\n--- INASISTENCIAS DE HOY ({fecha_actual}) ---")
        context.append("No hay inasistencias confirmadas hasta el momento (aún hay clases en curso o todos asistieron).")

    return "\n".join(context)

def ask_ai_assistant(db_path, user_question):
    """Obtiene respuesta de la IA (Gemini) para la consulta del usuario."""
    import urllib.request
    import json
    
    if not os.path.exists(db_path):
        return {"success": False, "error": "Base de datos no encontrada"}
    
    con = get_db_connection(db_path)
    cur = con.cursor()
    cur.execute("SELECT gemini_api_key FROM admin_config WHERE id = 1")
    row = cur.fetchone()
    con.close()
    
    api_key = row["gemini_api_key"] if row else ""
    if not api_key:
        return {"success": False, "error": "API Key de Gemini no configurada"}
    
    system_context = get_all_system_context(db_path)
    
    system_instruction = (
        "Eres un asistente virtual de asistencia académica para la institución. Tu objetivo es responder preguntas "
        "del personal administrativo utilizando únicamente la información real del sistema que te proporcionamos "
        "en el contexto. Responde de forma amable, clara y concisa en español. "
        "Si te preguntan por datos que no están en el contexto o que no pertenecen a la institución, responde amablemente "
        "que no tienes esa información en el sistema.\n\n"
        f"CONTEXTO DE LA INSTITUCIÓN:\n{system_context}"
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": user_question}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if 'candidates' in res_data and len(res_data['candidates']) > 0:
                text_response = res_data['candidates'][0]['content']['parts'][0]['text']
                return {"success": True, "reply": text_response}
            else:
                return {"success": False, "error": "Respuesta vacía o error de formato de la API"}
    except Exception as e:
        print("Error en llamada a Gemini API:", e)
        return {"success": False, "error": f"Error al conectar con la API de Gemini. Verifica tu conexión a internet o la API Key."}

def get_downloads_folder():
    """Retorna la ruta de la carpeta de descargas del usuario de forma multiplataforma."""
    home = os.path.expanduser("~")
    # Intentar buscar la carpeta Descargas en español o Downloads en inglés
    descargas = os.path.join(home, "Descargas")
    if os.path.exists(descargas):
        return descargas
    downloads = os.path.join(home, "Downloads")
    if os.path.exists(downloads):
        return downloads
    return home # Fallback al home

def save_pdf_file(base64_data, filename):
    """Guarda un archivo PDF codificado en base64 en la carpeta de Descargas del usuario."""
    import base64
    try:
        downloads_dir = get_downloads_folder()
        filepath = os.path.join(downloads_dir, filename)
        
        # Si el archivo ya existe, añadir sufijo incremental para no sobreescribir
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            counter += 1
            
        file_bytes = base64.b64decode(base64_data)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
            
        return {"success": True, "path": filepath}
    except Exception as e:
        print("Error al guardar PDF desde el backend:", e)
        return {"success": False, "error": str(e)}


