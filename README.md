# Lab TDC: AI Agents na OCI com RAG e Tools

Este projeto contem o material de apoio para um laboratorio de 1 hora sobre **AI Agents em Oracle Cloud Infrastructure**, usando:

- OCI Generative AI Agents;
- Object Storage;
- Knowledge Base com RAG;
- Custom Tool via API publica ja preparada;
- endpoint do agente;
- programacao real do TDC Floripa 2026 como dataset estruturado da tool.

O objetivo do lab e criar um agente chamado **Assistente TDC Floripa**, capaz de responder perguntas gerais sobre o evento usando RAG e consultar programacao, horarios, sessoes e speakers usando uma tool.

## Entregaveis do repositorio

```text
assets/
  base_rag_tdc_floripa_2026.pdf         # Base estatica para RAG
  programacao_tdc_floripa_2026.json     # Dataset estruturado usado pela tool
  custom_tool_openapi.yaml              # Contrato pronto da Custom Tool
api/
  server.js                             # API completa de busca para a Custom Tool
```

O PDF e o JSON foram separados de proposito:

- **PDF/RAG**: contexto estatico do evento, FAQ, jornadas, formato, links oficiais e orientacoes.
- **API/Tool**: busca estruturada sobre o JSON de programacao, com filtros por termo, speaker, dia e trilha.

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

3. Escolha **Create VCN with Internet Connectivity**.
6. Use:

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

10. Crie a knowledge base.
11. Aguarde a ingestao finalizar.
    


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
Nao use a base de conhecimento para responder perguntas sobre speakers, sessoes, horarios ou trilhas especificas.
Se o usuario perguntar sobre uma pessoa, como Ana Lindiner, chame a tool consulta_programacao_tdc usando o nome como parametro speaker ou q.
Quando uma informacao puder mudar, informe que a fonte oficial deve ser consultada.
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
GET /sessions?q=agentes&limit=5
GET /sessions?speaker=Ana%20Lindiner
GET /sessions?day=22/jul&track=Agentic%20AI
GET /speakers?q=ana
```

Como fizemos:

- coletamos a programacao real do TDC Floripa 2026;
- normalizamos as informacoes em JSON;
- deixamos o JSON versionado no repositorio;
- criamos uma API que filtra sessoes, speakers, trilhas e dias;
- criamos um contrato OpenAPI para o OCI Agent chamar essa API como Custom Tool.

O importante para o conceito e que o agente nao busque sessoes e speakers no PDF. Ele deve chamar a tool, e a API deve devolver somente os resultados relevantes para a pergunta.

Para usar no OCI Agent, publique essa API em um endpoint HTTPS publico. Pode ser em OCI, Render, Railway, Fly.io, Cloud Run ou outro servico simples de hosting Node.js. Depois substitua `https://SEU_ENDPOINT_PUBLICO` no OpenAPI pela URL publicada.

Este repositorio ja inclui `render.yaml`, entao o caminho mais simples e publicar no Render:

1. Acesse `https://render.com`.
2. Crie um **New > Blueprint** ou **New > Web Service** conectado ao repositorio GitHub.
3. Se usar **Blueprint**, selecione este repositorio e confirme o arquivo `render.yaml`.
4. Se usar **Web Service**, configure:

```text
Root Directory: api
Build Command: npm install
Start Command: npm start
Health Check Path: /health
```

5. Aguarde o deploy finalizar.
6. Copie a URL publica gerada, por exemplo:

```text
https://tdc-floripa-programacao-api.onrender.com
```

7. Teste:

```text
https://SUA_URL_RENDER/sessions?speaker=Ana%20Lindiner
```

Se o retorno vier em JSON com as sessoes da speaker, a API esta pronta para ser usada na Custom Tool.

Contrato OpenAPI pronto para cadastrar a tool:

