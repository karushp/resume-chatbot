// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById("userInput");
    const chat = document.getElementById("chat");
    const sendButton = document.querySelector(".send-btn");
    
    // Get the user's message
    const userMessage = input.value.trim();
    if (!userMessage) return;
    
    // Clear input and disable button
    input.value = "";
    sendButton.disabled = true;
        sendButton.innerHTML = '<span class="send-icon">⋯</span>';
    
    // Add user message to chat
    chat.innerHTML += `
        <div class="chat-message user">
            <div class="user-avatar">U</div>
            <div class="message-bubble user">${userMessage}</div>
        </div>
    `;
    
    // Add loading indicator
    const loadingId = "loading-" + Date.now();
    chat.innerHTML += `
        <div id="${loadingId}" class="loading-container">
            <img src="frontend/photo.jpeg" alt="Bot" class="loading-avatar">
            <div class="loading-bubble">
                <div class="loading-spinner"></div>
                <span class="loading-text">🤖 Bot is thinking...</span>
            </div>
        </div>
    `;
    
    // Scroll to bottom
    chat.scrollTop = chat.scrollHeight;
    
    try {
        const response = await fetch("https://resume-chatbot-162o.onrender.com/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: userMessage })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add bot response
        chat.innerHTML += `
            <div class="chat-message bot">
                <img src="frontend/photo.jpeg" alt="Bot" class="message-avatar">
                <div class="message-bubble bot">${data.answer}</div>
            </div>
        `;
        
    } catch (error) {
        // Remove loading indicator
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Add error message
        chat.innerHTML += `
            <div class="chat-message bot">
                <img src="frontend/photo.jpeg" alt="Bot" class="message-avatar">
                <div class="message-bubble bot">❌ Sorry, I encountered an error: ${error.message}</div>
            </div>
        `;
    }
    
    // Re-enable button and scroll to bottom
        sendButton.disabled = false;
        sendButton.innerHTML = '<span class="send-icon">↑</span>';
    chat.scrollTop = chat.scrollHeight;
}