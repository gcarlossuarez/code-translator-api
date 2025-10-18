
"""
Punto de entrada principal para Replit
"""
import os
import sys

# Configurar variables de entorno para Replit
os.environ['REPLIT'] = 'true'
os.environ['SUPPRESS_SELENIUM_WARNINGS'] = 'true'
os.environ['DEBUG'] = 'false'
os.environ['LOG_LEVEL'] = 'INFO'

# Configurar paths de Chrome para Replit
os.environ['CHROME_BIN'] = '/nix/store/*-chromium-*/bin/chromium'
os.environ['CHROMEDRIVER_PATH'] = '/nix/store/*-chromedriver-*/bin/chromedriver'

print("=" * 60)
print("🚀 Iniciando Code Translator API en Replit")
print("=" * 60)

# Importar y ejecutar el servidor
from api_server import app
from waitress import serve

# Replit usa el puerto 8080 por defecto
PORT = int(os.environ.get('PORT', 8080))
HOST = '0.0.0.0'

print(f"📍 Servidor escuchando en puerto {PORT}")
print(f"🌐 URL pública: Disponible en la pestaña 'Webview' de Replit")
print("=" * 60)

# Iniciar servidor
serve(app, host=HOST, port=PORT, threads=4)