#!/bin/bash
# Script para ejecutar la extracción con el entorno virtual activado

source .venv/bin/activate
source .env

echo "🚀 Starting extraction for 1852..."
echo "=================================="
echo ""

python3 extract_1852.py

echo ""
echo "✅ Extraction complete!"
echo ""
echo "Next steps:"
echo "  1. python3 main.py → Option 6 (check status)"
echo "  2. python3 main.py → Option 7 (show statistics)"
echo "  3. python3 main.py → Option 8.1 (export data)"
