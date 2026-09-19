# 🧠 Tutor de Frações

Um protótipo de agente de tutoria para o ensino de frações, desenvolvido com **Python, FastAPI, HTML, CSS e JavaScript**.

O projeto busca investigar como sistemas computacionais podem identificar erros no processo de resolução de problemas matemáticos e fornecer **intervenções pedagógicas direcionadas**, em vez de simplesmente apresentar a resposta correta.

> **Status:** 🚧 Protótipo em desenvolvimento

---

## 🎯 Objetivo

O Tutor de Frações foi desenvolvido para experimentar uma abordagem de tutoria baseada no seguinte fluxo:

```text
Problema
   ↓
Resposta do aluno
   ↓
Raciocínio apresentado
   ↓
Diagnóstico do erro
   ↓
Intervenção pedagógica
   ↓
Nova tentativa
```

A proposta é que o sistema considere não apenas a resposta final do estudante, mas também **como ele chegou ao resultado**.

---

## 🧮 Problema atual

Nesta primeira versão, o sistema trabalha com:

```text
1/2 + 1/3
```

O aluno informa:

1. Sua resposta;
2. Como chegou ao resultado.

Por exemplo:

```text
Resposta:
2/5

Raciocínio:
somei os numeradores e denominadores
```

O sistema identifica o padrão de erro e apresenta uma intervenção.

---

## 🔎 Diagnóstico

Atualmente, o protótipo reconhece alguns estados:

| Diagnóstico                 | Descrição                                               |
| --------------------------- | ------------------------------------------------------- |
| `correto`                   | A resposta corresponde ao resultado esperado            |
| `soma_direta`               | O aluno soma diretamente numeradores e denominadores    |
| `denominador_nao_calculado` | A resposta apresenta um padrão compatível com esse erro |
| `erro_nao_identificado`     | O sistema não conseguiu classificar o erro              |

O diagnóstico atualmente é realizado por regras implementadas em Python.

---

## 💡 Intervenção pedagógica

Após o diagnóstico, o sistema apresenta uma orientação relacionada ao erro identificado.

A intenção não é simplesmente entregar a resposta, mas oferecer uma **pista para que o estudante possa reconsiderar seu procedimento**.

Exemplo:

```text
Você somou os numeradores e os denominadores diretamente.

Em uma adição de frações, precisamos primeiro encontrar
um denominador comum.
```

---

## 🏗️ Arquitetura

O projeto possui uma arquitetura simples de aplicação web:

```text
                  👨‍🎓 Aluno
                      │
                      ▼
            ┌─────────────────┐
            │    Front-end    │
            │ HTML + CSS + JS │
            └────────┬────────┘
                     │
                     │ HTTP POST
                     ▼
            ┌─────────────────┐
            │     FastAPI     │
            │     Python      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │    Diagnóstico  │
            │     Python      │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │    Intervenção  │
            │    pedagógica   │
            └────────┬────────┘
                     │
                     ▼
                  💡 Feedback
```

---

## 🎨 Interface

A interface foi desenvolvida com uma proposta visual inspirada em **Pop Art**, utilizando cores vibrantes, contornos marcantes e elementos visuais semelhantes aos de histórias em quadrinhos.

O objetivo é tornar a interação mais amigável e adequada a uma aplicação educacional.

---

## 🛠️ Tecnologias utilizadas

* **Python**
* **FastAPI**
* **Pydantic**
* **HTML5**
* **CSS3**
* **JavaScript**
* **Uvicorn**
* **Postman** para testes da API
* **Git/GitHub** para versionamento

---

## 📁 Estrutura do projeto

```text
fracao_tutor/
│
├── main.py          # API e lógica do tutor
├── index.html       # Interface do aluno
├── style.css        # Estilização da interface
├── script.js        # Comunicação entre front-end e API
├── .env             # Variáveis de ambiente (não versionado)
├── .gitignore       # Arquivos ignorados pelo Git
└── README.md        # Documentação do projeto
```

