OPCIÓN 5: EXTRACCIÓN POR AÑO (PROFESIONAL)
============================================

DESCRIPCIÓN:
- Procesa todos los años disponibles en la carpeta OCR
- Genera 4 archivos por año:
  * {año}_traversing.json
  * {año}_traversing.csv
  * {año}_cabotage.json
  * {año}_cabotage.csv

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

CÓMO USAR:
1. Ejecutar: python main.py
2. Seleccionar opción: 5
3. Ingresar:
   - Ruta OCR: .data/Nuevo
   - Ruta salida: .data/output
   - Threads: 8 (o el número que prefieras)

SALIDA:
- Archivos JSON y CSV en la carpeta de salida
- Log detallado: extraction_YYYYMMDD_HHMMSS.log
- Progreso en tiempo real en la consola

CARACTERÍSTICAS:
✓ Logging completo y detallado
✓ Procesamiento paralelo por threads
✓ Manejo de errores robusto
✓ Progreso visible con barra de progreso
✓ 4 archivos por año (JSON + CSV para cada tipo)
✓ Información de tokens usados
✓ Recuperación de errores sin perder datos

TESTING:
python test/test_extractor.py