```yaml
openapi: 3.0.3
info:
  title: TDC Floripa 2026 Programacao API
  version: 1.0.0
  description: API de busca da programacao do TDC Floripa 2026 para uso como Custom Tool no OCI Generative AI Agents.
servers:
  - url: https://SEU_ENDPOINT_PUBLICO
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
  /sessions:
    get:
      operationId: searchSessions
      summary: Busca sessoes, palestras, horarios e speakers
      description: Use obrigatoriamente para perguntas sobre agenda, programacao, sessoes, palestras, horarios, trilhas especificas, speakers, nomes de pessoas ou busca por termo.
      parameters:
        - name: q
          in: query
          required: false
          schema:
            type: string
          description: Termo de busca geral, como agentes, IA, arquitetura, Java ou nome de uma pessoa.
        - name: speaker
          in: query
          required: false
          schema:
            type: string
          description: Nome do speaker ou parte do nome, por exemplo Ana Lindiner.
        - name: day
          in: query
          required: false
          schema:
            type: string
          description: Dia da programacao, por exemplo 22/jul, 23/jul ou 24/jul.
        - name: track
          in: query
          required: false
          schema:
            type: string
          description: Nome ou parte do nome da trilha.
        - name: limit
          in: query
          required: false
          schema:
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
  /speakers:
    get:
      operationId: searchSpeakers
      summary: Busca speakers e suas sessoes
      description: Use para perguntas sobre palestrantes/speakers, nomes de pessoas e sessoes associadas a uma pessoa.
      parameters:
        - name: q
          in: query
          required: false
          schema:
            type: string
          description: Nome ou parte do nome do speaker.
        - name: limit
          in: query
          required: false
          schema:
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

Antes de colar o OpenAPI na OCI, substitua:

```text
https://SEU_ENDPOINT_PUBLICO
```

pela URL publica da API publicada.

Para testar a API localmente antes de publicar:

```bash
cd api
npm start
```

Exemplos de teste local:

```text
http://localhost:3000/sessions?speaker=Ana%20Lindiner
http://localhost:3000/sessions?q=agentes&limit=5
http://localhost:3000/tracks?day=22/jul
http://localhost:3000/speakers?q=ana
```

<img width="1470" height="876" alt="image" src="https://github.com/user-attachments/assets/506f20bd-0790-46da-acb5-2c77649e6f14" />

## 11. Adicionar Custom Tool no agente

1. Volte ao agente.
2. Clique em **Add tool**.
3. Escolha **Custom tool**.
4. Cole o contrato OpenAPI da secao anterior ou use o arquivo `assets/custom_tool_openapi.yaml`.
5. Substitua `https://SEU_ENDPOINT_PUBLICO` pela URL publica da API.

6. Nome sugerido:

```text
consulta_programacao_tdc
```

7. Descricao:

```text
Use esta ferramenta obrigatoriamente para buscar sessoes, speakers, trilhas por dia, horarios, palestras, nomes de pessoas e detalhes estruturados da programacao do TDC Floripa 2026.
Ela deve ser usada sempre que o usuario perguntar sobre agenda, horarios, palestras, trilhas especificas, speakers, nomes de pessoas ou busca por termo na programacao.
Exemplos: Ana Lindiner, sessoes sobre agentes, trilhas do dia 22/jul, palestras de arquitetura, horarios de uma sessao.
```

8. Em **Authentication type**, selecione **No authentication** ou **None**.
9. Em rede, selecione os recursos criados no passo 4:

```text
VCN compartment: tdc-ai-agents-lab
VCN: tdc-ai-agents-vcn
Subnet compartment: tdc-ai-agents-lab
Subnet: public subnet criada pelo wizard
```

10. Salve a tool.

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

> INSERIR PRINT: endpoint ativo.

## 13. Testar no chat

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

### Se o agente usar RAG em vez da Custom Tool

Se a resposta disser que nao encontrou um speaker e o trace mostrar somente:

```text
Tool output: consulta_base_tdc
```

entao o agente escolheu a ferramenta errada. Para corrigir:

1. Confirme se a Custom Tool `consulta_programacao_tdc` foi criada com o OpenAPI atualizado deste repositorio.
2. Confirme se a descricao da RAG Tool diz que ela nao deve ser usada para agenda, sessoes, horarios, speakers ou nomes de pessoas.
3. Confirme se as instrucoes do agente dizem explicitamente para usar `consulta_programacao_tdc` quando a pergunta mencionar speakers, sessoes, trilhas, horarios ou nomes de pessoas.
4. Teste com uma pergunta mais direcionada:

```text
Use a tool consulta_programacao_tdc e responda quais sessoes a Ana Lindiner apresenta.
```

Resultado esperado para esse teste:

```text
Ana Lindiner Lima de Araujo apresenta a sessao "Arquiteturas orientadas a agentes: quando sistemas deixam de executar e passam a decidir", no dia 22/jul, das 10:30 as 11:05, na Trilha Agentic AI.
```

## 14. Demonstrar endpoint

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
