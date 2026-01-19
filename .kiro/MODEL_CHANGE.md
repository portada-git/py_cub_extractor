# Model Change: GPT-5 Nano → GPT-4o Mini

## Problem
GPT-5 nano processed 538 files but saved 0 entries:
- Used 120,444 tokens
- All entries were rejected by validation
- Model was not following the JSON structure correctly

## Root Cause
GPT-5 nano limitations:
- ❌ No temperature control (only default=1)
- ❌ Uses `max_completion_tokens` instead of `max_tokens`
- ❌ Poor JSON structure compliance
- ❌ High hallucination rate
- ❌ Inconsistent field extraction

## Solution
Switched to **GPT-4o Mini**:
- ✅ Supports temperature control (0.3)
- ✅ Uses standard `max_tokens` parameter
- ✅ Better JSON structure compliance
- ✅ Lower hallucination rate
- ✅ More reliable field extraction
- ✅ Better cost/performance ratio

## Changes Made

### 1. Model Name
```python
# Before
model="gpt-5-nano-2025-08-07"

# After
model="gpt-4o-mini"
```

### 2. Token Parameter
```python
# Before (GPT-5 nano)
max_completion_tokens=4000

# After (GPT-4o mini)
max_tokens=4000
```

### 3. Temperature
```python
# Before (not supported)
# No temperature parameter

# After (supported)
temperature=0.3
```

## Next Steps

1. **Delete 1850 data** (already processed with bad model):
   ```
   Option 5: Reprocess YEAR
   Enter year: 1850
   ```

2. **Reprocess with new model**:
   - Will use GPT-4o mini
   - Should extract valid entries
   - Better validation pass rate

## Expected Results

With GPT-4o mini:
- ✅ Valid JSON responses
- ✅ Correct field extraction
- ✅ Entries pass validation
- ✅ Data saved to database
- ✅ Better accuracy

## Cost Comparison

| Model | Input | Output | Quality |
|-------|-------|--------|---------|
| GPT-5 nano | $0.15/1M | $0.60/1M | ❌ Poor |
| GPT-4o mini | $0.15/1M | $0.60/1M | ✅ Good |

Same cost, better quality!
