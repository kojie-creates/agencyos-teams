from __future__ import annotations

import argparse
from pathlib import Path

from agencyos_runtime import build_activation_states, build_evidence_lock_status, load_events, render_timeline_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Render AgencyOS runtime events into an activation timeline.")
    parser.add_argument("events", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    events = load_events(args.events)
    states = build_activation_states(events)
    evidence_lock = build_evidence_lock_status(events)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_timeline_html(states, evidence_lock), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
