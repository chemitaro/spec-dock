---
種別: レポート（Epic）
ID: "epic-00107"
タイトル: "Worktree Provisioning"
状態: "in_progress"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00002"]
---

# epic-00107 Worktree Provisioning — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - requirement phase は調査、reuse 判定、要件定義、fresh spec-reviewer gate まで完了。
  - design phase は既存 runtime 責務境界、failure contract、bootstrap contract、test strategy を固定し、fresh spec-reviewer gate まで完了。
  - plan phase は issue 分割、tranche、integration checkpoint、quality gate、rollout/docs impact、final exit contract を作成済み。
  - `requirement.md` / `design.md` / `plan.md` は `approved`。
  - GitHub-linked issue `iss-00108` (#108), `iss-00109` (#109), `iss-00110` (#110) を作成済み。
  - `worktree create` runtime core / CLI / docs / dogfooding parity の実装と tests は完了。
  - reviewer feedback により label raw validation、bootstrap failure/detection failure tests、fatal Git/path failure tests、dogfooding parity maps を追加済み。
  - final code-reviewer / qa-reviewer / spec-reviewer gates は pass。
- 次のマイルストーン:
  - final commit / push / epic-level PR 作成。
- ブロッカー:
  - なし。

## Spec Authoring Gate

| phase | investigated facts | open questions | delegation consent | reviewer | verdict | fixes | promotion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| requirement | `workflow_epic.md`, `workflow_spec_authoring.md`, `phase_requirement.md`, upstream `init-local-00002/requirement.md`, existing `epic-00054` / `epic-00074`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{cli,commands,application,infra,presentation}`, `tests/cli_runtime`, `/Users/iwasawayuuta/workspace/product/taikyohiyou_project-issue-1716/scripts/worktree/create_worktree.sh`, `Makefile`, `docs/dynamic-worktree-support.md`, Git worktree manual, Codex app worktree/local-environment/AGENTS.md docs | User intent was sufficient after local investigation. `MakeInit` was interpreted as `make init` from reference product evidence. User later accepted the recommended decisions for CLI shape and output path style: `spec-dock worktree create [LABEL]` and absolute path primary output. | User explicitly requested `$spec-dock-epic-planning`; reviewer use was limited to current repo/worktree, epic-00107, current session, `spec-reviewer`; destructive action, external publishing, credentialed access, scope expansion, and write-capable delegation excluded. | Fresh `spec-reviewer` 1 (`019e4eab-143a-7482-9f65-79fff2a99f60`) failed on bootstrap exit-code contract, linked-worktree invocation behavior, and research metadata. Fresh `spec-reviewer` 2 (`019e4ead-72c1-7d41-856d-792506c65cc2`) passed with P2/P3 hardening suggestions. Fresh `spec-reviewer` 3 (`019e4eb0-1eff-7ef1-bfa2-f3d7f3583b0c`) returned findings `[]`, `review_status: pass`. | passed | Fixed bootstrap failure to exit code 0 with warning, defined linked-worktree invocation normalization to main worktree, completed research metadata, added non-retryable Git failure AC, added `20260522t075615z-disc-new-epic-reuse-decision.md` for new-epic rationale, and resolved the two requirement open questions with the user-approved recommended options. | Promote requirement to design. |
| design | Approved `requirement.md`, `phase_design.md`, `workflow_epic.md`, existing runtime parser / registry / dispatch / UseCases / Ports / GitGateway / CliText patterns, `tests/cli_runtime/harness.py`, reference product `create_worktree.sh`, Git worktree behavior, optional `make init` bootstrap constraints. | No user questions remained. Design-local choices were fixed in the design: candidate retry ceiling `10000`, `make -n init` detection with `detection_failed` warning, fatal Git partial failures as `RuntimeError`, absolute path output, and `worktree create` CLI shape. | Same epic-planning scope and reviewer boundary as requirement gate. | Fresh `spec-reviewer` 1 (`019e4edf-36ad-7243-a7b8-29b7f8a8ef0c`) failed on undefined retry ceiling, unclassified bootstrap detection errors, and proposed-only reuse-disc authority. Fresh `spec-reviewer` 2 (`019e4ee2-a04a-7a31-83b5-2d7e3f4705db`) returned findings `[]`, `review_status: pass`. | passed | Added retry ceiling `10000` and fatal no-candidate output contract, classified `make -n init` non-target failures as non-fatal `detection_failed`, and finalized reuse-decision discussion metadata. | Promote design to plan. |
| plan | Approved `requirement.md`, approved `design.md`, `phase_plan.md`, `phase_plan_epic.md`, `workflow_epic.md`, upstream `init-local-00002/plan.md`, and generated `plan.md` issue slicing. | No open plan questions. Issue numbering is planned as `iss-00108`..`iss-00110`; actual creation may adjust only if runtime allocation conflicts. | Same epic-planning scope and reviewer boundary as requirement gate. | Fresh `spec-reviewer` 1 (`019e4ee6-655e-7551-968f-f246729b5cce`) failed because `report.md` still described `plan.md` as unstarted and pointed next milestone back to design work. Fresh `spec-reviewer` 2 (`019e4ee8-cb7d-7aa1-99d4-c11c413acf90`) returned `review_status: pass` with one P3 stale follow-up wording cleanup. | passed | Updated progress summary, next milestone, blocker, follow-up, and plan gate ledger to reflect the authored plan and reviewer finding. Removed stale design-phase follow-up wording. | Promote plan to issue decomposition. |

## 決定事項（ADRリンク） (必須)
- ADR なし。
- `20260522t075615z-disc-new-epic-reuse-decision.md`: 既存 `epic-00054` / `epic-00074` ではなく、新規 `epic-00107` として worktree 作成 capability を扱う。
- `requirement.md` Q-001: CLI shape は `spec-dock worktree create [LABEL]` を採用する。
- `requirement.md` Q-002: command output は absolute path を主表示する。
- `design.md`: candidate retry ceiling は `10000` とし、超過時は fatal `RuntimeError` とする。
- `design.md`: `make -n init` detection failure は non-fatal `bootstrap_status=detection_failed` warning とする。

## 完了した Issue / PR / Release (必須)
- `iss-00110` Worktree create core use case:
  - core contracts, ports, Git / make adapters, and core tests implemented.
- `iss-00108` Worktree create CLI and output:
  - parser, registry, command handler, bootstrap wiring, output rendering implemented.
- `iss-00109` Worktree docs dogfooding and final verification:
  - provider docs, dogfooding docs/runtime parity, snapshot/parity tests, and final verification evidence added.
- PR:
  - pending epic-level single PR.

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001 basic create:
  - pass via `test_worktree_create_uses_sibling_container_auto_id_and_branch`.
- E-AC-002 repeated create / collision:
  - pass via `test_worktree_create_retries_collisions_and_accepts_label`, `test_worktree_create_retries_auto_id_collisions`, and `test_worktree_create_retries_git_add_collision`.
- E-AC-003 label naming:
  - pass via label success tests and slash-current-branch branch prefix test.
- E-AC-004 invalid label:
  - pass via invalid label matrix for underscore, uppercase, dot, slash, spaces, leading whitespace, whitespace-only labels, and shell metacharacters.
- E-AC-005 `make init` success:
  - pass via `test_worktree_create_runs_make_init_when_available`.
- E-AC-006 bootstrap skipped:
  - pass via no-Makefile basic create test reporting `bootstrap status=skipped`.
- E-AC-007 bootstrap detection/execution failure warning + exit `0`:
  - pass via `test_worktree_create_keeps_worktree_when_make_init_fails` and `test_worktree_create_keeps_worktree_when_make_init_detection_fails`.
- E-AC-008 linked-worktree normalization:
  - pass via `test_worktree_create_normalizes_container_from_linked_worktree`.
- E-AC-009 non-retryable Git/path failure:
  - pass via container-file fatal path and non-collision `cannot lock ref` fatal classification test.
  - Container creation failures include `artifact_state=path_exists:<bool>,branch_exists:<bool>,record_exists:<bool>` for the attempted worktree.
  - Non-retryable `git worktree add` failures include attempted id/path/branch and `artifact_state=path_exists:<bool>,branch_exists:<bool>,record_exists:<bool>` so the caller can see whether no artifacts were created or partial state remains.
- E-AC-010 detached/outside repo failure:
  - pass via detached HEAD and outside Git repo tests.
- E-AC-011 provider / dogfooding / docs parity:
  - pass via docs/runtime parity tests and dogfooding command help smoke.

## Final Quality Gate
- Verification:
  - `python -m unittest tests.cli_runtime.test_worktree tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v`: pass, 17 tests.
  - `python -m unittest discover -v`: pass, 827 tests.
  - `./spec-dock/scripts/spec-dock validate`: pass, `nodes=50`.
  - `./spec-dock/scripts/spec-dock sync`: pass.
  - `git diff --check`: pass.
- Reviews:
  - final `code-reviewer`: pass, no findings.
  - final `qa-reviewer`: pass, P2 follow-up test-depth suggestions only.
  - final `spec-reviewer`: pass, P2 traceability suggestion addressed in `iss-00110/plan.md`.
- PR Delivery:
  - Pending external delivery evidence. One epic-level PR will link #108, #109, and #110.

## ロールアウト結果（必要なら） (任意)
- Shipped runtime assets updated under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.
- Dogfooding runtime mirror updated under `spec-dock/scripts/spec_dock_runtime/`.
- Shipped docs and dogfooding docs updated with `reference_worktree.md`.
- `uvx --from . spec-dock update .` failed due external uv cache permission; `PYTHONPATH=src python -m spec_dock.cli update .` partially updated runtime before managed `.agents` permission failure, and direct parity evidence now confirms relevant runtime/docs mirror files match provider assets.

## フォローアップ（別Issue化） (必須)
- Future extension:
  - `worktree list` / `show` / `remove` are implemented in the current epic scope through E-AC-012 / E-AC-013 and `iss-00137`.
  - `worktree status` / `prune` / `repair` remain out of scope.
  - Codex-managed worktree cleanup remains out of scope.

## 省略/例外メモ (必須)
- User requested one epic-level PR rather than one PR per issue; issue execution was sequenced on the epic branch and will be delivered by one PR.
- `issue finish` is intentionally deferred until after the epic-level PR is merged because `issue finish` closes the linked GitHub issue; running it before merge would prematurely close #108, #109, and #110. The PR body should link these issues with merge-time closure keywords, and post-merge cleanup should run the lifecycle closure.
- Write-capable subagent delegation was not used because current host policy requires explicit subagent delegation permission; local implementation was recorded as Parent Implementation Exception in issue reports.
