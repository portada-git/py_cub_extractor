#!/usr/bin/env python3
"""
Script para exportar datos de la base de datos a JSON y CSV
Permite exportar por año, mes, día, puerto, barco, capitán
"""
import json
import csv
from pathlib import Path
from utils.db import ExtractionDB


def export_year(db, year, output_dir):
    """Exporta un año completo"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Travesías
    traversing = db.get_traversing_by_year(year)
    if traversing:
        traversing_clean = _remove_excluded_fields(traversing)
        json_file = output_path / f"{year}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing to {json_file}")
        
        csv_file = output_path / f"{year}_traversing.csv"
        _export_to_csv(csv_file, traversing_clean)
    
    # Cabotajes
    cabotage = db.get_cabotage_by_year(year)
    if cabotage:
        cabotage_clean = _remove_excluded_fields(cabotage)
        json_file = output_path / f"{year}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage to {json_file}")
        
        csv_file = output_path / f"{year}_cabotage.csv"
        _export_to_csv(csv_file, cabotage_clean)


def export_month(db, year, month, output_dir):
    """Exporta un mes específico"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Travesías
    traversing = db.get_traversing_by_month(year, month)
    if traversing:
        traversing_clean = _remove_excluded_fields(traversing)
        json_file = output_path / f"{year}_{month:02d}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing to {json_file}")
        
        csv_file = output_path / f"{year}_{month:02d}_traversing.csv"
        _export_to_csv(csv_file, traversing_clean)
    
    # Cabotajes
    cabotage = db.get_cabotage_by_month(year, month)
    if cabotage:
        cabotage_clean = _remove_excluded_fields(cabotage)
        json_file = output_path / f"{year}_{month:02d}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage to {json_file}")
        
        csv_file = output_path / f"{year}_{month:02d}_cabotage.csv"
        _export_to_csv(csv_file, cabotage_clean)


def export_day(db, year, month, day, output_dir):
    """Exporta un día específico"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Travesías
    traversing = db.get_traversing_by_day(year, month, day)
    if traversing:
        traversing_clean = _remove_excluded_fields(traversing)
        json_file = output_path / f"{year}_{month:02d}_{day:02d}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing to {json_file}")
        
        csv_file = output_path / f"{year}_{month:02d}_{day:02d}_traversing.csv"
        _export_to_csv(csv_file, traversing_clean)
    
    # Cabotajes
    cabotage = db.get_cabotage_by_day(year, month, day)
    if cabotage:
        cabotage_clean = _remove_excluded_fields(cabotage)
        json_file = output_path / f"{year}_{month:02d}_{day:02d}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage to {json_file}")
        
        csv_file = output_path / f"{year}_{month:02d}_{day:02d}_cabotage.csv"
        _export_to_csv(csv_file, cabotage_clean)


def export_port(db, port_name, output_dir):
    """Exporta datos de un puerto específico"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    safe_name = port_name.replace(' ', '_').replace('/', '_')
    
    # Travesías
    traversing = db.get_traversing_by_port(port_name)
    if traversing:
        traversing_clean = _remove_excluded_fields(traversing)
        json_file = output_path / f"port_{safe_name}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing from {port_name}")
        
        csv_file = output_path / f"port_{safe_name}_traversing.csv"
        _export_to_csv(csv_file, traversing_clean)
    
    # Cabotajes
    cabotage = db.get_cabotage_by_port(port_name)
    if cabotage:
        cabotage_clean = _remove_excluded_fields(cabotage)
        json_file = output_path / f"port_{safe_name}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage from {port_name}")
        
        csv_file = output_path / f"port_{safe_name}_cabotage.csv"
        _export_to_csv(csv_file, cabotage_clean)


