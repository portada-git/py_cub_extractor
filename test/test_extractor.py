#!/usr/bin/env python3
"""
Test simple para la opción 5
"""
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractor import Extractor

def test_single_year():
    """Test extrayendo solo 1852"""
    print("Testing extraction for year 1852...")
    
    input_dir = ".data/Nuevo"
    output_dir = ".data/test_output"
    
    extractor = Extractor(input_dir, output_dir, max_workers=4)
    result = extractor.extract_year("1852")
    
    print(f"\nResult: {result}")
    
    # Verificar archivos generados
    output_path = Path(output_dir)
    files = list(output_path.glob("1852_*"))
    print(f"\nGenerated files: {len(files)}")
    for f in sorted(files):
        size = f.stat().st_size / 1024  # KB
        print(f"  {f.name}: {size:.1f} KB")

if __name__ == "__main__":
    test_single_year()
