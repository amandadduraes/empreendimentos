from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import unicodedata
from typing import Optional, List, Dict, Callable
from pydantic import BaseModel

CITY_RULES = {
    "rio de janeiro": {1, 2},
    "sao paulo": {2, 3},  # sem acento para normalizar
}



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _norm(text: str) -> str:
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text.lower())
        if not unicodedata.combining(c)
    ).strip()

class Rule:
    """Interface simples para uma regra."""
    key: str
    description: str
    def validate(self, emp: dict) -> Optional[str]:
        raise NotImplementedError
    
class RegraAlturaMenor30(Rule):
    key = "r1_altura<30"
    description = "Torres devem ter menos de 30m de altura"
    def validate(self, emp: dict) -> Optional[str]:
        if emp["altura-da-torre"] >= 30:
            return "Torres devem ter menos de 30m de altura"
        return None

class RegraAreaTorresMenor80(Rule):
    key = "r2_area_torres<80%_terreno"
    description = "Área total das torres < 80% da área do terreno"
    def validate(self, emp: dict) -> Optional[str]:
        total = emp["numero-de-torres"] * emp["area-da-torre"]
        if total >= 0.8 * emp["area-do-terreno"]:
            return "Área total das torres deve ser inferior a 80% da área do terreno"
        return None

class RegraAreaLazerQuandoVarias(Rule):
    key = "r3_lazer>=10%_se_varias_torres"
    description = "Se >1 torre, exigir área de lazer >=10% do terreno"
    def validate(self, emp: dict) -> Optional[str]:
        if emp["numero-de-torres"] > 1:
            if "area-de-lazer" not in emp:
                return "Precisa de área de lazer"
            if emp["area-de-lazer"] < 0.1 * emp["area-do-terreno"]:
                return "Área de lazer deve ser >= 10% da área do terreno"
        return None

class RegraBoituvaMax5Torres(Rule):
    key = "boituva_max5_torres"
    description = "Boituva: no máximo 5 torres"
    def validate(self, emp: dict) -> Optional[str]:
        if _norm(emp.get("cidade")) == "boituva" and emp["numero-de-torres"] > 5:
            return "Boituva: não pode haver mais de 5 torres no terreno"
        return None

class RegraGuaratinguetaAlturaPorTorres(Rule):
    key = "guaratingueta_altura_por_torres"
    description = "Guaratinguetá: altura máxima depende do nº de torres"
    def validate(self, emp: dict) -> Optional[str]:
        if _norm(emp.get("cidade")) != "guaratingueta":
            return None
        n = emp["numero-de-torres"]
        if n <= 2:
            limite = 25
        elif n == 3:
            limite = 20
        else:
            limite = 15
        if emp["altura-da-torre"] > limite:
            return f"Guaratinguetá: para {n} torres, altura máxima é {limite}m"
        return None
    
class RegraAlphaLazerSempre(Rule):
    key = "alpha_lazer>=10%_sempre"
    description = "Alpha: sempre possui área de lazer >=10% do terreno"
    def validate(self, emp: dict) -> Optional[str]:
        if _norm(emp.get("construtora")) != "construtora alpha" and _norm(emp.get("construtora")) != "alpha":
            return None
        if "area-de-lazer" not in emp:
            return "Alpha: precisa de área de lazer (sempre)"
        if emp["area-de-lazer"] < 0.1 * emp["area-do-terreno"]:
            return "Alpha: área de lazer deve ser >= 10% da área do terreno"
        return None
    
ALL_RULES: Dict[str, Rule] = {
    RegraAlturaMenor30.key: RegraAlturaMenor30(),
    RegraAreaTorresMenor80.key: RegraAreaTorresMenor80(),
    RegraAreaLazerQuandoVarias.key: RegraAreaLazerQuandoVarias(),
    RegraBoituvaMax5Torres.key: RegraBoituvaMax5Torres(),
    RegraGuaratinguetaAlturaPorTorres.key: RegraGuaratinguetaAlturaPorTorres(),
    RegraAlphaLazerSempre.key: RegraAlphaLazerSempre(),
}


CITY_RULE_SETS: Dict[str, List[str]] = {
    # do enunciado anterior:
    "rio de janeiro": [RegraAlturaMenor30.key, RegraAreaTorresMenor80.key],
    "sao paulo": [RegraAreaTorresMenor80.key, RegraAreaLazerQuandoVarias.key],
    # novas
    "boituva": [
        RegraAlturaMenor30.key,
        RegraAreaTorresMenor80.key,
        RegraAreaLazerQuandoVarias.key,
        RegraBoituvaMax5Torres.key,
    ],
     "guaratingueta": [
        RegraGuaratinguetaAlturaPorTorres.key,
        RegraAreaTorresMenor80.key,
        RegraAreaLazerQuandoVarias.key,
    ],
}

