"""Reusable draw.io builder for OCI architecture diagrams.

Provides the DrawioBuilder class, OCI SVG icon loading with viewBox fix,
Oracle template container styles, and PNG-in-SVG logo embedding.

Usage:
    1. Copy this file into your diagram script directory
    2. Icons are bundled in the plugin's icons/ directory (auto-detected)
    3. Override with OCI_SVG_DIR env var if needed
    4. Import and use:

        from drawio_builder import DrawioBuilder, add_icons_to_map
        add_icons_to_map({"my_icon": "networking/networking_vcn.svg"})
        d = DrawioBuilder(page_name="My Diagram", width=1600, height=1100)
        region = d.add_group("eu-frankfurt-1", 20, 75, 1560, 1000, group_type="region")
        d.add_icon("Load Balancer", "load_balancer", 50, 50, parent=region)
        d.write(Path("output.drawio"))
"""

import base64
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths - resolve icons directory with fallback chain:
#   1. OCI_SVG_DIR env var (explicit override)
#   2. Bundled icons/ directory (sibling to scripts/, inside plugin)
#   3. Legacy path ~/tests/oci-iconset/icons/svg
# ---------------------------------------------------------------------------
def _resolve_icon_dir() -> Path:
    env = os.environ.get("OCI_SVG_DIR")
    if env:
        return Path(env)
    bundled = Path(__file__).resolve().parent.parent / "icons"
    if bundled.is_dir():
        return bundled
    return Path.home() / "tests" / "oci-iconset" / "icons" / "svg"

OCI_SVG_DIR = _resolve_icon_dir()

# ---------------------------------------------------------------------------
# OCI Template Colors (from Oracle draw.io templates)
# ---------------------------------------------------------------------------
COLORS = {
    "region_fill": "#F5F4F2",
    "neutral_2": "#DFDCD8",
    "region_stroke": "#9E9892",
    "neutral_4": "#70736E",
    "air": "#FCFBFA",
    "ocean": "#2C5967",
    "vcn_stroke": "#AE562C",       # oracle orange for VCN/subnet borders
    "vcn_label": "#AE562C",        # same orange for VCN/subnet labels
    "text_primary": "#312D2A",     # charcoal for region/general text
    "rose": "#A36472",
    "ivy": "#759C6C",
    "oracle_red": "#C74634",
    "edge_color": "#312D2A",
    "edge_accent": "#AE562C",      # orange for accent edges
    "edge_purple": "#7B61FF",
}

ICON_W = 72
ICON_H = 72
PRIMARY_ICON_SIZE = 72
SECONDARY_ICON_SIZE = 60
CONNECTOR_ICON_W = 48
CONNECTOR_ICON_H = 36
LABEL_GAP = 2
LANE_GAP = 18

LANE_OFFSETS = {
    "ingress": 0,
    "hybrid": 1,
    "runtime": 2,
    "data": 3,
    "security": 4,
    "telemetry": 5,
    "async": 6,
}

