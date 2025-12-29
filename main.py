from utils.utils import read_txt_files_recursively, catch_news_fragment, group_and_concatenate_txt_by_date, extract_entradas_cabotaje
from utils.utils import compute_important_dates, save_in_csv_file
from llm_service.llm_openai import extract_structured_data_with_openai, extract_news_list_with_openai, extract_cabotaje_data_with_openai
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
    print("1. Concatenate OCR text files by date")
    print("2. Extract TRAVERSING ENTRANCES")
    print("3. Extract CABOTAGE ENTRIES")
    print("4. Extract BOTH (Traversing + Cabotage)")
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
    Runs both extraction processes sequentially.
    """
    print("\n🚢 Combined Extraction: Traversing + Cabotage")
    
    input_dir = input("Enter path from joined TXT to extract info: ").strip()
    output_dir = input("Enter path to output directory of extraction result: ").strip()
    base_file_name = input("Enter base name for output files: ").strip()
    
    traversing_results = []
    cabotage_results = []
    traversing_error = None
    cabotage_error = None
    
    # Step 1: Extract Traversing Entrances
    print("\n📍 STEP 1: Extracting TRAVERSING ENTRANCES...")
    try:
        content_extracted, dates_from_file = process_directory(input_dir)
        
        for content, date_file in zip(content_extracted, dates_from_file):
            news_delimited = extract_news_list_with_openai(content['info_text'])
            news_delimited = news_delimited.split("###")
            for news in news_delimited[1:len(news_delimited)-1]:
                row = extract_structured_data_with_openai(news)
                if 'raw_text' in row and row['raw_text'] is not None:
                    departure_date, arrival_date = compute_important_dates(date_file, row['travel_duration'], row['publication_day'])
                    row['departure_date'] = departure_date
                    row['arrival_date'] = arrival_date
                    traversing_results.append(row)
        
        traversing_json = f"{output_dir}/{base_file_name}_traversing.json"
        with open(traversing_json, "w", encoding="utf-8") as out:
            json.dump(traversing_results, out, ensure_ascii=False, indent=4)
        save_in_csv_file(f"{output_dir}/{base_file_name}_traversing.csv", traversing_results)
        print(f"\n✅ Extracted {len(traversing_results)} traversing entries")
    except Exception as e:
        traversing_error = str(e)
        print(f"\n❌ Error during traversing extraction: {traversing_error}")
    
    # Step 2: Extract Cabotage Entries
    print("\n📍 STEP 2: Extracting CABOTAGE ENTRIES...")
    try:
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
                    cabotage_results.append(row)
        
        cabotage_json = f"{output_dir}/{base_file_name}_cabotage.json"
        with open(cabotage_json, "w", encoding="utf-8") as out:
            json.dump(cabotage_results, out, ensure_ascii=False, indent=4)
        save_in_csv_file(f"{output_dir}/{base_file_name}_cabotage.csv", cabotage_results)
        print(f"\n✅ Extracted {len(cabotage_results)} cabotage entries")
    except Exception as e:
        cabotage_error = str(e)
        print(f"\n❌ Error during cabotage extraction: {cabotage_error}")
    
    # Summary
    print("\n📊 COMBINED EXTRACTION SUMMARY")
    
    if traversing_error:
        print(f"❌ Traversing: FAILED - {traversing_error}")
    else:
        print(f"✅ Traversing: {len(traversing_results)} entries")
        print(f"   → {output_dir}/{base_file_name}_traversing.json")
        print(f"   → {output_dir}/{base_file_name}_traversing.csv")
    
    if cabotage_error:
        print(f"❌ Cabotage: FAILED - {cabotage_error}")
    else:
        print(f"✅ Cabotage: {len(cabotage_results)} entries")
        print(f"   → {output_dir}/{base_file_name}_cabotage.json")
        print(f"   → {output_dir}/{base_file_name}_cabotage.csv")
    
    total = len(traversing_results) + len(cabotage_results)
    print(f"\n🎯 Total entries extracted: {total}")



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
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()