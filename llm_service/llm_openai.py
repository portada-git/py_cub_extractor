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
