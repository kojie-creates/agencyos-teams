from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ROLE_MAP = ROOT / "personality" / "ROLE-PERSONALITY-MAP.md"
OUT_BASE = ROOT / "marketing" / "agencyos-solo-agency-specialist-parent-icons-jaavis-deterministic"
WIDTH = 1536
HEIGHT = 1024


TEAMS = [
    ("Research", "@atlas", "Scout", ["Research Analyst", "Market Intelligence", "Idea Generator", "Knowledge Librarian"]),
    ("Engineering", "@bob", "Builder", ["Architect", "UX Designer", "Code Developer", "QA / Testing", "Truth Agent"]),
    ("Operations", "@maya", "Steward", ["DevOps", "Data Pipeline", "Security", "Performance Optimization"]),
    ("Growth", "@miles / @katie / @star", "Distribution", ["Marketing Strategy", "Content Creation", "Sales Enablement", "Community Manager"]),
    ("Insights", "@elias", "Archivist", ["Analytics", "Customer Insight", "Experimentation", "Strategy Advisor"]),
    ("Governance", "@vera", "Evidence", ["Audit", "Risk Assessment", "Policy", "Ethics Review"]),
]

BEINGS = {
    "@jaavis": ("Sentinel", "shield"),
    "@athena": ("Strategist", "knight"),
    "@atlas": ("Scout", "compass"),
    "@bob": ("Builder", "wrench"),
    "@maya": ("Steward", "leaf-flame"),
    "@miles": ("Closer", "folder-check"),
    "@katie": ("Host", "heart-door"),
    "@star": ("Muse", "star"),
    "@elias": ("Archivist", "archive"),
    "@vera": ("Auditor", "audit"),
}

COLORS = {
    "bg": "#F7F3EC",
    "ink": "#1F2933",
    "muted": "#667085",
    "line": "#D6CDBF",
    "panel": "#FFFDF8",
    "panel2": "#EFE7DA",
    "jaavis": "#2F4F4F",
    "athena": "#5A4A7A",
    "atlas": "#2F6F7E",
    "bob": "#7A5731",
    "maya": "#66824B",
    "miles": "#8A5A44",
    "katie": "#B36571",
    "star": "#B8860B",
    "elias": "#596375",
    "vera": "#6A5B8E",
}