BUILDER_RULE_SETS: Dict[str, List[str]] = {
    "alpha": [RegraAlphaLazerSempre.key],
    "construtora alpha": [RegraAlphaLazerSempre.key],
}

DEFAULT_RULE_KEYS = [
    RegraAlturaMenor30.key,
    RegraAreaTorresMenor80.key,
    RegraAreaLazerQuandoVarias.key,
]

def _rules_for(emp: dict) -> List[Rule]:
    city = _norm(emp.get("cidade"))
    builder = _norm(emp.get("construtora"))
    keys = list(CITY_RULE_SETS.get(city, DEFAULT_RULE_KEYS))
    for k in BUILDER_RULE_SETS.get(builder, []):
        if k not in keys:
            keys.append(k)
    return [ALL_RULES[k] for k in keys]

def _normalize_city(name: str) -> str:
    if not name:
        return ""
    # remove acentos e transforma em minúsculas
    return "".join(
        c for c in unicodedata.normalize("NFKD", name.lower())
        if not unicodedata.combining(c)
    ).strip()

def validar_empreendimento(emp: dict) -> List[str]:
    """Executa o conjunto de regras aplicável à cidade e construtora."""
    erros: List[str] = []
    for rule in _rules_for(emp):
        msg = rule.validate(emp)
        if msg:
            erros.append(msg)
    return erros

class RegraInfo(BaseModel):
    key: str
    description: str

class RegrasAplicadasOut(BaseModel):
    cidade: Optional[str] = None
    construtora: Optional[str] = None
    default_city_rules: bool
    city_rules: List[RegraInfo]
    builder_rules: List[RegraInfo]
    merged_rules: List[RegraInfo]   # união na ordem: cidade -> construtora (sem duplicar)

def _rules_keys_for(cidade: Optional[str], construtora: Optional[str]):
    city_key = _norm(cidade or "")
    builder_key = _norm(construtora or "")
    city_keys = CITY_RULE_SETS.get(city_key, DEFAULT_RULE_KEYS)
    builder_keys = BUILDER_RULE_SETS.get(builder_key, [])
    # mescla mantendo ordem e sem duplicar
    merged = list(city_keys) + [k for k in builder_keys if k not in city_keys]
    return city_keys, builder_keys, merged, (city_key not in CITY_RULE_SETS)

def _keys_to_infos(keys: List[str]) -> List[RegraInfo]:
    return [RegraInfo(key=k, description=ALL_RULES[k].description) for k in keys]

# ---------- NOVO ENDPOINT ----------
@app.get("/regras-aplicadas", response_model=RegrasAplicadasOut)
def regras_aplicadas(cidade: Optional[str] = None, construtora: Optional[str] = None):
    """
    Exibe quais regras serão aplicadas para a combinação informada.
    - Se `cidade` não estiver no mapa, usa o conjunto padrão (r1, r2, r3).
    - As regras da `construtora` são somadas às da cidade (sem duplicar).
    """
    city_keys, builder_keys, merged_keys, default_used = _rules_keys_for(cidade, construtora)
    return RegrasAplicadasOut(
        cidade=cidade,
        construtora=construtora,
        default_city_rules=default_used,
        city_rules=_keys_to_infos(city_keys),
        builder_rules=_keys_to_infos(builder_keys),
        merged_rules=_keys_to_infos(merged_keys),
    )

@app.get("/regras-opcoes")
def regras_opcoes():
    return {
        "cidades": sorted(CITY_RULE_SETS.keys()),
        "construtoras": sorted(BUILDER_RULE_SETS.keys()),  # <— aqui estava o typo
    }
@app.post("/validar")
async def validar(file: UploadFile = File(...)):
    content = await file.read()
    try:
        dados = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"JSON inválido: {e.msg} (linha {e.lineno}, coluna {e.colno})"
        )
    if not isinstance(dados, list):
        raise HTTPException(status_code=400, detail="O JSON deve ser uma lista de empreendimentos.")

    resultados = []
    for emp in dados:
        erros = validar_empreendimento(emp)
        resultados.append({
            "construtora": emp.get("construtora"),
            "cidade": emp.get("cidade"),
            "status": "Válido" if not erros else "Inválido",
            "erros": erros
        })
    return resultados
