# Cuban Maritime Data Extraction System

Professional OCR-based maritime data extraction system for historical newspaper records (1850-1915) from Diario de la Marina.

## Features

- **Structured Data Extraction**: Extracts traversing and cabotage entries from OCR documents
- **LLM-Powered**: Uses OpenAI GPT-4o-mini for intelligent text parsing
- **SQLite Database**: Persistent storage with efficient querying
- **Multi-threaded Processing**: 16 concurrent workers for fast extraction
- **Flexible Export**: JSON and CSV formats with field filtering
- **Year-based Organization**: Process data by year with reprocessing capability

## Project Structure

```
.
├── main.py                          # Main menu interface
├── requirements.txt                 # Python dependencies
├── llm_service/
│   ├── llm_openai.py               # OpenAI API integration
│   └── openai_key.txt              # Encrypted API key
├── utils/
│   ├── extractor.py                # Core extraction engine
│   ├── export_data.py              # Export functionality
│   ├── utils.py                    # Text processing utilities
│   └── db/
│       ├── database.py             # SQLite database operations
│       └── check_missing.py        # File verification
├── .data/
│   ├── Nuevo/                      # OCR input files (organized by year)
│   ├── extraction.db               # Main SQLite database
│   └── results/                    # Export output directory
└── docs/
    ├── README.md                   # English documentation
    ├── README_ES.md                # Spanish documentation
    └── README_EL.md                # Greek documentation
```

## Installation

