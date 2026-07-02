#!/usr/bin/env python3
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ASSETS / "base_rag_tdc_floripa_2026.pdf"


def clean_line(line: str) -> str:
    return line.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add_markdown(story, md_path: Path, styles, title: str):
    story.append(Paragraph(title, styles["Section"]))
    story.append(Spacer(1, 8))

    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean_line(line[2:]), styles["Section"]))
        elif line.startswith("## "):
            story.append(Paragraph(clean_line(line[3:]), styles["Subsection"]))
        elif line.startswith("### "):
            story.append(Paragraph(clean_line(line[4:]), styles["ItemTitle"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + clean_line(line[2:]), styles["RagBullet"]))
        else:
            story.append(Paragraph(clean_line(line), styles["Body"]))


def main():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading1"],
            fontSize=17,
            leading=21,
            textColor=colors.HexColor("#C74634"),
            spaceBefore=8,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subsection",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#111111"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ItemTitle",
            parent=styles["Heading3"],
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#245B8F"),
            spaceBefore=6,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=11,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RagBullet",
            parent=styles["Body"],
            leftIndent=12,
            firstLineIndent=-8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#555555"),
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm,
    )

    story = [
        Paragraph("Base RAG - TDC Floripa 2026", styles["Title"]),
        Paragraph(
            "Arquivo unico para upload no Object Storage e ingestao no OCI Generative AI Agents.",
            styles["BodyText"],
        ),
        Paragraph(
            "Inclui visao geral, FAQ, jornadas, trilhas, programacao, sessoes e speakers coletados das paginas oficiais do TDC.",
            styles["Small"],
        ),
        Paragraph("Fontes: https://thedevconf.com/tdc/2026/florianopolis/ e /jornadas/", styles["Small"]),
        Spacer(1, 14),
    ]

    add_markdown(story, ASSETS / "tdc_floripa_2026_oficial.md", styles, "Informacoes oficiais curadas")
    story.append(PageBreak())
    add_markdown(story, ASSETS / "programacao_tdc_floripa_2026.md", styles, "Programacao oficial com speakers")

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
