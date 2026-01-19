#!/usr/bin/env python3
"""
Script para analizar datos extraídos
Genera reportes y estadísticas
"""
import json
from collections import Counter
from utils.db import ExtractionDB


def analyze_year(db, year):
    """Analiza datos de un año"""
    traversing = db.get_traversing_by_year(year)
    cabotage = db.get_cabotage_by_year(year)
    
    print(f"\n📊 ANALYSIS FOR YEAR {year}")
    print("="*70)
    
    # Travesías
    print(f"\n🚢 TRAVERSING ({len(traversing)} entries)")
    print("-"*70)
    
    if traversing:
        ports = Counter([t.get('travel_departure_port') for t in traversing if t.get('travel_departure_port')])
        ships = Counter([t.get('ship_name') for t in traversing if t.get('ship_name')])
        masters = Counter([t.get('master_name') for t in traversing if t.get('master_name')])
        
        print(f"  Unique ports: {len(ports)}")
        print(f"  Top 5 ports:")
        for port, count in ports.most_common(5):
            print(f"    • {port}: {count}")
        
        print(f"\n  Unique ships: {len(ships)}")
        print(f"  Top 5 ships:")
        for ship, count in ships.most_common(5):
            print(f"    • {ship}: {count}")
        
        print(f"\n  Unique captains: {len(masters)}")
        print(f"  Top 5 captains:")
        for master, count in masters.most_common(5):
            print(f"    • {master}: {count}")
        
        # Cargo analysis
        all_cargo = []
        for t in traversing:
            if t.get('cargo_list'):
                try:
                    cargo = json.loads(t['cargo_list']) if isinstance(t['cargo_list'], str) else t['cargo_list']
                    all_cargo.extend(cargo)
                except:
                    pass
        
        if all_cargo:
            cargo_counter = Counter(all_cargo)
            print(f"\n  Total cargo items: {len(all_cargo)}")
            print(f"  Top 10 cargo types:")
            for cargo, count in cargo_counter.most_common(10):
                print(f"    • {cargo}: {count}")
    
    # Cabotajes
    print(f"\n⛵ CABOTAGE ({len(cabotage)} entries)")
    print("-"*70)
    
    if cabotage:
        ports = Counter([c.get('travel_departure_port') for c in cabotage if c.get('travel_departure_port')])
        ships = Counter([c.get('ship_name') for c in cabotage if c.get('ship_name')])
        masters = Counter([c.get('master_name') for c in cabotage if c.get('master_name')])
        
        print(f"  Unique ports: {len(ports)}")
        print(f"  Top 5 ports:")
        for port, count in ports.most_common(5):
            print(f"    • {port}: {count}")
        
        print(f"\n  Unique ships: {len(ships)}")
        print(f"  Top 5 ships:")
        for ship, count in ships.most_common(5):
            print(f"    • {ship}: {count}")
        
        print(f"\n  Unique captains: {len(masters)}")
        print(f"  Top 5 captains:")
        for master, count in masters.most_common(5):
            print(f"    • {master}: {count}")
        
        # Cargo analysis
        all_cargo = []
        for c in cabotage:
            if c.get('cargo_list'):
                try:
                    cargo = json.loads(c['cargo_list']) if isinstance(c['cargo_list'], str) else c['cargo_list']
                    all_cargo.extend(cargo)
                except:
                    pass
        
        if all_cargo:
            cargo_counter = Counter(all_cargo)
            print(f"\n  Total cargo items: {len(all_cargo)}")
            print(f"  Top 10 cargo types:")
            for cargo, count in cargo_counter.most_common(10):
                print(f"    • {cargo}: {count}")


def analyze_port(db, port_name):
    """Analiza datos de un puerto"""
    traversing = db.get_traversing_by_port(port_name)
    cabotage = db.get_cabotage_by_port(port_name)
    
    print(f"\n📍 ANALYSIS FOR PORT: {port_name}")
    print("="*70)
    
    print(f"\n🚢 TRAVERSING ({len(traversing)} entries)")
    if traversing:
        ships = Counter([t.get('ship_name') for t in traversing if t.get('ship_name')])
        masters = Counter([t.get('master_name') for t in traversing if t.get('master_name')])
        
        print(f"  Ships: {len(ships)}")
        print(f"  Captains: {len(masters)}")
        print(f"  Top ships:")
        for ship, count in ships.most_common(5):
            print(f"    • {ship}: {count}")
    
    print(f"\n⛵ CABOTAGE ({len(cabotage)} entries)")
    if cabotage:
        ships = Counter([c.get('ship_name') for c in cabotage if c.get('ship_name')])
        masters = Counter([c.get('master_name') for c in cabotage if c.get('master_name')])
        
        print(f"  Ships: {len(ships)}")
        print(f"  Captains: {len(masters)}")
        print(f"  Top ships:")
        for ship, count in ships.most_common(5):
            print(f"    • {ship}: {count}")


