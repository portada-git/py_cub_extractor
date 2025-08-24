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

4. Configurar tu clave de API de OpenAI (u otro proveedor):

```bash
export OPENAI_API_KEY="tu_api_key_aqui"   # Linux/Mac
setx OPENAI_API_KEY "tu_api_key_aqui"     # Windows
```

---

## 🛠️ Uso

Ejecutar el script principal:

```bash
python main.py
```

---

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

