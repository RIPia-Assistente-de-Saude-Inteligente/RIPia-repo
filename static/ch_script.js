document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("user-input");

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});

function appendMessage(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');

    if (sender === 'user') {
        messageElement.classList.add('user-msg');
        messageElement.innerHTML = `<b>Você:</b> ${message}`;
    } else {
        messageElement.classList.add('ia-msg');
        messageElement.innerHTML = `<b>RIPia:</b> ${message}`;
    }

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showOptions(options) {
    const optionsArea = document.getElementById('options-area');
    optionsArea.innerHTML = '';  // Limpa opções anteriores

    options.forEach(option => {
        const button = document.createElement('button');
        button.classList.add('option-button');
        button.innerText = option;
        button.onclick = () => {
            appendMessage('user', option);
            sendMessage(option);
        };
        optionsArea.appendChild(button);
    });
}

function sendMessage(userMessage = null) {
    const inputField = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const message = userMessage || inputField.value.trim();

    if (message === '') return;

    if (!userMessage) {
        appendMessage('user', message);
    }

    inputField.value = '';
    inputField.disabled = true;
    sendButton.disabled = true;
  
    showLoading(true);

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {

        const resposta = data.response || data.error || "Erro inesperado.";
        appendMessage('bot', resposta);

        if (data.options) {
            showOptions(data.options);
        } else {
            document.getElementById('options-area').innerHTML = '';
        }
    })
    .catch(() => {
        appendMessage('bot', 'Ocorreu um erro. Tente novamente.');
    })
    .finally(() => {
        inputField.disabled = false;
        sendButton.disabled = false;
        inputField.focus();
        showLoading(false);
    });
}

function showLoading(show) {
    const spinner = document.getElementById('loading'); // correto spinner
    const button = document.getElementById('send-button');

    if (show) {
        button.style.display = "none";      // esconde o botão
        spinner.classList.add('active');    // mostra o spinner
    } else {
        button.style.display = "inline-block"; // mostra o botão
        spinner.classList.remove('active');    // esconde o spinner
    }
}

