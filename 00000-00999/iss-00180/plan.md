---
種別: 実装計画書（Issue）
ID: "iss-00180"
タイトル: "Github Token Capability Preflight"
関連GitHub: ["#180"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-11"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00180 Github Token Capability Preflight — 実装計画（実行契約）

## この計画で満たす要件ID
- AC:
  - AC-001: `doctor` が明示 target 付きで core capability findings を表示する。
  - AC-001b: `doctor` が target なしでは PR core probe を失敗扱いしない。
  - AC-002: PR observation が permission limitation を final JSON に返す。
  - AC-003: trigger write failure が core read failure と分離される。
  - AC-004: capability probe が secret を出力しない。
  - AC-005: capability probe が fixed endpoint set に閉じる。
  - AC-006: malformed input と capability limitation が分離される。
  - AC-007: `doctor` が optional extended checks を core と分離して表示する。
- EC:
  - EC-001: `GH_TOKEN` missing。
  - EC-002: auth missing。
  - EC-003: rate limit / transient failure。
  - EC-004: partial capability。
  - EC-005: optional extended check unavailable。
- 制約:
  - Provider-side source を先に変更し、必要な dogfooding mirror parity を確認する。
  - Runtime Python と installed agent scripts の間に import dependency を作らない。
  - `doctor` standalone probe で write operation を実行しない。
  - PR observation の stdout final JSON を authority とし、permission limitation を merge-prepared evidence にしない。
  - Token value / hosts.yml secret / private payload を出力しない。

## 依存関係から導く実装順序
- 参照元:
  - `requirement.md`
  - `design.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/`
- 順序ルール:
  - 共通語彙と runtime contract を先に固定する。
  - PR observation scripts は runtime contract に import せず、同じ capability code / status names を再現する。
  - Provider-side 実装後、dogfooding mirror と docs / skill guidance の差分を確認する。
- step 依存サマリー:
  - S01: Runtime doctor capability diagnostics。S02/S03 の vocabulary 前提を固定する。
  - S02: PR observation limitation classification。S01 の語彙と design の status mapping を使う。
  - S03: Installed asset guidance と dogfooding parity。S01/S02 の provider-side 差分を反映・確認する。
  - S99: Issue-wide validation / QA / review / handoff。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `spec-dock doctor` が fixed GitHub capability diagnostics を structural findings と分離して返す。
  - 依存: requirement / design の core / optional capability model。
  - unblock: PR observation 側と共通に使う capability code / status vocabulary。
  - 対象ファイル: runtime application / ports / infra / command / presentation / doctor tests。
  - 閉じる要件: AC-001, AC-001b, AC-004, AC-005, AC-007, EC-001, EC-002, EC-003, EC-004, EC-005。
  - レビューゲート: code-reviewer pass。
- S02:
  - 観測可能な振る舞い: `github-pr-observation` が read permission failure と trigger write failure を final JSON limitation として分類する。
  - 依存: S01 の語彙、design の status mapping。
  - unblock: merge-preparer が permission issue を semantic non-success として扱う証跡。
  - 対象ファイル: provider-side `github-pr-observation` scripts / script tests。
  - 閉じる要件: AC-002, AC-003, AC-004, AC-005, AC-006, EC-002, EC-003, EC-004。
  - レビューゲート: code-reviewer pass。
- S03:
  - 観測可能な振る舞い: shipped asset guidance と dogfooding mirror が provider-side 実装と矛盾しない。
  - 依存: S01, S02。
  - unblock: installed workspace / dogfooding workspace での利用可能性。
  - 対象ファイル: `SKILL.md`、dogfooding mirrors、parity tests / inspection。
  - 閉じる要件: AC-004, AC-005, AC-006, provider / mirror parity 制約。
  - レビューゲート: spec-reviewer または code-reviewer pass。
- S99:
  - 観測可能な振る舞い: issue 全体が requirement / design / plan / implementation / tests / docs の整合を満たす。
  - 依存: S01-S03。
  - unblock: PR 作成・merge-preparer へ進める状態。
  - 対象ファイル: issue-wide diff。
  - 閉じる要件: 全 AC/EC、final gate。
  - レビューゲート: qa-reviewer pass、code-reviewer pass、spec-reviewer pass。

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-001b -> S01
- AC-002 -> S02
- AC-003 -> S02
- AC-004 -> S01, S02, S03
- AC-005 -> S01, S02, S03
- AC-006 -> S02, S03
- AC-007 -> S01
- EC-001 -> S01
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S01, S02
- EC-005 -> S01

## 仕様固定クロージャ索引
| ID | step | slice | type | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | doctor-targeted-core | acceptance | AC-001, AC-004 | Target 付き doctor が `check_runs_read` permission denied を secret なしで診断する | `GH_TOKEN` source、repo/pr/head SHA、fake gateway permission denied | opaque unknown / secret leak | yes | red-required | S01 report closure |
| tc-002 | S01 | doctor-no-target | acceptance | AC-001b | Target なし doctor は PR core probe を `target_unavailable` / `skipped` とし exit 0 structural success を維持する | 通常 `spec-dock doctor` | false permission failure | yes | red-required | S01 report closure |
| tc-003 | S01 | doctor-optional-extended | acceptance | AC-007, EC-005 | `actions_read` / `issue_comments_read` は optional group に分離され、core pass/fail を汚さない | fake gateway partial optional failure | core/optional conflation | yes | red-required | S01 report closure |
| tc-004 | S01 | fixed-runtime-surface | negative | AC-005 | doctor は raw endpoint / method / jq / header / raw gh args を受け付けない | CLI parser / command args inspection | arbitrary API checker 化 | yes | inspect-only | S01 report closure |
| tc-005 | S01 | doctor-auth-source | edge | EC-001, EC-002 | `GH_TOKEN` missing は `gh_saved_auth` または `unknown` source として表示し、auth missing は `auth_missing` として permission denied と区別する | fake gateway saved-auth fallback / auth-missing | auth state misdiagnosis | yes | red-required | S01 report closure |
| tc-006 | S01 | doctor-transient-classification | edge | EC-003 | rate limit / transient / schema unavailable を `rate_limited` / `transient_unknown` / `schema_unavailable` として permission denied と区別する | fake gateway classified failures | retryable or schema issue misdiagnosed as token permission | yes | red-required | S01 report closure |
| tc-007 | S02 | checks-permission-limitation | acceptance | AC-002, EC-004 | checks/status/rollup permission denied は `exit_code=0` で final JSON に `github_token_permission_denied`、`normalized_status=unknown`、`overall_status=unknown`、`recommended_next_action=fix_github_token_permissions` を返す | stubbed `gh api` / `gh pr view` permission denied | merge-prepared false positive / downstream process failure | yes | red-required | S02 report closure |
| tc-008 | S02 | trigger-write-limitation | acceptance | AC-003 | trigger comment permission denied は `exit_code=0` で `trigger_comment_write` limitation と `human_gate` を返す | stubbed trigger script failure | blind retry / read failure conflation / downstream process failure | yes | red-required | S02 report closure |
| tc-009 | S02 | script-auth-transient-classification | edge | EC-002, EC-003 | PR observation scripts classify auth missing, rate limit, transient, and schema unavailable separately from permission denied | stubbed `gh` auth/rate/transient/schema failures | all GitHub failures collapsed into permission issue | yes | red-required | S02 report closure |
| tc-010 | S02 | script-error-semantics | negative | AC-006 | malformed input / JSON construction failure は non-zero process error で、capability limitation と混同しない | invalid repo/pr/head or malformed fixture | misuse hidden as permission issue | yes | red-required | S02 report closure |
| tc-011 | S02 | script-secret-redaction | negative | AC-004 | stdout/stderr JSON に token value / raw secret-bearing stderr を出さない | stub stderr containing token-like marker | credential leak | yes | red-required | S02 report closure |
| tc-012 | S03 | guidance-and-parity | inspect | AC-005, provider parity | SKILL guidance / provider asset / dogfooding mirror が fixed contract と一致する | provider vs mirror diff / installed asset tests | shipped behavior drift | yes | inspect-only | S03 report closure |
| tc-013 | S99 | issue-wide-quality | final gate | 全 AC/EC | focused tests、validation、reviewer gates が pass する | issue-wide diff | incomplete handoff | yes | manual-required | S99 report closure |

## レビュー / QA ゲート方針
- 各 implementation step:
  - dev-coder に bounded task として委任する。
  - step-local 実装後、fresh code-reviewer を pass まで回す。
- S03 が docs / skill guidance only で閉じる場合:
  - doc-writer または dev-coder に委任し、fresh spec-reviewer または code-reviewer を pass まで回す。
- S99:
  - qa-reviewer で obligation coverage を確認する。
  - code-reviewer で issue-wide integrated diff を確認する。
  - spec-reviewer で requirement / design / plan / report / implementation evidence の整合を確認する。

## 実行ルール（全ステップ共通）
- `report.md` に実行結果、reviewer verdict、test evidence、closure delta を記録する。
- 実装は provider-side source of truth を優先し、dogfooding mirror は parity 確認または必要な refresh として扱う。
- Capability probe の fixed endpoint set を広げる発見があれば、実装を止めて plan / design amendment と再レビューに戻す。
- Token source label は出してよいが、token value、hosts.yml secret、private payload は出してはならない。
- Live GitHub API に依存する自動テストは禁止。`gh` stub / fake gateway / fixture で閉じる。

## 実装ステップ S01 — Runtime doctor capability diagnostics
- 振る舞いの目標:
  - `doctor` に GitHub capability diagnostics channel を追加し、structural `DoctorFinding` / `DoctorResult.ok` と分離する。
- design 参照:
  - `Capability Result Model`
  - `インターフェース契約`
  - `ディレクトリ / ファイル変更計画`
- 依存:
  - なし。最初に実施する。
- unblock:
  - S02/S03 が使う common vocabulary。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/doctor.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
- planned contract:
  - Add dataclasses / Literals for GitHub capability diagnostics with fixed codes and statuses from `design.md`.
  - Add `GitHubCapabilityGateway` Protocol and `Ports.github_capability_gateway`.
  - Add optional fixed `doctor` args for repo / PR / head SHA and optional extended group; do not add raw API args.
  - No-target doctor emits skipped / target_unavailable diagnostic without structural failure.
  - Fake gateway tests must prove permission denied, optional extended separation, source label, and no secret output.
- implementation scope:
  - allowed paths: listed S01 target files only.
  - forbidden changes: PR observation scripts, unrelated doctor findings, arbitrary GitHub scanner, live network tests.
- concrete tests:
  - `tc-001`: fake gateway returns `check_runs_read` permission denied with `token_source=GH_TOKEN`; CLI/app output includes capability/status/api/source and excludes token value.
  - `tc-002`: no target returns skipped / target_unavailable diagnostic and keeps structural exit semantics.
  - `tc-003`: optional `actions_read` / `issue_comments_read` are rendered separately and do not change core result.
  - `tc-004`: parser / command assertions reject absence of raw endpoint/method/jq/header surface by inspection or negative invocation.
  - `tc-005`: `GH_TOKEN` missing renders `gh_saved_auth` or `unknown` source without secret; unauthenticated `gh` path renders `auth_missing`, not `permission_denied`.
  - `tc-006`: rate limit / transient / schema-unavailable gateway results render distinct statuses and remediation hints.
- green verification:
  - `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`
  - focused `rg` inspection for forbidden raw API argument names in doctor command surface.
- delegation contract:
  - delegated role: dev-coder.
  - input docs: `requirement.md`, `design.md`, `plan.md`.
  - required output: changed files, tests run, closure evidence for `tc-001`-`tc-006`, unresolved risks.
  - stop conditions: target fields cannot be modeled without broad command redesign; capability probe needs endpoint outside fixed set; secret redaction cannot be asserted.
- step gate:
  - reviewer: code-reviewer.
  - pass condition: `review_status: pass`.

## 実装ステップ S02 — PR observation permission limitation classification
- 振る舞いの目標:
  - `github-pr-observation` scripts が token permission failure を final JSON limitation として分類し、process success と semantic non-success を分離する。
- design 参照:
  - `Status policy`
  - `PR observation final JSON`
  - `シーケンス差分`
- 依存:
  - S01 の vocabulary。
- unblock:
  - merge-preparer / orchestrator が permission issue を machine-readable に判断できる。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- planned contract:
  - Permission denied from checks/status/rollup read produces `github_token_permission_denied` limitation with capability, API, token source, `secret_redacted=true`, `stderr_sha256`, `recommended_next_action=fix_github_token_permissions`.
  - Read permission failure maps to `normalized_status=unknown`, `overall_status=unknown`, `observation_complete=false`.
  - Trigger comment write permission failure maps to `capability=trigger_comment_write`, `normalized_status=human_gate`, `overall_status=human_gate`.
  - Malformed input / script misuse / JSON construction failure remains non-zero and is not encoded as permission limitation.
- implementation scope:
  - allowed paths: listed S02 target files only.
  - forbidden changes: raw endpoint/method args, extra write probes, retired `pr-monitor`, live GitHub tests.
- concrete tests:
  - `tc-007`: stubbed `gh api check-runs` or `gh pr view statusCheckRollup` permission denied exits 0 when final JSON is built, and yields final JSON limitation plus `unknown` semantic status.
  - `tc-008`: stubbed trigger comment permission denied exits 0 when final JSON is built, and yields `trigger_comment_write` limitation plus `human_gate`.
  - `tc-009`: stubbed auth missing, rate limit, transient, and schema-unavailable cases are not misclassified as permission denied.
  - `tc-010`: invalid inputs / malformed JSON remain non-zero process errors and do not claim token limitation.
  - `tc-011`: token-like stderr fixture is redacted or hashed; final JSON never includes the raw token marker.
- green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or codex_review or checks_snapshot'`
  - targeted shell fixture tests already housed in `test_init_update.py`.
- delegation contract:
  - delegated role: dev-coder.
  - input docs: `requirement.md`, `design.md`, `plan.md`, `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`.
  - required output: changed files, tests run, final JSON examples, unresolved risks.
  - stop conditions: status enum conflict, JSON compatibility break, needing arbitrary API surface.
- step gate:
  - reviewer: code-reviewer.
  - pass condition: `review_status: pass`.

## 実装ステップ S03 — Guidance, shipped asset, and dogfooding parity
- 振る舞いの目標:
  - Shipped guidance and dogfooding mirror expose the same fixed contract as provider-side implementation.
- design 参照:
  - `ディレクトリ / ファイル変更計画`
  - `テスト戦略`
- 依存:
  - S01, S02。
- unblock:
  - Consumer repos and this dogfooding repo can run the installed skill/runtime consistently.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/`
  - `spec-dock/scripts/spec_dock_runtime/`
  - installer / parity tests in `tests/unit/infra/test_init_update.py` if needed.
- planned contract:
  - SKILL guidance explains permission limitation semantics without turning the scripts into arbitrary permission scanners.
  - Dogfooding mirror either matches provider-side changed assets or the report records why sync is intentionally deferred.
  - Parity / install tests cover changed shipped files where practical.
- implementation scope:
  - allowed paths: listed S03 target files and focused parity assertions.
  - forbidden changes: unrelated workflow text, broad docs rewrite, credential instructions that imply token storage or secret disclosure.
- concrete tests:
  - `tc-012`: inspect provider vs dogfooding mirror and run parity / install test path that covers installed `github-pr-observation` assets.
- green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or checked_in_dogfooding_runtime'`
  - `git diff -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation`
- delegation contract:
  - delegated role: dev-coder if code/test parity changes are needed; doc-writer only if guidance-only update is needed.
  - input docs: `requirement.md`, `design.md`, `plan.md`.
  - required output: changed files, parity evidence, tests/inspection run, unresolved risks.
  - stop conditions: mirror sync would overwrite unrelated user changes; guidance needs new scope not in requirement.
- step gate:
  - reviewer: code-reviewer for code/test/scaffold changes; spec-reviewer for guidance-only changes.
  - pass condition: `review_status: pass`.

## 最終品質ゲートステップ S99
- 振る舞いの目標:
  - Issue-wide diff is implementation-ready / PR-ready with complete evidence.
- 依存:
  - S01-S03 closed.
- 対象:
  - All files changed for `iss-00180`.
- required validation:
  - `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or codex_review or checks_snapshot or checked_in_dogfooding_runtime'`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- final QA gate:
  - reviewer: qa-reviewer.
  - scope: AC/EC coverage, missing high-value tests, integration risk.
  - pass condition: `review_status: pass`.
- final code review gate:
  - reviewer: code-reviewer.
  - scope: issue-wide integrated diff, runtime/script boundaries, secret handling, compatibility.
  - pass condition: `review_status: pass`.
- final spec review gate:
  - reviewer: spec-reviewer.
  - scope: requirement / design / plan / report / implementation evidence.
  - pass condition: `review_status: pass`.
- report evidence:
  - Record command outputs, reviewer statuses, closure coverage, closure delta, and remaining risk in `report.md`.

## 未確定事項
- なし:
  - Scope、probe profile、failure semantics、runtime port / adapter、PR observation status mapping は requirement / design review で確定済み。

## 最終完了条件
- AC/EC 達成:
  - All closure IDs `tc-001` through `tc-013` are closed or explicitly amended with reviewer-approved rationale.
- docs 影響解決:
  - S03 parity / guidance evidence is recorded.
- 全 implementation step 完了:
  - S01-S03 are committed or approved-no-op with report evidence.
- final quality gate pass:
  - qa-reviewer: pass.
  - issue-wide code-reviewer: pass.
  - final spec-reviewer: pass.
- handoff:
  - `report.md` contains implementation delegation contracts, reviewer verdicts, validation commands, and PR-ready remaining risks.
