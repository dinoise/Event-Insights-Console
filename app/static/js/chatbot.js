// Selectores actualizados para nuestro diseño
const sendButton = document.getElementById('sendButton');
const messageInput = document.getElementById('messageInput');
const resetButton = document.getElementById('resetButton');
const chatMessages = document.getElementById('chatMessages');
const loadingIndicator = document.getElementById('loadingIndicator');

// Submit chat message via click
sendButton.addEventListener('click', async (e) => {
    if (messageInput.value.trim() !== '') {
        await submitMessage();
    }
});

// Submit chat message via enter
messageInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && messageInput.value.trim() !== '') {
        await submitMessage();
    }
});

// Reset conversation
resetButton.addEventListener('click', async (e) => {
    if (confirm('¿Estás seguro de que quieres reiniciar la conversación?')) {
        // TODO
        console.log("RESET")
        // await resetConversation();
    }
});

async function submitMessage() {
    const msg = messageInput.value.trim();
    
    // Add message to UI
    addMessageToUI("human", msg);
    
    // Clear input
    messageInput.value = '';
    
    // Show loading indicator
    showLoading(true);
    
    try {
        // Prompt LLM
        const answer = await askQuestion(msg);
         
        // Add response to UI
        addMessageToUI(answer.type, answer.content);
    } catch (err) {
        console.error("Error submitting question:", err);
        addMessageToUI("ai", "Lo siento, hubo un error al procesar tu solicitud. Por favor intenta nuevamente.");
    } finally {
        // Hide loading indicator
        showLoading(false);
    }
}

// Add message to chat UI
function addMessageToUI(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    // Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = `avatar ${sender}-avatar`;
    
    const icon = document.createElement('span');
    icon.className = 'material-icons-round';
    icon.textContent = sender === 'ai' ? 'smart_toy' : 'person';
    avatarDiv.appendChild(icon);
    
    // Message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;
    
    // Build message
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    // Add to chat
    chatMessages.insertBefore(messageDiv, loadingIndicator);
    
    // Scroll to bottom
    scrollToBottom();
}

// Show/hide loading indicator
function showLoading(show) {
    loadingIndicator.style.display = show ? 'flex' : 'none';
    if (show) {
        scrollToBottom();
    }
}

// Scroll chat to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send request to backend
async function askQuestion(prompt) {
    const response = await fetch('/api/llm/call', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ prompt }),
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Reset conversation
async function resetConversation() {
    showLoading(true);
    try {
        const response = await fetch('/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Clear chat UI (keeping the first message if you want)
            while (chatMessages.firstChild) {
                chatMessages.removeChild(chatMessages.firstChild);
            }
            // Add initial bot message
            addMessageToUI('ai', '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?');
        }
    } catch (err) {
        console.error("Error resetting conversation:", err);
    } finally {
        showLoading(false);
    }
}

// Initialize chat with welcome message if empty
if (chatMessages.children.length <= 1) { // Only loading indicator exists
    addMessageToUI('ai', '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?');
}