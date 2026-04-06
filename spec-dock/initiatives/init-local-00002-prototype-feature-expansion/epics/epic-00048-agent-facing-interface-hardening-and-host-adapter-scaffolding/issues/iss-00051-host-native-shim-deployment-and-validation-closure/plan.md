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
    - provider asset / manifest / installer sync-prune の実装と regression test
  - exit:
    - gate-2 を機械検証できる状態
- M2:
  - 対象:
    - dogfooding mirror / manual validation / final closure
  - exit:
    - gate-3 / gate-4 / extension_closure を同 issue で閉じる

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - manifest / asset / test contract を先に固定しないと installer 実装も manual validation schema もぶれる
  - installer sync/prune が固まってから dogfooding/manual validation を回す
- step ordering notes:
  - S01 が manifest shape と asset path を固定
  - S02 が installer sync/prune と regression test を閉じる
  - S03 が dogfooding/manual validation / final review evidence を閉じる

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - provider assets と manifest shape が issue contract と一致する
  - closes:
    - AC-001 の前半
  - review gate:
    - spec/design alignment
- S02:
  - 観測可能な振る舞い:
    - init/update で native shim が生成/更新され、obsolete managed file だけが prune される
  - closes:
    - AC-001
    - AC-002
    - EC-002
  - review gate:
    - implementation review + regression tests
- S03:
  - 観測可能な振る舞い:
    - dogfooding workspace と manual validation evidence が両 host 分そろい、fixed closure schema で final closure を判定できる
  - closes:
    - AC-003
    - AC-004
    - EC-001
    - EC-003
  - review gate:
    - QA review + final spec review

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S03
- EC-001 -> S03
- EC-002 -> S02
- EC-003 -> S03

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S02 実装後
  - scope:
    - manifest shape / installer sync-prune / tests
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S03 manual validation evidence 収集後
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

### S01 — native shim contract fixed point
- target:
  - provider-side native shim assets の配置先
  - manifest exact fields
  - gate-2 / gate-3 / gate-4 evidence shape
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `変更計画`
- step boundary:
  - ここではコード本体より先に asset path / manifest shape / test fixture contract を固定する

#### Red
- failing test:
  - manifest shape と provider asset path が存在しない/一致しないテストを追加する
- expected failure:
  - native shim asset 未存在または meta shape 不足で失敗する

#### Green
- minimum implementation:
  - provider asset 配置先と manifest shape を追加する
- pass condition:
  - S02 で installer 実装に進める前提ファイルが揃う

#### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - manifest shape / asset path / issue docs 整合
- expected tests:
  - targeted installer fixture tests
- report update:
  - reviewer verdict / test結果 / 修正内容を `spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — installer sync/prune and regression closure
- target:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - related provider assets
- design refs:
  - `design.md` の `変更計画`
  - `design.md` の `テスト戦略`
- step boundary:
  - gate-2 sync/prune verification を通せる実装まで

#### Red
- failing test:
  - `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke`
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
- expected failure:
  - 現状は native shim 未配備 / prune policy 不足で失敗する

#### Green
- minimum implementation:
  - manifest を読んで native shim を copy/update/prune する installer 拡張
- pass condition:
  - `gate_2_sync_prune_pass` の 5 subchecks を exact fixture/path/command sequence で tests と手順の両方から再現できる

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
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S03 — dogfooding/manual validation and closure
- target:
  - dogfooding workspace
  - manual validation evidence
  - final review evidence
- design refs:
  - `design.md` の `テスト戦略`
  - `design.md` の `要件 / 例外 -> verification mapping`
- step boundary:
  - required host set の両 host を含む gate-3 と gate-4 を閉じる

#### Red
- failing test:
  - evidence 欠落により closure 判定できない状態を明示する
- expected failure:
  - report fixed keys が埋まらない / one-host-only では closure できない

#### Green
- minimum implementation:
  - `spec-dock update .`
  - `spec-dock validate`
  - Codex canonical action:
    - `.codex/agents/spec-dock.toml` を選択し、`Summarize the active spec-dock target and the next workflow doc to read before editing.` を実行する
  - Copilot canonical action:
    - `.github/agents/spec-dock.agent.md` を選択し、同じ task 文面を実行する
  - Codex / Copilot それぞれについて以下を host-scoped に記録する
    - `selection_evidence_format`
    - `selection_signal_expected_any`
    - `selection_signal_observed`
    - `selection_signal_pass`
    - `response_target_expected`
    - `response_target_observed`
    - `response_target_pass`
    - `next_doc_expected_any`
    - `next_doc_observed`
    - `next_doc_pass`
    - `delegation_evidence_expected`
    - `delegation_evidence_observed`
    - `delegation_evidence_pass`
    - `non_reimplementation_evidence_expected`
    - `non_reimplementation_evidence_observed`
    - `non_reimplementation_evidence_pass`
    - `direct_protocol_read_expected`
    - `direct_protocol_read_observed`
    - `direct_protocol_read_pass`
    - `fallback_evidence_required`
    - `fallback_evidence_observed`
    - `fallback_evidence_pass`
  - static check は host-scoped に実行する
    - Codex: `.codex/agents/spec-dock.toml` のみ
    - Copilot: `.github/agents/spec-dock.agent.md` のみ
  - `non_reimplementation_evidence_observed` には host ごとに次の 2 コマンドの no-match を固定記録する
    - `rg -n '"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*=' <host shim>`
    - `rg -n "\.agent/.*\.json|context-pack\.md" <host shim>`
  - fixed expected values は事前に次で固定する
    - Codex `selection_signal_expected_any=["spec-dock.toml", ".codex/agents/spec-dock.toml"]`
    - Copilot `selection_signal_expected_any=["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]`
    - shared `response_target_expected=active target summary or active-none stop`
    - shared `next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`
    - Codex `delegation_evidence_expected=.agents/skills/spec-dock-codex-adapter/SKILL.md`
    - Copilot `delegation_evidence_expected=.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - gate-3 / gate-4 fixed keys と `baseline_inherited_closure` / `extension_closure` を report に記録
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
  - `spec-dock update .`
  - `spec-dock validate`
  - manual validation evidence
- report update:
  - reviewer verdict / test結果 / evidence / closing judgment を `spec-dock/active/issue/report.md` に残す
  - `report.md` には少なくとも `baseline_inherited_closure`、`extension_closure`、`follow_up_issue_*`、両 host の gate-3 fixed keys、`gate_4_review_evidence.*` を固定キーで残す
  - `selection_signal_pass` / `response_target_pass` / `next_doc_pass` / `delegation_evidence_pass` / `non_reimplementation_evidence_pass` / `direct_protocol_read_pass` / `fallback_evidence_pass` を host ごとに判定し、required host set=`codex,copilot` の両方が満たされたときのみ closure 判定へ進む
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / skill
- 対応:
  - provider docs、dogfooding mirror、issue report を同期する

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00051...HEAD`
- required validation:
  - relevant installer tests
  - `spec-dock update .`
  - `spec-dock validate`
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
  - AC-001..004 / EC-001..003 が gate evidence で閉じている
- docs impact resolved:
  - provider / dogfooding / report が同期している
- final diff approved:
  - code review / QA review / spec review が pass
