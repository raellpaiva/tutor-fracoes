const botao = document.getElementById("verificar");

botao.addEventListener("click", async () => {

    const resposta = document.getElementById("resposta").value.trim();
    const raciocinio = document.getElementById("raciocinio").value.trim();
    const resultado = document.getElementById("resultado");

    // Verifica se os campos foram preenchidos
    if (!resposta || !raciocinio) {

        resultado.textContent =
            "⚠️ Preencha sua resposta e explique como você resolveu.";

        return;
    }

    // Mensagem enquanto o tutor analisa
    resultado.textContent =
        "🧠 Analisando sua tentativa...";

    try {

        const respostaAPI = await fetch(
            "/api/index",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    problema: "1/2 + 1/3",
                    resposta: resposta,
                    raciocinio: raciocinio
                })
            }
        );

        const dados = await respostaAPI.json();

        // Mostra a intervenção do tutor
        resultado.textContent = dados.intervencao;

    } catch (erro) {

        console.error(erro);

        resultado.textContent =
            "❌ Não consegui conectar ao Tutor. Verifique se o servidor está funcionando.";
    }
});

async function carregarNovoExercicio() {
    try {
        const respostaAPI = await fetch("/api/index");

        if (!respostaAPI.ok) {
            throw new Error("Erro ao buscar exercício");
        }

        const dados = await respostaAPI.json();

        document.getElementById("problema").textContent =
            dados.problema;

        document.getElementById("resposta").value = "";
        document.getElementById("raciocinio").value = "";

        document.getElementById("resultado").textContent =
            "O feedback aparecerá aqui.";

    } catch (erro) {
        console.error(erro);

        document.getElementById("resultado").textContent =
            "Não foi possível carregar um novo exercício.";
    }
}


document.getElementById("novo-exercicio").addEventListener(
    "click",
    carregarNovoExercicio
);
