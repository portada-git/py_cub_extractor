# Cuban Maritime Data Extractor

Professional OCR data extraction system for historical maritime records from the *Diario de la Marina* newspaper (1850-1915). Extracts structured information about ship arrivals at the Port of Havana using AI-powered text processing.

## Overview

This system processes OCR-digitized newspaper documents to extract and structure maritime data including:
- **Traversing Entries** (Travesías): International ship arrivals with full voyage details
- **Cabotage Entries** (Cabotajes): Domestic coastal ship arrivals

Data is extracted using OpenAI's GPT-4 API with intelligent error correction for OCR artifacts and historical spelling variations.

## Features

- **Multi-threaded Extraction**: 16 concurrent workers for fast processing
- **SQLite Database**: Persistent storage with duplicate detection
- **Structured Output**: JSON and CSV exports with complete maritime metadata
- **Smart Filtering**: Automatic removal of incomplete entries and page fragments
- **Token Tracking**: Monitor API usage and costs
- **Incremental Processing**: Skip already-processed files automatically

## Project Structure

```
py_cub_extractor/
├── llm_service/                    # OpenAI API integration
│   ├── __init__.py
│   ├── llm_openai.py              # LLM extraction functions (GPT-4)
│   ├── llm_ollama.py              # Alternative Ollama integration
│   └── openai_key.txt             # Encrypted API key
│
├── utils/                          # Core utilities
│   ├── __init__.py
│   ├── extractor.py               # Main extraction engine (16 threads)
│   ├── export_data.py             # JSON/CSV export functions
│   ├── utils.py                   # Text processing utilities
│   ├── decrypt.py                 # API key decryption
│   ├── analyze_data.py            # Data analysis tools
│   ├── count_json.py              # JSON counting utility
│   │
│   └── db/                        # Database layer
│       ├── __init__.py
│       ├── database.py            # SQLite schema and operations
│       ├── migrate.py             # Database migration tools
│       ├── reset.py               # Database reset utilities
│       ├── inspect.py             # Database inspection tool
│       ├── check_missing.py       # Missing files checker
│       └── db_utils.py            # Database utilities
│
├── .data/                         # Data directory
│   ├── Nuevo/                     # OCR input files (organized by year/month)
│   │   ├── 1852/
│   │   │   ├── 01/
│   │   │   ├── 02/
│   │   │   └── ...
│   │   ├── 1887/
│   │   └── ...
│   ├── output/                    # Processing logs
│   ├── results/                   # JSON and CSV exports
│   └── extraction.db              # SQLite database
│
├── main.py                        # Main interactive menu
├── extract_1852.py                # Quick extraction script
├── extract_month.py               # Month extraction script
├── export_month.py                # Month export script
├── export_all_years.py            # Full database export script
├── count_all_json.py              # Count entries in JSON files
│
├── test_extraction.py             # Unit tests
├── test_cabotage_extraction.py    # Cabotage tests
├── test_january_1852.py           # Specific date tests
│
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
├── quickstart.sh                  # Quick start script
├── run_extraction.sh              # Extraction runner script
│
├── README.md                      # This file
├── USAGE_GUIDE.md                 # Detailed usage guide
└── SCHEMA_UPDATE.md               # Schema documentation
```

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd py_cub_extractor
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Main Menu

Run the interactive menu:
```bash
python3 main.py
```

**Available Options:**

1. **Concatenate OCR text files by date** - Merge multiple OCR files by publication date
2. **Extract TRAVERSING ENTRANCES** - Extract international ship arrivals
3. **Extract CABOTAGE ENTRIES** - Extract domestic ship arrivals
4. **Extract TRAVERSING ENTRANCES, CABOTAGE ENTRIES by YEAR (by threads)** - Professional extraction with 16 threads
5. **Check missing files to process** - Identify unprocessed files
6. **Show database statistics** - View extraction summary
7. **Export all years (JSON + CSV)** - Export entire database to files
0. **Exit**

### Quick Extraction

Extract a specific year:
```bash
python3 extract_1852.py
```

### Export Data

Export all years to JSON and CSV:
```bash
python3 export_all_years.py
```

Export specific year:
```bash
python3 export_month.py
```

## Data Structure

### Traversing Entry (Travesía)

```json
{
  "publication_day": "1876-01-12",
  "travel_arrival_date": "1876-01-10",
  "travel_departure_port": "Buenos Aires",
  "travel_port_of_call_list": ["Santiago de Cuba"],
  "travel_duration_value": 13,
  "travel_duration_unit": "días",
  "ship_type": "berg.",
  "ship_flag": "esp.",
  "ship_name": "Tola",
  "ship_tons_capacity": 121,
  "ship_tons_unit": "tons.",
  "master_role": "cap.",
  "master_name": "Moreno",
  "crew_number": 10,
  "passenger_account": null,
  "cargo_list": [
    {
      "cargo_merchant_name": "R. Morales y cp",
      "cargo": [
        {
          "cargo_commodity": "sal",
          "cargo_quantity": "",
          "cargo_unit": ""
        }
      ]
    }
  ],
  "quarantine": false,
  "forced_arrival": false,
  "parsed_text": "De Buenos Aires en 13 dias berg. esp. Tola cap. Moreno, tons. 121, trip. 10. con sal, a R. Morales y cp.",
  "obs": ""
}
```

