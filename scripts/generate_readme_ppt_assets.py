"""Generate PNG assets used by the README and demo deck."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics.barcode import qr


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GITHUB_URL = "https://github.com/LiviaFernandes/tdc-oci-ai-agents-lab"


COLORS = {
    "air": "#FCFBFA",
    "neutral": "#F5F4F2",
    "bark": "#312D2A",
    "sienna": "#AE562C",
    "ocean": "#2C5967",
    "ivy": "#759C6C",
    "rose": "#A36472",
    "line": "#706C66",
    "oracle": "#C74634",
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def rounded_box(draw, xy, fill, outline=COLORS["line"], width=2, radius=18):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def label(draw, text, x, y, size=24, fill=COLORS["bark"], bold=False, anchor=None):
    draw.text((x, y), text, fill=fill, font=font(size, bold), anchor=anchor)


def arrow(draw, start, end, fill=COLORS["line"], width=4, via=None):
    points = [start] + (via or []) + [end]
    draw.line(points, fill=fill, width=width)
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        points = [(x2, y2), (x2 - 16 * direction, y2 - 8), (x2 - 16 * direction, y2 + 8)]
    else:
        direction = 1 if y2 >= y1 else -1
        points = [(x2, y2), (x2 - 8, y2 - 16 * direction), (x2 + 8, y2 - 16 * direction)]
    draw.polygon(points, fill=fill)


def draw_icon_card(draw, xy, icon, title, subtitle, accent):
    x1, y1, x2, y2 = xy
    rounded_box(draw, xy, fill="#FFFFFF", outline=accent, radius=18)
    draw.ellipse((x1 + 22, y1 + 28, x1 + 82, y1 + 88), fill=accent, outline=accent)
    label(draw, icon, x1 + 52, y1 + 45, size=20, fill="#FFFFFF", bold=True, anchor="mm")
    label(draw, title, x1 + 102, y1 + 22, size=24, bold=True)
    if subtitle:
        y = y1 + 58
        for line in subtitle.split("\n"):
            label(draw, line, x1 + 102, y, size=17, fill="#504B45")
            y += 24


def generate_architecture_png():
    path = DOCS / "arquitetura-oci-ai-agents-tdc.png"
    img = Image.new("RGB", (1800, 980), COLORS["air"])
    draw = ImageDraw.Draw(img)

    label(draw, "Arquitetura da demo: OCI Generative AI Agents", 60, 36, size=38, bold=True)
    label(draw, "RAG para conhecimento do evento + Custom Tool para agenda estruturada", 60, 86, size=22, fill="#5B5650")

    rounded_box(draw, (55, 145, 505, 830), fill="#F5F4F2", outline="#9E9892", radius=24)
    label(draw, "Canais externos", 85, 178, size=28, bold=True)
    draw_icon_card(draw, (105, 245, 455, 355), "U", "Participante", "Pergunta no Telegram", COLORS["ocean"])
    draw_icon_card(draw, (105, 420, 455, 530), "TG", "Telegram Bot", "Webhook HTTPS", COLORS["ocean"])
    draw_icon_card(draw, (105, 595, 455, 725), "JS", "Render Backend", "Node.js\nOCI SDK + env vars", COLORS["ocean"])

    rounded_box(draw, (585, 145, 1735, 830), fill="#F5F4F2", outline="#9E9892", radius=24)
    label(draw, "OCI Region: us-phoenix-1 | Compartment: tdc-ai-agents-lab", 625, 178, size=27, bold=True)

    draw_icon_card(draw, (640, 250, 940, 375), "IAM", "IAM + Policies", "Grupo, API key\ne permissao", COLORS["rose"])
    draw_icon_card(draw, (1045, 250, 1345, 375), "EP", "Agent Endpoint", "Sessao + chat\nruntime", COLORS["sienna"])
    draw_icon_card(draw, (1410, 250, 1695, 375), "AI", "AI Agent", "Orquestra RAG,\ntools e LLM", COLORS["sienna"])

    draw_icon_card(draw, (640, 535, 940, 660), "OBJ", "Object Storage", "PDF base RAG\nTDC Floripa 2026", COLORS["ivy"])
    draw_icon_card(draw, (1045, 535, 1345, 660), "RAG", "Knowledge Base", "Busca semantica\nno PDF", COLORS["ivy"])
    draw_icon_card(draw, (1410, 535, 1695, 660), "API", "Custom Tool", "OpenAPI HTTP\nagenda estruturada", COLORS["sienna"])

    rounded_box(draw, (1260, 720, 1695, 790), fill="#FFF8F2", outline=COLORS["sienna"], radius=16)
    label(draw, "Private subnet + NAT Gateway", 1290, 736, size=20, bold=True)
    label(draw, "egress HTTPS para API publica da programacao", 1290, 762, size=17, fill="#504B45")

    # Clean lanes. All connectors pass between cards, never over text.
    arrow(draw, (280, 355), (280, 420), COLORS["ocean"])
    arrow(draw, (280, 530), (280, 595), COLORS["ocean"])
    arrow(draw, (455, 660), (1195, 250), COLORS["line"], via=[(540, 660), (540, 225), (1195, 225)])
    arrow(draw, (940, 315), (1045, 315), COLORS["rose"])
    arrow(draw, (1345, 315), (1410, 315), COLORS["sienna"])
    arrow(draw, (1550, 375), (1550, 535), COLORS["sienna"])
    arrow(draw, (1410, 598), (1345, 598), COLORS["ivy"])
    arrow(draw, (1045, 598), (940, 598), COLORS["ivy"])
    arrow(draw, (1550, 660), (1550, 720), COLORS["sienna"])
    arrow(draw, (1260, 755), (455, 755), COLORS["line"])

    label(draw, "pergunta", 304, 382, size=17, fill=COLORS["ocean"])
    label(draw, "webhook", 304, 556, size=17, fill=COLORS["ocean"])
    label(draw, "chamada assinada ao endpoint", 650, 205, size=18, fill=COLORS["line"])
    label(draw, "RAG", 970, 570, size=18, fill=COLORS["ivy"])
    label(draw, "tool call", 1568, 452, size=18, fill=COLORS["sienna"])
    label(draw, "consulta JSON da programacao", 690, 738, size=18, fill=COLORS["line"])

    rounded_box(draw, (55, 875, 1735, 940), fill="#FFFFFF", outline="#DFDCD8", radius=18)
    label(draw, "Resumo:", 90, 895, size=22, bold=True)
    label(draw, "o agente combina conhecimento nao estruturado do PDF com dados estruturados da agenda via Custom Tool.", 200, 896, size=20, fill="#504B45")

    img.save(path)
    return path


def generate_qr():
    path = DOCS / "github-qr.png"
    widget = qr.QrCodeWidget(GITHUB_URL)
    widget.qr.make()
    count = widget.qr.moduleCount
    scale = 10
    quiet = 4
    size = (count + quiet * 2) * scale
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    for row in range(count):
        for col in range(count):
            if widget.qr.isDark(row, col):
                x1 = (col + quiet) * scale
                y1 = (row + quiet) * scale
                draw.rectangle((x1, y1, x1 + scale - 1, y1 + scale - 1), fill="black")
    image = image.resize((360, 360), Image.Resampling.NEAREST)
    image.save(path)
    return path


if __name__ == "__main__":
    DOCS.mkdir(parents=True, exist_ok=True)
    print(generate_architecture_png())
    print(generate_qr())
