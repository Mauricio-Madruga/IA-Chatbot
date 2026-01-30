# Development Guidelines

## Code Quality Standards

### Python Code Formatting
- **Indentation**: 4 spaces (PEP 8 compliant)
- **Line Length**: Pragmatic approach, prioritize readability over strict 80-char limit
- **String Quotes**: Double quotes for strings, triple double-quotes for docstrings
- **Imports**: Grouped logically (standard library, third-party, local modules)
- **Naming Conventions**:
  - Variables/functions: `snake_case` (e.g., `bedrock_agent`, `classify_query`)
  - Classes: `PascalCase` (e.g., `QueryHandler`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `SYSTEM_PROMPTS`, `API_URL`)

### JavaScript Code Formatting
- **Indentation**: 4 spaces (consistent with Python)
- **Variable Declaration**: `const` for immutable, `let` for mutable (no `var`)
- **String Quotes**: Single quotes for strings
- **Naming Conventions**:
  - Variables/functions: `camelCase` (e.g., `chatContainer`, `sendMessage`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `API_URL`, `FIXED_MODEL`)
  - DOM elements: Descriptive names ending in element type (e.g., `messageDiv`, `contentDiv`)

### Documentation Standards
- **Python Docstrings**: Triple-quoted strings for classes and complex functions
  ```python
  """Brief description on first line
  
  Detailed explanation if needed
  """
  ```
- **Inline Comments**: Used for complex logic explanation, prefixed with `#`
- **Debug Logging**: Extensive use of `print()` statements with prefixes like `[KB]`, `[QUERY]`, `[DEBUG]`
- **Comment Style**: Descriptive, explains "why" not "what"

## Structural Conventions

### Flask Application Structure
- **Route Handlers**: Defined with `@app.route()` decorator
- **Error Handling**: Try-except blocks with JSON error responses
- **Status Codes**: Explicit HTTP status codes (400 for bad request, 500 for server error)
- **Response Format**: Consistent JSON structure using `jsonify()`

### AWS Boto3 Integration Pattern
```python
# Client initialization with environment variables
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)
```

### Configuration Management
- **Environment Variables**: Loaded via `python-dotenv` at application start
- **Centralized Config**: All prompts and settings in `config.py`
- **Dictionary-Based Config**: Structured as nested dictionaries for easy access
  ```python
  SYSTEM_PROMPTS = {
      "knowledge_base": "...",
      "direct_mode": "..."
  }
  ```

## Semantic Patterns

### Query Classification Pattern (5/5 files)
**Purpose**: Intelligent routing of user queries to optimize retrieval and response generation

**Implementation**:
```python
classification = QueryHandler.classify_query(message)
# Returns: {'type': 'comparison', 'needs_many_results': True, ...}

retrieval_config = QueryHandler.get_retrieval_config(classification)
# Adjusts numberOfResults based on query complexity

prompt = QueryHandler.enhance_prompt(message, classification, context)
# Generates specialized prompt for query type
```

**Key Characteristics**:
- Static methods in `QueryHandler` class
- Keyword-based pattern matching using predefined lists
- Returns structured dictionaries with classification metadata
- Used to optimize both retrieval (chunk count) and generation (prompt engineering)

### Chunk Prioritization Pattern (2/5 files)
**Purpose**: Re-rank retrieved chunks to prioritize those with critical information

**Implementation**:
```python
priority_chunks = []
other_chunks = []

for chunk in chunks:
    content = chunk['content']['text']
    has_price = 'PRECIO' in content
    has_keywords = any(kw in content.lower() for kw in product_keywords)
    
    if has_price and has_keywords:
        priority_chunks.append(chunk)
    else:
        other_chunks.append(chunk)

chunks = priority_chunks + other_chunks
```

**Key Characteristics**:
- Separates chunks into priority and non-priority lists
- Combines keyword matching with critical field detection (e.g., "PRECIO")
- Reorders before context construction to ensure important info appears first

### Price Validation Pattern (2/5 files)
**Purpose**: Prevent AI hallucination by verifying mentioned prices exist in source context