# ---------------------------------------------------------------------------
# Icon key -> SVG file path (relative to OCI_SVG_DIR)
# ---------------------------------------------------------------------------
ICON_MAP = {
    "load_balancer": "networking/networking_load_balancer.svg",
    "flexible_lb": "networking/networking_flexible_load_balancer.svg",
    "vm": "compute/compute_virtual_machine_vm.svg",
    "autoscaling": "compute/compute_autoscaling.svg",
    "flex_vm": "compute/compute_flex_virtual_machine_flex_vm.svg",
    "burstable_vm": "compute/compute_burstable_virtual_machine_burstable_vm.svg",
    "instance_pools": "compute/compute_instance_pools.svg",
    "block_storage": "storage/storage_block_storage.svg",
    "object_storage": "storage/storage_object_storage.svg",
    "functions": "compute/compute_functions.svg",
    "autonomous_db": "database/database_autonomous_db.svg",
    "adw": "database/database_autonomous_data_warehouse_adw.svg",
    "atp": "database/database_autonomous_transaction_processing_atp.svg",
    "data_safe": "database/database_data_safe.svg",
    "db_system": "database/database_database_system.svg",
    "mysql": "database/database_mysql.svg",
    "nosql": "database/database_nosql.svg",
    "opensearch": "database/database_opensearch.svg",
    "nsg": "identity_and_security/identity_and_security_nsg.svg",
    "big_data": "analytics_and_ai/analytics_and_ai_big_data.svg",
    "data_catalog": "general/analytics_and_ai_amp_nbsp_data_catalog.svg",
    "data_flow": "general/analytics_and_ai_amp_nbsp_data_flow.svg",
    "data_integration": "general/analytics_and_ai_amp_nbsp_data_integration.svg",
    "service_gateway": "networking/networking_service_gateway.svg",
    "data_science": "analytics_and_ai/analytics_and_ai_data_science.svg",
    "ai": "analytics_and_ai/analytics_and_ai_artificial_intelligence.svg",
    "digital_assistant": "analytics_and_ai/analytics_and_ai_digital_assistant.svg",
    "ml": "analytics_and_ai/analytics_and_ai_machine_learning.svg",
    "connector_hub": "analytics_and_ai/analytics_and_ai_service_connector_hub.svg",
    "streaming": "analytics_and_ai/analytics_and_ai_streaming.svg",
    "vault": "identity_and_security/identity_and_security_vault.svg",
    "iam": "identity_and_security/identity_and_security_iam_identity_and_access_management.svg",
    "identity": "identity_and_security/identity_and_security_identity.svg",
    "user": "identity_and_security/identity_and_security_user.svg",
    "user_group": "identity_and_security/identity_and_security_user_group.svg",
    "policies": "identity_and_security/identity_and_security_policies.svg",
    "cloud_guard": "identity_and_security/identity_and_security_cloud_guard.svg",
    "key_mgmt": "identity_and_security/identity_and_security_key_management.svg",
    "key_vault": "identity_and_security/identity_and_security_key_vault.svg",
    "waf": "identity_and_security/identity_and_security_waf.svg",
    "certificates": "identity_and_security/identity_and_security_certificates.svg",
    "bastion": "identity_and_security/identity_and_security_bastion.svg",
    "devops": "developer_services/developer_services_devops.svg",
    "api_gateway": "developer_services/developer_services_api_gateway.svg",
    "api_service": "developer_services/developer_services_api_service.svg",
    "integrations": "developer_services/developer_services_integrations.svg",
    "oke": "developer_services/developer_services_container_engine_for_kubernetes.svg",
    "container_registry": "developer_services/developer_services_container_registry.svg",
    "notifications": "developer_services/developer_services_notifications.svg",
    "resource_manager": "developer_services/developer_services_resource_manager.svg",
    "service_mesh": "developer_services/developer_services_service_mesh.svg",
    "visual_builder": "developer_services/developer_services_visual_builder.svg",
    "buckets": "storage/storage_buckets.svg",
    "queuing": "observability_and_management/observability_and_management_queuing.svg",
    "logging": "observability_and_management/observability_and_management_logging.svg",
    "logging_analytics": "observability_and_management/observability_and_management_logging_analytics.svg",
    "apm": "observability_and_management/observability_and_management_application_performance_management.svg",
    "alarms": "observability_and_management/observability_and_management_alarms.svg",
    "monitoring": "observability_and_management/observability_and_management_monitoring.svg",
    "auditing": "observability_and_management/observability_and_management_auditing.svg",
    "search": "observability_and_management/observability_and_management_search.svg",
    "workflow": "observability_and_management/observability_and_management_workflow.svg",
    "flow_logs": "observability_and_management/observability_and_management_vcn_flow_logs.svg",
    "dns": "networking/networking_dns.svg",
    "cpe": "networking/networking_customer_premises_equipment_cpe.svg",
    "customer_dc": "networking/networking_customer_data_center.svg",
    "drg": "networking/networking_dynamic_routing_gateway_drg.svg",
    "nat_gateway": "networking/networking_nat_gateway.svg",
    "route_table": "networking/networking_route_table.svg",
    "firewall": "identity_and_security/identity_and_security_firewall.svg",
    "internet_gateway": "networking/networking_internet_gateway.svg",
    "vcn": "networking/networking_virtual_cloud_network_vcn.svg",
    "fastconnect": "physical/physical_special_connectors_fastconnect_horizontal.svg",
    "fastconnect_horizontal": "physical/physical_special_connectors_fastconnect_horizontal.svg",
    "fastconnect_vertical": "physical/physical_special_connectors_fastconnect_vertical.svg",
    "s2s_vpn": "physical/physical_special_connectors_site_to_site_vpn_vertical.svg",
    "site_to_site_vpn": "physical/physical_special_connectors_site_to_site_vpn_vertical.svg",
    "remote_peering": "physical/physical_special_connectors_remote_peering_horizontal.svg",
    "remote_peering_horizontal": "physical/physical_special_connectors_remote_peering_horizontal.svg",
    "remote_peering_vertical": "physical/physical_special_connectors_remote_peering_vertical.svg",
}


def add_icons_to_map(new_icons: dict[str, str]) -> None:
    """Add or override entries in the global ICON_MAP.

    Args:
        new_icons: dict of {key: "category/filename.svg"} paths relative to OCI_SVG_DIR.
    """
    ICON_MAP.update(new_icons)


# Cache: icon_key -> URL-encoded SVG data URI
_svg_cache: dict[str, str] = {}


