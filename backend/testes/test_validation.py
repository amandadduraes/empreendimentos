import pytest
from app import validar_empreendimento

def test_altura_deve_ser_menor_que_30():
    emp = {
        "area-do-terreno": 1000,
        "numero-de-torres": 1,
        "altura-da-torre": 30,  
        "area-da-torre": 100
    }
    erros = validar_empreendimento(emp)
    assert "Torres devem ter menos de 30m de altura" in erros

def test_area_total_torres_deve_ser_menor_que_80_porcento_terreno():
    emp = {
        "area-do-terreno": 1000,
        "numero-de-torres": 2,
        "altura-da-torre": 20,
        "area-da-torre": 400  
    }
    erros = validar_empreendimento(emp)
    assert "Área total das torres deve ser inferior a 80% da área do terreno" in erros

def test_area_de_lazer_obrigatoria_para_mais_de_uma_torre():
    emp = {
        "area-do-terreno": 1000,
        "numero-de-torres": 2,  
        "altura-da-torre": 20,
        "area-da-torre": 200
    }
    erros = validar_empreendimento(emp)
    assert "Precisa de área de lazer" in erros

def test_area_de_lazer_deve_ser_pelo_menos_10_porcento_terreno():
    emp = {
        "area-do-terreno": 1000,
        "numero-de-torres": 2,
        "altura-da-torre": 20,
        "area-da-torre": 200,
        "area-de-lazer": 90 
    }
    erros = validar_empreendimento(emp)
    assert "Área de lazer deve ser >= 10% da área do terreno" in erros

def test_empreendimento_valido_nao_retorna_erros():
    emp = {
        "area-do-terreno": 10000,
        "numero-de-torres": 2,
        "altura-da-torre": 25,
        "area-da-torre": 3000,  
        "area-de-lazer": 1200   
    }
    erros = validar_empreendimento(emp)
    assert erros == []


def test_rio_aplica_apenas_regras_1_e_2():
    emp = {
        "construtora": "X",
        "cidade": "Rio de Janeiro",
        "area-do-terreno": 10000,
        "numero-de-torres": 2,
        "altura-da-torre": 20,   
        "area-da-torre": 3000   
    }
    erros = validar_empreendimento(emp)
    assert erros == [] 

def test_rio_ainda_valida_altura_e_area_total():
    emp = {
        "construtora": "Y",
        "cidade": "Rio de Janeiro",
        "area-do-terreno": 8000,
        "numero-de-torres": 3,
        "altura-da-torre": 32,   
        "area-da-torre": 2500    
    }
    erros = validar_empreendimento(emp)
    assert "Torres devem ter menos de 30m de altura" in erros
    assert "Área total das torres deve ser inferior a 80% da área do terreno" in erros

def test_sao_paulo_aplica_regras_2_e_3_nao_aplica_1():
    emp = {
        "construtora": "Z",
        "cidade": "São Paulo",
        "area-do-terreno": 6000,
        "numero-de-torres": 2,
        "altura-da-torre": 35, 
        "area-da-torre": 3000,  
        "area-de-lazer": 200    
    }
    erros = validar_empreendimento(emp)
    assert "Torres devem ter menos de 30m de altura" not in erros
    assert "Área total das torres deve ser inferior a 80% da área do terreno" in erros
    assert "Área de lazer deve ser >= 10% da área do terreno" in erros

def test_outras_cidades_aplicam_todas_as_regras():
    emp = {
        "construtora": "W",
        "cidade": "Fortaleza",
        "area-do-terreno": 4000,
        "numero-de-torres": 2,
        "altura-da-torre": 31,   
        "area-da-torre": 2000,   
    }
    erros = validar_empreendimento(emp)
    assert "Torres devem ter menos de 30m de altura" in erros
    assert "Área total das torres deve ser inferior a 80% da área do terreno" in erros
    assert "Precisa de área de lazer" in erros

def test_boituva_limite_5_torres():
    emp = {
        "construtora": "Qualquer",
        "cidade": "Boituva",
        "area-do-terreno": 10000,
        "numero-de-torres": 6,  # >5
        "altura-da-torre": 20,
        "area-da-torre": 1000,
        "area-de-lazer": 1200,
    }
    erros = validar_empreendimento(emp)
    assert "Boituva: não pode haver mais de 5 torres no terreno" in erros

def test_guaratingueta_altura_por_torres():
    emp = {
        "construtora": "Qualquer",
        "cidade": "Guaratinguetá",
        "area-do-terreno": 9000,
        "numero-de-torres": 4,  
        "altura-da-torre": 18,
        "area-da-torre": 1000,
        "area-de-lazer": 1000,
    }
    erros = validar_empreendimento(emp)
    assert any("Guaratinguetá: para 4 torres" in e for e in erros)

def test_alpha_semper_lazer():
    emp = {
        "construtora": "Alpha",
        "cidade": "São Paulo",
        "area-do-terreno": 7000,
        "numero-de-torres": 1,
        "altura-da-torre": 29,
        "area-da-torre": 2000,
    }
    erros = validar_empreendimento(emp)
    assert "Alpha: precisa de área de lazer (sempre)" in erros