**Implementation**:
```python
import re
price_match = re.search(r'\$?([0-9,]+\.\d{2})\s*USD', reply)
if price_match:
    mentioned_price = price_match.group(1)
    if mentioned_price not in context:
        print(f"[ALERTA] Precio {mentioned_price} NO encontrado en contexto")
        reply = "Lo siento, no puedo confirmar el precio exacto..."
    else:
        print(f"[OK] Precio {mentioned_price} verificado en contexto")
```

**Key Characteristics**:
- Regex extraction of price from AI response
- String matching against original context
- Fallback response if validation fails
- Debug logging for monitoring

### Model-Agnostic Invocation Pattern (3/5 files)
**Purpose**: Support multiple Bedrock models with different API formats

**Implementation**:
```python
if 'nova' in model_id.lower():
    body = json.dumps({
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"max_new_tokens": 1000, "temperature": 0.0}
    })
elif 'claude' in model_id.lower():
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    })

response = bedrock.invoke_model(modelId=invoke_model_id, body=body)
response_body = json.loads(response['body'].read())

# Model-specific response parsing
if 'nova' in model_id.lower():
    reply = response_body['output']['message']['content'][0]['text']
elif 'claude' in model_id.lower():
    reply = response_body['content'][0]['text']
```

**Key Characteristics**:
- Conditional body construction based on model family
- Separate response parsing logic per model
- Supports Nova, Claude, Llama, and Titan models
- ARN conversion for Nova models (inference profiles)

### Async Frontend Communication Pattern (2/5 files)
**Purpose**: Non-blocking UI updates during API calls

**Implementation**:
```javascript
async function sendMessage() {
    isLoading = true;
    sendButton.disabled = true;
    addLoadingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message, model_id, use_knowledge_base})
        });
        
        const data = await response.json();
        removeLoadingIndicator();
        
        if (response.ok) {
            addMessage(data.response, 'assistant');
        } else {
            addMessage(`Error: ${data.error}`, 'assistant');
        }
    } catch (error) {
        removeLoadingIndicator();
        addMessage(`Error de conexión: ${error.message}`, 'assistant');
    } finally {
        isLoading = false;
        sendButton.disabled = false;
    }
}
```

**Key Characteristics**:
- Async/await for clean asynchronous code
- Loading state management (disable button, show indicator)
- Try-catch-finally for comprehensive error handling
- Always cleanup in finally block

### Debug Logging Pattern (4/5 files)
**Purpose**: Comprehensive logging for production debugging without external tools

**Implementation**:
```python
print(f"[KB] Usando retrieve manual + invoke...")
print(f"[QUERY] Tipo: {classification['type']}, Precio: {classification['is_price_query']}")
print(f"[KB] Encontrados {len(chunks)} chunks")
print(f"[ALERTA] Precio {mentioned_price} NO encontrado en contexto")
print(f"[OK] Precio {mentioned_price} verificado en contexto")
```

**Key Characteristics**:
- Prefixed tags for log categorization ([KB], [QUERY], [DEBUG], [ALERTA], [OK])
- F-strings for variable interpolation
- Strategic placement at key decision points
- Used for both debugging and production monitoring

## Internal API Usage

### Bedrock Knowledge Base Retrieve API
```python
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
```

**Best Practices**:
- Always use `retrievalConfiguration` to control chunk count
- Access results via `.get()` with default empty list
- Extract text content: `chunk['content']['text']`
- Access metadata: `chunk.get('location', {}).get('s3Location', {})`

### Bedrock Invoke Model API
```python
response = bedrock.invoke_model(
    modelId=invoke_model_id,
    body=json.dumps(request_body)
)

response_body = json.loads(response['body'].read())
```

**Best Practices**:
- Always JSON-serialize request body
- Read response body stream: `response['body'].read()`
- Parse JSON response immediately
- Handle model-specific response structures

### Flask Request/Response Pattern
```python
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    try:
        # Process request
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Best Practices**:
- Use `request.json` for JSON payloads
- Use `.get()` with defaults for optional fields
- Validate required fields before processing
- Return `jsonify()` for all responses
- Include HTTP status codes for errors

## Frequently Used Code Idioms

### Safe Dictionary Access
```python
# Preferred pattern throughout codebase
value = data.get('key', default_value)
nested = data.get('level1', {}).get('level2', {})
```

### List Comprehension for Filtering
```python
keywords = [word for word in query_lower.split() 
            if len(word) > 3 and word in important_words]

