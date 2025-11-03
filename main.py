import discord
import os
import random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
# --- CAMBIO CLAVE 1: Importamos el módulo completo ---
import hf_api 
from keep_alive import keep_alive

# Cargar variables del archivo .env
load_dotenv()

# --- Intents (Permisos del bot) ---
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# --- Inicialización del bot ---
bot = commands.Bot(command_prefix='!', intents=intents)
# NOTA: Se eliminó la variable MODELO_IA ya que la lógica está en hf_api.py

# =========================================================
# Evento on_ready (Inicio del bot y sincronización de comandos)
# =========================================================
@bot.event
async def on_ready():
    print(f'✅ MystiaAi está conectada como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="charlar contigo 💕"))

    try:
        # Esto asegura que el modelo de IA se intente cargar en la fase de inicio, 
        # antes de que el bot necesite responder a mensajes.
        print("Intentando inicializar modelo de IA (puede tardar en Render)...")
        # El modelo se carga en el módulo hf_api.py cuando se importa.

        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)} comandos.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")
    print('--------------------------------------------------')

# =========================================================
# Comando de barra /ping
# =========================================================
@bot.tree.command(name="ping", description="Comprueba si MystiaAi está activa y muestra la latencia.")
async def ping_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 ¡Pong!",
        description="¡MystiaAi está online y funcionando perfectamente! 😊",
        color=0x40E0D0
    )
    embed.add_field(
        name="Latencia:",
        value=f"**{round(bot.latency * 1000)}ms**",
        inline=True
    )
    embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

# =========================================================
# Evento on_message (Respuestas automáticas y conexión con IA)
# =========================================================
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user.mentioned_in(message):
        mention_id = f'<@{bot.user.id}>'
        mention_nick = f'<@!{bot.user.id}>'
        content_lower = message.content.lower()
        # Limpieza del mensaje
        content_cleaned = message.content.replace(mention_id, '').replace(mention_nick, '').strip()

        # --- Lógica de respuestas predefinidas (omisiones por brevedad) ---
        if not content_cleaned:
            respuestas_amables = [
                f'¡Hola, {message.author.display_name}! ✨ ¿Necesitas algo, cielo?',
                '¡Aquí estoy! ¿En qué puedo ayudarte, corazón? 😊',
                f'¿Me llamabas, {message.author.display_name}? ¡Siempre es un gusto saludarte! 🥰'
            ]
            await message.channel.send(random.choice(respuestas_amables))
            return
        
        # ... (otras respuestas predefinidas) ...
        # --- Fin de la lógica de respuestas predefinidas ---

        # Respuesta generada por IA
        async with message.channel.typing():
            # --- CAMBIO CLAVE 2: Llamada a la función a través del módulo ---
            respuesta_ia = hf_api.query_hf(content_cleaned) 

        respuesta_discord = f"**Pregunta:** *{content_cleaned}*\n**MystiaAi dice:** {respuesta_ia}"
        await message.channel.send(respuesta_discord)

# =========================================================
# Ejecución del bot
# =========================================================
# --- CORRECCIÓN FINAL de error de sintaxis ---
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ Error: No se encontró el DISCORD_TOKEN.")
else:
    try:
        keep_alive()
        bot.run(TOKEN)
    except discord.errors.HTTPException as e:
        print(f"❌ Error al conectar: {e}")
