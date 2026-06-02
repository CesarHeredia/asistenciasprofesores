import sqlite3
import os

db_path = 'backend/db/gestion_academica.db'
if os.path.exists(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    try:
        # Disable foreign keys temporarily for schema changes
        cur.execute("PRAGMA foreign_keys = OFF;")
        
        # 1. Migrate horario table (remove id_aula column)
        # Check if id_aula is in columns
        cur.execute("PRAGMA table_info(horario);")
        columns = [c[1] for c in cur.fetchall()]
        
        if 'id_aula' in columns:
            print("Migrating horario table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS horario_new (
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
            
            cur.execute("""
                INSERT INTO horario_new (id_horario, id_profesor, id_materia, dia_semana, hora_inicio, hora_fin, num_aula)
                SELECT id_horario, id_profesor, id_materia, dia_semana, hora_inicio, hora_fin, num_aula
                FROM horario;
            """)
            
            cur.execute("DROP TABLE horario;")
            cur.execute("ALTER TABLE horario_new RENAME TO horario;")
            print("Migrated horario table successfully.")

        # 2. Recreate aula table without id_facultad
        cur.execute("PRAGMA table_info(aula);")
        aula_columns = [c[1] for c in cur.fetchall()]
        if 'id_facultad' in aula_columns:
            print("Migrating aula table...")
            cur.execute("DROP TABLE IF EXISTS aula;")
            cur.execute("""
                CREATE TABLE aula (
                    id_aula INTEGER PRIMARY KEY AUTOINCREMENT,
                    num_aula TEXT NOT NULL
                );
            """)
            print("Migrated aula table successfully.")
            
        # 3. Drop facultad table
        print("Dropping facultad table...")
        cur.execute("DROP TABLE IF EXISTS facultad;")
        print("Dropped facultad table successfully.")
        
        con.commit()
        print("Migration complete!")
    except Exception as e:
        con.rollback()
        print("Migration failed:", e)
    finally:
        con.close()
else:
    print("Database file not found.")
