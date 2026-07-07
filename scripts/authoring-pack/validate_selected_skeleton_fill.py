#!/usr/bin/env python3
"""Validate selected-skeleton section fills from a reviewed ChatGPT authoring pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from authoring_pack_selected_skeleton_fill import (
    STATUS_EXIT_CODES,
    cli_summary,
    validate_selected_skeleton_fill,
    write_validation_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-report", required=True, help="validation-report.json from review helper.")
    parser.add_argument("--pack-tree", required=True, help="Extracted specdock-authoring-pack tree.")
    parser.add_argument("--assurance", required=True, help="Local .assurance.json selected by SpecDock.")
    parser.add_argument("--selected-skeleton", required=True, help="Local selected skeleton manifest JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory for validation report and summary.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    result = validate_selected_skeleton_fill(
        Path(args.review_report),
        Path(args.pack_tree),
        Path(args.assurance),
        Path(args.selected_skeleton),
    )
    result = write_validation_outputs(output_dir, result)
    print(json.dumps(cli_summary(result, output_dir), ensure_ascii=False, sort_keys=True))
    return STATUS_EXIT_CODES[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
