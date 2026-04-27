"""Standalone runtime CLI entrypoint.

Usage:
  python -m m365_runtime [--host 127.0.0.1] [--port 9300]

The launcher resolves its installed root from the package location. The
banned source-repo and sibling-repo env names live in `_forbidden_tokens.py`;
this module never reads them.
"""

from __future__ import annotations

import argparse
import sys

from .launcher import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="m365-runtime", description="SMARTHAUS standalone M365 Graph runtime service"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9300)
    args = parser.parse_args(argv)
    return run(host=args.host, port=args.port)


if __name__ == "__main__":
    sys.exit(main())
