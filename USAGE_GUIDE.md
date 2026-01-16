# Guía de Uso - Extracción de Datos

## ⚠️ IMPORTANTE: Rutas Correctas

### ❌ INCORRECTO
```bash
python3 main.py
→ Opción 5
→ Input: .data/Nuevo/1887  # ❌ NO - esto es un año específico
```

### ✅ CORRECTO
```bash
python3 main.py
→ Opción 5
→ Input: .data/Nuevo  # ✅ SÍ - directorio raíz con todos los años
```

## Opciones de Extracción

### Opción 5: Extraer Todos los Años
```bash
python3 main.py
→ Opción 5
→ Input: .data/Nuevo
→ Output: .data/output
→ Threads: 16
```

**Resultado:** Procesa 1852, 1887, 1892, 1903 (todos los años)

### Opción 5b: Extraer Un Mes Específico
```bash
python3 main.py
→ Opción 5b
→ Input: .data/Nuevo
→ Output: .data/output
→ Year: 1852
→ Month: 1
→ Threads: 16
```

**Resultado:** Procesa solo enero 1852

### Script: Extraer Solo 1852
```bash
python3 extract_1852.py
```

**Resultado:** Procesa todo el año 1852

### Script: Extraer Todos los Años
```bash
python3 process_all_years.py
```

**Resultado:** Procesa 1852, 1887, 1892, 1903

## Estructura de Directorios

```
.data/Nuevo/
├── 1852/
│   ├── 01/
│   │   ├── 1852_01_01_HAB_DM_U_01_0_V_001-001.txt
│   │   ├── 1852_01_01_HAB_DM_U_01_0_C_001-001.txt
│   │   └── ...
│   ├── 02/
│   │   └── ...
│   └── ...
├── 1887/
│   ├── 01/
│   └── ...
├── 1892/
│   └── ...
└── 1903/
    └── ...
```

## Deduplicación Automática

### Escenario 1: Extraer mes, luego año
```bash
# Paso 1: Extraer enero 1852
python3 main.py → Opción 5b → Year: 1852, Month: 1
# Resultado: 31 archivos procesados

# Paso 2: Extraer todo 1852
python3 extract_1852.py
# Resultado: 
#   - Enero: SALTADO (ya procesado)
#   - Febrero-Diciembre: PROCESADOS
#   - Total: 548 archivos, 0 duplicados
```

### Escenario 2: Extraer año, luego mes
```bash
# Paso 1: Extraer todo 1852
python3 extract_1852.py
# Resultado: 548 archivos procesados

# Paso 2: Extraer enero 1852
python3 main.py → Opción 5b → Year: 1852, Month: 1
# Resultado: 0 archivos nuevos (todos ya procesados)
```

## Verificar Progreso

### Ver Estado por Año
```bash
python3 main.py
→ Opción 6
```

**Muestra:**
- Total de archivos por año
- Cuántos procesados (Traversing + Cabotage)
- Cuántos faltan
- Porcentaje de progreso

### Ver Estadísticas de BD
```bash
python3 main.py
→ Opción 7
```

**Muestra:**
- Total de entradas en la BD
- Desglose por tipo (Traversing/Cabotage)
- Archivos procesados

## Exportar Datos

### Exportar Año Completo
```bash
python3 main.py
→ Opción 8
→ Opción 1 (Export year from DB)
→ Year: 1852
→ Output: .data/output
```

**Genera:**
- `1852_traversing.json`
- `1852_traversing.csv`
- `1852_cabotage.json`
- `1852_cabotage.csv`

### Exportar Mes Específico
```bash
python3 main.py
→ Opción 8
→ Opción 2 (Export month)
→ Year: 1852
→ Month: 1
→ Output: .data/output
```

**Genera:**
- `1852_01_traversing.json`
- `1852_01_traversing.csv`
- `1852_01_cabotage.json`
- `1852_01_cabotage.csv`

## Troubleshooting

### Error: "No year directories found"
**Causa:** Pasaste un directorio de meses en lugar del directorio raíz
```bash
# ❌ INCORRECTO
Input: .data/Nuevo/1887

# ✅ CORRECTO
Input: .data/Nuevo
```

### Error: "Year directory not found"
**Causa:** El año no existe
```bash
# Años disponibles: 1852, 1887, 1892, 1903
# ❌ INCORRECTO
Year: 1900

# ✅ CORRECTO
Year: 1852
```

### Error: "Invalid month"
**Causa:** Mes fuera de rango
```bash
# Meses válidos: 1-12
# ❌ INCORRECTO
Month: 13

# ✅ CORRECTO
Month: 1
```

## Flujo Recomendado

1. **Extraer todo 1852 primero**
   ```bash
   python3 extract_1852.py
   ```

2. **Verificar que todo se procesó**
   ```bash
   python3 main.py → Opción 6
   ```

3. **Exportar datos**
   ```bash
   python3 main.py → Opción 8 → Opción 1 → Year: 1852
   ```

4. **Procesar otros años**
   ```bash
   python3 process_all_years.py
   ```

5. **Verificar estado final**
   ```bash
   python3 main.py → Opción 6
   ```

6. **Exportar todos los años**
   ```bash
   python3 main.py → Opción 8 → Opción 1 → Year: 1887
   python3 main.py → Opción 8 → Opción 1 → Year: 1892
   python3 main.py → Opción 8 → Opción 1 → Year: 1903
   ```
