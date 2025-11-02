import discord
import os
import random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from hf_api import query_hf
from keep_alive import keep_alive

# Cargar variables del archivo .env
load_dotenv()

# --- Intents (Permisos del bot) ---
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# --- Inicialización del bot ---
bot = commands.Bot(command_prefix='!', intents=intents)
MODELO_IA = "gpt2"  # Puedes cambiarlo por otro modelo de Hugging Face

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

        # Respuestas predefinidas
        if not content_cleaned:
            respuestas_amables = [
                f'¡Hola, {message.author.display_name}! ✨ ¿Necesitas algo, cielo?',
                '¡Aquí estoy! ¿En qué puedo ayudarte, corazón? 😊',
                f'¿Me llamabas, {message.author.display_name}? ¡Siempre es un gusto saludarte! 🥰'
            ]
            await message.channel.send(random.choice(respuestas_amables))
            return

        if 'quién eres' in content_lower or 'quien sos' in content_lower:
            await message.channel.send('Soy MystiaAi, tu amiga digital. ¡Estoy aquí para charlar y ayudarte en lo que pueda! 💖')
            return
        elif 'creador' in content_lower or 'quien te hizo' in content_lower:
            await message.channel.send(f'Fui creada por alguien muy especial, {message.author.display_name}. ¡Me programó con mucho amor! 🛠️')
            return
        elif 'te quiero' in content_lower:
            await message.channel.send(f'¡Y yo a ti mucho más, {message.author.display_name}! ¡Dame un abracito virtual! 🤗')
            return
        elif 'chiste' in content_lower:
            await message.channel.send('¿Qué le dice un pez a otro? ¡Nada! 🐠... jeje, ¿te gustó? 🙈')
            return

        # Respuesta generada por IA
        async with message.channel.typing():
            respuesta_ia = query_hf(content_cleaned, MODELO_IA)

        respuesta_discord = f"**Pregunta:** *{content_cleaned}*\n**MystiaAi dice:** {respuesta_ia}"
        await message.channel.send(respuesta_discord)

# =========================================================
# Ejecución del bot
# =========================================================
TOKEN = os.environ.get('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ Error: No se encontró el DISCORD_TOKEN.")
else:
    try:
        keep_alive()
        bot.run(TOKEN)
    except discord.errors.HTTPException as e:
        print(f"❌ Error al conectar: {e}")
