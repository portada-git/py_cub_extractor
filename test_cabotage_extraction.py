#!/usr/bin/env python3
"""
Script para probar la extracción de cabotaje
"""
from pathlib import Path
from utils.utils import extract_entradas_cabotaje

# Buscar un archivo _C_ de 1852
data_dir = Path(".data/Nuevo/1852")
cabotage_files = sorted(data_dir.rglob("*_C_*.txt"))

if not cabotage_files:
    print("❌ No cabotage files found")
    exit(1)

print(f"🧪 Testing cabotage extraction")
print(f"Found {len(cabotage_files)} cabotage files")
print()

# Probar con el primer archivo
test_file = cabotage_files[0]
print(f"📄 Testing with: {test_file.name}")
print()

with open(test_file, encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"File size: {len(content)} characters")
print()

# Extraer cabotajes
lines = extract_entradas_cabotaje(content)

print(f"📊 Extracted {len(lines)} cabotage lines")
print()

if lines:
    print("First 5 lines:")
    for i, line in enumerate(lines[:5], 1):
        print(f"{i}. {line['info_text'][:80]}...")
else:
    print("⚠️  No cabotage lines found!")
    print()
    print("File content (first 500 chars):")
    print(content[:500])
