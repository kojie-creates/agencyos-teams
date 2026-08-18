import argparse
import re
from datetime import date
from pathlib import Path


TYPE_LABELS = {
    "Jaavis": "Polite Formal Loyal Dry Wit",
    "Katie": "Warm Enthusiastic Conversational",
}


def display_name_from_handle(handle):
    return " ".join(part.capitalize() for part in handle.lstrip("@").split("-"))


def resolve_personality(root, requested):
    if requested.startswith("@") and "-" in requested:
        role_map = root / "personality" / "ROLE-PERSONALITY-MAP.md"
        if role_map.exists():
            for line in role_map.read_text(encoding="utf-8").splitlines():
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(cells) >= 4 and cells[1] == requested:
                    primary = re.search(r"@([a-z]+)", cells[3])
                    if primary:
                        return {
                            "active": requested,
                            "source": primary.group(1).capitalize(),
                            "shape": cells[2],
                            "type_label": "Specialist Route",
                        }

    if requested.startswith("@"):
        source = requested.lstrip("@").capitalize()
        return {
            "active": requested,
            "source": source,
            "shape": source,
            "type_label": TYPE_LABELS.get(source, f"{source} Personality"),
        }

    return {
        "active": requested,
        "source": requested,
        "shape": display_name_from_handle(requested),
        "type_label": TYPE_LABELS.get(requested, f"{display_name_from_handle(requested)} Personality"),
    }


def replace_or_insert(lines, prefix, replacement, insert_after_prefix=None):
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = replacement
            return

    insert_at = 0
    if insert_after_prefix:
        for index, line in enumerate(lines):
            if line.startswith(insert_after_prefix):
                insert_at = index + 1
                break
    lines.insert(insert_at, replacement)


def switch_personality(root, personality, switch_date):
    resolved = resolve_personality(root, personality)
    personality_path = root / "personality" / f"{resolved['source']}.md"
    if not personality_path.exists():
        raise FileNotFoundError(f"personality/{resolved['source']}.md not found")

    active_path = root / "personality" / "ACTIVE-PERSONALITY.md"
    lines = active_path.read_text(encoding="utf-8").splitlines()

    replace_or_insert(
        lines,
        "Current active personality:",
        f"Current active personality: {resolved['active']}",
        insert_after_prefix="# Active Personality",
    )
    replace_or_insert(lines, "Active personality:", f"Active personality: {resolved['active']}")
    replace_or_insert(lines, "Source:", f"Source: personality/{resolved['source']}.md")
    replace_or_insert(lines, "Last switched:", f"Last switched: {switch_date}")
    replace_or_insert(lines, "Default shape:", f"Default shape: {resolved['shape']}.")
    replace_or_insert(lines, "User-defined type:", f"User-defined type: {resolved['type_label']}.")
    replace_or_insert(lines, "### Default Shape:", f"### Default Shape: {resolved['shape']}")
    replace_or_insert(lines, "## User-Defined Type:", f"## User-Defined Type: {resolved['type_label']}")

    active_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return active_path


def main():
    parser = argparse.ArgumentParser(description="Switch the active AgencyOS personality.")
    parser.add_argument("personality")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()

    try:
        active_path = switch_personality(args.root, args.personality, args.date)
    except FileNotFoundError as error:
        parser.exit(1, f"{error}\n")

    print(f"Active personality switched to {args.personality}: {active_path}")


if __name__ == "__main__":
    main()