def export_ship(db, ship_name, output_dir):
    """Exporta datos de un barco específico"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    safe_name = ship_name.replace(' ', '_').replace('/', '_')
    
    # Travesías
    traversing = db.get_traversing_by_ship(ship_name)
    if traversing:
        traversing_clean = _remove_excluded_fields(traversing)
        json_file = output_path / f"ship_{safe_name}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing for ship {ship_name}")
        
        csv_file = output_path / f"ship_{safe_name}_traversing.csv"
        _export_to_csv(csv_file, traversing_clean)
    
    # Cabotajes
    cabotage = db.get_cabotage_by_ship(ship_name)
    if cabotage:
        cabotage_clean = _remove_excluded_fields(cabotage)
        json_file = output_path / f"ship_{safe_name}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage for ship {ship_name}")
        
        csv_file = output_path / f"ship_{safe_name}_cabotage.csv"
        _export_to_csv(csv_file, cabotage_clean)


def export_master(db, master_name, output_dir):
    """Exporta datos de un capitán específico"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    safe_name = master_name.replace(' ', '_').replace('/', '_')
    
    # Travesías
    traversing = db.get_traversing_by_master(master_name)
    if traversing:
        traversing_clean = _remove_excluded_fields(traversing)
        json_file = output_path / f"master_{safe_name}_traversing.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(traversing_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(traversing)} traversing for captain {master_name}")
        
        csv_file = output_path / f"master_{safe_name}_traversing.csv"
        _export_to_csv(csv_file, traversing_clean)
    
    # Cabotajes
    cabotage = db.get_cabotage_by_master(master_name)
    if cabotage:
        cabotage_clean = _remove_excluded_fields(cabotage)
        json_file = output_path / f"master_{safe_name}_cabotage.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cabotage_clean, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported {len(cabotage)} cabotage for captain {master_name}")
        
        csv_file = output_path / f"master_{safe_name}_cabotage.csv"
        _export_to_csv(csv_file, cabotage_clean)


def list_ports(db):
    """Lista todos los puertos"""
    ports = db.get_all_ports()
    print(f"\n📍 PORTS ({len(ports)} total)")
    print("="*50)
    for port in ports:
        print(f"  • {port}")


def list_ships(db):
    """Lista todos los barcos"""
    ships = db.get_all_ships()
    print(f"\n⛵ SHIPS ({len(ships)} total)")
    print("="*50)
    for ship in ships[:50]:  # Mostrar primeros 50
        print(f"  • {ship}")
    if len(ships) > 50:
        print(f"  ... and {len(ships) - 50} more")


def list_masters(db):
    """Lista todos los capitanes"""
    masters = db.get_all_masters()
    print(f"\n👨‍⚓ CAPTAINS ({len(masters)} total)")
    print("="*50)
    for master in masters[:50]:  # Mostrar primeros 50
        print(f"  • {master}")
    if len(masters) > 50:
        print(f"  ... and {len(masters) - 50} more")


