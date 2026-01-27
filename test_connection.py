#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar la conexión a la base de datos
"""

import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_connection(base_url):
    """Prueba la conexión de la API"""
    
    print("\n" + "="*60)
    print("PRUEBA DE CONEXIÓN A LA BASE DE DATOS")
    print("="*60 + "\n")
    
    # Test 1: Health Check
    print("1. Probando Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] Servidor respondiendo")
        else:
            print("   [ERROR] Servidor no responde correctamente")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 2: Endpoint que requiere DB
    print("\n2. Probando conexión a PostgreSQL...")
    try:
        response = requests.get(f"{base_url}/api/regiones", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Base de datos conectada!")
            print(f"   Regiones encontradas: {len(data)}")
            return True
        elif response.status_code == 500:
            error = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
            if 'localhost' in str(error):
                print("   [ERROR] Aún intenta conectar a localhost")
                print("   -> Configura DATABASE_URL en Railway")
                print("   -> Haz Redeploy después de configurar")
            elif 'relation' in str(error).lower() or 'table' in str(error).lower():
                print("   [OK] Base de datos conectada!")
                print("   [INFO] Pero faltan las tablas - ejecuta init_db.py")
                return True
            else:
                print(f"   [ERROR] {error}")
            return False
        else:
            print(f"   [ERROR] Código inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = input("URL base del API: ").strip().rstrip('/')
    
    if test_connection(base_url):
        print("\n" + "="*60)
        print("SIGUIENTE PASO: Inicializar la base de datos")
        print("="*60)
        print("\nEjecuta en Railway CLI:")
        print("  railway run python backend/scripts/init_db.py")
        print("  railway run python backend/scripts/populate_catalogs.py")
    else:
        print("\n" + "="*60)
        print("ACCIÓN REQUERIDA")
        print("="*60)
        print("\n1. Configura DATABASE_URL en Railway")
        print("2. Redeploy el servicio")
        print("3. Vuelve a ejecutar este script")
