import os
import discord
import aiohttp
import asyncio

# Cargar tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Endpoint de Hugging Face con GPT-Neo (no GPT-2)
HF_API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-125M"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Función para consultar GPT-Neo usando aiohttp
async def query_model(prompt: str):
    payload = {"inputs": prompt, "max_length": 150, "temperature": 0.8}
    async with aiohttp.ClientSession() as session:
        async with session.post(HF_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]["generated_text"]
                elif isinstance(data, dict) and "error" in data:
                    return f"Error de API: {data['error']}"
                else:
                    return "Lo siento, la API no devolvió un texto válido."
            else:
                return f"Error de API ({response.status}): {await response.text()}"

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
            await message.channel.send("⏳ Pensando con GPT‑Neo...")

            try:
                respuesta = await query_model(pregunta)
            except Exception as e:
                respuesta = f"Ocurrió un error de conexión: {e}"

            if respuesta.startswith("Error de API") or respuesta.startswith("Ocurrió un error"):
                await message.channel.send(respuesta)
                return

            # Recorte seguro: eliminar el prompt si está repetido
            if respuesta.startswith(pregunta):
                respuesta_final = respuesta[len(pregunta):].strip()
            else:
                respuesta_final = respuesta.strip()

            await message.channel.send(respuesta_final or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# Iniciar el bot
if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No se encontró el token de Discord en las variables de entorno.")
