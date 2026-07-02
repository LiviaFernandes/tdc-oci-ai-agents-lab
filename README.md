# Lab TDC: AI Agents na OCI com RAG e Tools

Este projeto contem o material de apoio para um laboratorio de 1 hora sobre **AI Agents em Oracle Cloud Infrastructure**, usando:

- OCI Generative AI Agents;
- Object Storage;
- Knowledge Base com RAG;
- Custom Tool via API publica ja preparada;
- endpoint do agente;
- programacao real do TDC Floripa 2026 como dataset estruturado da tool.

O objetivo do lab e criar um agente chamado **Assistente TDC Floripa**, capaz de responder perguntas gerais sobre o evento usando RAG e consultar programacao, horarios, sessoes e speakers usando uma tool.


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


Perguntas sobre conceitos gerais, jornadas, formato, FAQ e regras usam **RAG** porque estao no PDF.

Perguntas sobre busca estruturada de sessoes, speakers, trilhas por dia e filtros usam **Custom Tool** porque dependem do JSON.

## Arquitetura

```text
Usuario
  -> OCI Generative AI Agent endpoint
     -> RAG Tool
        -> Knowledge Base
        -> Object Storage
        -> assets/base_rag_tdc_floripa_2026.pdf
     -> Custom Tool
        -> API publica de busca
        -> api/server.js
        -> assets/programacao_tdc_floripa_2026.json
```

## Pre-requisitos

- Conta OCI Trial ativa.
- Acesso ao OCI Console.
- Regiao com OCI Generative AI Agents disponivel.
- Permissao para criar compartment, policies, rede, bucket, knowledge base, agent e endpoint.
- Acesso a internet para o agente consultar a API publica da programacao.

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

> <img width="1470" height="776" alt="image" src="https://github.com/user-attachments/assets/b48c1ffe-83d6-45fe-9557-2bd3060f6a6f" />


## 2. Criar grupo e adicionar usuario

1. Va em **Identity & Security**.
2. Acesse **Domains**.
3. Entre no dominio default no compartment root.
4. Acesse **Groups**.
5. Crie um grupo:
   <img width="1161" height="247" alt="image" src="https://github.com/user-attachments/assets/a9ae3208-db9f-4bcf-aa95-f47e627df6c5" />

6. Utilize o seguinte name para o grupo
```text
tdc-ai-agents-users
```

7. Adicione seu usuario ao grupo e clique em create.

<img width="1466" height="829" alt="image" src="https://github.com/user-attachments/assets/2ad7d490-099a-4f4b-a0d2-447342503eed" />

## 3. Criar policies do lab

Va em **Identity & Security > Policies** e crie uma policy no compartment root

Nome sugerido:

```text
tdc-ai-agents-lab-policy
```

Statements sugeridas para o lab:

```text
Allow group tdc-ai-agents-users to manage object-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to manage virtual-network-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to manage generative-ai-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to manage ai-service-generative-ai-agents-family in compartment tdc-ai-agents-lab
Allow group tdc-ai-agents-users to read compartments in tenancy
```
<img width="1466" height="829" alt="image" src="https://github.com/user-attachments/assets/78e3c250-9211-4928-9a0b-aa38e7bae3a6" />


## 4. Criar rede para a Custom Tool

A Custom Tool precisa de uma VCN e de uma subnet para fazer chamadas HTTPS externas. Para o lab, use uma rede simples criada pelo wizard da OCI.

1. Va em **Networking > Virtual cloud networks**.
2. Selecione o compartment `tdc-ai-agents-lab`.
3. Clique em **Start VCN Wizard**.
  <img width="1470" height="831" alt="image" src="https://github.com/user-attachments/assets/0073e861-2ec1-4102-a005-6ff4fd45c9b2" />

4. Escolha **Create VCN with Internet Connectivity**.
5. Use:

```text
VCN name: tdc-ai-agents-vcn
Compartment: tdc-ai-agents-lab
VCN CIDR block: 10.0.0.0/16
Public subnet CIDR block: 10.0.0.0/24
Private subnet CIDR block: 10.0.1.0/24
```

6. Clique em **Next**.
7. Revise os recursos que serao criados.
8. Clique em **Create**.
 <img width="1470" height="842" alt="image" src="https://github.com/user-attachments/assets/86f75d50-f12a-405c-9521-2e9325e8e17b" />

O wizard cria a VCN, a subnet publica, a subnet privada, Internet Gateway, NAT Gateway, route tables e security lists. Para a Custom Tool, use a **private subnet** criada pelo wizard. Ela deve sair para a internet pelo **NAT Gateway**, o que e mais confiavel para chamadas HTTPS feitas por servicos gerenciados.

