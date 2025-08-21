const statusText = document.getElementById("statusText");
const toggleButton = document.getElementById("toggleButton");
const log = document.getElementById("log");

let ativo = true;

function adicionarLog(msg) {
    const p = document.createElement("p");
    p.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    log.prepend(p);
}

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

        if (!res.ok) {
            const errText = await res.text();
            adicionarLog(`Erro ao alterar status: ${errText}`);
            return;
        }

        const data = await res.json();
        ativo = data.status;
        statusText.innerText = ativo ? "Ativo" : "Desativado";
        statusText.classList.remove("ativo","desativado");
        statusText.classList.add(ativo ? "ativo":"desativado");
        adicionarLog(`Status alterado para: ${ativo ? "Ativo" : "Desativado"}`);
    } catch(err) {
        adicionarLog(`Erro ao alterar status: ${err}`);
    }
});
