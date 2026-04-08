---
種別: 実装計画書（Issue）
ID: "iss-00051"
タイトル: "Host native shim deployment and validation closure"
関連GitHub: ["#51"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00051 Host native shim deployment and validation closure — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
  - AC-005
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - native shim は discovery/delegation only
  - required host set は `codex,copilot`
  - 実装と確認評価は同じ issue で閉じる

## マイルストーン一覧
- M1:
  - 対象:
    - baseline native shim 導入 tranche（完了済み履歴）
  - exit:
    - S01-S03 が issue の履歴として保持される
- M2:
  - 対象:
    - correction tranche の contract 追加と regression 更新
  - exit:
    - gate-2 を asset-copy contract で再検証できる状態
- M3:
  - 対象:
    - correction tranche の dogfooding / review / closure
  - exit:
    - gate-3 / gate-4 / extension_closure を追加修正込みで閉じる

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - baseline tranche は履歴として保持し、今回の correction tranche はその後ろに追加する
  - correction tranche では asset-copy contract を先に固定し、その後に current-checkout regression verification、最後に current-checkout closure verification を更新する
- step ordering notes:
  - baseline tranche（完了済み）: S01-S03
  - correction tranche（今回の実装対象）: S04-S06

## ステップ一覧
- baseline tranche（実施済み・read-only history）:
  - S01:
    - provider assets と manifest shape の baseline 固定
  - S02:
    - native shim 導入本体、installer sync/prune、baseline regression
  - S03:
    - dogfooding/manual validation / final closure の baseline evidence
- correction tranche（今回の実装対象）:
  - S04:
    - 観測可能な振る舞い:
      - asset-copy install contract が issue docs / design / test contract に独立 step として追加される
    - closes:
      - AC-005 の docs/tranche separation
    - review gate:
      - spec/design alignment
  - S05:
    - 観測可能な振る舞い:
      - init/update が provider-side asset の copy/replace を正本として扱い、asset-copy parity regression が pass する
    - closes:
      - AC-001
      - AC-002
      - EC-002
      - AC-005 の code/test correction
    - review gate:
      - implementation review + regression tests
  - S06:
    - 観測可能な振る舞い:
      - dogfooding workspace と manual validation / final review evidence が correction tranche を含めて更新される
    - closes:
      - AC-003
      - AC-004
      - EC-001
      - EC-003
    - review gate:
      - QA review + final spec review

## 要件 ↔ ステップ対応
- AC-001 -> S05
- AC-002 -> S05
- AC-003 -> S06
- AC-004 -> S06
- AC-005 -> S04, S05, S06
- EC-001 -> S06
- EC-002 -> S05
- EC-003 -> S06

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S05 実装後
  - scope:
    - manifest shape / installer sync-prune / tests
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S06 manual validation evidence 収集後
  - scope:
    - gate-2 / gate-3 / gate-4 evidence
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - 実装着手前と final closure 前
  - scope:
    - requirement / design / plan と fixed closure schema
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `Red` はまず tests / fixture / expected failure を固定する。
- `Refactor` は green 維持を前提に必要最小限で行う。
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。
- no-op の場合のみ `report.md` に理由を残し、commit を省略できる。

## 実装ステップ

### baseline tranche（履歴保持・再実行しない）
- S01-S03 は `iss-00051` の baseline native shim 導入で既に実施済み。
- 今回の作業ではこれらを編集対象の step として再実行せず、証跡付きの履歴として保持する。

### correction tranche（今回の追加修正 step）

### S04 — asset-copy contract docs alignment
- target:
  - issue requirement / design / plan
  - asset-copy install contract の追加定義
- design refs:
  - `design.md` の `baseline tranche と correction tranche の境界`
  - `design.md` の `今回の追加修正で変えるもの / 変えないもの`
- step boundary:
  - baseline tranche を残したまま、今回の修正対象が correction tranche のみであることを docs 上で固定する

#### Red
- failing test:
  - requirement / design / plan で baseline tranche と correction tranche が混在していることをレビューで検出する
- expected failure:
  - 追加修正 step が独立して定義されていないため spec review が fail する

#### Green
- minimum implementation:
  - baseline tranche を履歴として保持し、追加修正 step を独立して追記する
  - asset-copy install contract と current checkout 直実行の verification 手順を correction tranche に閉じる
- pass condition:
  - spec reviewer が correction tranche の独立性を確認できる

#### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - spec review
- expected tests:
  - issue docs consistency check
- report update:
  - reviewer verdict / 追加修正 step の定義内容を `spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S05 — asset-copy installer correction and regression
- target:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - related provider assets
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `変更計画`
  - `design.md` の `テスト戦略`
- step boundary:
  - baseline native shim 導入本体は触らず、asset-copy parity と installer correction を追加修正として通せる実装まで

#### Red
- failing test:
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli init /tmp/spec-dock-native-shim-smoke --force`
  - obsolete managed fixture:
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md`
  - unknown custom fixture:
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/skills/custom-reviewer/SKILL.md`
  - before/after target path set:
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/skills/custom-reviewer/SKILL.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-codex-adapter/SKILL.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-copilot-adapter/SKILL.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/host-adapters/meta.json`
  - five fixed subchecks:
    - `managed_codex_shim_generated_or_updated`
    - `managed_copilot_shim_generated_or_updated`
    - `obsolete_managed_fixture_pruned`
    - `unknown_custom_fixture_preserved`
    - `baseline_skill_and_metadata_untouched`
  - generated target file と provider-side asset file の byte-for-byte parity check
- expected failure:
  - 現状は asset-copy parity 未固定または verification command 不統一で失敗する

#### Green
- minimum implementation:
  - native shim / host-native agent 本文の生成・合成・テンプレート展開を持たず、source asset file を target managed file へ copy/replace する installer correction を実装する
  - current checkout installer 直実行を canonical verification command として tests / docs / report に反映する
- pass condition:
  - `gate_2_sync_prune_pass` の 5 subchecks を exact fixture/path/command sequence で tests と手順の両方から再現できる
  - generated target file が対応する source asset file と byte-for-byte で一致する

#### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - implementation review
- expected tests:
  - `tests/test_init_update.py`
  - relevant installer regression
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `spec-dock/active/issue/report.md` に残す
  - `gate_2_sync_prune_evidence.managed_codex_shim_generated_or_updated`, `managed_copilot_shim_generated_or_updated`, `obsolete_managed_fixture_pruned`, `unknown_custom_fixture_preserved`, `baseline_skill_and_metadata_untouched` を `expected/observed/pass` で固定記録する
  - `unknown_custom_fixture_preserved` は unknown custom native shim と unknown custom skill の両方が update 後も残る場合のみ `pass=true`
  - `baseline_skill_and_metadata_untouched` は `.agents/skills/spec-dock-codex-adapter/SKILL.md` / `.agents/skills/spec-dock-copilot-adapter/SKILL.md` が残り、`targets.codex.entry_file=.agents/skills/spec-dock-codex-adapter/SKILL.md` と `targets.copilot.entry_file=.agents/skills/spec-dock-copilot-adapter/SKILL.md` が維持される場合のみ `pass=true`
  - generated target file と provider-side asset file の parity 結果を記録し、本文生成ロジックを持たないことを確認する
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S06 — correction validation and closure
- target:
  - dogfooding workspace
  - manual validation evidence
  - final review evidence
- design refs:
  - `design.md` の `テスト戦略`
  - `design.md` の `要件 / 例外 -> verification mapping`
- step boundary:
  - correction tranche に対応する required host set の両 host evidence と final review を追加で閉じる

#### Red
- failing test:
  - correction tranche の evidence 欠落により closure 判定できない状態を明示する
- expected failure:
  - report fixed keys が埋まらない / one-host-only では closure できない

#### Green
- minimum implementation:
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli update .`
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli validate .`
  - Codex canonical action:
    - `.codex/agents/spec-dock.toml` を選択し、`Summarize the active spec-dock target and the next workflow doc to read before editing.` を実行する
  - Copilot canonical action:
    - `.github/agents/spec-dock.agent.md` を選択し、同じ task 文面を実行する
  - Codex / Copilot それぞれについて gate-3 fixed keys を host-scoped に記録する
  - gate-3 / gate-4 fixed keys と `baseline_inherited_closure` / `extension_closure` を report に記録する
  - direct host verification が unavailable な host では `fallback_evidence_required=true` を固定し、artifact snapshot・static delegation check・non-reimplementation static check・dated transcript/ui screenshot/cli log の bundle で host block を閉じる
- pass condition:
  - `extension_closure_pass=true`

#### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - QA review / final spec review
- expected tests:
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli update .`
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli validate .`
  - manual validation evidence
- report update:
  - reviewer verdict / test結果 / evidence / closing judgment を `spec-dock/active/issue/report.md` に残す
  - `report.md` には `baseline_inherited_closure.accepted_issues`、`baseline_inherited_closure.baseline_inherited_closure_pass`、`extension_closure.follow_up_issue_id`、`extension_closure.follow_up_issue_ref`、`extension_closure.follow_up_issue_discussion_ref`、`extension_closure.follow_up_issue_status`、`extension_closure.gate_2_sync_prune_pass`、`extension_closure.gate_2_sync_prune_evidence`、`extension_closure.gate_3_manual_validation`、`extension_closure.gate_4_review_pass`、`extension_closure.gate_4_review_evidence`、`extension_closure.extension_closure_pass` を固定キーで残す
  - `extension_closure.gate_3_manual_validation.codex` と `...copilot` には `selection_evidence_format`、`selection_signal_expected_any`、`selection_signal_observed`、`selection_signal_pass`、`response_target_expected`、`response_target_observed`、`response_target_pass`、`next_doc_expected_any`、`next_doc_observed`、`next_doc_pass`、`delegation_evidence_expected`、`delegation_evidence_observed`、`delegation_evidence_pass`、`non_reimplementation_evidence_expected`、`non_reimplementation_evidence_observed`、`non_reimplementation_evidence_pass`、`direct_protocol_read_expected`、`direct_protocol_read_observed`、`direct_protocol_read_pass`、`fallback_evidence_required`、`fallback_evidence_observed`、`fallback_evidence_pass` を host ごとに固定キーで残す
  - `extension_closure.gate_4_review_evidence` には `additive_only_scope_preserved_expected/observed/pass`、`single_follow_up_issue_rule_expected/observed/pass`、`native_manifest_shape_expected/observed/pass`、`report_schema_compliance_expected/observed/pass`、`discussion_schema_compliance_expected/observed/pass`、`host_native_scope_consistency_expected/observed/pass`、`final_review_ref` を固定キーで残す
  - 上記 closure schema がそろった上で、`selection_signal_pass` / `response_target_pass` / `next_doc_pass` / `delegation_evidence_pass` / `non_reimplementation_evidence_pass` / `direct_protocol_read_pass` / `fallback_evidence_pass` を host ごとに判定し、required host set=`codex,copilot` の両方が満たされたときのみ closure 判定へ進む
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / skill
- 対応:
  - provider docs、dogfooding mirror、issue report を同期する

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00051...HEAD`（correction tranche の追加差分）
- required validation:
  - relevant installer tests
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli update .`
  - `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli validate .`
  - gate-2 / gate-3 / gate-4 evidence complete
- reviewer approvals:
  - code review
  - QA review
  - spec review
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- 該当なし

## final exit contract
- AC/EC 達成:
  - AC-001..005 / EC-001..003 が gate evidence で閉じている
- docs impact resolved:
  - provider / dogfooding / report が同期している
- final diff approved:
  - code review / QA review / spec review が pass
