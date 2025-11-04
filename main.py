import os
import discord
import asyncio
import requests # <-- ¡Nueva importación clave!
from flask import Flask
import threading

# Tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents de Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# URL del endpoint de la API de Inferencia de Hugging Face
# Usaremos un modelo compatible con text generation, como CodeLlama 7B Instruct
HF_API_URL = "https://api-inference.huggingface.co/models/codellama/CodeLlama-7b-Instruct-hf"

# --- Servidor Flask mínimo para Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot de Discord corriendo en Render"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- Eventos de Discord ---
@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

# --- Función de llamada HTTP síncrona ---
def call_hf_api_direct(prompt_text):
    """
    Realiza la llamada HTTP síncrona a la API de Hugging Face usando requests.
    """
    # 1. Cabeceras de autenticación
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # 2. Datos de la solicitud (payload)
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 250,
            "do_sample": True,
            "temperature": 0.7,
            "stop": ["</s>", "[INST]"],
            "return_full_text": False # Pedimos solo el texto generado
        }
    }

    # 3. Llamada síncrona
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    response.raise_for_status() # Lanza una excepción para códigos de estado erróneos (4xx o 5xx)

    # 4. Procesar la respuesta
    data = response.json()
    
    # La respuesta es una lista de resultados, tomamos el primero
    if data and isinstance(data, list) and 'generated_text' in data[0]:
        return data[0]['generated_text'].strip()
    
    return "No se pudo obtener la respuesta de la IA."

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        pregunta = (
            message.content.replace(f"<@{client.user.id}>", "")
            .replace(f"<@!{client.user.id}>", "")
            .strip()
        )

        if pregunta:
            await message.channel.send("⏳ Pensando con Hugging Face...")

            try:
                # 1. Formateamos el prompt
                prompt_formateado = (
                    f"<s>[INST] Eres un asistente útil y amigable. Responde de forma concisa. "
                    f"Pregunta: {pregunta} [/INST]"
                )

                # 2. Ejecutamos la función síncrona en un hilo separado
                #    usando el executor del loop de Discord.py. Esto es lo que
                #    resuelve el conflicto de concurrencia y el TypeError.
                respuesta = await client.loop.run_in_executor(
                    None, 
                    call_hf_api_direct, # Usamos la nueva función con requests
                    prompt_formateado
                )
                
            except requests.exceptions.HTTPError as e:
                # Manejo específico para errores HTTP
                print(f"Error HTTP al consultar la IA: {e}")
                respuesta = f"Ocurrió un error en la API de Hugging Face: {e}"
            
            except Exception as e:
                # Otros errores (red, JSON, etc.)
                print(f"Error durante la generación de texto: {e}")
                respuesta = f"Ocurrió un error al consultar la IA: {e}"

            # Enviamos la respuesta
            await message.channel.send(respuesta or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# --- Lanzar Flask y Discord ---
if DISCORD_TOKEN:
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No se encontró el token de Discord en las variables de entorno.")
