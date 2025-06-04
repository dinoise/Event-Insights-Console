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
        await resetConversation();
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
        
        console.info( "ANSWER ", answer )

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

// Add message to chat UI with Markdown support
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
    
    // Parse Markdown if message is from AI, otherwise display as-is
    if (sender === 'ai') {
        // Sanitize and parse Markdown
        contentDiv.innerHTML = marked.parse(escapeHtml(content));
    } else {
        // For human messages, just escape HTML for security
        contentDiv.textContent = content;
    }
    
    // Build message
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    // Add to chat
    chatMessages.insertBefore(messageDiv, loadingIndicator);
    
    // Scroll to bottom
    scrollToBottom();
}

// Helper function to escape HTML (security)
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
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
        const response = await fetch('/api/llm/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(() => {
            window.location.reload()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (err) {
        console.error("Error resetting conversation:", err);
    } finally {
        showLoading(false);
    }
}
