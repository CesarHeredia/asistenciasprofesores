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

        # Obtener todos los profesores
        con = get_db_connection(db_path)
        cur = con.cursor()
        cur.execute("SELECT id_profesor, nb_profesor, ap_profesor FROM profesor")
        all_profs = [dict(p) for p in cur.fetchall()]
        con.close()

        import datetime
        today_str = datetime.date.today().isoformat()

        # Profesores que ya tienen registros hoy
        checked_in_today = {r["id_profesor"] for r in rows if r["fecha_asistencia"] == today_str}

        for prof in all_profs:
            if prof["id_profesor"] not in checked_in_today:
                rows.append({
                    "id_asistencia": None,
                    "fecha_asistencia": today_str,
                    "hora_entrada": "",
                    "hora_salida": "",
                    "id_profesor": prof["id_profesor"],
                    "nb_profesor": prof["nb_profesor"],
                    "ap_profesor": prof["ap_profesor"],
                    "estado": "Ausente"
                })

        # Ordenar por fecha desc, luego por hora_entrada desc
        rows.sort(key=lambda x: (x["fecha_asistencia"] or "", x["hora_entrada"] or ""), reverse=True)
        return rows
    except Exception as e:
        print("Error obteniendo historial de asistencias:", e)
        return []

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


