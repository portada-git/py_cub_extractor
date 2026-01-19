#!/usr/bin/env python3
"""
Script para contar objetos en archivos JSON
"""
import json
from pathlib import Path


def count_json_objects(json_file):
    """Cuenta los objetos en un archivo JSON"""
    json_path = Path(json_file)
    
    if not json_path.exists():
        print(f"❌ Archivo no encontrado: {json_file}")
        return
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("="*80)
        print(f"📊 ANÁLISIS: {json_path.name}")
        print("="*80)
        
        if isinstance(data, list):
            print(f"📈 Total de objetos: {len(data)}")
            print()
            
            # Estadísticas por campo
            if len(data) > 0:
                print("📋 Campos disponibles:")
                first_obj = data[0]
                for key in sorted(first_obj.keys()):
                    print(f"  • {key}")
                
                print()
                print("📊 Estadísticas:")
                
                # Contar campos no vacíos
                for key in sorted(first_obj.keys()):
                    non_empty = sum(1 for obj in data if obj.get(key))
                    percentage = (non_empty / len(data)) * 100
                    print(f"  {key:30} {non_empty:6} ({percentage:5.1f}%)")
                
                print()
                print("🔍 Detalles de cargo_list:")
                total_cargos = 0
                for i, obj in enumerate(data):
                    cargo_list = obj.get('cargo_list', [])
                    if isinstance(cargo_list, str):
                        try:
                            cargo_list = json.loads(cargo_list)
                        except:
                            cargo_list = []
                    
                    if isinstance(cargo_list, list):
                        total_cargos += len(cargo_list)
                
                avg_cargos = total_cargos / len(data) if len(data) > 0 else 0
                print(f"  Total de items de carga: {total_cargos}")
                print(f"  Promedio por registro: {avg_cargos:.2f}")
        
        elif isinstance(data, dict):
            print(f"📈 Es un objeto único con {len(data)} campos")
            for key in sorted(data.keys()):
                print(f"  • {key}")
        
        else:
            print(f"📈 Tipo: {type(data).__name__}")
            print(f"📈 Contenido: {data}")
        
        print()
        print("="*80)
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 utils/count_json.py <archivo.json>")
        print()
        print("Ejemplos:")
        print("  python3 utils/count_json.py .data/results/1852_traversing.json")
        print("  python3 utils/count_json.py .data/results/1852_cabotage.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    count_json_objects(json_file)
