# Sistema de Extracción de Datos Marítimos Cubanos

Sistema profesional de extracción de datos basado en OCR para registros históricos de periódicos (1850-1915) del Diario de la Marina.

## 🌍 Idiomas de Documentación

- 🇬🇧 **English** - [README.md](../README.md)
- 🇪🇸 **Español** (actual) - [docs/README_ES.md](README_ES.md)
- 🇬🇷 **Ελληνικά** - [docs/README_EL.md](README_EL.md)

---

## Características

- **Extracción de Datos Estructurados**: Extrae entradas de travesías y cabotajes de documentos OCR
- **Potenciado por IA**: Utiliza OpenAI GPT-4o-mini para análisis inteligente de texto
- **Base de Datos SQLite**: Almacenamiento persistente con consultas eficientes
- **Procesamiento Multi-hilo**: 16 trabajadores concurrentes para extracción rápida
- **Exportación Flexible**: Formatos JSON y CSV con filtrado de campos
- **Organización por Año**: Procesa datos por año con capacidad de reprocesamiento

## Estructura del Proyecto

```
.
├── main.py                          # Interfaz de menú principal
├── requirements.txt                 # Dependencias de Python
├── README.md                        # Este archivo (Inglés)
├── llm_service/
│   ├── llm_openai.py               # Integración con OpenAI API
│   └── openai_key.txt              # Clave API encriptada
├── utils/
│   ├── extractor.py                # Motor de extracción principal
│   ├── export_data.py              # Funcionalidad de exportación
│   ├── utils.py                    # Utilidades de procesamiento de texto
│   └── db/
│       ├── database.py             # Operaciones de base de datos SQLite
│       └── check_missing.py        # Verificación de archivos
├── .data/
│   ├── Nuevo/                      # Archivos OCR de entrada (ver estructura abajo)
│   ├── extraction.db               # Base de datos SQLite principal
│   └── results/                    # Directorio de salida de exportación
└── docs/
    ├── INDEX.md                    # Índice de documentación
    ├── README.md                   # Documentación en inglés
    ├── README_ES.md                # Documentación en español
    └── README_EL.md                # Documentación en griego
```

## Estructura de Directorio OCR de Entrada

Esta es la **estructura exacta** requerida para que el sistema detecte y procese correctamente los archivos:

### Jerarquía de Directorios

```
.data/Nuevo/
├── 1850/
│   ├── 01/
│   │   ├── 1850_01_01_HAB_DM_U_01_0_V_003-001.txt
│   │   ├── 1850_01_01_HAB_DM_U_01_0_C_003-001.txt
│   │   ├── 1850_01_02_HAB_DM_U_01_0_V_003-001.txt
│   │   └── ...
│   ├── 02/
│   │   ├── 1850_02_01_HAB_DM_U_01_0_V_003-001.txt
│   │   ├── 1850_02_01_HAB_DM_U_01_0_C_003-001.txt
│   │   └── ...
│   └── 12/
│       └── ...
├── 1852/
│   ├── 01/
│   │   ├── 1852_01_01_HAB_DM_U_01_0_V_003-001.txt
│   │   ├── 1852_01_01_HAB_DM_U_01_0_C_003-001.txt
│   │   └── ...
│   ├── 02/
│   └── ...
├── 1857/
├── 1860/
└── ... (otros años)
```

### Reglas de Estructura de Directorios

**Directorios de Año**
- Formato: `YYYY` (año de 4 dígitos)
- Ejemplos: `1850`, `1852`, `1876`, `1914`
- Ubicación: `.data/Nuevo/YYYY/`

**Directorios de Mes**
- Formato: `MM` (mes de 2 dígitos, con cero a la izquierda)
- Rango: `01` a `12`
- Ubicación: `.data/Nuevo/YYYY/MM/`
- Ejemplos: `01` (Enero), `02` (Febrero), `12` (Diciembre)

