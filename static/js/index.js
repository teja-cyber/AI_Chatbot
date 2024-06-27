document.addEventListener('DOMContentLoaded', function() {
    const messagesDiv = document.getElementById('messages');
    const userInput = document.getElementById('userInput');
    const welcomeMessage = messagesDiv.getAttribute('data-welcome-message');
    
    if (welcomeMessage) {
        messagesDiv.innerHTML += `<div class="message bot-message"><strong>Bot:</strong> ${welcomeMessage}</div>`;
    }

    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;

        messagesDiv.innerHTML += `<div class="message user-message"><strong>You:</strong> ${userMessage}</div>`;
        userInput.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            const botResponse = data.response;
            messagesDiv.innerHTML += `<div class="message bot-message"><strong>Bot:</strong> ${botResponse}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    }

    document.getElementById('userInput').addEventListener('keydown', handleKeyPress);
    document.querySelector('.input-container button').addEventListener('click', sendMessage);
});
