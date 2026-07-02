# Exemplo opcional: Telegram Bot

Este exemplo mostra como levar o assistente para um canal externo.

Fluxo:

```text
Telegram -> Backend do bot -> API/OCI Agent -> Backend -> Telegram
```

Para o lab, o exemplo vem em modo `mock`: ele usa a API publica da programacao para responder perguntas sobre palestrantes. Depois, voce pode trocar para `BOT_MODE=oci` e implementar a chamada ao OCI Agent Endpoint.

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

Resposta esperada: o bot lista as sessoes encontradas na API de programacao.

## 5. Conectar ao OCI Agent Endpoint

Para usar o agente real:

1. Configure `BOT_MODE=oci`.
2. Adicione a chamada autenticada ao OCI Agent Endpoint em `answerWithOciAgent`.
3. Mantenha credenciais OCI somente no backend, nunca no Telegram nem no frontend.
