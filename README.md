# 📖 py_cub_extractor

Herramienta en **Python** para realizar **extracción automática de información estructurada desde noticias o textos históricos**, utilizando un **LLM** (por defecto OpenAI, aunque puede adaptarse a otros modelos como Ollama o Anthropic).

---

## 🚀 Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/portada-git/py_cub_extractor.git
cd py_cub_extractor
```

2. Crear entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate   # En Linux/Mac
venv\Scripts\activate      # En Windows
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Definir variables de entorno:

- *ADATROP_TERCES* Almacena clave de cifrado
- Guardar el archivo de llave openAI (📄 openai_key.txt cifrado) en la carpeta del proyecto: 📂*llm_service* 

---

## 🛠️ Uso

Ejecutar el script principal y seguir instrucciones del menu:

```bash
python main.py
```
```bash
    *** Cuban Node Traversing Entrances Extractor ***
    === Diario de la Marina Newspaper ===
    
                  |    |    |
                 )_)  )_)  )_)
                )___))___))___)
               )____)____)_____)
             _____|____|____|____\__
        ----\                   /-----
             \_________________/
     ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~~ ~ ~ ~ ~
     
    
1. Concatenate OCR text files by date
2. Extract TRAVERSING ENTRANCES
3. Extract CABOTAGE ENTRIES
4. Extract BOTH (Traversing + Cabotage)
0. Exit
Choose an option: 
---
```

### Opciones:

- 1. Concatenate OCR text files by date. Recide la ubicacion de la carpeta que contiene los archivos TXT que fueron generados por el OCR. Se recomienda siempre ejecutarlo sobre el OCR en bruto para crear un archivo TXT por dia y evitar que la noticia quede fragmentada.
- 2. Extract TRAVERSING ENTRANCES. Realiza la extracción de entradas de travesía de los datos ya concatenados. Recibe la carpeta que contiene los TXT concatenados y la carpeta de destino. Devuelve como salida archivos JSON y CSV del resultado de la extraccion.  
- 3. Extract CABOTAGE ENTRIES. Realiza la extracción de entradas de cabotaje de los datos ya concatenados. Recibe la carpeta que contiene los TXT concatenados y la carpeta de destino. Devuelve como salida archivos JSON y CSV del resultado de la extraccion.  
- 4. Extract BOTH (Traversing + Cabotage). Ejecuta ambas extracciones (travesía y cabotaje) en un solo flujo de trabajo. Solicita un directorio de entrada, un directorio de salida y un nombre base para los archivos. Genera archivos separados para cada tipo:
  - `{nombre_base}_traversing.json` y `{nombre_base}_traversing.csv`
  - `{nombre_base}_cabotage.json` y `{nombre_base}_cabotage.csv`
  
  Esta opción incluye manejo de errores independiente para cada paso, permitiendo que si una extracción falla, la otra continúe ejecutándose.  

## 📂 Estructura del proyecto

```
py_cub_extractor/
│
├── main.py              # Punto de entrada principal
├── llm_service/         # Lógica para interactuar con LLMs (OpenAI, Ollama, etc.)
├── utils/               # Funciones auxiliares (limpieza de texto, guardado, etc.)
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Esta documentación
```
## 📑 Ejemplo 1

### Entrada (`ejemplo1.txt`)

```
Dia 30: ENTRADOS De Matanzas, en 1 día, vp. alm. Andes, capitán Gortz, ton. 1869, en lastre à E. Heilbut.
```

### Salida (`salida1.json`)

```json
{
    "publication_day": "Dia 30",
    "travel_duration": 1,
    "travel_departure_port": "Matanzas",
    "ship_type": "vp.",
    "ship_name": "alm. Andes",
    "ship_tons_capacity": "1869",
    "ship_tons_units": "ton.",
    "master_role": "cap.",
    "master_name": "Gortz",
    "cargo_list": [
        "en lastre à E. Heilbut."
    ],
    "raw_text": "Dia 30: ENTRADOS De Matanzas, en 1 día, vp. alm. Andes, capitán Gortz, ton. 1869, en lastre à E. Heilbut.",
    "departure_date": "1903-10-29",
    "arrival_date": "1903-10-30"
}
```


