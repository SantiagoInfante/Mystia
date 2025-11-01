import os
import requests
from dotenv import load_dotenv

# Carga las variables de entorno si se ejecuta localmente
load_dotenv() 

# =========================================================
# FUNCIÓN DE CONSULTA A LA API DE HUGGING FACE
# =========================================================
def query_hf(prompt, model_id):
    """
    Consulta un modelo de Hugging Face (HF) usando su API de Inferencia.
    
    :param prompt: El texto que se enviará al modelo.
    :param model_id: El ID del modelo en HF (ej. "gpt2").
    :return: El texto generado por el modelo.
    """
    
    # 1. Obtener el token de las variables de entorno
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if not HF_TOKEN:
        return "Error: Token de Hugging Face no encontrado."
    
    # 2. Configurar el endpoint de la API
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    # 3. Definir la carga útil (payload)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,  # Límite de texto generado
            "temperature": 0.9,     # Creatividad
            "do_sample": True       # Habilita la selección muestreada
        }
    }

    # 4. Enviar la solicitud POST
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # 5. Manejar la respuesta
    try:
        data = response.json()
        
        # El formato de respuesta de la API es una lista de diccionarios
        if isinstance(data, list) and data and 'generated_text' in data[0]:
            # Limpia y devuelve solo el texto generado
            return data[0]['generated_text'].replace(prompt, '').strip()
        
        # Manejar errores o estados de "modelo cargando"
        elif 'error' in data:
            return f"Error de HF: {data.get('error')}"
        elif 'estimated_time' in data:
             return "El modelo se está cargando, inténtalo de nuevo en unos segundos. ⏳"
        
        return "Respuesta desconocida del modelo."

    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"
    except Exception as e:
        return f"Error al procesar JSON: {e}"
