#!/usr/bin/env python3
"""
Migración de esquema para alinear la BD con los prompts mejorados
"""
import sqlite3
from pathlib import Path


def migrate_database(db_path=".data/extraction.db"):
    """Migra la BD al nuevo esquema"""
    db_path = Path(db_path)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        print("=" * 70)
        print("INICIANDO MIGRACIÓN DE ESQUEMA")
        print("=" * 70)
        
        # Crear tablas nuevas con esquema correcto
        print("\n1. Creando tablas nuevas con esquema correcto...")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traversing_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                files TEXT,
                publication_date TEXT,
                publication_day TEXT,
                travel_arrival_date TEXT,
                travel_departure_port TEXT,
                travel_departure_date TEXT,
                travel_port_of_call_list TEXT,
                travel_duration_value INTEGER,
                travel_duration_unit TEXT,
                ship_type TEXT,
                ship_flag TEXT,
                ship_name TEXT,
                ship_tons_capacity INTEGER,
                ship_tons_unit TEXT,
                master_role TEXT,
                master_name TEXT,
                crew_number INTEGER,
                passenger_account INTEGER,
                cargo_list TEXT,
                quarantine BOOLEAN,
                forced_arrival BOOLEAN,
                parsed_text TEXT,
                obs TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cabotage_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                files TEXT,
                publication_date TEXT,
                publication_day TEXT,
                travel_arrival_date TEXT,
                travel_departure_port TEXT,
                travel_departure_date TEXT,
                travel_port_of_call_list TEXT,
                travel_duration_value INTEGER,
                travel_duration_unit TEXT,
                ship_type TEXT,
                ship_flag TEXT,
                ship_name TEXT,
                master_role TEXT,
                master_name TEXT,
                crew_number INTEGER,
                passenger_account INTEGER,
                cargo_list TEXT,
                quarantine BOOLEAN,
                forced_arrival BOOLEAN,
                parsed_text TEXT,
                obs TEXT
            )
        ''')
        
        print("   ✅ Tablas nuevas creadas")
        
        # Migrar datos de traversing
        print("\n2. Migrando datos de traversing...")
        cursor.execute('''
            INSERT INTO traversing_new (
                publication_day, travel_arrival_date, travel_departure_port,
                travel_duration_value, travel_duration_unit, ship_type, ship_flag,
                ship_name, ship_tons_capacity, ship_tons_unit, master_role,
                master_name, crew_number, passenger_account, cargo_list,
                quarantine, forced_arrival, parsed_text, obs, files
            )
            SELECT
                publication_day, arrival_date, travel_departure_port,
                travel_duration_value, travel_duration_unit, ship_type, ship_flag,
                ship_name, ship_tons_capacity, ship_tons_unit, master_role,
                master_name, crew_number, passenger_account, cargo_list,
                quarantine, forced_arrival, parsed_text, obs, source_file
            FROM traversing
        ''')
        trav_count = cursor.rowcount
        print(f"   ✅ {trav_count} registros migrados")
        
        # Migrar datos de cabotage
        print("\n3. Migrando datos de cabotage...")
        cursor.execute('''
            INSERT INTO cabotage_new (
                publication_day, travel_arrival_date, travel_departure_port,
                travel_duration_value, travel_duration_unit, ship_type, ship_flag,
                ship_name, master_role, master_name, crew_number, passenger_account,
                cargo_list, quarantine, forced_arrival, parsed_text, obs, files
            )
            SELECT
                publication_day, arrival_date, travel_departure_port,
                travel_duration_value, travel_duration_unit, ship_type, ship_flag,
                ship_name, master_role, master_name, crew_number, passenger_account,
                cargo_list, quarantine, forced_arrival, parsed_text, obs, source_file
            FROM cabotage
        ''')
        cab_count = cursor.rowcount
        print(f"   ✅ {cab_count} registros migrados")
        
        # Eliminar tablas antiguas
        print("\n4. Eliminando tablas antiguas...")
        cursor.execute('DROP TABLE traversing')
        cursor.execute('DROP TABLE cabotage')
        print("   ✅ Tablas antiguas eliminadas")
        
        # Renombrar tablas nuevas
        print("\n5. Renombrando tablas nuevas...")
        cursor.execute('ALTER TABLE traversing_new RENAME TO traversing')
        cursor.execute('ALTER TABLE cabotage_new RENAME TO cabotage')
        print("   ✅ Tablas renombradas")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"Traversing: {trav_count} registros")
        print(f"Cabotage: {cab_count} registros")
        print("=" * 70)


if __name__ == "__main__":
    migrate_database()
