#!/usr/bin/env python3
"""
Script de migración para actualizar el esquema de la base de datos
Migra de esquema antiguo a esquema nuevo sin perder datos
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime


def migrate_database(db_path=".data/extraction.db"):
    """Migra la base de datos al nuevo esquema"""
    db_path = Path(db_path)
    
    if not db_path.exists():
        print("❌ Base de datos no encontrada. Nada que migrar.")
        return False
    
    # Crear backup
    backup_path = db_path.parent / f"extraction_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si las tablas antiguas existen
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='traversing'")
            if not cursor.fetchone():
                print("❌ Tabla 'traversing' no encontrada. Base de datos vacía o ya migrada.")
                return False
            
            # Obtener estructura actual
            cursor.execute("PRAGMA table_info(traversing)")
            current_columns = {row[1] for row in cursor.fetchall()}
            
            # Campos que queremos mantener (esquema nuevo)
            new_fields = {
                'source_file', 'publication_day', 'arrival_date', 'arrival_date_calc',
                'travel_departure_port', 'ship_type', 'ship_flag', 'ship_name',
                'master_role', 'master_name', 'cargo_list', 'raw_text'
            }
            
            # Si ya tiene el esquema nuevo, no hacer nada
            if current_columns == new_fields | {'id'}:
                print("✅ Base de datos ya tiene el esquema nuevo. Nada que migrar.")
                return True
            
            print(f"📊 Columnas actuales: {current_columns}")
            print(f"📊 Columnas nuevas: {new_fields | {'id'}}")
            
            # Limpiar tablas temporales si existen de intentos anteriores
            cursor.execute("DROP TABLE IF EXISTS traversing_new")
            cursor.execute("DROP TABLE IF EXISTS cabotage_new")
            
            # Crear tabla temporal con nuevo esquema
            cursor.execute('''
                CREATE TABLE traversing_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT NOT NULL,
                    publication_day TEXT,
                    arrival_date TEXT,
                    arrival_date_calc TEXT,
                    travel_departure_port TEXT,
                    ship_type TEXT,
                    ship_flag TEXT,
                    ship_name TEXT,
                    master_role TEXT,
                    master_name TEXT,
                    cargo_list TEXT,
                    raw_text TEXT NOT NULL,
                    UNIQUE(raw_text, source_file)
                )
            ''')
            
            # Copiar datos del esquema antiguo al nuevo con transformaciones
            # Mapear campos que existen en ambos esquemas
            fields_to_copy = new_fields & current_columns
            
            # Transformar publication_date a publication_day (formato DD-MM-YYYY)
            # Transformar travel_arrival_date a arrival_date_calc
            cursor.execute('''
                INSERT INTO traversing_new (
                    source_file, publication_day, arrival_date, arrival_date_calc,
                    travel_departure_port, ship_type, ship_flag, ship_name,
                    master_role, master_name, cargo_list, raw_text
                )
                SELECT 
                    source_file,
                    CASE 
                        WHEN publication_date LIKE '____-__-__' THEN 
                            substr(publication_date, 9, 2) || '-' || substr(publication_date, 6, 2) || '-' || substr(publication_date, 1, 4)
                        ELSE publication_date
                    END as publication_day,
                    NULL as arrival_date,
                    travel_arrival_date as arrival_date_calc,
                    travel_departure_port,
                    ship_type,
                    ship_flag,
                    ship_name,
                    master_role,
                    master_name,
                    cargo_list,
                    COALESCE(parsed_text, '') as raw_text
                FROM traversing
                WHERE parsed_text IS NOT NULL AND parsed_text != ''
            ''')
            
            migrated_count = cursor.rowcount
            print(f"✅ Migrados {migrated_count} registros de travesías")
            
            # Hacer lo mismo para cabotajes
            cursor.execute('''
                CREATE TABLE cabotage_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT NOT NULL,
                    publication_day TEXT,
                    arrival_date TEXT,
                    arrival_date_calc TEXT,
                    travel_departure_port TEXT,
                    ship_type TEXT,
                    ship_flag TEXT,
                    ship_name TEXT,
                    master_role TEXT,
                    master_name TEXT,
                    cargo_list TEXT,
                    raw_text TEXT NOT NULL,
                    UNIQUE(raw_text, source_file)
                )
            ''')
            
            # Mismo proceso para cabotaje con transformaciones
            cursor.execute('''
                INSERT INTO cabotage_new (
                    source_file, publication_day, arrival_date, arrival_date_calc,
                    travel_departure_port, ship_type, ship_flag, ship_name,
                    master_role, master_name, cargo_list, raw_text
                )
                SELECT 
                    source_file,
                    CASE 
                        WHEN publication_date LIKE '____-__-__' THEN 
                            substr(publication_date, 9, 2) || '-' || substr(publication_date, 6, 2) || '-' || substr(publication_date, 1, 4)
                        ELSE publication_date
                    END as publication_day,
                    NULL as arrival_date,
                    travel_arrival_date as arrival_date_calc,
                    travel_departure_port,
                    ship_type,
                    ship_flag,
                    ship_name,
                    master_role,
                    master_name,
                    cargo_list,
                    COALESCE(parsed_text, '') as raw_text
                FROM cabotage
                WHERE parsed_text IS NOT NULL AND parsed_text != ''
            ''')
            
            migrated_cabotage = cursor.rowcount
            print(f"✅ Migrados {migrated_cabotage} registros de cabotajes")
            
            # Eliminar tablas antiguas
            cursor.execute('DROP TABLE traversing')
            cursor.execute('DROP TABLE cabotage')
            
            # Renombrar tablas nuevas
            cursor.execute('ALTER TABLE traversing_new RENAME TO traversing')
            cursor.execute('ALTER TABLE cabotage_new RENAME TO cabotage')
            
            # Verificar que processed_files existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_files'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE processed_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL UNIQUE,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        traversing_count INTEGER DEFAULT 0,
                        cabotage_count INTEGER DEFAULT 0
                    )
                ''')
                print("✅ Tabla 'processed_files' creada")
            
            conn.commit()
            print("✅ Migración completada exitosamente")
            return True
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        print(f"💾 Backup disponible en: {backup_path}")
        return False


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else ".data/extraction.db"
    
    print("="*60)
    print("MIGRACIÓN DE BASE DE DATOS")
    print("="*60)
    print(f"Base de datos: {db_path}")
    print()
    
    success = migrate_database(db_path)
    
    if success:
        print()
        print("="*60)
        print("✅ MIGRACIÓN EXITOSA")
        print("="*60)
        sys.exit(0)
    else:
        print()
        print("="*60)
        print("❌ MIGRACIÓN FALLIDA")
        print("="*60)
        sys.exit(1)
