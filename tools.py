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

# Mapa que liga o NOME (que o modelo devolve) à FUNÇÃO real (que executamos).
TOOLS = {
    "calculator": calculator,
}

SCHEMAS = [CALCULATOR_SCHEMA]
