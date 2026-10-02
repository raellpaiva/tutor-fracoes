let problemaAtual = "1/2 + 1/3";
let tentativaN = 0;

// ---- Registro das tentativas (planilha Google) ----
// Cole aqui a URL do Apps Script (termina em /exec) e o mesmo token do script.
const SHEETS_URL = "https://script.google.com/macros/s/AKfycbyMT9EAwGkyzjenUYA8htiCDOPiMUxuGUH8wmfwiohUfTCK3Tb1Yqvh-wHfW28tQ1szHw/exec";
const SHEETS_TOKEN = "TUTOR_FRACOES";
const CODIGO_VALIDO = /^[A-Za-z0-9-]{3,12}$/;

function registrarTentativa(dados) {
    if (!SHEETS_URL || SHEETS_URL.includes("COLE_AQUI")) {
        return;
    }

    try {
        fetch(SHEETS_URL, {
            method: "POST",
            mode: "no-cors",
            headers: { "Content-Type": "text/plain;charset=utf-8" },
            body: JSON.stringify({ token: SHEETS_TOKEN, ...dados }),
            keepalive: true
        }).catch((erro) => console.warn("Registro falhou:", erro));
    } catch (erro) {
        console.warn("Registro falhou:", erro);
    }
}

const botao = document.getElementById("verificar");
const botaoNovoExercicio = document.getElementById("novo-exercicio");

botao.addEventListener("click", async () => {
    const codigo = document.getElementById("codigo").value.trim().toUpperCase();
    const resposta = document.getElementById("resposta").value.trim();
    const raciocinio = document.getElementById("raciocinio").value.trim();
    const resultado = document.getElementById("resultado");

    if (!CODIGO_VALIDO.test(codigo)) {
        resultado.textContent =
            "⚠️ Digite seu código (exemplo: 7A-14). Não use seu nome.";
        return;
    }

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

        tentativaN += 1;

        registrarTentativa({
            codigo: codigo,
            problema: problemaAtual,
            resposta: resposta,
            raciocinio: raciocinio,
            diagnostico: dados.diagnostico || "",
            origem: dados.origem || "",
            correta: dados.diagnostico === "correto",
            tentativa_n: tentativaN
        });

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
        tentativaN = 0;

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
