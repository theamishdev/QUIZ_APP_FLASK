document.addEventListener('DOMContentLoaded', () => {
    const chatTrigger = document.getElementById('chatTrigger');
    const chatContainer = document.getElementById('chatContainer');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');

    // Toggle Chat Window
    chatTrigger.addEventListener('click', () => {
        chatContainer.style.display = chatContainer.style.display === 'flex' ? 'none' : 'flex';
        if (chatContainer.style.display === 'flex') {
            chatInput.focus();
        }
    });

    closeChat.addEventListener('click', () => {
        chatContainer.style.display = 'none';
    });

    // Send Message
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to UI
        appendMessage('user', message);
        chatInput.value = '';

        // Typing indicator
        const typingId = appendMessage('bot', 'Thinking...');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            
            // Remove typing indicator and add response
            const typingMsg = document.getElementById(typingId);
            if (typingMsg) typingMsg.remove();
            
            appendMessage('bot', data.reply);
        } catch (error) {
            console.error('Error:', error);
            const typingMsg = document.getElementById(typingId);
            if (typingMsg) typingMsg.remove();
            appendMessage('bot', 'Sorry, something went wrong. Please try again.');
        }
    }

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        const id = 'msg-' + Date.now();
        msgDiv.id = id;
        msgDiv.className = `message ${role}`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
