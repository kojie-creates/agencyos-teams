from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


ROOT = Path(r"C:\Users\felix\Desktop\agencyos-pro")
REF = Path(r"C:\Users\felix\Downloads\1786534042194.jpg")
OUT = ROOT / "sales-enablement" / "agencyos-orchestration-side-by-side.png"

W, H = 2400, 1500
BG = "#071019"
GRID = "#172536"
PANEL = "#0f1721"
PANEL_2 = "#111c28"
TEXT = "#edf4fb"
MUTED = "#9fb0c4"
BLUE = "#4d9dff"
GREEN = "#66df84"
PURPLE = "#c99bff"
GOLD = "#f3c456"
ORANGE = "#ff7a45"
RED = "#ff6688"
LINE = "#33465a"


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


F = {
    "hero": font(52, True),
    "h1": font(34, True),
    "h2": font(26, True),
    "h3": font(20, True),
    "body": font(18),
    "small": font(15),
    "tiny": font(12),
    "micro": font(11, True),
}


def rounded(draw, box, r=18, fill=PANEL, outline=LINE, width=2):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def text(draw, xy, s, fill=TEXT, f="body", anchor=None):
    draw.text(xy, s, fill=fill, font=F[f], anchor=anchor)


def wrapped(draw, xy, s, max_w, fill=MUTED, f="small", line_gap=6):
    words = s.split()
    lines = []
    line = ""
    for w in words:
        test = w if not line else f"{line} {w}"
        if draw.textlength(test, font=F[f]) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    x, y = xy
    line_h = F[f].size + line_gap
    for ln in lines:
        draw.text((x, y), ln, fill=fill, font=F[f])
        y += line_h
    return y


def arrow(draw, start, end, fill=BLUE, width=4):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=fill, width=width)
    if x2 >= x1:
        pts = [(x2, y2), (x2 - 14, y2 - 8), (x2 - 14, y2 + 8)]
    else:
        pts = [(x2, y2), (x2 + 14, y2 - 8), (x2 + 14, y2 + 8)]
    draw.polygon(pts, fill=fill)


def node(draw, x, y, w, h, title, sub=None, accent=BLUE, fill=PANEL_2):
    rounded(draw, (x, y, x + w, y + h), 14, fill, accent, 3)
    text(draw, (x + 18, y + 18), title, TEXT, "h3")
    if sub:
        wrapped(draw, (x + 18, y + 52), sub, w - 36, MUTED, "small", 4)


def chip(draw, x, y, w, h, label, accent=BLUE):
    rounded(draw, (x, y, x + w, y + h), 10, "#101923", accent, 2)
    text(draw, (x + w / 2, y + h / 2), label, TEXT, "small", "mm")


