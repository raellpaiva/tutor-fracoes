import json
import os
import re
import unicodedata
from fractions import Fraction

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TentativaAluno(BaseModel):
    problema: str
    resposta: str
    raciocinio: str


PROBLEMAS = [
    {"id": 1, "problema": "1/2 + 1/3", "foco": "denominador_comum"},
    {"id": 2, "problema": "2/3 + 1/6", "foco": "frações_equivalentes"},
    {"id": 3, "problema": "3/4 - 1/2", "foco": "subtração"},
    {"id": 4, "problema": "2/5 + 3/10", "foco": "denominadores_múltiplos"},
    {"id": 5, "problema": "1/3 + 1/3", "foco": "mesmo_denominador"},
    {"id": 6, "problema": "3/4 - 1/4", "foco": "subtração_mesmo_denominador"},
    {"id": 7, "problema": "2/3 - 1/6", "foco": "equivalência_e_subtração"},
    {"id": 8, "problema": "1/2 + 2/5", "foco": "denominadores_diferentes"},
    {"id": 9, "problema": "3/5 + 1/10", "foco": "transformação_de_fração"},
    {"id": 10, "problema": "5/6 - 1/3", "foco": "equivalência_e_subtração"},
]


def normalizar_texto(texto):
    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")

    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto


SINONIMOS_SOMA = (
    "somei",
    "adicionei",
    "somando",
    "adicionando",
    "juntei",
)

SINONIMOS_SUBTRACAO = (
    "subtrai",
    "subtraindo",
    "tirei",
    "diminui",
)

PALAVRAS_NUMERADOR = ("numerador",)
PALAVRAS_DENOMINADOR = ("denominador",)


def contem_alguma(texto, palavras):
    return any(palavra in texto for palavra in palavras)


def parse_problema(problema_str):
    match = re.match(
        r"\s*(\d+)/(\d+)\s*([+-])\s*(\d+)/(\d+)\s*",
        problema_str
    )

    if not match:
        return None

    num1, den1, operador, num2, den2 = match.groups()

    return int(num1), int(den1), operador, int(num2), int(den2)


