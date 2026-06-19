# iss-00209 dependency view manual progress log

| Step | Command / 作業 | Result | Notes |
|---|---|---|---|
| 01 | Copy prior realistic fixture into `manual-tests/iss-00209-dependency-view` | PASS | iss-00207 fixture structureを再利用。 |
| 02 | Remove copied nested `.git`, then reinitialize trial repo with `git init` and `git remote add origin https://github.com/example/repo.git` | PASS | Runtime GitHub repo detection用に最小 Git metadata を再作成。 |
| 03 | `uv run python -m spec_dock.cli update manual-tests/iss-00209-dependency-view/trial-repo` | PASS | current provider runtime に更新。 |
| 04 | Adjust fixture metadata | PASS | Parent epic high-level dependenciesを外し、`iss-01940 -> epic-01929` と `iss-01933 -> epic-01930` を独立して観測できるようにした。 |
| 05 | Adjust fake GitHub state | PASS | `epic-01929` は open、descendant issues `iss-01730` / `iss-01731` は closed。`epic-01937` は closed。`epic-01930` は open empty。 |
| 06 | First current-runtime capture | EXPECTED FAIL | 旧 verifier が satisfied edge を PUML に出す旧仕様を期待していた。 |
| 07 | Update `verify_projection.py` | PASS | `dependency_contexts` に satisfied context が残り、PUML から satisfied-only high-level node/edge が省かれることを確認する仕様へ変更。 |
| 08 | `./capture_evidence.py` | PASS | sync exit 0, ready check exit 0, blocked checks exit 3, verifier exit 0。Generated artifacts copied into `evidence/`。 |
| 09 | Direct evidence inspection | PASS | `.agent__deps-issues.json` に lifecycle/disposition/basis があり、`deps-issues.puml` は active blockers only、`deps-raw.puml` は active raw direct edge のみ。 |
| 10 | Add unknown fail-closed fixture for spec-reviewer P1 | PASS | Added `epic-01941` with missing fake GitHub status and `iss-01942 -> epic-01941`; fake GitHub keeps `iss-01942` open. |
| 11 | Re-run `./capture_evidence.py` and `./verify_projection.py` | PASS | `iss-01942` exits 3 and verifier confirms `dependency_disposition=indeterminate`, `disposition_basis=empty_unknown_container`. |
