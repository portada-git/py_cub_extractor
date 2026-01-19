#!/usr/bin/env python3
"""
Export data from database to JSON and CSV formats
"""
import json
import csv
from pathlib import Path


def export_year(db, year, output_dir):
    """Exporta un año completo a JSON y CSV"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Exportar travesias
    travesias = db.get_traversing_by_year(year)
    if travesias:
        # JSON
        json_file = output_path / f"{year}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(travesias, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = output_path / f"{year}_traversing.csv"
        if travesias:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=travesias[0].keys())
                writer.writeheader()
                writer.writerows(travesias)
    
    # Exportar cabotajes
    cabotajes = db.get_cabotage_by_year(year)
    if cabotajes:
        # JSON
        json_file = output_path / f"{year}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotajes, f, ensure_ascii=False, indent=2)
        
        # CSV
        csv_file = output_path / f"{year}_cabotage.csv"
        if cabotajes:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cabotajes[0].keys())
                writer.writeheader()
                writer.writerows(cabotajes)
