from transformers import pipeline
import os

# NOTA: Ya no necesitamos load_dotenv ni HF_API_TOKEN aquí.

# =========================================================
# CONFIGURACIÓN GLOBAL (Carga única al iniciar el bot)
# =========================================================

# NOTA IMPORTANTE: Esta carga es lenta y consume memoria.
# Render debe tener suficiente RAM para correr esto.
MODEL_NAME = "openai-community/gpt2"
try:
    # El pipeline gestiona el modelo y el tokenizador automáticamente.
    # Usamos un generador de bajo nivel para más control sobre la salida.
    global pipe
    pipe = pipeline(
        "text-generation", 
        model=MODEL_NAME,
        device=-1 # Ejecutar en CPU (necesario si no hay GPU)
    )
    print(f"✅ IA: Modelo {MODEL_NAME} cargado exitosamente de forma local.")
except Exception as e:
    print(f"❌ ERROR al cargar el modelo Transformers localmente: {e}")
    # En caso de error, el pipe se deja como None para evitar fallos.
    pipe = None


# =========================================================
# FUNCIÓN DE CONSULTA (query_hf)
# =========================================================

def query_hf(prompt, model=MODEL_NAME):
    # Si la carga del modelo falló, regresamos un error inmediato.
    if pipe is None:
        return "Lo siento, la IA no se pudo inicializar en el servidor. Revisa los logs de Render."
        
    try:
        # 1. Generar texto usando el pipeline.
        result = pipe(
            prompt,
            max_length=50,
            do_sample=True,
            top_k=50,         # Mejora la calidad de la muestra
            top_p=0.95,       # Mejora la calidad de la muestra
            num_return_sequences=1,
            # Evita que el generador cree más de una respuesta si encuentra fin de texto.
            eos_token_id=pipe.tokenizer.eos_token_id 
        )
        
        # 2. Devolver el texto generado (el pipeline devuelve una lista de diccionarios).
        # Hacemos un poco de limpieza extra para que no incluya el prompt en la respuesta de Discord.
        full_text = result[0]["generated_text"]
        
        # Elimina el prompt del texto generado para que no se repita en la respuesta de Discord
        if full_text.startswith(prompt):
            return full_text[len(prompt):].strip()
        
        return full_text
        
    except Exception as e:
        return f"Lo siento, hubo un error al generar la respuesta de la IA: {e}"
