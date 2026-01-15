#!/usr/bin/env python3
"""
Script para verificar qué archivos faltan por procesar
Útil cuando agregas más carpetas a .data/Nuevo
"""
from pathlib import Path
from utils.db import ExtractionDB


def check_missing_files(input_dir=".data/Nuevo"):
    """Verifica qué archivos faltan por procesar"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    db = ExtractionDB()
    
    # Encontrar todos los archivos
    all_files = sorted(input_path.rglob("*.txt"))
    
    # Filtrar solo travesías y cabotajes
    relevant_files = [f for f in all_files if "_V_" in f.name or "_C_" in f.name]
    
    print(f"\n📊 FILE PROCESSING STATUS")
    print("="*70)
    print(f"Total files found: {len(relevant_files)}")
    print()
    
    # Contar por tipo
    traversing_files = [f for f in relevant_files if "_V_" in f.name]
    cabotage_files = [f for f in relevant_files if "_C_" in f.name]
    
    print(f"Traversing files (_V_): {len(traversing_files)}")
    print(f"Cabotage files (_C_): {len(cabotage_files)}")
    print()
    
    # Verificar cuáles ya fueron procesados
    processed = 0
    missing = []
    
    for file_path in relevant_files:
        if db.is_file_processed(file_path):
            processed += 1
        else:
            missing.append(file_path)
    
    print(f"✅ Already processed: {processed}")
    print(f"⏳ Missing to process: {len(missing)}")
    print()
    
    # Mostrar archivos faltantes por año
    if missing:
        print("📋 MISSING FILES BY YEAR:")
        print("-"*70)
        
        missing_by_year = {}
        for file_path in missing:
            # Extraer año del nombre del archivo
            year = file_path.stem[:4]
            if year not in missing_by_year:
                missing_by_year[year] = {'V': 0, 'C': 0}
            
            if "_V_" in file_path.name:
                missing_by_year[year]['V'] += 1
            else:
                missing_by_year[year]['C'] += 1
        
        for year in sorted(missing_by_year.keys()):
            v_count = missing_by_year[year]['V']
            c_count = missing_by_year[year]['C']
            total = v_count + c_count
            print(f"  {year}: {total} files (V: {v_count}, C: {c_count})")
        
        print()
        print("💡 To process missing files, run:")
        print("   python3 main.py")
        print("   → Select option 5")
        print("   → Enter input directory: .data/Nuevo")
        print("   → Enter output directory: .data/output")
        print("   → Enter threads: 8")
    else:
        print("✅ All files have been processed!")


def check_by_year(input_dir=".data/Nuevo"):
    """Muestra el estado de procesamiento por año"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    db = ExtractionDB()
    
    print(f"\n📊 PROCESSING STATUS BY YEAR")
    print("="*70)
    
    # Obtener años disponibles
    years = sorted([d.name for d in input_path.iterdir() if d.is_dir() and d.name.isdigit()])
    
    for year in years:
        year_dir = input_path / year
        year_files = sorted(year_dir.rglob("*.txt"))
        relevant_files = [f for f in year_files if "_V_" in f.name or "_C_" in f.name]
        
        if not relevant_files:
            continue
        
        # Contar procesados
        processed = sum(1 for f in relevant_files if db.is_file_processed(f))
        missing = len(relevant_files) - processed
        
        # Contar por tipo
        v_files = len([f for f in relevant_files if "_V_" in f.name])
        c_files = len([f for f in relevant_files if "_C_" in f.name])
        
        v_processed = sum(1 for f in relevant_files if "_V_" in f.name and db.is_file_processed(f))
        c_processed = sum(1 for f in relevant_files if "_C_" in f.name and db.is_file_processed(f))
        
        v_missing = v_files - v_processed
        c_missing = c_files - c_processed
        
        percent = (processed / len(relevant_files) * 100) if relevant_files else 0
        
        status = "✅" if missing == 0 else "⏳"
        
        print(f"\n{status} {year}")
        print(f"   Total: {len(relevant_files)} files")
        print(f"   Traversing: {v_files} ({v_processed} processed, {v_missing} missing)")
        print(f"   Cabotage: {c_files} ({c_processed} processed, {c_missing} missing)")
        print(f"   Progress: {percent:.1f}% ({processed}/{len(relevant_files)})")


def check_database_vs_files(input_dir=".data/Nuevo"):
    """Compara la base de datos con los archivos del sistema"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    db = ExtractionDB()
    stats = db.get_stats()
    
    # Contar archivos
    all_files = sorted(input_path.rglob("*.txt"))
    relevant_files = [f for f in all_files if "_V_" in f.name or "_C_" in f.name]
    
    print(f"\n📊 DATABASE vs FILES COMPARISON")
    print("="*70)
    print(f"\nFiles in system: {len(relevant_files)}")
    print(f"  Traversing: {len([f for f in relevant_files if '_V_' in f.name])}")
    print(f"  Cabotage: {len([f for f in relevant_files if '_C_' in f.name])}")
    
    print(f"\nEntries in database: {stats['traversing'] + stats['cabotage']:,}")
    print(f"  Traversing: {stats['traversing']:,}")
    print(f"  Cabotage: {stats['cabotage']:,}")
    
    print(f"\nFiles processed: {stats['files_processed']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_missing.py status              # Show missing files")
        print("  python check_missing.py by-year             # Show status by year")
        print("  python check_missing.py compare             # Compare DB vs files")
        print("\nExamples:")
        print("  python check_missing.py status")
        print("  python check_missing.py by-year")
        print("  python check_missing.py compare")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        check_missing_files()
    elif command == "by-year":
        check_by_year()
    elif command == "compare":
        check_database_vs_files()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
