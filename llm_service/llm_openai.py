import os
import json
from openai import OpenAI
from utils import decrypt

api_key = decrypt.decrypt_file_openssl('llm_service/openai_key.txt', os.environ.get("ADATROP_TERCES"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", api_key))

# Global token tracking
_token_usage = {'total': 0}


def extract_structured_data_with_openai(text: str) -> dict:
    prompt = """
        Extrae información estructurada de una entrada de travesía de barco en formato JSON.
        
        FORMATO JSON REQUERIDO:
        {{
            "publication_day": "DD-MM-YYYY",
            "arrival_date": "Día XX:",
            "arrival_date_calc": "DD-MM-YYYY",
            "travel_departure_port": "Puerto",
            "ship_type": "tipo",
            "ship_flag": "bandera",
            "ship_name": "nombre",
            "master_role": "cap./pat./pil.",
            "master_name": "nombre",
            "cargo_list": [
                {{
                    "cargo_name": "producto",
                    "cargo_units": "unidad",
                    "cargo_count": "cantidad"
                }}
            ],
            "raw_text": "texto original"
        }}

        DEFINICIONES DE CAMPOS:

        - publication_day: Fecha de publicación en formato DD-MM-YYYY (ej: 01-01-1852)
        - arrival_date: Texto original de la fecha de llegada en formato DD-MM-YYYY (ej: 01-01-1852)
        - travel_departure_port: Puerto de salida (ej: "Liverpool", "Nueva York")
        - ship_type: Tipo de barco (vap., berg., gol., bea., paq., can., bal., brig., pol.)
        - ship_flag: Bandera (esp., am., ing., etc.) - puede ser vacío
        - ship_name: Nombre del barco
        - master_role: "cap.", "c.", "pat.", "p.", "pil."
        - master_name: Nombre del capitán
        - cargo_list: Lista de cargas con nombre, unidades y cantidad
        - raw_text: El texto original completo

        ESTRUCTURA TÍPICA:
        "De [PUERTO] en [DÍAS] días, [TIPO]. [BANDERA]. [NOMBRE], cap. [CAPITÁN], con [CARGA]"

        EJEMPLO:
        Input: "De Cuba; vapor Cosme de Herrera, cap. Vaca: con 250 reyes; 100 carneros; 1.363 sacos azúcar; 301 sacos maíz y efectos."
        Output: {{
            "publication_day": "01-01-1892",
            "arrival_date": "Día 31:",
            "travel_departure_port": "Cuba",
            "ship_type": "vapor",
            "ship_flag": "",
            "ship_name": "Cosme de Herrera",
            "master_role": "cap.",
            "master_name": "Vaca",
            "cargo_list": [
                {{"cargo_name": "reyes", "cargo_units": "", "cargo_count": "250"}},
                {{"cargo_name": "carneros", "cargo_units": "", "cargo_count": "100"}},
                {{"cargo_name": "azúcar", "cargo_units": "sacos", "cargo_count": "1.363"}},
                {{"cargo_name": "maíz", "cargo_units": "sacos", "cargo_count": "301"}},
                {{"cargo_name": "efectos", "cargo_units": "", "cargo_count": ""}}
            ],
            "raw_text": "De Cuba; vapor Cosme de Herrera, cap. Vaca: con 250 reyes; 100 carneros; 1.363 sacos azúcar; 301 sacos maíz y efectos."
        }}

        IMPORTANTE:
        - Si no encuentras información clara, usa null o cadena vacía
        - NO inventes datos
        - cargo_list es una lista simple de objetos con cargo_name, cargo_units, cargo_count
        - El campo raw_text debe ser el texto original completo

        Texto a procesar: {}
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Eres un especialista en digitalización de registros marítimos históricos. "
                        "Tu prioridad es la PRECISIÓN. Debes responder EXCLUSIVAMENTE con un objeto JSON válido. "
                        "Si no encuentras información clara para algún campo, debes responder con null o cadena vacía. "
                        "NUNCA inventes datos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=2000
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
        if hasattr(response, 'usage') and response.usage:
            _token_usage['total'] += response.usage.total_tokens
        return result
    except json.JSONDecodeError:
        print("❌ JSON inválido:\n", content)
        return {}


def extract_news_list_with_openai(text: str) -> dict:
    prompt = """

        Identifica donde aparecen las entradas de travesía en un texto:

        Para ello marcalas con un '###' y coloca en cada una identificada la fecha si aparece.
        Ejemplo
        'Dia 27: A- De Nueva Orleans y escalas en 5 dias, vap. america-C no Cliton, cap. Morgan, 
        trip. 32, tons. 717: con 10- carga general á Lawton y Hnos.--Matanzas en 12 horas, vap. esp. Alicia, capitan de Arribi, trip. 38, tons. 1,837: con azúcar de tránsito a- á Deulofeu é hijo. ron Canarias y Caibarien en 35 dias, bea. esp. Ver08 dad, cap. Sevilla, trip. 19, tons. 486: con carga t
        general á A. Serpa. Canarias y Caibarien en 35 dias, bea. esp. Ver08 dad, cap. Sevilla, trip. 19, tons. 486: con carga t
        general á A. Serpa'

        -output: 

        'Dia 27: ###Dia 27:A- De Nueva Orleans y escalas en 5 dias, vap. america-C no Cliton, cap. Morgan, 
        trip. 32, tons. 717: con 10- carga general á Lawton y Hnos.###Dia 27:--Matanzas en 12 horas, vap. esp. Alicia, capitan de Arribi, trip. 38, tons. 1,837: con azúcar de tránsito a- á Deulofeu é hijo. ron Canarias y Caibarien en 35 dias, bea. esp. Ver08 dad, cap. Sevilla, trip. 19, tons. 486: con carga t
        general á A. Serpa.###Dia 27:Canarias y Caibarien en 35 dias, bea. esp. Ver08 dad, cap. Sevilla, trip. 19, tons. 486: con carga t
        general á A. Serpa###'

        Texto de donde extraer la información: {}
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "Eres un asistente experto en extraer información de notas sobre entradas de"
                        "barcos a puerto. Responde exclusivamente con la salida transformada"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=9000
    )

    content = response.choices[0].message.content.strip()

    if hasattr(response, 'usage') and response.usage:
        _token_usage['total'] += response.usage.total_tokens
    
    return content


def extract_cabotaje_data_with_openai(text: str) -> dict:
    """
    Extrae datos estructurados de una línea de 'Entrada de Cabotaje'.
    Usa el formato antiguo definido originalmente.
    """
    prompt = """
        Analiza la siguiente entrada de tráfico marítimo de CABOTAJE (doméstico) y extrae los datos en JSON.
        
        FORMATO JSON REQUERIDO:
        {{
            "publication_day": "DD-MM-YYYY",
            "arrival_date": "Día XX:",
            "travel_departure_port": "Puerto",
            "ship_type": "tipo de barco",
            "ship_flag": "bandera",
            "ship_name": "nombre del barco",
            "master_role": "pat./cap./pil.",
            "master_name": "nombre",
            "cargo_list": [
                {{
                    "cargo_name": "producto",
                    "cargo_units": "unidad",
                    "cargo_count": "cantidad"
                }}
            ],
            "raw_text": "texto original"
        }}

        REGLAS ESPECÍFICAS PARA CABOTAJE:
        1. Puerto Origen: Ubicado después de "De", "Del", "Do"
        2. Tipo de Barco: gol., paq., b., can., berg., vap., etc.
        3. Bandera: esp., am., ing., etc. - puede ser vacío
        4. Mando: "pat." (patrón), "p.", "cap." (capitán), "pil." (piloto)
        5. Carga: Lista simple de productos con nombre, unidades y cantidad
        6. publication_day: Fecha en formato DD-MM-YYYY (ej: 01-01-1887)
        7. arrival_date: Texto original de la fecha (ej: "Día 31:")
        8. arrival_date_calc: Fecha calculada en formato DD-MM-YYYY

        EJEMPLO:
        Input: "De Mantua gol. Anuta pat. Mayans, con 392 tercios de tabaco, 20 % de cera, á D. Pepe Gonzalez"
        Output: {{
            "publication_day": "01-01-1887",
            "arrival_date": "Día 01:",
            "arrival_date_calc": "01-01-1887",
            "travel_departure_port": "Mantua",
            "ship_type": "gol.",
            "ship_flag": "",
            "ship_name": "Anuta",
            "master_role": "pat.",
            "master_name": "Mayans",
            "cargo_list": [
                {{"cargo_name": "tabaco", "cargo_units": "tercios", "cargo_count": "392"}},
                {{"cargo_name": "cera", "cargo_units": "%", "cargo_count": "20"}}
            ],
            "raw_text": "De Mantua gol. Anuta pat. Mayans, con 392 tercios de tabaco, 20 % de cera, á D. Pepe Gonzalez"
        }}

        IMPORTANTE:
        - Si no encuentras información clara, usa null o cadena vacía
        - NO inventes datos
        - cargo_list es una lista simple de objetos
        - El campo raw_text debe ser el texto original completo

        Texto a procesar: {}
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Eres un especialista en digitalización de registros marítimos históricos. Tu prioridad es la precisión: si un dato no está, usa null o cadena vacía. NUNCA inventes datos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=1500
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        if hasattr(response, 'usage') and response.usage:
            _token_usage['total'] += response.usage.total_tokens
        return data
    except json.JSONDecodeError:
        print(f"❌ Error parseando JSON para: {text[:30]}...")
        return {}


def get_token_usage():
    """Retorna el uso total de tokens"""
    return _token_usage['total']


def reset_token_usage():
    """Reinicia el contador de tokens"""
    _token_usage['total'] = 0