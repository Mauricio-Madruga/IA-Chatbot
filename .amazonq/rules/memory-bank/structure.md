# Project Structure

## Directory Organization

```
IA-Chatbot/
├── .amazonq/                          # Amazon Q configuration
│   └── rules/
│       └── memory-bank/               # Project documentation
├── app.py                             # Flask backend server
├── query_handler.py                   # Query classification and processing logic
├── config.py                          # Configuration and system prompts
├── index.html                         # Frontend chat interface
├── script.js                          # Client-side chat logic
├── style.css                          # UI styling
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables (not in repo)
├── .env.example                       # Environment template
├── README.md                          # Project documentation
├── TEST_CASES.md                      # Test scenarios
├── CATALOGO_TESTING_EMBEDDINGS.txt    # Sample product catalog
├── PROMPT_UNIVERSAL_OPTIMIZACION.txt  # Prompt optimization notes
├── check_models.py                    # Model availability checker
└── test_chatbot.py                    # Testing utilities
```

## Core Components

### Backend Layer

**app.py** - Flask API Server
- Main application entry point
- Exposes `/chat` endpoint for message processing
- Integrates with AWS Bedrock Knowledge Base
- Handles CORS for frontend communication
- Manages conversation history and context

**query_handler.py** - Query Intelligence Engine
- Classifies queries into 6 types (pricing, comparison, superlative, specs, recommendations, accessories)
- Determines optimal chunk retrieval count per query type
- Generates specialized prompts for each query category
- Implements price validation logic
- Provides smart re-ranking of retrieved chunks

**config.py** - Configuration Management
- System prompts for knowledge base and direct modes
- Model configuration (temperature, max_tokens, top_p)
- Content filters and guardrails
- Fallback responses for edge cases

### Frontend Layer

**index.html** - Chat Interface
- Clean, user-friendly chat UI
- Message display area
- Input field and send button
- Welcome message display

**script.js** - Client Logic
- Handles user input and message sending
- Communicates with Flask backend via fetch API
- Manages message rendering (user/bot)
- Displays typing indicators
- Error handling and user feedback

**style.css** - Visual Design
- Modern chat interface styling
- Responsive layout
- Message bubble design
- Color scheme and typography

### Configuration Files

**.env** - Environment Variables
- AWS credentials (ACCESS_KEY_ID, SECRET_ACCESS_KEY)
- AWS region configuration
- Bedrock model ID (Claude 3 Haiku)
- Knowledge Base ID

**requirements.txt** - Python Dependencies
- flask==3.0.0 (web framework)
- flask-cors==4.0.0 (CORS handling)
- boto3==1.34.0 (AWS SDK)
- python-dotenv==1.0.0 (environment management)

## Architectural Patterns

### Request Flow
1. User sends message via frontend (index.html)
2. script.js sends POST request to `/chat` endpoint
3. app.py receives request and extracts message
4. query_handler.py classifies query type
5. app.py queries Bedrock Knowledge Base with optimized parameters
6. Response validated and formatted
7. JSON response sent back to frontend
8. script.js renders bot message in chat

### Query Processing Pipeline
```
User Query → Classification → Chunk Retrieval → Prompt Generation → 
Bedrock API Call → Price Validation → Response Formatting → User Display
```

### Integration Architecture
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Backend**: Flask REST API
- **AI Service**: AWS Bedrock (Claude 3 Haiku)
- **Knowledge Store**: Bedrock Knowledge Base (S3-backed PDFs)
- **Communication**: HTTP/JSON REST API

## Component Relationships

- **app.py** imports **query_handler.py** for query classification
- **app.py** imports **config.py** for system prompts and settings
- **script.js** communicates with **app.py** via HTTP
- **index.html** loads **script.js** and **style.css**
- All components access **.env** for AWS configuration
