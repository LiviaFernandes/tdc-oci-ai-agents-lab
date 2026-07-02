const PORT = Number(process.env.PORT || 3000);
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const BOT_MODE = process.env.BOT_MODE || "mock";
const PROGRAMACAO_API_URL = process.env.PROGRAMACAO_API_URL || "https://tdc-oci-ai-agents-lab.onrender.com";

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

  const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      parse_mode: "Markdown"
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Telegram sendMessage failed: ${response.status} ${errorText}`);
  }
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

async function answerWithOciAgent(message) {
  // TODO: conecte aqui o SDK/chamada autenticada ao OCI Generative AI Agent Endpoint.
  // Mantenha essa chamada no backend para nao expor credenciais OCI.
  return [
    "Modo OCI ainda nao configurado neste exemplo.",
    "",
    "Mensagem recebida:",
    message,
    "",
    "Configure BOT_MODE=mock para testar o Telegram com a API publica da programacao,",
    "ou implemente aqui a chamada ao OCI Agent Endpoint."
  ].join("\n");
}

async function answerMessage(message) {
  if (BOT_MODE === "oci") {
    return answerWithOciAgent(message);
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

  const answer = await answerMessage(message);
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
