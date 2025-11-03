import os
import discord
import requests
import json
import asyncio

# Cargar tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents para que el bot pueda leer mensajes
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Endpoint de Hugging Face para GPT-2
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Función para consultar GPT-2
def query_gpt2(prompt: str):
    payload = {"inputs": prompt, "max_length": 100, "temperature": 0.7}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            return "Lo siento, no pude generar una respuesta."
    else:
        return f"Error {response.status_code}: {response.text}"

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message):
    # Evitar que el bot se responda a sí mismo
    if message.author == client.user:
        return

    # Verificar si el bot fue mencionado
    if client.user.mentioned_in(message):
        pregunta = message.content.replace(f"<@{client.user.id}>", "").strip()
        if pregunta:
            await message.channel.send("⏳ Pensando con GPT-2...")
            respuesta = query_gpt2(pregunta)
            # Enviar solo la parte generada después del prompt
            respuesta_final = respuesta[len(pregunta):].strip()
            await message.channel.send(respuesta_final or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# Iniciar el bot
client.run(DISCORD_TOKEN)
