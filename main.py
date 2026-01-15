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
    print("4. Extract BOTH (Traversing + Cabotage)")
    print("5. Extract by YEAR (Professional - 16 threads)")
    print("5b. Extract by MONTH (Professional - 16 threads)")
    print()
    print("DATABASE & ANALYSIS:")
    print("6. Check missing files to process")
    print("7. Show database statistics")
    print("8. Export data (year/month/day/port/ship/captain)")
    print("9. Analyze data (year/port/ship/captain)")
    print("10. Database utilities (backup/reset/optimize)")
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
                departure_date, arrival_date = compute_important_dates(date_file, row['travel_duration'], row['publication_day'])
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
                departure_date, arrival_date = compute_important_dates(
                    entry['date_file'], 
                    row.get('travel_duration'), 
                    row.get('publication_day')
                )
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
                            departure_date, arrival_date = compute_important_dates(
                                date_file, row['travel_duration'], row['publication_day']
                            )
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
                            departure_date, arrival_date = compute_important_dates(
                                date_file, row.get('travel_duration'), row.get('publication_day')
                            )
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
    """Opción 5: Extrae por año, genera 4 archivos por año"""
    input_dir = input("Enter path to OCR directory (e.g., .data/Nuevo): ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    
    try:
        max_workers = int(input("Number of threads (default 16): ").strip() or "16")
    except:
        max_workers = 16
    
    extractor = Extractor(input_dir, output_dir, max_workers)
    extractor.extract_all_years()


def extract_by_month():
    """Opción 5b: Extrae por mes específico"""
    input_dir = input("Enter path to OCR directory (e.g., .data/Nuevo): ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    year = input("Enter year (e.g., 1852): ").strip()
    month = input("Enter month (1-12): ").strip()
    
    try:
        max_workers = int(input("Number of threads (default 16): ").strip() or "16")
    except:
        max_workers = 16
    
    try:
        month = int(month)
        if month < 1 or month > 12:
            print("❌ Invalid month. Must be 1-12")
            return
    except:
        print("❌ Invalid month")
        return
    
    extractor = Extractor(input_dir, output_dir, max_workers)
    result = extractor.extract_month(year, month)
    
    if result:
        print(f"\n✅ Extraction completed for {year}-{month:02d}")
        print(f"   Traversing: {result['traversing']}")
        print(f"   Cabotage: {result['cabotage']}")
        print(f"   Tokens: {result['tokens']:,}")
        print(f"   Files processed: {result['processed']}")


def check_missing():
    """Opción 6: Verifica qué archivos faltan por procesar"""
    import subprocess
    subprocess.run(["python3", "utils/db/check_missing.py", "status"])


def show_db_stats():
    """Opción 7: Muestra estadísticas de la base de datos"""
    import subprocess
    subprocess.run(["python3", "utils/db/db_utils.py", "info"])


def export_data_menu():
    """Opción 8: Menú de exportación"""
    print("\n📊 EXPORT DATA")
    print("="*50)
    print("1. Export year from DB (JSON + CSV)")
    print("2. Export month")
    print("3. Export day")
    print("4. Export by port")
    print("5. Export by ship")
    print("6. Export by captain")
    print("7. List ports")
    print("8. List ships")
    print("9. List captains")
    print("0. Back")
    
    choice = input("Choose option: ").strip()
    
    import subprocess
    
    if choice == "1":
        year = input("Enter year: ").strip()
        output_dir = input("Enter output directory: ").strip()
        subprocess.run(["python3", "utils/export_by_year.py", year, output_dir])
    elif choice == "2":
        year = input("Enter year: ").strip()
        month = input("Enter month (1-12): ").strip()
        output_dir = input("Enter output directory: ").strip()
        subprocess.run(["python3", "utils/export_data.py", "month", year, month, output_dir])
    elif choice == "3":
        year = input("Enter year: ").strip()
        month = input("Enter month (1-12): ").strip()
        day = input("Enter day (1-31): ").strip()
        output_dir = input("Enter output directory: ").strip()
        subprocess.run(["python3", "utils/export_data.py", "day", year, month, day, output_dir])
    elif choice == "4":
        port = input("Enter port name: ").strip()
        output_dir = input("Enter output directory: ").strip()
        subprocess.run(["python3", "utils/export_data.py", "port", port, output_dir])
    elif choice == "5":
        ship = input("Enter ship name: ").strip()
        output_dir = input("Enter output directory: ").strip()
        subprocess.run(["python3", "utils/export_data.py", "ship", ship, output_dir])
    elif choice == "6":
        master = input("Enter captain name: ").strip()
        output_dir = input("Enter output directory: ").strip()
        subprocess.run(["python3", "utils/export_data.py", "master", master, output_dir])
    elif choice == "7":
        subprocess.run(["python3", "utils/export_data.py", "list-ports"])
    elif choice == "8":
        subprocess.run(["python3", "utils/export_data.py", "list-ships"])
    elif choice == "9":
        subprocess.run(["python3", "utils/export_data.py", "list-masters"])


def analyze_data_menu():
    """Opción 9: Menú de análisis"""
    print("\n📈 ANALYZE DATA")
    print("="*50)
    print("1. Analyze year")
    print("2. Analyze port")
    print("3. Analyze ship")
    print("4. Analyze captain")
    print("0. Back")
    
    choice = input("Choose option: ").strip()
    
    import subprocess
    
    if choice == "1":
        year = input("Enter year: ").strip()
        subprocess.run(["python3", "utils/analyze_data.py", "year", year])
    elif choice == "2":
        port = input("Enter port name: ").strip()
        subprocess.run(["python3", "utils/analyze_data.py", "port", port])
    elif choice == "3":
        ship = input("Enter ship name: ").strip()
        subprocess.run(["python3", "utils/analyze_data.py", "ship", ship])
    elif choice == "4":
        master = input("Enter captain name: ").strip()
        subprocess.run(["python3", "utils/analyze_data.py", "master", master])


def db_utils_menu():
    """Opción 10: Menú de utilidades de BD"""
    print("\n🗄️  DATABASE UTILITIES")
    print("="*50)
    print("1. Show database info")
    print("2. Create backup")
    print("3. Delete year data")
    print("4. Delete duplicates")
    print("5. Optimize database")
    print("0. Back")
    
    choice = input("Choose option: ").strip()
    
    import subprocess
    
    if choice == "1":
        subprocess.run(["python3", "utils/db/db_utils.py", "info"])
    elif choice == "2":
        subprocess.run(["python3", "utils/db/db_utils.py", "backup"])
    elif choice == "3":
        year = input("Enter year to delete: ").strip()
        subprocess.run(["python3", "utils/db/db_utils.py", "delete-year", year])
    elif choice == "4":
        subprocess.run(["python3", "utils/db/db_utils.py", "delete-duplicates"])
    elif choice == "5":
        subprocess.run(["python3", "utils/db/db_utils.py", "vacuum"])


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
            extract_both_entries()
        elif choice == "5":
            extract_by_year()
        elif choice == "5b":
            extract_by_month()
        elif choice == "6":
            check_missing()
        elif choice == "7":
            show_db_stats()
        elif choice == "8":
            export_data_menu()
        elif choice == "9":
            analyze_data_menu()
        elif choice == "10":
            db_utils_menu()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()