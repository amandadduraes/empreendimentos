from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def _merged_keys(resp_json):
    return [r["key"] for r in resp_json["merged_rules"]]

def _city_keys(resp_json):
    return [r["key"] for r in resp_json["city_rules"]]

def _builder_keys(resp_json):
    return [r["key"] for r in resp_json["builder_rules"]]

def test_rio_aplica_regras_1_e_2():
    r = client.get("/regras-aplicadas", params={"cidade": "Rio de Janeiro"})
    assert r.status_code == 200
    data = r.json()
    keys = _merged_keys(data)
    assert set(keys) == {"r1_altura<30", "r2_area_torres<80%_terreno"}
    assert data["default_city_rules"] is False

def test_sp_alpha_aplica_r2_r3_mais_regra_alpha():
    r = client.get("/regras-aplicadas", params={"cidade": "São Paulo", "construtora": "Alpha"})
    assert r.status_code == 200
    data = r.json()
    assert _merged_keys(data) == [
        "r2_area_torres<80%_terreno",
        "r3_lazer>=10%_se_varias_torres",
        "alpha_lazer>=10%_sempre",
    ]
    assert _city_keys(data) == [
        "r2_area_torres<80%_terreno",
        "r3_lazer>=10%_se_varias_torres",
    ]
    assert _builder_keys(data) == ["alpha_lazer>=10%_sempre"]
    assert data["default_city_rules"] is False

def test_guaratingueta_troca_regra_de_altura_por_especial():
    r = client.get("/regras-aplicadas", params={"cidade": "Guaratinguetá"})
    assert r.status_code == 200
    data = r.json()
    keys = _merged_keys(data)
    assert "guaratingueta_altura_por_torres" in keys
    assert "r1_altura<30" not in keys  # substitui a regra 1
    assert data["default_city_rules"] is False

def test_boituva_inclui_limite_de_5_torres():
    r = client.get("/regras-aplicadas", params={"cidade": "Boituva"})
    assert r.status_code == 200
    data = r.json()
    keys = _merged_keys(data)
    assert "boituva_max5_torres" in keys
    assert data["default_city_rules"] is False

def test_cidade_outra_usa_conjunto_padrao():
    r = client.get("/regras-aplicadas", params={"cidade": "Fortaleza"})
    assert r.status_code == 200
    data = r.json()
    assert _merged_keys(data) == [
        "r1_altura<30",
        "r2_area_torres<80%_terreno",
        "r3_lazer>=10%_se_varias_torres",
    ]
    assert data["default_city_rules"] is True

def test_normalizacao_acentos_sp():
    r1 = client.get("/regras-aplicadas", params={"cidade": "São Paulo"})
    r2 = client.get("/regras-aplicadas", params={"cidade": "Sao Paulo"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert _merged_keys(r1.json()) == _merged_keys(r2.json())

def test_builder_alpha_em_cidade_padrao_adiciona_regra():
    r = client.get("/regras-aplicadas", params={"cidade": "Fortaleza", "construtora": "Construtora Alpha"})
    assert r.status_code == 200
    data = r.json()
    keys = _merged_keys(data)
    assert keys == [
        "r1_altura<30",
        "r2_area_torres<80%_terreno",
        "r3_lazer>=10%_se_varias_torres",
        "alpha_lazer>=10%_sempre",
    ]
