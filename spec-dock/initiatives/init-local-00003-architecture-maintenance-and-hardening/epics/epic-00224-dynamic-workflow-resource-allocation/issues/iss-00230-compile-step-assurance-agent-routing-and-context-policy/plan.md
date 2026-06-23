---
種別: 実装計画書（Issue）
ID: "iss-00230"
タイトル: "Compile Step Assurance Agent Routing And Context Policy"
関連GitHub: ["#230"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00230 Compile Step Assurance Agent Routing And Context Policy — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011
- EC:
  - EC-001, EC-002, EC-003, EC-004
- 制約:
  - `authorized_profile` authority、ignored projection、reviewer clean-room fail-closed、no raw transcript / private reasoning transfer。

## 依存関係から導く実装順序
- S01:
  - domain policy と policy source を先に固定し、routing matrix と continuation semantics を red/green で閉じる。
- S02:
  - S01 の decision を Context Packet と Runbook projection へ接続する。
- S90:
  - Provider / dogfooding mirror と docs / schema 影響を同期する。
- S99:
  - Issue-wide validation、reviewer gates、final commit。

## 仕様固定クロージャ索引
| ID | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-230-001 | S01 | routing-matrix | acceptance | AC-001 | docs/runtime/migration/security step で worker / effort / verification / reviewers が異なる | StepFacts + Assurance profile | one-size-fits-all workflow | yes | red-required | domain tests |
| tc-230-002 | S01 | continuation | acceptance | AC-002, AC-006, EC-004 | same binding/revision/goal/scope/allowed paths/risk と current HEAD/worktree/file revalidation pass では continuation allowed、変更時または revalidation failure は rejected/fallback | previous invocation + current facts | stale context reuse | yes | red-required | domain tests |
| tc-230-003 | S01 | clean-room | negative | AC-003, AC-004, AC-005 | reviewer / consultant は clean_room、禁止素材を含めない | role + candidate sources | review contamination | yes | red-required | domain tests |
| tc-230-004 | S02 | runbook-extension | acceptance | AC-007 | workflow next JSON / Markdown が step assurance と context refs を返す | active issue + valid assurance | invisible routing decision | yes | red-required | CLI tests |
| tc-230-005 | S02 | generated-state | acceptance | AC-008, AC-009 | packet projection が ignored state に書かれ、path/hash/missing reason を持つ | workflow next + git status | tracked projection pollution | yes | red-required | CLI / infra tests |
| tc-230-006 | S02 | precedence | negative | AC-010, EC-001 | missing/invalid assurance では step assurance を生成しない | scaffold/missing/invalid issue | bypassed assurance gate | yes | covered-existing + red-required | CLI tests |
| tc-230-007 | S02 | invalid-policy | negative | EC-002 | invalid policy は reviewer fail-closed / worker strict fallback | broken policy source | unsafe degraded mode | yes | red-required | infra/application tests |
| tc-230-008 | S02 | invocation-observability | acceptance | AC-011 | role/effort/context mode/policy version/packet hash/source hashes/fork turn count/include-exclude categories/returned evidence refs が machine-readable event に残る | workflow next + packet projection | invisible or unverifiable delegation | yes | red-required | CLI / infra tests |
| tc-230-009 | S90 | mirror-docs | structural | docs impact | provider source と dogfooding mirror が一致する | diff -ru | scaffold drift | yes | inspect-only | parity commands |

## 実装ステップ S01 — Step Assurance と Context Routing policy を固定する
- 振る舞いの目標:
  - StepFacts と Assurance authority から routing / context / verification / reviewer obligation を deterministic に決める。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/system/assurance/context-routing-policy.json`
  - `src/spec_dock/assets/spec_dock/system/assurance/schemas/context-routing-policy.schema.json`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
  - `tests/unit/domain/test_context_routing.py`
- 閉じる要件:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, EC-002
- Red / 代替証跡:
  - `uv run pytest tests/unit/domain/test_context_routing.py` が実装前に import / expectation failure になること。
- Green 検証:
  - `uv run pytest tests/unit/domain/test_context_routing.py`
- Refactor / cleanup ガードレール:
  - domain は filesystem / CLI に依存させない。routing matrix のために既存 Assurance classification を書き換えない。
- report 証跡の記録先:
  - `report.md` の S01 セッションログ、TDD evidence、Step Contract Closure、Reviewer Gate Status、Step Commit Gate。
- amendment trigger:
  - plan markdown 以外の canonical step metadata 形式、classifier profile semantics、live sub-agent invocation requirement が必要になった場合。
- reviewer:
  - code-reviewer
- commit:
  - S01 の runtime domain / policy / unit tests のみ。

## 実装ステップ S02 — Context Packet と Runbook projection へ接続する
- 振る舞いの目標:
  - `workflow next issue-execution` が active issue の selected step assurance と packet refs を JSON / Markdown に出し、generated packet を ignored state に書く。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/context_policy_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/context_packet_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/workflow.py`
  - `tests/unit/infra/test_context_packet_store.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - existing workflow tests as needed
- 閉じる要件:
  - AC-007, AC-008, AC-009, AC-010, AC-011, EC-001, EC-002, EC-003
- Red / 代替証跡:
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_context_packet_store.py` が実装前に import / expectation failure になること。
- Green 検証:
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_context_packet_store.py tests/cli_runtime/test_workflow.py`
- Refactor / cleanup ガードレール:
  - 既存 Runbook top-level fields の互換性を維持する。generated packet / event は ignored state に限定する。
- report 証跡の記録先:
  - `report.md` の S02 セッションログ、TDD evidence、Step Contract Closure、Reviewer Gate Status、Step Commit Gate。
- amendment trigger:
  - existing workflow state precedence の変更、new CLI command 追加、tracked artifact mutation が必要になった場合。
- reviewer:
  - code-reviewer
- commit:
  - S02 の application / infra / presentation / CLI tests のみ。

## ドキュメント影響の解消ステップ S90
- step kind:
  - docs impact gate / approved-no-op unless provider-to-mirror sync changes are required.
- 閉じる closure:
  - tc-230-009
- 対象:
  - provider policy schema、dogfooding mirror、runtime docs / active issue report。
- 対応:
  - `src/spec_dock/assets/spec_dock/...` から `spec-dock/...` へ必要な mirror を同期する。
  - policy JSON / schema が shipped asset として存在することを確認する。
- Red / 代替証跡:
  - inspect-only: code behavior を追加しない gate のため red test は要求しない。provider / mirror parity と shipped path inspection で閉じる。
- 検証:
  - `diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime`
  - `diff -ru src/spec_dock/assets/spec_dock/system/assurance spec-dock/system/assurance`
- Refactor / cleanup ガードレール:
  - S90 は implementation scope を広げず、S01/S02 で生じた docs / mirror drift のみ解消する。
- report 証跡の記録先:
  - `report.md` の S90 docs impact resolution、Closure Coverage、Reviewer Gate Status。
- amendment trigger:
  - shipped docs / templates / skills の behavioral text 変更が必要になった場合。
- commit / no-op gate:
  - provider / mirror sync 差分がある場合は S90 commit。差分がない場合は approved-no-op とし、parity command と `git status --short` を report に記録する。
- reviewer:
  - spec-reviewer

## 最終品質ゲートステップ S99
- step kind:
  - final verification gate / no implementation mutation except final report ledger.
- 閉じる closure:
  - tc-230-001〜tc-230-009 の integrated closure。
- 必須 validation:
  - `uv run pytest tests/unit/domain/test_context_routing.py tests/unit/infra/test_context_packet_store.py tests/cli_runtime/test_workflow_context_routing.py tests/cli_runtime/test_workflow.py`
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `make lint`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock workflow next issue-execution --format json`
- final QA gate:
  - qa-reviewer pass
- final code review gate:
  - code-reviewer pass
- final spec review gate:
  - spec-reviewer pass
- final commit gate:
  - final report ledger と verification evidence を commit する。
- Red / 代替証跡:
  - final integration gate のため red test は要求しない。S01/S02/S90 の closure evidence と full validation を統合証跡にする。
- Refactor / cleanup ガードレール:
  - S99 で runtime behavior を変更しない。reviewer 指摘への修正が必要な場合は対象 step の closure delta と re-review を記録する。
- report 証跡の記録先:
  - `report.md` の S99 final quality gate、final reviewer verdicts、final commit gate。
- amendment trigger:
  - S99 で未計画の behavior change、new artifact contract、または acceptance criteria gap が見つかった場合。

## 最終完了条件
- AC/EC 達成:
  - tc-230-001〜tc-230-009 が pass / approved-no-op。
- docs 影響解決:
  - provider / mirror parity が pass。
- 全 implementation step 完了:
  - S01, S02, S90, S99 が committed / approved-no-op。
- final quality gate pass:
  - qa-reviewer、code-reviewer、spec-reviewer が fresh pass。
- final clean state:
  - no unintended staged / unstaged changes。
