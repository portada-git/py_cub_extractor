import os
from pathlib import Path
from typing import Generator, Union
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

import re
import csv


def read_txt_files_recursively(base_dir: str) -> Generator[Path, None, None]:

    base_path = Path(base_dir)
    if not base_path.is_dir():
        raise ValueError(f"{base_dir} that is not a valid folder.")

    yield from base_path.rglob("*.txt")


def catch_news_fragment(text):

    pattern = re.compile(
        r'(PUERT.+.+HA[\w\W]*?[\n\s]+(?:ENTR[\w\W].*[\n\s])*'
        r'([EFMAMJASOND][a-zA-Z_íÍ]{2,10}\s?\d{0,2}(?=[\-:.]?[\n\s]?))'
        r'([\-:.\n\sA-Z]{1,2}[\w\s\d.,:\-\W]+?(?=\b[A-ZÁÉÍÓÚÜÑ]{5,}(?:\s+[A-ZÁÉÍÓÚÜÑ]{2,})*\b)))',
        re.MULTILINE
    )

    news_collection = []

    for match in pattern.finditer(text):
        news_collection.append(
            {
                "info_text": match.group(0).strip()
            }
        )

    return news_collection

def extract_entradas_cabotaje(text: str) -> list:
    # Case-insensitive regex to handle OCR variations
    pattern = re.compile(
        r'(ENTRADAS\s+DE\s+CAB[O0]TAJE[\w\W]*?[\n\s]+'
        r'([\-:.\n\sA-Z]{1,2}[\w\s\d.,:\-\W]+?(?=\b[A-ZÁÉÍÓÚÜÑ]{5,}(?:\s+[A-ZÁÉÍÓÚÜÑ]{2,})*\b)))',
        re.MULTILINE
    )

    news_collection = []

    for match in pattern.finditer(text):
        news_collection.append(
            {
                "info_text": match.group(0).strip()
            }
        )
            
    return news_collection



def group_and_concatenate_txt_by_date(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group files by date (first 10 characters of the filename: YYYY_MM_DD)
    files_by_date = defaultdict(list)

    for file_path in input_path.rglob("*.txt"):
        filename = file_path.stem  # filename without extension
        if len(filename) >= 10:
            date_key = filename[:10]  # assuming format like '1852_02_03'
            files_by_date[date_key].append(file_path)

    # Process each group
    for date, files in files_by_date.items():
        sorted_files = sorted(files)  # sort by filename

        combined_content = ""
        for file in sorted_files:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                combined_content += f.read().strip() + "\n"

        # Use the first file name as base for output
        base_filename = sorted_files[0].stem
        output_filename = output_path / f"{base_filename}_informationUnit.txt"

        with open(output_filename, "w", encoding="utf-8") as out_f:
            out_f.write(combined_content)

        print(f"✅ Created: {output_filename.name}")


def compute_important_dates(date_str: str, days_elapsed: int, publication_day: None, formato="%Y_%m_%d") -> str:

    if publication_day is not None:
        match = re.search(r'\bD[ií]a[\s:]*?(\d{1,2})\b', publication_day, re.IGNORECASE)
        if match:
            date_str = date_str.split('_')
            if match.group(1) != '0':
                date_str[2] = match.group(1)
            date_str = '_'.join(date_str)

    date_final = datetime.strptime(date_str, formato).date()

    if days_elapsed is not None:
        date_initial = date_final - timedelta(days=days_elapsed)
    else:
        date_initial = date_final

    return date_initial.isoformat(), date_final.isoformat()


def save_in_csv_file(output_file: str, data: list):
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        header = data[0].keys() if len(data) > 0  else []
        writer = csv.DictWriter(file, fieldnames=header, delimiter=";")
        writer.writeheader()
        for row in data:
            row = row.copy()
            if isinstance(row.get("cargo_list"), list):
                row["cargo_list"] = ", ".join(row["cargo_list"])
            writer.writerow(row)

    print(f"✅ CSV saved as: {output_file}")
