# TDC Floripa 2026 Tool API

Esta API e a custom tool usada no lab para mostrar que o agente pode consultar dados estruturados em tempo de execucao.

Ela le o arquivo:

```text
assets/programacao_tdc_floripa_2026.json
```

## Rodar localmente

```bash
cd tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8080
```

Teste:

```bash
curl http://127.0.0.1:8080/health
curl "http://127.0.0.1:8080/sessions?q=agentic&limit=5"
curl "http://127.0.0.1:8080/tracks?day=22/jul"
```

## Endpoints

- `GET /event`: informacoes gerais do evento.
- `GET /tracks`: trilhas, opcionalmente por dia.
- `GET /sessions`: busca sessoes por dia, trilha ou termo.
- `GET /speakers`: busca speakers e sessoes.

## OpenAPI para OCI Generative AI Agents

Use o arquivo:

```text
tool/openapi/tdc-tool.openapi.yaml
```

Antes de cadastrar a custom tool, substitua:

```text
https://SEU_ENDPOINT_PUBLICO
```

pelo endpoint publico da sua API.
