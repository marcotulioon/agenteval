"""
O agente: o loop agêntico manual.

A ideia central (o que faz disto um "agente"):
  - Mandamos a pergunta do usuário + a lista de ferramentas disponíveis.
  - O modelo responde de UMA de duas formas:
      (a) um texto final  -> terminamos, devolvemos a resposta; ou
      (b) um pedido de ferramenta (function_call) -> NÓS executamos a função,
          devolvemos o resultado, e chamamos o modelo de novo.
  - Repetimos até o modelo dar a resposta final (ou batermos no limite).

Fazemos isso À MÃO de propósito (sem LangChain) para você entender e
explicar o mecanismo. Rode com:  uv run python agent.py
"""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MAX_ITERATIONS, MODEL
from tools import SCHEMAS, TOOLS

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Monta o objeto de ferramentas que o Gemini entende, a partir dos schemas.
_TOOLS_CONFIG = types.Tool(
    function_declarations=[types.FunctionDeclaration(**s) for s in SCHEMAS]
)

SYSTEM = (
    "Você é um assistente que resolve problemas usando as ferramentas disponíveis. "
    "Quando precisar calcular algo, USE a ferramenta calculator em vez de fazer "
    "a conta de cabeça. Responda em português, de forma direta."
)


def _chamar_modelo(contents):
    """Chama o modelo com retry simples — chamadas de LLM falham de forma
    transitória (lembra do erro 503?). Produção precisa disto."""
    config = types.GenerateContentConfig(
        tools=[_TOOLS_CONFIG],
        system_instruction=SYSTEM,
        # Desligamos a execução automática de funções DE PROPÓSITO:
        # queremos rodar o loop nós mesmos para aprender/mostrar o mecanismo.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    for tentativa in range(3):
        try:
            return client.models.generate_content(
                model=MODEL, contents=contents, config=config
            )
        except Exception as e:
            if tentativa == 2:
                raise
            print(f"  [retry] chamada falhou ({e}); tentando de novo...")
            time.sleep(2 * (tentativa + 1))  # backoff: 2s, 4s


def executar_agente(pergunta: str) -> str:
    """Roda o loop agêntico para uma pergunta e devolve a resposta final."""
    # O histórico começa com a mensagem do usuário.
    contents = [types.Content(role="user", parts=[types.Part(text=pergunta)])]

    for iteracao in range(1, MAX_ITERATIONS + 1):
        resposta = _chamar_modelo(contents)
        parte_conteudo = resposta.candidates[0].content

        # O modelo pediu alguma ferramenta?
        chamadas = [p.function_call for p in parte_conteudo.parts if p.function_call]

        if not chamadas:
            # Sem pedido de ferramenta => é a resposta final.
            return resposta.text

        # Guardamos no histórico o que o MODELO disse (o pedido de ferramenta).
        contents.append(parte_conteudo)

        # Executamos cada ferramenta pedida e coletamos os resultados.
        partes_resultado = []
        for fc in chamadas:
            nome = fc.name
            args = dict(fc.args)
            print(f"  [tool] modelo pediu: {nome}({args})")
            funcao = TOOLS[nome]
            resultado = funcao(**args)
            print(f"  [tool] resultado: {resultado}")
            partes_resultado.append(
                types.Part.from_function_response(
                    name=nome, response={"result": resultado}
                )
            )

        # Devolvemos os resultados ao modelo (role 'tool') e o loop continua.
        contents.append(types.Content(role="tool", parts=partes_resultado))

    return "[limite de iterações atingido sem resposta final]"


if __name__ == "__main__":
    pergunta = (
        "Das 3 maiores cidades do Brasil (São Paulo, Rio de Janeiro e Brasília), "
        "qual está mais fria agora e quantos graus abaixo da mais quente ela está?"
    )
    print("=" * 60)
    print(f"PERGUNTA: {pergunta}")
    print("-" * 60)
    resposta = executar_agente(pergunta)
    print("-" * 60)
    print(f"RESPOSTA FINAL: {resposta}")
    print("=" * 60)
