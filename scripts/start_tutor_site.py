from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.local_tutor_server import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Start Yuan Jiale's local tutor web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run(ROOT, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
