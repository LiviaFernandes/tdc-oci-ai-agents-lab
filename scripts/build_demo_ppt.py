"""Build a short Redwood-style PowerPoint for the OCI AI Agents demo."""

from pathlib import Path
import shutil

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TEMPLATE = Path(
    "/Users/liviarodrigues/Documents/Codex/2026-06-18/"
    "redwood-powerpoint-creator-plugin-redwood-powerpoint/work/presentations/"
    "data-ai-lad-team-demos/tmp/template-starter.pptx"
)
OUTPUT = DOCS / "tdc-oci-ai-agents-demo-oracle.pptx"
ARCH = DOCS / "arquitetura-oci-ai-agents-tdc.png"
QR = DOCS / "github-qr.png"
GITHUB_URL = "https://github.com/LiviaFernandes/tdc-oci-ai-agents-lab"


COLORS = {
    "bark": RGBColor(49, 45, 42),
    "muted": RGBColor(92, 86, 80),
    "sienna": RGBColor(174, 86, 44),
    "ocean": RGBColor(44, 89, 103),
    "ivy": RGBColor(117, 156, 108),
    "rose": RGBColor(163, 100, 114),
    "air": RGBColor(252, 251, 250),
    "neutral": RGBColor(245, 244, 242),
    "oracle": RGBColor(199, 70, 52),
    "white": RGBColor(255, 255, 255),
}


def remove_slide(prs, index):
    slide_id_list = prs.slides._sldIdLst
    slide_id = slide_id_list[index]
    prs.part.drop_rel(slide_id.rId)
    del slide_id_list[index]


def delete_shape(shape):
    element = shape._element
    element.getparent().remove(element)


def clear_prompt_text(slide):
    stale_terms = [
        "CX Title",
        "Subhead goes here",
        "Name",
        "Presenter",
        "Title on a light",
        "Subtitle",
        "Main paragraph",
        "First level bullet",
        "An end slide",
    ]
    for shape in list(slide.shapes):
        text = shape.text.strip() if hasattr(shape, "text") else ""
        if text and any(term in text for term in stale_terms):
            delete_shape(shape)


def set_shape_text(shape, text, size=6, color="muted"):
    frame = shape.text_frame
    frame.clear()
    p = frame.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.name = "Oracle Sans"
    run.font.size = Pt(size)
    run.font.color.rgb = COLORS[color]


def normalize_template_footer(slide, slide_number):
    for shape in slide.shapes:
        if not hasattr(shape, "text"):
            continue
        text = shape.text.strip()
        if not text:
            continue
        if "Copyright" in text:
            set_shape_text(
                shape,
                "Copyright © 2026, Oracle and/or its affiliates | Confidential: Internal",
                size=6,
                color="muted",
            )
        elif text.isdigit():
            set_shape_text(shape, str(slide_number), size=6, color="muted")


def textbox(slide, text, x, y, w, h, size=24, bold=False, color="bark", align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Oracle Sans"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = COLORS[color]
    return box


def bullets(slide, items, x, y, w, h, size=19, color="bark"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    for idx, item in enumerate(items):
        p = frame.paragraphs[0] if idx == 0 else frame.add_paragraph()
        p.text = item
        p.level = 0
        p.font.name = "Oracle Sans"
        p.font.size = Pt(size)
        p.font.color.rgb = COLORS[color]
        p.space_after = Pt(10)
    return box


def pill(slide, text, x, y, w, h, fill="neutral", line="sienna", size=15):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLORS[fill]
    shape.line.color.rgb = COLORS[line]
    shape.line.width = Pt(1.25)
    frame = shape.text_frame
    frame.clear()
    frame.margin_left = Inches(0.12)
    frame.margin_right = Inches(0.12)
    p = frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.name = "Oracle Sans"
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = COLORS["bark"]
    return shape


def add_link(slide, text, x, y, w, h):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    p = frame.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.hyperlink.address = GITHUB_URL
    run.font.name = "Oracle Sans"
    run.font.size = Pt(16)
    run.font.color.rgb = COLORS["ocean"]
    return box


def build():
    DOCS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE, OUTPUT)
    prs = Presentation(str(OUTPUT))

    # Keep a single light content slide from the Redwood starter.
    for index in [8, 7, 6, 5, 4, 3, 2, 0]:
        remove_slide(prs, index)

    slides = list(prs.slides)
    for slide in slides:
        clear_prompt_text(slide)
    for idx, slide in enumerate(slides, start=1):
        normalize_template_footer(slide, idx)

    s = slides[0]
    textbox(s, "Lab TDC: AI Agents na OCI", 0.55, 0.35, 6.5, 0.45, size=27, bold=True)
    textbox(s, "Arquitetura, QR code e resumo da demo", 0.57, 0.82, 5.4, 0.28, size=14, color="muted")

    s.shapes.add_picture(str(ARCH), Inches(0.45), Inches(1.25), width=Inches(8.35), height=Inches(4.55))
    s.shapes.add_picture(str(QR), Inches(10.15), Inches(0.72), width=Inches(1.85), height=Inches(1.85))
    textbox(s, "GitHub do lab", 10.0, 2.62, 2.15, 0.25, size=13, bold=True, align=PP_ALIGN.CENTER)

    textbox(s, "O que a demo ensina", 9.15, 3.15, 3.5, 0.35, size=20, bold=True)
    bullets(
        s,
        [
            "Agent com RAG: PDF do evento como base de conhecimento.",
            "Custom Tool: agenda e speakers via API estruturada.",
            "Endpoint real: consumo pelo Telegram usando backend Render.",
        ],
        9.15,
        3.62,
        3.45,
        1.8,
        size=15,
        color="bark",
    )
    pill(s, "RAG + Tools + Endpoint", 9.25, 5.72, 3.0, 0.42, fill="neutral", line="sienna", size=13)
    add_link(s, GITHUB_URL, 0.6, 6.67, 7.4, 0.28)

    prs.save(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    print(build())