def _load_svg(icon_key: str) -> str:
    """Load an SVG, fix viewBox to fit all content, return URL-encoded data URI.

    OCI SVGs sometimes have content that extends beyond the declared viewBox
    (translate offsets + scaled paths exceed the width/height). We compute the
    actual content bounds from the transform attributes and expand the viewBox.
    """
    if icon_key in _svg_cache:
        return _svg_cache[icon_key]

    import re
    import urllib.parse

    svg_path = OCI_SVG_DIR / ICON_MAP[icon_key]
    svg_text = svg_path.read_text()

    # Compute actual content bounds from translate+scale transforms.
    # Each <g transform="translate(tx,ty) scale(sx,sy)"> contains paths in
    # a 0-100 coordinate space, so the drawn area goes to (tx+100*sx, ty+100*sy).
    transforms = re.findall(
        r'translate\(([\d.]+),([\d.]+)\)\s*scale\(([\d.]+),([\d.]+)\)', svg_text)
    if transforms:
        max_x = max(float(tx) + 100 * float(sx) for tx, _, sx, _ in transforms)
        max_y = max(float(ty) + 100 * float(sy) for _, ty, _, sy in transforms)
        # Add small padding
        max_x = round(max_x + 2)
        max_y = round(max_y + 2)

        vb_m = re.search(r'viewBox="([^"]+)"', svg_text)
        if vb_m:
            parts = vb_m.group(1).split()
            cur_w, cur_h = float(parts[2]), float(parts[3])
            new_w = max(cur_w, max_x)
            new_h = max(cur_h, max_y)
            svg_text = svg_text.replace(
                f'viewBox="{vb_m.group(1)}"',
                f'viewBox="0 0 {new_w} {new_h}"')
            # Update width/height attributes to match
            svg_text = re.sub(r'\bwidth="\d+"', f'width="{int(new_w)}"', svg_text)
            svg_text = re.sub(r'\bheight="\d+"', f'height="{int(new_h)}"', svg_text)

    encoded = urllib.parse.quote(svg_text, safe='')
    data_uri = f"data:image/svg+xml,{encoded}"
    _svg_cache[icon_key] = data_uri
    return data_uri


# ---------------------------------------------------------------------------
# Group style templates (from Oracle draw.io templates)
# ---------------------------------------------------------------------------
_GROUP_STYLES = {
    "region": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "fillColor={region_fill};strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;"
        "fontColor={text_primary};verticalAlign=top;align=left;"
        "spacingLeft=3;spacingRight=5;container=1;collapsible=0;expand=0;"
    ),
    "compartment": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "fillColor={region_fill};strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;"
        "fontColor={text_primary};verticalAlign=top;align=left;"
        "spacingLeft=3;container=1;collapsible=0;expand=0;"
    ),
    "vcn": (
        "whiteSpace=wrap;html=1;rounded=0;"
        "strokeWidth=2;dashed=1;"
        "fillColor=none;strokeColor={vcn_stroke};"
        "labelBackgroundColor=none;"
        "fontFamily=Oracle Sans;fontSize=13;fontStyle=1;"
        "fontColor={vcn_label};verticalAlign=top;align=left;"
        "spacingLeft=3;container=1;collapsible=0;expand=0;"
    ),
    "subnet": (
        "whiteSpace=wrap;html=1;rounded=0;"
        "strokeWidth=1;dashed=1;"
        "fillColor=none;strokeColor={vcn_stroke};"
        "fontFamily=Oracle Sans;fontSize=11;fontStyle=1;"
        "fontColor={vcn_label};verticalAlign=top;align=left;"
        "spacingLeft=3;container=1;collapsible=0;expand=0;"
    ),
    "services": (
        "whiteSpace=wrap;html=1;rounded=0;"
        "strokeWidth=1;dashed=1;"
        "fillColor=none;strokeColor={text_primary};"
        "fontFamily=Oracle Sans;fontSize=11;fontStyle=1;"
        "fontColor={text_primary};verticalAlign=top;align=left;"
        "spacingLeft=3;container=1;collapsible=0;expand=0;"
    ),
    "hub": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "fillColor={region_fill};strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;"
        "fontColor={text_primary};verticalAlign=top;align=left;"
        "spacingLeft=3;container=1;collapsible=0;expand=0;"
    ),
    "availability_domain": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "fillColor={neutral_2};strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;"
        "fontColor={text_primary};verticalAlign=top;align=center;"
        "container=1;collapsible=0;expand=0;"
    ),
    "fault_domain": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "fillColor={air};strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=11;fontStyle=0;"
        "fontColor={text_primary};verticalAlign=top;align=center;"
        "container=1;collapsible=0;expand=0;"
    ),
    "tier": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "fillColor={region_fill};strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=11;fontStyle=0;"
        "fontColor={text_primary};verticalAlign=top;align=center;"
        "container=1;collapsible=0;expand=0;"
    ),
    "oracle_services_network": (
        "whiteSpace=wrap;html=1;rounded=0;"
        "strokeWidth=2;dashed=1;fillColor=none;strokeColor={region_stroke};"
        "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;"
        "fontColor={text_primary};verticalAlign=top;align=left;"
        "spacingLeft=3;container=1;collapsible=0;expand=0;"
    ),
    "metro_area": (
        "whiteSpace=wrap;html=1;rounded=1;arcSize=1;"
        "strokeWidth=1;dashed=1;fillColor={air};strokeColor={rose};"
        "fontFamily=Oracle Sans;fontSize=12;fontStyle=1;"
        "fontColor={rose};verticalAlign=top;align=center;"
        "container=1;collapsible=0;expand=0;"
    ),
}


