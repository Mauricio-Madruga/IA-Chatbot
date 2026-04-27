import boto3, json, os, threading
from dotenv import load_dotenv
load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=region,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN")
)

nova_body = json.dumps({
    "messages": [{"role": "user", "content": [{"text": "Di hola"}]}],
    "inferenceConfig": {"max_new_tokens": 10}
})

ids_to_test = [
    "amazon.nova-micro-v1:0",
    "amazon.nova-lite-v1:0",
    "us.amazon.nova-micro-v1:0",
    "us.amazon.nova-lite-v1:0",
]

for mid in ids_to_test:
    print(f"\n{mid}...", flush=True)
    result = {"done": False}
    
    def invoke(m):
        try:
            r = bedrock.invoke_model(modelId=m, body=nova_body)
            data = json.loads(r["body"].read())
            print(f"  FUNCIONA: {data['output']['message']['content'][0]['text']}", flush=True)
        except Exception as e:
            print(f"  ERROR: {str(e)[:150]}", flush=True)
        result["done"] = True
    
    t = threading.Thread(target=invoke, args=(mid,))
    t.start()
    t.join(timeout=10)
    if not result["done"]:
        print(f"  TIMEOUT", flush=True)

print("\n--- Fin ---", flush=True)
