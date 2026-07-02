# Lab TDC: AI Agents na OCI com RAG e Tools

Este projeto contem o material de apoio para um laboratorio de 1 hora sobre **AI Agents em Oracle Cloud Infrastructure**, usando:

- OCI Generative AI Agents;
- Object Storage;
- Knowledge Base com RAG;
- Custom Tool via API;
- endpoint do agente;
- programacao real do TDC Floripa 2026 como base de conhecimento.

O objetivo do lab e criar um agente chamado **Assistente TDC Floripa**, capaz de responder perguntas sobre o evento usando RAG e consultar dados estruturados de programacao usando uma tool.

## Entregaveis do repositorio

```text
assets/
  base_rag_tdc_floripa_2026.pdf         # Arquivo unico recomendado para upload no RAG
  programacao_tdc_floripa_2026.pdf      # PDF da programacao com trilhas, sessoes e speakers
  programacao_tdc_floripa_2026.md       # Versao Markdown para RAG
  programacao_tdc_floripa_2026.json     # Dataset usado pela tool
  tdc_floripa_2026_oficial.md           # Base curada do evento

tool/
  src/main.py                           # API da custom tool
  openapi/tdc-tool.openapi.yaml         # Contrato OpenAPI para OCI Generative AI Agents
  requirements.txt

scripts/
  build_tdc_program.py                  # Atualiza programacao a partir do site oficial
```

## Demo do lab

O agente responde perguntas como:

```text
Quando acontece o TDC Floripa 2026?
```

```text
Quais trilhas existem no dia 22 de julho?
```

```text
Quais palestras falam sobre agentes?
```

```text
Quais sessoes a speaker Ana Lindiner apresenta?
```

Perguntas sobre conceitos gerais, jornadas, formato, FAQ e regras usam **RAG**.

Perguntas sobre busca estruturada de sessoes, speakers, trilhas por dia e filtros usam **Custom Tool**.

## Arquitetura

```text
Usuario
  -> OCI Generative AI Agent endpoint
     -> RAG Tool
        -> Knowledge Base
        -> Object Storage
        -> assets/*.md e assets/*.pdf
     -> Custom Tool
        -> API publica
        -> assets/programacao_tdc_floripa_2026.json
```

## Pre-requisitos

- Conta OCI Trial ativa.
- Acesso ao OCI Console.
- Regiao com OCI Generative AI Agents disponivel.
- Permissao para criar compartment, policies, bucket, knowledge base, agent e endpoint.
- Python 3.11+ para rodar a tool localmente, caso queira testar antes de publicar.

## 1. Criar o compartment

1. Acesse o OCI Console.
2. Va em **Identity & Security**.
3. Clique em **Compartments**.
4. Clique em **Create compartment**.
5. Use:

```text
Name: tdc-ai-agents-lab
Description: Recursos do laboratorio TDC AI Agents OCI
```

6. Clique em **Create compartment**.

> INSERIR PRINT: tela de criacao do compartment.

## 2. Criar grupo e adicionar usuario

1. Va em **Identity & Security**.
2. Acesse **Domains**.
3. Entre no dominio usado pela sua conta.
4. Acesse **Groups**.
5. Crie um grupo:

```text
tdc-ai-agents-users
```

6. Adicione seu usuario ao grupo.

> INSERIR PRINT: grupo criado com usuario associado.

## 3. Criar policies do lab

Va em **Identity & Security > Policies** e crie uma policy no compartment raiz ou no compartment de administracao da tenancy.

Nome sugerido:

```text
tdc-ai-agents-lab-policy
```

Statements sugeridas para o lab:

```text
Allow group tdc-ai-agents-users to manage object-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to manage generative-ai-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to manage ai-service-generative-ai-agents-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to read compartments in tenancy
```

Observacao: os nomes exatos de resource-types podem variar conforme evolucao do servico. Se sua tenancy apresentar um exemplo oficial ou policy wizard, use a recomendacao da propria OCI.

> INSERIR PRINT: policy criada.

## 4. Criar bucket no Object Storage

1. Va em **Storage**.
2. Clique em **Buckets**.
3. Selecione o compartment `tdc-ai-agents-lab`.
4. Clique em **Create bucket**.
5. Use:

```text
Bucket name: tdc-agent-kb
```

6. Mantenha as demais opcoes padrao.
7. Clique em **Create**.

> INSERIR PRINT: bucket criado.

## 5. Subir arquivo para RAG

No bucket `tdc-agent-kb`, faca upload dos arquivos:

```text
assets/base_rag_tdc_floripa_2026.pdf
```

Esse PDF unico contem a base sobre o evento, FAQ, jornadas e programacao coletada do site oficial. O arquivo `programacao_tdc_floripa_2026.json` fica reservado para a custom tool.

> INSERIR PRINT: upload dos arquivos no bucket.

## 6. Criar Knowledge Base

1. Va em **Analytics & AI**.
2. Acesse **Generative AI Agents**.
3. Clique em **Knowledge Bases**.
4. Clique em **Create knowledge base**.
5. Nome sugerido:

```text
tdc-floripa-2026-kb
```

6. Escolha Object Storage como origem.
7. Selecione o bucket `tdc-agent-kb`.
8. Selecione os arquivos enviados.
9. Crie a knowledge base.
10. Aguarde a ingestao finalizar.

> INSERIR PRINT: knowledge base criada e ativa.

## 7. Criar o agente

