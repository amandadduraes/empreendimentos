import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_validar_retorna_200_com_json_valido():
    payload = [
        {
            "construtora": "Construtora Alfa",
            "cidade": "São Paulo",
            "area-do-terreno": 10000,
            "numero-de-torres": 2,
            "altura-da-torre": 25,
            "area-da-torre": 3000,
            "area-de-lazer": 1200
        }
    ]
    files = {
        "file": ("empreendimentos.json", json.dumps(payload), "application/json")
    }
    resp = client.post("/validar", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["status"] == "Válido"
    assert data[0]["erros"] == []

def test_validar_retorna_erros_para_json_invalido_regra():
    payload = [
        {
            "construtora": "Construtora Beta",
            "cidade": "Rio de Janeiro",
            "area-do-terreno": 5000,
            "numero-de-torres": 1,
            "altura-da-torre": 35,   # viola altura
            "area-da-torre": 2000
        }
    ]
    files = {
        "file": ("empreendimentos.json", json.dumps(payload), "application/json")
    }
    resp = client.post("/validar", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["status"] == "Inválido"
    assert "Torres devem ter menos de 30m de altura" in data[0]["erros"]

def test_validar_rejeita_json_mal_formatado():
    # JSON propositalmente inválido (aspas simples e falta de aspas em chaves)
    bad_json = "{'construtora': 'X', area-do-terreno: 1000}"
    files = {
        "file": ("bad.json", bad_json, "application/json")
    }
    resp = client.post("/validar", files=files)
    # Se você adicionou o tratamento com HTTPException(400) para JSON inválido:
    assert resp.status_code == 400
    assert "JSON inválido" in resp.json()["detail"]
