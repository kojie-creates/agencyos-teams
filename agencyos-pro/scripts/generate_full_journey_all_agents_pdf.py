from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUT = "output/pdf/agencyos-full-journey-all-agents-walkthrough.pdf"
W, H = landscape(letter)

BG = colors.HexColor("#071019")
PANEL = colors.HexColor("#0f1721")
PANEL_2 = colors.HexColor("#111c28")
TEXT = colors.HexColor("#edf4fb")
MUTED = colors.HexColor("#9fb0c4")
BLUE = colors.HexColor("#4d9dff")
GREEN = colors.HexColor("#66df84")
PURPLE = colors.HexColor("#c99bff")
GOLD = colors.HexColor("#f3c456")
RED = colors.HexColor("#ff6f8f")
LINE = colors.HexColor("#304052")


def setup(c, title=None, subtitle=None, page=None):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#142031"))
    c.setLineWidth(0.4)
    for x in range(0, int(W), 48):
        c.line(x, 0, x, H)
    for y in range(0, int(H), 48):
        c.line(0, y, W, y)
    if title:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(0.55 * inch, H - 0.62 * inch, title)
    if subtitle:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(0.55 * inch, H - 0.86 * inch, subtitle)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - 0.55 * inch, 0.32 * inch, f"AgencyOS full journey walkthrough - {page}")


def wrap_text(text, font, size, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_block(c, x, y, text, max_width, size=9, color=MUTED, font="Helvetica", leading=None):
    leading = leading or size + 3
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap_text(text, font, size, max_width):
        c.drawString(x, y, line)
        y -= leading
    return y


def pill(c, x, y, w, h, label, stroke, fill=PANEL_2, size=8):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(1.1)
    c.roundRect(x, y, w, h, 7, fill=1, stroke=1)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", size)
    c.drawCentredString(x + w / 2, y + h / 2 - size / 3, label)


def card(c, x, y, w, h, title, subtitle=None, accent=BLUE):
    c.setFillColor(PANEL)
    c.setStrokeColor(LINE)
    c.setLineWidth(1.1)
    c.roundRect(x, y, w, h, 12, fill=1, stroke=1)
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.line(x + 12, y + h - 2, x + w - 12, y + h - 2)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x + 14, y + h - 24, title)
    if subtitle:
        text_block(c, x + 14, y + h - 43, subtitle, w - 28, 8.5, MUTED)


def arrow(c, x1, y1, x2, y2, color=BLUE, width=2):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    if x2 >= x1:
        c.line(x2, y2, x2 - 7, y2 + 4)
        c.line(x2, y2, x2 - 7, y2 - 4)
    else:
        c.line(x2, y2, x2 + 7, y2 + 4)
        c.line(x2, y2, x2 + 7, y2 - 4)


def draw_user(c, x, y):
    c.setFillColor(PANEL_2)
    c.setStrokeColor(TEXT)
    c.setLineWidth(1.5)
    c.circle(x, y, 24, fill=1, stroke=1)
    c.circle(x, y + 8, 7, fill=0, stroke=1)
    c.arc(x - 14, y - 13, x + 14, y + 8, 20, 140)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x, y - 38, "Test User")


def page_cover(c):
    setup(c, page=1)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(0.6 * inch, H - 1.1 * inch, "AgencyOS Full Journey Walkthrough")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 13)
    c.drawString(0.62 * inch, H - 1.42 * inch, "A time-based story showing every coordinator and specialist activated across one common request.")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(GREEN)
    c.drawString(0.62 * inch, H - 1.9 * inch, "Scenario")
    text_block(c, 0.62 * inch, H - 2.2 * inch,
               "Maya owns a small specialty coffee roaster. She asks AgencyOS to launch an office coffee subscription for local companies in 12 weeks. The work must move from research to build, marketing, operations, governance, launch, measurement, and learning.",
               5.3 * inch, 12, TEXT, "Helvetica")
    draw_user(c, 1.15 * inch, 2.25 * inch)
    x0, y0 = 2.05 * inch, 2.05 * inch
    labels = [("Intent", BLUE), ("Routed Work", GREEN), ("Deliverables", GOLD), ("Proof + Learning", PURPLE)]
    for i, (label, col) in enumerate(labels):
        pill(c, x0 + i * 1.85 * inch, y0, 1.35 * inch, 0.4 * inch, label, col, size=9)
        if i:
            arrow(c, x0 + i * 1.85 * inch - 0.5 * inch, y0 + 0.2 * inch, x0 + i * 1.85 * inch - 0.12 * inch, y0 + 0.2 * inch, col)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.62 * inch, 0.92 * inch, "What this PDF shows")
    text_block(c, 0.62 * inch, 0.68 * inch,
               "The same request travels through AgencyOS over time. Every coordinator routes work. Every specialist produces a named artifact. Governance and Truth Agent prevent unsupported closeout. Maya receives decisions, assets, evidence, and next steps.",
               9.5 * inch, 9.5, MUTED)
    c.showPage()


