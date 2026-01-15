OPCIÓN 5: EXTRACCIÓN POR AÑO (PROFESIONAL CON BASE DE DATOS)
===========================================================

DESCRIPCIÓN:
- Procesa todos los años disponibles en la carpeta OCR
- Almacena datos en SQLite para reutilización
- Permite exportar por año, mes, día, puerto, barco, capitán
- Genera reportes y análisis de datos
- Identifica automáticamente travesías (_V_) y cabotajes (_C_)
- Procesa línea por línea con IA para máxima precisión

ESTRUCTURA ESPERADA:
.data/Nuevo/
├── 1852/
│   ├── 01/
│   │   ├── 1852_01_01_..._V_*.txt  (travesía)
│   │   ├── 1852_01_01_..._C_*.txt  (cabotaje)
│   │   └── ...
│   ├── 02/
│   └── ...
├── 1887/
├── 1892/
└── 1903/

FLUJO DE TRABAJO:

1. EXTRACCIÓN (Opción 5 en main.py):
   source .env && source .venv/bin/activate && python3 main.py
   → Seleccionar opción 5
   → Ingresar rutas y threads
   → Los datos se guardan en .data/extraction.db

2. EXPORTACIÓN (export_data.py):
   python3 export_data.py stats                              # Ver estadísticas
   python3 export_data.py year 1852 .data/output             # Exportar año
   python3 export_data.py month 1852 1 .data/output          # Exportar mes
   python3 export_data.py day 1852 1 15 .data/output         # Exportar día
   python3 export_data.py port 'Nueva York' .data/output     # Exportar por puerto
   python3 export_data.py ship 'Neptuno' .data/output        # Exportar por barco
   python3 export_data.py master 'Cobos' .data/output        # Exportar por capitán
   python3 export_data.py list-ports                         # Listar puertos
   python3 export_data.py list-ships                         # Listar barcos
   python3 export_data.py list-masters                       # Listar capitanes

3. ANÁLISIS (analyze_data.py):
   python3 analyze_data.py year 1852                         # Analizar año
   python3 analyze_data.py port 'Nueva York'                 # Analizar puerto
   python3 analyze_data.py ship 'Neptuno'                    # Analizar barco
   python3 analyze_data.py master 'Cobos'                    # Analizar capitán

VENTAJAS:
✓ Extrae una sola vez, reutiliza datos
✓ Exporta en múltiples formatos (JSON, CSV)
✓ Permite exportar por año, mes, día, puerto, barco, capitán
✓ Base de datos SQLite (portable, sin dependencias)
✓ Evita reextracciones costosas
✓ Rastreo de archivos procesados
✓ Estadísticas y análisis en tiempo real
✓ Reportes detallados por entidad

CARACTERÍSTICAS:
✓ Regex mejorado para identificar líneas
✓ Procesamiento línea por línea con IA
✓ Logging completo y detallado
✓ Manejo de errores robusto
✓ Información de tokens usados
✓ Recuperación de errores sin perder datos
✓ Análisis de patrones comerciales
✓ Estadísticas de puertos, barcos, capitanes

TESTING:
python test/test_extractor.py

NOTAS:
- Los archivos _V_ contienen travesías (entradas de barcos extranjeros)
- Los archivos _C_ contienen cabotajes (tráfico marítimo doméstico)
- Cada línea se procesa individualmente con IA
- El log muestra todas las llamadas HTTP a OpenAI
- Los tokens se rastrean y se reportan al final
- La base de datos evita duplicados automáticamente
- Los reportes incluyen análisis de cargo, puertos, barcos y capitanes
