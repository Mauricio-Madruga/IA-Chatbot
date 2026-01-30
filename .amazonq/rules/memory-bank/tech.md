# Technology Stack

## Programming Languages

### Python 3.x
- **Backend Framework**: Flask 3.0.0
- **AWS Integration**: boto3 1.34.0
- **Environment Management**: python-dotenv 1.0.0
- **CORS Handling**: flask-cors 4.0.0

### JavaScript (ES6+)
- **Frontend Logic**: Vanilla JavaScript
- **API Communication**: Fetch API
- **DOM Manipulation**: Native JavaScript

### HTML5 & CSS3
- **Markup**: Semantic HTML5
- **Styling**: Modern CSS3 with flexbox

## Core Dependencies

### Python Packages (requirements.txt)
```
flask==3.0.0           # Web framework for REST API
flask-cors==4.0.0      # Cross-Origin Resource Sharing
boto3==1.34.0          # AWS SDK for Python
python-dotenv==1.0.0   # Environment variable management
```

### AWS Services
- **Amazon Bedrock**: AI model hosting (Claude 3 Haiku)
- **Bedrock Knowledge Base**: Document retrieval from S3
- **S3**: PDF storage for product catalogs
- **IAM**: Access control and permissions

## AI/ML Stack

### Model Configuration
- **Model**: anthropic.claude-3-haiku-20240307-v1:0
- **Temperature**: 0.0 (factual, no creativity)
- **Max Tokens**: 500 (cost-optimized responses)
- **Top P**: 0.9

### Knowledge Base
- **Type**: Amazon Bedrock Knowledge Base
- **Storage**: S3-backed PDF documents
- **Embedding Model**: Amazon Titan or Nova Lite
- **Retrieval**: Semantic search with configurable chunk count

## Development Commands

### Initial Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your AWS credentials and Knowledge Base ID
```

### Running the Application

**Backend Server**
```bash
# Start Flask server (default port 5000)
python app.py

# Server runs at http://localhost:5000
```

**Frontend Server**
```bash
# Option 1: Simple HTTP server
python -m http.server 8000

# Option 2: Open index.html directly in browser
# Navigate to http://localhost:8000
```

### Testing
```bash
# Run chatbot tests
python test_chatbot.py

# Check available Bedrock models
python check_models.py
```

### Environment Variables Required
```bash
AWS_ACCESS_KEY_ID=<your_access_key>
AWS_SECRET_ACCESS_KEY=<your_secret_key>
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
KNOWLEDGE_BASE_ID=<your_kb_id>
```

## Build System

### No Build Process Required
- **Backend**: Direct Python execution (no compilation)
- **Frontend**: Static files (no bundling/transpilation)
- **Deployment**: Simple file copy to server

### Development Workflow
1. Edit Python files (app.py, query_handler.py, config.py)
2. Restart Flask server to apply changes
3. Edit frontend files (HTML/CSS/JS)
4. Refresh browser to see changes (no build step)

## API Endpoints

### POST /chat
**Request Body**:
```json
{
  "message": "user query text",
  "history": []
}
```

**Response**:
```json
{
  "response": "bot response text"
}
```

## Configuration Files

### .env (Environment)
- AWS credentials and region
- Bedrock model identifier
- Knowledge Base ID

### config.py (Application)
- System prompts for different modes
- Model parameters (temperature, tokens)
- Content filters and guardrails
- Fallback responses

## Version Requirements
- **Python**: 3.8+ (for boto3 and Flask compatibility)
- **Browser**: Modern browser with ES6 support
- **AWS SDK**: boto3 1.34.0+
- **Flask**: 3.0.0+

## External Services
- **AWS Account**: Required with Bedrock access
- **IAM Permissions**: Bedrock invoke and Knowledge Base query
- **S3 Bucket**: For Knowledge Base document storage
