import os
import discord
import asyncio
from huggingface_hub import InferenceClient
from flask import Flask
import threading

# Tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents de Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cliente de Hugging Face
hf_client = InferenceClient(
    model="codellama/CodeLlama-7b-Instruct-hf", 
    token=HF_API_TOKEN
)

# --- Servidor Flask mínimo para Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot de Discord corriendo en Render"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- Función Auxiliar Síncrona para evadir el error de asyncio ---
def generar_respuesta_sincrona(prompt_text):
    """Llama a la API de Hugging Face de forma síncrona."""
    # Usamos 'stop' en lugar de 'stop_sequences' para eliminar la advertencia
    respuesta_raw = hf_client.text_generation(
        prompt=prompt_text,
        max_new_tokens=250,
        do_sample=True,
        temperature=0.7,
        stop=["</s>", "[INST]"],
    )
    return respuesta_raw.strip()


# --- Eventos de Discord ---
@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

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

                # 2. Llamamos a la función síncrona dentro de asyncio.to_thread
                respuesta = await asyncio.to_thread(
                    generar_respuesta_sincrona,
                    prompt_formateado
                )
                
            except Exception as e:
                # Si ocurre un error, lo registramos y respondemos
                print(f"Error durante la generación de texto: {e}")
                respuesta = f"Ocurrió un error al consultar la IA: {e}"

            # Enviamos la respuesta
            await message.channel.send(respuesta or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# --- Lanzar Flask y Discord ---
if DISCORD_TOKEN:
    # Nota: Tu bot ya está funcionando en un hilo, esta es la forma estándar de hacerlo.
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No se encontró el token de Discord en las variables de entorno.")
