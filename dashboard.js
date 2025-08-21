const statusText = document.getElementById("statusText");
const toggleButton = document.getElementById("toggleButton");
const log = document.getElementById("log");

// Inicializa status
let ativo = true;
statusText.classList.add("ativo");

// Função para adicionar log
function adicionarLog(msg) {
    const p = document.createElement("p");
    p.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    log.prepend(p);
}

// Toggle botão
toggleButton.addEventListener("click", async () => {
    const user = prompt("Usuário:");
    const pass = prompt("Senha:");
    if (!user || !pass) return;

    const auth = btoa(`${user}:${pass}`);

    try {
        const res = await fetch("/api/toggle", {
            method: "POST",
            headers: { "Authorization": `Basic ${auth}` }
        });
        const data = await res.json();
        ativo = data.status;
        statusText.innerText = ativo ? "Ativo" : "Desativado";

        statusText.classList.remove("ativo", "desativado");
        statusText.classList.add(ativo ? "ativo" : "desativado");

        adicionarLog(`Status alterado para: ${ativo ? "Ativo" : "Desativado"}`);
    } catch (err) {
        adicionarLog(`Erro ao alterar status: ${err}`);
    }
});