def page_cast(c):
    setup(c, "The Cast", "Every coordinator and specialist appears in the 12-week journey.", 2)
    cols = [
        ("Research", GREEN, ["Research Coordinator", "Market Intelligence", "Research Analyst", "Idea Generator", "Knowledge Librarian"]),
        ("Engineering", BLUE, ["Engineering Coordinator", "Architect", "UX Designer", "Code Developer", "QA / Testing", "Truth Agent"]),
        ("Growth", GOLD, ["Growth Coordinator", "Marketing Strategy", "Content Creation", "Sales Enablement", "Community Manager"]),
        ("Operations", colors.HexColor("#67d7ff"), ["Operations Coordinator", "DevOps", "Data Pipeline", "Security", "Performance Optimization"]),
        ("Insights", PURPLE, ["Insights Coordinator", "Analytics", "Experimentation", "Customer Insight", "Strategy Advisor"]),
        ("Governance", RED, ["Policy", "Risk Assessment", "Ethics Review", "Audit"]),
    ]
    x, y = 0.45 * inch, H - 1.55 * inch
    w = 1.52 * inch
    gap = 0.12 * inch
    for i, (name, col, agents) in enumerate(cols):
        xx = x + i * (w + gap)
        card(c, xx, y - 3.8 * inch, w, 3.75 * inch, name, "Activates when this work appears.", col)
        yy = y - 1.0 * inch
        for agent in agents:
            pill(c, xx + 0.09 * inch, yy, w - 0.18 * inch, 0.28 * inch, agent, col, size=6.2)
            yy -= 0.36 * inch
    c.showPage()


def page_timeline(c):
    setup(c, "The Time Lens", "A 12-week route that activates the full AgencyOS network without forcing fake work.", 3)
    phases = [
        ("Day 0", "Operator Team Lead", "Scope Gate, Risk Gate, definition of done", GREEN),
        ("Week 1", "Research", "Market, buyer, source, idea, and memory work", BLUE),
        ("Week 2-3", "Engineering", "Workflow, form, tracker, automation, QA", GREEN),
        ("Week 4-5", "Growth", "Positioning, content, sales, community signals", GOLD),
        ("Week 6", "Operations", "Launch runbook, data, access, security, throughput", colors.HexColor("#67d7ff")),
        ("Week 7", "Governance", "Policy, risk, ethics, audit checks", RED),
        ("Week 8-10", "Pilot", "Launch controlled pilot with human approval", PURPLE),
        ("Week 11", "Insights", "Analytics, experiments, customer insight, strategy", PURPLE),
        ("Week 12", "Closeout", "Truth Agent verifies and Knowledge Librarian stores learning", GREEN),
    ]
    x0, x1 = 0.75 * inch, W - 0.75 * inch
    y = H - 1.75 * inch
    c.setStrokeColor(LINE)
    c.setLineWidth(3)
    c.line(x0, y, x1, y)
    gap = (x1 - x0) / (len(phases) - 1)
    for i, (time, owner, artifact, col) in enumerate(phases):
        x = x0 + i * gap
        c.setFillColor(col)
        c.circle(x, y, 6, fill=1, stroke=0)
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x, y + 18, time)
        c.setFillColor(PANEL)
        c.setStrokeColor(col)
        c.setLineWidth(1)
        h = 1.22 * inch
        yy = y - 1.55 * inch if i % 2 == 0 else y - 3.05 * inch
        c.roundRect(x - 0.56 * inch, yy, 1.12 * inch, h, 8, fill=1, stroke=1)
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawCentredString(x, yy + h - 16, owner)
        text_block(c, x - 0.48 * inch, yy + h - 32, artifact, 0.96 * inch, 6.5, MUTED)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(0.65 * inch, 1.25 * inch, "Compelling story")
    text_block(c, 0.65 * inch, 1.0 * inch,
               "Maya never has to manually manage 30 agents. She makes the key decisions. AgencyOS routes the work, asks for approval at the right moments, and returns evidence-backed deliverables over time.",
               9.5 * inch, 10.5, MUTED)
    c.showPage()


