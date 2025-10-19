"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import argparse
import logging
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

# Configuración para modo debug
DEBUG_MODE = os.environ.get('DEBUG', 'true').lower() == 'true'
"""
import os
import sys
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

# Suprimir warnings de urllib3 para Selenium
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)

# Configuración para modo debug
DEBUG_MODE = os.environ.get('DEBUG', 'true').lower() == 'true'


def get_chrome_options():
    """Configura las opciones de Chrome según el entorno"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    # Configuración específica para Replit/Linux
    if os.environ.get('REPLIT') or sys.platform.startswith('linux'):
        # Buscar chromium en Replit
        chrome_bin = os.environ.get('CHROME_BIN')
        if chrome_bin:
            options.binary_location = chrome_bin
        else:
            # Intentar encontrar chromium automáticamente
            possible_paths = [
                '/nix/store/*-chromium-*/bin/chromium',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/usr/bin/google-chrome'
            ]
            import glob
            for path_pattern in possible_paths:
                matches = glob.glob(path_pattern)
                if matches:
                    options.binary_location = matches[0]
                    print(f"Chrome encontrado en: {matches[0]}")
                    break

    return options

def clean_translated_code(translated_code: str, original_code: str, target_lang: str) -> str:
    """
    Limpia el código traducido removiendo comentarios innecesarios y texto adicional.

    Args:
        translated_code: Código traducido raw de zzzcode.ai
        original_code: Código original (para comparación)
        target_lang: Lenguaje de destino

    Returns:
        Código limpio y formateado
    """
    lines = translated_code.split('\n')
    cleaned_lines = []

    # Detectar si TODO el código está comentado (caso problemático)
    non_empty_lines = [l.strip() for l in lines if l.strip()]
    all_commented = all(
        line.startswith('//') or line.startswith('/*') or line.startswith('*')
        for line in non_empty_lines
    )

    if all_commented:
        print("⚠️ Detectado: Todo el código está comentado. Descomentando...")
        # Descomentando líneas
        for line in lines:
            stripped = line.strip()

            # Remover // al inicio
            if stripped.startswith('// '):
                cleaned_lines.append(line.replace('// ', '', 1))
            elif stripped.startswith('//'):
                cleaned_lines.append(line.replace('//', '', 1))
            # Ignorar marcadores de comentarios de bloque
            elif stripped in ['/*', '*/', '/**', '**/']:
                continue
            # Remover * al inicio de líneas de comentario de bloque
            elif stripped.startswith('* '):
                cleaned_lines.append(line.replace('* ', '', 1))
            elif stripped.startswith('*') and len(stripped) > 1:
                cleaned_lines.append(line.replace('*', '', 1))
            else:
                cleaned_lines.append(line)
    else:
        # Caso normal: remover solo comentarios iniciales
        skip_initial_comments = True
        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            # Detectar inicio/fin de comentario de bloque
            if '/*' in stripped:
                in_block_comment = True

            if skip_initial_comments:
                # Saltar comentarios solo al inicio del archivo
                if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    if '*/' in stripped:
                        in_block_comment = False
                    continue
                elif in_block_comment:
                    if '*/' in stripped:
                        in_block_comment = False
                    continue
                elif stripped == '':
                    continue
                else:
                    # Primera línea de código real
                    skip_initial_comments = False
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)

            if '*/' in stripped:
                in_block_comment = False

    result = '\n'.join(cleaned_lines).strip()

    # Validación adicional
    if len(result) < 10:
        print(f"⚠️ Advertencia: Código limpio muy corto ({len(result)} chars)")
        print(f"Original length: {len(translated_code)}")
        # Si la limpieza fue demasiado agresiva, devolver el original
        if len(translated_code.strip()) > len(result) * 2:
            print("Usando código sin limpiar por seguridad")
            return translated_code.strip()

    return result


