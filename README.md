![CI](https://github.com/amandadduraes/empreendimentos/actions/workflows/ci.yml/badge.svg)


# Empreendimentos – Validador (FastAPI + React)

Validação de empreendimentos a partir de um arquivo (JSON) com regras de negócio
por **cidade** e por **construtora**, com **frontend** (React + styled-components) para upload,
consulta e auditoria das regras aplicadas.

---

## 🔧 Tecnologias

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic, pytest
- **Frontend**: Vite + React, styled-components
- **Testes**: pytest (+ httpx/anyio para TestClient)

---

### 📁 Estrutura

```text
empreendimentos/
├─ backend/
│  ├─ app.py
│  ├─ testes/
│  │  ├─ test_api.py
│  │  └─ test_validation.py
│  └─ .venv/            # virtualenv (ignorado no git)
├─ frontend/
│  ├─ src/
│  │  └─ App.jsx
│  ├─ package.json
│  └─ node_modules/     # dependências (ignorado no git)
├─ .gitignore
├─ .gitattributes
└─ README.md

```

---

## ▶️ Como rodar

### Backend (FastAPI)

> Windows / PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install fastapi uvicorn python-multipart pytest httpx anyio
uvicorn app:app --reload --port 8000
```

A API sobe em: http://localhost:8000 Ou
http:/localhost:8000/docs

Se o PowerShell bloquear a ativação da venv:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass


### FrontEnd (React com Vite)

```powershell
cd frontend
npm install
npm run dev
```

### Testes (backend)
Rodar todos os testes:

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
````
Rodar testes específicos:

```powershell
pytest testes\test_api.py -q
pytest -k regras_aplicadas -vv
```

(Caso peça, garanta que httpx e anyio foram instalados para o TestClient.)

## Formato do JSON (entrada)

Uma lista de empreendimentos, cada um com:

construtora (str)

cidade (str)

area-do-terreno (float/int, m²)

numero-de-torres (int)

altura-da-torre (float/int, m)

area-da-torre (float/int, m²)

area-de-lazer (float/int, m²) — obrigatório quando houver mais de 1 torre (ou quando regras exigirem)

Dentro da pasta Backend, há alguns exemplos de testes.json, caso precise utilizar.

## Regras de negócio

Regras base:

Altura < 30m por torre

Área total das torres < 80% da área do terreno

Se mais de uma torre, exigir área de lazer ≥ 10% do terreno

Regras por cidade (exemplos):

Rio de Janeiro: aplica 1 e 2

São Paulo: aplica 2 e 3

Boituva: máximo 5 torres (além de 1,2,3)

Guaratinguetá: altura máxima depende do nº de torres

1–2 torres: 25m

3 torres: 20m

4+ torres: 15m

Regras por construtora (exemplo):

Alpha: sempre tem área de lazer ≥ 10% do terreno (obrigatória em todos os empreendimentos)

Combinação: aplica primeiro o conjunto da cidade e depois somam-se as regras da construtora (sem duplicar).

## Endpoints
```powershell
POST /validar

Recebe um arquivo JSON (multipart/form-data) com a lista de empreendimentos e retorna a validação.

cURL:
curl -F "file=@teste.json" http://localhost:8000/validar

GET /regras-aplicadas?cidade=...&construtora=...

Retorna quais regras foram consideradas (útil para auditoria).

curl "http://localhost:8000/regras-aplicadas?cidade=Sao%20Paulo&construtora=Alpha"


GET /regras-opcoes

Retorna listas para popular selects do frontend:
{
  "cidades": ["boituva", "guaratingueta", "rio de janeiro", "sao paulo"],
  "construtoras": ["alpha", "construtora alpha"]
}
````
## Frontend (funcionalidades)

Upload do arquivo .json para /validar (ou /importar, se existir).
Auditoria: seleciona Cidade e Construtora e mostra as regras aplicadas (chama /regras-aplicadas).

Campos com styled-components e tema claro forçado (color-scheme: light) para não sumirem opções em tema escuro do Windows/Edge.

## Como criar novas regras

Crie uma classe que herda de Rule em app.py e implemente validate(self, emp) -> Optional[str].

Adicione a instância no dict ALL_RULES.

Inclua a chave da regra no conjunto apropriado:

CITY_RULE_SETS["nome-normalizado-da-cidade"] = [...]

BUILDER_RULE_SETS["nome-normalizado-da-construtora"] = [...]

A regra passa a valer automaticamente para POST /validar e aparecerá em /regras-aplicadas.




