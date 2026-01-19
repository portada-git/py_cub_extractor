# Hallucination Mitigation Strategy

## Problem
The GPT-5 nano model was generating hallucinated data (inventing fields that don't exist in the source text) and had temperature parameter restrictions.

## Solutions Implemented

### 1. Temperature Parameter Fix
- **Issue**: GPT-5 nano only supports default temperature (1), custom values like 0.1 are rejected
- **Solution**: Removed temperature parameter entirely, using model defaults
- **Impact**: Model now uses its default deterministic behavior

### 2. Enhanced System Prompts
Added explicit anti-hallucination rules to system prompts:
```
REGLAS CRÍTICAS:
1. Si no encuentras información clara para algún campo, DEBES responder con null (NUNCA inventes datos)
2. NO ALUCINES: Si un campo no está en el texto, usa null
3. SOLO extrae lo que está EXPLÍCITAMENTE en el texto
4. Los campos obligatorios son: publication_day, travel_arrival_date, parsed_text
5. Para fechas, usa SIEMPRE formato YYYY-MM-DD
6. Para listas (travel_port_of_call_list), usa arrays JSON
7. Para números, usa valores numéricos (sin comillas)
8. Para booleanos, usa true/false (sin comillas)
9. Verifica CADA campo antes de incluirlo - si no está seguro, usa null
```

### 3. Entry Validation Function
**Location**: `llm_service/llm_openai.py::validate_entry()`

Validates entries for:
- Required fields: `parsed_text`, `publication_day`, `travel_arrival_date`
- Date format compliance (YYYY-MM-DD)
- Type correctness (lists, numbers, booleans)
- Minimum text length (5+ characters)

Returns `True` only if entry passes all checks.

### 4. Entry Sanitization Function
**Location**: `llm_service/llm_openai.py::sanitize_entry()`

Cleans entries by:
- Converting invalid types to `null`
- Validating date formats
- Ensuring lists are actual arrays
- Ensuring numbers are numeric types
- Ensuring booleans are boolean types
- Removing entries with invalid `parsed_text`

### 5. Extractor Integration
**Location**: `utils/extractor.py`

Updated both `_process_traversing()` and `_process_cabotage()`:
1. Sanitize each entry from LLM
2. Validate sanitized entry
3. Log rejected entries (hallucinations detected)
4. Only add valid entries to results

## Data Flow

```
LLM Response
    ↓
Sanitize Entry (convert invalid types to null)
    ↓
Validate Entry (check required fields, formats, types)
    ↓
Valid? → Add to Results
    ↓
Invalid? → Log rejection + skip
```

## Benefits

✅ **Prevents hallucinations** - Invalid data is rejected before database insertion
✅ **Type safety** - All data types are validated
✅ **Format compliance** - Dates, lists, numbers follow specifications
✅ **Audit trail** - Rejected entries are logged for review
✅ **Data quality** - Only high-quality, validated data reaches database

## Testing

To verify the system works:
1. Run extraction on a test year
2. Check logs for "Invalid entry rejected (hallucination detected)" messages
3. Verify database contains only valid entries
4. Compare entry counts before/after validation

## Future Improvements

- Add confidence scoring for extracted fields
- Implement retry logic for low-confidence extractions
- Add field-level validation rules
- Create hallucination report dashboard