# ---------------------------------------------------------------------------
# XML builder
# ---------------------------------------------------------------------------
class DrawioBuilder:
    """Builds a draw.io XML document.

    Typical usage:
        d = DrawioBuilder(page_name="Architecture", width=1600, height=1100)
        region = d.add_group("eu-frankfurt-1", 20, 75, 1560, 1000, group_type="region")
        vcn = d.add_group("VCN: MyVCN (10.0.0.0/16)", 20, 40, 1500, 900,
                          parent=region, group_type="vcn")
        d.add_icon("Load Balancer", "load_balancer", 50, 50, parent=vcn)
        d.add_edge(source_id, target_id, "443", parent=vcn)
        d.write(Path("output.drawio"))
    """

    def __init__(self, page_name="Architecture", width=1600, height=1100, grid=False):
        self._cell_id = 1
        self._lanes = {}
        self._buses = {}
        self._geometry = {
            "1": {"x": 0, "y": 0, "w": width, "h": height, "parent": "0"},
        }
        self.mxfile = ET.Element("mxfile", host="Python", type="device")
        self.diagram = ET.SubElement(self.mxfile, "diagram", id="page1", name=page_name)
        self.model = ET.SubElement(
            self.diagram, "mxGraphModel",
            dx=str(width), dy=str(height),
            grid="1" if grid else "0", gridSize="10", guides="1", tooltips="1",
            connect="1", arrows="1", fold="1", page="1",
            pageScale="1", pageWidth=str(width), pageHeight=str(height),
            math="0", shadow="0", background="#FFFFFF",
        )
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")

    def register_lane(self, name, orientation="horizontal", base=0, offset=None):
        """Register a reusable route lane and return its absolute coordinate."""
        if orientation not in {"horizontal", "vertical"}:
            raise ValueError("orientation must be 'horizontal' or 'vertical'")
        lane_offset = LANE_OFFSETS.get(name, len(self._lanes)) if offset is None else offset
        coordinate = base + (lane_offset * LANE_GAP)
        self._lanes[name] = {
            "orientation": orientation,
            "coordinate": coordinate,
            "offset": lane_offset,
        }
        return coordinate

    def lane_coordinate(self, name, orientation="horizontal", base=0, offset=None):
        """Return a lane coordinate, registering it on first use."""
        lane = self._lanes.get(name)
        if lane:
            return lane["coordinate"]
        return self.register_lane(name, orientation=orientation, base=base, offset=offset)

    def _next_id(self) -> str:
        self._cell_id += 1
        return str(self._cell_id)

    def _remember_geometry(self, cid, x, y, w, h, parent):
        self._geometry[cid] = {
            "x": float(x), "y": float(y), "w": float(w), "h": float(h),
            "parent": parent,
        }

    def _absolute_origin(self, cid):
        x = 0.0
        y = 0.0
        current = cid
        while current in self._geometry:
            geom = self._geometry[current]
            x += geom["x"]
            y += geom["y"]
            current = geom["parent"]
            if current == "0":
                break
        return x, y

    def _port_point(self, cid, parent, px, py):
        geom = self._geometry[cid]
        cell_x, cell_y = self._absolute_origin(cid)
        parent_x, parent_y = self._absolute_origin(parent)
        return (
            cell_x + (geom["w"] * px) - parent_x,
            cell_y + (geom["h"] * py) - parent_y,
        )

    def add_group(self, label, x, y, w, h, parent="1", group_type="region"):
        """Add a container rectangle. Returns cell ID."""
        cid = self._next_id()
        style = _GROUP_STYLES[group_type].format(**COLORS)
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def _add_icon_image(self, icon_key, x, y, w, h, parent="1", preserve_aspect=True):
        """Add only an OCI SVG icon image. Returns cell ID."""
        cid = self._next_id()
        data_uri = _load_svg(icon_key)
        image_aspect = "1" if preserve_aspect else "0"
        style = (
            f"shape=image;verticalLabelPosition=bottom;verticalAlign=top;"
            f"imageAspect={image_aspect};aspect=fixed;"
            f"image={data_uri};"
        )
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value="", style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def add_icon(self, label, icon_key, x, y, parent="1",
                 w=ICON_W, h=ICON_H, preserve_aspect=True):
        """Add an OCI SVG icon with a label below. Returns cell ID."""
        cid = self._add_icon_image(icon_key, x, y, w, h, parent, preserve_aspect)

        # Text label below
        lid = self._next_id()
        label_style = (
            "text;html=1;strokeColor=none;fillColor=none;align=center;"
            "verticalAlign=top;whiteSpace=wrap;rounded=0;"
            f"fontFamily=Oracle Sans;fontSize=11;fontStyle=0;"
            f"fontColor={COLORS['text_primary']};"
        )
        lc = ET.SubElement(
            self.root, "mxCell", id=lid, value=label, style=label_style,
            vertex="1", parent=parent,
        )
        ET.SubElement(lc, "mxGeometry",
                      x=str(x - 15), y=str(y + h + LABEL_GAP),
                      width=str(w + 30), height=str(45)).set("as", "geometry")
        self._remember_geometry(lid, x - 15, y + h + LABEL_GAP, w + 30, 45, parent)
        return cid

    def add_primary_icon(self, label, icon_key, x, y, parent="1"):
        """Add a primary architecture component icon at the standard size."""
        return self.add_icon(label, icon_key, x, y, parent=parent,
                             w=PRIMARY_ICON_SIZE, h=PRIMARY_ICON_SIZE)

    def add_secondary_icon(self, label, icon_key, x, y, parent="1"):
        """Add a secondary control/support icon at the standard size."""
        return self.add_icon(label, icon_key, x, y, parent=parent,
                             w=SECONDARY_ICON_SIZE, h=SECONDARY_ICON_SIZE)

    def add_connector_icon(self, label, icon_key, x, y, parent="1"):
        """Add a special connectivity icon at the standard connector size."""
        return self.add_icon(label, icon_key, x, y, parent=parent,
                             w=CONNECTOR_ICON_W, h=CONNECTOR_ICON_H)

    def add_connector_label(self, label, x, y, w=130, h=22, parent="1"):
        """Add an official-style connector label with Air fill masking the line."""
        cid = self._next_id()
        style = (
            "text;html=1;strokeColor=none;fillColor={air};align=center;"
            "verticalAlign=middle;whiteSpace=wrap;rounded=0;spacing=2;"
            "fontFamily=Oracle Sans;fontSize=8;fontStyle=0;"
            "fontColor={text_primary};"
        ).format(**COLORS)
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def add_special_connection_label(self, label, icon_key, x, y, parent="1",
                                     horizontal=True):
        """Add a half-size special connector icon plus label over a connector line."""
        if horizontal:
            icon_w, icon_h = CONNECTOR_ICON_W, CONNECTOR_ICON_H
            icon_x, icon_y = x, y
            label_x, label_y = x + icon_w + 6, y + 7
        else:
            icon_w, icon_h = CONNECTOR_ICON_H, CONNECTOR_ICON_W
            icon_x, icon_y = x, y
            label_x, label_y = x + icon_w + 6, y + 13
        icon_id = self._add_icon_image(icon_key, icon_x, icon_y, icon_w, icon_h,
                                       parent=parent, preserve_aspect=True)
        label_id = self.add_connector_label(label, label_x, label_y, parent=parent)
        return icon_id, label_id

    def add_image(self, image_path, x, y, w, h, parent="1"):
        """Add a PNG/image as a URL-encoded SVG wrapper (draw.io ignores base64)."""
        import urllib.parse
        from PIL import Image
        import io

        cid = self._next_id()
        img_path = Path(image_path)

        # Load and resize to max 300px wide to keep data small
        img = Image.open(img_path)
        if img.width > 300:
            ratio = 300 / img.width
            img = img.resize((300, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

        # Wrap PNG in an SVG so we can URL-encode it (draw.io renders URL-encoded SVGs)
        svg_wrapper = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{img.width}" height="{img.height}">'
            f'<image width="{img.width}" height="{img.height}" '
            f'xlink:href="data:image/png;base64,{img_b64}"/>'
            f'</svg>'
        )
        encoded = urllib.parse.quote(svg_wrapper, safe='')
        data_uri = f"data:image/svg+xml,{encoded}"

        style = (
            f"shape=image;verticalLabelPosition=bottom;labelBackgroundColor=none;"
            f"verticalAlign=top;aspect=fixed;imageAspect=1;"
            f"image={data_uri};"
        )
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value="", style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def add_text(self, label, x, y, w=200, h=30, parent="1",
                 font_size=10, font_style=0, align="left", font_color=None,
                 font_family="Oracle Sans"):
        """Add a text-only label."""
        cid = self._next_id()
        fc = font_color or COLORS["text_primary"]
        style = (
            f"text;html=1;strokeColor=none;fillColor=none;align={align};"
            f"verticalAlign=middle;whiteSpace=wrap;rounded=0;"
            f"fontFamily={font_family};fontSize={font_size};fontStyle={font_style};"
            f"fontColor={fc};"
        )
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def add_scope_band(self, label, x, y, w, h, parent="1", color=None,
                       fill_color="none", dashed=True, font_size=10,
                       label_position="top"):
        """Add a lightweight coverage band for cross-cutting controls.

        Use scope bands for IAM, Vault, Logging, Monitoring, Cloud Guard,
        Data Safe, and similar services that apply to a container or zone.
        They intentionally avoid drawing one dashed connector per component.
        """
        cid = self._next_id()
        stroke = color or COLORS["edge_accent"]
        dash = "dashed=1;dashPattern=4 4;" if dashed else "dashed=0;"
        if label_position == "bottom":
            vertical_align = "bottom"
            spacing_top = 0
            spacing_bottom = 6
        else:
            vertical_align = "top"
            spacing_top = 6
            spacing_bottom = 0
        style = (
            "rounded=0;whiteSpace=wrap;html=1;fillColor={fill};"
            "strokeColor={stroke};strokeWidth=1;{dash}"
            "fontFamily=Oracle Sans;fontSize={font_size};fontStyle=1;"
            "fontColor={stroke};align=left;verticalAlign={vertical_align};"
            "spacingLeft=8;spacingRight=8;spacingTop={spacing_top};"
            "spacingBottom={spacing_bottom};container=0;pointerEvents=0;"
        ).format(
            fill=fill_color, stroke=stroke, dash=dash, font_size=font_size,
            vertical_align=vertical_align, spacing_top=spacing_top,
            spacing_bottom=spacing_bottom,
        )
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def add_coverage_connector(self, scope_id, target, label="", parent="1",
                               side="right", dashed=True, color=None,
                               style_extra="", label_x=None, label_y=None,
                               label_w=150, label_h=22, waypoints=None):
        """Connect a coverage band to a control-plane target once.

        This is a summarized relation: the target applies to the scope. It is
        cleaner than drawing many dashed edges from every covered component.
        """
        if side == "left":
            exit_x, exit_y = 0.0, 0.5
            entry_x, entry_y = 1.0, 0.5
        elif side == "top":
            exit_x, exit_y = 0.5, 0.0
            entry_x, entry_y = 0.5, 1.0
        elif side == "bottom":
            exit_x, exit_y = 0.5, 1.0
            entry_x, entry_y = 0.5, 0.0
        else:
            exit_x, exit_y = 1.0, 0.5
            entry_x, entry_y = 0.0, 0.5

        edge_id = self.add_edge(
            scope_id, target, "", parent=parent, dashed=dashed,
            color=color, style_extra=style_extra,
            exit_x=exit_x, exit_y=exit_y, entry_x=entry_x, entry_y=entry_y,
            waypoints=waypoints,
        )
        label_id = None
        if label:
            if label_x is None or label_y is None:
                sx, sy = self._port_point(scope_id, parent, exit_x, exit_y)
                tx, ty = self._port_point(target, parent, entry_x, entry_y)
                label_x = ((sx + tx) / 2) - (label_w / 2)
                label_y = ((sy + ty) / 2) - (label_h / 2)
            label_id = self.add_connector_label(
                label, label_x, label_y, w=label_w, h=label_h, parent=parent,
            )
        return edge_id, label_id

    def add_control_plane_summary(self, label, x, y, w=320, h=58,
                                  parent="1", color=None):
        """Add a compact note for cross-cutting controls without edge clutter."""
        stroke = color or COLORS["edge_accent"]
        cid = self._next_id()
        style = (
            "rounded=0;whiteSpace=wrap;html=1;fillColor={air};"
            "strokeColor={stroke};strokeWidth=1;dashed=1;dashPattern=4 4;"
            "fontFamily=Oracle Sans;fontSize=10;fontStyle=0;"
            "fontColor={text_primary};align=left;verticalAlign=middle;"
            "spacing=8;"
        ).format(stroke=stroke, **COLORS)
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y),
                      width=str(w), height=str(h)).set("as", "geometry")
        self._remember_geometry(cid, x, y, w, h, parent)
        return cid

    def _edge_style(self, color, dashed, style_extra):
        ec = color or COLORS["edge_color"]
        if dashed:
            arrow = "dashed=1;dashPattern=6 3;endArrow=none;endFill=0;"
        else:
            arrow = "dashed=0;endArrow=open;endFill=0;"
        return (
            f"edgeStyle=orthogonalEdgeStyle;html=1;strokeColor={ec};strokeWidth=1;{arrow}"
            f"fontFamily=Oracle Sans;fontSize=12;"
            f"fontColor={COLORS['text_primary']};rounded=1;"
            f"jettySize=auto;orthogonalLoop=1;"
            f"{style_extra}"
        )

    def _add_point_edge(self, x1, y1, x2, y2, label="", parent="1",
                        dashed=False, color=None, style_extra=""):
        """Add an edge between absolute points in the parent coordinate space."""
        cid = self._next_id()
        style = self._edge_style(color, dashed, style_extra)
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            edge="1", parent=parent,
        )
        geom = ET.SubElement(cell, "mxGeometry", relative="1")
        geom.set("as", "geometry")
        ET.SubElement(geom, "mxPoint", x=str(x1), y=str(y1)).set("as", "sourcePoint")
        ET.SubElement(geom, "mxPoint", x=str(x2), y=str(y2)).set("as", "targetPoint")
        return cid

    def _add_bus_terminal(self, x, y, parent="1", visible=True, size=6):
        """Add a tiny terminal vertex for stable bus fan-in/fan-out edges."""
        cid = self._next_id()
        if visible:
            style = (
                "ellipse;html=1;strokeColor={edge_color};fillColor={air};"
                "strokeWidth=1;resizable=0;rotatable=0;"
            ).format(**COLORS)
        else:
            style = (
                "ellipse;html=1;strokeColor=none;fillColor=none;"
                "opacity=0;resizable=0;rotatable=0;"
            )
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value="", style=style,
            vertex="1", parent=parent,
        )
        ET.SubElement(cell, "mxGeometry",
                       x=str(x - (size / 2)), y=str(y - (size / 2)),
                       width=str(size), height=str(size)).set("as", "geometry")
        self._remember_geometry(cid, x - (size / 2), y - (size / 2),
                                size, size, parent)
        return cid

    def _bus_anchor(self, bus_id, anchor=None, terminal_visible=True,
                    terminal_size=6):
        bus = self._buses[bus_id]
        if anchor is None:
            anchor = 0.5
        if isinstance(anchor, tuple):
            x, y = anchor
        elif bus["orientation"] == "horizontal":
            x = bus["x1"] + ((bus["x2"] - bus["x1"]) * float(anchor))
            y = bus["y1"]
        else:
            x = bus["x1"]
            y = bus["y1"] + ((bus["y2"] - bus["y1"]) * float(anchor))
        return self._add_bus_terminal(
            x, y, parent=bus["parent"],
            visible=terminal_visible, size=terminal_size,
        ), x, y

    def add_edge(self, source, target, label="", parent="1",
                 dashed=False, color=None, style_extra="",
                 exit_x=0.5, exit_y=1.0, entry_x=0.5, entry_y=0.0,
                 waypoints=None):
        """Add an edge with explicit ports and optional waypoints."""
        cid = self._next_id()
        style = self._edge_style(color, dashed, style_extra)
        style += (
            f"exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;"
            f"entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0;"
        )
        cell = ET.SubElement(
            self.root, "mxCell", id=cid, value=label, style=style,
            edge="1", parent=parent, source=source, target=target,
        )
        geom = ET.SubElement(cell, "mxGeometry", relative="1")
        geom.set("as", "geometry")
        if waypoints:
            arr = ET.SubElement(geom, "Array")
            arr.set("as", "points")
            for wx, wy in waypoints:
                ET.SubElement(arr, "mxPoint", x=str(wx), y=str(wy))
        return cid

    def add_orthogonal_edge(self, source, target, label="", parent="1",
                            pattern="horizontal_first", via_x=None, via_y=None,
                            dashed=False, color=None, style_extra="",
                            exit_x=1.0, exit_y=0.5, entry_x=0.0, entry_y=0.5):
        """Add an orthogonal edge using a common waypoint pattern.

        Use point-to-point ``add_edge`` for simple local routes. Use this helper
        when a route needs a named middle lane or a consistent bend pattern.
        """
        waypoints = None
        if pattern == "via_y":
            if via_y is None:
                raise ValueError("via_y is required for pattern='via_y'")
            sx, _ = self._port_point(source, parent, exit_x, exit_y)
            tx, _ = self._port_point(target, parent, entry_x, entry_y)
            waypoints = [(sx, via_y), (tx, via_y)]
        elif pattern == "via_x":
            if via_x is None:
                raise ValueError("via_x is required for pattern='via_x'")
            _, sy = self._port_point(source, parent, exit_x, exit_y)
            _, ty = self._port_point(target, parent, entry_x, entry_y)
            waypoints = [(via_x, sy), (via_x, ty)]
        elif pattern == "horizontal_first":
            if via_x is not None and via_y is not None:
                waypoints = [(via_x, via_y)]
        elif pattern == "vertical_first":
            if via_x is not None and via_y is not None:
                waypoints = [(via_x, via_y)]
            else:
                exit_x, exit_y = 0.5, 1.0
                entry_x, entry_y = 0.5, 0.0
        else:
            raise ValueError(
                "pattern must be 'horizontal_first', 'vertical_first', 'via_x', or 'via_y'"
            )
        return self.add_edge(
            source, target, label=label, parent=parent, dashed=dashed,
            color=color, style_extra=style_extra,
            exit_x=exit_x, exit_y=exit_y, entry_x=entry_x, entry_y=entry_y,
            waypoints=waypoints,
        )

    def add_labeled_edge(self, source, target, label, label_x, label_y,
                         parent="1", label_w=130, label_h=22, dashed=False,
                         color=None, style_extra="", exit_x=1.0, exit_y=0.5,
                         entry_x=0.0, entry_y=0.5, waypoints=None):
        """Add an edge plus an official connector label over a horizontal segment."""
        edge_id = self.add_edge(
            source, target, "", parent=parent, dashed=dashed, color=color,
            style_extra=style_extra, exit_x=exit_x, exit_y=exit_y,
            entry_x=entry_x, entry_y=entry_y, waypoints=waypoints,
        )
        label_id = self.add_connector_label(
            label, label_x, label_y, w=label_w, h=label_h, parent=parent,
        )
        return edge_id, label_id

    def add_bus(self, label, x1, y1, x2=None, y2=None, parent="1",
                orientation="horizontal", lane=None, dashed=False, color=None,
                label_position=0.5):
        """Create a reusable connector bus for many-to-one or one-to-many flows."""
        if orientation not in {"horizontal", "vertical"}:
            raise ValueError("orientation must be 'horizontal' or 'vertical'")
        if orientation == "horizontal":
            x2 = x1 if x2 is None else x2
            y2 = y1
        else:
            x2 = x1
            y2 = y1 if y2 is None else y2

        bus_id = self._add_point_edge(
            x1, y1, x2, y2, parent=parent, dashed=dashed, color=color,
            style_extra="endArrow=none;endFill=0;startArrow=none;"
        )
        self._buses[bus_id] = {
            "label": label,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "parent": parent,
            "orientation": orientation,
            "lane": lane,
        }
        if label:
            if orientation == "horizontal":
                lx = x1 + ((x2 - x1) * label_position) - 65
                ly = y1 - 11
            else:
                lx = x1 + 8
                ly = y1 + ((y2 - y1) * label_position) - 11
            self.add_connector_label(label, lx, ly, parent=parent)
        return bus_id

    def connect_to_bus(self, source, bus_id, anchor=None, label="",
                       parent=None, dashed=False, color=None, style_extra="",
                       exit_x=0.5, exit_y=1.0, terminal_visible=True,
                       terminal_size=6):
        """Connect a component into a bus using a stable visible terminal."""
        bus = self._buses[bus_id]
        anchor_id, _, _ = self._bus_anchor(
            bus_id, anchor, terminal_visible=terminal_visible,
            terminal_size=terminal_size,
        )
        edge_id = self.add_edge(
            source, anchor_id, label=label, parent=parent or bus["parent"],
            dashed=dashed, color=color, style_extra=style_extra,
            exit_x=exit_x, exit_y=exit_y, entry_x=0.5, entry_y=0.5,
        )
        return edge_id

    def connect_from_bus(self, bus_id, target, anchor=None, label="",
                         parent=None, dashed=False, color=None, style_extra="",
                         entry_x=0.5, entry_y=0.0, terminal_visible=True,
                         terminal_size=6):
        """Connect a bus out to a target component using a stable visible terminal."""
        bus = self._buses[bus_id]
        anchor_id, _, _ = self._bus_anchor(
            bus_id, anchor, terminal_visible=terminal_visible,
            terminal_size=terminal_size,
        )
        edge_id = self.add_edge(
            anchor_id, target, label=label, parent=parent or bus["parent"],
            dashed=dashed, color=color, style_extra=style_extra,
            exit_x=0.5, exit_y=0.5, entry_x=entry_x, entry_y=entry_y,
        )
        return edge_id

    def add_special_connection(self, source, target, label, icon_key, marker_x,
                               marker_y, parent="1", horizontal=True,
                               dashed=False, color=None, style_extra="",
                               exit_x=1.0, exit_y=0.5, entry_x=0.0, entry_y=0.5,
                               waypoints=None):
        """Add a styled connection plus half-size FastConnect/VPN/peering marker."""
        edge_id = self.add_edge(
            source, target, "", parent=parent, dashed=dashed, color=color,
            style_extra=style_extra, exit_x=exit_x, exit_y=exit_y,
            entry_x=entry_x, entry_y=entry_y, waypoints=waypoints,
        )
        marker_ids = self.add_special_connection_label(
            label, icon_key, marker_x, marker_y, parent=parent,
            horizontal=horizontal,
        )
        return edge_id, marker_ids

    def add_fastconnect(self, source, target, marker_x, marker_y, label="FastConnect",
                        parent="1", horizontal=True, **edge_kwargs):
        """Add an official FastConnect special connector."""
        icon_key = "fastconnect_horizontal" if horizontal else "fastconnect_vertical"
        return self.add_special_connection(
            source, target, label, icon_key, marker_x, marker_y,
            parent=parent, horizontal=horizontal, **edge_kwargs,
        )

    def add_site_to_site_vpn(self, source, target, marker_x, marker_y,
                             label="Site-to-Site VPN", parent="1",
                             horizontal=False, **edge_kwargs):
        """Add an official Site-to-Site VPN special connector."""
        return self.add_special_connection(
            source, target, label, "site_to_site_vpn", marker_x, marker_y,
            parent=parent, horizontal=horizontal, **edge_kwargs,
        )

    def add_remote_peering(self, source, target, marker_x, marker_y,
                           label="Remote Peering", parent="1",
                           horizontal=True, **edge_kwargs):
        """Add an official Remote Peering special connector."""
        icon_key = "remote_peering_horizontal" if horizontal else "remote_peering_vertical"
        return self.add_special_connection(
            source, target, label, icon_key, marker_x, marker_y,
            parent=parent, horizontal=horizontal, **edge_kwargs,
        )

    def write(self, path: Path):
        """Write the draw.io XML to disk."""
        tree = ET.ElementTree(self.mxfile)
        ET.indent(tree, space="  ")
        path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(path), encoding="utf-8", xml_declaration=True)
        print(f"Wrote {path} ({path.stat().st_size:,} bytes)")
