import os
import discord
import asyncio
from huggingface_hub import InferenceClient
from flask import Flask
import threading

# Tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # Token de Hugging Face

# Configurar intents de Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cliente de Hugging Face con Cohere como provider
hf_client = InferenceClient(
    provider="cohere",
    api_key=HF_API_TOKEN,
)

# --- Servidor Flask mínimo para Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot de Discord corriendo con Cohere vía Hugging Face"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- Función para llamar al modelo Cohere ---
def call_cohere(prompt_text: str) -> str:
    try:
        completion = hf_client.chat.completions.create(
            model="CohereLabs/aya-expanse-32b",
            messages=[
                {
                    "role": "system",
                    "content": "Eres muy cariñosa, amable, coqueta y breve. Responde siempre con pocas palabras, de manera cálida y positiva."
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
        )
        return completion.choices[0].message["content"].strip()
    except Exception as e:
        print(f"❌ Error al consultar Cohere: {e}")
        return f"Ocurrió un error al consultar Cohere: {e}"

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
            await message.channel.send("⏳ Pensando...")

            # Ejecutamos la llamada en un hilo separado para no bloquear el loop
            respuesta = await client.loop.run_in_executor(
                None,
                call_cohere,
                pregunta
            )

            await message.channel.send(respuesta or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# --- Lanzar Flask y Discord ---
if DISCORD_TOKEN and HF_API_TOKEN:
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: Faltan variables de entorno DISCORD_TOKEN o HF_API_TOKEN")

