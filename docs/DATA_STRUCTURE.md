# Estructura de Datos - Travesías y Cabotajes

## 1. ¿Se Reprocesarán los Datos?

**NO.** El sistema tiene un mecanismo de deduplicación:

### Tabla `processed_files`
```sql
CREATE TABLE processed_files (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    processed_at TIMESTAMP,
    traversing_count INTEGER,
    cabotage_count INTEGER
)
```

### Flujo de Procesamiento
1. **Extraer enero 1852** → Se procesan 31 archivos
   - Se guardan en `processed_files`
   - Se guardan datos en `traversing` y `cabotage`

2. **Extraer todo 1852** → Se procesan 548 archivos
   - Sistema verifica `processed_files`
   - Salta los 31 archivos de enero (ya procesados)
   - Procesa solo los 517 archivos nuevos

3. **Resultado:** Los datos de enero NO se reprocesarán ni se duplicarán

## 2. Estructura JSON - Travesía

```json
{
  "id": 1,
  "source_file": "1852_01_01",
  "publication_date": "1852-01-01",
  "travel_arrival_date": "1852-01-01",
  "travel_departure_port": "Liverpool",
  "travel_port_of_call_list": null,
  "travel_duration_value": 12,
  "travel_duration_unit": "días",
  "ship_type": "berg.",
  "ship_flag": "esp.",
  "ship_name": "Antio",
  "ship_tons_capacity": 106,
  "ship_tons_unit": "ton.",
  "master_role": "cap.",
  "master_name": "Ranton",
  "crew_number": null,
  "passenger_account": null,
  "cargo_list": [
    {
      "cargo_merchant_name": "Dua ke, H. y comp.",
      "cargo": [
        {
          "cargo_commodity": "vivares y loidines",
          "cargo_quantity": "",
          "cargo_unit": ""
        }
      ]
    }
  ],
  "quarantine": false,
  "forced_arrival": false,
  "parsed_text": "De Liverpool en 12 días, berg. esp. Antio, cap. Ranton, ton. 106, con vivares y loidines, a los Sres. Dua ke, H. y comp.",
  "obs": null,
  "extracted_at": "1852-01-01"
}
```

### Campos Principales - Travesía

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `source_file` | TEXT | Fecha del archivo (YYYY_MM_DD) |
| `publication_date` | TEXT | Fecha de publicación del periódico |
| `travel_arrival_date` | TEXT | Fecha de llegada al puerto (YYYY-MM-DD) |
| `travel_departure_port` | TEXT | Puerto de salida (ej: Liverpool, Nueva York) |
| `travel_port_of_call_list` | TEXT | Puertos intermedios (si los hay) |
| `travel_duration_value` | INTEGER | Número de días/horas |
| `travel_duration_unit` | TEXT | "días", "horas", "d.", "h." |
| `ship_type` | TEXT | Tipo de barco (berg., vap., gol., etc.) |
| `ship_flag` | TEXT | Bandera (esp., am., ing., etc.) |
| `ship_name` | TEXT | Nombre del barco |
| `ship_tons_capacity` | INTEGER | Toneladas de capacidad |
| `ship_tons_unit` | TEXT | "ton.", "tons.", "t." |
| `master_role` | TEXT | "cap.", "pat.", "pil." |
| `master_name` | TEXT | Nombre del capitán |
| `crew_number` | INTEGER | Número de tripulantes |
| `passenger_account` | INTEGER | Número de pasajeros |
| `cargo_list` | JSON | Lista de cargas con destinatarios |
| `quarantine` | BOOLEAN | Si hay cuarentena |
| `forced_arrival` | BOOLEAN | Si es llegada forzosa |
| `parsed_text` | TEXT | Texto original del periódico |
| `obs` | TEXT | Observaciones sobre errores OCR |
| `extracted_at` | TEXT | Fecha de extracción |

## 3. Estructura JSON - Cabotaje

