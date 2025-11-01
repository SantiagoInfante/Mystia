import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, InferenceTimeoutError, HfApi

# Carga las variables de entorno
load_dotenv()

# Inicializa el cliente de Hugging Face
# El cliente lee automáticamente el HF_TOKEN de las variables de entorno.
try:
    HF_TOKEN = os.environ.get("HF_TOKEN")
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN no encontrado en el entorno.")
        # Inicializa un cliente sin token si no se encuentra (solo para pruebas)
        client = InferenceClient() 
    else:
        # Inicializa el cliente con el token (forma preferida y segura)
        client = InferenceClient(token=HF_TOKEN)
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
        # La librería maneja internamente la autenticación, headers y URL (eliminando el 404).
        response = client.text_generation(
            model=model_id,
            prompt=prompt,
            max_new_tokens=100,
            temperature=0.9,
            details=False,
            timeout=30 # Espera hasta 30 segundos
        )
        
        # La respuesta es el texto puro generado.
        return response.strip()

    except InferenceTimeoutError:
        return "El modelo se está cargando o está demasiado ocupado. Inténtalo de nuevo en un minuto. ⏳"
    
    except HfApi.HTTPError as e:
        # Captura errores HTTP (incluyendo el 404, 401, 403, 503)
        if "404" in str(e):
            return f"Error: Modelo '{model_id}' no encontrado en Hugging Face. Revisa el ID."
        if "401" in str(e) or "403" in str(e):
             return f"Error: Token de Hugging Face rechazado. Revisa tus permisos de 'Read'."
        return f"Error HTTP de la API: {e}"

    except Exception as e:
        return f"Error general al consultar IA: {e}"
