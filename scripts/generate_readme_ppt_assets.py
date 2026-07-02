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


def arrow(draw, start, end, fill=COLORS["line"], width=4):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        points = [(x2, y2), (x2 - 16 * direction, y2 - 8), (x2 - 16 * direction, y2 + 8)]
    else:
        direction = 1 if y2 >= y1 else -1
        points = [(x2, y2), (x2 - 8, y2 - 16 * direction), (x2 + 8, y2 - 16 * direction)]
    draw.polygon(points, fill=fill)


def draw_component(draw, xy, title, subtitle, fill, outline=None):
    x1, y1, x2, y2 = xy
    rounded_box(draw, xy, fill=fill, outline=outline or COLORS["line"], radius=16)
    label(draw, title, x1 + 22, y1 + 20, size=25, bold=True)
    if subtitle:
        y = y1 + 56
        for line in subtitle.split("\n"):
            label(draw, line, x1 + 22, y, size=18, fill="#504B45")
            y += 24


def generate_architecture_png():
    path = DOCS / "arquitetura-oci-ai-agents-tdc.png"
    img = Image.new("RGB", (1800, 1040), COLORS["air"])
    draw = ImageDraw.Draw(img)

    label(draw, "Arquitetura da demo: OCI Generative AI Agents + RAG + Custom Tool", 60, 38, size=38, bold=True)
    label(draw, "Fluxo opcional com Telegram, backend Render e Agent Endpoint na OCI", 60, 88, size=22, fill="#5B5650")

    rounded_box(draw, (55, 150, 540, 870), fill="#F5F4F2", outline="#9E9892", radius=24)
    label(draw, "Canais externos", 85, 180, size=28, bold=True)
    draw_component(draw, (105, 245, 490, 345), "Participante", "Pergunta no Telegram", "#FFFFFF", COLORS["ocean"])
    draw_component(draw, (105, 410, 490, 535), "Telegram Bot", "Webhook para o backend", "#FFFFFF", COLORS["ocean"])
    draw_component(draw, (105, 600, 490, 740), "Render Web Service", "Node.js\nOCI SDK + env vars", "#FFFFFF", COLORS["ocean"])
    draw_component(draw, (105, 780, 490, 845), "API Programacao TDC", "JSON estruturado", "#FFFFFF", COLORS["ocean"])

    rounded_box(draw, (610, 150, 1735, 870), fill="#F5F4F2", outline="#9E9892", radius=24)
    label(draw, "OCI Region: us-phoenix-1", 645, 180, size=28, bold=True)
    rounded_box(draw, (645, 230, 1695, 830), fill="#FCFBFA", outline="#9E9892", radius=18)
    label(draw, "Compartment: tdc-ai-agents-lab", 675, 260, size=23, bold=True)

    draw_component(draw, (690, 330, 950, 455), "IAM + Policies", "Grupo tdc-ai-agents-users\nAPI key do backend", "#FFFFFF", COLORS["rose"])
    draw_component(draw, (1010, 315, 1290, 455), "Agent Endpoint", "Sessao + chat runtime", "#FFFFFF", COLORS["sienna"])
    draw_component(draw, (1370, 315, 1645, 455), "AI Agent", "Orquestra RAG, tools\ne modelo LLM", "#FFFFFF", COLORS["sienna"])
    draw_component(draw, (1010, 535, 1290, 675), "Knowledge Base", "RAG sobre PDF do evento", "#FFFFFF", COLORS["ivy"])
    draw_component(draw, (690, 535, 950, 675), "Object Storage", "PDF base RAG\nTDC Floripa 2026", "#FFFFFF", COLORS["ivy"])
    draw_component(draw, (1370, 535, 1645, 675), "Custom Tool HTTP", "Busca sessoes, trilhas\ne speakers", "#FFFFFF", COLORS["sienna"])
    rounded_box(draw, (1305, 720, 1680, 790), fill="#FFF8F2", outline=COLORS["sienna"], radius=14)
    label(draw, "VCN private subnet + NAT Gateway", 1330, 738, size=19, bold=True)
    label(draw, "egress HTTPS para a tool", 1330, 763, size=17, fill="#504B45")

    arrow(draw, (300, 345), (300, 410), COLORS["ocean"])
    arrow(draw, (300, 535), (300, 600), COLORS["ocean"])
    arrow(draw, (490, 670), (1010, 385), COLORS["line"])
    arrow(draw, (1290, 385), (1370, 385), COLORS["sienna"])
    arrow(draw, (1495, 455), (1495, 535), COLORS["sienna"])
    arrow(draw, (1370, 605), (1290, 605), COLORS["ivy"])
    arrow(draw, (1010, 605), (950, 605), COLORS["ivy"])
    arrow(draw, (1495, 675), (1495, 720), COLORS["sienna"])
    arrow(draw, (1325, 755), (490, 815), COLORS["line"])

    label(draw, "1 pergunta", 325, 370, size=17, fill=COLORS["ocean"])
    label(draw, "2 webhook", 325, 560, size=17, fill=COLORS["ocean"])
    label(draw, "3 chamada assinada ao Agent Endpoint", 585, 500, size=18, fill=COLORS["line"])
    label(draw, "4 RAG + tool call", 1320, 500, size=18, fill=COLORS["sienna"])
    label(draw, "5 consulta API de programacao", 775, 790, size=18, fill=COLORS["line"])

    rounded_box(draw, (55, 910, 1735, 1000), fill="#FFFFFF", outline="#DFDCD8", radius=18)
    label(draw, "Demo em uma frase:", 90, 935, size=22, bold=True)
    label(
        draw,
        "um agente OCI responde sobre o TDC usando RAG para conhecimento nao estruturado e Custom Tool para dados estruturados.",
        325,
        936,
        size=20,
        fill="#504B45",
    )

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