Antes de seguir, confira se a private subnet tem rota de saida:

```text
Destination: 0.0.0.0/0
Target: NAT Gateway
```

E se a security list/NSG permite saida HTTPS:

```text
Direction: Egress
Destination: 0.0.0.0/0
Protocol: TCP
Port: 443
```



## 5. Criar bucket no Object Storage

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

<img width="1470" height="831" alt="image" src="https://github.com/user-attachments/assets/41ad45b7-6ae9-4c4e-a81b-7416cbdb2507" />

## 6. Subir arquivo para RAG

No bucket `tdc-agent-kb`, faca upload de apenas um arquivo:

```text
assets/base_rag_tdc_floripa_2026.pdf
```

Esse PDF contem somente a base estatica do evento: visao geral, formato, FAQ, jornadas, links oficiais e instrucoes de comportamento. Ele nao contem programacao detalhada nem speakers; esses dados ficam no JSON e serao acessados pela Custom Tool.

<img width="1470" height="830" alt="image" src="https://github.com/user-attachments/assets/6423d963-06d3-4c1b-b946-f47d8b09dff2" />

## 7. Criar Knowledge Base

1. Va em **Analytics & AI**.
2. Acesse **Generative AI Agents**.
3. Clique em **Knowledge Bases**.
4. Clique em **Create knowledge base**.
5. Nome sugerido:

```text
tdc-floripa-2026-kb
```

6. Escolha Object Storage como origem.
7. Clique em 'specify data source'.
8. Selecione o bucket `tdc-agent-kb`.
<img width="1470" height="833" alt="image" src="https://github.com/user-attachments/assets/02664034-4ae3-4506-b040-04a9a3a702ac" />

9. Crie a knowledge base.
10. Aguarde a ingestao finalizar.
    


## 8. Criar o agente

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
Use a base de conhecimento para perguntas gerais sobre o evento, jornadas, formato, FAQ, regras e links oficiais.
Use obrigatoriamente a tool consulta_programacao_tdc quando a pergunta pedir agenda, programacao, trilhas por dia, horarios, palestras, sessoes, speakers, nomes de pessoas ou busca por termo.
Nao invente horarios, speakers, valores ou regras que nao estejam na base ou na resposta da tool.
```

<img width="1469" height="829" alt="image" src="https://github.com/user-attachments/assets/4e88776b-77c9-4f0d-bd62-5d4f9d826098" />

## 9. Adicionar RAG Tool

1. Na etapa de tools, clique em **Add tool**.
2. Escolha **RAG**.
3. Nome:

```text
consulta_base_tdc
```

4. Descricao:

```text
Use esta ferramenta somente para perguntas gerais sobre o TDC Floripa 2026, incluindo formato do evento, jornadas, FAQ, inscricoes, modalidades, links oficiais e orientacoes gerais. Nao use esta ferramenta para perguntas sobre agenda, programacao, sessoes, palestras, horarios, trilhas especificas, speakers ou nomes de pessoas; nesses casos use obrigatoriamente a Custom Tool consulta_programacao_tdc.
```

5. Selecione a knowledge base `tdc-floripa-2026-kb`.
6. Adicione a tool.

<img width="1470" height="771" alt="image" src="https://github.com/user-attachments/assets/2eb79fab-7d78-44e7-980d-5b2e62e0a004" />

## 10. Entender a API da Custom Tool

Para a Custom Tool funcionar bem, ela precisa chamar uma API que filtre a programacao antes de devolver a resposta ao agente. Por isso, este repositorio inclui uma API completa em Node.js:

```text
api/server.js
```

A API le o dataset estruturado:

```text
assets/programacao_tdc_floripa_2026.json
```

e expoe endpoints de busca:

```text
GET /event
GET /tracks?day=22/jul
POST /sessions/search
POST /speakers/search
```

Como fizemos:

- coletamos a programacao real do TDC Floripa 2026;
- normalizamos as informacoes em JSON;
- deixamos o JSON versionado no repositorio;
- criamos uma API que filtra sessoes, speakers, trilhas e dias;
- criamos um contrato OpenAPI para o OCI Agent chamar essa API como Custom Tool.

O importante para o conceito e que o agente nao busque sessoes e speakers no PDF. Ele deve chamar a tool, e a API deve devolver somente os resultados relevantes para a pergunta.

A API ja esta publicada para este lab em:

```text
https://tdc-oci-ai-agents-lab.onrender.com
```

Teste rapido:

```text
https://tdc-oci-ai-agents-lab.onrender.com/health
https://tdc-oci-ai-agents-lab.onrender.com/sessions?speaker=Livia%20Rodrigues
```

Contrato OpenAPI pronto para cadastrar a tool:

```yaml
openapi: 3.0.3
info:
  title: TDC Floripa 2026 Programacao API
  version: 1.0.0
  description: API de busca da programacao do TDC Floripa 2026 para uso como Custom Tool no OCI Generative AI Agents.
