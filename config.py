"""Configuração central. Nomes de modelo mudam — mantê-los num só lugar
evita ter que caçar strings soltas pelo código (lição do erro 404)."""

# Modelo usado pelo agente. Trocar aqui afeta o projeto inteiro.
MODEL = "gemini-3.1-flash-lite"

# Trava de segurança: nº máximo de idas ao modelo numa única execução.
# Sem isto, um agente pode entrar em loop infinito pedindo ferramentas
# para sempre (e queimando tokens). SEMPRE tenha um limite.
MAX_ITERATIONS = 10
