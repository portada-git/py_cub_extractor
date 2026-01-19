#!/usr/bin/env python3
"""
Database module para almacenar extracciones en SQLite
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime


class ExtractionDB:
    def __init__(self, db_path=".data/extraction.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla para travesías
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traversing (
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
            
            # Tabla para cabotajes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cabotage (
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
            
            # Tabla para rastrear archivos procesados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL UNIQUE,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    traversing_count INTEGER DEFAULT 0,
                    cabotage_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    def save_traversing(self, data):
        """Guarda una entrada de travesía"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cargo_json = json.dumps(data.get('cargo_list', []))
            travel_port_of_call_list_json = json.dumps(data.get('travel_port_of_call_list', []))
            
            try:
                cursor.execute('''
                    INSERT INTO traversing (
                        files, publication_date, publication_day, travel_arrival_date,
                        travel_departure_port, travel_departure_date, travel_port_of_call_list,
                        travel_duration_value, travel_duration_unit, ship_type, ship_flag,
                        ship_name, ship_tons_capacity, ship_tons_unit, master_role,
                        master_name, crew_number, passenger_account, cargo_list,
                        quarantine, forced_arrival, parsed_text, obs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('files'),
                    data.get('publication_date'),
                    data.get('publication_day'),
                    data.get('travel_arrival_date'),
                    data.get('travel_departure_port'),
                    data.get('travel_departure_date'),
                    travel_port_of_call_list_json,
                    data.get('travel_duration_value'),
                    data.get('travel_duration_unit'),
                    data.get('ship_type'),
                    data.get('ship_flag'),
                    data.get('ship_name'),
                    data.get('ship_tons_capacity'),
                    data.get('ship_tons_unit'),
                    data.get('master_role'),
                    data.get('master_name'),
                    data.get('crew_number'),
                    data.get('passenger_account'),
                    cargo_json,
                    data.get('quarantine'),
                    data.get('forced_arrival'),
                    data.get('parsed_text'),
                    data.get('obs')
                ))
                conn.commit()
                return True
            except Exception as e:
                import logging
                logging.error(f"Error saving traversing entry: {e}")
                return False
    
    def save_cabotage(self, data):
        """Guarda una entrada de cabotaje"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cargo_json = json.dumps(data.get('cargo_list', []))
            travel_port_of_call_list_json = json.dumps(data.get('travel_port_of_call_list', []))
            
            try:
                cursor.execute('''
                    INSERT INTO cabotage (
                        files, publication_date, publication_day, travel_arrival_date,
                        travel_departure_port, travel_departure_date, travel_port_of_call_list,
                        travel_duration_value, travel_duration_unit, ship_type, ship_flag,
                        ship_name, master_role, master_name, crew_number, passenger_account,
                        cargo_list, quarantine, forced_arrival, parsed_text, obs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('files'),
                    data.get('publication_date'),
                    data.get('publication_day'),
                    data.get('travel_arrival_date'),
                    data.get('travel_departure_port'),
                    data.get('travel_departure_date'),
                    travel_port_of_call_list_json,
                    data.get('travel_duration_value'),
                    data.get('travel_duration_unit'),
                    data.get('ship_type'),
                    data.get('ship_flag'),
                    data.get('ship_name'),
                    data.get('master_role'),
                    data.get('master_name'),
                    data.get('crew_number'),
                    data.get('passenger_account'),
                    cargo_json,
                    data.get('quarantine'),
                    data.get('forced_arrival'),
                    data.get('parsed_text'),
                    data.get('obs')
                ))
                conn.commit()
                return True
            except Exception as e:
                import logging
                logging.error(f"Error saving cabotage entry: {e}")
                return False
    
    def mark_file_processed(self, file_path, traversing_count=0, cabotage_count=0):
        """Marca un archivo como procesado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO processed_files (file_path, traversing_count, cabotage_count)
                VALUES (?, ?, ?)
            ''', (str(file_path), traversing_count, cabotage_count))
            conn.commit()
    
    def is_file_processed(self, file_path):
        """Verifica si un archivo ya fue procesado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM processed_files WHERE file_path = ?', (str(file_path),))
            return cursor.fetchone() is not None
    
    def get_traversing_by_year(self, year):
        """Obtiene todas las travesías de un año"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM traversing WHERE publication_day LIKE ?
                ORDER BY publication_day
            ''', (f'{year}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_year(self, year):
        """Obtiene todos los cabotajes de un año"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM cabotage WHERE publication_day LIKE ?
                ORDER BY publication_day
            ''', (f'{year}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_year_data(self, year):
        """Elimina todos los datos de un año específico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Eliminar travesías del año
            cursor.execute('DELETE FROM traversing WHERE publication_day LIKE ?', (f'{year}%',))
            traversing_deleted = cursor.rowcount
            
            # Eliminar cabotajes del año
            cursor.execute('DELETE FROM cabotage WHERE publication_day LIKE ?', (f'{year}%',))
            cabotage_deleted = cursor.rowcount
            
            # Eliminar archivos procesados del año
            cursor.execute('DELETE FROM processed_files WHERE file_path LIKE ?', (f'%{year}%',))
            files_deleted = cursor.rowcount
            
            conn.commit()
            
            return {
                'traversing': traversing_deleted,
                'cabotage': cabotage_deleted,
                'files': files_deleted
            }
    
    def get_stats(self):
        """Obtiene estadísticas de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM traversing')
            traversing_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM cabotage')
            cabotage_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM processed_files')
            files_count = cursor.fetchone()[0]
            
            return {
                'traversing': traversing_count,
                'cabotage': cabotage_count,
                'files_processed': files_count
            }