---

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone URL_DO_REPOSITORIO
```

Entre na pasta:

```bash
cd fracao_tutor
```

### 2. Instale as dependências

```bash
pip install fastapi uvicorn openai python-dotenv
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env`:

```env
OPENAI_API_KEY=sua_chave_aqui
```

> A chave de API não deve ser publicada no GitHub.

### 4. Execute a API

```bash
uvicorn main:app --reload
```

A API estará disponível localmente em:

```text
http://127.0.0.1:8000
```

### 5. Abra a interface

Abra o arquivo:

```text
index.html
```

no navegador.

---

## 🔌 API

### GET `/tutoria`

Verifica se a API está funcionando.

Resposta:

```json
{
    "mensagem": "API do Tutor de Frações funcionando!"
}
```

### POST `/tutoria`

Recebe uma tentativa do aluno.

Exemplo:

```json
{
    "problema": "1/2 + 1/3",
    "resposta": "2/5",
    "raciocinio": "somei os numeradores e denominadores"
}
```

O sistema retorna informações como:

```json
{
    "problema": "1/2 + 1/3",
    "resposta": "2/5",
    "raciocinio": "somei os numeradores e denominadores",
    "diagnostico": "soma_direta",
    "intervencao": "Você somou os numeradores e os denominadores diretamente..."
}
```

---

## 🧪 Testes

A API pode ser testada utilizando o **Postman**.

Também é possível realizar o teste diretamente pela interface web:

```text
Aluno
 ↓
index.html
 ↓
JavaScript
 ↓
POST /tutoria
 ↓
FastAPI
 ↓
Diagnóstico
 ↓
Feedback
```

---

## 🤖 Inteligência Artificial

A arquitetura do projeto foi pensada para futuramente incorporar um modelo de linguagem.

A proposta é utilizar uma arquitetura híbrida:

```text
Aluno
 ↓
Python
 ↓
Validação matemática
 ↓
Diagnóstico
 ↓
IA
 ↓
Intervenção pedagógica
```

Nesse modelo, o Python mantém o controle da lógica e da validação, enquanto a IA poderá interpretar o raciocínio do estudante e produzir intervenções mais adaptativas.

A integração com uma API de IA ainda está em desenvolvimento.

---

## 🔬 Possibilidades de evolução

Entre os próximos passos planejados estão:

* [ ] Melhorar a identificação dos erros matemáticos;
* [ ] Separar diagnóstico e geração de intervenção;
* [ ] Registrar as tentativas dos estudantes;
* [ ] Melhorar a análise do raciocínio;
* [ ] Criar novas situações-problema;
* [ ] Desenvolver uma interface mais interativa;
* [ ] Implementar histórico de tentativas;
* [ ] Incorporar inteligência artificial generativa;
* [ ] Criar intervenções adaptativas;
* [ ] Avaliar o comportamento do tutor com estudantes.

---

## 📚 Perspectiva educacional

O projeto parte da ideia de que, em Matemática, **o erro pode fornecer informações importantes sobre o processo de aprendizagem**.

Por isso, o sistema não considera apenas:

```text
Resposta correta
ou
Resposta incorreta
```

mas busca trabalhar com:

```text
O que o aluno respondeu?
        +
Como ele pensou?
        ↓
Qual erro ocorreu?
        ↓
Que intervenção pode ajudá-lo?
```

Essa abordagem aproxima o desenvolvimento de software educacional de conceitos como **feedback formativo, diagnóstico de aprendizagem e tutoria adaptativa**.

---

## 👨‍💻 Autor

**Antonio Rael de Paiva**

Licenciado em Matemática | Estudante de Bacharelado em Inteligência Artificial

Projeto desenvolvido como estudo prático envolvendo:

* Inteligência Artificial;
* Programação;
* Educação Matemática;
* Sistemas educacionais;
* Tutoria inteligente.

---

## 📌 Status do projeto

**Em desenvolvimento.**

Este repositório representa um protótipo inicial de um sistema de tutoria matemática. Novas funcionalidades serão incorporadas progressivamente, especialmente relacionadas à análise do raciocínio do estudante e à utilização de inteligência artificial generativa.
