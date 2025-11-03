import os
import discord
from huggingface_hub import InferenceClient

# Tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cliente de Hugging Face
hf_client = InferenceClient(token=HF_API_TOKEN)

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
                # Usamos el endpoint de chat/completions
                completion = hf_client.chat.completions.create(
                    model="mistralai/Mistral-7B-Instruct-v0.2",  # Modelo moderno y gratuito
                    messages=[{"role": "user", "content": pregunta}],
                    max_tokens=200,
                )
                respuesta = completion.choices[0].message["content"]
            except Exception as e:
                respuesta = f"Ocurrió un error: {e}"

            await message.channel.send(respuesta or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# Iniciar el bot
if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No se encontró el token de Discord en las variables de entorno.")
