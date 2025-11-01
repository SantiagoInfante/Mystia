from flask import Flask
from threading import Thread

# Crea una aplicación web simple
app = Flask('')

# Define una ruta que el monitor (UptimeRobot, etc.) visitará
@app.route('/')
def home():
    return "¡MystiaAi está viva y funcionando!"

# Función que ejecuta el servidor web
def run():
  # Flask se ejecuta en un hilo separado
  app.run(host='0.0.0.0', port=8080)

# Función principal que debe ser llamada desde main.py
def keep_alive():
    # Inicia el hilo del servidor web para que no bloquee el bot
    t = Thread(target=run)
    t.start()