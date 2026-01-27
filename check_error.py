import requests
import json

url = "https://noti-subvenciones-production.up.railway.app/api/regiones"
print(f"Consultando: {url}\n")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}\n")
    
    if response.headers.get('content-type') == 'application/json':
        data = response.json()
        print("Respuesta JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("Respuesta (texto):")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
