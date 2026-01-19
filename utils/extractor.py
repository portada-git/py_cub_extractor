#!/usr/bin/env python3
"""
Extractor profesional para travesías y cabotajes
Procesa por año con múltiples hilos (16 por defecto)
Almacena en SQLite para reutilización
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue

from utils.utils import catch_news_fragment, extract_entradas_cabotaje
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
    
    def extract_year(self, year):
        """Extrae travesías y cabotajes para un año específico"""
        self.logger.info(f"Starting extraction for year {year}")
        reset_token_usage()
        
        year_dir = self.input_dir / str(year)
        if not year_dir.exists():
            self.logger.error(f"Year directory not found: {year_dir}")
            return None
        
        # Cola para resultados (thread-safe)
        results_queue = Queue()
        
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
        
        # Procesar archivos con hilos (solo extracción, sin guardar)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_file, f): f for f in files_to_process}
            
            processed_count = 0
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    trav_results, cab_results = future.result()
                    
                    # Enviar resultados a la cola (thread-safe)
                    results_queue.put((file_path, trav_results, cab_results))
                    
                    processed_count += 1
                    self.logger.debug(f"Processed {file_path.name}: {len(trav_results)} traversing, {len(cab_results)} cabotage")
                except Exception as e:
                    self.logger.error(f"Error processing {file_path.name}: {e}")
        
        # Guardar todos los resultados en la base de datos (main thread - thread-safe)
        traversing_count = 0
        cabotage_count = 0
        
        self.logger.info(f"Queue size before processing: {results_queue.qsize()}")
        
        while not results_queue.empty():
            file_path, trav_results, cab_results = results_queue.get()
            
            self.logger.debug(f"Processing queue item: {file_path.name} - {len(trav_results)} trav, {len(cab_results)} cab")
            
            # Guardar travesías
            for row in trav_results:
                if not row.get('parsed_text'):
                    self.logger.warning(f"Missing parsed_text in traversing row from {file_path.name}")
                    continue
                saved = self.db.save_traversing(row)
                if saved:
                    traversing_count += 1
                else:
                    self.logger.debug(f"Failed to save traversing entry (likely duplicate): {row.get('parsed_text', 'NO PARSED_TEXT')[:50]}")
            
            # Guardar cabotajes
            for row in cab_results:
                if not row.get('parsed_text'):
                    self.logger.warning(f"Missing parsed_text in cabotage row from {file_path.name}")
                    continue
                saved = self.db.save_cabotage(row)
                if saved:
                    cabotage_count += 1
                else:
                    self.logger.debug(f"Failed to save cabotage entry (likely duplicate): {row.get('parsed_text', 'NO PARSED_TEXT')[:50]}")
            
            # Marcar archivo como procesado
            self.db.mark_file_processed(file_path, len(trav_results), len(cab_results))
        
        self.logger.info(f"Saved to database: {traversing_count} traversing, {cabotage_count} cabotage")
        
        tokens = get_token_usage()
        self.logger.info(f"Year {year} completed: {traversing_count} traversing saved, {cabotage_count} cabotage saved, {tokens:,} tokens")
        
        return {
            'year': year,
            'traversing': traversing_count,
            'cabotage': cabotage_count,
            'tokens': tokens,
            'processed': processed_count
        }
    
    def _process_file(self, file_path):
        """Procesa un archivo individual (ejecutado en hilo)"""
        traversing_results = []
        cabotage_results = []
        
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Procesar según el tipo de archivo
            if "_V_" in file_path.name:
                # Archivo de travesías
                self._process_traversing(content, file_path, traversing_results)
            elif "_C_" in file_path.name:
                # Archivo de cabotajes
                self._process_cabotage(content, file_path, cabotage_results)
        
        except Exception as e:
            self.logger.error(f"Error reading {file_path.name}: {e}")
        
        return traversing_results, cabotage_results
    
    def _process_traversing(self, content, file_path, results):
        """Procesa travesías del archivo"""
        try:
            # Llamar al LLM con el contenido completo
            llm_response = extract_structured_data_with_openai(content)
            
            # El LLM retorna: {"files": [...], "publication_date": "...", "entries": [...]}
            if llm_response and isinstance(llm_response, dict):
                entries = llm_response.get('entries', [])
                
                for entry in entries:
                    if entry and isinstance(entry, dict) and entry.get('parsed_text'):
                        # Asegurar que tiene el nombre del archivo
                        if not entry.get('files'):
                            entry['files'] = file_path.name
                        # Asegurar que travel_arrival_date es "La Habana" para travesías
                        if not entry.get('travel_arrival_date'):
                            entry['travel_arrival_date'] = 'La Habana'
                        results.append(entry)
                    else:
                        self.logger.debug(f"Empty or invalid entry from LLM for traversing")
            else:
                self.logger.debug(f"Empty response from LLM for traversing")
        except Exception as e:
            self.logger.error(f"Error processing traversing: {e}")
    
    def _process_cabotage(self, content, file_path, results):
        """Procesa cabotajes del archivo"""
        try:
            # Llamar al LLM con el contenido completo
            llm_response = extract_cabotaje_data_with_openai(content)
            
            # El LLM retorna: {"files": [...], "publication_date": "...", "entries": [...]}
            if llm_response and isinstance(llm_response, dict):
                entries = llm_response.get('entries', [])
                
                for entry in entries:
                    if entry and isinstance(entry, dict) and entry.get('parsed_text'):
                        # Asegurar que tiene el nombre del archivo
                        if not entry.get('files'):
                            entry['files'] = file_path.name
                        results.append(entry)
                    else:
                        self.logger.debug(f"Empty or invalid entry from LLM for cabotage")
            else:
                self.logger.debug(f"Empty response from LLM for cabotage")
        except Exception as e:
            self.logger.error(f"Error processing cabotage: {e}")
    
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
        
        self.logger.info("=" * 80)
        self.logger.info("EXTRACTION COMPLETED")
        self.logger.info("=" * 80)
        total_tokens = 0
        for r in results:
            self.logger.info(f"Year {r['year']}: {r['traversing']} traversing, {r['cabotage']} cabotage, {r['tokens']:,} tokens, {r['processed']} files processed")
            total_tokens += r['tokens']
        self.logger.info(f"TOTAL TOKENS USED: {total_tokens:,}")
        
        return results