**Directorios de Día**
- NO SE UTILIZAN - Los archivos están directamente en directorios de mes
- Los archivos se identifican por fecha en el nombre de archivo, no por estructura de directorio

### Convención de Nombres de Archivos OCR

Todos los archivos OCR deben seguir este patrón de nombre exacto:

```
YYYY_MM_DD_HAB_DM_U_01_0_[TIPO]_NNN-NNN.txt
```

**Componentes del Nombre de Archivo:**

| Componente | Formato | Ejemplo | Descripción |
|-----------|---------|---------|-------------|
| Año | `YYYY` | `1852` | Año de 4 dígitos |
| Mes | `MM` | `01` | Mes de 2 dígitos (01-12) |
| Día | `DD` | `15` | Día de 2 dígitos (01-31) |
| Ubicación | `HAB` | `HAB` | La Habana (fijo) |
| Publicación | `DM` | `DM` | Diario de la Marina (fijo) |
| Edición | `U` | `U` | Identificador de edición (fijo) |
| Número | `01` | `01` | Número de edición (fijo) |
| Página | `0` | `0` | Número de página (fijo) |
| **TIPO** | `V` o `C` | `V` | **CRÍTICO: Determina el tipo de entrada** |
| Secuencia | `NNN-NNN` | `003-001` | Identificador de secuencia |

### Detección de Tipo de Archivo

El sistema detecta tipos de entrada por el componente `TIPO` en el nombre de archivo:

**Entradas de Travesía (Llegadas Internacionales)**
- Nombre de archivo contiene: `_V_` (V = Viajes/Viajes)
- Ejemplo: `1852_01_15_HAB_DM_U_01_0_V_003-001.txt`
- Extrae: Llegadas de barcos internacionales con detalles completos del viaje

**Entradas de Cabotaje (Llegadas Domésticas)**
- Nombre de archivo contiene: `_C_` (C = Cabotaje/Costero)
- Ejemplo: `1852_01_15_HAB_DM_U_01_0_C_003-001.txt`
- Extrae: Llegadas de barcos domésticos/regionales

### Ejemplo Completo

