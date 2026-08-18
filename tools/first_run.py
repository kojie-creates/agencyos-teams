#!/usr/bin/env python3
"""AgencyOS first-run startup sequence.

Run from an AgencyOS One or AgencyOS Teams folder:

    python tools/first_run.py

For automation:

    python tools/first_run.py --non-interactive --name "client-launch" --owner "Kojie" --outcome "Launch packet"
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

try:
    from tools import dev_team_diagnostic_intake
except ModuleNotFoundError:
    import dev_team_diagnostic_intake


PRODUCTS = {
    "agencyos-one": {
        "name": "AgencyOS One",
        "unit": "workflow",
        "container_dir": "workflows",
        "template_dir": "workflows/_template",
        "starter_file": "workflows/{slug}/intake.md",
        "default_being": "Jaavis",
    },
    "agencyos-teams": {
        "name": "AgencyOS Teams",
        "unit": "project",
        "container_dir": "projects",
        "template_dir": "projects/_template",
        "starter_file": "projects/{slug}/intake.md",
        "default_being": "Jaavis",
    },
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "first-run"


def detect_root(start: Path) -> tuple[Path, dict[str, str]]:
    current = start.resolve()
    for path in [current, *current.parents]:
        marker = path.name.lower()
        if marker in PRODUCTS and (path / "DEFAULT-RUN-CONTRACT.md").exists():
            return path, PRODUCTS[marker]
        readme = path / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8", errors="ignore")[:500]
            if "# AgencyOS One" in text:
                return path, PRODUCTS["agencyos-one"]
            if "# AgencyOS Teams" in text:
                return path, PRODUCTS["agencyos-teams"]
    raise SystemExit("Could not find an AgencyOS One or AgencyOS Teams root.")


def ask(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{label}{suffix}: ").strip()
    return answer or default


def choose_install_mode() -> str:
    print("\nInstallation mode:")
    print("1. standalone - AgencyOS folder is the whole working surface")
    print("2. sidecar - AgencyOS sits beside an existing project")
    print("3. embedded - AgencyOS sits inside an existing project")
    value = ask("Choose 1, 2, or 3", "1")
    return {"1": "standalone", "2": "sidecar", "3": "embedded"}.get(value, value)


def collect_interactive(product: dict[str, str]) -> dict[str, str]:
    print(f"\n{product['name']} first-run")
    print("Answer once. The script will write startup context and create the first packet.\n")
    mode = choose_install_mode()
    unit = product["unit"]
    data = {
        "install_mode": mode,
        "name": ask(f"{unit.title()} name", f"first-{unit}"),
        "owner": ask("Human owner / approval owner", ""),
        "outcome": ask("Desired outcome", ""),
        "active_being": ask("Active Being", product["default_being"]),
        "project_root": ask("Existing project path, if any", ""),
        "allowed_tools": ask("Allowed tools", "local files, Codex, available project tools"),
        "off_limits": ask("Off-limits areas", "external sends, publication, paid commitments, sensitive data, destructive changes without approval"),
        "approval_required_for": ask("Approval required for", "external-facing, sensitive, paid, legal, financial, housing, medical, safety, memory, or destructive actions"),
        "notes": ask("Important startup notes", ""),
    }
    return data


def collect_args(product: dict[str, str]) -> dict[str, str]:
    parser = argparse.ArgumentParser(description=f"{product['name']} first-run startup")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--name", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--outcome", default="")
    parser.add_argument("--install-mode", default="standalone", choices=["standalone", "sidecar", "embedded"])
    parser.add_argument("--project-root", default="")
    parser.add_argument("--active-being", default=product["default_being"])
    parser.add_argument("--allowed-tools", default="local files, Codex, available project tools")
    parser.add_argument("--off-limits", default="external sends, publication, paid commitments, sensitive data, destructive changes without approval")
    parser.add_argument("--approval-required-for", default="external-facing, sensitive, paid, legal, financial, housing, medical, safety, memory, or destructive actions")
    parser.add_argument("--notes", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-dev-diagnostic", action="store_true")
    args = parser.parse_args()

    if not args.non_interactive:
        data = collect_interactive(product)
        data["force"] = str(args.force)
        data["skip_dev_diagnostic"] = str(args.skip_dev_diagnostic)
        return data

    unit = product["unit"]
    data = {
        "install_mode": args.install_mode,
        "name": args.name or f"first-{unit}",
        "owner": args.owner,
        "outcome": args.outcome,
        "active_being": args.active_being,
        "project_root": args.project_root,
        "allowed_tools": args.allowed_tools,
        "off_limits": args.off_limits,
        "approval_required_for": args.approval_required_for,
        "notes": args.notes,
        "force": str(args.force),
        "skip_dev_diagnostic": str(args.skip_dev_diagnostic),
    }
    return data


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_template(root: Path, product: dict[str, str], slug: str, force: bool) -> Path:
    src = root / product["template_dir"]
    dst = root / product["container_dir"] / slug
    if not src.exists():
        raise SystemExit(f"Missing template: {src}")
    if dst.exists():
        if not force:
            raise SystemExit(f"Destination already exists: {dst}\nUse --force to overwrite.")
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def context_markdown(product: dict[str, str], data: dict[str, str], slug: str, packet_path: Path) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unit = product["unit"]
    return f"""# First Run Context