def parse_specialists(markdown: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| Specialist | Specialist Handle | Display Name | Energy Parents | Domain Fit |"):
            in_table = True
            continue
        if in_table and line.startswith("| ---"):
            continue
        if in_table:
            if not line.startswith("|"):
                break
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != 5:
                continue
            specialist, handle, display, parents, domain = cells
            primary, support = [part.strip() for part in parents.split("+")]
            rows[specialist] = {
                "specialist": specialist,
                "handle": handle,
                "display": display,
                "primary": primary,
                "support": support,
                "domain": domain,
            }
    return rows


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def slug(handle: str) -> str:
    return handle.strip("@").replace("/", "").replace(" ", "-")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def icon_svg(kind: str, x: int, y: int, size: int, color: str) -> str:
    s = size
    c = esc(color)
    common = f'fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "shield":
        return f'<path {common} d="M{x+s/2} {y+3} L{x+s-4} {y+7} V{y+s/2} C{x+s-5} {y+s-7} {x+s/2} {y+s-3} {x+s/2} {y+s-2} C{x+5} {y+s-7} {x+4} {y+s/2} {x+4} {y+7} Z"/>'
    if kind == "knight":
        return f'<path {common} d="M{x+7} {y+s-4} H{x+s-4} M{x+10} {y+s-4} C{x+8} {y+s-10} {x+12} {y+s-15} {x+17} {y+s-20} L{x+12} {y+5} L{x+21} {y+8} L{x+s-5} {y+18} C{x+s-12} {y+18} {x+s-14} {y+25} {x+s-9} {y+32}"/>'
    if kind == "compass":
        return f'<circle {common} cx="{x+s/2}" cy="{y+s/2}" r="{s/2-4}"/><path {common} d="M{x+s*.62} {y+s*.38} L{x+s*.46} {y+s*.72} L{x+s*.54} {y+s*.54} Z"/>'
    if kind == "wrench":
        return f'<path {common} d="M{x+s-6} {y+8} L{x+s-15} {y+17} M{x+7} {y+s-7} L{x+19} {y+s-19} M{x+s-18} {y+5} C{x+s-8} {y+5} {x+s-5} {y+13} {x+s-10} {y+18} C{x+s-14} {y+22} {x+s-20} {y+22} {x+s-24} {y+18}"/>'
    if kind == "leaf-flame":
        return f'<path {common} d="M{x+s/2} {y+s-5} C{x+8} {y+s-13} {x+9} {y+18} {x+s/2} {y+5} C{x+s-4} {y+19} {x+s-7} {y+s-11} {x+s/2} {y+s-5} Z"/><path {common} d="M{x+s/2} {y+s-5} C{x+s/2-3} {y+s-17} {x+s/2+6} {y+s-20} {x+s/2+2} {y+11}"/>'
    if kind == "folder-check":
        return f'<path {common} d="M{x+4} {y+12} H{x+14} L{x+18} {y+17} H{x+s-4} V{y+s-6} H{x+4} Z"/><path {common} d="M{x+12} {y+s-16} L{x+18} {y+s-10} L{x+s-9} {y+s-22}"/>'
    if kind == "heart-door":
        return f'<path {common} d="M{x+s/2} {y+s-7} C{x+7} {y+21} {x+6} {y+10} {x+15} {y+8} C{x+20} {y+7} {x+s/2} {y+13} {x+s/2} {y+13} C{x+s/2} {y+13} {x+s-20} {y+7} {x+s-15} {y+8} C{x+s-6} {y+10} {x+s-7} {y+21} {x+s/2} {y+s-7} Z"/>'
    if kind == "star":
        return f'<path {common} d="M{x+s/2} {y+4} L{x+s*.60} {y+s*.39} L{x+s-5} {y+s*.40} L{x+s*.68} {y+s*.58} L{x+s*.78} {y+s-5} L{x+s/2} {y+s*.72} L{x+s*.22} {y+s-5} L{x+s*.32} {y+s*.58} L{x+5} {y+s*.40} L{x+s*.40} {y+s*.39} Z"/>'
    if kind == "archive":
        return f'<rect {common} x="{x+5}" y="{y+11}" width="{s-10}" height="{s-8}" rx="2"/><path {common} d="M{x+8} {y+5} H{x+s-8} V{y+11} H{x+8} Z M{x+14} {y+22} H{x+s-14}"/>'
    return f'<path {common} d="M{x+7} {y+8} H{x+s-7} V{y+s-6} H{x+7} Z"/><circle {common} cx="{x+s/2}" cy="{y+s/2}" r="{s/5}"/><path {common} d="M{x+s-12} {y+s-12} L{x+s-5} {y+s-5}"/>'


def svg_document(data: dict[str, dict[str, str]]) -> str:
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    title_font = font(13, True)
    col_w = 218
    gap = 22
    left = 48
    top = 276
    card_h = 118
    header_h = 42
    row_gap = 14

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        '<title id="title">AgencyOS Solo Agency deterministic specialist map</title>',
        '<desc id="desc">Source-driven diagram showing @jaavis as team lead, @athena as central orchestrator, and specialist cards with primary and support parent icons.</desc>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{COLORS["bg"]}"/>',
        f'<text x="48" y="58" fill="{COLORS["ink"]}" font-family="Arial, Segoe UI, sans-serif" font-size="31" font-weight="700">AgencyOS Solo Agency</text>',
        f'<text x="48" y="91" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="20">Team lead, coordinator routes, and specialist parent-energy map</text>',
        f'<text x="{WIDTH-48}" y="58" text-anchor="end" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="17">Source: personality/ROLE-PERSONALITY-MAP.md</text>',
        f'<text x="{WIDTH-48}" y="86" text-anchor="end" fill="{COLORS["ink"]}" font-family="Arial, Segoe UI, sans-serif" font-size="18" font-weight="700">@jaavis</text>',
        f'<rect x="48" y="122" width="682" height="106" rx="14" fill="{COLORS["panel"]}" stroke="{COLORS["line"]}" stroke-width="2"/>',
        icon_svg("shield", 70, 144, 54, COLORS["jaavis"]),
        f'<text x="144" y="157" fill="{COLORS["ink"]}" font-family="Arial, Segoe UI, sans-serif" font-size="20" font-weight="700">Team Lead / Operator</text>',
        f'<text x="144" y="188" fill="{COLORS["jaavis"]}" font-family="Arial, Segoe UI, sans-serif" font-size="30" font-weight="700">@jaavis</text>',
        f'<text x="144" y="212" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="16">Sentinel · shield · routing acceptance · closeout boundary</text>',
        f'<rect x="806" y="122" width="682" height="106" rx="14" fill="{COLORS["panel"]}" stroke="{COLORS["line"]}" stroke-width="2"/>',
        icon_svg("knight", 828, 144, 54, COLORS["athena"]),
        f'<text x="902" y="157" fill="{COLORS["ink"]}" font-family="Arial, Segoe UI, sans-serif" font-size="20" font-weight="700">Central Orchestrator</text>',
        f'<text x="902" y="188" fill="{COLORS["athena"]}" font-family="Arial, Segoe UI, sans-serif" font-size="30" font-weight="700">@athena</text>',
        f'<text x="902" y="212" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="16">Strategist · chess knight · cross-agency routing</text>',
    ]

    for i, (team, coord, energy, roles) in enumerate(TEAMS):
        x = left + i * (col_w + gap)
        color = COLORS[slug(coord.split()[0]) if coord.startswith("@") else "vera"] if team != "Growth" else COLORS["miles"]
        parts.append(f'<text x="{x}" y="{top - 20}" fill="{color}" font-family="Arial, Segoe UI, sans-serif" font-size="20" font-weight="700">{esc(team)}</text>')
        parts.append(f'<text x="{x}" y="{top + 5}" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="14">{esc(coord)} · {esc(energy)}</text>')
        parts.append(f'<line x1="{x}" y1="{top + header_h - 15}" x2="{x + col_w}" y2="{top + header_h - 15}" stroke="{COLORS["line"]}" stroke-width="2"/>')
        for j, role in enumerate(roles):
            item = data[role]
            y = top + header_h + j * (card_h + row_gap)
            p_kind = BEINGS[item["primary"]][1]
            s_kind = BEINGS[item["support"]][1]
            p_color = COLORS[slug(item["primary"])]
            s_color = COLORS[slug(item["support"])]
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{col_w}" height="{card_h}" rx="10" fill="{COLORS["panel"]}" stroke="{COLORS["line"]}" stroke-width="1.4"/>',
                    icon_svg(p_kind, x + col_w - 63, y + 13, 28, p_color),
                    icon_svg(s_kind, x + col_w - 33, y + 13, 28, s_color),
                ]
            )
            for k, line in enumerate(wrap_text(measure, item["specialist"], title_font, 132)[:2]):
                parts.append(f'<text x="{x + 14}" y="{y + 26 + k * 15}" fill="{COLORS["ink"]}" font-family="Arial, Segoe UI, sans-serif" font-size="13" font-weight="700">{esc(line)}</text>')
            parts.extend(
                [
                    f'<text x="{x + 14}" y="{y + 65}" fill="{COLORS["ink"]}" font-family="Arial, Segoe UI, sans-serif" font-size="19" font-weight="700">{esc(item["handle"])}</text>',
                    f'<text x="{x + 14}" y="{y + 88}" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="14">{esc(item["display"])}</text>',
                    f'<text x="{x + 14}" y="{y + 111}" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="12">{esc(item["primary"])} + {esc(item["support"])}</text>',
                ]
            )

    parts.extend(
        [
            f'<rect x="48" y="966" width="1440" height="1.5" fill="{COLORS["line"]}"/>',
            f'<text x="48" y="994" fill="{COLORS["muted"]}" font-family="Arial, Segoe UI, sans-serif" font-size="15">Coordinator rule: route, hand off, hash-lock final deliverables, then package closeout. Kojie decides.</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def html_document(svg: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgencyOS Solo Agency Specialist Map</title>
  <style>
    :root {{
      color-scheme: light;
      background: {COLORS["bg"]};
      color: {COLORS["ink"]};
      font-family: Arial, "Segoe UI", sans-serif;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: {COLORS["bg"]};
    }}
    .frame {{
      width: min(100vw, {WIDTH}px);
    }}
    svg {{
      display: block;
      width: 100%;
      height: auto;
    }}
  </style>
</head>
<body>
  <main class="frame">
{svg}
  </main>
</body>
</html>
"""


def draw_icon(draw: ImageDraw.ImageDraw, kind: str, x: int, y: int, size: int, color: str) -> None:
    # PNG mirrors the SVG semantic icons with simple deterministic line marks.
    c = color
    w = 3
    if kind == "shield":
        pts = [(x + size // 2, y + 3), (x + size - 4, y + 8), (x + size - 5, y + size // 2), (x + size // 2, y + size - 3), (x + 5, y + size // 2), (x + 4, y + 8)]
        draw.line(pts + [pts[0]], fill=c, width=w, joint="curve")
    elif kind == "knight":
        draw.line([(x + 7, y + size - 4), (x + size - 4, y + size - 4)], fill=c, width=w)
        draw.line([(x + 10, y + size - 4), (x + 16, y + size - 20), (x + 12, y + 5), (x + 21, y + 8), (x + size - 5, y + 18)], fill=c, width=w, joint="curve")
    elif kind == "compass":
        draw.ellipse((x + 4, y + 4, x + size - 4, y + size - 4), outline=c, width=w)
        draw.polygon([(x + int(size * .62), y + int(size * .38)), (x + int(size * .46), y + int(size * .72)), (x + int(size * .54), y + int(size * .54))], outline=c)
    elif kind == "wrench":
        draw.line([(x + 7, y + size - 7), (x + size - 8, y + 8)], fill=c, width=w)
        draw.arc((x + size - 24, y + 4, x + size - 3, y + 25), 35, 230, fill=c, width=w)
    elif kind == "leaf-flame":
        draw.line([(x + size // 2, y + size - 5), (x + 10, y + size - 15), (x + size // 2, y + 5), (x + size - 8, y + size - 15), (x + size // 2, y + size - 5)], fill=c, width=w, joint="curve")
    elif kind == "folder-check":
        draw.line([(x + 4, y + 12), (x + 14, y + 12), (x + 18, y + 17), (x + size - 4, y + 17), (x + size - 4, y + size - 6), (x + 4, y + size - 6), (x + 4, y + 12)], fill=c, width=w)
        draw.line([(x + 12, y + size - 16), (x + 18, y + size - 10), (x + size - 9, y + size - 22)], fill=c, width=w)
    elif kind == "heart-door":
        draw.line([(x + size // 2, y + size - 7), (x + 9, y + 20), (x + 12, y + 9), (x + size // 2, y + 13), (x + size - 12, y + 9), (x + size - 9, y + 20), (x + size // 2, y + size - 7)], fill=c, width=w, joint="curve")
    elif kind == "star":
        pts = [(x + size // 2, y + 4), (x + int(size * .60), y + int(size * .39)), (x + size - 5, y + int(size * .40)), (x + int(size * .68), y + int(size * .58)), (x + int(size * .78), y + size - 5), (x + size // 2, y + int(size * .72)), (x + int(size * .22), y + size - 5), (x + int(size * .32), y + int(size * .58)), (x + 5, y + int(size * .40)), (x + int(size * .40), y + int(size * .39))]
        draw.line(pts + [pts[0]], fill=c, width=w, joint="curve")
    elif kind == "archive":
        draw.rectangle((x + 5, y + 11, x + size - 5, y + size - 5), outline=c, width=w)
        draw.rectangle((x + 8, y + 5, x + size - 8, y + 12), outline=c, width=w)
        draw.line((x + 14, y + 22, x + size - 14, y + 22), fill=c, width=w)
    else:
        draw.rectangle((x + 7, y + 8, x + size - 7, y + size - 6), outline=c, width=w)
        draw.ellipse((x + size // 2 - 5, y + size // 2 - 5, x + size // 2 + 5, y + size // 2 + 5), outline=c, width=w)
        draw.line((x + size - 12, y + size - 12, x + size - 5, y + size - 5), fill=c, width=w)


def png_document(data: dict[str, dict[str, str]]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    f_title = font(31, True)
    f_sub = font(20)
    f_small = font(15)
    f_tiny = font(12)
    f_card = font(15, True)
    f_handle = font(19, True)
    f_top = font(30, True)

    draw.text((48, 29), "AgencyOS Solo Agency", fill=COLORS["ink"], font=f_title)
    draw.text((48, 70), "Team lead, coordinator routes, and specialist parent-energy map", fill=COLORS["muted"], font=f_sub)
    draw.text((1124, 35), "Source: personality/ROLE-PERSONALITY-MAP.md", fill=COLORS["muted"], font=font(17))
    draw.text((1408, 63), "@jaavis", fill=COLORS["ink"], font=font(18, True))

    for x, handle, kind, color, title, caption in [
        (48, "@jaavis", "shield", COLORS["jaavis"], "Team Lead / Operator", "Sentinel · shield · routing acceptance · closeout boundary"),
        (806, "@athena", "knight", COLORS["athena"], "Central Orchestrator", "Strategist · chess knight · cross-agency routing"),
    ]:
        draw.rounded_rectangle((x, 122, x + 682, 228), radius=14, fill=COLORS["panel"], outline=COLORS["line"], width=2)
        draw_icon(draw, kind, x + 22, 144, 54, color)
        draw.text((x + 96, 136), title, fill=COLORS["ink"], font=f_sub)
        draw.text((x + 96, 161), handle, fill=color, font=f_top)
        draw.text((x + 96, 195), caption, fill=COLORS["muted"], font=font(16))

    col_w = 218
    gap = 22
    left = 48
    top = 276
    card_h = 118
    header_h = 42
    row_gap = 14
    for i, (team, coord, energy, roles) in enumerate(TEAMS):
        x = left + i * (col_w + gap)
        color = COLORS["miles"] if team == "Growth" else COLORS[slug(coord.split()[0])]
        draw.text((x, top - 41), team, fill=color, font=f_sub)
        draw.text((x, top - 13), f"{coord} · {energy}", fill=COLORS["muted"], font=font(14))
        draw.line((x, top + header_h - 15, x + col_w, top + header_h - 15), fill=COLORS["line"], width=2)
        for j, role in enumerate(roles):
            item = data[role]
            y = top + header_h + j * (card_h + row_gap)
            draw.rounded_rectangle((x, y, x + col_w, y + card_h), radius=10, fill=COLORS["panel"], outline=COLORS["line"], width=1)
            draw_icon(draw, BEINGS[item["primary"]][1], x + col_w - 63, y + 13, 28, COLORS[slug(item["primary"])])
            draw_icon(draw, BEINGS[item["support"]][1], x + col_w - 33, y + 13, 28, COLORS[slug(item["support"])])
            for k, line in enumerate(wrap_text(draw, item["specialist"], font(13, True), 132)[:2]):
                draw.text((x + 14, y + 12 + k * 15), line, fill=COLORS["ink"], font=font(13, True))
            draw.text((x + 14, y + 40), item["handle"], fill=COLORS["ink"], font=f_handle)
            draw.text((x + 14, y + 72), item["display"], fill=COLORS["muted"], font=font(14))
            draw.text((x + 14, y + 99), f'{item["primary"]} + {item["support"]}', fill=COLORS["muted"], font=f_tiny)

    draw.line((48, 966, 1488, 966), fill=COLORS["line"], width=2)
    draw.text((48, 978), "Coordinator rule: route, hand off, hash-lock final deliverables, then package closeout. Kojie decides.", fill=COLORS["muted"], font=f_small)
    return img


def main() -> None:
    data = parse_specialists(ROLE_MAP.read_text(encoding="utf-8"))
    expected = {role for _, _, _, roles in TEAMS for role in roles}
    missing = expected - data.keys()
    extra = set(data) - expected
    if missing or extra:
        raise SystemExit(f"Specialist map mismatch. Missing={sorted(missing)} Extra={sorted(extra)}")

    svg = svg_document(data)
    OUT_BASE.with_suffix(".svg").write_text(svg, encoding="utf-8")
    OUT_BASE.with_suffix(".html").write_text(html_document(svg), encoding="utf-8")
    png_document(data).save(OUT_BASE.with_suffix(".png"))
    print(OUT_BASE.with_suffix(".svg"))
    print(OUT_BASE.with_suffix(".html"))
    print(OUT_BASE.with_suffix(".png"))


if __name__ == "__main__":
    main()
