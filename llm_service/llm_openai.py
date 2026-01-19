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
Eres experto en extraer información de texto no estructurado contenido en archivos textos obtenidos de un proceso de OCR a periódicos de la época del 1850 al 1915 relacionada con entradas de buques mercantes al puerto de la Habana. Este contenido que frecuencia contiene errores propios del proceso pero también errores tipográficos u ortográficos y a través de la lógica y semántica logras obtenerla y estructurarla en una estructura que ha continuación te describo:

publication_date: Muestra la fecha del periódico, el nombre del archivo contiene la fecha de al inicio YYYY_MM_DD_... en este ejemplo 1876-01-01El nombre del archivo aporta información que se necesita extraer, este nombre tiene el siguiente formato: Ej.: 1876_01_01_HAB_DM_U_01_0_C_003-001.txt

travel_arrival_date: Indica la fecha en la que el barco llegó al puerto de llegada (Marsella, Buenos Aires, La Habana o Barcelona) en formato YYYY-MM-DD.

travel_departure_port: Indica el puerto de salida del buque en este viaje.

travel_port_of_call_list: Indica la lista de puertos (y opcionalmente más información como fechas de llegada o salida) en los que el barco había hecho escala durante su trayecto al puerto de llegada. Si la información de esta lista es solo el nombre de los puertos, la lista estará compuesta por nombres de puertos separados por comas.

travel_duration_value: Indica el tiempo que el barco estuvo viajando desde el puerto de salida al puerto de llegada días u horas (este valores enteros [2, 5, etc.] o mixtos [5 1/2, 3 1/4, etc.], en formato descriptivo [dos horas, tres horas y 35 minutos, 5 días y medio, etc.]).

travel_duration_unit: Indica la unidad de tiempo en la que se expresa la duración ([hora(s), día(s)], o cualquiera otra forma semejante de escribirse estas dos unidades de tiempo como [hrs., h., d., etc.]).

ship_type: Describe el tipo de barco (bergantín, goleta, vapor, etc.) que menciona el periódico

ship_flag: Hace referencia al nombre del país o región de la bandera del barco descrito por el periódico

ship_name: Indica el nombre del barco que normalmente se presenta completo, como se menciona en la fuente del periódico

ship_tons_capacity: Especifica la capacidad del barco en toneladas presentada como un valor numérico con la unidad de medida. En el caso de los barcos, esto siempre es lo mismo, ya que se refiere al tonelaje del buque. Este dato se da normalmente con abreviaturas como "ton." o "t."

ship_tons_unit: Se refiere a la unidad de tonelaje del buque. Generalmente se expresa con abreviaturas como "tonelada" o "t".

master_role: Hace referencia a la categoría de la persona que comanda el buque. Puede ser capitán o patrón, aunque en algunos casos también aparece piloto. Las abreviaturas que se utilizan para designarlos suelen ser "c" y "p", respectivamente

master_name: Es la identificación nominal de la persona que comanda el buque. Puede aparecer de varias formas, al menos lleva el apellido, precedido de su cargo (rol). Indica el apellido del capitán del buque, a menudo precedido de "cap." o "c."

crew_number: Es el valor numérico de la tripulación del buque, número seguiente a la palabra ["trip.", "trp.", etc.] u otra forma de escribirse.

passenger_account: Cantidad de pasajeros, en ocaciones aparece la cantidad de pasajeros que vienen de viaje en la embarcación, si no se especifica se asume null

cargo_list: Es la lista con la información relativa a toda la carga transportada por el buque entrante (tipo de carga, cantidad, persona receptora de la carga, si la hay o "a la orden" en caso contrario, etc.). Cada mercancía se descompondrá en los siguientes campos.
- cargo_merchant_name: Es la persona a la que iba destinada la carga, muchas veces será el comerciante que la había comprado y que se hizo cargo de ella en el momento de la descarga. Indica el destinatario de la carga, con ocasional mención a "divers" [varios/diversos]. En este caso vemos nombres de personas o empresas. Estos nombres tienen las mismas características y dificultades que el resto de denominaciones. En ocasiones los barcos llegaban a carga completa y estaban destinados a la misma persona, y en otros casos, cada carga tenía su destinatario. También aparece con frecuencia la expresión "a la orden", que en principio es una carga para ser vendida a su llegada a puerto y que, por el contrario, no tiene un propietario anterior, más allá del propio capitán personalmente o por cuenta de alguien.
- cargo: Lista de de mercancias y cada una de ellas se descompone en:
  - cargo_commodity: Expresa los productos o tipos de mercancías que han llegado. Es un valor muy variable, las mercancías más habituales son el carbón o el algodón, pero existe una extraordinaria diversidad de productos que llegan al puerto.
  - cargo_quantity: Expresión numérica del importe de la carga
  - cargo_unit: Expresa las unidades en las que aparece la carga. Estas pueden ser unidades de peso, volumen, recuentos o unidades relativas al embalaje.

