"""Generate the OCI AI Agents lab architecture diagram."""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = Path(
    "/Users/liviarodrigues/.codex/plugins/cache/ai-factory/"
    "oci-drawio-architect/1.0.0/skills"
)
os.environ.setdefault("OCI_SVG_DIR", str(SKILL_DIR / "icons"))

from drawio_builder import DrawioBuilder, COLORS, add_icons_to_map  # noqa: E402


add_icons_to_map(
    {
        "external_cloud": "general/cloud.svg",
        "unknown": "general/unknown.svg",
        "compartment": "identity_and_security/identity_and_security_compartments.svg",
    }
)


def build_diagram() -> Path:
    out_path = ROOT / "docs" / "arquitetura-oci-ai-agents-tdc.drawio"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Canvas layout:
    # External systems: x=30, y=105, w=530, h=780 -> bottom 885
    # OCI region:       x=595, y=105, w=1125, h=780 -> bottom 885
    # Notes:            x=30, y=905, w=1690, h=120 -> bottom 1025
    d = DrawioBuilder(page_name="OCI AI Agents TDC Lab", width=1760, height=1060)

    d.add_text(
        "<b>Arquitetura do Lab: OCI Generative AI Agents + RAG + Custom Tool</b>"
        "<br/><i>TDC Floripa 2026 | canais externos, backend, OCI AI Agents e API HTTP</i>",
        x=24,
        y=18,
        w=980,
        h=58,
        font_size=18,
        font_style=1,
        font_family="Georgia",
    )

    external = d.add_group(
        "Canais externos e API publica",
        x=30,
        y=105,
        w=530,
        h=780,
        group_type="hub",
    )
    attendee = d.add_primary_icon("Participante", "user", 45, 70, parent=external)
    telegram = d.add_primary_icon("Telegram Bot", "external_cloud", 215, 70, parent=external)
    backend = d.add_primary_icon("Backend", "api_service", 215, 255, parent=external)
    public_api = d.add_primary_icon("API Programacao TDC", "external_cloud", 215, 575, parent=external)

    d.add_text(
        "Backend Node.js<br/>Webhook /telegram/webhook<br/>chamada assinada OCI SDK",
        x=340,
        y=260,
        w=150,
        h=78,
        parent=external,
        font_size=10,
    )

    region = d.add_group(
        "OCI Region: Phoenix (us-phoenix-1)",
        x=595,
        y=105,
        w=1125,
        h=780,
        group_type="region",
    )
    compartment = d.add_group(
        "Compartment: tdc-ai-agents-lab",
        x=25,
        y=52,
        w=1075,
        h=700,
        parent=region,
        group_type="compartment",
    )

    obs_panel = d.add_group(
        "Operacao opcional",
        x=30,
        y=50,
        w=270,
        h=205,
        parent=compartment,
        group_type="services",
    )
    logging = d.add_secondary_icon("Logging", "logging", 35, 70, parent=obs_panel)
    monitoring = d.add_secondary_icon("Monitoring", "monitoring", 160, 70, parent=obs_panel)

    genai_panel = d.add_group(
        "OCI Generative AI Agents",
        x=330,
        y=50,
        w=700,
        h=300,
        parent=compartment,
        group_type="services",
    )
    endpoint = d.add_primary_icon("Agent Endpoint", "api_gateway", 35, 55, parent=genai_panel)
    agent = d.add_primary_icon("AI Agent", "ai", 205, 55, parent=genai_panel)
    kb = d.add_primary_icon("Knowledge Base", "data_catalog", 375, 55, parent=genai_panel)
    tool = d.add_primary_icon("Custom Tool HTTP", "api_service", 545, 55, parent=genai_panel)
    model = d.add_secondary_icon("LLM Model", "ml", 205, 200, parent=genai_panel)

    data_panel = d.add_group(
        "Dados do RAG",
        x=330,
        y=390,
        w=315,
        h=220,
        parent=compartment,
        group_type="services",
    )
    bucket = d.add_primary_icon("Object Storage Bucket", "object_storage", 40, 60, parent=data_panel)
    pdf = d.add_primary_icon("PDF base TDC", "buckets", 185, 60, parent=data_panel)

    vcn = d.add_group(
        "VCN: tdc-ai-agents-vcn",
        x=685,
        y=390,
        w=345,
        h=220,
        parent=compartment,
        group_type="vcn",
    )
    subnet = d.add_group(
        "Private subnet para Custom Tool",
        x=25,
        y=45,
        w=295,
        h=145,
        parent=vcn,
        group_type="subnet",
    )
    nat = d.add_secondary_icon("NAT Gateway", "nat_gateway", 30, 55, parent=subnet)
    route = d.add_secondary_icon("Route Table", "route_table", 155, 55, parent=subnet)

    # Main product flow.
    d.add_labeled_edge(
        attendee,
        telegram,
        "",
        label_x=150,
        label_y=180,
        parent=external,
        exit_x=1.0,
        exit_y=0.5,
        entry_x=0.0,
        entry_y=0.5,
    )
    d.add_labeled_edge(
        telegram,
        backend,
        "",
        label_x=270,
        label_y=210,
        parent=external,
        exit_x=0.5,
        exit_y=1.0,
        entry_x=0.5,
        entry_y=0.0,
    )
    d.add_labeled_edge(
        backend,
        endpoint,
        "",
        label_x=550,
        label_y=385,
        parent="1",
        exit_x=1.0,
        exit_y=0.5,
        entry_x=0.0,
        entry_y=0.5,
        waypoints=[(560, 430), (640, 430)],
    )

    # Agent internals.
    d.add_labeled_edge(
        endpoint,
        agent,
        "",
        label_x=900,
        label_y=230,
        parent=genai_panel,
        exit_x=1.0,
        exit_y=0.5,
        entry_x=0.0,
        entry_y=0.5,
    )
    d.add_labeled_edge(
        agent,
        kb,
        "",
        label_x=1070,
        label_y=230,
        parent=genai_panel,
        exit_x=1.0,
        exit_y=0.5,
        entry_x=0.0,
        entry_y=0.5,
    )
    d.add_labeled_edge(
        agent,
        tool,
        "",
        label_x=1190,
        label_y=365,
        parent=genai_panel,
        exit_x=1.0,
        exit_y=0.75,
        entry_x=0.0,
        entry_y=0.75,
        waypoints=[(1180, 245), (1180, 335)],
    )
    d.add_edge(agent, model, "inference", parent=genai_panel, exit_x=0.5, exit_y=1.0, entry_x=0.5, entry_y=0.0)

    d.add_labeled_edge(
        kb,
        bucket,
        "",
        label_x=1110,
        label_y=500,
        parent=compartment,
        exit_x=0.5,
        exit_y=1.0,
        entry_x=0.5,
        entry_y=0.0,
        waypoints=[(735, 365), (515, 365)],
    )
    d.add_edge(bucket, pdf, "", parent=data_panel, exit_x=1.0, exit_y=0.5, entry_x=0.0, entry_y=0.5)

    d.add_labeled_edge(
        tool,
        nat,
        "",
        label_x=1310,
        label_y=500,
        parent=compartment,
        exit_x=0.5,
        exit_y=1.0,
        entry_x=0.5,
        entry_y=0.0,
        waypoints=[(895, 365), (760, 365)],
    )
    d.add_labeled_edge(
        nat,
        public_api,
        "",
        label_x=640,
        label_y=730,
        parent="1",
        exit_x=0.0,
        exit_y=0.5,
        entry_x=1.0,
        entry_y=0.5,
        waypoints=[(645, 735), (560, 735)],
    )

    telemetry_bus = d.add_bus(
        "logs e metricas",
        x1=460,
        y1=640,
        x2=935,
        parent=compartment,
        lane="telemetry",
        dashed=True,
    )
    for anchor, node in [(0.12, endpoint), (0.34, agent), (0.60, tool), (0.86, nat)]:
        d.connect_to_bus(node, telemetry_bus, anchor=anchor, dashed=True, exit_x=0.5, exit_y=1.0)
    d.connect_from_bus(telemetry_bus, logging, anchor=0.08, dashed=True, entry_x=1.0, entry_y=0.5)
    d.connect_from_bus(telemetry_bus, monitoring, anchor=0.16, dashed=True, entry_x=1.0, entry_y=0.5)

    d.add_text(
        "<b>Notas para a demo</b><br/>"
        "• O chat do console prova o Agent. O Telegram mostra o endpoint como produto.<br/>"
        "• RAG usa o PDF do evento no Object Storage. A Custom Tool consulta a API estruturada da programacao.<br/>"
        "• O backend guarda token Telegram e credenciais OCI em env vars; nada sensivel fica no frontend.",
        x=30,
        y=905,
        w=1690,
        h=120,
        font_size=12,
    )

    d.write(out_path)
    return out_path


if __name__ == "__main__":
    print(build_diagram())
