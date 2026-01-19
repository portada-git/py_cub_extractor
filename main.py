from utils.utils import read_txt_files_recursively, catch_news_fragment, group_and_concatenate_txt_by_date, extract_entradas_cabotaje
from utils.utils import compute_important_dates, save_in_csv_file
from llm_service.llm_openai import extract_structured_data_with_openai, extract_news_list_with_openai, extract_cabotaje_data_with_openai
from utils.extractor import Extractor
from utils.db import ExtractionDB
import json


def process_directory(base_dir: str):
    content_extracted = []
    dates_from_file=[]
    for file_path in read_txt_files_recursively(base_dir):
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        print(f"\n📄 Processing file: {file_path}")
        date_file = file_path.stem[:10]
        dates_from_file.append(date_file)
        cached_news_frag = catch_news_fragment(content)

        content_extracted += cached_news_frag

    return content_extracted, dates_from_file


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
    input_dir = input("Enter path to OCR input directory: ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    group_and_concatenate_txt_by_date(input_dir, output_dir)


def extract_structured_data():
    input_dir = input("Enter path from joined TXT to extract info: ").strip()
    output_dir = input("Enter path to output directory of extraction result: ").strip()
    file_name_json = input("Enter name only of output file (CSV and JSON): ").strip()
    content_extracted, dates_from_file = process_directory(input_dir)

    output_json = f"{output_dir}/{file_name_json}.json"

    results = []
    for content, date_file in zip(content_extracted, dates_from_file):
        news_delimited = extract_news_list_with_openai(content['info_text'])
        news_delimited = news_delimited.split("###")
        for news in news_delimited[1:len(news_delimited)-1]:
            row = extract_structured_data_with_openai(news)
            if 'raw_text' in row and row['raw_text'] is not None:
                try:
                    departure_date, arrival_date = compute_important_dates(date_file, row['travel_duration'], row['publication_day'])
                except ValueError:
                    departure_date, arrival_date = None, None
                row['departure_date'] = departure_date
                row['arrival_date'] = arrival_date
                results.append(row)

    with open(output_json, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=4)

    save_in_csv_file(f"{output_dir}/{file_name_json}.csv", results)

    print(f"\n✅ Extracted {len(results)} valid entries into {output_json}")


def extract_cabotage_data():
    """Extract and process cabotage entries using LLM service"""
    input_dir = input("Enter path from joined TXT to extract cabotage info: ").strip()
    output_dir = input("Enter path to output directory of extraction result: ").strip()
    file_name_json = input("Enter name only of output file (CSV and JSON): ").strip()
    
    all_cabotage_entries = []
    
    for file_path in read_txt_files_recursively(input_dir):
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        print(f"\n📄 Processing file: {file_path}")
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
            
            row = extract_cabotaje_data_with_openai(line)
            if 'raw_text' in row and row['raw_text'] is not None:
                try:
                    departure_date, arrival_date = compute_important_dates(
                        entry['date_file'], 
                        row.get('travel_duration'), 
                        row.get('publication_day')
                    )
                except ValueError:
                    departure_date, arrival_date = None, None
                row['departure_date'] = departure_date
                row['arrival_date'] = arrival_date
                results.append(row)
    
    output_json = f"{output_dir}/{file_name_json}.json"
    
    with open(output_json, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=4)
    
    save_in_csv_file(f"{output_dir}/{file_name_json}.csv", results)
    
    print(f"\n✅ Extracted {len(results)} cabotage entries into {output_json}")


def extract_both_entries():
    """
    Extract both TRAVERSING ENTRANCES and CABOTAGE ENTRIES in a single workflow.
    Processes each file once, extracting both types of entries simultaneously.
    """
    print("\n🚢 Combined Extraction: Traversing + Cabotage")
    
    input_dir = input("Enter path from joined TXT to extract info: ").strip()
    output_dir = input("Enter path to output directory of extraction result: ").strip()
    base_file_name = input("Enter base name for output files: ").strip()

    traversing_results = []
    cabotage_results = []
    traversing_error = None
    cabotage_error = None

    print("\n📍 Processing files for BOTH extraction types...")
    
    try:
        for file_path in read_txt_files_recursively(input_dir):
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            print(f"\n📄 Processing file: {file_path}")
            date_file = file_path.stem[:10]
            
            # --- TRAVERSING EXTRACTION ---
            try:
                cached_news_frag = catch_news_fragment(content)
                for news_frag in cached_news_frag:
                    news_delimited = extract_news_list_with_openai(news_frag['info_text'])
                    news_delimited = news_delimited.split("###")
                    
                    for news in news_delimited[1:len(news_delimited)-1]:
                        row = extract_structured_data_with_openai(news)
                        if 'raw_text' in row and row['raw_text'] is not None:
                            try:
                                departure_date, arrival_date = compute_important_dates(
                                    date_file, row['travel_duration'], row['publication_day']
                                )
                            except ValueError:
                                departure_date, arrival_date = None, None
                            row['departure_date'] = departure_date
                            row['arrival_date'] = arrival_date
                            traversing_results.append(row)
            except Exception as e:
                if traversing_error is None:
                    traversing_error = str(e)
                print(f"   ⚠️ Traversing error in {file_path}: {e}")
            
            # --- CABOTAGE EXTRACTION ---
            try:
                cabotage_sections = extract_entradas_cabotaje(content)
                
                for section in cabotage_sections:
                    lines = [line.strip() for line in section['info_text'].split('\n') 
                             if line.strip() and not line.strip().startswith('ENTRADAS')]
                    
                    for line in lines:
                        if len(line) < 10 or line.isupper():
                            continue
                        row = extract_cabotaje_data_with_openai(line)
                        if 'raw_text' in row and row['raw_text'] is not None:
                            try:
                                departure_date, arrival_date = compute_important_dates(
                                    date_file, row.get('travel_duration'), row.get('publication_day')
                                )
                            except ValueError:
                                departure_date, arrival_date = None, None
                            row['departure_date'] = departure_date
                            row['arrival_date'] = arrival_date
                            cabotage_results.append(row)
            except Exception as e:
                if cabotage_error is None:
                    cabotage_error = str(e)
                print(f"   ⚠️ Cabotage error in {file_path}: {e}")

    except Exception as e:
        print(f"\n❌ Error reading files: {e}")

    # Save traversing results
    if traversing_results:
        traversing_json = f"{output_dir}/{base_file_name}_traversing.json"
        with open(traversing_json, "w", encoding="utf-8") as out:
            json.dump(traversing_results, out, ensure_ascii=False, indent=4)
        save_in_csv_file(f"{output_dir}/{base_file_name}_traversing.csv", traversing_results)

    # Save cabotage results
    if cabotage_results:
        cabotage_json = f"{output_dir}/{base_file_name}_cabotage.json"
        with open(cabotage_json, "w", encoding="utf-8") as out:
            json.dump(cabotage_results, out, ensure_ascii=False, indent=4)
        save_in_csv_file(f"{output_dir}/{base_file_name}_cabotage.csv", cabotage_results)

    # Summary
    print("\n📊 COMBINED EXTRACTION SUMMARY")
    
    if traversing_error:
        print(f"❌ Traversing: PARTIAL/FAILED - {traversing_error}")
    else:
        print(f"✅ Traversing: {len(traversing_results)} entries")
    if traversing_results:
        print(f"   → {output_dir}/{base_file_name}_traversing.json")
        print(f"   → {output_dir}/{base_file_name}_traversing.csv")

    if cabotage_error:
        print(f"❌ Cabotage: PARTIAL/FAILED - {cabotage_error}")
    else:
        print(f"✅ Cabotage: {len(cabotage_results)} entries")
    if cabotage_results:
        print(f"   → {output_dir}/{base_file_name}_cabotage.json")
        print(f"   → {output_dir}/{base_file_name}_cabotage.csv")

    total = len(traversing_results) + len(cabotage_results)
    print(f"\n🎯 Total entries extracted: {total}")



def extract_by_year():
    """Opción 4: Extrae por año (primera vez)"""
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
    """Opción 5: Reprocessa un año, eliminando datos antiguos y reemplazándolos"""
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
    
    # Crear nuevo extractor (esto reinicia el contador de tokens)
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
    """Opción 6: Verifica qué archivos faltan por procesar"""
    from utils.db.check_missing import check_by_year
    check_by_year()


def show_db_stats():
    """Opción 7: Muestra estadísticas de la base de datos por año"""
    from utils.export_data import show_stats_by_year
    db = ExtractionDB()
    show_stats_by_year(db)


def export_all_years():
    """Opción 8: Exporta todos los años de la BD a JSON y CSV"""
    from utils.export_data import export_year
    
    output_dir = input("Enter output directory: ").strip()
    
    db = ExtractionDB()
    
    # Obtener años únicos de la BD usando la instancia de db
    import sqlite3
    with sqlite3.connect(str(db.db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT substr(source_file, 1, 4) as year 
            FROM traversing 
            UNION 
            SELECT DISTINCT substr(source_file, 1, 4) as year 
            FROM cabotage 
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


def analyze_data_menu():
    """Opción 9: Menú de análisis"""
    print("\n📈 ANALYZE DATA")
    print("="*50)
    print("1. Show database statistics")
    print("2. List all ports")
    print("3. List all ships")
    print("4. List all captains")
    print("0. Back")
    
    choice = input("Choose option: ").strip()
    
    from utils.export_data import show_stats, list_ports, list_ships, list_masters
    
    db = ExtractionDB()
    
    if choice == "1":
        show_stats(db)
    elif choice == "2":
        list_ports(db)
    elif choice == "3":
        list_ships(db)
    elif choice == "4":
        list_masters(db)


def db_utils_menu():
    """Opción 10: Menú de utilidades de BD"""
    print("\n🗄️  DATABASE UTILITIES")
    print("="*50)
    print("1. Show database info")
    print("0. Back")
    
    choice = input("Choose option: ").strip()
    
    from utils.export_data import show_stats
    
    if choice == "1":
        db = ExtractionDB()
        show_stats(db)


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