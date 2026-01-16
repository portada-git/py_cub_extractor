#!/usr/bin/env python3
"""
Script para inspeccionar la base de datos
Muestra esquema y datos de las tablas
"""
import sqlite3
import json
from pathlib import Path


def inspect_database(db_path=".data/extraction.db"):
    """Inspecciona la base de datos"""
    db_path = Path(db_path)
    
    if not db_path.exists():
        print("❌ Base de datos no encontrada")
        return False
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("="*80)
        print("INSPECCIÓN DE BASE DE DATOS")
        print("="*80)
        print(f"📍 Base de datos: {db_path}")
        print(f"📊 Tablas encontradas: {len(tables)}")
        print()
        
        for table_name in tables:
            print("="*80)
            print(f"📋 TABLA: {table_name}")
            print("="*80)
            
            # Esquema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("\n🔧 ESQUEMA:")
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                pk_str = "PRIMARY KEY" if pk else ""
                print(f"  • {col_name:25} {col_type:15} {nullable:10} {pk_str}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n📈 Total de registros: {count}")
            
            # Mostrar primeros registros
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                col_names = [description[0] for description in cursor.description]
                
                print(f"\n📄 Primeros {min(3, count)} registros:")
                print()
                
                for i, row in enumerate(rows, 1):
                    print(f"  Registro {i}:")
                    for col_name, value in zip(col_names, row):
                        if col_name == 'cargo_list' and value:
                            try:
                                cargo = json.loads(value)
                                print(f"    {col_name}: {json.dumps(cargo, ensure_ascii=False, indent=6)}")
                            except:
                                print(f"    {col_name}: {value[:100]}...")
                        elif value and len(str(value)) > 80:
                            print(f"    {col_name}: {str(value)[:80]}...")
                        else:
                            print(f"    {col_name}: {value}")
                    print()
            
            print()


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else ".data/extraction.db"
    inspect_database(db_path)