```
.data/Nuevo/1852/01/
├── 1852_01_01_HAB_DM_U_01_0_V_003-001.txt    ← Travesía (V)
├── 1852_01_01_HAB_DM_U_01_0_C_003-001.txt    ← Cabotaje (C)
├── 1852_01_02_HAB_DM_U_01_0_V_003-001.txt    ← Travesía (V)
├── 1852_01_02_HAB_DM_U_01_0_C_003-001.txt    ← Cabotaje (C)
├── 1852_01_03_HAB_DM_U_01_0_V_003-001.txt    ← Travesía (V)
├── 1852_01_03_HAB_DM_U_01_0_C_003-001.txt    ← Cabotaje (C)
└── ...
```

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual: `python3 -m venv .venv`
3. Activar: `source .venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar clave OpenAI: `export OPENAI_API_KEY=tu_clave_aqui`

## Uso

Ejecutar el menú principal:
```bash
python3 main.py
```

### Opciones del Menú

#### OPCIONES DE EXTRACCIÓN

**1. Concatenar archivos OCR por fecha**
- Agrupa archivos OCR por fecha
- Combina múltiples archivos en archivos únicos por fecha
- Útil para preprocesar datos OCR sin procesar
- Entrada: Directorio con archivos OCR
- Salida: Archivos de texto concatenados organizados por fecha

**2. Extraer ENTRADAS DE TRAVESÍA**
- Extrae llegadas de barcos internacionales del texto concatenado
- Utiliza IA para analizar texto OCR no estructurado
- Genera archivos JSON y CSV
- Entrada: Directorio con archivos de texto concatenados
- Salida: JSON y CSV con datos estructurados

**3. Extraer ENTRADAS DE CABOTAJE**
- Extrae llegadas de barcos domésticos/regionales del texto concatenado
- Utiliza IA para analizar texto OCR no estructurado
- Genera archivos JSON y CSV
- Entrada: Directorio con archivos de texto concatenados
- Salida: JSON y CSV con datos estructurados

**4. Extraer TRAVESÍAS Y CABOTAJES por AÑO (con hilos)**
- Extrae ambos tipos simultáneamente por año
- Utiliza 16 hilos concurrentes (configurable)
- Almacena directamente en base de datos SQLite
- Omite automáticamente archivos ya procesados
- Muestra progreso y estadísticas
- Entrada: Directorio OCR (`.data/Nuevo/`), año a procesar
- Salida: Datos almacenados en base de datos SQLite

#### BASE DE DATOS Y ANÁLISIS

**5. Reprocesar AÑO (eliminar datos antiguos y re-extraer)**
- Elimina todos los datos de un año específico de la base de datos
- Re-extrae de archivos OCR con prompts LLM actuales
- Útil para actualizar con reglas de extracción mejoradas
- Muestra estadísticas antes/después
- Requiere confirmación antes de eliminar
- Entrada: Año a reprocesar
- Salida: Base de datos actualizada con nuevos datos

**6. Verificar archivos faltantes por procesar**
- Compara archivos OCR en el sistema de archivos con registros de base de datos
- Muestra qué archivos aún no han sido procesados
- Muestra estadísticas por año
- Ayuda a identificar extracciones incompletas
- Entrada: Ruta del directorio OCR
- Salida: Lista de archivos faltantes por año

**7. Mostrar estadísticas de la base de datos**
- Muestra conteos de entradas por año
- Muestra desglose de travesías vs cabotajes
- Total de entradas y años en la base de datos
- Tabla formateada para fácil lectura
- Sin entrada requerida
- Salida: Tabla de estadísticas

**8. Exportar todos los años (JSON + CSV)**
- Exporta toda la base de datos a archivos
- Crea archivos separados para cada año
- Genera exportaciones de travesías y cabotajes
- Elimina campos internos (id, obs) de las exportaciones
- Convierte cargo_list a formato legible
- Entrada: Ruta del directorio de salida
- Salida: Archivos JSON y CSV para cada año

**0. Salir**
- Cierra la aplicación

## Estructura de Datos

### Entrada de Travesía (Llegadas Internacionales)
```json
{
  "source_file": "1852_01_01",
  "publication_day": "1852-01-01",
  "arrival_date": "1852-01-01",
  "arrival_date_calc": "1852-01-01",
  "travel_departure_port": "Liverpool",
  "ship_type": "bergantín",
  "ship_flag": "esp.",
  "ship_name": "María",
  "master_role": "cap.",
  "master_name": "García",
  "cargo_list": [
    {
      "cargo_merchant_name": "Lawton y Hnos.",
      "cargo": [
        {
          "cargo_commodity": "algodón",
          "cargo_quantity": "100",
          "cargo_unit": "balas"
        }
      ]
    }
  ],
  "raw_text": "De Liverpool en 12 días, bergantín español María, capitán García..."
}
```

### Entrada de Cabotaje (Llegadas Domésticas)
```json
{
  "source_file": "1852_01_01",
  "publication_day": "1852-01-01",
  "travel_arrival_date": "1852-01-01",
  "travel_departure_port": "Matanzas",
  "ship_type": "goleta",
  "ship_flag": null,
  "ship_name": "Esperanza",
  "master_role": "pat.",
  "master_name": "López",
  "cargo_list": [
    {
      "cargo_merchant_name": "a la orden",
      "cargo": [
        {
          "cargo_commodity": "azúcar",
          "cargo_quantity": "50",
          "cargo_unit": "cajas"
        }
      ]
    }
  ],
  "raw_text": "De Matanzas en 12 horas, goleta Esperanza, patrón López..."
}
```

## Esquema de Base de Datos

### Tabla traversing
- `id`: Clave primaria
- `source_file`: Identificador de archivo fuente (YYYY_MM_DD)
- `publication_day`: Fecha de publicación (YYYY-MM-DD)
- `arrival_date`: Fecha de llegada (YYYY-MM-DD)
- `arrival_date_calc`: Fecha de llegada calculada
- `travel_departure_port`: Puerto de salida
- `ship_type`: Tipo de embarcación
- `ship_flag`: Bandera/nacionalidad
- `ship_name`: Nombre del barco
- `master_role`: Rol de capitán/patrón
- `master_name`: Nombre de capitán/patrón
- `cargo_list`: Array JSON de artículos de carga
- `raw_text`: Texto extraído original
- `travel_duration_value`: Duración del viaje (numérico)
- `travel_duration_unit`: Unidad de duración (días/horas)
- `ship_tons_capacity`: Capacidad de tonelaje del barco
- `ship_tons_unit`: Unidad de tonelaje
- `crew_number`: Tamaño de la tripulación
- `passenger_account`: Cantidad de pasajeros
- `quarantine`: Estado de cuarentena
- `forced_arrival`: Indicador de llegada forzada
- `obs`: Observaciones/notas
- `parsed_text`: Representación de texto analizado

### Tabla cabotage
Misma estructura que la tabla traversing

### Tabla processed_files
- `id`: Clave primaria
- `file_path`: Ruta del archivo procesado
- `processed_at`: Marca de tiempo de procesamiento
- `traversing_count`: Entradas de travesía extraídas
- `cabotage_count`: Entradas de cabotaje extraídas

## Configuración

### Clave de API de OpenAI
Almacenar encriptada en `llm_service/openai_key.txt`:
```bash
export ADATROP_TERCES=tu_clave_encriptacion
```

### Ruta de Base de Datos
Predeterminado: `.data/extraction.db`
Modificar en código o pasar como parámetro a `ExtractionDB()`

### Cantidad de Hilos
Predeterminado: 16 trabajadores
Configurable al ejecutar opciones de extracción

## Rendimiento

- **Velocidad de Procesamiento**: ~100-200 entradas por minuto (depende de API LLM)
- **Tamaño de Base de Datos**: ~500MB para 60,000+ entradas
- **Uso de Memoria**: ~2GB con 16 hilos concurrentes
- **Uso de Tokens**: ~0.5-1.0 tokens por entrada

## Manejo de Errores

- El texto OCR inválido se omite
- Las entradas duplicadas se ignoran (restricción UNIQUE)
- Las llamadas API fallidas se registran
- Se crean copias de seguridad de base de datos antes de migraciones

## Solución de Problemas

### No se encuentran archivos
- Verificar que los archivos OCR estén en estructura `.data/Nuevo/YYYY/`
- Verificar nombres de archivo: `YYYY_MM_DD_*_V_*.txt` (travesías) o `*_C_*.txt` (cabotajes)

### Errores de base de datos
- Verificar permisos de `.data/extraction.db`
- Verificar que SQLite esté instalado
- Revisar registros en `.data/output/`

### Errores de API
- Verificar que la clave de API de OpenAI esté configurada
- Verificar saldo de tokens
- Revisar límites de velocidad

## Desarrollo

### Agregar nuevos tipos de extracción
1. Crear nuevo prompt LLM en `llm_service/llm_openai.py`
2. Agregar método de extracción en `utils/extractor.py`
3. Agregar tabla de base de datos en `utils/db/database.py`
4. Agregar opción de menú en `main.py`

### Pruebas
Ejecutar componentes individuales:
```bash
python3 -c "from utils.db import ExtractionDB; db = ExtractionDB(); print(db.get_stats())"
```

## Documentación

Disponible en múltiples idiomas:
- **Inglés**: README.md
- **Español**: docs/README_ES.md (este archivo)
- **Griego**: docs/README_EL.md

## Licencia

Extracción de datos históricos para fines de investigación.

## Soporte

Para problemas o preguntas, revise los registros en el directorio `.data/output/`.
