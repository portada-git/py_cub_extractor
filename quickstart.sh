#!/bin/bash
# Quick start script para el sistema de extracción

echo "🚀 QUICK START - MARITIME DATA EXTRACTION SYSTEM"
echo "=================================================="
echo ""

# Activar entorno
echo "1️⃣  Activating environment..."
source .env
source .venv/bin/activate

# Mostrar opciones
echo ""
echo "2️⃣  Choose an action:"
echo ""
echo "  1) Extract data (Option 5)"
echo "  2) Show database statistics"
echo "  3) Analyze year"
echo "  4) Export year"
echo "  5) Export month"
echo "  6) Export by port"
echo "  7) Export by ship"
echo "  8) Export by captain"
echo "  9) List ports"
echo "  10) List ships"
echo "  11) List captains"
echo "  12) Database info"
echo "  13) Create backup"
echo ""

read -p "Enter option (1-13): " option

case $option in
    1)
        echo ""
        echo "Starting extraction..."
        python3 main.py
        ;;
    2)
        echo ""
        python3 export_data.py stats
        ;;
    3)
        read -p "Enter year: " year
        python3 analyze_data.py year $year
        ;;
    4)
        read -p "Enter year: " year
        read -p "Enter output directory: " output_dir
        python3 export_data.py year $year $output_dir
        ;;
    5)
        read -p "Enter year: " year
        read -p "Enter month (1-12): " month
        read -p "Enter output directory: " output_dir
        python3 export_data.py month $year $month $output_dir
        ;;
    6)
        read -p "Enter port name: " port
        read -p "Enter output directory: " output_dir
        python3 export_data.py port "$port" $output_dir
        ;;
    7)
        read -p "Enter ship name: " ship
        read -p "Enter output directory: " output_dir
        python3 export_data.py ship "$ship" $output_dir
        ;;
    8)
        read -p "Enter captain name: " master
        read -p "Enter output directory: " output_dir
        python3 export_data.py master "$master" $output_dir
        ;;
    9)
        python3 export_data.py list-ports
        ;;
    10)
        python3 export_data.py list-ships
        ;;
    11)
        python3 export_data.py list-masters
        ;;
    12)
        python3 db_utils.py info
        ;;
    13)
        python3 db_utils.py backup
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
