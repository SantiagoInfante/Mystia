import discord
import os
import random
from discord.ext import commands 
from discord import app_commands # Importación necesaria para bot.tree
from dotenv import load_dotenv
from hf_api import query_hf # Importación de la función de IA
from keep_alive import keep_alive # Módulo para mantener el bot vivo

# Carga las variables del archivo .env
load_dotenv()

# --- Configuración de Intents (Permisos) ---
intents = discord.Intents.default()
intents.message_content = True 
intents.messages = True

# --- Inicialización del Bot ---
# Ahora usamos 'app_commands.CommandTree' para manejar comandos de barra
bot = commands.Bot(command_prefix='!', intents=intents) 

# --- CONFIGURACIÓN DE IA ---
# Define el modelo de Hugging Face a usar.
# Usamos un modelo válido para evitar errores 404/StopIteration.
MODELO_IA = "tiiuae/falcon-7b-instruct" 


# =========================================================
# Evento on_ready (Sincronización de Comandos)
# =========================================================
@bot.event 
async def on_ready():
    print(f'¡MystiaAi está conectada como {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="charlar contigo 💕"))
    
    # --- SINCRONIZACIÓN: Envía el comando /ping a Discord ---
    try:
        # La forma recomendada es bot.tree.sync()
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)} comandos.")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")
    print('--------------------------------------------------')


# =========================================================
# COMANDO DE BARRA INCLINADA (/PING) - ¡Respuesta Pública con Embed!
# =========================================================
# Usamos bot.tree.command
@bot.tree.command(name="ping", description="Comprueba si MystiaAi está activa y muestra la latencia.")
async def ping_command(interaction: discord.Interaction):
    
    # 1. Crear el Embed con el mensaje "Pong"
    embed = discord.Embed(
        title="🏓 ¡Pong!",
        description="¡MystiaAi está online y funcionando perfectamente! 😊",
        color=0x40E0D0 # Color turquesa
    )
    
    # Muestra la latencia (ping) real del bot
    embed.add_field(
        name="Latencia:",
        value=f"**{round(bot.latency * 1000)}ms**", # bot.latency da la latencia en segundos
        inline=True
    )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
    
    # 2. Enviar el Embed. Al no usar 'ephemeral=True', es visible para todos.
    await interaction.response.send_message(embed=embed)


# =========================================================
# Lógica de Mensaje (on_message) - Respuestas predefinidas Y LLAMADA A LA IA
# =========================================================
@bot.event 
async def on_message(message):
    # 1. No queremos que el bot se responda a sí mismo
    if message.author == bot.user: 
        return

    # 2. Procesar comandos de prefijo (si los hay), antes de la lógica de mención
    await bot.process_commands(message) 

    # 3. Comprobar si el bot fue mencionado
    if bot.user.mentioned_in(message):
        
        # Preparamos el contenido del mensaje para análisis
        mention_string_id = f'<@{bot.user.id}>'
        mention_string_nick = f'<@!{bot.user.id}>'
        
        content_lower = message.content.lower()
        # Limpia el contenido de ambas formas de mención posibles
        content_cleaned = message.content.replace(mention_string_id, '').replace(mention_string_nick, '').strip()

        # --- LÓGICA DE RESPUESTA ---
        
        # 1. Mención simple (sin más texto)
        if not content_cleaned:
            respuestas_amables = [
                f'¡Hola, {message.author.display_name}! ✨ ¿Necesitas algo, cielo?',
                '¡Aquí estoy! ¿En qué puedo ayudarte, corazón? 😊',
                f'¿Me llamabas, {message.author.display_name}? ¡Siempre es un gusto saludarte! 🥰'
            ]
            await message.channel.send(random.choice(respuestas_amables))
            return # Detiene la ejecución para no caer en la IA

        # 2. Respuestas ESPECÍFICAS programadas (Si se detecta una frase clave)
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
            
        # 3. RESPUESTA DE IA (El Comodín Final)
        
        # Notifica al usuario que está procesando la pregunta
        async with message.channel.typing():
            # Llama a la función de la API de Hugging Face
            respuesta_ia = query_hf(content_cleaned, MODELO_IA)
            
        # Envía la respuesta generada por la IA
        respuesta_discord = f"**Pregunta:** *{content_cleaned}*\n**MystiaAi dice:** {respuesta_ia}"
        await message.channel.send(respuesta_discord)


# --- Configuración del Token y Ejecución ---

TOKEN = os.environ.get('DISCORD_TOKEN')

if TOKEN is None:
    print("Error: No se encontró el DISCORD_TOKEN.")
else:
    try:
        keep_alive() # Llama a la función 24/7 antes de iniciar el bot.
        bot.run(TOKEN) 
    except discord.errors.HTTPException as e:
        print(f"Error al conectar: {e}")
