import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:5000"


def test_health():
    """Prueba el endpoint de health check"""
    print("\n" + "=" * 60)
    print("🔍 Probando Health Check...")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_stats():
    """Prueba el endpoint de estadísticas"""
    print("\n" + "=" * 60)
    print("📊 Obteniendo Estadísticas...")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_translate_cpp_to_cs():
    """Prueba traducción de C++ a C#"""
    print("\n" + "=" * 60)
    print("🔄 Probando Traducción: C++ → C#")
    print("=" * 60)

    code_cpp = """
#include <iostream>
#include <string>

int main() {
    std::string message = "Hello from C++";
    std::cout << message << std::endl;
    return 0;
}
"""

    payload = {
        "code": code_cpp,
        "direction": "cpp_to_cs",
        "mode": "study"
    }

    print("Código a traducir:")
    print(code_cpp)
    print("\nEnviando petición...")

    response = requests.post(
        f"{BASE_URL}/api/translate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("\n✅ Traducción exitosa!")
            print(f"De: {data['from_lang']} → A: {data['to_lang']}")
            print(f"Modo: {data['mode']}")
            print("\nCódigo traducido:")
            print("-" * 60)
            print(data['translated_code'])
            print("-" * 60)
            return True
        else:
            print(f"\n❌ Error: {data['error']}")
            return False
    else:
        print(f"\n❌ Error HTTP: {response.text}")
        return False


def test_translate_cs_to_cpp():
    """Prueba traducción de C# a C++"""
    print("\n" + "=" * 60)
    print("🔄 Probando Traducción: C# → C++")
    print("=" * 60)

    code_cs = """
using System;

class Program {
    static void Main() {
        string message = "Hello from C#";
        Console.WriteLine(message);
    }
}
"""

    payload = {
        "code": code_cs,
        "direction": "cs_to_cpp",
        "mode": "game"
    }

    print("Código a traducir:")
    print(code_cs)
    print("\nEnviando petición...")

    response = requests.post(
        f"{BASE_URL}/api/translate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("\n✅ Traducción exitosa!")
            print(f"De: {data['from_lang']} → A: {data['to_lang']}")
            print(f"Modo: {data['mode']}")
            print("\nCódigo traducido:")
            print("-" * 60)
            print(data['translated_code'])
            print("-" * 60)
            return True
        else:
            print(f"\n❌ Error: {data['error']}")
            return False
    else:
        print(f"\n❌ Error HTTP: {response.text}")
        return False


def test_invalid_request():
    """Prueba con una petición inválida"""
    print("\n" + "=" * 60)
    print("⚠️  Probando Petición Inválida...")
    print("=" * 60)

    payload = {
        "direction": "cpp_to_cs"
        # Falta el parámetro 'code'
    }

    response = requests.post(
        f"{BASE_URL}/api/translate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Debe retornar error 400
    return response.status_code == 400


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "=" * 60)
    print("🧪 INICIANDO SUITE DE PRUEBAS DE LA API")
    print("=" * 60)
    print("\n⚠️  Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    input("\nPresiona ENTER para continuar...")

    results = {
        "Health Check": test_health(),
        "Estadísticas": test_stats(),
        "Traducción C++ → C#": test_translate_cpp_to_cs(),
        "Traducción C# → C++": test_translate_cs_to_cpp(),
        "Petición Inválida": test_invalid_request()
    }

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n{passed}/{total} pruebas pasaron ({passed / total * 100:.1f}%)")

    # Mostrar estadísticas finales
    test_stats()


if __name__ == "__main__":
    main()