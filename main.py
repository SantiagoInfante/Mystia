import discord
import os
import random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from hf_api import query_hf # Suponiendo que tu Script 1 se llama hf_api.py
from keep_alive import keep_alive

# Cargar variables del archivo .env
load_dotenv()

# --- Intents (Permisos del bot) ---
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# --- Inicialización del bot ---
bot = commands.Bot(command_prefix='!', intents=intents)

# NOTA: Se eliminó la variable MODELO_IA ya que query_hf ya tiene el valor por defecto

# =========================================================
# Evento on_ready (Inicio del bot y sincronización de comandos)
# =========================================================
@bot.event
async def on_ready():
    print(f'✅ MystiaAi está conectada como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="charlar contigo 💕"))

    try:
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
        content_cleaned = message.content.replace(mention_id, '').replace(mention_nick, '').strip()

        # Respuestas predefinidas (código omitido por brevedad, no se modifica)
        # ...

        # Respuesta generada por IA
        async with message.channel.typing():
            # LLAMADA CORREGIDA: Ya no pasamos el modelo. Se usa el valor por defecto.
            respuesta_ia = query_hf(content_cleaned) 

        respuesta_discord = f"**Pregunta:** *{content_cleaned}*\n**MystiaAi dice:** {respuesta_ia}"
        await message.channel.send(respuesta_discord)

# =========================================================
# Ejecución del bot (código omitido por brevedad, no se modifica)
# =========================================================
TOKEN = os.environ.environ.get('DISCORD_TOKEN') # Corregido a os.environ.get('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ Error: No se encontró el DISCORD_TOKEN.")
else:
    try:
        keep_alive()
        bot.run(TOKEN)
    except discord.errors.HTTPException as e:
        print(f"❌ Error al conectar: {e}")
