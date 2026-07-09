"""
Fase 1 — Hello LLM.

Objetivo de aprendizado: fazer UMA chamada ao modelo e entender três coisas
que você precisa saber explicar em entrevista:
  1. Como se conecta e chama um LLM por código (não por curl).
  2. A estrutura de uma conversa: mensagens com "roles" (user / model).
  3. Tokens — a unidade que o modelo lê/escreve e que vira CUSTO.

Rode com:  uv run python hello_llm.py
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1) Carrega o .env para dentro das variáveis de ambiente do processo.
#    A chave NUNCA fica escrita no código — vem do .env (que o git ignora).
load_dotenv()

# 2) Cria o cliente. Ele lê a variável GEMINI_API_KEY automaticamente,
#    mas passamos explícito para deixar claro de onde vem.
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.1-flash-lite"

# 3) A "conversa" é uma lista de mensagens. Cada mensagem tem um ROLE:
#    - "user"  = o que nós dizemos ao modelo
#    - "model" = o que o modelo respondeu (em conversas de vários turnos)
#    Aqui é um turno só, então mandamos apenas uma mensagem de user.
pergunta = "Explique em uma frase o que é um token em um LLM."

resposta = client.models.generate_content(
    model=MODEL,
    contents=pergunta,
    # system_instruction define o "papel"/comportamento do assistente.
    config=types.GenerateContentConfig(
        system_instruction="Você é um professor didático. Responda em português, curto.",
    ),
)

# 4) O texto gerado:
print("=" * 60)
print("RESPOSTA DO MODELO:")
print(resposta.text)

# 5) Tokens = custo. Toda resposta traz um 'usage_metadata' com a contagem.
#    input  = o que ENVIAMOS (pergunta + system_instruction)
#    output = o que o modelo GEROU
u = resposta.usage_metadata
print("=" * 60)
print("TOKENS (isto é o que você paga):")
print(f"  input  (prompt):     {u.prompt_token_count}")
print(f"  output (resposta):   {u.candidates_token_count}")
print(f"  total:               {u.total_token_count}")
print("=" * 60)
