const API_URL = 'http://localhost:5000';
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

const FIXED_MODEL = 'amazon.nova-lite-v1:0';
const USE_KB = true; // Knowledge Base activado

let isLoading = false;

function showWelcomeMessage() {
    addMessage('¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte?', 'assistant');
}

function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Convertir texto a HTML con formato
    const formattedContent = content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/(\d+\.)\s/g, '<br>$1 ')
        .replace(/^\s*-\s/gm, '<br>• ');
    
    contentDiv.innerHTML = formattedContent;
    
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

// Botón para verificar estado de KB
document.getElementById('kbStatus').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/kb-status`);
        const data = await response.json();
        const status = data.status === 'ready' ? '✅ Lista' : '⚠️ Vacía';
        addMessage(`KB Status: ${status} (${data.documents_found} documentos)\n${data.message}`, 'assistant');
    } catch (error) {
        addMessage(`Error verificando KB: ${error.message}`, 'assistant');
    }
});

showWelcomeMessage();
