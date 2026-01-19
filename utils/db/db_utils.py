#!/usr/bin/env python3
"""
Utilidades para gestionar la base de datos
"""
import sqlite3
from pathlib import Path
from .database import ExtractionDB


def reset_database(db_path=".data/extraction.db"):
    """Reinicia la base de datos (elimina todos los datos)"""
    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()
        print(f"✅ Database reset: {db_path}")
    else:
        print(f"ℹ️  Database not found: {db_path}")


def backup_database(db_path=".data/extraction.db", backup_path=None):
    """Crea un backup de la base de datos"""
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    if backup_path is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f".data/extraction_backup_{timestamp}.db"
    
    backup_file = Path(backup_path)
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    import shutil
    shutil.copy(db_file, backup_file)
    print(f"✅ Backup created: {backup_path}")


def delete_year(db_path=".data/extraction.db", year=None):
    """Elimina todos los datos de un año específico"""
    if year is None:
        print("❌ Year is required")
        return
    
    db = ExtractionDB(db_path)
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Eliminar travesías
        cursor.execute('DELETE FROM traversing WHERE source_file LIKE ?', (f'{year}%',))
        trav_deleted = cursor.rowcount
        
        # Eliminar cabotajes
        cursor.execute('DELETE FROM cabotage WHERE source_file LIKE ?', (f'{year}%',))
        cab_deleted = cursor.rowcount
        
        # Eliminar archivos procesados
        cursor.execute('DELETE FROM processed_files WHERE file_path LIKE ?', (f'%/{year}/%',))
        files_deleted = cursor.rowcount
        
        conn.commit()
    
    print(f"✅ Deleted year {year}:")
    print(f"   Traversing: {trav_deleted}")
    print(f"   Cabotage: {cab_deleted}")
    print(f"   Files: {files_deleted}")


def delete_duplicates(db_path=".data/extraction.db"):
    """Elimina entradas duplicadas (mantiene la primera)"""
    db = ExtractionDB(db_path)
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Eliminar duplicados en travesías
        cursor.execute('''
            DELETE FROM traversing WHERE id NOT IN (
                SELECT MIN(id) FROM traversing GROUP BY raw_text, source_file
            )
        ''')
        trav_deleted = cursor.rowcount
        
        # Eliminar duplicados en cabotajes
        cursor.execute('''
            DELETE FROM cabotage WHERE id NOT IN (
                SELECT MIN(id) FROM cabotage GROUP BY raw_text, source_file
            )
        ''')
        cab_deleted = cursor.rowcount
        
        conn.commit()
    
    print(f"✅ Deleted duplicates:")
    print(f"   Traversing: {trav_deleted}")
    print(f"   Cabotage: {cab_deleted}")


def vacuum_database(db_path=".data/extraction.db"):
    """Optimiza la base de datos (libera espacio)"""
    with sqlite3.connect(db_path) as conn:
        conn.execute('VACUUM')
    print(f"✅ Database optimized: {db_path}")


def show_database_info(db_path=".data/extraction.db"):
    """Muestra información de la base de datos"""
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    db = ExtractionDB(db_path)
    stats = db.get_stats()
    
    size_mb = db_file.stat().st_size / (1024 * 1024)
    
    print(f"\n📊 DATABASE INFO: {db_path}")
    print("="*50)
    print(f"Size: {size_mb:.2f} MB")
    print(f"Traversing entries: {stats['traversing']:,}")
    print(f"Cabotage entries: {stats['cabotage']:,}")
    print(f"Files processed: {stats['files_processed']:,}")
    print(f"Total entries: {stats['traversing'] + stats['cabotage']:,}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python db_utils.py info                    # Show database info")
        print("  python db_utils.py backup                  # Create backup")
        print("  python db_utils.py reset                   # Reset database (DELETE ALL)")
        print("  python db_utils.py delete-year <year>      # Delete year data")
        print("  python db_utils.py delete-duplicates       # Remove duplicates")
        print("  python db_utils.py vacuum                  # Optimize database")
        print("\nExamples:")
        print("  python db_utils.py info")
        print("  python db_utils.py backup")
        print("  python db_utils.py delete-year 1852")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "info":
        show_database_info()
    elif command == "backup":
        backup_database()
    elif command == "reset":
        confirm = input("⚠️  This will DELETE ALL data. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            reset_database()
        else:
            print("Cancelled")
    elif command == "delete-year":
        if len(sys.argv) < 3:
            print("Error: delete-year requires <year>")
            sys.exit(1)
        year = sys.argv[2]
        delete_year(year=year)
    elif command == "delete-duplicates":
        delete_duplicates()
    elif command == "vacuum":
        vacuum_database()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