def _remove_excluded_fields(data):
    """Remueve campos excluidos (id, obs) de los datos y convierte cargo_list a dict"""
    exclude_fields = {'id', 'obs'}
    cleaned = []
    for row in data:
        cleaned_row = {k: v for k, v in row.items() if k not in exclude_fields}
        
        # Convertir cargo_list de string JSON a dict/list
        if 'cargo_list' in cleaned_row and isinstance(cleaned_row['cargo_list'], str):
            try:
                cleaned_row['cargo_list'] = json.loads(cleaned_row['cargo_list'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        cleaned.append(cleaned_row)
    return cleaned


def _export_to_csv(csv_file, data):
    """Exporta datos a CSV"""
    if not data:
        return
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        # Obtener todas las claves
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())
        
        # Excluir id y obs
        exclude_fields = {'id', 'obs'}
        fieldnames = sorted([k for k in all_keys if k not in exclude_fields])
        
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for row in data:
            row_copy = row.copy()
            
            # Remover campos excluidos
            for field in exclude_fields:
                row_copy.pop(field, None)
            
            # Convertir cargo_list de JSON a string legible
            if 'cargo_list' in row_copy:
                cargo_list = row_copy.get('cargo_list')
                if isinstance(cargo_list, str):
                    try:
                        cargo_list = json.loads(cargo_list)
                    except:
                        pass
                
                if isinstance(cargo_list, list) and len(cargo_list) > 0:
                    # Formatear cargo_list de forma legible
                    cargo_items = []
                    for item in cargo_list:
                        if isinstance(item, dict):
                            merchant = item.get('cargo_merchant_name', 'N/A')
                            cargos = item.get('cargo', [])
                            cargo_str = '; '.join([
                                f"{c.get('cargo_quantity', '')} {c.get('cargo_unit', '')} {c.get('cargo_commodity', '')}"
                                for c in cargos if isinstance(c, dict)
                            ])
                            cargo_items.append(f"{merchant}: {cargo_str}")
                    row_copy['cargo_list'] = ' | '.join(cargo_items)
                else:
                    row_copy['cargo_list'] = ''
            
            writer.writerow(row_copy)


def show_stats(db):
    """Muestra estadísticas de la base de datos"""
    stats = db.get_stats()
    print("\n📊 DATABASE STATISTICS")
    print("="*50)
    print(f"Traversing entries: {stats['traversing']:,}")
    print(f"Cabotage entries: {stats['cabotage']:,}")
    print(f"Files processed: {stats['files_processed']:,}")
    print(f"Total entries: {stats['traversing'] + stats['cabotage']:,}")


if __name__ == "__main__":
    import sys
    
    db = ExtractionDB()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python export_data.py stats                              # Show statistics")
        print("  python export_data.py year <year> <output_dir>           # Export year")
        print("  python export_data.py month <year> <month> <output_dir>  # Export month")
        print("  python export_data.py day <year> <month> <day> <output_dir> # Export day")
        print("  python export_data.py port <port_name> <output_dir>      # Export by port")
        print("  python export_data.py ship <ship_name> <output_dir>      # Export by ship")
        print("  python export_data.py master <master_name> <output_dir>  # Export by captain")
        print("  python export_data.py list-ports                         # List all ports")
        print("  python export_data.py list-ships                         # List all ships")
        print("  python export_data.py list-masters                       # List all captains")
        print("\nExamples:")
        print("  python export_data.py year 1852 .data/output")
        print("  python export_data.py month 1852 1 .data/output")
        print("  python export_data.py day 1852 1 15 .data/output")
        print("  python export_data.py port 'Nueva York' .data/output")
        print("  python export_data.py ship 'Neptuno' .data/output")
        print("  python export_data.py master 'Cobos' .data/output")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "stats":
        show_stats(db)
    elif command == "year":
        if len(sys.argv) < 4:
            print("Error: year command requires <year> and <output_dir>")
            sys.exit(1)
        year = sys.argv[2]
        output_dir = sys.argv[3]
        export_year(db, year, output_dir)
    elif command == "month":
        if len(sys.argv) < 5:
            print("Error: month command requires <year>, <month>, and <output_dir>")
            sys.exit(1)
        year = sys.argv[2]
        month = int(sys.argv[3])
        output_dir = sys.argv[4]
        export_month(db, year, month, output_dir)
    elif command == "day":
        if len(sys.argv) < 6:
            print("Error: day command requires <year>, <month>, <day>, and <output_dir>")
            sys.exit(1)
        year = sys.argv[2]
        month = int(sys.argv[3])
        day = int(sys.argv[4])
        output_dir = sys.argv[5]
        export_day(db, year, month, day, output_dir)
    elif command == "port":
        if len(sys.argv) < 4:
            print("Error: port command requires <port_name> and <output_dir>")
            sys.exit(1)
        port_name = sys.argv[2]
        output_dir = sys.argv[3]
        export_port(db, port_name, output_dir)
    elif command == "ship":
        if len(sys.argv) < 4:
            print("Error: ship command requires <ship_name> and <output_dir>")
            sys.exit(1)
        ship_name = sys.argv[2]
        output_dir = sys.argv[3]
        export_ship(db, ship_name, output_dir)
    elif command == "master":
        if len(sys.argv) < 4:
            print("Error: master command requires <master_name> and <output_dir>")
            sys.exit(1)
        master_name = sys.argv[2]
        output_dir = sys.argv[3]
        export_master(db, master_name, output_dir)
    elif command == "list-ports":
        list_ports(db)
    elif command == "list-ships":
        list_ships(db)
    elif command == "list-masters":
        list_masters(db)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
