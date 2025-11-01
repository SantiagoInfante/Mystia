import os
import requests
from dotenv import load_dotenv

load_dotenv() 

# URL del endpoint de inferencia de Hugging Face (URL simple, sin f-string para diagnostico)
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/"

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
    
    # Construcción de la URL final con el modelo
    API_URL = HF_INFERENCE_URL + model_id
    
    # Headers de la solicitud
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json" # Asegura el tipo de contenido
    }

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
        response.raise_for_status() # Lanza un error para códigos 4xx/5xx

        # Intento de parsear JSON para respuestas exitosas o de "cargando"
        data = response.json()
        
        if isinstance(data, list) and data and 'generated_text' in data[0]:
            # Éxito: limpia y devuelve el texto generado
            return data[0]['generated_text'].replace(prompt, '').strip()
        
        elif 'error' in data:
            return f"Error de HF: {data.get('error')}"
        elif 'estimated_time' in data:
             return "El modelo se está cargando, inténtalo de nuevo en unos segundos. ⏳"
        
        return "Respuesta desconocida del modelo."

    except requests.exceptions.RequestException as e:
        # DIAGNÓSTICO FINAL: Mostrar el error HTTP real
        try:
            # Si el error es HTTP (ej. 401 Unauthorized, 403 Forbidden)
            error_code = response.status_code
            return f"❌ Error de Servidor HF (Código {error_code}). Token no aceptado."
        except:
             return f"Error de conexión: {e}"
    
    except Exception as e:
        return f"Error interno del bot: {e}"
