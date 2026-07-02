from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "assets" / "programacao_tdc_floripa_2026.json"

app = FastAPI(
    title="TDC Floripa 2026 Tool API",
    version="1.0.0",
    description="API simples para consultar a programacao oficial coletada do TDC Floripa 2026.",
)


def load_sessions() -> list[dict[str, Any]]:
    return json.loads(DATASET.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    replacements = {
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    value = value.lower()
    return "".join(replacements.get(ch, ch) for ch in value)


@app.get("/health")
def health() -> dict[str, Any]:
    sessions = load_sessions()
    return {
        "ok": True,
        "dataset": str(DATASET.name),
        "sessions": len(sessions),
    }


@app.get("/event")
def event_info() -> dict[str, Any]:
    return {
        "event": "TDC Floripa 2026",
        "location": "CentroSul - Florianopolis",
        "dates": ["2026-07-22", "2026-07-23", "2026-07-24"],
        "format": "Presencial e Online",
        "official_url": "https://thedevconf.com/tdc/2026/florianopolis/",
        "journeys_url": "https://thedevconf.com/tdc/2026/florianopolis/jornadas/",
        "registration_url": "https://thedevconf.com/tdc/2026/florianopolis/inscricoes",
    }


@app.get("/tracks")
def tracks(day: str | None = Query(default=None, description="Dia no formato 22/jul, 23/jul ou 24/jul")) -> dict[str, Any]:
    sessions = load_sessions()
    filtered = sessions
    if day:
        day_n = normalize(day)
        filtered = [s for s in sessions if normalize(s.get("date", "")) == day_n]

    tracks = sorted({s["track"] for s in filtered if s.get("track")})
    return {
        "day": day,
        "count": len(tracks),
        "tracks": tracks,
    }


@app.get("/sessions")
def sessions(
    day: str | None = Query(default=None, description="Dia no formato 22/jul, 23/jul ou 24/jul"),
    track: str | None = Query(default=None, description="Nome ou parte do nome da trilha"),
    q: str | None = Query(default=None, description="Busca em titulo, descricao ou speakers"),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    all_sessions = load_sessions()
    result = all_sessions

    if day:
        day_n = normalize(day)
        result = [s for s in result if normalize(s.get("date", "")) == day_n]

    if track:
        track_n = normalize(track)
        result = [s for s in result if track_n in normalize(s.get("track", ""))]

    if q:
        q_n = normalize(q)
        def matches(session: dict[str, Any]) -> bool:
            haystack = " ".join(
                [
                    session.get("title", ""),
                    session.get("description", ""),
                    session.get("track", ""),
                    " ".join(session.get("speakers", [])),
                ]
            )
            return q_n in normalize(haystack)
        result = [s for s in result if matches(s)]

    return {
        "count": len(result),
        "items": result[:limit],
    }


@app.get("/speakers")
def speakers(q: str | None = Query(default=None, description="Busca por nome de speaker")) -> dict[str, Any]:
    sessions = load_sessions()
    speaker_map: dict[str, list[dict[str, str]]] = {}
    for session in sessions:
        for speaker in session.get("speakers", []):
            speaker_map.setdefault(speaker, []).append(
                {
                    "title": session.get("title", ""),
                    "track": session.get("track", ""),
                    "date": session.get("date", ""),
                    "time": session.get("time", ""),
                }
            )

    names = sorted(speaker_map)
    if q:
        q_n = normalize(q)
        names = [name for name in names if q_n in normalize(name)]

    return {
        "count": len(names),
        "items": [{"speaker": name, "sessions": speaker_map[name]} for name in names[:50]],
    }
