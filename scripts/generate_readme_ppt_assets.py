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
    label(draw, title, x1 + 24, y1 + 22, size=24, bold=True)
    if subtitle:
        y = y1 + 58
        for line in subtitle.split("\n"):
            label(draw, line, x1 + 24, y, size=17, fill="#504B45")
            y += 24


def generate_architecture_png():
    path = DOCS / "arquitetura-oci-ai-agents-tdc.png"
    img = Image.new("RGB", (1800, 980), COLORS["air"])
    draw = ImageDraw.Draw(img)

    label(draw, "Arquitetura da demo: OCI Generative AI Agents", 60, 36, size=38, bold=True)
    label(draw, "RAG para conhecimento do evento + Custom Tool para consulta HTTP estruturada", 60, 86, size=22, fill="#5B5650")

    rounded_box(draw, (55, 145, 470, 760), fill="#F5F4F2", outline="#9E9892", radius=24)
    label(draw, "Canais externos", 85, 178, size=28, bold=True)
    draw_icon_card(draw, (100, 250, 425, 350), "U", "Participante", "Pergunta no Telegram", COLORS["ocean"])
    draw_icon_card(draw, (100, 420, 425, 520), "TG", "Telegram Bot", "Webhook HTTPS", COLORS["ocean"])
    draw_icon_card(draw, (100, 590, 425, 710), "JS", "Backend", "Node.js\nOCI SDK + env vars", COLORS["ocean"])

    rounded_box(draw, (545, 145, 1550, 760), fill="#F5F4F2", outline="#9E9892", radius=24)
    label(draw, "OCI Region: us-phoenix-1", 585, 178, size=27, bold=True)
    rounded_box(draw, (585, 225, 1510, 725), fill="#FCFBFA", outline="#9E9892", radius=18)
    label(draw, "Compartment: tdc-ai-agents-lab", 615, 252, size=22, bold=True)

    draw_icon_card(draw, (635, 315, 900, 440), "EP", "Agent Endpoint", "Sessao + chat\nruntime", COLORS["sienna"])
    draw_icon_card(draw, (1010, 315, 1275, 440), "AI", "AI Agent", "Orquestra RAG,\ntools e LLM", COLORS["sienna"])

    draw_icon_card(draw, (635, 535, 900, 660), "OBJ", "Object Storage", "PDF base RAG\nTDC Floripa 2026", COLORS["ivy"])
    draw_icon_card(draw, (1010, 535, 1275, 660), "RAG", "Knowledge Base", "Busca semantica\nno PDF", COLORS["ivy"])
    draw_icon_card(draw, (1320, 315, 1495, 440), "API", "Custom Tool", "OpenAPI\nHTTP tool", COLORS["sienna"])

    rounded_box(draw, (1320, 535, 1490, 670), fill="#FFF8F2", outline=COLORS["sienna"], radius=16)
    label(draw, "VCN", 1345, 555, size=20, bold=True)
    label(draw, "Private subnet", 1345, 582, size=17, fill="#504B45")
    label(draw, "NAT Gateway", 1345, 606, size=17, fill="#504B45")
    label(draw, "egress HTTPS", 1345, 630, size=17, fill="#504B45")

    rounded_box(draw, (1590, 535, 1740, 670), fill="#FFFFFF", outline=COLORS["ocean"], radius=18)
    label(draw, "API HTTP", 1615, 555, size=21, bold=True)
    label(draw, "Programacao", 1615, 584, size=17, fill="#504B45")
    label(draw, "TDC", 1615, 608, size=17, fill="#504B45")
    label(draw, "JSON", 1615, 632, size=17, fill="#504B45")

    # Clean runtime and egress lanes. The NAT path belongs only to the Custom Tool.
    arrow(draw, (263, 350), (263, 420), COLORS["ocean"])
    arrow(draw, (263, 520), (263, 590), COLORS["ocean"])
    arrow(draw, (425, 650), (635, 377), COLORS["line"], via=[(500, 650), (500, 377)])
    arrow(draw, (900, 377), (1010, 377), COLORS["sienna"])
    arrow(draw, (1275, 377), (1320, 377), COLORS["sienna"])
    arrow(draw, (1142, 440), (1142, 535), COLORS["ivy"])
    arrow(draw, (1010, 598), (900, 598), COLORS["ivy"])
    arrow(draw, (1408, 440), (1408, 535), COLORS["sienna"])
    arrow(draw, (1490, 602), (1590, 602), COLORS["line"])

    rounded_box(draw, (55, 835, 1740, 920), fill="#FFFFFF", outline="#DFDCD8", radius=18)
    label(draw, "Resumo:", 90, 862, size=22, bold=True)
    label(draw, "o Agent Endpoint recebe a pergunta; o Agent combina RAG no PDF com chamada HTTP estruturada via Custom Tool.", 200, 863, size=20, fill="#504B45")

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
