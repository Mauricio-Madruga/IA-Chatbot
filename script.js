const API_URL = 'http://localhost:5000';
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

const FIXED_MODEL = 'anthropic.claude-3-haiku-20240307-v1:0';
const USE_KB = false; // Cambiar a true cuando tengas el Knowledge Base ID

let isLoading = false;

function showWelcomeMessage() {
    addMessage('¡Hola! Soy tu asistente virtual. Puedo ayudarte a comparar especificaciones y precios de productos. ¿Qué te gustaría saber?', 'assistant');
}

function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addLoadingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'loading-indicator';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message-content loading';
    loadingDiv.innerHTML = '<span></span><span></span><span></span>';
    
    messageDiv.appendChild(loadingDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;
    
    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    isLoading = true;
    sendButton.disabled = true;
    addLoadingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                model_id: FIXED_MODEL,
                use_knowledge_base: USE_KB
            })
        });
        
        const data = await response.json();
        
        removeLoadingIndicator();
        
        if (response.ok) {
            let responseText = data.response;
            if (data.sources && data.sources.length > 0) {
                responseText += '\n\n📚 Fuentes:\n' + data.sources.map(s => s.uri).join('\n');
            }
            addMessage(responseText, 'assistant');
        } else {
            addMessage(`Error: ${data.error}`, 'assistant');
        }
    } catch (error) {
        removeLoadingIndicator();
        addMessage(`Error de conexión: ${error.message}`, 'assistant');
    } finally {
        isLoading = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

sendButton.addEventListener('click', sendMessage);

showWelcomeMessage();
