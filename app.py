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
    model_id = data.get('model_id', os.getenv('BEDROCK_MODEL_ID'))
    use_kb = data.get('use_knowledge_base', False)
    
    if not message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    try:
        if use_kb:
            kb_id = os.getenv('KNOWLEDGE_BASE_ID')
            if not kb_id:
                return jsonify({'error': 'KNOWLEDGE_BASE_ID no configurado'}), 400
            
            response = bedrock_agent.retrieve_and_generate(
                input={'text': message},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': kb_id,
                        'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_REGION")}::foundation-model/{model_id}'
                    }
                }
            )
            reply = response['output']['text']
            sources = [{'uri': ref['location']['s3Location']['uri']} 
                      for ref in response.get('citations', [{}])[0].get('retrievedReferences', [])]
            return jsonify({'response': reply, 'sources': sources})
        
        else:
            if 'claude' in model_id:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": message}]
                })
            elif 'titan' in model_id:
                body = json.dumps({
                    "inputText": message,
                    "textGenerationConfig": {
                        "maxTokenCount": 1000,
                        "temperature": 0.7
                    }
                })
            else:
                return jsonify({'error': 'Modelo no soportado'}), 400
            
            response = bedrock.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'claude' in model_id:
                reply = response_body['content'][0]['text']
            elif 'titan' in model_id:
                reply = response_body['results'][0]['outputText']
            
            return jsonify({'response': reply})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    models = [
        {'id': 'anthropic.claude-3-sonnet-20240229-v1:0', 'name': 'Claude 3 Sonnet'},
        {'id': 'anthropic.claude-3-haiku-20240307-v1:0', 'name': 'Claude 3 Haiku'},
        {'id': 'amazon.titan-text-express-v1', 'name': 'Titan Text Express'}
    ]
    return jsonify(models)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
