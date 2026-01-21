"""
Script para configurar credenciales desde variable de entorno
Útil para Railway y otros servicios cloud
"""
import os
import json
from pathlib import Path

def setup_credentials():
    """Crear archivo de credenciales desde variable de entorno"""
    
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    if not credentials_json:
        print("⚠️  GOOGLE_CREDENTIALS_JSON no encontrado en variables de entorno")
        print("ℹ️  Si el archivo credentials/service-account.json existe, se usará ese")
        return
    
    try:
        # Verificar que es JSON válido
        json.loads(credentials_json)
        
        # Crear directorio si no existe
        credentials_dir = Path(__file__).parent.parent.parent / 'credentials'
        credentials_dir.mkdir(exist_ok=True)
        
        # Escribir archivo
        credentials_file = credentials_dir / 'service-account.json'
        with open(credentials_file, 'w') as f:
            f.write(credentials_json)
        
        # Permisos restrictivos (no funciona en Windows)
        try:
            os.chmod(credentials_file, 0o600)
        except:
            pass
        
        print(f"✓ Credenciales configuradas en {credentials_file}")
        
    except json.JSONDecodeError:
        print("❌ Error: GOOGLE_CREDENTIALS_JSON no es un JSON válido")
    except Exception as e:
        print(f"❌ Error al configurar credenciales: {e}")

if __name__ == "__main__":
    setup_credentials()
