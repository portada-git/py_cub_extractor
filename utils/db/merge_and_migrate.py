#!/usr/bin/env python3
"""
Script para:
1. Fusionar extraction2.db con extraction.db
2. Migrar al nuevo esquema con todos los campos
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime


def merge_databases(db1_path=".data/extraction.db", db2_path=".data/extraction2.db"):
    """Fusiona extraction2.db en extraction.db"""
    
    db1_path = Path(db1_path)
    db2_path = Path(db2_path)
    
    if not db2_path.exists():
        print(f"❌ {db2_path} not found")
        return False
    
    print("="*80)
    print("MERGING DATABASES")
    print("="*80)
    
    # Crear backup
    backup_path = db1_path.parent / f"extraction_backup_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy(db1_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    try:
        conn1 = sqlite3.connect(db1_path)
        conn2 = sqlite3.connect(db2_path)
        
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        # Contar registros antes
        cursor1.execute("SELECT COUNT(*) FROM traversing")
        trav_before = cursor1.fetchone()[0]
        cursor1.execute("SELECT COUNT(*) FROM cabotage")
        cab_before = cursor1.fetchone()[0]
        
        print(f"\nBefore merge:")
        print(f"  Traversing: {trav_before:,}")
        print(f"  Cabotage: {cab_before:,}")
        
        # Copiar travesías de db2 a db1
        cursor2.execute("SELECT * FROM traversing")
        trav_rows = cursor2.fetchall()
        
        cursor2.execute("PRAGMA table_info(traversing)")
        trav_cols = [col[1] for col in cursor2.fetchall()]
        
        inserted_trav = 0
        for row in trav_rows:
            try:
                placeholders = ','.join(['?' for _ in trav_cols])
                cursor1.execute(f"INSERT INTO traversing ({','.join(trav_cols)}) VALUES ({placeholders})", row)
                inserted_trav += 1
            except sqlite3.IntegrityError:
                pass  # Duplicate, skip
        
        # Copiar cabotajes de db2 a db1
        cursor2.execute("SELECT * FROM cabotage")
        cab_rows = cursor2.fetchall()
        
        cursor2.execute("PRAGMA table_info(cabotage)")
        cab_cols = [col[1] for col in cursor2.fetchall()]
        
        inserted_cab = 0
        for row in cab_rows:
            try:
                placeholders = ','.join(['?' for _ in cab_cols])
                cursor1.execute(f"INSERT INTO cabotage ({','.join(cab_cols)}) VALUES ({placeholders})", row)
                inserted_cab += 1
            except sqlite3.IntegrityError:
                pass  # Duplicate, skip
        
        # Copiar processed_files
        cursor2.execute("SELECT * FROM processed_files")
        files_rows = cursor2.fetchall()
        
        cursor2.execute("PRAGMA table_info(processed_files)")
        files_cols = [col[1] for col in cursor2.fetchall()]
        
        inserted_files = 0
        for row in files_rows:
            try:
                placeholders = ','.join(['?' for _ in files_cols])
                cursor1.execute(f"INSERT INTO processed_files ({','.join(files_cols)}) VALUES ({placeholders})", row)
                inserted_files += 1
            except sqlite3.IntegrityError:
                pass  # Duplicate, skip
        
        conn1.commit()
        
        # Contar registros después
        cursor1.execute("SELECT COUNT(*) FROM traversing")
        trav_after = cursor1.fetchone()[0]
        cursor1.execute("SELECT COUNT(*) FROM cabotage")
        cab_after = cursor1.fetchone()[0]
        
        print(f"\nAfter merge:")
        print(f"  Traversing: {trav_after:,} (+{inserted_trav:,})")
        print(f"  Cabotage: {cab_after:,} (+{inserted_cab:,})")
        print(f"  Files: +{inserted_files:,}")
        
        conn1.close()
        conn2.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during merge: {e}")
        return False


def migrate_to_new_schema(db_path=".data/extraction.db"):
    """Migra al nuevo esquema con todos los campos"""
    
    db_path = Path(db_path)
    
    print("\n" + "="*80)
    print("MIGRATING TO NEW SCHEMA")
    print("="*80)
    
    # Campos nuevos que faltan
    new_fields = {
        'travel_duration_value': 'INTEGER',
        'travel_duration_unit': 'TEXT',
        'ship_tons_capacity': 'INTEGER',
        'ship_tons_unit': 'TEXT',
        'crew_number': 'INTEGER',
        'passenger_account': 'INTEGER',
        'quarantine': 'BOOLEAN',
        'forced_arrival': 'BOOLEAN',
        'obs': 'TEXT',
        'parsed_text': 'TEXT'
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar qué campos faltan en traversing
        cursor.execute("PRAGMA table_info(traversing)")
        existing_cols = {col[1] for col in cursor.fetchall()}
        
        print("\nAdding missing columns to traversing table:")
        for field, field_type in new_fields.items():
            if field not in existing_cols:
                cursor.execute(f"ALTER TABLE traversing ADD COLUMN {field} {field_type}")
                print(f"  ✅ Added {field} ({field_type})")
            else:
                print(f"  ℹ️  {field} already exists")
        
        # Verificar qué campos faltan en cabotage
        cursor.execute("PRAGMA table_info(cabotage)")
        existing_cols = {col[1] for col in cursor.fetchall()}
        
        print("\nAdding missing columns to cabotage table:")
        for field, field_type in new_fields.items():
            if field not in existing_cols:
                cursor.execute(f"ALTER TABLE cabotage ADD COLUMN {field} {field_type}")
                print(f"  ✅ Added {field} ({field_type})")
            else:
                print(f"  ℹ️  {field} already exists")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("DATABASE MERGE AND MIGRATION TOOL")
    print("="*80)
    
    # Paso 1: Fusionar
    if merge_databases():
        print("\n✅ Merge completed")
        
        # Paso 2: Migrar
        if migrate_to_new_schema():
            print("\n" + "="*80)
            print("✅ ALL OPERATIONS COMPLETED SUCCESSFULLY")
            print("="*80)
            sys.exit(0)
    
    print("\n" + "="*80)
    print("❌ OPERATIONS FAILED")
    print("="*80)
    sys.exit(1)
