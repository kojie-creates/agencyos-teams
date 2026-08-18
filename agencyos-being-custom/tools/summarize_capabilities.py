from __future__ import annotations

import argparse
import json
from pathlib import Path

from capability_registry import build_capability_events, capability_summary, load_capabilities


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize AgencyOS capability activation state.")
    parser.add_argument("registry", type=Path)
    parser.add_argument("--events-output", type=Path)
    parser.add_argument("--timestamp", default="2026-08-12T16:45:00Z")
    args = parser.parse_args()

    records = load_capabilities(args.registry)
    summary = capability_summary(records)
    print(json.dumps(summary, indent=2, sort_keys=True))

    if args.events_output:
        events = build_capability_events(records, timestamp=args.timestamp)
        args.events_output.parent.mkdir(parents=True, exist_ok=True)
        args.events_output.write_text(
            "\n".join(json.dumps(event.__dict__, sort_keys=True) for event in events) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
