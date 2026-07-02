# Exemplo opcional: Telegram Bot

Este exemplo mostra como levar o assistente para um canal externo.

Fluxo:

```text
Telegram -> Backend do bot -> API/OCI Agent -> Backend -> Telegram
```

Para o lab, o exemplo pode rodar de duas formas:

- `BOT_MODE=mock`: consulta somente a API publica da programacao.
- `BOT_MODE=oci`: chama o OCI Generative AI Agent Endpoint real, mantendo RAG, tools e instrucoes do agente.

## 1. Criar bot no BotFather

No Telegram:

```text
/newbot
```

Guarde o token como:

```text
TELEGRAM_BOT_TOKEN
```

## 2. Publicar este backend no Render

Publique o repositorio como **New Web Service** no Render.

Configuracao sugerida:

```text
Root Directory: deixe vazio
Build Command: npm install
Start Command: npm start
Health Check Path: /health
```

O `package.json` da raiz do repositorio ja aponta o `npm start` para este exemplo:

```text
node examples/telegram-bot/server.js
```

Variaveis de ambiente:

```text
TELEGRAM_BOT_TOKEN=token_do_botfather
BOT_MODE=mock
PROGRAMACAO_API_URL=https://tdc-oci-ai-agents-lab.onrender.com
```

Para a opcao completa com OCI Agent Endpoint, use:

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

Observacoes:

- `OCI_AGENT_ENDPOINT_ID` fica na pagina do endpoint do agente em **Generative AI Agents > Agent endpoints**.
- `OCI_PRIVATE_KEY` deve ser a chave privada da API key do usuario. No Render, cole a chave em uma linha usando `\n` no lugar das quebras de linha.
- `OCI_PRIVATE_KEY_PASSPHRASE` so precisa ser preenchida se a chave privada tiver senha.
- O usuario da API key precisa estar no grupo com as policies do lab.

## 3. Configurar webhook

Depois do deploy, copie a URL publica do bot, por exemplo:

```text
https://tdc-telegram-bot.onrender.com
```

Abra no navegador:

```text
https://api.telegram.org/botSEU_TOKEN/setWebhook?url=https://tdc-telegram-bot.onrender.com/telegram/webhook
```

Troque `SEU_TOKEN` pelo token do BotFather.

## 4. Testar

No Telegram, envie:

```text
Quais palestras a Livia Rodrigues vai fazer?
```

Resposta esperada em `BOT_MODE=mock`: o bot lista as sessoes encontradas na API de programacao.

Resposta esperada em `BOT_MODE=oci`: o bot responde como o Agent Endpoint, usando RAG e Custom Tool.

## 5. Criar a API key OCI para o Render

1. Na OCI, clique no icone do usuario no canto superior direito.
2. Acesse **My profile > API keys**.
3. Clique em **Add API key**.
4. Gere ou envie uma chave publica.
5. Copie os dados exibidos no arquivo de configuracao:

```text
user=ocid1.user...
fingerprint=...
tenancy=ocid1.tenancy...
region=us-phoenix-1
```

6. Leve esses valores para as variaveis `OCI_USER_OCID`, `OCI_FINGERPRINT`, `OCI_TENANCY_OCID` e `OCI_REGION` no Render.
7. Cole a chave privada em `OCI_PRIVATE_KEY`.

Nunca coloque essas credenciais no frontend, no Telegram ou no repositorio. Elas ficam somente como variaveis de ambiente no backend.
