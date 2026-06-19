# iss-00209 dependency view manual summary report

## Status

PASS.

The trial repository reproduces the iss-00209 lifecycle / disposition cases without a real GitHub repository:

- `iss-01940 -> epic-01929`: GitHub-open epic whose descendant issues are all closed. It is ready with `dependency_disposition=satisfied` and `disposition_basis=all_descendant_issues_done`.
- `iss-01933 -> epic-01930`: GitHub-open epic with no descendant issues. It is blocked with `dependency_disposition=blocking` and `disposition_basis=empty_open_container`.
- `iss-01936 -> epic-01937`: GitHub-closed empty epic. It is satisfied with `disposition_basis=lifecycle_closed`.
- `iss-01939 -> iss-01933`: issue-level blocker remains active.
- `iss-01942 -> epic-01941`: empty epic with no GitHub lifecycle fact. It fails closed with `dependency_disposition=indeterminate` and `disposition_basis=empty_unknown_container`.

Command summary from `evidence/capture-summary.txt`:

```text
sync-github: exit=0
deps-check-ready-iss-01940-github: exit=0
deps-check-blocked-iss-01933-github: exit=3
deps-check-blocked-iss-01933-no-github: exit=3
deps-check-unknown-iss-01942-github: exit=3
verifier: exit=0
```

## Generated artifacts

- `trial-repo/spec-dock/.agent/deps-issues.json`
- `trial-repo/spec-dock/deps-issues.puml`
- `trial-repo/spec-dock/deps-raw.puml`
- `evidence/`

Evidence copies:

- `evidence/.agent__deps-issues.json`
- `evidence/deps-issues.puml`
- `evidence/deps-raw.puml`
- `evidence/tree.puml`
- `evidence/tree-all.puml`
- `evidence/dashboard.md`
- `evidence/*.{stdout,stderr,exit}`

## Observations

- `.agent/deps-issues.json` is the readiness / blocker authority and keeps `dependency_contexts` for satisfied high-level dependencies.
- `deps-issues.puml` renders active blockers with `blocks` and omits satisfied-only `epic-01929` / `epic-01937` nodes and edges.
- `deps-raw.puml` renders active raw direct dependencies and omits done / closed / satisfied-only high-level noise from the active raw view.
- Unknown high-level dependencies remain visible as active indeterminate blockers until lifecycle facts become known.
- Complete raw metadata remains available from `.meta.json.depends_on` and `.agent/index-all.json`.

## GitHub repo requirement

No real GitHub repository is required. `fake-bin/gh` returns deterministic `issue list` and `issue view` JSON for `example/repo`.

## Residual risks

- This manual fixture uses a deterministic fake `gh` and does not exercise live GitHub API failure modes.
- The trial repo is intentionally small; it validates the lifecycle/disposition and active-view rules, not every graph topology.