def page_operator(c):
    setup(c, "Day 0 - The Request Enters AgencyOS", "The user starts with one normal request. AgencyOS turns it into a governed work packet.", 4)
    draw_user(c, 0.95 * inch, H - 2.25 * inch)
    arrow(c, 1.35 * inch, H - 2.25 * inch, 2.25 * inch, H - 2.25 * inch, GREEN, 3)
    card(c, 2.35 * inch, H - 3.0 * inch, 2.25 * inch, 1.5 * inch, "Operator Team Lead", "Runs intake, scope gate, risk gate, human owner, and definition of done.", GREEN)
    arrow(c, 4.7 * inch, H - 2.25 * inch, 5.45 * inch, H - 2.25 * inch, BLUE, 3)
    card(c, 5.55 * inch, H - 3.0 * inch, 2.45 * inch, 1.5 * inch, "Central Orchestrator", "Selects configs, agencies, coordinators, governance route, loop cap, and return path.", BLUE)
    arrow(c, 8.12 * inch, H - 2.25 * inch, 9.0 * inch, H - 2.25 * inch, PURPLE, 3)
    card(c, 9.1 * inch, H - 3.0 * inch, 1.95 * inch, 1.5 * inch, "Work Packet", "The request is ready to move through time.", PURPLE)
    headings = [("Maya gives", "Launch an office coffee subscription."), ("AgencyOS asks", "Who approves public offers? What counts as success? What risks matter?"), ("Maya receives", "A route, timeline, human gates, and expected deliverables.")]
    y = 2.55 * inch
    for i, (h, body) in enumerate(headings):
        card(c, 0.75 * inch + i * 3.55 * inch, y, 3.1 * inch, 1.0 * inch, h, body, [GREEN, BLUE, GOLD][i])
    c.showPage()


def page_research(c):
    setup(c, "Week 1 - Research Becomes Direction", "Research Coordinator routes facts, buyer context, ideas, and reusable knowledge.", 5)
    card(c, 0.65 * inch, H - 2.0 * inch, 2.1 * inch, 0.9 * inch, "Research Coordinator", "Classifies research need and returns bounded artifacts.", GREEN)
    agents = [
        ("Market Intelligence", "market snapshot, buyer segments, competitor comparison"),
        ("Research Analyst", "research brief, evidence summary, unknowns"),
        ("Idea Generator", "offer angles, experiment ideas, concept options"),
        ("Knowledge Librarian", "source index, decision index, reuse recommendations"),
    ]
    for i, (a, out) in enumerate(agents):
        x = 3.0 * inch + i * 2.0 * inch
        card(c, x, H - 2.45 * inch, 1.72 * inch, 1.42 * inch, a, out, BLUE)
        arrow(c, 2.78 * inch, H - 1.55 * inch, x - 0.08 * inch, H - 1.75 * inch, BLUE, 1.5)
    card(c, 0.75 * inch, 1.0 * inch, 10.0 * inch, 1.2 * inch, "Maya receives", "A clear buyer hypothesis: office managers at 20-100 person companies want reliable local coffee without managing ad hoc orders. She also receives assumptions, proof gaps, and language customers already use.", GOLD)
    c.showPage()


