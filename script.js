let problemaAtual = "1/2 + 1/3";

const botao = document.getElementById("verificar");
const botaoNovoExercicio = document.getElementById("novo-exercicio");

botao.addEventListener("click", async () => {
    const resposta = document.getElementById("resposta").value.trim();
    const raciocinio = document.getElementById("raciocinio").value.trim();
    const resultado = document.getElementById("resultado");

    if (!resposta || !raciocinio) {
        resultado.textContent =
            "⚠️ Preencha sua resposta e explique como você resolveu.";
        return;
    }

    resultado.textContent = "🧠 Analisando sua tentativa...";

    try {
        const respostaAPI = await fetch("/api/index", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                problema: problemaAtual,
                resposta: resposta,
                raciocinio: raciocinio
            })
        });

        const textoResposta = await respostaAPI.text();

        console.log("STATUS:", respostaAPI.status);
        console.log("RESPOSTA DA API:", textoResposta);

        if (!respostaAPI.ok) {
            throw new Error(
                `Erro da API: ${respostaAPI.status} - ${textoResposta}`
            );
        }

        let dados;

        try {
            dados = JSON.parse(textoResposta);
        } catch (erro) {
            console.error("Erro ao interpretar JSON:", erro);

            resultado.textContent =
                "❌ A API retornou uma resposta inválida.";

            return;
        }

        if (dados.intervencao) {
            resultado.textContent = dados.intervencao;
        } else {
            resultado.textContent =
                "❌ A API não retornou uma intervenção.";
        }

    } catch (erro) {
        console.error("Erro na comunicação com a API:", erro);

        resultado.textContent =
            "❌ Não consegui conectar ao Tutor. Verifique se o servidor está funcionando.";
    }
});

async function carregarNovoExercicio() {
    const resultado = document.getElementById("resultado");

    try {
        resultado.textContent = "🔄 Carregando novo exercício...";

        const respostaAPI = await fetch("/api/index");

        if (!respostaAPI.ok) {
            throw new Error(
                `Erro ao buscar exercício: ${respostaAPI.status}`
            );
        }

        const dados = await respostaAPI.json();

        problemaAtual = dados.problema;

        document.getElementById("problema").textContent =
            problemaAtual;

        document.getElementById("resposta").value = "";
        document.getElementById("raciocinio").value = "";

        resultado.textContent =
            "O feedback aparecerá aqui.";

    } catch (erro) {
        console.error("Erro ao carregar exercício:", erro);

        resultado.textContent =
            "❌ Não foi possível carregar um novo exercício.";
    }
}

botaoNovoExercicio.addEventListener(
    "click",
    carregarNovoExercicio
);