1. Clone the repository
2. Create virtual environment: `python3 -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set OpenAI API key: `export OPENAI_API_KEY=your_key_here`

## Usage

Run the main menu:
```bash
python3 main.py
```

### Menu Options

#### EXTRACTION OPTIONS

**1. Concatenate OCR text files by date**
- Groups OCR files by date
- Combines multiple files into single date-based files
- Useful for preprocessing raw OCR data
- Input: Directory with OCR files
- Output: Concatenated text files organized by date

**2. Extract TRAVERSING ENTRANCES**
- Extracts international ship arrivals from concatenated text
- Uses LLM to parse unstructured OCR text
- Outputs JSON and CSV files
- Input: Directory with concatenated text files
- Output: JSON and CSV with structured data

**3. Extract CABOTAGE ENTRIES**
- Extracts domestic/regional ship arrivals from concatenated text
- Uses LLM to parse unstructured OCR text
- Outputs JSON and CSV files
- Input: Directory with concatenated text files
- Output: JSON and CSV with structured data

**4. Extract TRAVERSING ENTRANCES, CABOTAGE ENTRIES by YEAR (by threads)**
- Extracts both types simultaneously by year
- Uses 16 concurrent threads (configurable)
- Stores directly in SQLite database
- Skips already-processed files automatically
- Shows progress and statistics
- Input: OCR directory (`.data/Nuevo/`), year to process
- Output: Data stored in SQLite database

#### DATABASE & ANALYSIS

**5. Reprocess YEAR (delete old data and re-extract)**
- Deletes all data for a specific year from database
- Re-extracts from OCR files with current LLM prompts
- Useful for updating with improved extraction rules
- Shows before/after statistics
- Requires confirmation before deletion
- Input: Year to reprocess
- Output: Updated database with new data

**6. Check missing files to process**
- Compares OCR files in filesystem with database records
- Shows which files haven't been processed yet
- Displays statistics by year
- Helps identify incomplete extractions
- Input: OCR directory path
- Output: List of missing files by year

**7. Show database statistics**
- Displays entry counts by year
- Shows traversing vs cabotage breakdown
- Total entries and years in database
- Formatted table for easy reading
- No input required
- Output: Statistics table

**8. Export all years (JSON + CSV)**
- Exports entire database to files
- Creates separate files for each year
- Generates both traversing and cabotage exports
- Removes internal fields (id, obs) from exports
- Converts cargo_list to readable format
- Input: Output directory path
- Output: JSON and CSV files for each year

**0. Exit**
- Closes the application

## Data Structure

### Traversing Entry (International Arrivals)
```json
{
  "source_file": "1852_01_01",
  "publication_day": "1852-01-01",
  "arrival_date": "1852-01-01",
  "arrival_date_calc": "1852-01-01",
  "travel_departure_port": "Liverpool",
  "ship_type": "bergantín",
  "ship_flag": "esp.",
  "ship_name": "María",
  "master_role": "cap.",
  "master_name": "García",
  "cargo_list": [
    {
      "cargo_merchant_name": "Lawton y Hnos.",
      "cargo": [
        {
          "cargo_commodity": "algodón",
          "cargo_quantity": "100",
          "cargo_unit": "balas"
        }
      ]
    }
  ],
  "raw_text": "De Liverpool en 12 días, bergantín español María, capitán García..."
}
```

### Cabotage Entry (Domestic Arrivals)
```json
{
  "source_file": "1852_01_01",
  "publication_day": "1852-01-01",
  "travel_arrival_date": "1852-01-01",
  "travel_departure_port": "Matanzas",
  "ship_type": "goleta",
  "ship_flag": null,
  "ship_name": "Esperanza",
  "master_role": "pat.",
  "master_name": "López",
  "cargo_list": [
    {
      "cargo_merchant_name": "a la orden",
      "cargo": [
        {
          "cargo_commodity": "azúcar",
          "cargo_quantity": "50",
          "cargo_unit": "cajas"
        }
      ]
    }
  ],
  "raw_text": "De Matanzas en 12 horas, goleta Esperanza, patrón López..."
}
```

## Database Schema

### traversing table
- `id`: Primary key
- `source_file`: Source file identifier (YYYY_MM_DD)
- `publication_day`: Publication date (YYYY-MM-DD)
- `arrival_date`: Arrival date (YYYY-MM-DD)
- `arrival_date_calc`: Calculated arrival date
- `travel_departure_port`: Port of departure
- `ship_type`: Type of vessel
- `ship_flag`: Flag/nationality
- `ship_name`: Name of ship
- `master_role`: Captain/patron role
- `master_name`: Captain/patron name
- `cargo_list`: JSON array of cargo items
- `raw_text`: Original extracted text
- `travel_duration_value`: Travel duration (numeric)
- `travel_duration_unit`: Duration unit (days/hours)
- `ship_tons_capacity`: Ship tonnage capacity
- `ship_tons_unit`: Tonnage unit
- `crew_number`: Crew size
- `passenger_account`: Passenger count
- `quarantine`: Quarantine status
- `forced_arrival`: Forced arrival indicator
- `obs`: Observations/notes
- `parsed_text`: Parsed text representation

### cabotage table
Same structure as traversing table

### processed_files table
- `id`: Primary key
- `file_path`: Path to processed file
- `processed_at`: Processing timestamp
- `traversing_count`: Traversing entries extracted
- `cabotage_count`: Cabotage entries extracted

## Configuration

### OpenAI API Key
Store encrypted in `llm_service/openai_key.txt`:
```bash
export ADATROP_TERCES=your_encryption_key
```

### Database Path
Default: `.data/extraction.db`
Modify in code or pass as parameter to `ExtractionDB()`

### Thread Count
Default: 16 workers
Configurable when running extraction options

## Performance

- **Processing Speed**: ~100-200 entries per minute (depends on LLM API)
- **Database Size**: ~500MB for 60,000+ entries
- **Memory Usage**: ~2GB with 16 concurrent threads
- **Token Usage**: ~0.5-1.0 tokens per entry

## Error Handling

- Invalid OCR text is skipped
- Duplicate entries are ignored (UNIQUE constraint)
- Failed API calls are logged
- Database backups created before migrations

## Troubleshooting

### No files found
- Verify OCR files are in `.data/Nuevo/YYYY/` structure
- Check file naming: `YYYY_MM_DD_*_V_*.txt` (traversing) or `*_C_*.txt` (cabotage)

### Database errors
- Check `.data/extraction.db` permissions
- Verify SQLite is installed
- Review logs in `.data/output/`

### API errors
- Verify OpenAI API key is set
- Check token balance
- Review rate limits

## Development

### Adding new extraction types
1. Create new LLM prompt in `llm_service/llm_openai.py`
2. Add extraction method in `utils/extractor.py`
3. Add database table in `utils/db/database.py`
4. Add menu option in `main.py`

### Testing
Run individual components:
```bash
python3 -c "from utils.db import ExtractionDB; db = ExtractionDB(); print(db.get_stats())"
```

## Documentation

Available in multiple languages:
- **English**: README.md (this file)
- **Spanish**: docs/README_ES.md
- **Greek**: docs/README_EL.md

## License

Historical data extraction for research purposes.

## Support

For issues or questions, review the logs in `.data/output/` directory.
