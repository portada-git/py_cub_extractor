#!/usr/bin/env python3
"""
Script para contar entradas en todos los JSON de resultados
"""
import json
from pathlib import Path


if __name__ == "__main__":
    results_dir = Path(".data/results")
    
    print("="*80)
    print("CONTEO DE ENTRADAS EN JSON")
    print("="*80)
    print()
    
    # Encontrar todos los JSON
    json_files = sorted(results_dir.glob("*.json"))
    
    if not json_files:
        print("❌ No hay archivos JSON en .data/results/")
        exit(1)
    
    # Agrupar por tipo (traversing/cabotage)
    traversing_files = [f for f in json_files if 'traversing' in f.name]
    cabotage_files = [f for f in json_files if 'cabotage' in f.name]
    
    total_traversing = 0
    total_cabotage = 0
    
    print("📊 TRAVESÍAS")
    print("-" * 80)
    for json_file in traversing_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = len(data) if isinstance(data, list) else 1
            total_traversing += count
            print(f"  {json_file.name:40} {count:6,} entradas")
        except Exception as e:
            print(f"  {json_file.name:40} ❌ Error: {e}")
    
    print()
    print("📊 CABOTAJES")
    print("-" * 80)
    for json_file in cabotage_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = len(data) if isinstance(data, list) else 1
            total_cabotage += count
            print(f"  {json_file.name:40} {count:6,} entradas")
        except Exception as e:
            print(f"  {json_file.name:40} ❌ Error: {e}")
    
    print()
    print("="*80)
    print("📈 TOTALES")
    print("="*80)
    print(f"  Travesías:  {total_traversing:,}")
    print(f"  Cabotajes:  {total_cabotage:,}")
    print(f"  TOTAL:      {total_traversing + total_cabotage:,}")
    print()
