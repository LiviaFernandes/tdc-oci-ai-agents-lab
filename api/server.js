import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3000);
const DATA_PATH = process.env.DATA_PATH || join(__dirname, "..", "assets", "programacao_tdc_floripa_2026.json");

const sessions = JSON.parse(readFileSync(DATA_PATH, "utf8"));

function normalize(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function includesNormalized(value, query) {
  if (!query) return true;
  return normalize(value).includes(normalize(query));
}

function sessionText(session) {
  return [
    session.title,
    session.description,
    session.track,
    session.date,
    session.time,
    ...(session.speakers || [])
  ].join(" ");
}

function parseLimit(searchParams) {
  const limit = Number(searchParams.get("limit") || 10);
  if (!Number.isFinite(limit) || limit <= 0) return 10;
  return Math.min(limit, 50);
}

function compactSession(session) {
  return {
    title: session.title,
    date: session.date,
    time: session.time,
    track: session.track,
    speakers: session.speakers || [],
    description: session.description || "",
    source_url: session.source_url || ""
  };
}

function writeJson(response, status, body) {
  response.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "content-type"
  });
  response.end(JSON.stringify(body, null, 2));
}

function getEvent() {
  return {
    name: "TDC Floripa 2026",
    location: "Florianopolis, SC",
    dates: ["22/jul", "23/jul", "24/jul"],
    total_sessions: sessions.length,
    source: "https://thedevconf.com/tdc/2026/florianopolis/",
    available_endpoints: ["/event", "/tracks", "/sessions", "/speakers"]
  };
}

function listTracks(searchParams) {
  const day = searchParams.get("day");
  const q = searchParams.get("q");
  const filtered = sessions.filter((session) => {
    return includesNormalized(session.date, day) && includesNormalized(session.track, q);
  });

  const byTrack = new Map();
  for (const session of filtered) {
    if (!byTrack.has(session.track)) {
      byTrack.set(session.track, {
        track: session.track,
        dates: new Set(),
        session_count: 0
      });
    }
    const track = byTrack.get(session.track);
    track.dates.add(session.date);
    track.session_count += 1;
  }

  return {
    filters: { day: day || null, q: q || null },
    count: byTrack.size,
    results: [...byTrack.values()]
      .map((track) => ({ ...track, dates: [...track.dates].sort() }))
      .sort((a, b) => a.track.localeCompare(b.track, "pt-BR"))
  };
}

function searchSessions(searchParams) {
  const q = searchParams.get("q");
  const speaker = searchParams.get("speaker");
  const day = searchParams.get("day");
  const track = searchParams.get("track");
  const limit = parseLimit(searchParams);

  return searchSessionsFromFilters({ q, speaker, day, track, limit });
}

function searchSessionsFromFilters({ q, speaker, day, track, limit = 10 }) {
  const results = sessions.filter((session) => {
    const speakerText = (session.speakers || []).join(" ");
    return (
      includesNormalized(sessionText(session), q) &&
      includesNormalized(speakerText, speaker) &&
      includesNormalized(session.date, day) &&
      includesNormalized(session.track, track)
    );
  });

  return {
    filters: {
      q: q || null,
      speaker: speaker || null,
      day: day || null,
      track: track || null,
      limit
    },
    count: results.length,
    results: results.slice(0, limit).map(compactSession)
  };
}

function searchSpeakers(searchParams) {
  const q = searchParams.get("q");
  const limit = parseLimit(searchParams);
  return searchSpeakersFromFilters({ q, limit });
}

function searchSpeakersFromFilters({ q, limit = 10 }) {
  const speakers = new Map();

  for (const session of sessions) {
    for (const speaker of session.speakers || []) {
      if (!includesNormalized(speaker, q)) continue;
      if (!speakers.has(speaker)) {
        speakers.set(speaker, {
          speaker,
          session_count: 0,
          sessions: []
        });
      }
      const record = speakers.get(speaker);
      record.session_count += 1;
      record.sessions.push(compactSession(session));
    }
  }

  const results = [...speakers.values()]
    .sort((a, b) => a.speaker.localeCompare(b.speaker, "pt-BR"))
    .slice(0, limit);

  return {
    filters: { q: q || null, limit },
    count: results.length,
    results
  };
}

const routes = {
  "/health": () => ({ status: "ok" }),
  "/event": getEvent,
  "/tracks": listTracks,
  "/sessions": searchSessions,
  "/speakers": searchSpeakers
};

const postRoutes = {
  "/sessions/search": (body) => searchSessionsFromFilters({
    q: body.q,
    speaker: body.speaker,
    day: body.day,
    track: body.track,
    limit: Number(body.limit || 10)
  }),
  "/speakers/search": (body) => searchSpeakersFromFilters({
    q: body.q,
    limit: Number(body.limit || 10)
  })
};

function readJsonBody(request) {
  return new Promise((resolve, reject) => {
    let raw = "";
    request.on("data", (chunk) => {
      raw += chunk;
      if (raw.length > 100_000) {
        reject(new Error("Request body too large"));
        request.destroy();
      }
    });
    request.on("end", () => {
      if (!raw.trim()) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(new Error("Invalid JSON body"));
      }
    });
    request.on("error", reject);
  });
}

createServer(async (request, response) => {
  const url = new URL(request.url, `http://${request.headers.host}`);

  if (request.method === "OPTIONS") {
    writeJson(response, 200, { status: "ok" });
    return;
  }

  if (request.method === "POST") {
    const handler = postRoutes[url.pathname];
    if (!handler) {
      writeJson(response, 404, {
        error: "Not found",
        available_endpoints: [...Object.keys(routes), ...Object.keys(postRoutes)]
      });
      return;
    }

    try {
      const body = await readJsonBody(request);
      writeJson(response, 200, handler(body));
    } catch (error) {
      writeJson(response, 400, { error: error.message });
    }
    return;
  }

  if (request.method !== "GET") {
    writeJson(response, 405, { error: "Method not allowed" });
    return;
  }

  const handler = routes[url.pathname];
  if (!handler) {
    writeJson(response, 404, {
      error: "Not found",
      available_endpoints: Object.keys(routes)
    });
    return;
  }

  try {
    writeJson(response, 200, handler(url.searchParams));
  } catch (error) {
    writeJson(response, 500, { error: error.message });
  }
}).listen(PORT, () => {
  console.log(`TDC Programacao API running on http://localhost:${PORT}`);
});
