from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\felix\Desktop\agencyos-pro")
OUT = ROOT / "sales-enablement" / "agencyos-dual-config-orchestration.png"

W, H = 1920, 1080
BG = "#0b0d12"
PANEL = "#11151d"
PANEL_DARK = "#0e1219"
TEXT = "#f2f4f7"
MUTED = "#9aa3b2"
DIM = "#6d7687"
ORANGE = "#ff7442"
BLUE = "#5ca8ff"
GREEN = "#68e084"
PURPLE = "#a970ff"
GOLD = "#f1bd52"
RED = "#ff6382"
LINE = "#273141"


def font(size, bold=False):
    names = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


F = {
    "hero": font(50, True),
    "h1": font(28, True),
    "h2": font(22, True),
    "h3": font(17, True),
    "body": font(15),
    "small": font(12),
    "tiny": font(10),
    "micro": font(9, True),
}


def t(draw, xy, value, fill=TEXT, f="body", anchor=None):
    draw.text(xy, value, fill=fill, font=F[f], anchor=anchor)


def wrap(draw, xy, value, max_w, fill=MUTED, f="small", gap=5):
    words = value.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if draw.textlength(test, font=F[f]) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, fill=fill, font=F[f])
        y += F[f].size + gap
    return y


def round_rect(draw, box, radius=16, fill=PANEL, outline=LINE, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def node(draw, box, number, title, body, accent=ORANGE):
    x1, y1, x2, y2 = box
    round_rect(draw, box, 12, "#131821", "#263142", 1)
    draw.rounded_rectangle((x1, y1, x1 + 5, y2), radius=3, fill=accent)
    t(draw, (x1 + 20, y1 + 22), number, accent, "micro")
    t(draw, (x1 + 54, y1 + 20), title, TEXT, "h3")
    wrap(draw, (x1 + 54, y1 + 52), body, x2 - x1 - 76, MUTED, "small", 4)


def agent(draw, box, eyebrow, title, body, accent=BLUE):
    x1, y1, x2, y2 = box
    round_rect(draw, box, 10, "#111720", "#283546", 1)
    t(draw, ((x1 + x2) / 2, y1 + 21), eyebrow, accent, "micro", "mm")
    t(draw, ((x1 + x2) / 2, y1 + 48), title, TEXT, "h3", "mm")
    t(draw, ((x1 + x2) / 2, y1 + 73), body, MUTED, "tiny", "mm")


def arrow(draw, start, end, fill=ORANGE, width=2):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=fill, width=width)
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            pts = [(x2, y2), (x2 - 10, y2 - 6), (x2 - 10, y2 + 6)]
        else:
            pts = [(x2, y2), (x2 + 10, y2 - 6), (x2 + 10, y2 + 6)]
    else:
        if y2 >= y1:
            pts = [(x2, y2), (x2 - 6, y2 - 10), (x2 + 6, y2 - 10)]
        else:
            pts = [(x2, y2), (x2 - 6, y2 + 10), (x2 + 6, y2 + 10)]
    draw.polygon(pts, fill=fill)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 62):
        draw.line((x, 0, x, H), fill="#121722", width=1)
    for y in range(0, H, 62):
        draw.line((0, y, W, y), fill="#121722", width=1)

    t(draw, (96, 78), "Architecture - Agent Systems", ORANGE, "micro")
    t(draw, (96, 120), "Multi-Agent Orchestration", TEXT, "hero")
    t(draw, (760, 120), "with Dual Configs", ORANGE, "hero")
    t(draw, (96, 218), "A config selector improves both answer quality and operating quality before work is routed.", MUTED, "body")
    t(draw, (1585, 116), "AgencyOS", TEXT, "h1")
    t(draw, (1588, 148), "operating quality layer", MUTED, "small")

    # Input block
    round_rect(draw, (96, 470, 298, 612), 16, "#131821", "#252f3d", 1)
    t(draw, (197, 494), "Input", DIM, "micro", "mm")
    t(draw, (197, 535), "User Request", TEXT, "h2", "mm")
    t(draw, (197, 570), "intent + context", MUTED, "small", "mm")
    t(draw, (197, 590), "+ authority", MUTED, "small", "mm")
    arrow(draw, (300, 540), (382, 540), ORANGE, 2)

    # Main orchestration layer
    round_rect(draw, (388, 304, 1290, 944), 20, "#151014", "#4c2b22", 1)
    t(draw, (412, 335), "◆  Orchestration Layer", ORANGE, "micro")
    t(draw, (412, 382), "Dual Config Selector", TEXT, "h1")
    t(draw, (1168, 360), "stage 1 -> 6", DIM, "tiny")

    node(draw, (412, 420, 684, 526), "01", "Reasoning Config", "rewrite, clarify, decompose, grade, synthesize", ORANGE)
    node(draw, (720, 420, 992, 526), "02", "Operating Config", "scope, route, tools, permissions, handoffs", GOLD)
    node(draw, (1028, 420, 1266, 526), "03", "Governance Config", "risk, policy, public/client gates", BLUE)
    arrow(draw, (684, 473), (720, 473), ORANGE, 2)
    arrow(draw, (992, 473), (1028, 473), BLUE, 2)

    # Config selector hub
    round_rect(draw, (830, 556, 858, 584), 8, ORANGE, ORANGE, 1)
    draw.line((844, 526, 844, 556), fill=ORANGE, width=2)
    draw.line((475, 598, 824, 598), fill="#633528", width=1)
    draw.line((844, 584, 844, 598), fill=ORANGE, width=2)
    draw.line((844, 598, 1145, 598), fill="#2f4d75", width=1)

    agent(draw, (412, 610, 545, 708), "AGENT - A", "Research", "facts + sources", BLUE)
    agent(draw, (554, 610, 687, 708), "AGENT - B", "Builder", "create + test", GREEN)
    agent(draw, (696, 610, 829, 708), "AGENT - C", "Growth", "message + sell", GOLD)
    agent(draw, (838, 610, 971, 708), "AGENT - D", "Ops", "tools + flow", BLUE)
    agent(draw, (980, 610, 1113, 708), "AGENT - E", "Insights", "measure + learn", PURPLE)
    for x in [476, 618, 760, 902, 1044]:
        draw.line((x, 598, x, 610), fill="#633528", width=1)

    node(draw, (1028, 720, 1266, 826), "04", "Human Gate", "approve, reject, edit, or escalate high-stakes actions", BLUE)
    draw.line((1145, 708, 1145, 720), fill=BLUE, width=2)
    round_rect(draw, (1132, 698, 1158, 722), 6, BLUE, BLUE, 1)
    t(draw, (972, 674), "RESULTS", BLUE, "tiny")
    draw.line((972, 674, 1028, 674), fill=BLUE, width=1)
    draw.line((1028, 674, 1028, 773), fill=BLUE, width=1)

    node(draw, (566, 820, 956, 908), "05", "Closeout Config", "artifact exists, claim supported, memory and learning updated", ORANGE)
    arrow(draw, (1028, 864), (956, 864), BLUE, 2)
    t(draw, (598, 952), "answer quality + operating quality", ORANGE, "micro")

    # Checklist
    round_rect(draw, (1340, 304, 1826, 944), 20, "#10151d", "#202a37", 1)
    t(draw, (1372, 337), "›  Cheatsheet", BLUE, "micro")
    t(draw, (1372, 376), "Config checklist", TEXT, "h1")
    checklist = [
        ("01", "Choose Reasoning Config", "catch ambiguity before it propagates"),
        ("02", "Choose Operating Config", "turn answer work into routed work"),
        ("03", "Apply Governance Config", "gate public, risky, or irreversible actions"),
        ("04", "Route specialists with tools", "match task shape to skill and permission"),
        ("05", "Verify before closeout", "artifact, evidence, owner, memory"),
        ("06", "Learn after delivery", "feed lessons back into future routes"),
    ]
    y = 430
    for num, title, body in checklist:
        t(draw, (1372, y), num, ORANGE if num in {"01", "05"} else BLUE, "micro")
        t(draw, (1414, y), title, TEXT, "h3")
        t(draw, (1414, y + 28), body, MUTED, "small")
        draw.line((1372, y + 58, 1795, y + 58), fill="#202a37", width=1)
        y += 70

    round_rect(draw, (1372, 838, 1795, 922), 10, "#1b1515", "#613628", 1)
    t(draw, (1392, 864), "◆  PRO TIP", ORANGE, "micro")
    t(draw, (1392, 896), "Good config matters more than adding more agents.", TEXT, "body")

    draw.line((130, 1000, 1788, 1000), fill="#252b35", width=1)
    t(draw, (96, 1032), "AGENCYOS - DUAL CONFIG ORCHESTRATION - REFERENCE ARCHITECTURE", DIM, "micro")
    t(draw, (1736, 1032), "01 / 01", DIM, "tiny")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()