chunks_to_use = [chunk['content']['text'] 
                 for chunk in chunks[:num_chunks_to_use]]
```

### String Formatting with F-Strings
```python
# Consistent use of f-strings for interpolation
print(f"[KB] Encontrados {len(chunks)} chunks")
prompt = f"{base_instructions}\n\nCONTEXT:\n{context}\n\nQUERY: {query}"
```

### Conditional Model Handling
```python
# Pattern repeated for model compatibility
if 'nova' in model_id.lower():
    # Nova-specific logic
elif 'claude' in model_id.lower():
    # Claude-specific logic
else:
    # Fallback or error
```

### Environment Variable Loading
```python
from dotenv import load_dotenv
load_dotenv()  # At module top

# Access with defaults
region = os.getenv('AWS_REGION', 'us-east-1')
model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
```

## Popular Annotations

### Flask Route Decorators
```python
@app.route('/chat', methods=['POST'])
@app.route('/models', methods=['GET'])
@app.route('/kb-status', methods=['GET'])
```

### Static Methods (QueryHandler)
```python
@staticmethod
def classify_query(query: str) -> Dict:
    """Docstring"""
    pass
```

## Error Handling Practices

### Backend Error Handling
- Wrap all route handlers in try-except blocks
- Return JSON error responses with descriptive messages
- Include appropriate HTTP status codes (400, 500)
- Log errors to console with `print()`

### Frontend Error Handling
- Try-catch around all fetch calls
- Display user-friendly error messages in chat
- Always remove loading indicators in finally block
- Maintain UI state consistency (re-enable buttons)

## Testing Practices

### Manual Testing Script Pattern
```python
# test_chatbot.py structure
preguntas = ["pregunta 1", "pregunta 2", "pregunta 3"]

for i, pregunta in enumerate(preguntas, 1):
    print(f"\n{i}. PREGUNTA: {pregunta}")
    response = requests.post(API_URL, json={"message": pregunta})
    print(f"RESPUESTA: {response.json()['response']}")
```

**Characteristics**:
- Simple sequential test execution
- Console output with visual separators
- Direct API calls using requests library
- No formal test framework (pytest, unittest)

## Cost Optimization Patterns

### Token Limiting
```python
MODEL_CONFIG = {
    "temperature": 0.0,
    "max_tokens": 500,  # Reduced for cost control
    "top_p": 0.9
}
```

### Chunk Count Optimization
```python
# Adjust retrieval based on query complexity
if classification['needs_many_results']:
    config['numberOfResults'] = 30  # Reduced from 50
elif classification['is_price_query']:
    config['numberOfResults'] = 15  # Reduced from 20
else:
    config['numberOfResults'] = 10  # Default
```

### Context Truncation
```python
# Limit chunks used in context construction
num_chunks_to_use = min(len(chunks), 10 if needs_many else 8)
context = "\n\n".join([chunk['content']['text'] 
                       for chunk in chunks[:num_chunks_to_use]])
```

## Security Practices

### Environment Variable Protection
- Never commit `.env` file (in `.gitignore`)
- Provide `.env.example` template without real credentials
- Load credentials at runtime via `python-dotenv`

### Input Validation
```python
if not message:
    return jsonify({'error': 'Mensaje vacío'}), 400
```

### CORS Configuration
```python
from flask_cors import CORS
CORS(app)  # Enable for frontend communication
```

## UI/UX Patterns

### Message Formatting
```javascript
// Convert markdown-like syntax to HTML
const formattedContent = content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/(\d+\.)\s/g, '<br>$1 ')
    .replace(/^\s*-\s/gm, '<br>• ');
```

### Auto-Scrolling Chat
```javascript
chatContainer.scrollTop = chatContainer.scrollHeight;
```

### Dynamic Textarea Sizing
```javascript
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});
```

### Loading Indicators
```javascript
function addLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message-content loading';
    loadingDiv.innerHTML = '<span></span><span></span><span></span>';
    // Animated dots via CSS
}
```
