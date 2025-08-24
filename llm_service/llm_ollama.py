import ollama
import json


def extract_structured_data_with_ollama(text: str, model: str = "mistral") -> dict:
    prompt = f"""
        Extrae los siguientes datos del texto y devuélvelos como un JSON plano, sin explicaciones:
        
        - ship_type: Tipo de embarcación. Puede ser nulo
        - ship_name: Nombre del barco.
        - ship_tons_capacity: Capacidad de carga del buque en toneladas. Debido a los posibles errores de transcripción del OCR, este dato se expresará como una cadena de caracteres. Si en la transcrición indicara, por ejemplo que el barco tiene una capacidad de 'B7 t.', en este campo deberá trasladarse el valor B7. Si se omitiera este valor dejaras este valor a null
        - ship_tons_units: Especifica las unidades en las que está expresado las dimensiones del buque. Normalmente toneladas
        - master_role: Cargo del responsable a bordo. Puede ser 'capitan' abreviado con c. o cap., 'piloto'abreviado con pil. o 'patrón' abreviado con p. o pat.
        - master_name: Nombre del responsable a bordo.
        - cargo_list:  Lista de mercancías transportadas y sus propietarios (si aparecen).
        - raw_text: Texto completo de esa entrada
        
        Texto:
        \"\"\"{text}\"\"\"
    """

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"].strip()

    try:
        if content == "null":
            return None

        data = json.loads(content)
        if "raw_text" not in data or not data["raw_text"]:
            data["raw_text"] = text.strip()
        return data

    except Exception as e:
        print(f"⚠️ Error parsing Ollama response or calling API: {e}")
        # Return minimal structure with raw_text to avoid crash
        return {
            "ship_type": None,
            "ship_name": None,
            "ship_tons_capacity": None,
            "ship_tons_units": None,
            "master_role": None,
            "master_name": None,
            "cargo_list": None,
            "raw_text": text.strip(),
        }