#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TRIAL = ROOT / "trial-repo"
SPEC = TRIAL / "spec-dock"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def main():
    failures = []
    deps_issues_path = SPEC / ".agent" / "deps-issues.json"
    deps_issues_puml = SPEC / "deps-issues.puml"
    deps_raw_puml = SPEC / "deps-raw.puml"
    require(deps_issues_path.is_file(), "deps-issues.json exists", failures)
    require(deps_issues_puml.is_file(), "deps-issues.puml exists", failures)
    require(deps_raw_puml.is_file(), "deps-raw.puml exists", failures)
    if not deps_issues_path.is_file() or not deps_raw_puml.is_file():
        return 1

    payload = load_json(deps_issues_path)
    raw_text = deps_raw_puml.read_text(encoding="utf-8")
    issues_text = deps_issues_puml.read_text(encoding="utf-8") if deps_issues_puml.is_file() else ""
    nodes = payload.get("nodes", {})
    edges = payload.get("edges", [])
    if isinstance(nodes, dict):
        node_ids = set(nodes.keys())
    else:
        node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    edge_pairs = {
        (edge.get("from"), edge.get("to"), edge.get("relation") or edge.get("kind"), edge.get("state"))
        for edge in edges
        if isinstance(edge, dict)
    }
    contexts = {
        (
            context.get("source_issue_id"),
            context.get("target_node_id"),
            context.get("dependency_disposition"),
            context.get("disposition_basis"),
            context.get("lifecycle_state"),
        )
        for context in payload.get("dependency_contexts", [])
        if isinstance(context, dict)
    }

    require(payload.get("schema_version") == 2, "deps-issues schema_version is 2", failures)
    require(payload.get("projection") == "issue-readiness-with-dependency-context", "deps-issues v2 projection name", failures)
    require("iss-01940" in node_ids, "ready issue iss-01940 appears", failures)
    require("iss-01933" in node_ids, "blocked issue iss-01933 appears", failures)
    require("iss-01942" in node_ids, "unknown-blocked issue iss-01942 appears", failures)
    require("epic-01930" in node_ids, "empty open epic blocker appears", failures)
    require("epic-01941" in node_ids, "empty unknown epic blocker appears", failures)
    require("epic-01937" not in node_ids, "empty closed satisfied epic is omitted from active nodes", failures)
    require("epic-01929" not in node_ids, "open all-done epic is omitted from active nodes", failures)
    require(("iss-01939", "iss-01933", "compiled_issue", "blocking") in edge_pairs, "issue-to-issue blocking edge appears", failures)
    require(("iss-01933", "epic-01930", "raw_direct", "blocking") in edge_pairs, "issue-to-epic blocking raw edge appears", failures)
    require(
        ("iss-01942", "epic-01941", "raw_direct", "blocking") in edge_pairs,
        "issue-to-epic unknown raw edge appears as active blocker",
        failures,
    )
    require(("iss-01936", "epic-01937", "raw_direct", "satisfied") not in edge_pairs, "empty-closed satisfied edge is omitted from active edges", failures)
    require(("iss-01940", "epic-01929", "raw_direct", "satisfied") not in edge_pairs, "open all-done satisfied edge is omitted from active edges", failures)
    require(
        ("iss-01936", "epic-01937", "satisfied", "lifecycle_closed", "closed") in contexts,
        "empty closed satisfied context remains machine-readable",
        failures,
    )
    require(
        ("iss-01940", "epic-01929", "satisfied", "all_descendant_issues_done", "open") in contexts,
        "open all-done satisfied context remains machine-readable",
        failures,
    )
    require(
        ("iss-01933", "epic-01930", "blocking", "empty_open_container", "open") in contexts,
        "empty open high-level blocker context remains machine-readable",
        failures,
    )
    require(
        ("iss-01942", "epic-01941", "indeterminate", "empty_unknown_container", "unknown") in contexts,
        "empty unknown high-level context remains machine-readable",
        failures,
    )
    require("package" in raw_text and "init-01920" in raw_text and "epic-01934" in raw_text, "deps-raw has nested package content", failures)
    require("raw_direct" in raw_text, "deps-raw has raw_direct edge labels", failures)
    require("epic-01929" not in raw_text, "deps-raw omits open all-done satisfied high-level noise", failures)
    require("epic-01937" not in raw_text, "deps-raw omits closed satisfied high-level noise", failures)
    require("blocks" in issues_text and "satisfied" not in issues_text, "deps-issues.puml shows active blockers only", failures)
    require("epic-01929" not in issues_text and "epic-01937" not in issues_text, "deps-issues.puml omits satisfied-only high-level nodes", failures)
    if failures:
        print(f"RESULT FAIL count={len(failures)}")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
