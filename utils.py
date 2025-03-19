from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

WSP_TOKEN = os.getenv('WSP_TOKEN')
#WSP_TOKEN= "EAATxpGTTXIkBO9ySTskR48rWCbr3sRUWH57FmeZCBFqM8diuHzXlJukmUUy15ZBc5L1ZCDVnUiDHgbsWifc2FxDWRSGIrAyp1gGJKiSiZBMG3gZA7MakZCxPfu2161NJMYZA4TsySgoQbMT2CRWZBoZCGrB5wyHHppYDdsvvZCZA3weZAZAaXVqZCVV1GzwKKoPeQTvaZB6F8QdLFFqZAGgSwU0WkaDs5WRmkqYZD"
WSP_BUSINESS_ID = os.getenv('WSP_BUSINESS_ID')
WSP_PHONE_ID = os.getenv('WSP_PHONE_ID')
WSP_API_URL = os.getenv('WSP_API_URL')

HEADERS = {
    "Authorization": f"Bearer {WSP_TOKEN}",
    "Content-Type": "application/json"
}

def obtener_plantillas():
    url = f"{WSP_API_URL}{WSP_BUSINESS_ID}/message_templates"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Error al obtener plantillas: {response.json()}")
        return []
def seleccionar_plantilla(usuario, plantillas):
    return next((p for p in plantillas if p['name'] == usuario.plantilla_wsp), None)

def enviar_mensaje(proveedor,usuario, detalles_pedido):
    plantillas = obtener_plantillas()
    plantilla = seleccionar_plantilla(usuario, plantillas)
    
    if not plantilla:
        print("Plantilla no encontrada para el usuario.")
        return
    
    mensaje = {
        "messaging_product": "whatsapp",
        "to": proveedor.whatsapp,
        "type": "template",
        "template": {
            "name": plantilla['name'],
            "language": {"code": "es_ES"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": detalles_pedido}]
                }
            ]
        }
    }
    
    url = f"{WSP_API_URL}{WSP_PHONE_ID}/messages"
    response = requests.post(url, headers=HEADERS, json=mensaje)
    
    if response.status_code == 200:
        print("Mensaje enviado con éxito.")
    else:
        print(f"Error al enviar mensaje: {response.json()}")
