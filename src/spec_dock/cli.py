"""Public fixed-engine CLI."""

from __future__ import annotations


def main(argv: list[str] | None = None) -> int:
    """Enter the pinned external engine for every public invocation."""
    from spec_dock.external_cli import main as external_main

    return external_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
