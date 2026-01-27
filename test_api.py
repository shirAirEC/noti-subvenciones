#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de pruebas para la API del sistema de notificaciones de subvenciones
"""

import requests
import json
import sys
import io
from datetime import datetime

# Configurar stdout para UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}[OK] {text}{RESET}")

def print_error(text):
    print(f"{RED}[ERROR] {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}[INFO] {text}{RESET}")

def test_endpoint(base_url, endpoint, method='GET', data=None, description=""):
    """Prueba un endpoint de la API"""
    url = f"{base_url}{endpoint}"
    print(f"\n{YELLOW}Probando:{RESET} {method} {endpoint}")
    if description:
        print(f"  {description}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        # Mostrar respuesta
        print(f"  Status: {response.status_code}")
        
        if response.status_code < 400:
            print_success(f"Respuesta exitosa")
            try:
                json_data = response.json()
                print(f"  Datos: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}")
                return True, json_data
            except:
                print(f"  Texto: {response.text[:500]}")
                return True, response.text
        else:
            print_error(f"Error en la respuesta")
            print(f"  {response.text[:500]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print_error(f"No se pudo conectar a {url}")
        print_info("Verifica que el servidor esté corriendo")
        return False, None
    except requests.exceptions.Timeout:
        print_error(f"Timeout al conectar a {url}")
        return False, None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False, None

def run_tests(base_url):
    """Ejecuta todas las pruebas"""
    
    print_header("PRUEBAS DE LA API DE SUBVENCIONES")
    print(f"URL Base: {base_url}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Test 1: Health Check
    print_header("1. HEALTH CHECK")
    success, data = test_endpoint(
        base_url, 
        "/health",
        description="Verifica que el servidor esté funcionando"
    )
    results['total'] += 1
    if success:
        results['passed'] += 1
        if data and isinstance(data, dict):
            print_info(f"Scheduler activo: {data.get('scheduler', 'N/A')}")
    else:
        results['failed'] += 1
        print_error("El servidor no está respondiendo correctamente")
        return results
    
    # Test 2: Regiones
    print_header("2. CATÁLOGO DE REGIONES")
    success, regiones = test_endpoint(
        base_url,
        "/api/regiones",
        description="Obtiene el catálogo de regiones disponibles"
    )
    results['total'] += 1
    if success:
        results['passed'] += 1
        if regiones:
            print_info(f"Total de regiones: {len(regiones)}")
            if len(regiones) > 0:
                print_info(f"Primera región: {regiones[0].get('nombre', 'N/A')}")
    else:
        results['failed'] += 1
    
    # Test 3: Áreas Temáticas
    print_header("3. CATÁLOGO DE ÁREAS TEMÁTICAS")
    success, areas = test_endpoint(
        base_url,
        "/api/areas",
        description="Obtiene el catálogo de áreas temáticas"
    )
    results['total'] += 1
    if success:
        results['passed'] += 1
        if areas:
            print_info(f"Total de áreas: {len(areas)}")
    else:
        results['failed'] += 1
    
    # Test 4: Subvenciones
    print_header("4. LISTA DE SUBVENCIONES")
    success, subvenciones = test_endpoint(
        base_url,
        "/api/subvenciones?limit=5",
        description="Obtiene las últimas 5 subvenciones"
    )
    results['total'] += 1
    if success:
        results['passed'] += 1
        if subvenciones:
            print_info(f"Total de subvenciones: {len(subvenciones)}")
            if len(subvenciones) > 0:
                print_info(f"Primera: {subvenciones[0].get('titulo', 'N/A')[:80]}")
    else:
        results['failed'] += 1
    
    # Test 5: Crear Suscripción (TEST)
    print_header("5. CREAR SUSCRIPCIÓN (PRUEBA)")
    test_data = {
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
        "nombre": "Usuario de Prueba",
        "regiones": None,
        "areas_tematicas": None,
        "presupuesto_min": None,
        "presupuesto_max": None
    }
    print_info(f"Email de prueba: {test_data['email']}")
    success, response = test_endpoint(
        base_url,
        "/api/suscripcion/crear",
        method='POST',
        data=test_data,
        description="Crea una suscripción de prueba"
    )
    results['total'] += 1
    if success:
        results['passed'] += 1
        if response and isinstance(response, dict):
            print_info(f"Suscripción ID: {response.get('id', 'N/A')}")
            print_info(f"Token: {response.get('token', 'N/A')[:30]}...")
            if 'calendar_url' in response:
                print_info(f"URL Calendario: {response.get('calendar_url', 'N/A')}")
    else:
        results['failed'] += 1
    
    # Test 6: Documentación API (Swagger)
    print_header("6. DOCUMENTACIÓN API")
    success, _ = test_endpoint(
        base_url,
        "/docs",
        description="Verifica que la documentación Swagger esté disponible"
    )
    results['total'] += 1
    if success:
        results['passed'] += 1
        print_info(f"Swagger UI disponible en: {base_url}/docs")
    else:
        results['failed'] += 1
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    print(f"Total de pruebas: {results['total']}")
    print_success(f"Exitosas: {results['passed']}")
    if results['failed'] > 0:
        print_error(f"Fallidas: {results['failed']}")
    
    # Porcentaje
    percentage = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    if percentage == 100:
        print_success(f"\nTodas las pruebas pasaron!")
    elif percentage >= 70:
        print(f"\n{YELLOW}Porcentaje de exito: {percentage:.1f}%{RESET}")
    else:
        print_error(f"\nPorcentaje de exito: {percentage:.1f}%")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        print("Uso: python test_api.py <URL_BASE>")
        print("Ejemplo: python test_api.py https://tu-proyecto.up.railway.app")
        print("\nO introduce la URL manualmente:")
        base_url = input("URL base del API: ").strip().rstrip('/')
    
    if not base_url:
        print_error("URL base es requerida")
        sys.exit(1)
    
    try:
        run_tests(base_url)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Pruebas interrumpidas por el usuario{RESET}")
        sys.exit(0)
