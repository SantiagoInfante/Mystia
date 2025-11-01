import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, InferenceTimeoutError
# SOLUCIÓN: Importación correcta del error HTTP desde el módulo de errores
from huggingface_hub.errors import HfHubHTTPError 

# Carga las variables de entorno
load_dotenv()

# Inicializa el cliente de Hugging Face
try:
    HF_TOKEN = os.environ.get("HF_TOKEN")
    # Inicialización del cliente con token y timeout (a prueba de errores de sintaxis)
    client = InferenceClient(token=HF_TOKEN, timeout=30)
except Exception as e:
    print(f"Error al inicializar el cliente de HF: {e}")
    client = None


# =========================================================
# FUNCIÓN DE CONSULTA A LA API DE HUGGING FACE
# =========================================================
def query_hf(prompt, model_id):
    """
    Consulta un modelo de Hugging Face (HF) usando la librería huggingface_hub.
    """
    if client is None:
        return "Error interno del bot: Cliente de Hugging Face no inicializado."

    # Intentamos la generación de texto
    try:
        response = client.text_generation(
            model=model_id,
            prompt=prompt,
            max_new_tokens=100,
            temperature=0.9,
            details=False
        )
        
        # La respuesta es el texto puro generado.
        return response.strip()

    except InferenceTimeoutError:
        return "El modelo se está cargando o está demasiado ocupado. Inténtalo de nuevo en un minuto. ⏳"
    
    # SOLUCIÓN: Captura el error HTTP de Hugging Face de forma correcta
    except HfHubHTTPError as e: 
        if "404" in str(e):
            return f"Error: Modelo '{model_id}' no encontrado. Verifica el ID."
        if "401" in str(e) or "403" in str(e):
             return f"Error: Token de Hugging Face rechazado. Revisa tus permisos de 'Read'."
        if "503" in str(e):
            return "El servidor de IA está ocupado o el modelo se está cargando. Inténtalo de nuevo."
        return f"Error HTTP de la API: {e}"

    except Exception as e:
        # Capturamos el StopIteration y otros errores generales aquí
        if "StopIteration" in str(e) or "provider" in str(e):
            return "Error al conectar con el servidor del modelo. Intenta con un modelo más popular (ej. 'gpt2')."
        return f"Error general al consultar IA: {e}"
