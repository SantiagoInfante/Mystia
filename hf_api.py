def query_hf(prompt, model_id):
    """
    Consulta un modelo de Hugging Face (HF) usando la librería huggingface_hub.
    """
    if client is None:
        return "Error interno del bot: Cliente de Hugging Face no inicializado."

    try:
        # Usar 'inputs' (no 'prompt') y leer la respuesta de forma segura
        response = client.text_generation(
            model=model_id,
            inputs=prompt,
            max_new_tokens=100,
            temperature=0.9,
            details=False
        )

        # Extraer texto según el tipo de respuesta que devuelva la librería
        text = ""
        # Si es string simple
        if isinstance(response, str):
            text = response
        # Si es una lista/dict con 'generated_text'
        elif isinstance(response, dict):
            # Algunos endpoints devuelven {'generated_text': '...'} o {'generated_texts': [...]}
            if "generated_text" in response:
                text = response["generated_text"]
            elif "generated_texts" in response and response["generated_texts"]:
                text = response["generated_texts"][0]
            else:
                text = str(response)
        # Si es una lista (p.ej. [{'generated_text': '...'}])
        elif isinstance(response, (list, tuple)):
            first = response[0] if response else ""
            if isinstance(first, dict) and "generated_text" in first:
                text = first["generated_text"]
            else:
                text = str(response)
        # Si es un objeto con atributo 'generated_text'
        elif hasattr(response, "generated_text"):
            text = getattr(response, "generated_text")
        else:
            text = str(response)

        return text.strip()

    except InferenceTimeoutError:
        return "El modelo se está cargando o está demasiado ocupado. Inténtalo de nuevo en un minuto. ⏳"

    except HfHubHTTPError as e:
        print(f"HfHubHTTPError en query_hf: {e}")  # log para Render
        if "404" in str(e):
            return f"Error: Modelo '{model_id}' no encontrado. Verifica el ID."
        if "401" in str(e) or "403" in str(e):
            return f"Error: Token de Hugging Face rechazado. Revisa tus permisos de 'Read'."
        if "503" in str(e):
            return "El servidor de IA está ocupado o el modelo se está cargando. Inténtalo de nuevo."
        return f"Error HTTP de la API: {e}"

    except Exception as e:
        print(f"Exception en query_hf: {type(e).__name__}: {e}")  # log para Render
        if "StopIteration" in str(e) or "provider" in str(e):
            return "Error al conectar con el servidor del modelo. Intenta con un modelo más popular (ej. 'gpt2')."
        return f"Error general al consultar IA: {e}"