def translate_code_zzzcode(code: str, from_lang: str, to_lang: str) -> str:
    """Traduce código usando zzzcode.ai a través de Selenium."""
    options = get_chrome_options()

    driver = None
    try:
        print("🔧 Configurando ChromeDriver...")

        # Usar webdriver-manager para manejar ChromeDriver automáticamente
        if os.environ.get('REPLIT'):
            service = Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            )
            print("✅ Usando Chromium para Replit")
        else:
            service = Service(ChromeDriverManager().install())
            print("✅ Usando Chrome estándar")

        driver = webdriver.Chrome(service=service, options=options)
        print("✅ ChromeDriver iniciado correctamente")

        driver.get("https://zzzcode.ai/code-converter")

        # Esperar a que los elementos estén presentes y sean interactuables
        wait = WebDriverWait(driver, 30)

        # Rellenar el lenguaje de origen
        print("Rellenando lenguaje de origen...")
        from_lang_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='From language']/following-sibling::input")))
        from_lang_input.clear()
        from_lang_input.send_keys(from_lang)
        time.sleep(0.5)  # Esperar a que aparezcan las opciones
        from_lang_input.send_keys(Keys.RETURN)
        time.sleep(0.5)

        # Rellenar el lenguaje de destino
        print("Rellenando lenguaje de destino...")
        to_lang_input = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='To language']/following-sibling::input")))
        to_lang_input.clear()
        to_lang_input.send_keys(to_lang)
        time.sleep(0.5)
        to_lang_input.send_keys(Keys.RETURN)
        time.sleep(0.5)

        # Rellenar el código a convertir
        print("Rellenando código a convertir...")
        code_textarea = wait.until(EC.presence_of_element_located((By.XPATH, "//label[text()='Code to convert']/following-sibling::textarea")))
        code_textarea.clear()
        code_textarea.send_keys(code)
        time.sleep(1)

        # Intentar diferentes estrategias para encontrar y hacer clic en el botón
        print("Buscando botón Execute...")
        execute_button = None
        
        # Estrategia 2: Buscar por tipo submit
        if not execute_button:
            try:
                execute_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                print("Botón encontrado con estrategia 2")
            except:
                pass

        # Estrategia 1: Buscar por texto 'Execute'
        try:
            execute_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Execute')]")))
            print("Botón encontrado con estrategia 1")
        except:
            pass

        # Estrategia 3: Buscar cualquier botón cerca del textarea
        if not execute_button:
            try:
                execute_button = driver.find_element(By.XPATH, "//textarea/following::button[1]")
                print("Botón encontrado con estrategia 3")
            except:
                pass
        
        if not execute_button:
            raise Exception("No se pudo encontrar el botón Execute")
        
        # Scroll al botón para asegurarse de que es visible
        driver.execute_script("arguments[0].scrollIntoView(true);", execute_button)
        time.sleep(0.5)
        
        # Intentar hacer clic con JavaScript si el clic normal falla

        print("Haciendo clic en el botón...")
        try:
            execute_button.click()
        except:
            print("Clic normal falló, intentando con JavaScript...")
            driver.execute_script("arguments[0].click();", execute_button)

        print("Esperando resultado de la traducción...")
        # Esperar más tiempo para el resultado (el sitio puede tardar en procesar)
        # Probar diferentes estrategias para encontrar el resultado
        translated_code = None

        # Estrategia 3: Buscar por pre/code directamente
        print("Esperando resultado de la traducción...")
        # Esperar más tiempo para el resultado (el sitio puede tardar en procesar)
        # Probar diferentes estrategias para encontrar el resultado
        translated_code = None

        # Estrategia 3: Buscar por pre/code directamente con reintentos
        if not translated_code:
            try:
                print("Intentando estrategia 3 para encontrar resultado...")
                time.sleep(5)
                # Reintentar hasta 3 veces para manejar elementos "stale"
                for attempt in range(3):
                    try:
                        pre_elements = driver.find_elements(By.TAG_NAME, "pre")
                        for pre in pre_elements:
                            try:
                                code_in_pre = pre.find_elements(By.TAG_NAME, "code")
                                if code_in_pre and code_in_pre[0].text.strip():
                                    potential_result = code_in_pre[0].text.strip()
                                    # Verificar que no es el código original
                                    if potential_result != code.strip() and len(potential_result) > 10:
                                        translated_code = potential_result
                                        print("Resultado encontrado con estrategia 3")
                                        break
                            except:
                                continue
                        if translated_code:
                            break
                        time.sleep(2)
                    except Exception as e:
                        if attempt == 2:
                            raise e
                        time.sleep(2)
            except Exception as e3:
                print(f"Estrategia 3 falló: {e3}")

        # Estrategia 5: Usar JavaScript para extraer el contenido
        if not translated_code:
            try:
                print("Intentando estrategia 5 (JavaScript) para encontrar resultado...")
                time.sleep(5)
                # Usar JavaScript para obtener todos los elementos code
                js_code = """
                var codes = document.querySelectorAll('pre code');
                var results = [];
                for(var i = 0; i < codes.length; i++) {
                    if(codes[i].textContent.trim().length > 10) {
                        results.push(codes[i].textContent);
                    }
                }
                return results;
                """
                code_contents = driver.execute_script(js_code)

                if code_contents and len(code_contents) >= 2:
                    # Tomar el último que sea diferente al código original
                    for content in reversed(code_contents):
                        if content.strip() != code.strip():
                            translated_code = content
                            print("Resultado encontrado con estrategia 5")
                            break
            except Exception as e5:
                print(f"Estrategia 5 falló: {e5}")

        # Estrategia 2: Buscar cualquier elemento <code> que aparezca después del clic
        if not translated_code:
            try:
                print("Intentando estrategia 2 para encontrar resultado...")
                time.sleep(8)  # Dar más tiempo para que cargue completamente
                code_elements = driver.find_elements(By.TAG_NAME, "code")
                if len(code_elements) > 1:  # El segundo code suele ser el resultado
                    translated_code = code_elements[-1].text
                    print("Resultado encontrado con estrategia 2")
            except Exception as e2:
                print(f"Estrategia 2 falló: {e2}")

        # Estrategia 1: Buscar por el h2 "Code Converted"
        if not translated_code:
            try:
                print("Intentando estrategia 1 para encontrar resultado...")
                translated_code_element = WebDriverWait(driver, 45).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//h2[contains(text(),'Code Converted')]/following-sibling::pre/code"))
                )
                time.sleep(3)  # Aumentar tiempo de espera
                translated_code = translated_code_element.text
                print("Resultado encontrado con estrategia 1")
            except Exception as e1:
                print(f"Estrategia 1 falló: {e1}")

        # Estrategia 4: Esperar a que cambie el contenido de la página con más paciencia
        if not translated_code:
            try:
                print("Intentando estrategia 4 para encontrar resultado...")
                # Esperar hasta 90 segundos a que aparezca algún resultado (código largo tarda más)
                for i in range(18):  # 18 intentos de 5 segundos = 90 segundos
                    time.sleep(5)
                    print(f"Esperando... intento {i + 1}/18")
                    try:
                        # Re-buscar elementos cada vez para evitar stale elements
                        code_elements = driver.find_elements(By.XPATH, "//pre/code")
                        print(f"  Encontrados {len(code_elements)} elementos <code>")

                        if len(code_elements) >= 2:
                            # Intentar obtener el último elemento
                            last_element = code_elements[-1]
                            translated_code = last_element.text

                            if translated_code and translated_code.strip() != code.strip() and len(
                                    translated_code.strip()) > 10:
                                print("Resultado encontrado con estrategia 4")
                                break
                            else:
                                translated_code = None
                    except Exception as inner_e:
                        print(f"  Error en intento {i + 1}: {str(inner_e)[:100]}")
                        continue
            except Exception as e4:
                print(f"Estrategia 4 falló: {e4}")

        if not translated_code or translated_code.strip() == "":
            raise Exception("El código traducido está vacío o no se pudo encontrar después de múltiples intentos")

        # Limpiar comentarios generados automáticamente
        lines = translated_code.split('\n')
        cleaned_lines = []
        skip_comments = True

        for line in lines:
            stripped = line.strip()
            # Saltar comentarios iniciales
            if skip_comments and (stripped.startswith('//') or stripped.startswith('/*') or
                                  stripped.startswith('*') or stripped == '*/'):
                continue
            skip_comments = False
            cleaned_lines.append(line)

            # Limpiar y procesar el código traducido
        result = clean_translated_code(translated_code, code, to_lang)
        print("Traducción completada exitosamente")
        return result

    except Exception as e:
        print(f"Ocurrió un error durante la traducción: {e}")
        if driver:
            # Intentar capturar el HTML de la página en caso de error para depuración
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Se ha guardado el HTML de la página en 'error_page.html' para depuración.")
            
            # Capturar screenshot si es posible
            try:
                driver.save_screenshot("error_screenshot.png")
                print("Se ha guardado un screenshot en 'error_screenshot.png'")
            except:
                pass
        
        return f"Error en la traducción: {str(e)}"
    finally:
        if driver:
            driver.quit()

            driver.quit()


