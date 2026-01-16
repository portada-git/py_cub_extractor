#!/usr/bin/env python3
"""
Script para probar la extracción de enero 1852 (solo 31 archivos)
Rápido para verificar que cabotaje funciona
"""
from utils.extractor import Extractor

input_dir = ".data/Nuevo"
output_dir = ".data/output"
year = "1852"
month = 1

print(f"\n🧪 Testing extraction for {year}-{month:02d}")
print("="*70)

extractor = Extractor(input_dir, output_dir, max_workers=16)
result = extractor.extract_month(year, month)

if result:
    print(f"\n✅ RESULTS:")
    print(f"  Traversing: {result['traversing']}")
    print(f"  Cabotage: {result['cabotage']}")
    print(f"  Total: {result['traversing'] + result['cabotage']}")
    print(f"  Files processed: {result['processed']}")
    print(f"  Tokens: {result['tokens']:,}")
    
    if result['cabotage'] > 0:
        print(f"\n✅ CABOTAGE EXTRACTION WORKING!")
    else:
        print(f"\n❌ CABOTAGE STILL NOT WORKING")
else:
    print("❌ Extraction failed")
