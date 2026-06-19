# iss-00209 dependency view manual test plan

| ID | 確認項目 | 手順 | 期待結果 | 実施結果 |
|---|---|---|---|---|
| TP-001 | trial repo が current provider runtime を使う | `uv run python -m spec_dock.cli update manual-tests/iss-00209-dependency-view/trial-repo` | `spec-dock: ok (update)` が出る | PASS。current checkout の runtime に更新済み。 |
| TP-002 | fake GitHub を使って sync できる | `PATH="../fake-bin:$PATH" ./spec-dock/scripts/spec-dock sync --github --no-update-active` | exit 0。`.agent/deps-issues.json`, `deps-issues.puml`, `deps-raw.puml` が生成される | PASS。`evidence/sync-github.exit` は `0`。 |
| TP-003 | open all-descendant-done high-level dependency が satisfied になる | `deps check iss-01940 --github --json` | exit 0。`ready=true`。`dependency_contexts` に `epic-01929`, `dependency_disposition=satisfied`, `disposition_basis=all_descendant_issues_done`, `lifecycle_state=open` が残る | PASS。`evidence/deps-check-ready-iss-01940-github.exit` は `0`。 |
| TP-004 | empty open high-level dependency が blocking になる | `deps check iss-01933 --github --json` | exit 3。`ready=false`。`epic-01930` が `dependency_disposition=blocking`, `disposition_basis=empty_open_container` で出る | PASS。`evidence/deps-check-blocked-iss-01933-github.exit` は `3`。 |
| TP-005 | cache/local 再確認ができる | `deps check iss-01933 --no-github --json` | exit 3。sync で得た GitHub state を cache として使い、empty open blocker を維持する | PASS。`evidence/deps-check-blocked-iss-01933-no-github.exit` は `3`。 |
| TP-006 | empty unknown high-level dependency が fail-closed になる | `deps check iss-01942 --github --json` | exit 3。GitHub lifecycle fact のない `epic-01941` が `dependency_disposition=indeterminate`, `disposition_basis=empty_unknown_container` で出る | PASS。`evidence/deps-check-unknown-iss-01942-github.exit` は `3`。 |
| TP-007 | deps-issues JSON が authority context を保持する | `./verify_projection.py` | active graph と `dependency_contexts` が分離され、blocking / satisfied / indeterminate / lifecycle / basis を確認できる | PASS。`evidence/verifier.exit` は `0`。 |
| TP-008 | PUML が active view として noise を省く | `./verify_projection.py` と `evidence/deps-issues.puml`, `evidence/deps-raw.puml` の inspection | `deps-issues.puml` は `blocks` のみを表示し、satisfied-only high-level node/edge を省く。`deps-raw.puml` は active raw direct edge を表示し、done/closed/satisfied-only high-level noise を省く | PASS。verifier が `epic-01929` / `epic-01937` の PUML omission を確認。 |
