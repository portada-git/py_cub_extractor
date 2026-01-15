#!/usr/bin/env python3
"""
Extractor profesional para travesías y cabotajes
Procesa por año, genera 4 archivos por año (2 JSON + 2 CSV)
"""
import json
import csv
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.utils import read_txt_files_recursively, catch_news_fragment, extract_entradas_cabotaje
from utils.utils import compute_important_dates
from llm_service.llm_openai import extract_structured_data_with_openai, extract_news_list_with_openai
from llm_service.llm_openai import extract_cabotaje_data_with_openai, get_token_usage, reset_token_usage


class Extractor:
    def __init__(self, input_dir, output_dir, max_workers=8):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        traversing_data = []
        cabotage_data = []
        
        # Encontrar todos los archivos del año
        all_files = sorted(year_dir.rglob("*.txt"))
        self.logger.info(f"Found {len(all_files)} files for year {year}")
        
        for file_path in all_files:
            filename = file_path.name
            is_traversing = "_V_" in filename
            is_cabotage = "_C_" in filename
            
            if not (is_traversing or is_cabotage):
                continue
            
            date_file = file_path.stem[:10]
            
            try:
                with open(file_path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if is_traversing:
                    self._process_traversing(content, date_file, traversing_data)
                
                if is_cabotage:
                    self._process_cabotage(content, date_file, cabotage_data)
                    
            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}")
        
        # Guardar resultados
        self._save_results(year, traversing_data, cabotage_data)
        
        usage = get_token_usage()
        self.logger.info(f"Year {year} completed: {len(traversing_data)} traversing, {len(cabotage_data)} cabotage")
        self.logger.info(f"Tokens used: {usage['total_tokens']:,}")
        
        return {
            'year': year,
            'traversing': len(traversing_data),
            'cabotage': len(cabotage_data),
            'tokens': usage['total_tokens']
        }
    
    def _process_traversing(self, content, date_file, results):
        """Procesa fragmentos de travesía"""
        try:
            fragments = catch_news_fragment(content)
            
            for fragment in fragments:
                news_delimited = extract_news_list_with_openai(fragment['info_text']).split("###")
                
                for news in news_delimited[1:len(news_delimited)-1]:
                    try:
                        row = extract_structured_data_with_openai(news)
                        
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
                    except Exception as e:
                        self.logger.debug(f"Error extracting news: {e}")
        except Exception as e:
            self.logger.debug(f"Error processing traversing: {e}")
    
    def _process_cabotage(self, content, date_file, results):
        """Procesa secciones de cabotaje"""
        try:
            sections = extract_entradas_cabotaje(content)
            
            for section in sections:
                lines = [l.strip() for l in section['info_text'].split('\n')
                        if l.strip() and not l.strip().startswith('ENTRADAS')]
                
                for line in lines:
                    if len(line) < 10 or line.isupper():
                        continue
                    
                    try:
                        row = extract_cabotaje_data_with_openai(line)
                        
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
                    except Exception as e:
                        self.logger.debug(f"Error extracting cabotage: {e}")
        except Exception as e:
            self.logger.debug(f"Error processing cabotage: {e}")
    
    def _save_results(self, year, traversing_data, cabotage_data):
        """Guarda resultados en JSON y CSV"""
        base_name = f"{year}"
        
        # Traversing
        if traversing_data:
            json_file = self.output_dir / f"{base_name}_traversing.json"
            csv_file = self.output_dir / f"{base_name}_traversing.csv"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(traversing_data, f, ensure_ascii=False, indent=2)
            
            self._save_csv(csv_file, traversing_data)
            self.logger.info(f"Saved traversing: {json_file}")
        
        # Cabotage
        if cabotage_data:
            json_file = self.output_dir / f"{base_name}_cabotage.json"
            csv_file = self.output_dir / f"{base_name}_cabotage.csv"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(cabotage_data, f, ensure_ascii=False, indent=2)
            
            self._save_csv(csv_file, cabotage_data)
            self.logger.info(f"Saved cabotage: {json_file}")
    
    def _save_csv(self, csv_file, data):
        """Guarda datos en CSV"""
        if not data:
            return
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader()
            
            for row in data:
                row_copy = row.copy()
                if isinstance(row_copy.get('cargo_list'), list):
                    row_copy['cargo_list'] = ', '.join(str(x) for x in row_copy['cargo_list'])
                writer.writerow(row_copy)
    
    def extract_all_years(self):
        """Extrae todos los años disponibles"""
        self.logger.info(f"Starting extraction from {self.input_dir}")
        
        years = sorted([d.name for d in self.input_dir.iterdir() if d.is_dir() and d.name.isdigit()])
        self.logger.info(f"Found years: {years}")
        
        results = []
        for year in years:
            result = self.extract_year(year)
            if result:
                results.append(result)
        
        self.logger.info("="*80)
        self.logger.info("EXTRACTION COMPLETED")
        self.logger.info("="*80)
        for r in results:
            self.logger.info(f"Year {r['year']}: {r['traversing']} traversing, {r['cabotage']} cabotage, {r['tokens']:,} tokens")
        
        return results
