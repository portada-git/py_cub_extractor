#!/usr/bin/env python3
"""
Script para extraer solo el año 1852
"""
from utils.extractor import Extractor
from utils.db.check_missing import check_by_year
from pathlib import Path


def main():
    input_dir = ".data/Nuevo"
    output_dir = ".data/output"
    year = "1852"
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    print(f"\n🚀 EXTRACTING YEAR {year}")
    print("="*70)
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print()
    
    # Mostrar estado actual
    print("📊 CURRENT STATUS:")
    check_by_year(input_dir)
    
    # Procesar año
    print("\n" + "="*70)
    print(f"🔄 STARTING EXTRACTION FOR {year}")
    print("="*70)
    print("Processing with 16 threads...")
    print()
    
    extractor = Extractor(input_dir, output_dir, max_workers=16)
    result = extractor.extract_year(year)
    
    # Resumen final
    print("\n" + "="*70)
    print(f"✅ EXTRACTION COMPLETE FOR {year}")
    print("="*70)
    
    if result:
        print(f"\n📊 RESULTS:")
        print(f"  Traversing entries: {result['traversing']:,}")
        print(f"  Cabotage entries: {result['cabotage']:,}")
        print(f"  Total entries: {result['traversing'] + result['cabotage']:,}")
        print(f"  Files processed: {result['processed']}")
        print(f"  Tokens used: {result['tokens']:,}")
    
    print("\n💡 Next steps:")
    print("   1. Run: python3 main.py → Option 6 to verify all files processed")
    print("   2. Run: python3 main.py → Option 8.1 to export data")
    print("   3. Run: python3 main.py → Option 7 to see database statistics")


if __name__ == "__main__":
    main()
