const statusText = document.getElementById("statusText");
const toggleButton = document.getElementById("toggleButton");

toggleButton.addEventListener("click", async () => {
    const user = prompt("Usuário:");
    const pass = prompt("Senha:");
    const auth = btoa(`${user}:${pass}`);
    const res = await fetch("/api/toggle", { 
        method: "POST", 
        headers: { "Authorization": `Basic ${auth}` } 
    });
    const data = await res.json();
    statusText.innerText = data.status ? "Ativo" : "Desativado";
});
