# Actualización de Esquema de Base de Datos

## Cambios Realizados

### 1. Nueva Estructura de Tablas

Las tablas `traversing` y `cabotage` ahora tienen los siguientes campos:

```sql
- id: INTEGER PRIMARY KEY
- source_file: TEXT (fecha del archivo: YYYY_MM_DD)
- publication_date: TEXT (fecha de publicación del periódico)
- travel_arrival_date: TEXT (fecha de llegada: YYYY-MM-DD)
- travel_departure_port: TEXT (puerto de salida)
- travel_port_of_call_list: TEXT (puertos intermedios)
- travel_duration_value: INTEGER (número de días/horas)
- travel_duration_unit: TEXT (días, horas, etc.)
- ship_type: TEXT (vap., berg., gol., etc.)
- ship_flag: TEXT (esp., am., ing., etc.)
- ship_name: TEXT (nombre del barco)
- ship_tons_capacity: INTEGER (toneladas)
- ship_tons_unit: TEXT (ton., tons., t.)
- master_role: TEXT (cap., pat., pil., etc.)
- master_name: TEXT (nombre del capitán)
- crew_number: INTEGER (número de tripulantes)
- passenger_account: INTEGER (número de pasajeros)
- cargo_list: TEXT (JSON con lista de cargas)
- quarantine: BOOLEAN (si hay cuarentena)
- forced_arrival: BOOLEAN (si es llegada forzosa)
- parsed_text: TEXT (texto original)
- obs: TEXT (observaciones sobre errores OCR)
- extracted_at: TEXT (fecha de extracción)
```

### 2. Cambios en el Prompt del LLM

El nuevo prompt extrae todos los campos anteriores con instrucciones claras:

- Identifica tipos de barco válidos (vap., berg., gol., etc.)
- Ignora descriptores de nacionalidad (esp., am., ing.)
- Extrae información de carga con destinatarios
- Incluye observaciones sobre errores OCR
- Usa `null` para campos no encontrados

### 3. Cambios en el Extractor

- `_process_traversing()` ahora usa `parsed_text` en lugar de `raw_text`
- `_process_cabotage()` ahora usa `parsed_text` en lugar de `raw_text`
- Ambos métodos agregan `publication_date` y `extracted_at` automáticamente

### 4. Cambios en la BD

- `save_traversing()` ahora inserta todos los nuevos campos
- `save_cabotage()` ahora inserta todos los nuevos campos
- Ambos métodos convierten `cargo_list` a JSON

## Ejemplo de Datos Extraídos

```json
{
  "travel_arrival_date": "1852-01-27",
  "travel_departure_port": "Mallorca",
  "travel_port_of_call_list": null,
  "travel_duration_value": 42,
  "travel_duration_unit": "días",
  "ship_type": "pol.",
  "ship_flag": "csp.",
  "ship_name": "Isabel",
  "ship_tons_capacity": 157,
  "ship_tons_unit": "ton.",
  "master_role": "cap.",
  "master_name": "Palmer",
  "crew_number": null,
  "passenger_account": null,
  "cargo_list": [
    {
      "cargo_merchant_name": "D. F. Ventosa",
      "cargo": [
        {
          "cargo_commodity": "frutos",
          "cargo_quantity": "",
          "cargo_unit": ""
        }
      ]
    }
  ],
  "quarantine": false,
  "forced_arrival": false,
  "parsed_text": "De Mallorca en 42 dias pol. csp. Isabel, cap. Palmer, ton 157, con frutos, á D. F. Ventosa.",
  "obs": "Bandera 'csp.' probable error OCR por 'esp.'. Tipo de barco 'pol.' probablemente 'gol.' (goleta) o 'pol.' (polacra)."
}
```

## Próximos Pasos

1. Eliminar la BD anterior: `rm -f .data/extraction.db`
2. Procesar todos los años: `python3 process_all_years.py`
3. Verificar que los datos se extraen correctamente
4. Exportar datos: `python3 main.py → Opción 8.1`