def analyze_ship(db, ship_name):
    """Analiza datos de un barco"""
    traversing = db.get_traversing_by_ship(ship_name)
    cabotage = db.get_cabotage_by_ship(ship_name)
    
    print(f"\n⛵ ANALYSIS FOR SHIP: {ship_name}")
    print("="*70)
    
    print(f"\n🚢 TRAVERSING ({len(traversing)} entries)")
    if traversing:
        ports = Counter([t.get('travel_departure_port') for t in traversing if t.get('travel_departure_port')])
        masters = Counter([t.get('master_name') for t in traversing if t.get('master_name')])
        
        print(f"  Ports: {len(ports)}")
        print(f"  Captains: {len(masters)}")
        print(f"  Top ports:")
        for port, count in ports.most_common(5):
            print(f"    • {port}: {count}")
        print(f"  Captains:")
        for master, count in masters.most_common(5):
            print(f"    • {master}: {count}")
    
    print(f"\n⛵ CABOTAGE ({len(cabotage)} entries)")
    if cabotage:
        ports = Counter([c.get('travel_departure_port') for c in cabotage if c.get('travel_departure_port')])
        masters = Counter([c.get('master_name') for c in cabotage if c.get('master_name')])
        
        print(f"  Ports: {len(ports)}")
        print(f"  Captains: {len(masters)}")
        print(f"  Top ports:")
        for port, count in ports.most_common(5):
            print(f"    • {port}: {count}")


def analyze_master(db, master_name):
    """Analiza datos de un capitán"""
    traversing = db.get_traversing_by_master(master_name)
    cabotage = db.get_cabotage_by_master(master_name)
    
    print(f"\n👨‍⚓ ANALYSIS FOR CAPTAIN: {master_name}")
    print("="*70)
    
    print(f"\n🚢 TRAVERSING ({len(traversing)} entries)")
    if traversing:
        ports = Counter([t.get('travel_departure_port') for t in traversing if t.get('travel_departure_port')])
        ships = Counter([t.get('ship_name') for t in traversing if t.get('ship_name')])
        
        print(f"  Ports: {len(ports)}")
        print(f"  Ships: {len(ships)}")
        print(f"  Top ports:")
        for port, count in ports.most_common(5):
            print(f"    • {port}: {count}")
        print(f"  Ships:")
        for ship, count in ships.most_common(5):
            print(f"    • {ship}: {count}")
    
    print(f"\n⛵ CABOTAGE ({len(cabotage)} entries)")
    if cabotage:
        ports = Counter([c.get('travel_departure_port') for c in cabotage if c.get('travel_departure_port')])
        ships = Counter([c.get('ship_name') for c in cabotage if c.get('ship_name')])
        
        print(f"  Ports: {len(ports)}")
        print(f"  Ships: {len(ships)}")
        print(f"  Top ports:")
        for port, count in ports.most_common(5):
            print(f"    • {port}: {count}")


if __name__ == "__main__":
    import sys
    
    db = ExtractionDB()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python analyze_data.py year <year>           # Analyze year")
        print("  python analyze_data.py port <port_name>      # Analyze port")
        print("  python analyze_data.py ship <ship_name>      # Analyze ship")
        print("  python analyze_data.py master <master_name>  # Analyze captain")
        print("\nExamples:")
        print("  python analyze_data.py year 1852")
        print("  python analyze_data.py port 'Nueva York'")
        print("  python analyze_data.py ship 'Neptuno'")
        print("  python analyze_data.py master 'Cobos'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "year":
        if len(sys.argv) < 3:
            print("Error: year command requires <year>")
            sys.exit(1)
        year = sys.argv[2]
        analyze_year(db, year)
    elif command == "port":
        if len(sys.argv) < 3:
            print("Error: port command requires <port_name>")
            sys.exit(1)
        port_name = sys.argv[2]
        analyze_port(db, port_name)
    elif command == "ship":
        if len(sys.argv) < 3:
            print("Error: ship command requires <ship_name>")
            sys.exit(1)
        ship_name = sys.argv[2]
        analyze_ship(db, ship_name)
    elif command == "master":
        if len(sys.argv) < 3:
            print("Error: master command requires <master_name>")
            sys.exit(1)
        master_name = sys.argv[2]
        analyze_master(db, master_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
