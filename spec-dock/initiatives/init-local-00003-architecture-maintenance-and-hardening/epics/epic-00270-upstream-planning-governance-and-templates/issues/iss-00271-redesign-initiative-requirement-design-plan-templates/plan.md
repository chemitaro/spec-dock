---
種別: 実装計画書（Issue）
ID: "iss-00271"
タイトル: "Redesign Initiative Requirement Design Plan Templates"
関連GitHub: ["#271"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00271 Initiative テンプレート再設計 — 実装計画

## 証跡採用
| 証跡 | 採用判断 | 理由 |
|---|---|---|
| `artifacts/20260702t081001z-draft-plan-initiative-template-redesign-pre-start-seed.md` | partially_adopted | 実行順と対象ファイル候補は有用だが、正本計画としては検証ゲートとテスト対応が不足していた。 |
| `artifacts/20260702t090341z-draft-plan-implementation-plan-initiative-template-redesign.md` | partially_adopted | step order、target files、test ladder、finish gate を採用する。diff guard failed は artifact 作成時の並行未追跡artifactによるため、正本採用時の成功証跡としては扱わない。 |

## 実装方針
- provider-side Initiative templates を先に更新し、dogfooding mirror を同内容へ同期する。
- 3 templates を一つの語彙セットとして扱い、分断した表現にしない。
- template tests は全文一致ではなく、主要契約 fragment と禁止事項を確認する。
- `authoring/scope-layering.md` への final link は `iss-00273` に残し、この Issue では dangling link を作らない。

## 変更許可範囲
| 種別 | パス | 内容 |
|---|---|---|
| provider templates | `src/spec_dock/assets/spec_dock/templates/initiative/{requirement,design,plan}.md` | Initiative template prompt の再設計。 |
| dogfooding mirror | `spec-dock/templates/initiative/{requirement,design,plan}.md` | provider template と同内容へ同期。 |
| tests | `tests/unit/infra/test_init_update.py` | Initiative template contract の focused assertion 追加。 |
| issue report | `spec-dock/active/issue/report.md` | 採用判断、実装証跡、検証結果、reviewer gate を記録。 |

## 禁止変更
- Issue grade templates、Issue profile templates、runtime command、dependency algorithm を変更しない。
- workflow docs / skills の本格更新をこの Issue に含めない。
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` を作成しない。
- PR 作成、GitHub Issue close、merge 操作を行わない。

## 実装ステップ

### S00 正規計画化
- `assurance classify --stage requirement`、`assurance compose --artifact all`、`assurance verify` を実行する。
- delegated design / plan draft を report EAL へ採用または部分採用として記録する。
- `design.md` / `plan.md` を Issue 固有の正本候補へ更新する。
- fresh `spec-reviewer` を通す。

### S01 Red: Initiative template contract test
- `tests/unit/infra/test_init_update.py` に Initiative templates の主要 fragment assertion を追加する。
- 期待する Red:
  - 現行 templates に `capability landscape`、`source-of-truth`、`Epic handoff`、`artifact adoption`、`reviewer gate`、`handoff readiness`、`controlled re-slicing` などが不足して失敗する。
- 実行:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`

### S02 Green: Initiative requirement template
- `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md` を更新する。
- `spec-dock/templates/initiative/requirement.md` を同期する。
- 閉じる要件:
  - `I271-AC-001`, `I271-AC-004`, `I271-AC-005`, `I271-AC-006` の一部。

### S03 Green: Initiative design template
- `src/spec_dock/assets/spec_dock/templates/initiative/design.md` を更新する。
- `spec-dock/templates/initiative/design.md` を同期する。
- 閉じる要件:
  - `I271-AC-002`, `I271-AC-004`, `I271-AC-005`, `I271-AC-006`, `I271-AC-007` の一部。

### S04 Green: Initiative plan template
- `src/spec_dock/assets/spec_dock/templates/initiative/plan.md` を更新する。
- `spec-dock/templates/initiative/plan.md` を同期する。
- 閉じる要件:
  - `I271-AC-003`, `I271-AC-004`, `I271-AC-005`, `I271-AC-006`, `I271-AC-007` の一部。

### S05 Refactor / parity
- provider templates と dogfooding mirror の差分がないことを確認する。
- template wording を日本語ファーストに整え、policy の長文複製を避ける。
- dangling `authoring/scope-layering.md` link がないことを確認する。

### S90 検証
- Focused test:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
- Mirror parity:
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
- 必要に応じた broader scaffold regression:
  - `uv run pytest tests/unit/infra/test_init_update.py`
- SpecDock validation:
  - `./spec-dock/scripts/spec-dock validate`

### S99 完了ゲート
- report に Red / Green / Refactor、検証コマンド、未実施理由、残リスクを記録する。
- `spec-reviewer` で要件・設計・計画・実装差分の整合性を確認する。
- 実装差分があるため `code-reviewer` または `qa-reviewer` によるレビューを通す。
- PR は作らず、完了後に `issue finish` で `iss-00272` へ進む。

## 具体テストケース
| テストID | 対象 | 目的 | コマンド / 観測 |
|---|---|---|---|
| T271-001 | Initiative template contract | `requirement` / `design` / `plan` template が上流 planning prompts を持つことを確認する。 | `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` |
| T271-002 | provider / dogfooding parity | provider templates と checked-in dogfooding mirror が一致することを確認する。 | `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` |
| T271-003 | SpecDock tree | active Issue と spec tree が構造的に妥当であることを確認する。 | `./spec-dock/scripts/spec-dock validate` |
| T271-004 | forbidden wording | mandatory DDD / EDA、Issue-level TDD、private design、dangling scope-layering link がないことを確認する。 | `rg` による targeted inspection |

## 報告証跡の記録先
| 証跡 | 記録先 |
|---|---|
| S00 planning normalization / reviewer pass | `report.md#仕様-authoring-ゲート` |
| Red / Green / Refactor 実行結果 | `report.md#Step Evidence` |
| テストコマンド結果 | `report.md#検証` |
| reviewer verdict | `report.md#仕様-authoring-ゲート` と `report.md#完了--PR` |
| Issue完了判断 | `report.md#完了--PR` |

## Reviewer obligations
- `spec-reviewer`: 正本 requirement / design / plan / report と template diff の整合性を確認する。
- `code-reviewer`: tests または scaffold behavior assertion を変更した場合に、実装差分とテストの妥当性を確認する。
- `qa-reviewer`: 検証範囲が Issue acceptance criteria を十分に覆っているかを確認する。

## 受け入れ条件とステップ対応
| 要件 | 主ステップ | 検証 |
|---|---|---|
| `I271-AC-001` | S01, S02 | focused assertion / template read-through |
| `I271-AC-002` | S01, S03 | focused assertion / template read-through |
| `I271-AC-003` | S01, S04 | focused assertion / template read-through |
| `I271-AC-004` | S02-S05 | grep / reviewer |
| `I271-AC-005` | S02-S05 | grep / reviewer |
| `I271-AC-006` | S02-S05 | Japanese-primary test / reviewer |
| `I271-AC-007` | S03-S05 | dangling link check / reviewer |

## バトン出力
- `iss-00272` が再利用できる上流 planning 語彙。
- `iss-00273` が接続する scope-layering reference link の未完了事項。
- `iss-00276` が final PR description に含められる Issue完了証跡。
