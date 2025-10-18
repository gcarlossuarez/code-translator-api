"""
Script para iniciar el servidor con configuración apropiada
"""
import os
import sys
import argparse
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description='Iniciar Code Translator API Server')
    parser.add_argument(
        '--mode',
        choices=['dev', 'prod'],
        default='dev',
        help='Modo de ejecución: dev (desarrollo) o prod (producción)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Puerto del servidor (default: 5000 dev, 8080 prod)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host del servidor (default: 0.0.0.0)'
    )

    args = parser.parse_args()

    # Cargar variables de entorno
    load_dotenv()

    # Suprimir warnings de Selenium
    os.environ['SUPPRESS_SELENIUM_WARNINGS'] = 'true'

    if args.mode == 'dev':
        # Modo desarrollo con Flask
        port = args.port or int(os.environ.get('PORT', 5000))
        print("\n" + "=" * 60)
        print("🔧 MODO DESARROLLO")
        print("=" * 60)
        print(f"Puerto: {port}")
        print(f"Debug: Activado")
        print(f"Auto-reload: Activado")
        print("=" * 60 + "\n")

        from api_server import app
        app.run(host=args.host, port=port, debug=True)

    else:
        # Modo producción con Waitress
        port = args.port or int(os.environ.get('PORT', 8080))
        print("\n" + "=" * 60)
        print("🚀 MODO PRODUCCIÓN")
        print("=" * 60)
        print(f"Puerto: {port}")
        print(f"Workers: 4 threads")
        print(f"Servidor: Waitress")
        print("=" * 60 + "\n")

        try:
            from waitress import serve
            from api_server import app
            serve(app, host=args.host, port=port, threads=4)
        except ImportError:
            print("❌ Error: waitress no está instalado")
            print("Instala con: pip install waitress")
            sys.exit(1)


if __name__ == '__main__':
    main()