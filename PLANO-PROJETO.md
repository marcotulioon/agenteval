# Projeto de Portfólio: Agente de IA + Avaliação

**Objetivo:** um repositório público no GitHub com um agente de IA (tool-calling,
loop agêntico manual) e um pipeline de avaliação/observabilidade. Cobre os
requisitos que TODAS as vagas de AI Engineer pedem: *agentic workflows*,
*evaluation*, *observability (latency/cost)*, *test coverage / CI*.

**Meta dupla:**
1. Ter o repo + demo para linkar no CV e LinkedIn.
2. Você ENTENDER cada peça para explicar em entrevista sem IA do lado.

## O que vamos construir — "AgentEval"

Um agente que responde perguntas em linguagem natural que exigem dados ao vivo e
raciocínio em vários passos. Exemplo: *"Qual das 3 maiores cidades do Brasil está
mais fria agora e quantos graus abaixo da mais quente?"* — o agente precisa
geolocalizar, buscar clima de cada uma, comparar e calcular.

**Ferramentas do agente (APIs públicas gratuitas, sem chave):**
1. `geocode(cidade)` → latitude/longitude (Open-Meteo Geocoding)
2. `get_weather(lat, lon)` → clima atual e previsão (Open-Meteo)
3. `calculator(expr)` → cálculo seguro

**Por que impressiona em entrevista:**
- Loop agêntico MANUAL (mostra que você entende orquestração, não só "chamei o LangChain")
- Múltiplas ferramentas + raciocínio multi-passo
- APIs externas reais (nada de mock)
- Harness de avaliação: dataset de perguntas + verificações automáticas + LLM-as-judge; relatório com taxa de acerto, latência, custo em tokens, nº de tool calls
- Observabilidade: log de cada tool call, tokens e latência
- Testes (pytest) + CI (GitHub Actions rodando o eval como "gate")

## Fases (cada uma é uma etapa guiada)

- **Fase 0 — Setup:** conta GitHub, ambiente Python (uv), chave de API, repo criado
- **Fase 1 — Hello LLM:** 1 chamada à API; entender mensagens, roles, tokens
- **Fase 2 — Uma ferramenta + loop manual:** o coração do mecanismo agêntico
- **Fase 3 — Agente multi-ferramenta:** geocode + weather + calculadora
- **Fase 4 — Observabilidade:** log de tokens, latência e tool calls por execução
- **Fase 5 — Avaliação:** dataset + verificações automáticas + LLM-as-judge; relatório
- **Fase 6 — Testes + CI:** pytest + GitHub Actions com "eval gate"
- **Fase 7 — README + polish + push final**
- **Fase 8 (bônus) — API FastAPI + deploy público**

## Como cada fase funciona
1. Eu explico o conceito (o "porquê")
2. Escrevemos o código juntos
3. Você roda e vê funcionando
4. Eu te faço 1-2 perguntas para fixar (o que você diria em entrevista)

## Stack
- Python 3.11+ (via uv)
- SDK do provedor de LLM escolhido
- Loop agêntico manual (SEM LangChain — decisão deliberada)
- `httpx` para as APIs de clima
- `pytest` para testes
- GitHub Actions para CI

## Progresso
- [ ] Fase 0 — Setup
- [ ] Fase 1 — Hello LLM
- [ ] Fase 2 — Uma ferramenta + loop
- [ ] Fase 3 — Multi-ferramenta
- [ ] Fase 4 — Observabilidade
- [ ] Fase 5 — Avaliação
- [ ] Fase 6 — Testes + CI
- [ ] Fase 7 — README + push
- [ ] Fase 8 — Deploy (bônus)
