import requests
import json

# Configuración
API_URL = "http://localhost:5000/chat"

# Preguntas de prueba
preguntas = [
    "¿Cuánto cuesta el iPhone 14 Pro?",
    "¿Cuál es el celular más barato?",
    "¿Qué características tiene el Samsung S24 Ultra?"
]

print("=" * 60)
print("PRUEBA DE CHATBOT CON RETRIEVE_AND_GENERATE")
print("=" * 60)

for i, pregunta in enumerate(preguntas, 1):
    print(f"\n{i}. PREGUNTA: {pregunta}")
    print("-" * 60)
    
    try:
        response = requests.post(
            API_URL,
            json={
                "message": pregunta,
                "use_knowledge_base": True
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"RESPUESTA: {data['response']}")
            if data.get('sources'):
                print(f"FUENTES: {len(data['sources'])} documentos")
        else:
            print(f"ERROR {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("=" * 60)

print("\n✅ Prueba completada")