quarantine: Información relativa a condiciones especiales de la llegada motivadas por circunstancias sanitarias.

forced_arrival: Indicación sobre las causas de la llegada forzosa.

obs: Notas o comentarios adicionales que aborden aspectos no contemplados en las variables registradas, proporcionando información contextual o relevante sobre el evento.

FORMATO DE SALIDA JSON:
{{
    "publication_day": "YYYY-MM-DD",
    "travel_arrival_date": "YYYY-MM-DD",
    "travel_departure_port": "Puerto",
    "travel_port_of_call_list": ["Puerto1", "Puerto2"] o [],
    "travel_duration_value": número o null,
    "travel_duration_unit": "días" o "horas" o null,
    "ship_type": "tipo de barco",
    "ship_flag": "bandera" o null,
    "ship_name": "nombre del barco" o null,
    "ship_tons_capacity": número o null,
    "ship_tons_unit": "ton." o "t." o null,
    "master_role": "cap." o "pat." o "pil." o null,
    "master_name": "nombre del capitán" o null,
    "crew_number": número o null,
    "passenger_account": número o null,
    "cargo_list": [
        {{
            "cargo_merchant_name": "destinatario",
            "cargo": [
                {{
                    "cargo_commodity": "producto",
                    "cargo_quantity": "cantidad" o "",
                    "cargo_unit": "unidad" o ""
                }}
            ]
        }}
    ],
    "quarantine": false,
    "forced_arrival": false,
    "parsed_text": "texto original",
    "obs": "observaciones" o ""
}}

OBSERVACIONES:
- Los archivos comienzan con títulos que debes ignorar y continuan con la representación de una fecha en varios formatos que debes traducir al formato "YYYY-MM-DD"
- Usualmente para fechas de publicación a inicios de mes o año, vienen con fechas de arribo del mes anterior, lo que debes tener en cuenta para determinar correctamente la fecha en su formato "YYYY-MM-DD"
- Las entradas pueden comenzar usualmente con las palabras "De", "Do", "-", "--", o simplemente al inicio de la línea, se asume la fecha de arribo a partir de la primera vez que aparece representada en el texto y continua hasta tanto no aparezca otra que defina el cambio
- Los campos, atributos o grupos de atributos no siempre vienen en el mismo orden dentro de cada entrada, y alguno de ellos no siempre están presentes por lo que no son obligatorios
- Existen campos o atributos que su valor es "..." o "..", por tanto asignarás el valor de "???"

IMPORTANTE: No me especifiques ni expliques nada al respecto solo espera a que te solicite la información cuando te anexe los archivos y te especifique el orden, pues un mismo contenido puede estar en más de un archivo.

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
    """
    prompt = """
Eres experto en extraer información de texto no estructurado contenido en archivos textos obtenidos de un proceso de OCR a periódicos de la época del 1850 al 1915 relacionada con entradas de buques mercantes al puerto de la Habana. Este contenido que frecuencia contiene errores propios del proceso pero también errores tipográficos u ortográficos y a través de la lógica y semántica logras obtenerla y estructurarla en una estructura que ha continuación te describo:

publication_date: Muestra la fecha del periódico, el nombre del archivo contiene la fecha de al inicio YYYY_MM_DD_... en este ejemplo 1876-01-01El nombre del archivo aporta información que se necesita extraer, este nombre tiene el siguiente formato: Ej.: 1876_01_01_HAB_DM_U_01_0_C_003-001.txt

travel_arrival_date: Indica la fecha en la que el barco llegó al puerto de llegada (Marsella, Buenos Aires, La Habana o Barcelona) en formato YYYY-MM-DD.

travel_departure_port: Indica el puerto de salida del buque en este viaje.

travel_port_of_call_list: Indica la lista de puertos (y opcionalmente más información como fechas de llegada o salida) en los que el barco había hecho escala durante su trayecto al puerto de llegada. Si la información de esta lista es solo el nombre de los puertos, la lista estará compuesta por nombres de puertos separados por comas.

ship_type: Describe el tipo de barco (bergantín, goleta, vapor, etc.) que menciona el periódico

ship_flag: Hace referencia al nombre del país o región de la bandera del barco descrito por el periódico, pero es poco común en entradas de cabotaje

