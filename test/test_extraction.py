#!/usr/bin/env python3
"""
Test simple para la opción 5 - con pocos archivos
"""
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.extractor import Extractor

def test_single_month():
    """Test extrayendo solo octubre de 1887 (mes con pocos archivos)"""
    print("Testing extraction for October 1887...")
    
    input_dir = ".data/Nuevo"
    output_dir = ".data/test_output"
    
    # Crear un directorio temporal con solo los archivos de octubre
    test_input = Path(".data/test_input")
    test_input.mkdir(exist_ok=True)
    
    # Copiar solo archivos de octubre 1887
    oct_dir = test_input / "1887" / "10"
    oct_dir.mkdir(parents=True, exist_ok=True)
    
    source_oct = Path(input_dir) / "1887" / "10"
    if source_oct.exists():
        for file in list(source_oct.glob("*.txt"))[:5]:  # Solo 5 archivos
            import shutil
            shutil.copy(file, oct_dir / file.name)
    
    print(f"Test input directory: {test_input}")
    print(f"Files copied: {len(list(oct_dir.glob('*.txt')))}")
    
    extractor = Extractor(str(test_input), output_dir, max_workers=2)
    result = extractor.extract_year("1887")
    
    print(f"\nResult: {result}")
    
    # Verificar archivos generados
    output_path = Path(output_dir)
    files = list(output_path.glob("1887_*"))
    print(f"\nGenerated files: {len(files)}")
    for f in sorted(files):
        size = f.stat().st_size / 1024  # KB
        print(f"  {f.name}: {size:.1f} KB")
    
    # Mostrar el log
    log_files = list(output_path.glob("extraction_*.log"))
    if log_files:
        print(f"\nLog file: {log_files[0].name}")
        with open(log_files[0]) as f:
            print(f.read())

if __name__ == "__main__":
    test_single_month()