def identificar_erro(
    problema_str,
    resposta_correta,
    resposta_aluno,
    resposta_original,
    raciocinio
):
    if resposta_aluno is None:
        return "resposta_invalida"

    if resposta_aluno == resposta_correta:
        return "correto"

    raciocinio_normalizado = normalizar_texto(raciocinio)

    if (
        contem_alguma(raciocinio_normalizado, SINONIMOS_SOMA)
        and contem_alguma(raciocinio_normalizado, PALAVRAS_NUMERADOR)
        and contem_alguma(raciocinio_normalizado, PALAVRAS_DENOMINADOR)
    ):
        return "soma_direta"

    if (
        contem_alguma(raciocinio_normalizado, SINONIMOS_SUBTRACAO)
        and contem_alguma(raciocinio_normalizado, PALAVRAS_NUMERADOR)
        and contem_alguma(raciocinio_normalizado, PALAVRAS_DENOMINADOR)
    ):
        return "subtracao_direta"

    partes = parse_problema(problema_str)

    if partes:
        _, den1, _, _, den2 = partes

        if (
            resposta_aluno.denominator in (den1, den2)
            and resposta_aluno.denominator != resposta_correta.denominator
        ):
            return "denominador_nao_calculado"

    return "erro_nao_identificado"


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-3.5-flash-lite"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def diagnosticar_com_ia(
    problema_str,
    resposta_correta,
    resposta_aluno,
    raciocinio,
    diagnostico
):
    """
    Usa o Gemini para interpretar o raciocínio do aluno
    e produzir uma intervenção pedagógica personalizada.
    """

    if not GEMINI_API_KEY:
        return None

    prompt = f"""
Você é o Tutor Inteligente de Frações.

Sua função é ajudar um estudante a aprender adição e subtração
de frações por meio de perguntas e pistas graduais.

NÃO entregue a resposta final do exercício.

Analise principalmente o RACIOCÍNIO escrito pelo estudante.

Dados da tentativa:

Problema:
{problema_str}

Resposta correta (informação interna, NÃO revele):
{resposta_correta}

Resposta do estudante:
{resposta_aluno}

Raciocínio do estudante:
{raciocinio}

Diagnóstico preliminar do sistema:
{diagnostico}

Sua tarefa:

1. Identifique o ponto do raciocínio em que o estudante
   provavelmente encontrou dificuldade.

2. Produza uma intervenção personalizada relacionada
   diretamente ao que o estudante escreveu.

3. Faça apenas uma pergunta ou proponha um próximo passo.

4. Não entregue a resposta final.

5. Use português brasileiro simples, claro e encorajador.

6. Não diga apenas que a resposta está errada.

7. Não faça uma explicação longa.

Retorne SOMENTE um JSON válido neste formato:

{{
    "diagnostico": "categoria_curta",
    "intervencao": "uma ou duas frases personalizadas para o estudante"
}}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = httpx.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        texto = data["candidates"][0]["content"]["parts"][0]["text"]

        texto = texto.strip()

        if texto.startswith("```"):
            texto = re.sub(r"^```(?:json)?", "", texto)
            texto = re.sub(r"```$", "", texto)
            texto = texto.strip()

        resultado = json.loads(texto)

        if (
            not isinstance(resultado, dict)
            or "diagnostico" not in resultado
            or "intervencao" not in resultado
        ):
            return None

        if not resultado["intervencao"].strip():
            return None

        return resultado

   except Exception as erro:
    print("ERRO GEMINI:", repr(erro))
    if hasattr(erro, "response") and erro.response is not None:
        print("STATUS GEMINI:", erro.response.status_code)
        print("RESPOSTA GEMINI:", erro.response.text)
    return None


def calcular_resposta(problema):
    respostas = {
        "1/2 + 1/3": Fraction(1, 2) + Fraction(1, 3),
        "2/3 + 1/6": Fraction(2, 3) + Fraction(1, 6),
        "3/4 - 1/2": Fraction(3, 4) - Fraction(1, 2),
        "2/5 + 3/10": Fraction(2, 5) + Fraction(3, 10),
        "1/3 + 1/3": Fraction(1, 3) + Fraction(1, 3),
        "3/4 - 1/4": Fraction(3, 4) - Fraction(1, 4),
        "2/3 - 1/6": Fraction(2, 3) - Fraction(1, 6),
        "1/2 + 2/5": Fraction(1, 2) + Fraction(2, 5),
        "3/5 + 1/10": Fraction(3, 5) + Fraction(1, 10),
        "5/6 - 1/3": Fraction(5, 6) - Fraction(1, 3),
    }

    return respostas.get(problema)


@app.get("/api/index")
def tutoria():
    import random

    exercicio = random.choice(PROBLEMAS)

    return {
        "id": exercicio["id"],
        "problema": exercicio["problema"],
        "foco": exercicio["foco"],
    }


@app.get("/api/index/exercicio")
def novo_exercicio():
    import random

    exercicio = random.choice(PROBLEMAS)

    return {
        "id": exercicio["id"],
        "problema": exercicio["problema"],
        "foco": exercicio["foco"],
    }


@app.post("/api/index")
def receber_tentativa(tentativa: TentativaAluno):

    try:
        numerador, denominador = tentativa.resposta.split("/")

        resposta_aluno = Fraction(
            int(numerador),
            int(denominador)
        )

    except (ValueError, ZeroDivisionError):
        return {
            "diagnostico": "resposta_invalida",
            "intervencao": (
                "Digite sua resposta no formato de uma fração, "
                "como 5/6."
            )
        }

    resposta_correta = calcular_resposta(tentativa.problema)

    if resposta_correta is None:
        return {
            "diagnostico": "problema_nao_reconhecido",
            "intervencao": (
                "Não reconheço esse exercício. "
                "Tente carregar um novo exercício."
            )
        }

    erro = identificar_erro(
        tentativa.problema,
        resposta_correta,
        resposta_aluno,
        tentativa.resposta,
        tentativa.raciocinio
    )

    # Resposta correta continua sendo verificada
    # deterministicamente pelo Python.
    if erro == "correto":

        intervencao = (
            "Muito bem! Seu raciocínio está correto. "
            "Você conseguiu resolver a operação."
        )

        return {
            "problema": tentativa.problema,
            "resposta": tentativa.resposta,
            "raciocinio": tentativa.raciocinio,
            "diagnostico": erro,
            "intervencao": intervencao
        }

    # Para respostas incorretas, a IA passa a analisar
    # o raciocínio e produzir a intervenção.
    diagnostico_ia = diagnosticar_com_ia(
        tentativa.problema,
        resposta_correta,
        resposta_aluno,
        tentativa.raciocinio,
        erro
    )

    if diagnostico_ia:

        erro = diagnostico_ia["diagnostico"]

        intervencao = diagnostico_ia["intervencao"]

    else:

        # Fallback caso a IA esteja indisponível.
        if erro == "soma_direta":

            intervencao = (
                "Você somou os numeradores e os denominadores "
                "diretamente. Antes de fazer essa operação, "
                "o que precisamos observar nos denominadores?"
            )

        elif erro == "subtracao_direta":

            intervencao = (
                "Você subtraiu os numeradores e os denominadores "
                "diretamente. Antes de continuar, o que precisamos "
                "fazer quando os denominadores são diferentes?"
            )

        elif erro == "denominador_nao_calculado":

            intervencao = (
                "Observe os denominadores das duas frações. "
                "Que número poderia ser usado como denominador comum?"
            )

        else:

            intervencao = (
                "Vamos investigar seu raciocínio. "
                "Qual foi o primeiro passo que você realizou "
                "para tentar resolver essa operação?"
            )

    return {
        "problema": tentativa.problema,
        "resposta": tentativa.resposta,
        "raciocinio": tentativa.raciocinio,
        "diagnostico": erro,
        "intervencao": intervencao
    }
