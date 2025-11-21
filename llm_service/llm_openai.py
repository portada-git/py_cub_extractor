import os
import json
from openai import OpenAI
from utils import decrypt

api_key = decrypt.decrypt_file_openssl('llm_service/openai_key.txt', os.environ.get("ADATROP_TERCES"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", api_key))


def extract_structured_data_with_openai(text: str) -> dict:
    prompt = """

        Extrae la siguiente información del evento de entrada de barco descrita en la nota, 
        utilizando el formato JSON exacto: 

        {{
            'publication_day': null,
            'travel_duration': null,
            'travel_departure_port': null,
            'ship_type': null,
            'ship_name': null,
            'ship_tons_capacity': null,
            'ship_tons_units': null,
            'master_role': null,
            'master_name': null,
            'cargo_list': [],
            'raw_text': null
        }}

        Aquí está la definición de cada clave: 

        - publication_day: Date of publication in words (e.g "Día 5", "Febrero 15")
        - travel_duration: Travel duration in days
        - travel_departure_port: Departure port Name (e.g. "New york", "Barcelona")
        - ship_type: Type of ship. Can be null.
        - ship_name: Name of the vessel.
        - ship_tons_capacity: Capacity value, even if malformed (e.g., "B7", "47", "S9").
        - ship_tons_units: Typically "toneladas" or "tons".
        - master_role: One of ("cap.", "c.", "pat.", "p.", "pil."). Null if missing.
        - master_name: Person in charge onboard.
        - cargo_list: List of cargo and owners if mentioned.
        - raw_text: The full original entry.

        Ejemplos: 

        EJEMPLO 1:

        -input: 

        'Dia 27: A- De Nueva Orleans y escalas en 5 dias, vap. america-C no Cliton, cap. Morgan, 
        trip. 32, tons. 717: con 10- carga general á Lawton y Hnos.'

        -output: 

        {{
            'publication_day': 'Dia 27',
            'travel_duration': 5,
            'travel_departure_port': 'Nueva Orleans',
            'ship_type': 'vap.',
            'ship_name': 'america-C no Cliton',
            'ship_tons_capacity': '717',
            'ship_tons_units': 'tons.',
            'master_role': 'cap.',
            'master_name': 'Morgan',
            'cargo_list': ['carga general á Lawton y Hnos.'],
            'raw_text': 'Dia 27: A- De Nueva Orleans y escalas en 5 dias, vap. america-C no Cliton, cap. Morgan, trip. 32, tons. 717: con 10- carga general á Lawton y Hnos.'
        }}

        Texto de donde extraer la información: {} 
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Eres un asistente experto en extraer información estructurada de notas sobre entradas de"
                        "barcos a puerto. Debes responder EXCLUSIVAMENTE con un objeto JSON válido que contenga los campos solicitados."
                        "Si no encuentras información para algún campo, debes responder con el valor null en ese campo."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=9000
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
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

    return content


def extract_cabotaje_data_with_openai(text: str) -> dict:
    """
    Extrae datos estructurados de una línea de 'Entrada de Cabotaje'.
    Especializada en abreviaturas domésticas (gol., pat., p.) y manejo de datos faltantes.
    """
    prompt = """
        Analiza la siguiente entrada de tráfico marítimo de CABOTAJE (doméstico) y extrae los datos en JSON.
        
        Texto a procesar: "{}"

        Formato JSON Obligatorio:
        {{
            "publication_day": null,
            "travel_duration": null,
            "travel_departure_port": null,
            "ship_type": null,
            "ship_name": null,
            "ship_tons_capacity": null,
            "ship_tons_units": null,
            "master_role": null,
            "master_name": null,
            "cargo_list": [],
            "raw_text": null
        }}

        Reglas Específicas para Cabotaje:
        1. Puerto Origen: Ubicado después de "De", "Del", "Do".
        2. Tipo de Barco (ship_type): Busca abreviaturas como "gol." (goleta), "paq." (paquete), "b." (balandra), "can." (cañonera).
        3. Mando (master_role/name): Busca "pat.", "p." (patrón) o "cap." (capitán).
        4. Carga (cargo_list): Lista de productos después de "con" (ej: ["10 cajas azúcar"]).
        5. IMPORTANTISIMO: En cabotaje, 'travel_duration' (días) y 'ship_tons_capacity' (toneladas) RARAMENTE aparecen. 
           - Si no hay un número explícito seguido de "días" o "tons", devuelve NULL. 
           - NO inventes ni calcules estos datos.

        Responde EXCLUSIVAMENTE con el JSON válido.
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Eres un especialista en digitalización de registros marítimos históricos. Tu prioridad es la precisión: si un dato no está, usa null."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=1000
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        # Aseguramos que raw_text siempre esté presente y sea el original
        data["raw_text"] = text
        return data
    except json.JSONDecodeError:
        print(f"❌ Error parseando JSON para: {text[:30]}...")
        return {}
    prompt = """
    Extrae información estructurada de la siguiente entrada de cabotaje (tráfico marítimo interno), 
    utilizando el formato JSON exacto descrito abajo.

    Formato JSON de salida:
    {{
        "publication_day": null,
        "travel_duration": null,
        "travel_departure_port": null,
        "ship_type": null,
        "ship_name": null,
        "ship_tons_capacity": null,
        "ship_tons_units": null,
        "master_role": null,
        "master_name": null,
        "cargo_list": [],
        "raw_text": null
    }}

    Instrucciones de extracción:
    - publication_day: Extraer si aparece explícito (ej: "Dia 30"). Si no está en el texto, null.
    - travel_departure_port: Nombre del puerto de origen (suele estar después de "De" o "Del").
    - ship_type: Tipo de embarcación abreviado (ej: "gol.", "berg.", "paq.", "vap.").
    - ship_name: Nombre del barco (suele estar con mayúscula después del tipo).
    - master_role: Rol del mando (ej: "pat." para patrón, "cap." para capitán).
    - master_name: Apellido o nombre del patrón/capitán.
    - cargo_list: Lista de mercancías transportadas (ej: ["10 cajas azúcar", "2 pipas aguardiente"]).
    - raw_text: El texto original de entrada.

    Ejemplo de referencia:
    Input: "De Cárdenas gol. Victoria, pat. Llanger, con 10 cajas de azúcar."
    Output:
    {{
        "publication_day": null,
        "travel_duration": null,
        "travel_departure_port": "Cárdenas",
        "ship_type": "gol.",
        "ship_name": "Victoria",
        "ship_tons_capacity": null,
        "ship_tons_units": null,
        "master_role": "pat.",
        "master_name": "Llanger",
        "cargo_list": ["10 cajas de azúcar"],
        "raw_text": "De Cárdenas gol. Victoria, pat. Llanger, con 10 cajas de azúcar."
    }}

    Texto a procesar: {}
    """.format(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "Eres un asistente especializado en historia marítima y OCR. Tu tarea es extraer datos estructurados de entradas portuarias de cabotaje. Responde SOLAMENTE con el JSON válido."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=1000
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("❌ JSON inválido en cabotaje:\n", content)
        return {}