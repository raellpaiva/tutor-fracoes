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
    {
        "id": 1,
        "problema": "1/2 + 1/3",
        "foco": "denominador_comum"
    },
    {
        "id": 2,
        "problema": "2/3 + 1/6",
        "foco": "frações_equivalentes"
    },
    {
        "id": 3,
        "problema": "3/4 - 1/2",
        "foco": "subtração"
    },
    {
        "id": 4,
        "problema": "2/5 + 3/10",
        "foco": "denominadores_múltiplos"
    },
    {
        "id": 5,
        "problema": "1/3 + 1/3",
        "foco": "mesmo_denominador"
    },
    {
        "id": 6,
        "problema": "3/4 - 1/4",
        "foco": "subtração_mesmo_denominador"
    },
    {
        "id": 7,
        "problema": "2/3 - 1/6",
        "foco": "equivalência_e_subtração"
    },
    {
        "id": 8,
        "problema": "1/2 + 2/5",
        "foco": "denominadores_diferentes"
    },
    {
        "id": 9,
        "problema": "3/5 + 1/10",
        "foco": "transformação_de_fração"
    },
    {
        "id": 10,
        "problema": "5/6 - 1/3",
        "foco": "equivalência_e_subtração"
    }
]

def identificar_erro(
    problema,
    resposta_aluno,
    resposta_original,
    raciocinio
):
    if resposta_aluno is None:
        return "resposta_invalida"

    if resposta_aluno == problema:
        return "correto"

    raciocinio_normalizado = raciocinio.lower()

    if (
        "somei" in raciocinio_normalizado
        and "numeradores" in raciocinio_normalizado
        and "denominadores" in raciocinio_normalizado
    ):
        return "soma_direta"

    if resposta_aluno == Fraction(1, 3):
        return "denominador_nao_calculado"

    return "erro_nao_identificado"


@app.get("/api/index")
def tutoria():
    import random

    exercicio = random.choice(PROBLEMAS)

    return {
        "id": exercicio["id"],
        "problema": exercicio["problema"],
        "foco": exercicio["foco"]
    }

@app.get("/api/index/exercicio")
def novo_exercicio():
    import random

    exercicio = random.choice(PROBLEMAS)

    return {
        "id": exercicio["id"],
        "problema": exercicio["problema"],
        "foco": exercicio["foco"]
    }
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
        "5/6 - 1/3": Fraction(5, 6) - Fraction(1, 3)
    }

    return respostas.get(problema)

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

    problema = calcular_resposta(tentativa.problema)

    erro = identificar_erro(
        problema,
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

    elif erro == "denominador_nao_calculado":
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
