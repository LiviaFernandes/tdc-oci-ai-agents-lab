const PORT = Number(process.env.PORT || 3000);
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const BOT_MODE = process.env.BOT_MODE || "mock";
const PROGRAMACAO_API_URL = process.env.PROGRAMACAO_API_URL || "https://tdc-oci-ai-agents-lab.onrender.com";
const OCI_AGENT_ENDPOINT_ID = process.env.OCI_AGENT_ENDPOINT_ID;
const OCI_REGION = process.env.OCI_REGION || "us-phoenix-1";

let ociClientPromise;
const telegramSessions = new Map();

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" }
  });
}

async function sendTelegramMessage(chatId, text) {
  if (!TELEGRAM_BOT_TOKEN) {
    throw new Error("Missing TELEGRAM_BOT_TOKEN");
  }

  const chunks = splitTelegramText(text);
  for (const chunk of chunks) {
    const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: chunk
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Telegram sendMessage failed: ${response.status} ${errorText}`);
    }
  }
}

function splitTelegramText(text) {
  const maxLength = 3800;
  if (text.length <= maxLength) return [text];

  const chunks = [];
  for (let index = 0; index < text.length; index += maxLength) {
    chunks.push(text.slice(index, index + maxLength));
  }
  return chunks;
}

function requiredEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing ${name}`);
  }
  return value;
}

function normalizePrivateKey(value) {
  return value.replace(/\\n/g, "\n");
}

async function getOciAgentClient() {
  if (!ociClientPromise) {
    ociClientPromise = (async () => {
      const ociCommon = await import("oci-common");
      const agentRuntime = await import("oci-generativeaiagentruntime");
      const region = ociCommon.Region.fromRegionId(OCI_REGION);
      const provider = new ociCommon.SimpleAuthenticationDetailsProvider(
        requiredEnv("OCI_TENANCY_OCID"),
        requiredEnv("OCI_USER_OCID"),
        requiredEnv("OCI_FINGERPRINT"),
        normalizePrivateKey(requiredEnv("OCI_PRIVATE_KEY")),
        process.env.OCI_PRIVATE_KEY_PASSPHRASE || null,
        region
      );

      const client = new agentRuntime.GenerativeAiAgentRuntimeClient({
        authenticationDetailsProvider: provider
      });
      client.region = region;
      return client;
    })();
  }

  return ociClientPromise;
}

async function getOrCreateAgentSession(chatId) {
  if (telegramSessions.has(chatId)) {
    return telegramSessions.get(chatId);
  }

  const client = await getOciAgentClient();
  const response = await client.createSession({
    agentEndpointId: requiredEnv("OCI_AGENT_ENDPOINT_ID"),
    createSessionDetails: {
      displayName: `telegram-${chatId}`,
      description: "Sessao criada pelo bot Telegram do lab TDC OCI AI Agents"
    }
  });

  const sessionId = response.session?.id;
  if (!sessionId) {
    throw new Error("OCI Agent Runtime did not return a session id");
  }

  telegramSessions.set(chatId, sessionId);
  return sessionId;
}

function extractName(text) {
  const normalized = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const match = normalized.match(/(?:palestras|sessoes|sessões).*(?:da|do|de)\s+(.+?)(?:\?|$)/);
  if (match?.[1]) return match[1].trim();
  if (normalized.includes("livia")) return "Livia Rodrigues";
  if (normalized.includes("ana lindiner")) return "Ana Lindiner";
  return text;
}

function formatSessionsFromSpeakerResult(data) {
  if (!data?.results?.length) {
    return "Nao encontrei sessoes para esse nome na programacao.";
  }

  const lines = [];
  for (const speaker of data.results) {
    lines.push(`*${speaker.speaker}* participa de:`);
    for (const session of speaker.sessions || []) {
      lines.push("");
      lines.push(`- ${session.title}`);
      lines.push(`  Data: ${session.date}`);
      lines.push(`  Horario: ${session.time}`);
      lines.push(`  Trilha: ${session.track}`);
    }
  }
  return lines.join("\n");
}

async function answerWithMockMode(message) {
  const name = extractName(message);
  const response = await fetch(`${PROGRAMACAO_API_URL}/speakers/search`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ q: name, limit: 10 })
  });

  if (!response.ok) {
    throw new Error(`Programacao API failed: ${response.status}`);
  }

  return formatSessionsFromSpeakerResult(await response.json());
}

async function answerWithOciAgent(message, chatId) {
  if (!OCI_AGENT_ENDPOINT_ID) {
    throw new Error("Missing OCI_AGENT_ENDPOINT_ID");
  }

  const client = await getOciAgentClient();
  const sessionId = await getOrCreateAgentSession(chatId);
  const response = await client.chat({
    agentEndpointId: OCI_AGENT_ENDPOINT_ID,
    chatDetails: {
      userMessage: message,
      sessionId,
      shouldStream: false
    }
  });

  const text = response?.chatResult?.message?.content?.text;
  if (!text) {
    throw new Error("OCI Agent Runtime returned an empty answer");
  }

  return text;
}

async function answerMessage(message, chatId) {
  if (BOT_MODE === "oci") {
    return answerWithOciAgent(message, chatId);
  }
  return answerWithMockMode(message);
}

async function handleTelegramWebhook(request) {
  const update = await request.json();
  const message = update.message?.text;
  const chatId = update.message?.chat?.id;

  if (!message || !chatId) {
    return jsonResponse({ ok: true, ignored: true });
  }

  let answer;
  try {
    answer = await answerMessage(message, chatId);
  } catch (error) {
    console.error("Failed to answer Telegram message", error);
    answer = "Nao consegui consultar o agente agora. Verifique as variaveis do Render e os logs do backend.";
  }

  await sendTelegramMessage(chatId, answer);

  return jsonResponse({ ok: true });
}

const { createServer } = await import("node:http");

createServer(async (request, response) => {
  const url = new URL(request.url, `http://${request.headers.host}`);

  try {
    if (request.method === "GET" && url.pathname === "/health") {
      response.writeHead(200, { "content-type": "application/json; charset=utf-8" });
      response.end(JSON.stringify({ status: "ok", mode: BOT_MODE }));
      return;
    }

    if (request.method === "POST" && url.pathname === "/telegram/webhook") {
      const chunks = [];
      for await (const chunk of request) chunks.push(chunk);
      const body = Buffer.concat(chunks).toString("utf8");
      const fakeRequest = new Request("http://localhost/telegram/webhook", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body
      });
      const result = await handleTelegramWebhook(fakeRequest);
      response.writeHead(result.status, Object.fromEntries(result.headers.entries()));
      response.end(await result.text());
      return;
    }

    response.writeHead(404, { "content-type": "application/json; charset=utf-8" });
    response.end(JSON.stringify({ error: "not found" }));
  } catch (error) {
    response.writeHead(500, { "content-type": "application/json; charset=utf-8" });
    response.end(JSON.stringify({ error: error.message }));
  }
}).listen(PORT, () => {
  console.log(`Telegram bot example running on http://localhost:${PORT}`);
});
