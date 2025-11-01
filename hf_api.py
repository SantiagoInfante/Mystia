import os
from dotenv import load_dotenv
# Importamos HfApi (que contiene HTTPError) y InferenceClient
from huggingface_hub import InferenceClient, InferenceTimeoutError, HfApi 

# Carga las variables de entorno
load_dotenv()

# Inicializa el cliente de Hugging Face
try:
    HF_TOKEN = os.environ.get("HF_TOKEN")
    # ASUMIMOS que el token ya es correcto (lo hemos comprobado)
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
        # Llama al método de generación de texto del cliente
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
    
    except HfApi.HTTPError as e: 
        # Captura errores HTTP (404, 401, 403, 503)
        if "404" in str(e):
            return f"Error: Modelo '{model_id}' no encontrado. Intenta con 'gpt2'."
        if "401" in str(e) or "403" in str(e):
             return f"Error: Token de Hugging Face rechazado. Revisa permisos."
        if "503" in str(e):
            return "El servidor de IA está ocupado o el modelo se está cargando. Inténtalo de nuevo."
        return f"Error HTTP de la API: {e}"

    except Exception as e:
        # Capturamos el StopIteration y otros errores internos aquí
        if "StopIteration" in str(e):
            return "Error al conectar con el servidor del modelo. El modelo puede no ser compatible con la API de inferencia gratuita. Intenta con un modelo más popular."
        return f"Error general al consultar IA: {e}"
