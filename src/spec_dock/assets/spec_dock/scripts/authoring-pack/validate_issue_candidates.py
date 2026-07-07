#!/usr/bin/env python3
"""Validate evidence-only Issue candidates from a ChatGPT authoring pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from authoring_pack_issue_candidates import (
    STATUS_EXIT_CODES,
    cli_summary,
    validate_issue_candidates,
    write_issue_candidate_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-report", required=True, help="validation-report.json from review helper.")
    parser.add_argument("--pack-tree", required=True, help="Extracted specdock-authoring-pack tree.")
    parser.add_argument("--expected-parent-epic", required=True, help="Expected parent Epic id.")
    parser.add_argument(
        "--expected-requirement",
        action="append",
        default=[],
        help="Expected parent requirement id. Repeat for multiple values.",
    )
    parser.add_argument(
        "--expected-acceptance",
        action="append",
        default=[],
        help="Expected parent acceptance id. Repeat for multiple values.",
    )
    parser.add_argument("--issue-id", default="iss-00288", help="Issue id to record in validation trace.")
    parser.add_argument("--output-dir", required=True, help="Directory for validation report and comparison summary.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    result = validate_issue_candidates(
        Path(args.review_report),
        Path(args.pack_tree),
        issue_id=args.issue_id,
        expected_parent_epic=args.expected_parent_epic,
        expected_requirements=args.expected_requirement,
        expected_acceptance=args.expected_acceptance,
    )
    result = write_issue_candidate_outputs(output_dir, result)
    print(json.dumps(cli_summary(result, output_dir), ensure_ascii=False, sort_keys=True))
    return STATUS_EXIT_CODES[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
