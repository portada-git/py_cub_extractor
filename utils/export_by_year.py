#!/usr/bin/env python3
"""
Script para exportar datos por año desde la base de datos
Genera JSON y CSV para travesías y cabotajes
"""
import json
import csv
from pathlib import Path
from utils.db import ExtractionDB


def export_year_from_db(year, output_dir):
    """Exporta un año completo desde la BD"""
    db = ExtractionDB()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📊 EXPORTING YEAR {year}")
    print("="*70)
    
    # Travesías
    traversing = db.get_traversing_by_year(year)
    if traversing:
        # JSON
        json_file = output_path / f"{year}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing to {json_file.name}")
        
        # CSV
        csv_file = output_path / f"{year}_traversing.csv"
        _export_to_csv(csv_file, traversing)
        print(f"✅ Exported {len(traversing)} traversing to {csv_file.name}")
    else:
        print(f"⚠️  No traversing data for year {year}")
    
    # Cabotajes
    cabotage = db.get_cabotage_by_year(year)
    if cabotage:
        # JSON
        json_file = output_path / f"{year}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage to {json_file.name}")
        
        # CSV
        csv_file = output_path / f"{year}_cabotage.csv"
        _export_to_csv(csv_file, cabotage)
        print(f"✅ Exported {len(cabotage)} cabotage to {csv_file.name}")
    else:
        print(f"⚠️  No cabotage data for year {year}")
    
    print()


def _export_to_csv(csv_file, data):
    """Exporta datos a CSV"""
    if not data:
        return
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        # Obtener todas las claves
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())
        
        fieldnames = sorted(list(all_keys))
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for row in data:
            row_copy = row.copy()
            # Convertir cargo_list de JSON a string
            if isinstance(row_copy.get('cargo_list'), str):
                try:
                    cargo_list = json.loads(row_copy['cargo_list'])
                    row_copy['cargo_list'] = ', '.join(str(x) for x in cargo_list)
                except:
                    pass
            writer.writerow(row_copy)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python utils/export_by_year.py <year> <output_dir>")
        print("\nExample:")
        print("  python utils/export_by_year.py 1852 .data/output")
        sys.exit(1)
    
    year = sys.argv[1]
    output_dir = sys.argv[2]
    
    export_year_from_db(year, output_dir)
