import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

def query_hf(prompt, model="openai-community/gpt2"):
    # --- LÍNEAS DE DIAGNÓSTICO A COPIAR ---
    print(f"DEBUG: El modelo utilizado es: {model}")
    # ---------------------------------------
    
    url = f"https://api-inference.huggingface.co/models/{model}"
    
    # --- LÍNEA DE DIAGNÓSTICO A COPIAR ---
    print(f"DEBUG: La URL generada es: {url}")
    # ---------------------------------------
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    # ... el resto del código ...
    
    # ...
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 50,
            "do_sample": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result[0]["generated_text"]
    except Exception as e:
        return f"Lo siento, hubo un error al consultar la IA: {e}"