def page_engineering(c):
    setup(c, "Weeks 2-3 - Direction Becomes A Usable System", "Engineering Coordinator turns the research into intake, workflow, automations, and tested assets.", 6)
    card(c, 0.65 * inch, H - 2.0 * inch, 2.25 * inch, 0.9 * inch, "Engineering Coordinator", "Routes structure, design, implementation, and testing.", GREEN)
    agents = [
        ("Architect", "subscription workflow, operating map, dependencies"),
        ("UX Designer", "buyer intake form, review checklist, friction notes"),
        ("Code Developer", "lead tracker, reorder calculator, automation draft"),
        ("QA / Testing", "test results, defects, pass/fail notes"),
        ("Truth Agent", "artifact check, claim-to-evidence, closure status"),
    ]
    for i, (a, out) in enumerate(agents):
        x = 0.8 * inch + i * 2.05 * inch
        y = H - 4.25 * inch
        card(c, x, y, 1.78 * inch, 1.5 * inch, a, out, BLUE if i < 3 else PURPLE)
    card(c, 0.75 * inch, 0.9 * inch, 10.0 * inch, 1.2 * inch, "Maya receives", "A usable subscription workflow: intake form, approval checklist, lead tracker, pilot runbook draft, tested calculations, and verified artifact existence before the build lane closes.", GOLD)
    c.showPage()


def page_growth(c):
    setup(c, "Weeks 4-5 - The Offer Becomes Buyable", "Growth Coordinator routes positioning, copy, sales assets, and community feedback.", 7)
    card(c, 0.65 * inch, H - 2.0 * inch, 2.25 * inch, 0.9 * inch, "Growth Coordinator", "Names audience, channel, claims needing proof, and review route.", GOLD)
    agents = [
        ("Marketing Strategy", "positioning brief, channel strategy, campaign angle"),
        ("Content Creation", "landing copy, emails, posts, training docs"),
        ("Sales Enablement", "discovery questions, objection handling, follow-up sequence"),
        ("Community Manager", "reply drafts, feedback notes, question list"),
    ]
    for i, (a, out) in enumerate(agents):
        card(c, 1.0 * inch + i * 2.45 * inch, H - 4.1 * inch, 2.05 * inch, 1.45 * inch, a, out, GOLD)
    card(c, 0.75 * inch, 1.0 * inch, 10.0 * inch, 1.2 * inch, "Maya receives", "A clear offer, landing page copy, outreach sequence, sales call script, objection handling, and approved community reply drafts. Anything public waits for human approval.", GREEN)
    c.showPage()


def page_ops(c):
    setup(c, "Week 6 - Launch Gets Operational", "Operations Coordinator ensures the subscription can actually run after the sale.", 8)
    card(c, 0.65 * inch, H - 2.0 * inch, 2.25 * inch, 0.9 * inch, "Operations Coordinator", "Routes timing, ownership, tools, data, security, and operating cadence.", colors.HexColor("#67d7ff"))
    agents = [
        ("DevOps", "runbook, environment notes, automation health check"),
        ("Data Pipeline", "field map, data quality notes, reporting input"),
        ("Security", "access review, sensitive data handling, risk recommendations"),
        ("Performance Optimization", "bottleneck analysis, throughput checklist"),
    ]
    for i, (a, out) in enumerate(agents):
        card(c, 1.0 * inch + i * 2.45 * inch, H - 4.1 * inch, 2.05 * inch, 1.45 * inch, a, out, colors.HexColor("#67d7ff"))
    card(c, 0.75 * inch, 1.0 * inch, 10.0 * inch, 1.2 * inch, "Maya receives", "A launch runbook, data fields, access rules, privacy handling notes, delivery cadence, and a bottleneck plan for roasting, packing, routing, and customer updates.", GOLD)
    c.showPage()


def page_governance(c):
    setup(c, "Week 7 - Governance Protects Trust", "Governance checks the work before the public pilot starts.", 9)
    agents = [
        ("Policy", "checks refund terms, subscription rules, privacy language"),
        ("Risk Assessment", "maps delivery, pricing, reputation, and fulfillment risks"),
        ("Ethics Review", "reviews claims, consent, customer impact, and transparency"),
        ("Audit", "checks evidence, ownership, completeness, and closeout readiness"),
    ]
    for i, (a, out) in enumerate(agents):
        card(c, 0.8 * inch + i * 2.55 * inch, H - 3.2 * inch, 2.18 * inch, 1.65 * inch, a, out, RED)
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.5)
    c.roundRect(0.85 * inch, 1.0 * inch, 9.9 * inch, 1.4 * inch, 12, fill=0, stroke=1)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1.05 * inch, 2.05 * inch, "Maya's approval gate")
    text_block(c, 1.05 * inch, 1.78 * inch,
               "Maya approves the public offer, refund terms, customer data handling, claims, pricing assumptions, and pilot limits. AgencyOS can recommend. Maya authorizes.",
               9.2 * inch, 11, MUTED)
    c.showPage()


