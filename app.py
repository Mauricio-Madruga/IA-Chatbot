from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import os
from dotenv import load_dotenv
from config import SYSTEM_PROMPTS, MODEL_CONFIG, FALLBACK_RESPONSES
from query_handler import QueryHandler

load_dotenv()

app = Flask(__name__)
CORS(app)

bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

bedrock_agent = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
    use_kb = data.get('use_knowledge_base', False)
    
    if not message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    try:
        # Convertir modelo Nova a ARN de inference profile
        invoke_model_id = model_id
        if 'nova' in model_id.lower() and not model_id.startswith('arn:'):
            region = os.getenv('AWS_REGION', 'us-east-1')
            invoke_model_id = f'arn:aws:bedrock:{region}::foundation-model/{model_id}'
        
        if use_kb:
            print("[KB] Usando retrieve manual + invoke...")
            kb_id = os.getenv('KNOWLEDGE_BASE_ID')
            if not kb_id:
                return jsonify({'error': 'KNOWLEDGE_BASE_ID no configurado'}), 400
            
            # CLASIFICAR consulta para optimizar recuperación
            classification = QueryHandler.classify_query(message)
            print(f"[QUERY] Tipo: {classification['type']}, Precio: {classification['is_price_query']}, Keywords: {classification['keywords']}")
            
            # Obtener configuración de recuperación optimizada
            retrieval_config = QueryHandler.get_retrieval_config(classification)
            print(f"[QUERY] Recuperando {retrieval_config['numberOfResults']} chunks")
            
            # 1. RETRIEVE: Buscar documentos relevantes con configuración optimizada
            retrieve_response = bedrock_agent.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': message},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': retrieval_config['numberOfResults']
                    }
                }
            )
            
            chunks = retrieve_response.get('retrievalResults', [])
            print(f"[KB] Encontrados {len(chunks)} chunks")
            
            # PRIORIZAR chunks con producto exacto + precio
            product_keywords = message.lower().split()
            priority_chunks = []
            other_chunks = []
            
            for chunk in chunks:
                content = chunk['content']['text']
                # Si tiene PRECIO y menciona palabras clave de la pregunta
                has_price = 'PRECIO' in content
                has_keywords = any(kw in content.lower() for kw in product_keywords if len(kw) > 3)
                
                if has_price and has_keywords:
                    priority_chunks.append(chunk)
                else:
                    other_chunks.append(chunk)
            
            # Reordenar: primero chunks con precio relevante
            chunks = priority_chunks + other_chunks
            print(f"[KB] Chunks priorizados con precio: {len(priority_chunks)}")
            
            # DEBUG: Mostrar qué chunks se recuperaron
            print("\n[DEBUG] Buscando 'PRECIO' en chunks...")
            for i, chunk in enumerate(chunks[:10]):
                content = chunk['content']['text']
                if 'PRECIO' in content and 'iPhone 14 Pro' in content:
                    print(f"[CHUNK {i+1}] ¡Encontrado iPhone 14 Pro con PRECIO! Score: {chunk.get('score', 0):.3f}")
                    print(content[:500])
                    print("="*80)
            
            if not chunks:
                return jsonify({'response': 'No encontré información sobre ese producto.', 'sources': []})
            
            # 2. Construir contexto con chunks priorizados (limitado para controlar costos)
            num_chunks_to_use = min(len(chunks), 10 if classification['needs_many_results'] else 8)
            context = "\n\n".join([f"Documento {i+1}:\n{chunk['content']['text']}" 
                                    for i, chunk in enumerate(chunks[:num_chunks_to_use])])
            
            print(f"[KB] Contexto construido: {len(context)} caracteres, {num_chunks_to_use} chunks")
            
            # 3. INVOKE: Generar respuesta con prompt optimizado según tipo de consulta
            prompt = QueryHandler.enhance_prompt(message, classification, context)
            
            body = None
            if 'nova' in model_id.lower():
                body = json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 1000, "temperature": 0.0}
                })
            elif 'claude' in model_id.lower():
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0.0,
                    "messages": [{"role": "user", "content": prompt}]
                })
            else:
                return jsonify({'error': f'Modelo {model_id} no soportado para KB'}), 400
            
            response = bedrock.invoke_model(modelId=invoke_model_id, body=body)
            response_body = json.loads(response['body'].read())
            
            if 'nova' in model_id.lower():
                reply = response_body['output']['message']['content'][0]['text']
            elif 'claude' in model_id.lower():
                reply = response_body['content'][0]['text']
            else:
                reply = "Error: modelo no reconocido"
            
            # VALIDACIÓN: Verificar que el precio mencionado existe en el contexto
            import re
            price_match = re.search(r'\$?([0-9,]+\.\d{2})\s*USD', reply)
            if price_match:
                mentioned_price = price_match.group(1)
                if mentioned_price not in context:
                    print(f"[ALERTA] Precio {mentioned_price} NO encontrado en contexto - posible alucinación")
                    reply = "Lo siento, no puedo confirmar el precio exacto de ese producto. ¿Podrías especificar el modelo completo?"
                else:
                    print(f"[OK] Precio {mentioned_price} verificado en contexto")
            
            sources = [{'uri': chunk.get('location', {}).get('s3Location', {}).get('uri', 'unknown')} 
                      for chunk in chunks[:3]]
            
            print(f"[KB] Respuesta generada, {len(sources)} fuentes")
            return jsonify({'response': reply, 'sources': sources})
        
        else:
            print("[DIRECTO] Sin Knowledge Base")
            print(f"Usando modelo: {invoke_model_id}")
            
            # System prompt para modo directo
            user_message = f"{SYSTEM_PROMPTS['direct_mode']}\n\nPregunta del cliente: {message}"
            
            if 'claude' in model_id.lower():
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": user_message}]
                })
            elif 'nova' in model_id.lower():
                body = json.dumps({
                    "messages": [{"role": "user", "content": [{"text": user_message}]}],
                    "inferenceConfig": {
                        "max_new_tokens": MODEL_CONFIG["max_tokens"],
                        "temperature": MODEL_CONFIG["temperature"]
                    }
                })
            elif 'llama' in model_id.lower() or 'meta' in model_id.lower():
                body = json.dumps({
                    "prompt": user_message,
                    "max_gen_len": 1000,
                    "temperature": 0.7
                })
            elif 'titan' in model_id.lower():
                body = json.dumps({
                    "inputText": user_message,
                    "textGenerationConfig": {
                        "maxTokenCount": 1000,
                        "temperature": 0.7
                    }
                })
            else:
                print(f"Modelo no reconocido: {model_id}")
                return jsonify({'error': f'Modelo no soportado: {model_id}'}), 400
            
            response = bedrock.invoke_model(
                modelId=invoke_model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'claude' in model_id.lower():
                reply = response_body['content'][0]['text']
            elif 'nova' in model_id.lower():
                reply = response_body['output']['message']['content'][0]['text']
            elif 'llama' in model_id.lower() or 'meta' in model_id.lower():
                reply = response_body['generation']
            elif 'titan' in model_id.lower():
                reply = response_body['results'][0]['outputText']
            
            return jsonify({'response': reply})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    models = [
        {'id': 'anthropic.claude-3-sonnet-20240229-v1:0', 'name': 'Claude 3 Sonnet'},
        {'id': 'anthropic.claude-3-haiku-20240307-v1:0', 'name': 'Claude 3 Haiku'},
        {'id': 'amazon.titan-text-express-v1', 'name': 'Titan Text Express'}
    ]
    return jsonify(models)

@app.route('/kb-status', methods=['GET'])
def kb_status():
    """Diagnóstico rápido de Knowledge Base"""
    try:
        kb_id = os.getenv('KNOWLEDGE_BASE_ID')
        if not kb_id:
            return jsonify({'error': 'KNOWLEDGE_BASE_ID no configurado'})
        
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': 'test'}
        )
        
        results = response.get('retrievalResults', [])
        return jsonify({
            'kb_id': kb_id,
            'documents_found': len(results),
            'status': 'ready' if len(results) > 0 else 'empty',
            'message': 'KB lista para usar' if len(results) > 0 else 'KB vacía - necesita sincronizar documentos'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'})

@app.route('/test-kb', methods=['GET'])
def test_kb():
    """Diagnóstico detallado de qué puede encontrar la KB"""
    try:
        kb_id = os.getenv('KNOWLEDGE_BASE_ID')
        if not kb_id:
            return jsonify({'error': 'KNOWLEDGE_BASE_ID no configurado'}), 400
        
        # Probar varias búsquedas
        test_queries = [
            'iPhone 14 Pro',
            'iPhone 14',
            'iPhone',
            'producto',
            'precio'
        ]
        
        results = {}
        for query in test_queries:
            response = bedrock_agent.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5
                    }
                }
            )
            
            chunks = response.get('retrievalResults', [])
            results[query] = {
                'found': len(chunks),
                'previews': [chunk['content']['text'][:150] + '...' for chunk in chunks[:3]]
            }
        
        return jsonify({
            'kb_id': kb_id,
            'test_results': results,
            'recommendation': 'Si todos muestran 0 resultados, necesitas SINCRONIZAR la KB en AWS Console'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