servers:
  - url: https://tdc-oci-ai-agents-lab.onrender.com
paths:
  /event:
    get:
      operationId: getEventInfo
      summary: Retorna informacoes gerais do evento
      description: Use para perguntas gerais sobre o nome do evento, datas, local e quantidade total de sessoes.
      responses:
        "200":
          description: Informacoes gerais do evento
          content:
            application/json:
              schema:
                type: object
  /tracks:
    get:
      operationId: listTracks
      summary: Lista trilhas da programacao
      description: Use para perguntas sobre trilhas, especialmente quando houver filtro por dia.
      parameters:
        - name: day
          in: query
          required: false
          schema:
            type: string
          description: Dia da programacao, por exemplo 22/jul, 23/jul ou 24/jul.
        - name: q
          in: query
          required: false
          schema:
            type: string
          description: Termo para filtrar o nome da trilha.
      responses:
        "200":
          description: Trilhas encontradas
          content:
            application/json:
              schema:
                type: object
  /sessions/search:
    post:
      operationId: searchSessions
      summary: Busca sessoes, palestras, horarios e speakers
      description: Use obrigatoriamente para perguntas sobre agenda, programacao, sessoes, palestras, horarios, trilhas especificas, speakers, nomes de pessoas ou busca por termo. Envie nomes com espacos no corpo JSON, nao na URL.
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                q:
                  type: string
                  description: Termo de busca geral, como agentes, IA, arquitetura, Java, titulo ou nome de uma pessoa.
                speaker:
                  type: string
                  description: Nome do speaker ou parte do nome, por exemplo Ana Lindiner ou Livia Rodrigues.
                day:
                  type: string
                  description: Dia da programacao, por exemplo 22/jul, 23/jul ou 24/jul.
                track:
                  type: string
                  description: Nome ou parte do nome da trilha.
                limit:
                  type: integer
                  default: 10
                  description: Quantidade maxima de resultados.
      responses:
        "200":
          description: Sessoes encontradas
          content:
            application/json:
              schema:
                type: object
  /speakers/search:
    post:
      operationId: searchSpeakers
      summary: Busca speakers e suas sessoes
      description: Use para perguntas sobre palestrantes/speakers, nomes de pessoas e sessoes associadas a uma pessoa. Envie nomes com espacos no corpo JSON, nao na URL.
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                q:
                  type: string
                  description: Nome ou parte do nome do speaker.
                limit:
                  type: integer
                  default: 10
                  description: Quantidade maxima de speakers.
      responses:
        "200":
          description: Speakers encontrados
          content:
            application/json:
              schema:
                type: object
                additionalProperties: true
```

O mesmo contrato esta salvo em:

```text
assets/custom_tool_openapi.yaml
```

Para testar a API localmente antes de publicar:

```bash
cd api
npm start
```

Exemplos de teste local:

```text
http://localhost:3000/sessions?q=agentes&limit=5
http://localhost:3000/tracks?day=22/jul
http://localhost:3000/speakers?q=ana

