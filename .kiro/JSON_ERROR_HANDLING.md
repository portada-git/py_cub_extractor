# JSON Error Handling & Recovery

## Problem
The LLM was returning malformed JSON that couldn't be parsed, causing extraction to fail with:
```
❌ Error parseando JSON para: ENTRADAS DE CABOTAJE...
```

## Root Causes
1. **Model limitations**: GPT-5 nano sometimes returns incomplete or malformed JSON
2. **Complex prompts**: Long prompts with many examples can confuse the model
3. **No fallback**: Previous code had no recovery mechanism for invalid JSON

## Solutions Implemented

### 1. JSON Recovery Mechanism
**Location**: `llm_service/llm_openai.py`

Added regex-based JSON extraction:
```python
# Try to extract valid JSON from malformed response
json_match = re.search(r'\{.*\}', content, re.DOTALL)
if json_match:
    try:
        data = json.loads(json_match.group())
        return data
    except json.JSONDecodeError:
        pass
```

### 2. Graceful Fallback
If JSON cannot be recovered, return valid empty structure:
```python
return {"files": [], "publication_date": None, "entries": []}
```

This prevents crashes and allows extraction to continue.

### 3. Better Logging
- Log when no entries are returned
- Log when entries are rejected (hallucinations)
- Continue processing instead of failing

## Data Flow

```
LLM Response (possibly malformed)
    ↓
Try JSON parse
    ↓
Success? → Return data
    ↓
Fail? → Try regex extraction
    ↓
Success? → Return data
    ↓
Fail? → Return empty structure
    ↓
Extractor processes (empty = skip file)
```

## Benefits

✅ **Resilient**: Handles malformed JSON gracefully
✅ **Continues**: Extraction doesn't crash on bad responses
✅ **Recoverable**: Attempts to extract valid JSON from malformed responses
✅ **Logged**: All issues are logged for debugging
✅ **Safe**: Returns valid structures, never crashes

## Validation Still Applies

Even if JSON is recovered, entries still go through:
1. Sanitization (fix data types)
2. Validation (check required fields)
3. Rejection (if invalid)

So bad data is still filtered out.

## Testing

Run extraction and look for:
- Files that return empty entries (logged as "No entries returned")
- Files that skip entries (logged as "Invalid entry rejected")
- Files that successfully extract data

All should complete without crashes.
