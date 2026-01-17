#!/usr/bin/env python3
"""
Script para exportar todos los años a la vez
"""
from utils.export_data import export_year
from utils.db import ExtractionDB


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    print("="*80)
    print("EXPORTADOR DE TODOS LOS AÑOS")
    print("="*80)
    print()
    
    # Crear conexión a BD
    db = ExtractionDB()
    
    # Obtener estadísticas para saber qué años hay
    stats = db.get_stats()
    print(f"📊 Estadísticas de la BD:")
    print(f"  • Travesías: {stats['traversing']:,}")
    print(f"  • Cabotajes: {stats['cabotage']:,}")
    print(f"  • Archivos procesados: {stats['files_processed']:,}")
    print()
    
    # Obtener años únicos de la BD
    with __import__('sqlite3').connect(".data/extraction.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT substr(source_file, 1, 4) as year 
            FROM traversing 
            UNION 
            SELECT DISTINCT substr(source_file, 1, 4) as year 
            FROM cabotage 
            ORDER BY year
        ''')
        years = [row[0] for row in cursor.fetchall()]
    
    if not years:
        print("❌ No hay datos en la base de datos")
        sys.exit(1)
    
    print(f"📅 Años encontrados: {', '.join(years)}")
    print()
    print("Exportando todos los años...")
    print()
    
    # Exportar cada año
    for year in years:
        print(f"  Exportando {year}...", end=" ", flush=True)
        try:
            export_year(db, year, ".data/results")
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("="*80)
    print("✅ EXPORTACIÓN COMPLETADA")
    print("="*80)
    print(f"Archivos guardados en: .data/results/")
    print()
    print("Archivos generados:")
    for year in years:
        print(f"  • {year}_traversing.json / .csv")
        print(f"  • {year}_cabotage.json / .csv")