ship_name: Indica el nombre del barco que normalmente se presenta completo, como se menciona en la fuente del periódico

master_role: Hace referencia a la categoría de la persona que comanda el buque. Puede ser capitán o patrón, aunque en algunos casos también aparece piloto. Las abreviaturas que se utilizan para designarlos suelen ser "c" y "p", respectivamente

master_name: Es la identificación nominal de la persona que comanda el buque. Puede aparecer de varias formas, al menos lleva el apellido, precedido de su cargo (rol). Indica el apellido del capitán del buque, a menudo precedido de "cap." o "c."

cargo_list: Es la lista con la información relativa a toda la carga transportada por el buque entrante (tipo de carga, cantidad, unidad de la carga, etc.). Cada mercancía se descompondrá en los siguientes campos.
- cargo_merchant_name: Es la persona a la que iba destinada la carga, muchas veces será el comerciante que la había comprado y que se hizo cargo de ella en el momento de la descarga. Indica el destinatario de la carga, con ocasional mención a "divers" [varios/diversos]. En este caso vemos nombres de personas o empresas. Estos nombres tienen las mismas características y dificultades que el resto de denominaciones. En ocasiones los barcos llegaban a carga completa y estaban destinados a la misma persona, y en otros casos, cada carga tenía su destinatario. También aparece con frecuencia la expresión "a la orden", que en principio es una carga para ser vendida a su llegada a puerto y que, por el contrario, no tiene un propietario anterior, más allá del propio capitán personalmente o por cuenta de alguien.
- cargo: Lista de mercancias y cada una de ellas se descompone en:
  - cargo_commodity: Expresa los productos o tipos de mercancías que han llegado. Es un valor muy variable, las mercancías más habituales son el carbón o el algodón, pero existe una extraordinaria diversidad de productos que llegan al puerto.
  - cargo_quantity: Expresión numérica del importe de la carga
  - cargo_unit: Expresa las unidades en las que aparece la carga. Estas pueden ser unidades de peso, volumen, recuentos o unidades relativas al embalaje.

Nota: En ocasiones un mismo producto se expresa en una misma entrada con diferentes unidades de medidas y cantidades, lo que deberás separar en dos entradas de mercancías diferentes.

obs: Notas o comentarios adicionales que aborden aspectos no contemplados en las variables registradas, proporcionando información contextual o relevante sobre el evento.

FORMATO DE SALIDA JSON:
{{
    "publication_day": "YYYY-MM-DD",
    "travel_arrival_date": "YYYY-MM-DD",
    "travel_departure_port": "Puerto",
    "travel_port_of_call_list": ["Puerto1", "Puerto2"] o [],
    "ship_type": "tipo de barco",
    "ship_flag": "bandera" o null,
    "ship_name": "nombre del barco" o null,
    "master_role": "pat." o "cap." o "pil." o null,
    "master_name": "nombre del patrón" o null,
    "cargo_list": [
        {{
            "cargo_merchant_name": "destinatario" o "",
            "cargo": [
                {{
                    "cargo_commodity": "producto",
                    "cargo_quantity": "cantidad" o "",
                    "cargo_unit": "unidad" o ""
                }}
            ]
        }}
    ],
    "parsed_text": "texto original",
    "obs": "observaciones" o ""
}}

OBSERVACIONES:
- Los archivos comienzan con títulos que debes ignorar y continuan con la representación de una fecha en varios formatos que debes traducir al formato "YYYY-MM-DD"
- Usualmente para fechas de publicación a inicios de mes o año, vienen con fechas de arribo del mes anterior, lo que debes tener en cuenta para determinar correctamente la fecha en su formato "YYYY-MM-DD"
- Las entradas pueden comenzar usualmente con las palabras "De", "Do", "-", "--", o simplemente al inicio de la línea, se asume la fecha de arribo a partir de la primera vez que aparece representada en el texto y continua hasta tanto no aparezca otra que defina el cambio
- Los campos, atributos o grupos de atributos no siempre vienen en el mismo orden dentro de cada entrada, y alguno de ellos no siempre están presentes por lo que no son obligatorios
- Existen campos o atributos que su valor es "..." o "..", por tanto asignarás el valor de "???"
- Es común que se utilice las palabras 'id', 'id.' o 'idem' para referirse al puerto origen, la cantidad, unidad o mercancía inmediatamente anterior, evitando la repetición.

IMPORTANTE: No me especifiques ni expliques nada al respecto solo espera a que te solicite la información cuando te anexe los archivos y te especifique el orden, pues un mismo contenido puede estar en más de un archivo.

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
