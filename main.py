from utils.utils import read_txt_files_recursively, catch_news_fragment, group_and_concatenate_txt_by_date, extract_cabotage_entries_regex
from utils.utils import compute_important_dates, save_in_csv_file
from llm_service.llm_openai import extract_structured_data_with_openai, extract_news_list_with_openai
from pathlib import Path
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
    print("""
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
    print("2. Extract structured data from concatenated files")
    print("3. Extract Cabotage Entries from Maritime News")
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
    input_dir = input("Enter path to directory with TXT files: ").strip()
    output_dir = input("Enter path to output directory: ").strip()
    file_name = input("Enter name only of output file (CSV and JSON): ").strip()

    all_results = []
    
    print("\nStarting cabotage entry extraction...")
    for file_path in read_txt_files_recursively(input_dir):
        print(f"📄 Processing file: {file_path.name}")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        cabotage_entries = extract_cabotage_entries_regex(content)
        
        if not cabotage_entries:
            print(f"   -> No 'Entradas de Cabotaje' section found in this file.")
            continue
            
        print(f"   -> Found {len(cabotage_entries)} potential entries. Processing with OpenAI...")

        for entry in cabotage_entries:
            structured_data = extract_structured_data_with_openai(entry)
            if structured_data and structured_data.get("ship_name"):
                date_file_str = file_path.stem[:10]
                departure_date, arrival_date = compute_important_dates(
                    date_file_str, 
                    structured_data.get('travel_duration'), 
                    structured_data.get('publication_day')
                )
                structured_data['departure_date'] = departure_date
                structured_data['arrival_date'] = arrival_date
                all_results.append(structured_data)
            else:
                print(f"   ⚠️ Could not process entry: '{entry[:60]}...'")

    if not all_results:
        print("\nNo valid cabotage entries were extracted from any file.")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    json_path = output_path / f"{file_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
    print(f"\n✅ JSON with {len(all_results)} entries saved as: {json_path}")
    
    csv_path = output_path / f"{file_name}.csv"
    save_in_csv_file(str(csv_path), all_results)

def main():
    while True:
        choice = show_menu()
        if choice == "1":
            concatenate_files_by_date()
        elif choice == "2":
            extract_structured_data()
        elif choice =="3":
            extract_cabotage_data()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()