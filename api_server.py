from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from waitress import serve

from zzzcode_translator import translate_code_zzzcode, parse_direction
import logging
from datetime import datetime
import traceback
import os

# Configurar logging antes de cualquier otra cosa
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suprimir warnings específicos si está configurado
if os.environ.get('SUPPRESS_SELENIUM_WARNINGS', 'true').lower() == 'true':
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('selenium').setLevel(logging.ERROR)
    logging.getLogger('werkzeug').setLevel(logging.INFO)  # Mantener logs de Flask

logger = logging.getLogger(__name__)

# Suprimir warnings de urllib3 de Selenium
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)



# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS para permitir llamadas desde CodePen y otros orígenes
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # En producción, especifica dominios permitidos
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Estadísticas simples
stats = {
    'total_requests': 0,
    'successful': 0,
    'failed': 0,
    'start_time': datetime.now()
}


@app.route('/')
def home():
    """Página de inicio con documentación de la API"""
    uptime = datetime.now() - stats['start_time']

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Translator API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
            }
            .endpoint {
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                font-family: monospace;
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .post { background: #27ae60; color: white; }
            .get { background: #3498db; color: white; }
            code {
                background: #34495e;
                color: #ecf0f1;
                padding: 2px 6px;
                border-radius: 3px;
            }
            pre {
                background: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .stats {
                background: #3498db;
                color: white;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .stat-item {
                background: rgba(255,255,255,0.2);
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔄 Code Translator API</h1>
            <p>API REST para traducir código entre C++ y C# usando zzzcode.ai</p>

            <div class="stats">
                <h3>📊 Estadísticas del Servidor</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">""" + str(stats['total_requests']) + """</div>
                        <div>Total Requests</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">""" + str(stats['successful']) + """</div>
                        <div>Exitosos</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">""" + str(stats['failed']) + """</div>
                        <div>Fallidos</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">""" + str(uptime).split('.')[0] + """</div>
                        <div>Uptime</div>
                    </div>
                </div>
            </div>

            <h2>📍 Endpoints Disponibles</h2>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/translate</strong>
                <p>Traduce código entre C++ y C#</p>
            </div>

            <h3>Parámetros (JSON):</h3>
            <pre>{
    "code": "string (código fuente)",
    "direction": "cpp_to_cs | cs_to_cpp",
    "mode": "game | study (opcional, default: study)"
}</pre>

            <h3>Ejemplo de Request:</h3>
            <pre>fetch('http://localhost:5000/api/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        code: '#include &lt;iostream&gt;\\n\\nint main() { return 0; }',
        direction: 'cpp_to_cs',
        mode: 'study'
    })
})
.then(res => res.json())
.then(data => console.log(data.translated_code));</pre>

            <h3>Respuesta Exitosa:</h3>
            <pre>{
    "success": true,
    "translated_code": "using System;\\n\\nclass Program {...}",
    "from_lang": "C++",
    "to_lang": "C#",
    "mode": "study",
    "timestamp": "2025-10-18T12:34:56"
}</pre>

            <h3>Respuesta de Error:</h3>
            <pre>{
    "success": false,
    "error": "Descripción del error",
    "timestamp": "2025-10-18T12:34:56"
}</pre>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/health</strong>
                <p>Verifica el estado del servidor</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/stats</strong>
                <p>Obtiene estadísticas del servidor</p>
            </div>

            <h2>🧪 Probar desde JavaScript (CodePen)</h2>
            <pre>// Función helper para tu juego
async function translateCode(code, direction = 'cpp_to_cs', mode = 'study') {
    try {
        const response = await fetch('http://localhost:5000/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, direction, mode })
        });

        const data = await response.json();

        if (data.success) {
            return data.translated_code;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error traduciendo código:', error);
        throw error;
    }
}</pre>

            <h2>⚙️ Configuración</h2>
            <ul>
                <li><strong>Puerto:</strong> 5000</li>
                <li><strong>Host:</strong> localhost (0.0.0.0 para acceso externo)</li>
                <li><strong>CORS:</strong> Habilitado para todos los orígenes</li>
            </ul>

            <p style="margin-top: 30px; color: #7f8c8d; text-align: center;">
                Desarrollado con Flask y Selenium • 2025
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/api/translate', methods=['POST', 'OPTIONS'])
def translate():
    """Endpoint principal para traducir código"""
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return '', 204

    stats['total_requests'] += 1

    try:
        # Validar que la petición tenga JSON
        if not request.is_json:
            stats['failed'] += 1
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'timestamp': datetime.now().isoformat()
            }), 400

        data = request.get_json()

        # Validar parámetros requeridos
        if 'code' not in data:
            stats['failed'] += 1
            return jsonify({
                'success': False,
                'error': 'Parámetro "code" es requerido',
                'timestamp': datetime.now().isoformat()
            }), 400

        if 'direction' not in data:
            stats['failed'] += 1
            return jsonify({
                'success': False,
                'error': 'Parámetro "direction" es requerido',
                'timestamp': datetime.now().isoformat()
            }), 400

        code = data['code']
        direction = data['direction']
        mode = data.get('mode', 'study')

        # Validar dirección
        if direction not in ['cpp_to_cs', 'cs_to_cpp']:
            stats['failed'] += 1
            return jsonify({
                'success': False,
                'error': 'direction debe ser "cpp_to_cs" o "cs_to_cpp"',
                'timestamp': datetime.now().isoformat()
            }), 400

        # Validar modo
        if mode not in ['game', 'study']:
            stats['failed'] += 1
            return jsonify({
                'success': False,
                'error': 'mode debe ser "game" o "study"',
                'timestamp': datetime.now().isoformat()
            }), 400

        # Log de la petición
        logger.info(f"Nueva petición - Direction: {direction}, Mode: {mode}, Code length: {len(code)}")

        # Obtener los lenguajes
        from_lang, to_lang = parse_direction(direction)

        # Realizar la traducción
        logger.info(f"Iniciando traducción de {from_lang} a {to_lang}")
        translated_code = translate_code_zzzcode(code, from_lang, to_lang)

        # Verificar que se obtuvo un resultado válido
        if not translated_code or "Error en la traducción" in translated_code:
            stats['failed'] += 1
            return jsonify({
                'success': False,
                'error': 'No se pudo traducir el código',
                'details': translated_code,
                'timestamp': datetime.now().isoformat()
            }), 500

        stats['successful'] += 1
        logger.info(f"Traducción exitosa - Resultado length: {len(translated_code)}")

        # Respuesta exitosa
        return jsonify({
            'success': True,
            'translated_code': translated_code,
            'from_lang': from_lang,
            'to_lang': to_lang,
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        stats['failed'] += 1
        logger.error(f"Error en traducción: {str(e)}")
        logger.error(traceback.format_exc())

        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint para verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': str(datetime.now() - stats['start_time']).split('.')[0]
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint para obtener estadísticas del servidor"""
    uptime = datetime.now() - stats['start_time']
    success_rate = (stats['successful'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0

    return jsonify({
        'total_requests': stats['total_requests'],
        'successful': stats['successful'],
        'failed': stats['failed'],
        'success_rate': f"{success_rate:.2f}%",
        'uptime': str(uptime).split('.')[0],
        'start_time': stats['start_time'].isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Manejador para rutas no encontradas"""
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejador para errores internos del servidor"""
    logger.error(f"Error interno del servidor: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'timestamp': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Iniciando Code Translator API Server")
    logger.info("=" * 60)
    logger.info("📍 Servidor disponible en: http://localhost:5000")
    logger.info("📖 Documentación en: http://localhost:5000")
    logger.info("🔍 Health check en: http://localhost:5000/api/health")
    logger.info("📊 Estadísticas en: http://localhost:5000/api/stats")
    logger.info("=" * 60)

    # Iniciar servidor
    # debug=True para desarrollo, cambiar a False en producción
    #app.run(host='0.0.0.0', port=5000, debug=True)

    # Usar Waitress (servidor WSGI de producción)
    serve(app, host='0.0.0.0', port=8080, threads=4)