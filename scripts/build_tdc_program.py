#!/usr/bin/env python3
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


BASE_URL = "https://thedevconf.com"
EVENT_URL = "https://thedevconf.com/tdc/2026/florianopolis/"
JOURNEYS_URL = "https://thedevconf.com/tdc/2026/florianopolis/jornadas/"


@dataclass
class Session:
    track: str
    title: str
    date: str
    time: str
    speakers: list[str]
    description: str
    source_url: str


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
        if not self.skip and tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
        if not self.skip and tag in {"p", "div", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        value = " ".join(unescape(data).split())
        if value:
            self.parts.append(value + " ")

    def text(self):
        lines = []
        for line in "".join(self.parts).splitlines():
            clean = " ".join(line.split())
            if clean:
                lines.append(clean)
        return "\n".join(lines)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def text_from_html(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def strip_tags(html: str) -> str:
    return " ".join(text_from_html(html).split())


def discover_pages(home_html: str) -> list[str]:
    links = sorted(
        set(
            re.findall(
                r'href="(/tdc/2026/florianopolis/(?:trilha|forum|workshops|hub|community)[^"]*)"',
                home_html,
            )
        )
    )
    return [urllib.parse.urljoin(BASE_URL, link) for link in links]


def page_title(html: str) -> str:
    match = re.search(r'<h2 class="titulo-trilha">\s*(.*?)\s*</h2>', html, re.S)
    if match:
        return strip_tags(match.group(1)).replace("Trilha:", "").strip()
    match = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if match:
        title = strip_tags(match.group(1))
        title = title.replace("#TheDevConf 2026 |", "").replace("TDC Florianópolis 2026", "")
        title = title.replace("Trilha:", "").strip(" |")
        return title or "TDC Floripa 2026"
    return "TDC Floripa 2026"


def parse_sessions(html: str, source_url: str) -> tuple[str, list[Session]]:
    track = page_title(html)
    blocks = re.findall(
        r'<div class="single-schedules-inner[^"]*"[^>]*data-id="([^"]+)"[^>]*>(.*?)(?=<div class="single-schedules-inner|\Z)',
        html,
        re.S,
    )
    sessions = []
    for _sid, block in blocks:
        title_match = re.search(r'<p class="title">(.*?)</p>', block, re.S)
        if not title_match:
            continue
        title = strip_tags(title_match.group(1))
        if not title or title.lower() in {"almoço", "almoco"}:
            continue

        date_match = re.search(r'<div class="date"[^>]*>(.*?)</div>', block, re.S)
        hour_match = re.search(r'<div class="hour"[^>]*>(.*?)</div>', block, re.S)
        date = strip_tags(date_match.group(1)) if date_match else ""
        hour = strip_tags(hour_match.group(1)) if hour_match else ""

        speakers = []
        for speaker_block in re.findall(r'<div class="speaker">(.*?)</div>', block, re.S):
            a = re.search(r'<a [^>]*title="Clique para saber mais sobre ([^"]+)"', speaker_block)
            if a:
                name = unescape(a.group(1)).strip()
                if name and name not in speakers:
                    speakers.append(name)

        desc = ""
        modal_match = re.search(r'<div class="modal-body">(.*?)<div class="modal-footer">', block, re.S)
        if modal_match:
            desc = strip_tags(modal_match.group(1))
            desc = re.sub(r"Palestrantes?.*$", "", desc).strip()

        sessions.append(
            Session(
                track=track,
                title=title,
                date=date,
                time=hour,
                speakers=speakers,
                description=desc,
                source_url=source_url,
            )
        )
    return track, sessions


def write_markdown(path: Path, sessions: list[Session]):
    by_track = {}
    for session in sessions:
        by_track.setdefault(session.track, []).append(session)

    lines = [
        "# Programacao TDC Floripa 2026",
        "",
        f"Fonte principal: {EVENT_URL}",
        f"Fonte de jornadas: {JOURNEYS_URL}",
        "Dados coletados do site oficial no momento da geracao deste arquivo.",
        "",
        "Observacao: a programacao do evento pode mudar. Confirme sempre no site oficial antes de publicar uma versao final.",
        "",
    ]
    for track in sorted(by_track):
        lines += [f"## {track}", ""]
        for s in by_track[track]:
            speakers = ", ".join(s.speakers) if s.speakers else "Speakers nao publicados ou nao identificados"
            lines += [
                f"### {s.title}",
                "",
                f"- Data: {s.date or 'Nao informada'}",
                f"- Horario: {s.time or 'Nao informado'}",
                f"- Speakers: {speakers}",
                f"- Fonte: {s.source_url}",
                "",
            ]
            if s.description:
                lines += [s.description, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_pdf(path: Path, sessions: list[Session]):
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TrackTitle", parent=styles["Heading2"], textColor=colors.HexColor("#C74634"), spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle(name="SessionTitle", parent=styles["Heading3"], fontSize=11, leading=13, spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#555555")))

    story = []
    story.append(Paragraph("Programacao TDC Floripa 2026", styles["Title"]))
    story.append(Paragraph("Agenda com trilhas, sessoes e speakers coletados do site oficial do TDC.", styles["BodyText"]))
    story.append(Paragraph(f"Fonte: {EVENT_URL}", styles["Small"]))
    story.append(Paragraph("Observacao: confirme mudancas no site oficial antes de publicar a versao final.", styles["Small"]))
    story.append(Spacer(1, 12))

    by_track = {}
    for session in sessions:
        by_track.setdefault(session.track, []).append(session)

    first = True
    for track in sorted(by_track):
        if not first:
            story.append(PageBreak())
        first = False
        story.append(Paragraph(track, styles["TrackTitle"]))
        for s in by_track[track]:
            speakers = ", ".join(s.speakers) if s.speakers else "Speakers nao publicados ou nao identificados"
            story.append(Paragraph(s.title, styles["SessionTitle"]))
            story.append(Paragraph(f"{s.date or 'Data nao informada'} | {s.time or 'Horario nao informado'} | {speakers}", styles["Small"]))
            if s.description:
                story.append(Paragraph(s.description[:900], styles["BodyText"]))
            story.append(Spacer(1, 6))
    doc.build(story)


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = out_dir / "_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    home_html = fetch(EVENT_URL)
    (cache_dir / "home.html").write_text(home_html, encoding="utf-8")
    pages = discover_pages(home_html)

    sessions = []
    for url in pages:
        name = urllib.parse.urlparse(url).path.strip("/").replace("/", "__")
        if urllib.parse.urlparse(url).query:
            name += "__" + urllib.parse.urlparse(url).query.replace("=", "-")
        html_path = cache_dir / f"{name}.html"
        if html_path.exists():
            html = html_path.read_text(encoding="utf-8")
        else:
            print(f"Fetching {url}")
            html = fetch(url)
            html_path.write_text(html, encoding="utf-8")
            time.sleep(0.1)
        _track, parsed = parse_sessions(html, url)
        sessions.extend(parsed)

    sessions = sorted(sessions, key=lambda s: (s.date, s.time, s.track, s.title))
    json_path = out_dir / "programacao_tdc_floripa_2026.json"
    md_path = out_dir / "programacao_tdc_floripa_2026.md"
    pdf_path = out_dir / "programacao_tdc_floripa_2026.pdf"

    json_path.write_text(json.dumps([asdict(s) for s in sessions], ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, sessions)
    write_pdf(pdf_path, sessions)
    print(f"Generated {len(sessions)} sessions")
    print(json_path)
    print(md_path)
    print(pdf_path)


if __name__ == "__main__":
    main()
