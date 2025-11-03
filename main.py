import os
import discord
import aiohttp
import asyncio

# ... (rest of the code up to line 12)

# Endpoint de Hugging Face
# 1️⃣ CORRECCIÓN CLAVE: Usar la URL actualizada. La anterior devuelve 410 GONE.
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Función para consultar GPT-2 usando aiohttp (asíncrono)
async def query_gpt2(prompt: str):
    payload = {"inputs": prompt, "max_length": 100, "temperature": 0.7}
    async with aiohttp.ClientSession() as session:
        async with session.post(HF_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and "generated_text" in data[0]:
                    return data[0]["generated_text"]
                elif isinstance(data, dict) and "error" in data:
                    return f"Error de API: {data['error']}"
                else:
                    return "Lo siento, la API no devolvió un texto generado válido."
            else:
                return f"Error de API ({response.status}): {await response.text()}"


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Usamos un solo canal de mención, ya que el anterior se bloqueaba.
    if client.user.mentioned_in(message):
        pregunta = (
            message.content.replace(f"<@{client.user.id}>", "")
            .replace(f"<@!{client.user.id}>", "")
            .strip()
        )

        if pregunta:
            # 2️⃣ CORRECCIÓN MENOR: Solo enviar el "Pensando..." una vez.
            # La doble ejecución del handler era la causa principal de la duplicación en el output.
            await message.channel.send("⏳ Pensando con GPT-2...")

            try:
                # La llamada asíncrona está correcta aquí: await query_gpt2(pregunta)
                respuesta = await query_gpt2(pregunta)
            except Exception as e:
                respuesta = f"Ocurrió un error de conexión: {e}"

            # Manejo de Errores de API (prioridad)
            if respuesta.startswith("Error de API") or respuesta.startswith("Ocurrió un error"):
                await message.channel.send(respuesta)
                return # Detener la ejecución si hay un error claro

            # 3️⃣ MEJORA: Recorte más seguro. Asumimos que GPT-2 repite el prompt.
            # Usar .strip() en la pregunta para asegurar la longitud correcta.
            prompt_limpio = pregunta.strip()
            
            if respuesta.startswith(prompt_limpio):
                # Recorta solo si el prompt está exactamente al inicio de la respuesta.
                respuesta_final = respuesta[len(prompt_limpio):].strip()
            else:
                # Si no empieza con el prompt (ej: es solo la respuesta), usar el texto completo.
                respuesta_final = respuesta.strip()
                
            # Envía la respuesta final o un mensaje predeterminado.
            await message.channel.send(respuesta_final or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# ... (rest of the code)