```json
{
  "id": 1,
  "source_file": "1852_01_15",
  "publication_date": "1852-01-15",
  "travel_arrival_date": "1852-01-15",
  "travel_departure_port": "Matanzas",
  "travel_port_of_call_list": null,
  "travel_duration_value": 12,
  "travel_duration_unit": "horas",
  "ship_type": "gol.",
  "ship_flag": "esp.",
  "ship_name": "Alicia",
  "ship_tons_capacity": 45,
  "ship_tons_unit": "ton.",
  "master_role": "pat.",
  "master_name": "Arribi",
  "crew_number": 8,
  "passenger_account": null,
  "cargo_list": [
    {
      "cargo_merchant_name": "Deulofeu é hijo",
      "cargo": [
        {
          "cargo_commodity": "azúcar",
          "cargo_quantity": "50",
          "cargo_unit": "cajas"
        },
        {
          "cargo_commodity": "ron",
          "cargo_quantity": "20",
          "cargo_unit": "barriles"
        }
      ]
    }
  ],
  "quarantine": false,
  "forced_arrival": false,
  "parsed_text": "Matanzas en 12 horas, gol. esp. Alicia, pat. Arribi, trip. 8, ton. 45, con azúcar y ron, á Deulofeu é hijo.",
  "obs": "Cabotaje doméstico. Duración en horas en lugar de días.",
  "extracted_at": "1852-01-15"
}
```

### Diferencias Cabotaje vs Travesía

| Aspecto | Travesía | Cabotaje |
|--------|----------|----------|
| **Duración** | Días (típicamente 5-50) | Horas (típicamente 2-48) |
| **Puertos** | Internacionales (Liverpool, Nueva York) | Domésticos (Matanzas, Cárdenas) |
| **Tipo de barco** | Más variado (berg., vap., etc.) | Más pequeños (gol., paq., bal.) |
| **Tripulación** | Raramente especificada | A veces especificada |
| **Carga** | Más detallada | Menos detallada |

## 4. Estructura de `cargo_list`

```json
"cargo_list": [
  {
    "cargo_merchant_name": "Destinatario o empresa",
    "cargo": [
      {
        "cargo_commodity": "Tipo de producto",
        "cargo_quantity": "Cantidad",
        "cargo_unit": "Unidad (cajas, barriles, etc.)"
      },
      {
        "cargo_commodity": "Otro producto",
        "cargo_quantity": "Cantidad",
        "cargo_unit": "Unidad"
      }
    ]
  },
  {
    "cargo_merchant_name": "Otro destinatario",
    "cargo": [...]
  }
]
```

## 5. Ejemplo de Exportación

Cuando exportas datos con `python3 main.py → Opción 8.1`:

```bash
python3 main.py
→ Opción 8
→ Opción 1 (Export year from DB)
→ Year: 1852
→ Output: .data/output
```

Genera 4 archivos:
- `1852_traversing.json` - Todas las travesías en JSON
- `1852_traversing.csv` - Todas las travesías en CSV
- `1852_cabotage.json` - Todos los cabotajes en JSON
- `1852_cabotage.csv` - Todos los cabotajes en CSV

## 6. Flujo Completo de Extracción

```
1. Extraer enero 1852
   ├─ Procesa 31 archivos
   ├─ Guarda en processed_files
   └─ Guarda datos en traversing/cabotage

2. Extraer febrero 1852
   ├─ Procesa 28 archivos
   ├─ Guarda en processed_files
   └─ Guarda datos en traversing/cabotage

3. Extraer todo 1852
   ├─ Verifica processed_files
   ├─ Salta enero (31 archivos)
   ├─ Salta febrero (28 archivos)
   ├─ Procesa marzo-diciembre (489 archivos)
   └─ Total: 548 archivos procesados, 0 duplicados
```

## 7. Verificar Deduplicación

```bash
# Ver estado por año
python3 main.py → Opción 6

# Ver estadísticas
python3 main.py → Opción 7

# Exportar datos
python3 main.py → Opción 8 → Opción 1
```