def parse_direction(direction: str) -> tuple[str, str]:
    """
    Convierte la dirección de traducción a lenguajes origen y destino.

    Args:
        direction: 'cpp_to_cs' o 'cs_to_cpp'

    Returns:
        Tupla (lenguaje_origen, lenguaje_destino)
    """
    direction_map = {
        'cpp_to_cs': ('C++', 'C#'),
        'cs_to_cpp': ('C#', 'C++'),
    }

    if direction not in direction_map:
        raise ValueError(f"Dirección inválida: {direction}. Usa 'cpp_to_cs' o 'cs_to_cpp'")

    return direction_map[direction]


def main():
    """Función principal que maneja argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Traductor de código entre C++ y C# usando zzzcode.ai',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python zzzcode_translator.py "código aquí" cpp_to_cs
  python zzzcode_translator.py "código aquí" cs_to_cpp game
  python zzzcode_translator.py archivo.cpp cpp_to_cs study
        """
    )

    parser.add_argument(
        'source',
        help='Código fuente a traducir o ruta a archivo con el código'
    )

    parser.add_argument(
        'direction',
        choices=['cpp_to_cs', 'cs_to_cpp'],
        help='Dirección de traducción: cpp_to_cs (C++ a C#) o cs_to_cpp (C# a C++)'
    )

    parser.add_argument(
        'mode',
        nargs='?',
        choices=['game', 'study'],
        default='study',
        help='Modo de traducción: game o study (por defecto: study)'
    )

    # Valores por defecto para modo debug
    if DEBUG_MODE and len(sys.argv) == 1:
        print("=== MODO DEBUG ACTIVADO ===")
        print("Usando valores por defecto para debug\n")

        # Código de ejemplo por defecto
        default_code = """
#include <iostream>

int main() {
    std::cout << "Hello, C++!" << std::endl;
    return 0;
}
"""
        args = argparse.Namespace(
            source=default_code,
            direction='cpp_to_cs',
            mode='study'
        )
    else:
        args = parser.parse_args()

    # Determinar si el source es un archivo o código directo
    code_to_translate = args.source

    if os.path.isfile(args.source):
        print(f"Leyendo código desde archivo: {args.source}")
        with open(args.source, 'r', encoding='utf-8') as f:
            code_to_translate = f.read()
    else:
        print("Usando código proporcionado directamente")

    # Obtener los lenguajes desde la dirección
    from_lang, to_lang = parse_direction(args.direction)

    print(f"\n{'=' * 60}")
    print(f"Configuración de traducción:")
    print(f"  Dirección: {args.direction}")
    print(f"  De: {from_lang} → A: {to_lang}")
    print(f"  Modo: {args.mode}")
    print(f"{'=' * 60}\n")

    print("Código a traducir:")
    print("-" * 60)
    print(code_to_translate)
    print("-" * 60)
    print()

    # Realizar la traducción
    print("Iniciando traducción...\n")
    translated_code = translate_code_zzzcode(code_to_translate, from_lang, to_lang)

    print("\n" + "=" * 60)
    print("RESULTADO DE LA TRADUCCIÓN:")
    print("=" * 60)
    print(translated_code)
    print("=" * 60)

    # TODO: Aquí se podrán agregar funcionalidades según el modo (game/study)
    if args.mode == 'game':
        print("\n[INFO] Modo 'game' seleccionado (funcionalidad pendiente)")
    elif args.mode == 'study':
        print("\n[INFO] Modo 'study' seleccionado (funcionalidad pendiente)")


if __name__ == "__main__":
    # Ejemplos antiguos comentados para referencia
    """
    # Ejemplo de código C#
    csharp_example = \"\"\"
using System;

public class HelloWorld
{
    public static void Main(string[] args)
    {
        Console.WriteLine("Hello, C#!");
    }
}
\"\"\"

    print("\\n--- Traduciendo C# a C++ ---")
    translated_cpp = translate_code_zzzcode(csharp_example, "C#", "C++")
    print("Código C++ traducido:\\n")
    print(translated_cpp)

    # Ejemplo de código C++
    cpp_example = \"\"\"
#include <iostream>

int main() {
    std::cout << "Hello, C++!" << std::endl;
    return 0;
}
\"\"\"

    print("\\n--- Traduciendo C++ a C# ---")
    translated_csharp = translate_code_zzzcode(cpp_example, "C++", "C#")
    print("Código C# traducido:\\n")
    print(translated_csharp)
    """

if __name__ == '__main__':
    main()