```
<img width="1470" height="877" alt="image" src="https://github.com/user-attachments/assets/df3fbb08-ae3a-4f14-87f2-2ba83248dffb" />


## 11. Adicionar Custom Tool no agente

1. Volte ao agente.
2. Clique em **Add tool**.
3. Escolha **Custom tool**.
4. Cole o contrato OpenAPI da secao anterior ou use o arquivo `assets/custom_tool_openapi.yaml`.

5. Nome sugerido:

```text
consulta_programacao_tdc
```

6. Descricao:

```text
Use esta ferramenta obrigatoriamente para buscar sessoes, speakers, trilhas por dia, horarios, palestras, nomes de pessoas e detalhes estruturados da programacao do TDC Floripa 2026.
Ela deve ser usada sempre que o usuario perguntar sobre agenda, horarios, palestras, trilhas especificas, speakers, nomes de pessoas ou busca por termo na programacao.
```

7. Em **Authentication type**, selecione **No authentication** ou **None**.
8. Em rede, selecione os recursos criados no passo 4:

```text
VCN compartment: tdc-ai-agents-lab
VCN: tdc-ai-agents-vcn
Subnet compartment: tdc-ai-agents-lab
Subnet: private subnet criada pelo wizard
```

Use a **private subnet** porque a Custom Tool faz chamada HTTPS para uma API publica. A saida deve acontecer via NAT Gateway criado pelo wizard. Se usar uma subnet sem rota para internet, a tool pode falhar com `Internal Execution Error`.

9. Salve a tool.

<img width="1470" height="792" alt="image" src="https://github.com/user-attachments/assets/a8a51ac5-e772-4dff-be31-61c4964f3114" />

## 12. Criar endpoint do agente

Na tela **Setup agent endpoint**, use uma configuracao simples para o lab:

1. Mantenha **Automatically create an endpoint for this agent** ativado.
2. Mantenha **Enable human in the loop** desativado.
 <img width="1470" height="827" alt="image" src="https://github.com/user-attachments/assets/3d85c92a-6451-4a89-9dbe-ee0fd33e98cd" />

3. Em **Content moderation**, selecione:

```text
Input: Disable
Output: Disable
```
<img width="1470" height="829" alt="image" src="https://github.com/user-attachments/assets/979039b3-7e55-4dc4-8c59-7e5d2f2eb8a4" />

4. Em **Prompt injection (PI) protection**, selecione:

```text
Disable
```

5. Em **Personally identifiable information (PII) protection**, selecione:

```text
Input: Disable
Output: Disable
```

6. Clique em **Next**.
7. Na tela de revisao, confira:

```text
Agent: Assistente TDC Floripa
RAG tool: consulta_base_tdc
Custom tool: consulta_programacao_tdc
Endpoint automatico: ativado
```

8. Clique em **Create**.
9. Aguarde o agente e o endpoint ficarem com status **Active**.

Para o lab, deixamos os guardrails em `Disable` para reduzir variaveis durante os testes e facilitar a demonstracao do uso de RAG e Custom Tool. Em um ambiente produtivo, avalie usar `Block` ou `Inform` para content moderation, prompt injection e PII conforme a politica de seguranca da aplicacao.


## 13. Testar no chat

Antes dos testes, aqueça a API da Custom Tool:

```text
https://tdc-oci-ai-agents-lab.onrender.com/health
```

Use os testes abaixo para demonstrar o papel de cada ferramenta.

### Teste 1: RAG com informacao geral do evento

Objetivo: mostrar que o agente usa a Knowledge Base para responder contexto geral do evento, sem depender da API de programacao.

```text
O que sao as Jornadas TDC e como elas ajudam uma pessoa a escolher melhor a experiencia dela no TDC Floripa 2026?
```

Resultado esperado: resposta conceitual sobre Jornadas TDC, formato do evento e orientacao geral. O trace deve mostrar uso da RAG Tool `consulta_base_tdc`.

### Teste 2: Custom Tool com speaker especifica

Objetivo: mostrar que perguntas sobre speakers e sessoes usam a API estruturada.

```text
Quais palestras a Livia Rodrigues vai fazer?
```

Resultado esperado: resposta com as sessoes da Livia Rodrigues Fernandes Silva:

- Painel: GenAI no Limite: Arquiteturas Avancadas e as Conversas que Evitamos.
- LLM-as-Judge: Usando IA para avaliar IA.

O trace deve mostrar `POST /speakers/search` ou `POST /sessions/search`.

### Teste 3: RAG + Custom Tool na mesma resposta

Objetivo: mostrar que o agente pode combinar contexto geral do evento com busca estruturada na programacao.

```text
Estou interessado em GenAI e agentes. Explique rapidamente como o TDC organiza trilhas ou jornadas e depois liste sessoes da programacao que falem sobre agentes.
```

Resultado esperado: a primeira parte vem da RAG, explicando organizacao/jornadas/trilhas; a segunda vem da Custom Tool, listando sessoes filtradas por `agentes`, `agentic` ou termos relacionados.

### Teste 4: roteiro personalizado por acesso e interesses

Objetivo: demonstrar um uso mais proximo de produto, onde o agente cruza preferencia do usuario com a programacao.

```text
Tenho acesso ao dia 24/jul e me interesso por GenAI, LLMs e avaliacao de modelos. Monte um roteiro objetivo para mim com as sessoes mais relevantes, horarios e trilha.
```

Resultado esperado: o agente deve usar a Custom Tool para buscar sessoes do dia 24/jul relacionadas a GenAI/LLMs e montar um roteiro em ordem de horario.

Outro exemplo:

```text
Tenho acesso ao dia 22/jul e quero focar em Agentic AI e arquitetura. Quais sessoes voce recomenda e em que ordem?
```

Resultado esperado: roteiro com sessoes do dia 22/jul, priorizando trilha Agentic AI e termos de arquitetura.


## 14. Demonstrar endpoint

- Console chat: valida comportamento.
- Agent endpoint: integra com aplicacao real.
- Custom tool: conecta o agente a dados vivos ou estruturados.

Mensagem para o publico:

```text
O chat prova que o agente funciona. O endpoint prova que ele pode virar produto.
```

> INSERIR PRINT: tela do endpoint do agente.

## 15. Opcional: Telegram Bot

Depois de criar o Agent Endpoint, voce pode mostrar como o agente seria usado em um canal real, como Telegram.

Fluxo:

```text
Telegram
  -> backend do bot
  -> OCI Agent Endpoint
  -> RAG Tool / Custom Tool
  -> resposta no Telegram