1. Em **Generative AI Agents**, clique em **Agents**.
2. Clique em **Create agent**.
3. Nome:

```text
Assistente TDC Floripa
```

4. Welcome message:

```text
Ola! Sou o Assistente TDC Floripa. Posso responder perguntas sobre o TDC Floripa 2026, trilhas, jornadas, speakers e programacao.
```

5. Instrucoes do agente:

```text
Voce e o Assistente TDC Floripa, um agente para orientar participantes sobre o TDC Floripa 2026.
Responda em portugues brasileiro, de forma clara, objetiva e educada.
Use a base de conhecimento para perguntas sobre o evento, jornadas, formato, FAQ, regras, trilhas e programacao.
Use a tool de programacao quando a pergunta pedir busca por dia, trilha, speaker, termo ou sessao especifica.
Quando uma informacao puder mudar, informe que a fonte oficial deve ser consultada.
Nao invente horarios, speakers, valores ou regras que nao estejam na base ou na resposta da tool.
```

> INSERIR PRINT: tela de criacao do agente.

## 8. Adicionar RAG Tool

1. Na etapa de tools, clique em **Add tool**.
2. Escolha **RAG**.
3. Nome:

```text
consulta_base_tdc
```

4. Descricao:

```text
Use esta ferramenta para responder perguntas sobre o TDC Floripa 2026, incluindo formato do evento, jornadas, FAQ, inscricoes, modalidades, trilhas e programacao oficial. Responda com base nos documentos recuperados e cite a fonte quando disponivel.
```

5. Selecione a knowledge base `tdc-floripa-2026-kb`.
6. Adicione a tool.

> INSERIR PRINT: RAG tool adicionada.

## 9. Preparar a Custom Tool

A custom tool deste projeto fica em:

```text
tool/
```

Ela expoe uma API com:

- `GET /event`
- `GET /tracks`
- `GET /sessions`
- `GET /speakers`

Para testar localmente:

```bash
cd tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8080
```

Testes:

```bash
curl http://127.0.0.1:8080/event
curl "http://127.0.0.1:8080/tracks?day=22/jul"
curl "http://127.0.0.1:8080/sessions?q=agentic&limit=5"
curl "http://127.0.0.1:8080/speakers?q=ana"
```

Para usar no OCI Generative AI Agents, publique essa API em um endpoint acessivel pela OCI. Opcoes:

- OCI Functions + API Gateway;
- Compute pequena;
- Container Instance;
- outro endpoint HTTPS publico para fins de demo.

Depois, edite:

```text
tool/openapi/tdc-tool.openapi.yaml
```

Substitua:

```text
https://SEU_ENDPOINT_PUBLICO
```

pelo endpoint real.

> INSERIR PRINT: API/tool publicada ou teste local.

## 10. Adicionar Custom Tool no agente

1. Volte ao agente.
2. Clique em **Add tool**.
3. Escolha **Custom tool**.
4. Use o OpenAPI:

```text
tool/openapi/tdc-tool.openapi.yaml
```

5. Nome sugerido:

```text
consulta_programacao_tdc
```

6. Descricao:

```text
Use esta ferramenta para buscar sessoes, speakers, trilhas por dia e detalhes estruturados da programacao do TDC Floripa 2026.
```

7. Salve a tool.

> INSERIR PRINT: custom tool adicionada.

## 11. Criar endpoint do agente

1. Na etapa de endpoint, mantenha a criacao automatica ativada.
2. Deixe guardrails desativados para o lab ou mostre rapidamente as opcoes.
3. Crie o agente.
4. Aguarde status **Active**.

> INSERIR PRINT: endpoint ativo.

## 12. Testar no chat

Perguntas para testar RAG:

```text
Quando acontece o TDC Floripa 2026?
```

```text
O que sao as Jornadas TDC?
```

```text
O evento e presencial ou online?
```

Perguntas para testar tool:

```text
Quais trilhas existem no dia 22/jul?
```

```text
Busque sessoes sobre agentes.
```

```text
Quais sessoes a Ana Lindiner apresenta?
```

Pergunta para discutir limite entre RAG e tool:

```text
Qual e o link oficial de inscricao?
```

> INSERIR PRINT: chat respondendo com RAG.

> INSERIR PRINT: trace mostrando uso da tool.

## 13. Demonstrar endpoint

Explique a diferenca:

- Console chat: valida comportamento.
- Agent endpoint: integra com aplicacao real.
- Custom tool: conecta o agente a dados vivos ou estruturados.

Mensagem para o publico:

```text
O chat prova que o agente funciona. O endpoint prova que ele pode virar produto.
```

> INSERIR PRINT: tela do endpoint do agente.

## Atualizar programacao antes do evento

Para atualizar a programacao a partir do site oficial:

```bash
python3 scripts/build_tdc_program.py assets
```

Isso regenera:

```text
assets/programacao_tdc_floripa_2026.json
assets/programacao_tdc_floripa_2026.md
assets/programacao_tdc_floripa_2026.pdf
```

Depois regenere tambem o PDF unico do RAG:

```bash
python3 scripts/build_rag_pdf.py
```

## Limpeza dos recursos

Ao final do lab, remova:

- agent endpoint;
- agent;
- knowledge base;
- objetos do bucket;
- bucket;
- API/tool publicada;
- policies e compartment, se forem descartaveis.

## Fontes

- https://thedevconf.com/tdc/2026/florianopolis/
- https://thedevconf.com/tdc/2026/florianopolis/jornadas/
