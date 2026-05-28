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

    # 1. Tabla Facultad
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facultad (
            id_facultad INTEGER PRIMARY KEY AUTOINCREMENT,
            nb_facultad TEXT NOT NULL
        );
    """)

    # 2. Tabla Profesor
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profesor (
            id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
            nb_profesor TEXT NOT NULL,
            ap_profesor TEXT NOT NULL,
            qr_content TEXT DEFAULT '' NOT NULL
        );
    """)

    # Migración: agregar qr_content si ya existe la tabla sin esa columna
    cur.execute("PRAGMA table_info(profesor);")
    col_names = [row[1] for row in cur.fetchall()]
    if 'qr_content' not in col_names:
        cur.execute("ALTER TABLE profesor ADD COLUMN qr_content TEXT DEFAULT '' NOT NULL;")

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
            num_aula TEXT NOT NULL,
            id_facultad INTEGER NOT NULL,
            FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad) ON DELETE RESTRICT
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
            id_aula INTEGER,
            dia_semana TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            num_aula TEXT,
            FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor) ON DELETE CASCADE,
            FOREIGN KEY (id_materia) REFERENCES materia(id_materia) ON DELETE CASCADE,
            FOREIGN KEY (id_aula) REFERENCES aula(id_aula) ON DELETE CASCADE
        );
    """)

    # --- SEED DE FACULTADES Y AULAS ---
    # Solo si la tabla facultad está vacía
    cur.execute("SELECT COUNT(*) FROM facultad;")
    if cur.fetchone()[0] == 0:
        facultades = ["Ingeniería", "Ciencias Exactas", "Humanidades"]
        facultad_ids = {}
        for f in facultades:
            cur.execute("INSERT INTO facultad (nb_facultad) VALUES (?);", (f,))
            facultad_ids[f] = cur.lastrowid
            
        aulas_data = [
            ("101-B", "Ingeniería"),
            ("205", "Ciencias Exactas"),
            ("310", "Humanidades"),
            ("G-01", "Ingeniería")
        ]
        for num_aula, fac_name in aulas_data:
            fac_id = facultad_ids[fac_name]
            cur.execute("INSERT INTO aula (num_aula, id_facultad) VALUES (?, ?);", (num_aula, fac_id))

    # --- SEED DE PROFESORES, MATERIAS Y HORARIOS ---
    # ¡SOLO si no hay profesores ni materias ya registradas!
    # Esto protege y preserva por completo la base de datos original del usuario.
    cur.execute("SELECT COUNT(*) FROM profesor;")
    prof_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM materia;")
    mat_count = cur.fetchone()[0]

    if prof_count == 0 and mat_count == 0:
        profesores_data = [
            ("Carlos", "Rodríguez"),
            ("Ana", "Pérez"),
            ("Sofía", "Martínez"),
            ("David", "Chen")
        ]
        prof_ids = []
        for nb, ap in profesores_data:
            cur.execute("INSERT INTO profesor (nb_profesor, ap_profesor, qr_content) VALUES (?, ?, '');", (nb, ap))
            prof_ids.append(cur.lastrowid)

        materias_data = [
            "Algoritmos Avanzados",
            "Introducción a la Física",
            "Historia del Arte",
            "Programación de Sistemas"
        ]
        mat_ids = []
        for m in materias_data:
            cur.execute("INSERT INTO materia (nb_materia) VALUES (?);", (m,))
            mat_ids.append(cur.lastrowid)

        horarios_data = [
            (prof_ids[0], mat_ids[0], "Lunes", "07:00", "08:30", "101-B"),
            (prof_ids[1], mat_ids[1], "Lunes", "08:30", "10:00", "205"),
            (prof_ids[2], mat_ids[2], "Lunes", "10:00", "11:30", "310"),
            (prof_ids[3], mat_ids[3], "Lunes", "11:30", "13:00", "G-01")
        ]
        for p_id, m_id, dia, h_ini, h_fin, aula in horarios_data:
            cur.execute("""
                INSERT INTO horario (id_profesor, id_materia, dia_semana, hora_inicio, hora_fin, num_aula)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (p_id, m_id, dia, h_ini, h_fin, aula))

        asistencias_data = [
            (prof_ids[0], "2026-05-26", "06:55:00", "08:35:00"),
            (prof_ids[1], "2026-05-26", "08:28:00", "10:05:00"),
            (prof_ids[2], "2026-05-26", "09:50:00", "11:32:00")
        ]
        for p_id, fecha, h_ent, h_sal in asistencias_data:
            cur.execute("""
                INSERT INTO asistencias (id_profesor, fecha_asistencia, hora_entrada, hora_salida)
                VALUES (?, ?, ?, ?);
            """, (p_id, fecha, h_ent, h_sal))

    con.commit()
    con.close()

