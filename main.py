import os
import discord
import asyncio
from huggingface_hub import InferenceClient
from flask import Flask
import threading

# Tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cliente de Hugging Face
hf_client = InferenceClient(token=HF_API_TOKEN)

# --- Servidor Flask mínimo ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot de Discord corriendo en Render"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- Discord Bot ---
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
                completion = await asyncio.to_thread(
                    hf_client.chat.completions.create,
                    model="mistralai/Mistral-7B-Instruct-v0.2",
                    messages=[{"role": "user", "content": pregunta}],
                    max_tokens=200,
                )
                respuesta = completion.choices[0].message["content"]
            except Exception as e:
                respuesta = f"Ocurrió un error: {e}"

            await message.channel.send(respuesta or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# --- Lanzar Flask y Discord ---
if DISCORD_TOKEN:
    # Flask en un hilo aparte
    threading.Thread(target=run_flask).start()
    # Discord en el hilo principal
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No se encontró el token de Discord en las variables de entorno.")
