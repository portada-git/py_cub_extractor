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
            "travel_arrival_date": "YYYY-MM-DD",
            "travel_departure_port": "Puerto",
            "travel_port_of_call_list": null,
            "travel_duration_value": número,
            "travel_duration_unit": "días/horas",
            "ship_type": "tipo",
            "ship_flag": "bandera",
            "ship_name": "nombre",
            "ship_tons_capacity": número,
            "ship_tons_unit": "ton.",
            "master_role": "cap./pat./pil.",
            "master_name": "nombre",
            "crew_number": null,
            "passenger_account": null,
            "cargo_list": [
                {{
                    "cargo_merchant_name": "destinatario",
                    "cargo": [
                        {{
                            "cargo_commodity": "producto",
                            "cargo_quantity": "cantidad",
                            "cargo_unit": "unidad"
                        }}
                    ]
                }}
            ],
            "quarantine": false,
            "forced_arrival": false,
            "parsed_text": "texto original",
            "obs": "observaciones"
        }}

        DEFINICIONES DE CAMPOS:

        - travel_arrival_date: Fecha de llegada (YYYY-MM-DD). Extrae del nombre del archivo si es necesario.
        - travel_departure_port: Puerto de salida (después de "De", "Del", "Do")
        - travel_port_of_call_list: Puertos intermedios (si aparecen "escalas en...")
        - travel_duration_value: Número de días/horas (solo el número)
        - travel_duration_unit: "días", "horas", "d.", "h.", etc.
        - ship_type: Tipo de barco (vap., berg., gol., bea., paq., can., bal., brig., pol.)
            * IGNORAR: esp., am., ing., por el sol., por la sol. (son descriptores/errores)
        - ship_flag: Bandera del barco (esp., am., ing., etc.)
        - ship_name: Nombre del barco
        - ship_tons_capacity: Capacidad en toneladas (número)
        - ship_tons_unit: "ton.", "tons.", "t."
        - master_role: "cap.", "c.", "pat.", "p.", "pil."
        - master_name: Nombre del capitán
        - crew_number: Número de tripulantes (si aparece "trip.", "trp.")
        - passenger_account: Número de pasajeros (si aparece)
        - cargo_list: Lista de cargas con destinatarios
        - quarantine: true si menciona cuarentena
        - forced_arrival: true si menciona llegada forzosa
        - parsed_text: El texto original completo
        - obs: Observaciones sobre errores OCR o ambigüedades

        ESTRUCTURA TÍPICA:
        "De [PUERTO] en [DÍAS] días, [TIPO]. [BANDERA]. [NOMBRE], cap. [CAPITÁN], ton. [TONELADAS], con [CARGA], á [DESTINATARIO]"

        EJEMPLO:
        Input: "De Mallorca en 42 dias pol. csp. Isabel, cap. Palmer, ton 157, con frutos, á D. F. Ventosa."
        Output: {{
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
                {{
                    "cargo_merchant_name": "D. F. Ventosa",
                    "cargo": [
                        {{
                            "cargo_commodity": "frutos",
                            "cargo_quantity": "",
                            "cargo_unit": ""
                        }}
                    ]
                }}
            ],
            "quarantine": false,
            "forced_arrival": false,
            "parsed_text": "De Mallorca en 42 dias pol. csp. Isabel, cap. Palmer, ton 157, con frutos, á D. F. Ventosa.",
            "obs": "Bandera 'csp.' probable error OCR por 'esp.'. Tipo de barco 'pol.' probablemente 'gol.' (goleta) o 'pol.' (polacra)."
        }}

        IMPORTANTE:
        - Si no encuentras información clara, usa null
        - NO inventes datos
        - Incluye observaciones sobre errores OCR o ambigüedades
        - El campo parsed_text debe ser el texto original completo

        Texto a procesar: {}
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Eres un especialista en digitalización de registros marítimos históricos. "
                        "Tu prioridad es la PRECISIÓN. Debes responder EXCLUSIVAMENTE con un objeto JSON válido. "
                        "Si no encuentras información clara para algún campo, debes responder con null. "
                        "NUNCA inventes datos. Incluye observaciones sobre errores OCR o ambigüedades."},
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
    Especializada en abreviaturas domésticas (gol., pat., p.) y manejo de datos faltantes.
    """
    prompt = """
        Analiza la siguiente entrada de tráfico marítimo de CABOTAJE (doméstico) y extrae los datos en JSON.
        
        FORMATO JSON REQUERIDO:
        {{
            "travel_arrival_date": "YYYY-MM-DD",
            "travel_departure_port": "Puerto",
            "travel_port_of_call_list": null,
            "travel_duration_value": número,
            "travel_duration_unit": "horas/días",
            "ship_type": "tipo",
            "ship_flag": "bandera",
            "ship_name": "nombre",
            "ship_tons_capacity": número,
            "ship_tons_unit": "ton.",
            "master_role": "pat./cap./pil.",
            "master_name": "nombre",
            "crew_number": null,
            "passenger_account": null,
            "cargo_list": [
                {{
                    "cargo_merchant_name": "destinatario",
                    "cargo": [
                        {{
                            "cargo_commodity": "producto",
                            "cargo_quantity": "cantidad",
                            "cargo_unit": "unidad"
                        }}
                    ]
                }}
            ],
            "quarantine": false,
            "forced_arrival": false,
            "parsed_text": "texto original",
            "obs": "observaciones"
        }}

        REGLAS ESPECÍFICAS PARA CABOTAJE:
        1. Puerto Origen: Ubicado después de "De", "Del", "Do"
        2. Tipo de Barco: Busca "gol." (goleta), "paq." (paquete), "b." (balandra), "can." (cañonera), "berg.", "vap."
        3. Bandera: esp., am., ing., etc.
        4. Mando: "pat." (patrón), "p.", "cap." (capitán), "pil." (piloto)
        5. Duración: En HORAS (típicamente 2-48 horas), no días
        6. Toneladas: RARAMENTE aparecen en cabotaje - si no está explícito, usa null
        7. Carga: Lista de productos con cantidad y unidad (ej: "392 tercios de tabaco")
        8. Crew: A veces aparece "trip." (tripulación)

        EJEMPLO:
        Input: "De Mantua gol. Anuta pat. Mayans, con 392 tercios de tabaco, 20 % de cera, á D. Pepe Gonzalez"
        Output: {{
            "travel_arrival_date": null,
            "travel_departure_port": "Mantua",
            "travel_port_of_call_list": null,
            "travel_duration_value": null,
            "travel_duration_unit": null,
            "ship_type": "gol.",
            "ship_flag": null,
            "ship_name": "Anuta",
            "ship_tons_capacity": null,
            "ship_tons_unit": null,
            "master_role": "pat.",
            "master_name": "Mayans",
            "crew_number": null,
            "passenger_account": null,
            "cargo_list": [
                {{
                    "cargo_merchant_name": "D. Pepe Gonzalez",
                    "cargo": [
                        {{"cargo_commodity": "tabaco", "cargo_quantity": "392", "cargo_unit": "tercios"}},
                        {{"cargo_commodity": "cera", "cargo_quantity": "20", "cargo_unit": "%"}}
                    ]
                }}
            ],
            "quarantine": false,
            "forced_arrival": false,
            "parsed_text": "De Mantua gol. Anuta pat. Mayans, con 392 tercios de tabaco, 20 % de cera, á D. Pepe Gonzalez",
            "obs": "Cabotaje doméstico"
        }}

        IMPORTANTE:
        - Si no encuentras información clara, usa null
        - NO inventes datos
        - Incluye observaciones sobre errores OCR o ambigüedades
        - El campo parsed_text debe ser el texto original completo

        Texto a procesar: {}
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Eres un especialista en digitalización de registros marítimos históricos. Tu prioridad es la precisión: si un dato no está, usa null. NUNCA inventes datos."},
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