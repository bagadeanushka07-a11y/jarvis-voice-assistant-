// DOM elements
const chatContainer = document.getElementById('chatMessages');
const micBtn = document.getElementById('micButton');
const micStatusSpan = document.getElementById('micStatusText');
const waveDiv = document.getElementById('waveContainer');
const commandPreviewSpan = document.getElementById('commandPreview');
const clearBtn = document.getElementById('clearChatBtn');
const testCmdBtn = document.getElementById('testCmdBtn');
const connStatusSpan = document.getElementById('connStatus');
const connectionBadge = document.getElementById('connectionBadge');
const commandInput = document.getElementById('commandInput');
const sendCommandBtn = document.getElementById('sendCommandBtn');

const BACKEND_URL = 'http://localhost:5000';

// Check backend health
async function checkBackendHealth() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/health`);
        if (response.ok) {
            const data = await response.json();
            connStatusSpan.innerText = 'Connected';
            connectionBadge.classList.add('status-online');
            connectionBadge.classList.remove('status-offline');
            micStatusSpan.innerText = 'JARVIS ready';
            return true;
        }
    } catch (error) {
        console.error('Health check failed:', error);
        connStatusSpan.innerText = 'Disconnected';
        connectionBadge.classList.add('status-offline');
        connectionBadge.classList.remove('status-online');
        micStatusSpan.innerText = 'Backend offline';
        return false;
    }
    return false;
}

// Send command to backend
async function sendCommandToBackend(command) {
    commandPreviewSpan.innerHTML = `📤 Sending: "${command.substring(0, 50)}"`;
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.response && data.response !== 'Command processed') {
                addMessage('JARVIS', data.response, false);
            }
            commandPreviewSpan.innerHTML = `✅ Command sent: "${command}"`;
            return true;
        } else {
            addSystemMessage(`Backend error: ${response.status}`, true);
            return false;
        }
    } catch (error) {
        console.error('Failed to send command:', error);
        addSystemMessage(`Cannot reach backend: ${error.message}`, true);
        return false;
    }
}

function addMessage(sender, text, isUser = true) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-msg' : 'jarvis-msg'}`;
    const icon = isUser ? '<i class="fas fa-user-astronaut"></i>' : '<i class="fas fa-microchip"></i>';
    msgDiv.innerHTML = `
        <div class="msg-icon">${icon}</div>
        <div class="msg-content">
            ${escapeHtml(text)}<br>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function addSystemMessage(text, isError = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message jarvis-msg`;
    msgDiv.innerHTML = `
        <div class="msg-icon"><i class="fas ${isError ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i></div>
        <div class="msg-content" style="color: ${isError ? '#f66' : '#0cf'}">
            ${escapeHtml(text)}<br>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    msgDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sendTextCommand() {
    const command = commandInput.value.trim();
    if (command) {
        addMessage('You', command, true);
        sendCommandToBackend(command);
        commandInput.value = '';
    }
}

// Voice Recognition
let recognition = null;
let isListening = false;

function initVoiceRecognition() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        addSystemMessage('❌ Your browser does not support voice recognition. Please use Chrome or Edge.', true);
        if (micBtn) {
            micBtn.style.opacity = '0.5';
            micBtn.style.cursor = 'not-allowed';
        }
        return false;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    recognition.onstart = () => {
        isListening = true;
        micStatusSpan.innerText = "🎤 Listening... Speak now";
        waveDiv.classList.remove('inactive-wave');
        micBtn.classList.add('listening');
        addSystemMessage("🎤 Voice recognition active - speak your command", false);
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Voice recognized:', transcript);
        addMessage('You (voice)', transcript, true);
        sendCommandToBackend(transcript);
        recognition.stop();
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        let errorMsg = '';
        switch(event.error) {
            case 'no-speech':
                errorMsg = 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMsg = 'No microphone found. Please check your microphone.';
                break;
            case 'not-allowed':
                errorMsg = 'Microphone permission denied. Please allow microphone access.';
                break;
            default:
                errorMsg = `Error: ${event.error}`;
        }
        addSystemMessage(`🎤 ${errorMsg}`, true);
        resetVoiceState();
    };
    
    recognition.onend = () => {
        resetVoiceState();
    };
    
    return true;
}

function resetVoiceState() {
    isListening = false;
    waveDiv.classList.add('inactive-wave');
    if (micBtn) micBtn.classList.remove('listening');
    micStatusSpan.innerText = 'Click mic to speak';
}

// Setup microphone button
function setupMicrophone() {
    if (!micBtn) return;
    
    micBtn.onclick = async () => {
        if (isListening) {
            recognition.stop();
            return;
        }
        
        // Check if backend is connected
        const isConnected = await checkBackendHealth();
        if (!isConnected) {
            addSystemMessage('❌ Backend not connected. Please start the backend first.', true);
            return;
        }
        
        // Check if recognition is initialized
        if (!recognition) {
            const success = initVoiceRecognition();
            if (!success) return;
        }
        
        // Request microphone permission
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop()); // Stop the stream after getting permission
            recognition.start();
        } catch (err) {
            console.error('Microphone permission error:', err);
            addSystemMessage('❌ Cannot access microphone. Please check your microphone settings and permissions.', true);
        }
    };
}

// Test connection
async function testConnection() {
    addSystemMessage('Testing connection...', false);
    const isConnected = await checkBackendHealth();
    if (isConnected) {
        addSystemMessage('✅ Connection successful! JARVIS is ready.', false);
        addSystemMessage('💡 Try: typing "time" or clicking the microphone and saying "time"', false);
    } else {
        addSystemMessage('❌ Backend not running. Please run: python working_backend.py', true);
    }
}

// Clear chat
if (clearBtn) {
    clearBtn.onclick = () => {
        chatContainer.innerHTML = '';
        addMessage('JARVIS', 'Chat log cleared. Ready for commands.', false);
    };
}

// Test button
if (testCmdBtn) {
    testCmdBtn.onclick = testConnection;
}

// Send button
if (sendCommandBtn) {
    sendCommandBtn.onclick = sendTextCommand;
}

// Enter key
if (commandInput) {
    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendTextCommand();
        }
    });
}

// Initialize
console.log('Starting JARVIS frontend...');
checkBackendHealth();
initVoiceRecognition();
setupMicrophone();

// Periodic health check
setInterval(() => {
    checkBackendHealth();
}, 30000);