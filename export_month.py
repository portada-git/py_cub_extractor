#!/usr/bin/env python3
"""
Script para exportar un mes específico
"""
from utils.export_data import export_month
from utils.db import ExtractionDB


if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("EXPORTADOR DE MES")
    print("="*80)
    print()
    
    # Solicitar entrada
    year = input("Ingresa el año (ej: 1852): ").strip()
    month = input("Ingresa el mes (1-12): ").strip()
    
    try:
        year = int(year)
        month = int(month)
        
        if month < 1 or month > 12:
            print("❌ Mes inválido. Debe estar entre 1 y 12")
            sys.exit(1)
        
        # Crear conexión a BD
        db = ExtractionDB()
        
        print()
        print(f"Exportando {year}-{month:02d}...")
        print()
        
        # Exportar mes
        export_month(db, year, month, ".data/results")
        
        print()
        print("="*80)
        print("✅ EXPORTACIÓN COMPLETADA")
        print("="*80)
        print(f"Archivos guardados en: .data/results/")
        print(f"  • {year}_{month:02d}_traversing.json")
        print(f"  • {year}_{month:02d}_traversing.csv")
        print(f"  • {year}_{month:02d}_cabotage.json")
        print(f"  • {year}_{month:02d}_cabotage.csv")
        
    except ValueError:
        print("❌ Entrada inválida")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
