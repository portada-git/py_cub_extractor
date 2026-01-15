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
                    source_file TEXT NOT NULL,
                    publication_day TEXT,
                    travel_duration INTEGER,
                    travel_departure_port TEXT,
                    ship_type TEXT,
                    ship_name TEXT,
                    ship_tons_capacity TEXT,
                    ship_tons_units TEXT,
                    master_role TEXT,
                    master_name TEXT,
                    cargo_list TEXT,
                    raw_text TEXT NOT NULL,
                    departure_date TEXT,
                    arrival_date TEXT,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(raw_text, source_file)
                )
            ''')
            
            # Tabla para cabotajes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cabotage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT NOT NULL,
                    publication_day TEXT,
                    travel_duration INTEGER,
                    travel_departure_port TEXT,
                    ship_type TEXT,
                    ship_name TEXT,
                    ship_tons_capacity TEXT,
                    ship_tons_units TEXT,
                    master_role TEXT,
                    master_name TEXT,
                    cargo_list TEXT,
                    raw_text TEXT NOT NULL,
                    departure_date TEXT,
                    arrival_date TEXT,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(raw_text, source_file)
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
            
            try:
                cursor.execute('''
                    INSERT INTO traversing (
                        source_file, publication_day, travel_duration, travel_departure_port,
                        ship_type, ship_name, ship_tons_capacity, ship_tons_units,
                        master_role, master_name, cargo_list, raw_text,
                        departure_date, arrival_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('source_file'),
                    data.get('publication_day'),
                    data.get('travel_duration'),
                    data.get('travel_departure_port'),
                    data.get('ship_type'),
                    data.get('ship_name'),
                    data.get('ship_tons_capacity'),
                    data.get('ship_tons_units'),
                    data.get('master_role'),
                    data.get('master_name'),
                    cargo_json,
                    data.get('raw_text'),
                    data.get('departure_date'),
                    data.get('arrival_date')
                ))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Ya existe
                return False
    
    def save_cabotage(self, data):
        """Guarda una entrada de cabotaje"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cargo_json = json.dumps(data.get('cargo_list', []))
            
            try:
                cursor.execute('''
                    INSERT INTO cabotage (
                        source_file, publication_day, travel_duration, travel_departure_port,
                        ship_type, ship_name, ship_tons_capacity, ship_tons_units,
                        master_role, master_name, cargo_list, raw_text,
                        departure_date, arrival_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('source_file'),
                    data.get('publication_day'),
                    data.get('travel_duration'),
                    data.get('travel_departure_port'),
                    data.get('ship_type'),
                    data.get('ship_name'),
                    data.get('ship_tons_capacity'),
                    data.get('ship_tons_units'),
                    data.get('master_role'),
                    data.get('master_name'),
                    cargo_json,
                    data.get('raw_text'),
                    data.get('departure_date'),
                    data.get('arrival_date')
                ))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Ya existe
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
                SELECT * FROM traversing WHERE source_file LIKE ?
                ORDER BY source_file
            ''', (f'{year}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_year(self, year):
        """Obtiene todos los cabotajes de un año"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM cabotage WHERE source_file LIKE ?
                ORDER BY source_file
            ''', (f'{year}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_traversing_by_month(self, year, month):
        """Obtiene travesías de un mes específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            pattern = f'{year}_{month:02d}%'
            cursor.execute('''
                SELECT * FROM traversing WHERE source_file LIKE ?
                ORDER BY source_file
            ''', (pattern,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_month(self, year, month):
        """Obtiene cabotajes de un mes específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            pattern = f'{year}_{month:02d}%'
            cursor.execute('''
                SELECT * FROM cabotage WHERE source_file LIKE ?
                ORDER BY source_file
            ''', (pattern,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_traversing_by_day(self, year, month, day):
        """Obtiene travesías de un día específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            pattern = f'{year}_{month:02d}_{day:02d}%'
            cursor.execute('''
                SELECT * FROM traversing WHERE source_file LIKE ?
                ORDER BY source_file
            ''', (pattern,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_day(self, year, month, day):
        """Obtiene cabotajes de un día específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            pattern = f'{year}_{month:02d}_{day:02d}%'
            cursor.execute('''
                SELECT * FROM cabotage WHERE source_file LIKE ?
                ORDER BY source_file
            ''', (pattern,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_traversing_by_port(self, port_name):
        """Obtiene travesías de un puerto específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM traversing WHERE travel_departure_port LIKE ?
                ORDER BY source_file
            ''', (f'%{port_name}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_port(self, port_name):
        """Obtiene cabotajes de un puerto específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM cabotage WHERE travel_departure_port LIKE ?
                ORDER BY source_file
            ''', (f'%{port_name}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_traversing_by_ship(self, ship_name):
        """Obtiene travesías de un barco específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM traversing WHERE ship_name LIKE ?
                ORDER BY source_file
            ''', (f'%{ship_name}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_ship(self, ship_name):
        """Obtiene cabotajes de un barco específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM cabotage WHERE ship_name LIKE ?
                ORDER BY source_file
            ''', (f'%{ship_name}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_traversing_by_master(self, master_name):
        """Obtiene travesías de un capitán específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM traversing WHERE master_name LIKE ?
                ORDER BY source_file
            ''', (f'%{master_name}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cabotage_by_master(self, master_name):
        """Obtiene cabotajes de un capitán específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM cabotage WHERE master_name LIKE ?
                ORDER BY source_file
            ''', (f'%{master_name}%',))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_ports(self):
        """Obtiene lista de todos los puertos únicos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT travel_departure_port FROM traversing
                WHERE travel_departure_port IS NOT NULL
                UNION
                SELECT DISTINCT travel_departure_port FROM cabotage
                WHERE travel_departure_port IS NOT NULL
                ORDER BY travel_departure_port
            ''')
            return [row[0] for row in cursor.fetchall()]
    
    def get_all_ships(self):
        """Obtiene lista de todos los barcos únicos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT ship_name FROM traversing
                WHERE ship_name IS NOT NULL
                UNION
                SELECT DISTINCT ship_name FROM cabotage
                WHERE ship_name IS NOT NULL
                ORDER BY ship_name
            ''')
            return [row[0] for row in cursor.fetchall()]
    
    def get_all_masters(self):
        """Obtiene lista de todos los capitanes únicos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT master_name FROM traversing
                WHERE master_name IS NOT NULL
                UNION
                SELECT DISTINCT master_name FROM cabotage
                WHERE master_name IS NOT NULL
                ORDER BY master_name
            ''')
            return [row[0] for row in cursor.fetchall()]
    
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
