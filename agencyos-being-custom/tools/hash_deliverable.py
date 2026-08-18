from __future__ import annotations

import argparse
import json
from pathlib import Path

from agencyos_runtime import hash_deliverable


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash an AgencyOS deliverable.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--owner", required=True)
    args = parser.parse_args()

    record = hash_deliverable(args.path, root=args.root, owner=args.owner)
    print(json.dumps(record.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
