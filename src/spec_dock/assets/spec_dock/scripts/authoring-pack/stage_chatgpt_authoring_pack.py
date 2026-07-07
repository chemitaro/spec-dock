#!/usr/bin/env python3
"""Stage a reviewed evidence-only ChatGPT authoring pack tree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from authoring_pack_stage import STATUS_EXIT_CODES, cli_summary, stage_reviewed_pack, write_stage_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-report", required=True, help="validation-report.json from review helper.")
    parser.add_argument("--pack-tree", required=True, help="Extracted specdock-authoring-pack tree.")
    parser.add_argument(
        "--issue-dir", required=True, help="Issue directory containing canonical requirement/design/plan."
    )
    parser.add_argument("--output-dir", required=True, help="Directory for staged artifacts and dry-run reports.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    result = stage_reviewed_pack(
        Path(args.review_report),
        Path(args.pack_tree),
        Path(args.issue_dir),
    )
    result = write_stage_outputs(output_dir, result)
    print(json.dumps(cli_summary(result, output_dir), ensure_ascii=False, sort_keys=True))
    return STATUS_EXIT_CODES[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
