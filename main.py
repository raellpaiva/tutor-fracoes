from fractions import Fraction
from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from pydantic import BaseModel


class TentativaAluno(BaseModel):
    problema: str
    resposta: str
    raciocinio: str

def apresentar_problema():
    """
    Define e apresenta o problema ao aluno.
    """

    problema = Fraction(1, 2) + Fraction(1, 3)

    print("=== TUTOR DE FRAÇÕES ===")
    print()
    print("Resolva o problema:")
    print("1/2 + 1/3")
    print()

    return problema


def receber_resposta():
    """
    Recebe a resposta digitada pelo aluno,
    guarda a forma original, transforma
    em uma fração e registra o raciocínio.
    """

    resposta = input("Sua resposta: ")

    try:
        numerador, denominador = resposta.split("/")

        resposta_aluno = Fraction(
            int(numerador),
            int(denominador)
        )

        print()
        raciocinio = input("Como você chegou a esse resultado? ")

        return resposta, resposta_aluno, raciocinio

    except ValueError:
        print()
        print("Formato inválido.")
        print("Digite uma fração como 5/6.")

        return None, None, None


def validar_resposta(problema, resposta_aluno):
    """
    Compara a resposta do aluno
    com a resposta correta.
    """

    if resposta_aluno == problema:
        return True

    return False


def identificar_erro(
    problema,
    resposta_aluno,
    resposta_original,
    raciocinio
):
    """
    Identifica erros comuns usando
    a resposta e o raciocínio do aluno.
    """

    if resposta_aluno is None:
        return "resposta_invalida"

    if resposta_aluno == problema:
        return "correto"

    # Normaliza o texto informado pelo aluno
    raciocinio_normalizado = raciocinio.lower()

    # Identifica soma direta dos numeradores
    # e denominadores, mesmo que a ordem
    # das palavras seja diferente.
    if (
        "somei" in raciocinio_normalizado
        and "numeradores" in raciocinio_normalizado
        and "denominadores" in raciocinio_normalizado
    ):
        return "soma_direta"

    # Identifica respostas equivalentes a 1/3
    if resposta_aluno == Fraction(1, 3):
        return "denominador_nao_calculado"

    return "erro_nao_identificado"

def criar_dados_tentativa(
    problema,
    resposta_original,
    raciocinio,
    erro
):
    """
    Organiza todas as informações
    da tentativa do aluno.
    """

    dados_tentativa = {
        "problema": "1/2 + 1/3",
        "resposta": resposta_original,
        "raciocinio": raciocinio,
        "diagnostico": erro
    }

    return dados_tentativa
    

def explicar_erro(erro, resposta_original):
    """
    Apresenta uma orientação pedagógica
    de acordo com o erro identificado.
    """

    print()

    if erro == "correto":
        print("Muito bem! Seu raciocínio está correto.")

    elif erro == "soma_direta":
        print("Vamos analisar seu raciocínio.")
        print()
        print("Você somou os numeradores e os denominadores diretamente.")
        print()
        print("Em uma adição de frações, não podemos")
        print("simplesmente somar os denominadores.")
        print()
        print("Dica: primeiro precisamos encontrar")
        print("um denominador comum.")

    elif erro == "denominador_nao_calculado":
        print("Vamos analisar sua resposta.")
        print()
        print("Você escreveu", resposta_original)
        print()
        print("Observe que, para somar frações,")
        print("não basta somar os numeradores.")
        print()
        print("Precisamos transformar as frações")
        print("em frações equivalentes com")
        print("um denominador comum.")
        print()
        print("Dica:")
        print("pense em uma fração equivalente")
        print("a 1/2 com denominador 6.")

    elif erro == "erro_nao_identificado":
        print("Sua resposta não está correta.")
        print()
        print("Ainda não conseguimos identificar")
        print("exatamente onde ocorreu o erro.")
        print()
        print("Vamos investigar passo a passo")
        print("como você chegou a esse resultado.")


def mostrar_resultado(correto, resposta_original):
    """
    Mostra o resultado da tentativa.
    """

    print()

    if correto:
        print("✓ Correto!")
        print("Muito bem! Você acertou.")

    else:
        print("✗ Incorreto.")

        if resposta_original is not None:
            print(
                "Sua resposta:",
                resposta_original
            )

def executar_agente():
    """
    Controla o fluxo principal do agente.
    """

    problema = apresentar_problema()

    while True:

        resposta_original, resposta_aluno, raciocinio = receber_resposta()

        if resposta_aluno is None:
            return

        correto = validar_resposta(
            problema,
            resposta_aluno
        )

        erro = identificar_erro(
            problema,
            resposta_aluno,
            resposta_original, 
            raciocinio
        )

        dados_tentativa = criar_dados_tentativa(
            problema,
            resposta_original,
            raciocinio,
            erro
        )

        mostrar_resultado(
            correto,
            resposta_original
        )

        print()
        print("Diagnóstico:", erro)

        explicar_erro(
            erro,
            resposta_original
        )

        if correto:
            break

        print()
        print("Tente novamente.")
        print()

@app.get("/tutoria")
def tutoria():
    return {
        "mensagem": "API do Tutor de Frações funcionando!"
    }

@app.post("/tutoria")
def receber_tentativa(tentativa: TentativaAluno):

    try:
        numerador, denominador = tentativa.resposta.split("/")

        resposta_aluno = Fraction(
            int(numerador),
            int(denominador)
        )

    except ValueError:
        return {
            "diagnostico": "resposta_invalida",
            "intervencao": "Digite uma fração no formato 5/6."
        }

    problema = Fraction(1, 2) + Fraction(1, 3)

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
 
