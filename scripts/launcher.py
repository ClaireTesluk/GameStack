"""Explicit entrypoint for the standalone CLI bundle."""
from gamestack.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
