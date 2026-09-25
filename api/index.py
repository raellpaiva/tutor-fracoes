import re
import unicodedata
from fractions import Fraction

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
    """
    Remove acentos, pontuação e caixa alta, para tornar
    a checagem de palavras-chave mais tolerante à forma
    como o aluno escreve.
    """

    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")

    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto


# Sinônimos comuns para as operações, já sem acento
# (compatível com a saída de normalizar_texto).
SINONIMOS_SOMA = ("somei", "adicionei", "somando", "adicionando", "juntei")
SINONIMOS_SUBTRACAO = ("subtrai", "subtraindo", "tirei", "diminui")
PALAVRAS_NUMERADOR = ("numerador",)  # cobre "numerador" e "numeradores"
PALAVRAS_DENOMINADOR = ("denominador",)  # cobre "denominador" e "denominadores"


def contem_alguma(texto, palavras):
    return any(palavra in texto for palavra in palavras)


def parse_problema(problema_str):
    """
    Extrai (num1, den1, operador, num2, den2) de uma string
    como "2/3 + 1/6" ou "3/4 - 1/2".
    """

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

    # Generalização: o aluno usou um dos denominadores originais
    # como denominador final, em vez de calcular um denominador
    # comum (antes, isso só era checado para o caso fixo 1/2 + 1/3).
    partes = parse_problema(problema_str)

    if partes:
        _, den1, _, _, den2 = partes

        if (
            resposta_aluno.denominator in (den1, den2)
            and resposta_aluno.denominator != resposta_correta.denominator
        ):
            return "denominador_nao_calculado"

    return "erro_nao_identificado"


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
            "intervencao": "Digite uma fração no formato 5/6."
        }

    resposta_correta = calcular_resposta(tentativa.problema)

    if resposta_correta is None:
        return {
            "diagnostico": "problema_nao_reconhecido",
            "intervencao": "Não reconheço esse problema. Peça um novo exercício."
        }

    erro = identificar_erro(
        tentativa.problema,
        resposta_correta,
        resposta_aluno,
        tentativa.resposta,
        tentativa.raciocinio
    )

    if erro == "correto":

        intervencao = (
            "Muito bem! Seu raciocínio está correto."
        )

    elif erro == "soma_direta":

        intervencao = (
            "Você somou os numeradores e os denominadores "
            "diretamente. Em uma adição de frações, "
            "precisamos primeiro encontrar um denominador comum."
        )

    elif erro == "subtracao_direta":

        intervencao = (
            "Você subtraiu os numeradores e os denominadores "
            "diretamente. Na subtração de frações, "
            "precisamos primeiro encontrar um denominador comum."
        )

    elif erro == "denominador_nao_calculado":

        if "-" in tentativa.problema:

            intervencao = (
                "Observe sua resposta. Para subtrair frações, "
                "precisamos transformar as frações em frações "
                "equivalentes com um denominador comum."
            )

        else:

            intervencao = (
                "Observe sua resposta. Para somar frações, "
                "precisamos transformar as frações em frações "
                "equivalentes com um denominador comum."
            )

    else:

        intervencao = (
            "Sua resposta não está correta. "
            "Vamos investigar passo a passo como você chegou "
            "a esse resultado."
        )

    return {
        "problema": tentativa.problema,
        "resposta": tentativa.resposta,
        "raciocinio": tentativa.raciocinio,
        "diagnostico": erro,
        "intervencao": intervencao
    }
