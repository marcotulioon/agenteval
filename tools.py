"""
Ferramentas que o agente pode chamar.

Cada ferramenta tem DUAS partes:
  1. A função Python real (o que EXECUTA).
  2. Um "schema" que descreve a função para o modelo (nome, o que faz,
     quais argumentos). O modelo lê o schema para decidir quando e como chamar.

Começamos com uma calculadora. Ela é determinística e não depende de rede —
perfeita para aprender o mecanismo antes de adicionar APIs externas (Fase 3).
"""

import ast
import operator

import httpx

# --- 1. A função real ------------------------------------------------------

# Por que NÃO usar eval()? Porque eval() executa QUALQUER código Python —
# um modelo (ou um usuário malicioso) poderia mandar algo como
# "__import__('os').system('rm -rf ~')". Em vez disso, usamos o módulo `ast`
# para interpretar SÓ expressões aritméticas. (Ótima resposta de entrevista:
# "por que você não usou eval?")

_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _avaliar(no):
    """Avalia recursivamente um nó da árvore sintática, só com números e operadores."""
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return no.value
    if isinstance(no, ast.BinOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.left), _avaliar(no.right))
    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPERADORES:
        return _OPERADORES[type(no.op)](_avaliar(no.operand))
    raise ValueError("Expressão não permitida")


def calculator(expression: str) -> str:
    """Calcula uma expressão aritmética simples e devolve o resultado como texto."""
    try:
        arvore = ast.parse(expression, mode="eval")
        resultado = _avaliar(arvore.body)
        return str(resultado)
    except Exception as e:
        # Devolver o erro como texto deixa o MODELO decidir o que fazer
        # (tentar de novo, pedir esclarecimento). Não derrubamos o agente.
        return f"Erro ao calcular '{expression}': {e}"


# --- 2. O schema (como o modelo enxerga a ferramenta) ----------------------
# Formato de "function declaration" que o Gemini entende.
CALCULATOR_SCHEMA = {
    "name": "calculator",
    "description": (
        "Calcula o resultado de uma expressão aritmética "
        "(ex: '2 + 2', '15 * 3.5', '(100 - 20) / 4')."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A expressão aritmética a calcular, ex: '2 + 2'.",
            }
        },
        "required": ["expression"],
    },
}

# --- 3. Ferramentas de rede: geocode + get_weather (Fase 3) ----------------
# Estas tocam APIs externas reais (Open-Meteo, gratuitas e SEM chave). Duas
# lições de produção aqui:
#   (a) Chamadas de rede FALHAM (timeout, 404, API fora). Capturamos o erro e
#       devolvemos como DADO — nunca derrubamos o agente. O MODELO decide o
#       que fazer com o erro (tentar de novo, pedir esclarecimento).
#   (b) get_weather depende do resultado de geocode (precisa de lat/lon). O
#       modelo tem que ENCADEAR as chamadas — é o raciocínio multi-passo real.

_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT = 10.0  # SEMPRE ponha timeout em chamada de rede; sem isto o agente trava.


def geocode(city: str) -> dict:
    """Converte o nome de uma cidade em latitude/longitude (Open-Meteo Geocoding)."""
    try:
        resp = httpx.get(
            _GEOCODE_URL,
            params={"name": city, "count": 1, "language": "pt", "format": "json"},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        dados = resp.json()
    except Exception as e:
        return {"erro": f"Falha ao geocodificar '{city}': {e}"}

    resultados = dados.get("results")
    if not resultados:
        return {"erro": f"Cidade não encontrada: '{city}'"}

    r = resultados[0]
    return {
        "cidade": r.get("name"),
        "pais": r.get("country"),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
    }


def get_weather(latitude: float, longitude: float) -> dict:
    """Busca o clima atual para uma coordenada (Open-Meteo Forecast)."""
    try:
        resp = httpx.get(
            _WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        dados = resp.json()
    except Exception as e:
        return {"erro": f"Falha ao buscar clima ({latitude},{longitude}): {e}"}

    atual = dados.get("current", {})
    unidades = dados.get("current_units", {})
    return {
        "temperatura": atual.get("temperature_2m"),
        "unidade_temp": unidades.get("temperature_2m", "°C"),
        "umidade": atual.get("relative_humidity_2m"),
        "vento": atual.get("wind_speed_10m"),
    }


GEOCODE_SCHEMA = {
    "name": "geocode",
    "description": (
        "Converte o nome de uma cidade em coordenadas (latitude e longitude). "
        "Use ANTES de get_weather, que exige coordenadas."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Nome da cidade, ex: 'São Paulo'.",
            }
        },
        "required": ["city"],
    },
}

GET_WEATHER_SCHEMA = {
    "name": "get_weather",
    "description": (
        "Retorna o clima atual (temperatura em °C, umidade, vento) de uma "
        "latitude/longitude. Obtenha as coordenadas com geocode primeiro."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number", "description": "Latitude da localização."},
            "longitude": {"type": "number", "description": "Longitude da localização."},
        },
        "required": ["latitude", "longitude"],
    },
}

# Mapa que liga o NOME (que o modelo devolve) à FUNÇÃO real (que executamos).
TOOLS = {
    "calculator": calculator,
    "geocode": geocode,
    "get_weather": get_weather,
}

SCHEMAS = [CALCULATOR_SCHEMA, GEOCODE_SCHEMA, GET_WEATHER_SCHEMA]