def draw_agencyos(draw, x, y, w, h):
    rounded(draw, (x, y, x + w, y + h), 24, "#0b121b", GREEN, 2)
    text(draw, (x + 34, y + 34), "AgencyOS orchestration layer", TEXT, "h1")
    text(draw, (x + 34, y + 76), "Scope, route, equip, govern, verify, remember, learn, and close real work.", MUTED, "body")

    y0 = y + 130
    node(draw, x + 34, y0, 210, 92, "Human Request", "intent + context + authority", GREEN)
    arrow(draw, (x + 252, y0 + 46), (x + 315, y0 + 46), GREEN, 4)
    node(draw, x + 322, y0, 240, 92, "Scope + Intake", "boundaries, risk, definition of done", GREEN)
    arrow(draw, (x + 570, y0 + 46), (x + 638, y0 + 46), GREEN, 4)
    node(draw, x + 646, y0, 248, 92, "Signal Check", "InnerLight coherence before routing", PURPLE)

    y1 = y + 275
    node(draw, x + 150, y1, 280, 92, "Operator Team Lead", "scope gate, risk gate, decision owner", GREEN)
    node(draw, x + 498, y1, 330, 92, "Central Orchestrator", "config, agency route, loop cap, return path", GREEN)
    arrow(draw, (x + 894, y0 + 92), (x + 828, y1 + 46), PURPLE, 3)
    arrow(draw, (x + 430, y1 + 46), (x + 498, y1 + 46), GREEN, 4)

    y2 = y + 430
    chip(draw, x + 52, y2, 150, 44, "Research", BLUE)
    chip(draw, x + 222, y2, 170, 44, "Engineering", BLUE)
    chip(draw, x + 412, y2, 135, 44, "Growth", GOLD)
    chip(draw, x + 567, y2, 165, 44, "Operations", "#67d7ff")
    chip(draw, x + 752, y2, 135, 44, "Insights", PURPLE)
    arrow(draw, (x + 663, y1 + 92), (x + 663, y2 - 10), GREEN, 4)
    draw.line((x + 127, y2 - 10, x + 820, y2 - 10), fill=GREEN, width=3)

    y3 = y + 540
    node(draw, x + 52, y3, 245, 96, "Specialists", "market, build, content, ops, analytics", BLUE)
    node(draw, x + 340, y3, 245, 96, "Tool Access", "files, apps, APIs, actions with permission", GOLD)
    node(draw, x + 628, y3, 245, 96, "Handoffs", "work packets keep context intact", PURPLE)
    arrow(draw, (x + 174, y2 + 44), (x + 174, y3 - 10), BLUE, 3)
    arrow(draw, (x + 475, y2 + 44), (x + 475, y3 - 10), GOLD, 3)
    arrow(draw, (x + 754, y2 + 44), (x + 754, y3 - 10), PURPLE, 3)

    y4 = y + 675
    node(draw, x + 94, y4, 235, 90, "Governance", "policy, risk, ethics, audit", RED)
    node(draw, x + 373, y4, 235, 90, "Evidence", "artifact proof + claim checks", PURPLE)
    node(draw, x + 652, y4, 235, 90, "Closeout", "truth verified, memory updated", GREEN)
    arrow(draw, (x + 297, y3 + 42), (x + 373, y4 + 45), PURPLE, 3)
    arrow(draw, (x + 585, y3 + 42), (x + 652, y4 + 45), GREEN, 3)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    for gx in range(0, W, 80):
        draw.line((gx, 0, gx, H), fill=GRID, width=1)
    for gy in range(0, H, 80):
        draw.line((0, gy, W, gy), fill=GRID, width=1)

    text(draw, (80, 70), "Orchestration Layer Comparison", TEXT, "hero")
    text(draw, (82, 132), "Reference architecture vs. AgencyOS as a work operating layer", MUTED, "body")

    left_x, top_y = 80, 205
    left_w, panel_h = 1070, 840
    right_x, right_w = 1250, 1070

    rounded(draw, (left_x, top_y, left_x + left_w, top_y + panel_h), 24, "#0b1017", ORANGE, 2)
    text(draw, (left_x + 30, top_y + 34), "Attached reference", TEXT, "h1")
    text(draw, (left_x + 30, top_y + 76), "Multi-agent orchestration with reasoning", MUTED, "body")
    ref = Image.open(REF).convert("RGB")
    ref.thumbnail((left_w - 60, 570))
    img.paste(ref, (left_x + 30, top_y + 120))
    text(draw, (left_x + 30, top_y + 720), "Primary pattern", TEXT, "h3")
    wrapped(draw, (left_x + 30, top_y + 755),
            "User query moves through rewrite, route, grade, human review, and final synthesis. The core promise is better answer quality than a single agent.",
            left_w - 60, MUTED, "body")

    draw_agencyos(draw, right_x, top_y, right_w, panel_h)

    bottom_y = 1100
    rounded(draw, (80, bottom_y, 2320, 330 + bottom_y), 24, "#0b121b", LINE, 2)
    text(draw, (112, bottom_y + 34), "What changes when AgencyOS becomes the orchestration layer?", TEXT, "h1")
    rows = [
        ("Unit of work", "Query or task", "Work packet with scope, owner, evidence, state, and closeout"),
        ("Routing goal", "Pick the right specialist", "Pick route, config, tools, permissions, governance, and return path"),
        ("Human role", "Review high-stakes output", "Hold authority over risky, public, financial, legal, and client-facing actions"),
        ("Evidence model", "Grade intermediate results", "Verify artifacts, claims, handoffs, audit trail, and completion"),
        ("Learning loop", "Synthesize final answer", "Store decisions, lessons, performance signals, and reusable memory"),
    ]
    x_cols = [112, 470, 990]
    text(draw, (x_cols[0], bottom_y + 92), "Dimension", GREEN, "h3")
    text(draw, (x_cols[1], bottom_y + 92), "Reference image", ORANGE, "h3")
    text(draw, (x_cols[2], bottom_y + 92), "AgencyOS", GREEN, "h3")
    y = bottom_y + 132
    for dim, ref_s, ag_s in rows:
        draw.line((112, y - 12, 2288, y - 12), fill=GRID, width=1)
        text(draw, (x_cols[0], y), dim, TEXT, "body")
        wrapped(draw, (x_cols[1], y), ref_s, 430, MUTED, "small")
        wrapped(draw, (x_cols[2], y), ag_s, 1160, MUTED, "small")
        y += 39

    text(draw, (112, H - 46), "Short read: the attached image orchestrates reasoning for better answers; AgencyOS orchestrates work for better operating quality.", GOLD, "body")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
