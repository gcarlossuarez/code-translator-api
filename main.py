
"""
Punto de entrada principal para Replit
"""
import os
import sys
import glob
import subprocess

# Configurar variables de entorno para Replit
os.environ['REPLIT'] = 'true'
os.environ['SUPPRESS_SELENIUM_WARNINGS'] = 'true'
os.environ['DEBUG'] = 'false'
os.environ['LOG_LEVEL'] = 'INFO'

print("=" * 60)
print("🚀 Iniciando Code Translator API en Replit")
print("=" * 60)

# INSTALAR DEPENDENCIAS AUTOMÁTICAMENTE
print("📦 Verificando dependencias...")
try:
    import flask
    print("✅ Flask disponible")
except ImportError:
    print("📥 Instalando dependencias...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--user', '--quiet',
        'flask', 'flask-cors', 'waitress', 'selenium',
        'webdriver-manager', 'requests', 'python-dotenv'
    ])
    print("✅ Dependencias instaladas")

# Buscar Chromium y ChromeDriver automáticamente
print("🔍 Buscando Chromium y ChromeDriver...")

# Buscar chromium
chromium_path = None
try:
    result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
    if result.returncode == 0:
        chromium_path = result.stdout.strip()
except:
    pass

if not chromium_path:
    chromium_paths = glob.glob('/home/runner/.nix-profile/bin/chromium')
    if chromium_paths:
        chromium_path = chromium_paths[0]

if not chromium_path:
    chromium_paths = glob.glob('/nix/store/*-chromium-*/bin/chromium')
    if chromium_paths:
        chromium_path = chromium_paths[0]

if chromium_path:
    os.environ['CHROME_BIN'] = chromium_path
    print(f"✅ Chromium: {chromium_path}")
else:
    print("❌ Chromium NO encontrado")

# Buscar chromedriver
chromedriver_path = None
try:
    result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
    if result.returncode == 0:
        chromedriver_path = result.stdout.strip()
except:
    pass

if not chromedriver_path:
    chromedriver_paths = glob.glob('/home/runner/.nix-profile/bin/chromedriver')
    if chromedriver_paths:
        chromedriver_path = chromedriver_paths[0]

if not chromedriver_path:
    chromedriver_paths = glob.glob('/nix/store/*-chromedriver-*/bin/chromedriver')
    if chromedriver_paths:
        chromedriver_path = chromedriver_paths[0]

if chromedriver_path:
    os.environ['CHROMEDRIVER_PATH'] = chromedriver_path
    # Añadir al PATH
    chromedriver_dir = os.path.dirname(chromedriver_path)
    current_path = os.environ.get('PATH', '')
    os.environ['PATH'] = f"{chromedriver_dir}:{current_path}"
    print(f"✅ ChromeDriver: {chromedriver_path}")
    print(f"✅ PATH actualizado")
else:
    print("❌ ChromeDriver NO encontrado")

print("=" * 60)

# Importar y ejecutar el servidor
from api_server import app
from waitress import serve

PORT = int(os.environ.get('PORT', 8080))
HOST = '0.0.0.0'

print(f"📍 Servidor escuchando en puerto {PORT}")
print(f"🌐 URL: https://794d657b-57e9-4adb-95f6-84a12f944f65-00-2vf0i0bc6x0xp.worf.replit.dev")
print("=" * 60)

# Iniciar servidor
serve(app, host=HOST, port=PORT, threads=4)