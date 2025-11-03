import os
import discord
import requests
import json
import asyncio # Importado correctamente
# import aiohttp # Opcional: para mejor rendimiento, pero usaremos asyncio.to_thread

# Cargar tokens desde variables de entorno
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Configurar intents para que el bot pueda leer mensajes
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# 1️⃣ CORRECCIÓN CLAVE: Endpoint de Hugging Face actualizado.
# El error indicó que el host antiguo ya no es compatible.
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Función para consultar GPT-2 (Mantenemos la función síncrona con requests)
def query_gpt2(prompt: str):
    payload = {"inputs": prompt, "max_length": 100, "temperature": 0.7}
    
    # Usamos requests de forma síncrona; esto se corrige al ser llamado
    # con 'asyncio.to_thread' más adelante.
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            # 2️⃣ MEJORA: Manejo de respuesta vacía o formato inesperado
            # Si el JSON es válido pero no tiene el campo esperado.
            return "Lo siento, la API no devolvió un texto generado válido."
    else:
        # Enviar solo el mensaje de error, no el JSON completo
        return f"Error de API ({response.status_code}): {response.text}"

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
        # 3️⃣ MEJORA: Eliminar la mención antes de procesar el prompt
        pregunta = message.content.replace(f"<@{client.user.id}>", "").strip()
        
        if pregunta:
            await message.channel.send("⏳ Pensando con GPT-2...")
            
            # 2️⃣ CORRECCIÓN CLAVE: Ejecutar la función bloqueante en un hilo aparte.
            # Esto evita que el bot se congele mientras espera la respuesta de Hugging Face.
            try:
                respuesta = await asyncio.to_thread(query_gpt2, pregunta)
            except Exception as e:
                respuesta = f"Ocurrió un error al comunicarse con la API: {e}"

            # Enviar solo la parte generada después del prompt
            # GPT-2 repite el prompt; esta línea elimina el prompt de la respuesta.
            respuesta_final = respuesta[len(pregunta):].strip()
            
            # 3️⃣ MEJORA: Evitar enviar el mensaje de error de la API con el recorte.
            if respuesta.startswith("Error de API") or respuesta.startswith("Ocurrió un error"):
                await message.channel.send(respuesta)
            else:
                await message.channel.send(respuesta_final or "No tengo respuesta.")
                
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# Iniciar el bot
client.run(DISCORD_TOKEN)
