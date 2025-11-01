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
    """
    
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if not HF_TOKEN:
        return "Error: Token de Hugging Face no encontrado."
    
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.9,
            "do_sample": True
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # Lanza un error si el código es 4xx o 5xx
        
        # --- Lógica de Manejo de Respuesta (Normal) ---
        data = response.json()
        
        if isinstance(data, list) and data and 'generated_text' in data[0]:
            return data[0]['generated_text'].replace(prompt, '').strip()
        
        elif 'error' in data:
            return f"Error de HF: {data.get('error')}"
        elif 'estimated_time' in data:
             return "El modelo se está cargando, inténtalo de nuevo en unos segundos. ⏳"
        
        return "Respuesta desconocida del modelo."

    except requests.exceptions.RequestException as e:
        # --- DIAGNÓSTICO CLAVE ---
        # Si la solicitud falla, intentamos leer la respuesta como texto
        try:
            # Si el error no fue JSON, leemos el texto puro del error
            error_text = response.text 
            # Imprime el error real en el log de Render
            print(f"ERROR DE HF DETECTADO (RAW TEXT): {error_text}") 
            
            # Devuelve un mensaje genérico de error al usuario
            return f"❌ Error de autenticación o servidor de HF. Por favor, revisa el log de Render."
        except:
             return f"Error de conexión HTTP: {e}"

    except Exception as e:
        return f"Error interno del bot: {e}"