### Cabotage Entry (Cabotaje)

Same structure as traversing entries, with:
- Typically no `travel_port_of_call_list` (domestic routes)
- Shorter voyage durations
- Master role usually "pat." (patrón/skipper)
- No crew or passenger information

## Database

### Schema

**traversing** table:
- `id` (PRIMARY KEY)
- `source_file` - OCR filename (YYYY_MM_DD format)
- `publication_day` - Newspaper publication date (YYYY-MM-DD)
- `travel_arrival_date` - Ship arrival date (YYYY-MM-DD)
- `travel_departure_port` - Origin port
- `travel_port_of_call_list` - Intermediate ports (JSON array)
- `travel_duration_value` - Journey duration (numeric)
- `travel_duration_unit` - Duration unit (days/hours)
- `ship_type` - Vessel type (bergantín, goleta, vapor, etc.)
- `ship_flag` - Flag country
- `ship_name` - Vessel name
- `ship_tons_capacity` - Tonnage capacity
- `ship_tons_unit` - Tonnage unit
- `master_role` - Captain role (cap./pat./pil.)
- `master_name` - Captain name
- `crew_number` - Crew size
- `passenger_account` - Passenger count
- `cargo_list` - Cargo details (JSON)
- `quarantine` - Quarantine status (boolean)
- `forced_arrival` - Forced arrival status (boolean)
- `parsed_text` - Original text
- `obs` - Observations

**cabotage** table: Identical schema to traversing

**processed_files** table:
- `id` (PRIMARY KEY)
- `file_path` - Full file path
- `processed_at` - Processing timestamp
- `traversing_count` - Entries extracted
- `cabotage_count` - Entries extracted

### Database Operations

Check database statistics:
```bash
python3 -m utils.db.inspect
```

Migrate database schema:
```bash
python3 -m utils.db.migrate
```

Reset database:
```bash
python3 -m utils.db.reset
```

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your-api-key
ADATROP_TERCES=encryption-key  # For encrypted API key storage
```

### Input Directory Structure

```
.data/Nuevo/
├── 1852/
│   ├── 01/  # January
│   │   ├── 1852_01_01_HAB_DM_U_01_0_V_003-001.txt
│   │   └── ...
│   ├── 02/  # February
│   └── ...
├── 1887/
└── ...
```

Files must follow naming convention: `YYYY_MM_DD_*_V_*.txt` (traversing) or `*_C_*.txt` (cabotage)

## Processing Pipeline

1. **File Discovery** - Scan OCR directory for unprocessed files
2. **Text Extraction** - Read and parse OCR text
3. **Line Filtering** - Remove incomplete entries and page fragments
4. **LLM Processing** - Send to OpenAI for structured extraction
5. **Database Storage** - Save to SQLite with duplicate detection
6. **Export** - Generate JSON and CSV files

## Performance

- **Processing Speed**: ~2-3 seconds per entry (including API calls)
- **Threads**: 16 concurrent workers
- **API Costs**: ~$0.001-0.002 per entry (GPT-4o-mini)
- **Database Size**: ~50MB per 10,000 entries

## Error Handling

The system automatically:
- Skips already-processed files
- Filters incomplete entries (fragments, page notes)
- Corrects common OCR errors using semantic analysis
- Handles missing or null fields gracefully
- Logs all errors with timestamps

## Troubleshooting

### API Key Issues
```bash
export OPENAI_API_KEY="your-key"
python3 main.py
```

### Database Errors
Reset and reinitialize:
```bash
python3 -m utils.db.reset
```

### Missing Files
Check what needs processing:
```bash
python3 main.py  # Option 5
```

## Output Files

### JSON Format
- `YYYY_traversing.json` - All traversing entries for year
- `YYYY_cabotage.json` - All cabotage entries for year

### CSV Format
- `YYYY_traversing.csv` - Semicolon-delimited export
- `YYYY_cabotage.csv` - Semicolon-delimited export

Fields are automatically formatted for readability (cargo lists, dates, etc.)

## Development

### Adding New Features

1. Update LLM prompts in `llm_service/llm_openai.py`
2. Modify extraction logic in `utils/extractor.py`
3. Update database schema in `utils/db/database.py`
4. Add menu options in `main.py`

### Testing

Run extraction on sample data:
```bash
python3 extract_month.py
```

Verify output:
```bash
python3 count_all_json.py
```

## License

[Specify your license here]

## Contributors

[List contributors]

## Support

For issues or questions, please open an issue on the repository.

## Changelog

### v1.0.0 (Current)
- Initial release
- Support for traversing and cabotage entries
- Multi-threaded extraction
- SQLite database with incremental processing
- JSON and CSV export
- OpenAI GPT-4 integration
