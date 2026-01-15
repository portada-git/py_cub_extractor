#!/usr/bin/env python3
"""
Extractor profesional para travesías y cabotajes
Procesa por año con múltiples hilos (16 por defecto)
Almacena en SQLite para reutilización
"""
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from utils.utils import catch_news_fragment, extract_entradas_cabotaje
from utils.utils import compute_important_dates
from llm_service.llm_openai import extract_structured_data_with_openai
from llm_service.llm_openai import extract_cabotaje_data_with_openai, get_token_usage, reset_token_usage
from utils.db import ExtractionDB


class Extractor:
    def __init__(self, input_dir, output_dir, max_workers=16, db_path=".data/extraction.db"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Base de datos
        self.db = ExtractionDB(db_path)
        
        # Lock para sincronización de hilos
        self.lock = threading.Lock()
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
    def setup_logging(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.output_dir / f"extraction_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True
        )
    
    def extract_month(self, year, month):
        """Extrae travesías y cabotajes para un mes específico"""
        self.logger.info(f"Starting extraction for {year}-{month:02d}")
        reset_token_usage()
        
        month_dir = self.input_dir / str(year) / f"{month:02d}"
        if not month_dir.exists():
            self.logger.error(f"Month directory not found: {month_dir}")
            return None
        
        traversing_data = []
        cabotage_data = []
        
        # Encontrar todos los archivos del mes
        all_files = sorted(month_dir.glob("*.txt"))
        relevant_files = [f for f in all_files if "_V_" in f.name or "_C_" in f.name]
        
        # Filtrar solo archivos no procesados
        files_to_process = [f for f in relevant_files if not self.db.is_file_processed(f)]
        
        self.logger.info(f"Found {len(relevant_files)} files for {year}-{month:02d}")
        self.logger.info(f"Already processed: {len(relevant_files) - len(files_to_process)}")
        self.logger.info(f"To process: {len(files_to_process)}")
        
        if not files_to_process:
            self.logger.info(f"All files for {year}-{month:02d} already processed")
            return {
                'year': year,
                'month': month,
                'traversing': 0,
                'cabotage': 0,
                'tokens': 0,
                'processed': 0
            }
        
        # Procesar archivos con hilos
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_file, f): f for f in files_to_process}
            
            processed_count = 0
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    trav_results, cab_results = future.result()
                    
                    with self.lock:
                        traversing_data.extend(trav_results)
                        cabotage_data.extend(cab_results)
                        
                        # Marcar archivo como procesado
                        self.db.mark_file_processed(file_path, len(trav_results), len(cab_results))
                    
                    processed_count += 1
                    self.logger.debug(f"Processed {file_path.name}: {len(trav_results)} traversing, {len(cab_results)} cabotage")
                except Exception as e:
                    self.logger.error(f"Error processing {file_path.name}: {e}")
        
        tokens = get_token_usage()
        self.logger.info(f"{year}-{month:02d} completed: {len(traversing_data)} traversing, {len(cabotage_data)} cabotage, {tokens:,} tokens")
        
        return {
            'year': year,
            'month': month,
            'traversing': len(traversing_data),
            'cabotage': len(cabotage_data),
            'tokens': tokens,
            'processed': processed_count
        }
    
    def extract_year(self, year):
        """Extrae travesías y cabotajes para un año específico"""
        self.logger.info(f"Starting extraction for year {year}")
        reset_token_usage()
        
        year_dir = self.input_dir / str(year)
        if not year_dir.exists():
            self.logger.error(f"Year directory not found: {year_dir}")
            return None
        
        traversing_data = []
        cabotage_data = []
        
        # Encontrar todos los archivos del año
        all_files = sorted(year_dir.rglob("*.txt"))
        relevant_files = [f for f in all_files if "_V_" in f.name or "_C_" in f.name]
        
        # Filtrar solo archivos no procesados
        files_to_process = [f for f in relevant_files if not self.db.is_file_processed(f)]
        
        self.logger.info(f"Found {len(relevant_files)} files for year {year}")
        self.logger.info(f"Already processed: {len(relevant_files) - len(files_to_process)}")
        self.logger.info(f"To process: {len(files_to_process)}")
        
        if not files_to_process:
            self.logger.info(f"All files for year {year} already processed")
            return {
                'year': year,
                'traversing': 0,
                'cabotage': 0,
                'tokens': 0,
                'processed': 0
            }
        
        # Procesar archivos con hilos
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_file, f): f for f in files_to_process}
            
            processed_count = 0
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    trav_results, cab_results = future.result()
                    
                    with self.lock:
                        traversing_data.extend(trav_results)
                        cabotage_data.extend(cab_results)
                        
                        # Marcar archivo como procesado
                        self.db.mark_file_processed(file_path, len(trav_results), len(cab_results))
                    
                    processed_count += 1
                    self.logger.debug(f"Processed {file_path.name}: {len(trav_results)} traversing, {len(cab_results)} cabotage")
                except Exception as e:
                    self.logger.error(f"Error processing {file_path.name}: {e}")
        
        tokens = get_token_usage()
        self.logger.info(f"Year {year} completed: {len(traversing_data)} traversing, {len(cabotage_data)} cabotage, {tokens:,} tokens")
        
        return {
            'year': year,
            'traversing': len(traversing_data),
            'cabotage': len(cabotage_data),
            'tokens': tokens,
            'processed': processed_count
        }
    
    def _process_file(self, file_path):
        """Procesa un archivo individual (ejecutado en hilo)"""
        traversing_results = []
        cabotage_results = []
        date_file = file_path.stem[:10]
        
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if "_V_" in file_path.name:
                self._process_traversing(content, date_file, traversing_results)
            
            if "_C_" in file_path.name:
                self._process_cabotage(content, date_file, cabotage_results)
        
        except Exception as e:
            self.logger.error(f"Error reading {file_path.name}: {e}")
        
        return traversing_results, cabotage_results
    
    def _process_traversing(self, content, date_file, results):
        """Procesa líneas individuales de travesía"""
        try:
            lines = catch_news_fragment(content)
            
            for line_obj in lines:
                try:
                    row = extract_structured_data_with_openai(line_obj['info_text'])
                    
                    if row.get('raw_text'):
                        try:
                            departure_date, arrival_date = compute_important_dates(
                                date_file, row.get('travel_duration'), row.get('publication_day')
                            )
                            row['departure_date'] = departure_date
                            row['arrival_date'] = arrival_date
                        except:
                            row['departure_date'] = None
                            row['arrival_date'] = None
                        
                        row['source_file'] = date_file
                        results.append(row)
                        
                        # Guardar en base de datos
                        self.db.save_traversing(row)
                except Exception as e:
                    self.logger.debug(f"Error extracting traversing line: {e}")
        except Exception as e:
            self.logger.debug(f"Error processing traversing: {e}")
    
    def _process_cabotage(self, content, date_file, results):
        """Procesa líneas individuales de cabotaje"""
        try:
            lines = extract_entradas_cabotaje(content)
            
            for line_obj in lines:
                try:
                    row = extract_cabotaje_data_with_openai(line_obj['info_text'])
                    
                    if row.get('raw_text'):
                        try:
                            departure_date, arrival_date = compute_important_dates(
                                date_file, row.get('travel_duration'), row.get('publication_day')
                            )
                            row['departure_date'] = departure_date
                            row['arrival_date'] = arrival_date
                        except:
                            row['departure_date'] = None
                            row['arrival_date'] = None
                        
                        row['source_file'] = date_file
                        results.append(row)
                        
                        # Guardar en base de datos
                        self.db.save_cabotage(row)
                except Exception as e:
                    self.logger.debug(f"Error extracting cabotage line: {e}")
        except Exception as e:
            self.logger.debug(f"Error processing cabotage: {e}")
    
    def extract_all_years(self):
        """Extrae todos los años disponibles"""
        self.logger.info(f"Starting extraction from {self.input_dir}")
        
        years = sorted([d.name for d in self.input_dir.iterdir() if d.is_dir() and d.name.isdigit()])
        self.logger.info(f"Found years: {years}")
        
        results = []
        
        # Procesar años secuencialmente
        for year in years:
            result = self.extract_year(year)
            if result:
                results.append(result)
        
        self.logger.info("="*80)
        self.logger.info("EXTRACTION COMPLETED")
        self.logger.info("="*80)
        total_tokens = 0
        for r in results:
            self.logger.info(f"Year {r['year']}: {r['traversing']} traversing, {r['cabotage']} cabotage, {r['tokens']:,} tokens, {r['processed']} files processed")
            total_tokens += r['tokens']
        self.logger.info(f"TOTAL TOKENS USED: {total_tokens:,}")
        
        return results
