from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import os
from dotenv import load_dotenv

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
            print("[KB] Consultando Knowledge Base...")
            kb_id = os.getenv('KNOWLEDGE_BASE_ID')
            if not kb_id:
                return jsonify({'error': 'KNOWLEDGE_BASE_ID no configurado'}), 400
            
            # Recuperar documentos manualmente
            retrieve_response = bedrock_agent.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': message}
            )
            
            # Construir contexto desde los documentos recuperados
            context = ""
            sources = []
            results = retrieve_response.get('retrievalResults', [])
            
            print(f"[KB] Documentos recuperados: {len(results)}")
            
            for idx, result in enumerate(results[:3]):
                content_text = result.get('content', {}).get('text', '')
                score = result.get('score', 0)
                print(f"[KB] Documento {idx+1} - Score: {score:.3f} - Longitud: {len(content_text)} chars")
                print(f"[KB] Preview: {content_text[:200]}...")
                
                context += content_text + "\n\n"
                if 'location' in result and 's3Location' in result['location']:
                    sources.append({'uri': result['location']['s3Location']['uri']})
            
            if not context.strip():
                print("[KB] ADVERTENCIA: No se recuperó contexto de la KB")
                return jsonify({
                    'response': 'La base de conocimiento está vacía. Ve a AWS Console > Bedrock > Knowledge bases > tu_KB_ID > Data sources > Sync para cargar documentos.',
                    'sources': [],
                    'kb_empty': True
                })
            
            # Invocar Nova directamente con el contexto
            prompt = f"Usa SOLO la siguiente información para responder. NO uses conocimiento general.\n\nInformación disponible:\n{context}\n\nPregunta: {message}\n\nRespuesta basada SOLO en la información anterior:"
            
            body = json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7
                }
            })
            
            response = bedrock.invoke_model(
                modelId=invoke_model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            reply = response_body['output']['message']['content'][0]['text']
            
            print(f"[KB] Fuentes encontradas: {len(sources)}")
            return jsonify({'response': reply, 'sources': sources})
        
        else:
            print("[DIRECTO] Sin Knowledge Base")
            print(f"Usando modelo: {invoke_model_id}")
            
            if 'claude' in model_id.lower():
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": message}]
                })
            elif 'nova' in model_id.lower():
                body = json.dumps({
                    "messages": [{"role": "user", "content": [{"text": message}]}],
                    "inferenceConfig": {
                        "max_new_tokens": 1000,
                        "temperature": 0.7
                    }
                })
            elif 'llama' in model_id.lower() or 'meta' in model_id.lower():
                body = json.dumps({
                    "prompt": message,
                    "max_gen_len": 1000,
                    "temperature": 0.7
                })
            elif 'titan' in model_id.lower():
                body = json.dumps({
                    "inputText": message,
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
    """Endpoint para probar la conexión con Knowledge Base"""
    try:
        kb_id = os.getenv('KNOWLEDGE_BASE_ID')
        if not kb_id:
            return jsonify({'error': 'KNOWLEDGE_BASE_ID no configurado'}), 400
        
        # Obtener info de la KB usando bedrock client
        bedrock_client = boto3.client(
            service_name='bedrock-agent',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        
        try:
            kb_info = bedrock_client.get_knowledge_base(knowledgeBaseId=kb_id)
            print(f"[TEST-KB] KB Status: {kb_info['knowledgeBase']['status']}")
        except Exception as e:
            print(f"[TEST-KB] No se pudo obtener info de KB: {e}")
        
        # Intentar recuperar con una consulta simple
        test_query = "celular"
        print(f"[TEST-KB] Probando con query: '{test_query}'")
        
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': test_query}
        )
        
        results = response.get('retrievalResults', [])
        print(f"[TEST-KB] Resultados: {len(results)}")
        
        result_info = []
        for idx, result in enumerate(results[:5]):
            info = {
                'index': idx + 1,
                'score': result.get('score', 0),
                'content_length': len(result.get('content', {}).get('text', '')),
                'preview': result.get('content', {}).get('text', '')[:300]
            }
            result_info.append(info)
            print(f"[TEST-KB] Resultado {idx+1}: Score={info['score']:.3f}, Length={info['content_length']}")
        
        message = "KB vacía. Pasos: 1) Ve a AWS Console > Bedrock > Knowledge bases > CSQSSS8KH0, 2) Click en Data sources, 3) Click en Sync, 4) Espera 5-15 min" if len(results) == 0 else "KB funcionando correctamente"
        
        return jsonify({
            'kb_id': kb_id,
            'query': test_query,
            'total_results': len(results),
            'results': result_info,
            'message': message
        })
        
    except Exception as e:
        print(f"[TEST-KB] Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