def page_insights(c):
    setup(c, "Weeks 8-12 - Launch Learns", "Insights Coordinator turns pilot activity into learning, decisions, and next moves.", 10)
    card(c, 0.65 * inch, H - 2.0 * inch, 2.25 * inch, 0.9 * inch, "Insights Coordinator", "Routes measurement, customer signal, experiments, and strategic review.", PURPLE)
    agents = [
        ("Analytics", "metric table, baseline comparison, measurement gaps"),
        ("Experimentation", "test plan, hypotheses, variants, success metric"),
        ("Customer Insight", "feedback themes, objections, language patterns"),
        ("Strategy Advisor", "decision brief, tradeoff map, next strategic move"),
    ]
    for i, (a, out) in enumerate(agents):
        card(c, 1.0 * inch + i * 2.45 * inch, H - 4.1 * inch, 2.05 * inch, 1.45 * inch, a, out, PURPLE)
    card(c, 0.75 * inch, 1.0 * inch, 10.0 * inch, 1.2 * inch, "Maya receives", "A pilot scorecard, customer themes, test recommendations, a strategic next-move memo, and a learning packet returned to Knowledge Librarian for reuse.", GOLD)
    c.showPage()


def page_deliverables(c):
    setup(c, "Deliverables And User Relationship", "Every artifact connects back to something the user can decide, use, review, or remember.", 11)
    rows = [
        ("Route + scope packet", "Shows Maya what will happen and what remains her decision."),
        ("Research brief", "Turns market uncertainty into a first buyer hypothesis."),
        ("Workflow + intake form", "Makes the subscription operational instead of abstract."),
        ("Sales assets", "Gives Maya messages, questions, and follow-up she can review."),
        ("Launch runbook", "Shows who does what, when, and with what tools."),
        ("Governance packet", "Protects claims, customer data, pricing, and approval boundaries."),
        ("Pilot scorecard", "Shows what worked and what needs to change."),
        ("Closeout + memory update", "Preserves the lesson so the next launch starts smarter."),
    ]
    y = H - 1.35 * inch
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y, "Deliverable")
    c.drawString(3.2 * inch, y, "How it relates to Maya")
    y -= 0.22 * inch
    for i, (d, rel) in enumerate(rows):
        fill = PANEL if i % 2 == 0 else PANEL_2
        c.setFillColor(fill)
        c.setStrokeColor(LINE)
        c.roundRect(0.65 * inch, y - 0.45 * inch, 10.1 * inch, 0.42 * inch, 6, fill=1, stroke=0)
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 8.8)
        c.drawString(0.82 * inch, y - 0.29 * inch, d)
        text_block(c, 3.2 * inch, y - 0.18 * inch, rel, 7.1 * inch, 8.5, MUTED, leading=9.5)
        y -= 0.52 * inch
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(0.75 * inch, 0.95 * inch, "Story close")
    text_block(c, 0.75 * inch, 0.7 * inch,
               "Maya starts with one request. Over 12 weeks, every AgencyOS coordinator and specialist contributes exactly once or at the right recurring point. The work closes only when Truth Agent verifies the artifacts and Audit confirms the evidence trail.",
               9.7 * inch, 10.5, MUTED)
    c.showPage()


def main():
    c = canvas.Canvas(OUT, pagesize=landscape(letter))
    c.setTitle("AgencyOS Full Journey Walkthrough")
    page_cover(c)
    page_cast(c)
    page_timeline(c)
    page_operator(c)
    page_research(c)
    page_engineering(c)
    page_growth(c)
    page_ops(c)
    page_governance(c)
    page_insights(c)
    page_deliverables(c)
    c.save()


if __name__ == "__main__":
    main()
