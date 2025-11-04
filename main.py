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

# Cliente de Hugging Face (modo text_generation)
# -----------------------------------------------------------------
# CAMBIO 1: Usamos un modelo compatible con text_generation (Mixtral)
# -----------------------------------------------------------------
hf_client = InferenceClient(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1", # Modelo más potente
    # model="mistralai/Mistral-7B-Instruct-v0.1", # Alternativa más rápida
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
                # ---------------------------------------------------------
                # CAMBIO 2: Usamos text_generation y el formato de MISTRAL
                # ---------------------------------------------------------

                # 1. Formateamos el prompt para Mistral/Mixtral
                #    Usa [INST] para las instrucciones/preguntas
                #    y [/INST] para marcar el final de la instrucción.
                prompt_formateado = (
                    f"[INST] Eres un asistente de Discord útil. "
                    f"Responde la siguiente pregunta de forma concisa:\n"
                    f"{pregunta} [/INST]"
                )

                # 2. Usamos .text_generation()
                respuesta_raw = await asyncio.to_thread(
                    hf_client.text_generation,
                    prompt=prompt_formateado,
                    max_new_tokens=250,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.95,
                    top_k=50,
                    repetition_penalty=1.1,
                    stop_sequences=["</s>", "[INST]"], # Detenerse antes de que intente preguntar de nuevo
                )
                
                # 3. La respuesta es un string simple
                respuesta = respuesta_raw.strip()
                
                # ---------------------------------------------------------

            except Exception as e:
                respuesta = f"Ocurrió un error al consultar la IA: {e}"

            # Evita enviar mensajes vacíos
            await message.channel.send(respuesta or "No tengo respuesta.")
        else:
            await message.channel.send("¿Qué quieres preguntarme?")

# --- Lanzar Flask y Discord ---
if DISCORD_TOKEN:
    threading.Thread(target=run_flask).start()
    client.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No se encontró el token de Discord en las variables de entorno.")
