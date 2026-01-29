import boto3
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client(
    service_name='bedrock',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

try:
    response = bedrock.list_foundation_models()
    print("Modelos disponibles:")
    for model in response['modelSummaries']:
        if 'TEXT' in model.get('outputModalities', []):
            print(f"- {model['modelId']} ({model['modelName']})")
except Exception as e:
    print(f"Error: {e}")