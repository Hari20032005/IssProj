const API_URL = 'http://localhost:5000';
let currentUser = null;

async function register() {
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            alert('Registered successfully. Please login.');
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            currentUser = username;
            document.getElementById('auth').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
            loadMessages();
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

async function sendMessage() {
    const recipient = document.getElementById('recipient').value;
    const content = document.getElementById('message').value;

    try {
        const response = await fetch(`${API_URL}/send_message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender: currentUser, recipient, content })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.phishing_detected) {
                if (confirm("This message may be a phishing attempt. Do you still want to send it?")) {
                    document.getElementById('message').value = '';
                    loadMessages();
                }
            } else {
                document.getElementById('message').value = '';
                loadMessages();
            }
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

async function loadMessages() {
    try {
        const response = await fetch(`${API_URL}/get_messages`);
        const messages = await response.json();

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';

        messages.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            messageElement.classList.add(message.sender === currentUser ? 'sent' : 'received');
            if (message.phishing_detected) {
                messageElement.classList.add('phishing');
            }
            
            const contentElement = document.createElement('div');
            contentElement.textContent = `${message.sender}: ${message.content}`;
            messageElement.appendChild(contentElement);
            
            const hmacElement = document.createElement('div');
            hmacElement.classList.add('hmac');
            hmacElement.textContent = `HMAC: ${message.hmac}`;
            messageElement.appendChild(hmacElement);
            
            messagesContainer.appendChild(messageElement);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while loading messages.');
    }
}

// Load messages every 5 seconds
setInterval(loadMessages, 5000);