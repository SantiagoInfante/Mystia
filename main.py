import discord
import requests
import os

# Cargar las variables de entorno del archivo .env
load_dotenv()

# --- Configuración de Tokens y API ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HFAPI_TOKEN = os.getenv("HFAPI_TOKEN")

# Elige un modelo de texto gratuito en Hugging Face (text-generation)
# Puedes cambiar este modelo por otro que te guste, como 'google/gemma-2b' o 'mistralai/Mistral-7B-v0.1'
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b"

# --- Inicialización del Bot de Discord ---
intents = discord.Intents.default()
intents.message_content = True 

client = discord.Client(intents=intents)

# --- Función para comunicarse con la API de Hugging Face ---
def generate_response(prompt):
    """
    Envía el prompt al modelo de Hugging Face a través de su API.
    """
    if not HUGGINGFACE_TOKEN:
        return "Error: Token de Hugging Face no configurado."
        
    headers = {"Authorization": f"Bearer {HFAPI_TOKEN}"}
    
    # Parámetros para la generación de texto
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100, # Longitud máxima de la respuesta
            "temperature": 0.8,
            "return_full_text": False # Solo devuelve el texto generado, no el prompt + texto
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Lanza una excepción para códigos de estado de error (4xx o 5xx)
        
        # El formato de respuesta es una lista de diccionarios
        result = response.json()
        if result and isinstance(result, list) and 'generated_text' in result[0]:
            # Limpiamos el texto para asegurar que no contenga el prompt si API lo incluyó
            reply = result[0]['generated_text'].strip()
            return reply
        else:
            print(f"Respuesta inesperada de la API: {result}")
            return "Lo siento, la API me dio una respuesta inválida."

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API de Hugging Face: {e}")
        return "Lo siento, no pude conectarme al servidor de IA. Inténtalo más tarde."

# --- Eventos de Discord ---

@client.event
async def on_ready():
    """Se ejecuta cuando el bot se ha conectado a Discord."""
    print(f'🤖 Bot de IA conectado como {client.user}!')
    print('-------------------------------------------')

@client.event
async def on_message(message):
    """Se ejecuta cada vez que se envía un mensaje."""
    
    # 1. Ignorar mensajes del propio bot
    if message.author == client.user:
        return

    # 2. Verificar si el bot fue mencionado
    if client.user.mentioned_in(message):
        
        # Obtener el texto del mensaje sin la mención del bot
        mention_string = client.user.mention
        prompt = message.content.replace(mention_string, '').strip()
        
        if not prompt:
            prompt = "Hola, ¿cómo estás?" # Mensaje por defecto si solo se menciona

        # Enviamos un mensaje de "Pensando..."
        typing_task = client.loop.create_task(message.channel.typing()) # Muestra el estado de "Escribiendo..."
        
        try:
            # 3. Llamar a la función de generación de texto (se conecta a Hugging Face)
            reply = generate_response(prompt)
            
            # 4. Enviar la respuesta
            await message.reply(reply) 
            
        finally:
            typing_task.cancel() # Detenemos el estado de "Escribiendo..."

# --- Ejecución del Bot ---

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("🛑 ERROR: No se encontró el DISCORD_TOKEN en el archivo .env.")
    elif not HUGGINGFACE_TOKEN:
        print("🛑 AVISO: No se encontró el HFAPI_TOKEN en el archivo .env. La IA no funcionará.")
    else:
        client.run(DISCORD_TOKEN)