```

Este repositorio inclui um exemplo em:

```text
examples/telegram-bot
```

Para uma demo rapida sem credenciais OCI, o exemplo roda em `BOT_MODE=mock` e consulta a API publica da programacao. Para a opcao completa, use `BOT_MODE=oci`: o backend chama o OCI Generative AI Agent Endpoint real e a resposta passa pelo agente, RAG e Custom Tool.

Resumo do setup:

1. Crie um bot no Telegram com `@BotFather`.
2. Guarde o token como `TELEGRAM_BOT_TOKEN`.
3. Publique este repositorio como **New Web Service** no Render.
4. Use:

```text
Root Directory: deixe vazio
Build Command: npm install
Start Command: npm start
Health Check Path: /health
```

5. Configure as variaveis:

```text
TELEGRAM_BOT_TOKEN=token_do_botfather
BOT_MODE=mock
PROGRAMACAO_API_URL=https://tdc-oci-ai-agents-lab.onrender.com
```

Para usar o Agent Endpoint real:

```text
TELEGRAM_BOT_TOKEN=token_do_botfather
BOT_MODE=oci
OCI_REGION=us-phoenix-1
OCI_AGENT_ENDPOINT_ID=ocid1.genaiagentendpoint...
OCI_TENANCY_OCID=ocid1.tenancy...
OCI_USER_OCID=ocid1.user...
OCI_FINGERPRINT=fingerprint_da_api_key
OCI_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----
OCI_PRIVATE_KEY_PASSPHRASE=
```

Como obter esses valores:

- `OCI_AGENT_ENDPOINT_ID`: na pagina do endpoint em **Generative AI Agents > Agent endpoints**.
- `OCI_TENANCY_OCID`: em **Tenancy details**.
- `OCI_USER_OCID`, `OCI_FINGERPRINT` e chave privada: em **My profile > API keys**.
- `OCI_REGION`: a regiao usada no lab, por exemplo `us-phoenix-1`.

No Render, cole `OCI_PRIVATE_KEY` em uma linha usando `\n` no lugar das quebras de linha. Deixe `OCI_PRIVATE_KEY_PASSPHRASE` vazio se sua chave privada nao tiver senha.

6. Configure o webhook:

```text
https://api.telegram.org/botSEU_TOKEN/setWebhook?url=https://SUA_URL_DO_BOT/telegram/webhook
```

7. Teste no Telegram:

```text
Quais palestras a Livia Rodrigues vai fazer?
```

> Esse passo e opcional. Ele mostra que o Agent Endpoint pode virar produto em canais como Telegram, WhatsApp, Slack ou uma pagina web, mas nao e necessario para concluir o lab principal.

Importante: as credenciais OCI ficam somente no backend. Nunca coloque `OCI_PRIVATE_KEY`, token do Telegram ou OCIDs sensiveis em uma pagina web publica.

## Atualizar programacao antes do evento

Para atualizar a programacao a partir do site oficial:

Atualize o arquivo:

```text
assets/programacao_tdc_floripa_2026.json
```

Depois faca commit e push para a branch `main` e redeploy/restart da API publicada. A API le o JSON atualizado e passa a devolver os novos resultados nas consultas da Custom Tool. O PDF do RAG so deve ser alterado quando mudarem informacoes estaticas do evento, como formato, FAQ, links oficiais ou regras gerais.

## Limpeza dos recursos

Ao final do lab, remova:

- agent endpoint;
- agent;
- knowledge base;
- objetos do bucket;
- bucket;
- policies e compartment, se forem descartaveis.

## Fontes

- https://thedevconf.com/tdc/2026/florianopolis/
- https://thedevconf.com/tdc/2026/florianopolis/jornadas/
