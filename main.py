from utils.utils import read_txt_files_recursively, catch_news_fragment, group_and_concatenate_txt_by_date, extract_entradas_cabotaje
from utils.utils import compute_important_dates, save_in_csv_file
from utils.extractor import Extractor
from utils.db import ExtractionDB
import json


def show_menu():
    print(r"""
    *** Cuban Node Traversing Entrances Extractor ***
    === Diario de la Marina Newspaper ===
    
                  |    |    |
                 )_)  )_)  )_)
                )___))___))___)
               )____)____)_____)
             _____|____|____|____\__
        ----\                   /-----
             \_________________/
     ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~~ ~ ~ ~ ~
     
    """)
    print("EXTRACTION OPTIONS:")
    print("1. Concatenate OCR text files by date")
    print("2. Extract TRAVERSING ENTRANCES")
    print("3. Extract CABOTAGE ENTRIES")
    print("4. Extract TRAVERSING ENTRANCES, CABOTAGE ENTRIES by YEAR (by threads)")
    print("5. Reprocess YEAR (delete old data and re-extract)")
    print()
    print("DATABASE & ANALYSIS:")
    print("6. Check missing files to process")
    print("7. Show database statistics")
    print("8. Export all years (JSON + CSV)")
    print()
    print("0. Exit")
    return input("Choose an option: ")


