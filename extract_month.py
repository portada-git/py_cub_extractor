#!/usr/bin/env python3
"""
Script para extraer un mes específico
"""
from utils.extractor import Extractor


if __name__ == "__main__":
    import sys
    
    print("="*80)
    print("EXTRACTOR DE MES")
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
        
        # Crear extractor
        extractor = Extractor(
            input_dir=".data/Nuevo",
            output_dir=".data/output",
            max_workers=16
        )
        
        print()
        print(f"Extrayendo {year}-{month:02d}...")
        print()
        
        # Extraer mes
        result = extractor.extract_month(year, month)
        
        if result:
            print()
            print("="*80)
            print("✅ EXTRACCIÓN COMPLETADA")
            print("="*80)
            print(f"Travesías: {result['traversing']}")
            print(f"Cabotajes: {result['cabotage']}")
            print(f"Tokens usados: {result['tokens']:,}")
            print(f"Archivos procesados: {result['processed']}")
        
    except ValueError:
        print("❌ Entrada inválida")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