Generated: {now}

Product:

```text
{product['name']}
```

Installation mode:

```text
{data['install_mode']}
```

{unit.title()}:

```text
{data['name']}
```

Slug:

```text
{slug}
```

Packet path:

```text
{packet_path.as_posix()}
```

Human owner / approval owner:

```text
{data['owner']}
```

Active Being:

```text
{data['active_being']}
```

Desired outcome:

```text
{data['outcome']}
```

Existing project path:

```text
{data['project_root']}
```

Allowed tools:

```text
{data['allowed_tools']}
```

Off-limits:

```text
{data['off_limits']}
```

Approval required for:

```text
{data['approval_required_for']}
```

Startup notes:

```text
{data['notes']}
```

## Next Action

Open the packet path, then route the request using the product run contract.
"""


def project_link_markdown(product: dict[str, str], data: dict[str, str]) -> str:
    return f"""# Project Link

Purpose:

```text
Connect this {product['name']} installation to the project or workspace it governs.
```

Installation mode:

```text
{data['install_mode']}
```

Project root:

```text
{data['project_root']}
```

Human approval owner:

```text
{data['owner']}
```

Allowed tools:

```text
{data['allowed_tools']}
```

Off-limits:

```text
{data['off_limits']}
```

Approval required for:

```text
{data['approval_required_for']}
```
"""


def update_packet(packet: Path, product: dict[str, str], data: dict[str, str]) -> None:
    unit = product["unit"]
    intake = packet / "intake.md"
    if intake.exists():
        intake.write_text(f"""# {unit.title()} Intake

## Request

```text
{data['name']}
```

## Desired Outcome

```text
{data['outcome']}
```

## Context

```text
Installation mode: {data['install_mode']}
Existing project path: {data['project_root']}
Active Being: {data['active_being']}
```

## Constraints

```text
Off-limits: {data['off_limits']}
Allowed tools: {data['allowed_tools']}
```

## Human Approval Needed For

```text
{data['approval_required_for']}
```

## Definition Of Done

```text
A usable artifact exists, evidence status is clear, human approval boundaries are respected, and the next step is obvious.
```
""", encoding="utf-8")

    active = packet / "active-being.md"
    if active.exists():
        active.write_text(f"""# Active Being

| Being | Handle | Role In Workflow | Why Assigned | Approval Limits |
| --- | --- | --- | --- | --- |
| {data['active_being']} | @{slugify(data['active_being'])} | User-facing partner | Default first-run Being | {data['approval_required_for']} |

## Personality Source

```text
agencyos-being-custom/personalities/{data['active_being']}.md
```
""", encoding="utf-8")

    assigned = packet / "assigned-beings.md"
    if assigned.exists():
        assigned.write_text(f"""# Assigned Beings

| Being | Handle | Project Role | Workstreams | Approval Limits |
| --- | --- | --- | --- | --- |
| {data['active_being']} | @{slugify(data['active_being'])} | Human-AI interaction point | First routing pass | {data['approval_required_for']} |
""", encoding="utf-8")


def needs_dev_team_diagnostic(data: dict[str, str]) -> bool:
    haystack = " ".join(
        [
            data.get("name", ""),
            data.get("outcome", ""),
            data.get("notes", ""),
        ]
    ).lower()
    signals = [
        "dev-team diagnostic",
        "development team diagnostic",
        "technical diagnostic",
        "diagnostic memo",
        "developer diagnostic",
        "implementation evidence",
    ]
    return any(signal in haystack for signal in signals)


def maybe_run_dev_team_diagnostic(
    data: dict[str, str],
    packet: Path,
    collect_answers=dev_team_diagnostic_intake.collect_interactive,
) -> bool:
    skip = data.get("skip_dev_diagnostic", "False").lower() == "true"
    if skip or not needs_dev_team_diagnostic(data):
        return False

    print("\nDev-team diagnostic intake")
    print("First-run context indicates diagnostic evidence is needed before this project can continue.\n")
    answers = collect_answers()
    result = dev_team_diagnostic_intake.write_response_packet(packet, answers)
    print(f"Wrote: {result.markdown_path}")
    print(f"Wrote: {result.json_path}")
    print(f"Uploads: {result.upload_dir}")
    return True


def main() -> None:
    root, product = detect_root(Path.cwd())
    data = collect_args(product)
    slug = slugify(data["name"])
    force = data.get("force", "False").lower() == "true"
    packet = copy_template(root, product, slug, force)
    update_packet(packet, product, data)

    write_text(root / "FIRST-RUN-CONTEXT.md", context_markdown(product, data, slug, packet.relative_to(root)))
    write_text(root / "PROJECT-LINK.md", project_link_markdown(product, data))
    write_text(root / ".first-run.json", json.dumps({"product": product["name"], "slug": slug, **data}, indent=2))

    print(f"First run complete for {product['name']}.")
    print(f"Created: {packet}")
    print(f"Wrote: {root / 'FIRST-RUN-CONTEXT.md'}")
    print(f"Wrote: {root / 'PROJECT-LINK.md'}")
    maybe_run_dev_team_diagnostic(data, packet)


if __name__ == "__main__":
    main()