def concatenate_files_by_date():
    """Opción 1: Concatena archivos OCR por fecha"""
    input_dir = input("Enter path to OCR input directory: ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    group_and_concatenate_txt_by_date(input_dir, output_dir)
    print("✅ Files concatenated successfully")


def extract_structured_data():
    """Opción 2: Extrae travesías de archivos concatenados"""
    print("\n🚢 EXTRACT TRAVERSING ENTRANCES")
    input_dir = input("Enter path from joined TXT to extract info: ").strip()
    output_dir = input("Enter path to output directory of extraction result: ").strip()
    file_name_json = input("Enter name only of output file (CSV and JSON): ").strip()
    
    content_extracted = []
    dates_from_file = []
    
    for file_path in read_txt_files_recursively(input_dir):
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        print(f"📄 Processing file: {file_path}")
        date_file = file_path.stem[:10]
        dates_from_file.append(date_file)
        cached_news_frag = catch_news_fragment(content)
        content_extracted += cached_news_frag
    
    output_json = f"{output_dir}/{file_name_json}.json"
    results = []
    
    for content, date_file in zip(content_extracted, dates_from_file):
        # Usar directamente el LLM sin extract_news_list_with_openai
        try:
            from llm_service.llm_openai import extract_structured_data_with_openai
            row = extract_structured_data_with_openai(content['info_text'])
            
            if row and 'parsed_text' in row and row['parsed_text'] is not None:
                results.append(row)
        except Exception as e:
            print(f"   ⚠️ Error processing: {e}")
    
    with open(output_json, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=4)
    
    save_in_csv_file(f"{output_dir}/{file_name_json}.csv", results)
    
    print(f"\n✅ Extracted {len(results)} valid entries into {output_json}")


def extract_cabotage_data():
    """Opción 3: Extrae cabotajes de archivos concatenados"""
    print("\n⛵ EXTRACT CABOTAGE ENTRIES")
    input_dir = input("Enter path from joined TXT to extract cabotage info: ").strip()
    output_dir = input("Enter path to output directory of extraction result: ").strip()
    file_name_json = input("Enter name only of output file (CSV and JSON): ").strip()
    
    all_cabotage_entries = []
    
    for file_path in read_txt_files_recursively(input_dir):
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        print(f"📄 Processing file: {file_path}")
        date_file = file_path.stem[:10]
        
        cabotage_sections = extract_entradas_cabotaje(content)
        
        for section in cabotage_sections:
            all_cabotage_entries.append({
                'text': section['info_text'],
                'date_file': date_file
            })
    
    results = []
    for entry in all_cabotage_entries:
        lines = [line.strip() for line in entry['text'].split('\n') if line.strip() and not line.strip().startswith('ENTRADAS')]
        
        for line in lines:
            if len(line) < 10 or line.isupper():
                continue
            
            try:
                from llm_service.llm_openai import extract_cabotaje_data_with_openai
                row = extract_cabotaje_data_with_openai(line)
                
                if row and 'parsed_text' in row and row['parsed_text'] is not None:
                    results.append(row)
            except Exception as e:
                print(f"   ⚠️ Error processing: {e}")
    
    output_json = f"{output_dir}/{file_name_json}.json"
    
    with open(output_json, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=4)
    
    save_in_csv_file(f"{output_dir}/{file_name_json}.csv", results)
    
    print(f"\n✅ Extracted {len(results)} cabotage entries into {output_json}")


def extract_by_year():
    """Opción 4: Extrae por año con threads"""
    print("\n📅 EXTRACT BY YEAR (with threads)")
    input_dir = input("Enter path to OCR directory (e.g., .data/Nuevo): ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    
    from pathlib import Path
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Directory not found: {input_dir}")
        return
    
    subdirs = [d.name for d in input_path.iterdir() if d.is_dir() and d.name.isdigit()]
    
    if not subdirs:
        print(f"❌ No year directories found in {input_dir}")
        return
    
    if all(len(d) == 2 for d in subdirs):
        print(f"❌ Error: {input_dir} contains months (01-12), not years")
        print(f"   Please use the parent directory: .data/Nuevo")
        return
    
    try:
        max_workers = int(input("Number of threads (default 16): ").strip() or "16")
    except:
        max_workers = 16
    
    extractor = Extractor(input_dir, output_dir, max_workers)
    extractor.extract_all_years()


def reprocess_year():
    """Opción 5: Reprocessa un año"""
    print("\n🔄 REPROCESS YEAR")
    input_dir = input("Enter path to OCR directory (e.g., .data/Nuevo): ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    year = input("Enter year to reprocess (e.g., 1852): ").strip()
    
    from pathlib import Path
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Directory not found: {input_dir}")
        return
    
    year_path = input_path / year
    if not year_path.exists():
        print(f"❌ Year directory not found: {year_path}")
        return
    
    # Confirmar reprocessing
    db = ExtractionDB()
    stats = db.get_stats()
    
    print()
    print("="*60)
    print(f"⚠️  REPROCESSING YEAR {year}")
    print("="*60)
    print(f"Current database statistics:")
    print(f"  • Traversing entries: {stats['traversing']:,}")
    print(f"  • Cabotage entries: {stats['cabotage']:,}")
    print(f"  • Files processed: {stats['files_processed']:,}")
    print()
    print(f"This will DELETE all {year} data and reprocess from OCR files.")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("❌ Reprocessing cancelled")
        return
    
    # Eliminar datos del año
    print()
    print(f"🗑️  Deleting {year} data from database...")
    deleted = db.delete_year_data(year)
    print(f"  ✅ Deleted {deleted['traversing']} traversing entries")
    print(f"  ✅ Deleted {deleted['cabotage']} cabotage entries")
    print(f"  ✅ Deleted {deleted['files']} file records")
    
    # Reprocessar año
    print()
    print(f"🔄 Reprocessing {year}...")
    
    try:
        max_workers = int(input("Number of threads (default 16): ").strip() or "16")
    except:
        max_workers = 16
    
    extractor = Extractor(input_dir, output_dir, max_workers)
    result = extractor.extract_year(year)
    
    if result:
        print()
        print("="*60)
        print(f"✅ REPROCESSING COMPLETED FOR {year}")
        print("="*60)
        print(f"  Traversing: {result['traversing']:,}")
        print(f"  Cabotage: {result['cabotage']:,}")
        print(f"  Tokens: {result['tokens']:,}")
        print(f"  Files processed: {result['processed']}")
        print()
        
        # Mostrar nuevas estadísticas
        new_stats = db.get_stats()
        print("Updated database statistics:")
        print(f"  • Total traversing: {new_stats['traversing']:,}")
        print(f"  • Total cabotage: {new_stats['cabotage']:,}")
        print(f"  • Total files processed: {new_stats['files_processed']:,}")


def check_missing():
    """Opción 6: Verifica archivos faltantes"""
    print("\n📋 CHECK MISSING FILES")
    input_dir = input("Enter path to OCR directory (e.g., .data/Nuevo): ").strip()
    
    from pathlib import Path
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Directory not found: {input_dir}")
        return
    
    db = ExtractionDB()
    
    # Obtener todos los archivos
    all_files = sorted(input_path.rglob("*.txt"))
    relevant_files = [f for f in all_files if "_V_" in f.name or "_C_" in f.name]
    
    # Obtener archivos procesados
    import sqlite3
    with sqlite3.connect(str(db.db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT file_path FROM processed_files')
        processed = set(row[0] for row in cursor.fetchall())
    
    # Encontrar faltantes
    missing = [f for f in relevant_files if str(f) not in processed]
    
    print()
    print("="*60)
    print("MISSING FILES REPORT")
    print("="*60)
    print(f"Total files found: {len(relevant_files)}")
    print(f"Files processed: {len(processed)}")
    print(f"Files missing: {len(missing)}")
    print()
    
    if missing:
        print("Missing files by year:")
        by_year = {}
        for f in missing:
            year = f.name[:4]
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(f.name)
        
        for year in sorted(by_year.keys()):
            print(f"  {year}: {len(by_year[year])} files")
    else:
        print("✅ All files have been processed!")
    
    print("="*60)


def show_db_stats():
    """Opción 7: Muestra estadísticas de la BD"""
    print("\n📊 DATABASE STATISTICS")
    db = ExtractionDB()
    stats = db.get_stats()
    
    print()
    print("="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"  • Traversing entries: {stats['traversing']:,}")
    print(f"  • Cabotage entries: {stats['cabotage']:,}")
    print(f"  • Files processed: {stats['files_processed']:,}")
    print(f"  • Total entries: {stats['traversing'] + stats['cabotage']:,}")
    print("="*60)


def export_all_years():
    """Opción 8: Exporta todos los años"""
    print("\n💾 EXPORT ALL YEARS")
    output_dir = input("Enter output directory: ").strip()
    
    from utils.export_data import export_year
    
    db = ExtractionDB()
    
    # Obtener años únicos de la BD
    import sqlite3
    with sqlite3.connect(str(db.db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT substr(publication_day, 1, 4) as year 
            FROM travesias 
            UNION 
            SELECT DISTINCT substr(publication_day, 1, 4) as year 
            FROM cabotajes 
            ORDER BY year
        ''')
        years = [row[0] for row in cursor.fetchall()]
    
    if not years:
        print("❌ No data in database")
        return
    
    print(f"\n📅 Years found: {', '.join(years)}")
    print(f"Exporting to: {output_dir}\n")
    
    # Exportar cada año
    for year in years:
        print(f"  Exporting {year}...", end=" ", flush=True)
        try:
            export_year(db, year, output_dir)
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("="*60)
    print("✅ EXPORT COMPLETED")
    print("="*60)
    print(f"Files saved in: {output_dir}/")
    for year in years:
        print(f"  • {year}_traversing.json / .csv")
        print(f"  • {year}_cabotage.json / .csv")


def main():
    while True:
        choice = show_menu()
        if choice == "1":
            concatenate_files_by_date()
        elif choice == "2":
            extract_structured_data()
        elif choice == "3":
            extract_cabotage_data()
        elif choice == "4":
            extract_by_year()
        elif choice == "5":
            reprocess_year()
        elif choice == "6":
            check_missing()
        elif choice == "7":
            show_db_stats()
        elif choice == "8":
            export_all_years()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
