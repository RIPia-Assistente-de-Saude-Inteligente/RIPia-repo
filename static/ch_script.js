document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("user-input");

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Evita quebra de linha
            sendMessage(); // Chama a função de envio
        }
    });
});

function sendMessage() {
    const input = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const message = input.value.trim();
    if (!message) return;

    // Desativa botão e campo
    sendButton.disabled = true;
    input.disabled = true;

    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<div class="user-msg"><b>You:</b> ${message}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight; // Garante scroll após mensagem do usuário
    input.value = '';
    showLoading(true);

    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    })
    .then(response => response.json())
    .then(data => {
        let resposta = data.response || data.error || "Erro inesperado.";
        resposta = resposta.replace(/\n/g, "<br>");
        chatBox.innerHTML += `<div class="ia-msg"><b>AI:</b> ${resposta}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight; // Garante scroll após resposta da IA
    })
    .catch(() => {
        chatBox.innerHTML += `<div class="ia-msg"><b>AI:</b> Ocorreu um erro. Tente novamente.</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .finally(() => {
        // Reativa botão e campo
        sendButton.disabled = false;
        input.disabled = false;
        input.focus();
        showLoading(false);
    });
}

function showLoading(show) {
    const spinner = document.getElementById('loading');
    if (show) {
        spinner.classList.add('active');
    } else {
        spinner.classList.remove('active');
    }
}