def get_dashboard_data(db_path):
    """Devuelve la lista de profesores combinada con sus materias y aulas activas para el Dashboard central."""
    if not os.path.exists(db_path):
        return []
    try:
        con = get_db_connection(db_path)
        cur = con.cursor()
        
        # JOIN query to load complete teachers and schedule/subject information
        query = """
            SELECT 
                p.id_profesor, 
                p.nb_profesor, 
                p.ap_profesor,
                m.nb_materia,
                h.num_aula,
                COALESCE(f.nb_facultad, 'Sin Asignar') AS nb_facultad,
                h.dia_semana,
                h.hora_inicio,
                h.hora_fin
            FROM profesor p
            LEFT JOIN horario h ON p.id_profesor = h.id_profesor
            LEFT JOIN materia m ON h.id_materia = m.id_materia
            LEFT JOIN aula a ON h.num_aula = a.num_aula
            LEFT JOIN facultad f ON a.id_facultad = f.id_facultad
        """
        cur.execute(query)
        rows = cur.fetchall()
        con.close()
        
        # Group database items by teacher ID
        profesores_dict = {}
        for r in rows:
            id_prof, nb, ap, materia, aula, facultad, dia, h_ini, h_fin = r
            nombre_completo = f"{nb} {ap}".strip()
            
            if id_prof not in profesores_dict:
                profesores_dict[id_prof] = {
                    "id_profesor": id_prof,
                    "nombre": nombre_completo,
                    "materias": [],
                    "aulas": [],
                    "facultades": [],
                    "horarios": [],
                    "schedule_slots": []
                }
            
            if materia and materia not in profesores_dict[id_prof]["materias"]:
                profesores_dict[id_prof]["materias"].append(materia)
            if aula and aula not in profesores_dict[id_prof]["aulas"]:
                profesores_dict[id_prof]["aulas"].append(str(aula))
            if facultad and facultad != 'Sin Asignar' and facultad not in profesores_dict[id_prof]["facultades"]:
                profesores_dict[id_prof]["facultades"].append(facultad)
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
            
            # Resolve a representative faculty
            if info["facultades"]:
                facultad_str = info["facultades"][0]
            else:
                m_lower = materia_str.lower()
                if any(x in m_lower for x in ["ingenieria", "programacion", "sistemas", "algoritmos", "computacion"]):
                    facultad_str = "Ingeniería"
                elif any(x in m_lower for x in ["fisica", "quimica", "matematica", "calculo", "algebra"]):
                    facultad_str = "Ciencias Exactas"
                elif any(x in m_lower for x in ["arte", "historia", "humanidades", "lengua", "filosofia"]):
                    facultad_str = "Humanidades"
                else:
                    facultad_str = "Ingeniería"  # Por defecto
            
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
            
            result.append({
                "id_profesor": id_prof,
                "nombre": info["nombre"],
                "materia": materia_str,
                "aula": aula_str,
                "facultad": facultad_str,
                "avatar": avatar,
                "horario": ", ".join(info["horarios"]) if info["horarios"] else "No programado",
                "schedule_slots": info["schedule_slots"]
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
