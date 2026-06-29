---
種別: 要件定義書（Issue）
ID: "iss-00237"
タイトル: "Analyze Manual Test Routing Failures"
関連GitHub: ["#237"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["epic-00224", "init-local-00003"]
---

# iss-00237 Analyze Manual Test Routing Failures — 要件定義

## 目的
- Epic 00224 の手動テストで見つかった runtime task routing failure を修正し、runtime 作業が docs-only に過小分類されたり、否定文だけで security-sensitive に過剰分類されたりしないようにする。
- `TaskKind.RUNTIME` に到達すべき plan step は、`dev-coder` / `medium` / `unit_tests` / `code-reviewer` の workflow obligations を維持する。
- docs-only、migration、security-sensitive の true positive は壊さず、軽量化と安全側の重い routing の両方を成立させる。

## 背景・現状
- Epic 00224 の手動テスト結果は `PASS 21 / FAIL 2 / BLOCKED 1 / SKIPPED 1`。
- FAIL した2件はいずれも runtime routing 周辺である。
  - MT-009:
    - runtime command behavior task が期待した `dev-coder` / `medium` / `unit_tests` に routing されなかった。
    - 否定文 `security/privacy-sensitive として過剰に分類しない` が `security-sensitive` / `xhigh` として扱われた。
    - 否定文除去後も、runtime paths と `unit_tests` obligation がある step が `docs-only` / `doc-writer` / `low` に過小分類された。
  - MT-024:
    - bug exploration として、否定文と runtime-path precedence の問題を再確認した。
- 調査により、原因は routing policy matrix ではなく、`application/context_packets.py` の `_classify_task_kind` が plan block 全体を単純 substring で分類していることだと判明した。
- `TaskKind.RUNTIME` が正しく渡れば、`domain/context_routing.py` の routing matrix は期待どおり `dev-coder` / `medium` / `recent_fork` / `unit_tests` / `code-reviewer` を返す。

## スコープ
- 必須:
  - `_classify_task_kind` を evidence-based classifier に改善する。
  - 否定文・禁止事項・停止条件に含まれる high-risk word だけで `security-sensitive` に昇格しないようにする。
  - runtime positive evidence を docs-only weak evidence より優先する。
  - `docs-only verification` や `tests または docs-only verification` のような template-derived phrase だけで docs-only に分類しない。
  - explicit docs-only、migration、security-sensitive の既存 true positive を維持する。
  - MT-009 / MT-024 を再現する regression tests を追加する。
- 禁止:
  - routing policy matrix の意味を変更しない。
  - assurance classification policy、PR observation scripts、`workflow_state.py` を今回の修正範囲に含めない。
  - plan step への explicit `task_kind` / `risk_tags` field 導入は行わない。
  - 手動テスト evidence を削除しない。
- 対象外:
  - MT-003 empty workspace validation の product behavior 変更。
  - MT-004 `--github-issue` docs cleanup。
  - MT-015 symlink abuse fresh trial retest。
  - true lite profile authorization の rollout policy 変更。

## 非交渉制約
- 過小分類を避ける。docs-only か runtime か曖昧な場合は runtime 側に倒す。
- security-sensitive の肯定的 evidence がある場合は、runtime evidence より security-sensitive を優先する。
- negation handling を広げすぎて、本物の authentication / authorization / permissions risk を見落とさない。
- 既存の generated context packet / runbook projection contract を壊さない。

## 受け入れ条件
- AC-001:
  - アクター: SpecDock operator
  - 前提: plan step に runtime paths、`unit_tests`、`dev-coder` / `code-reviewer` evidence と `docs-only verification` phrase が同居している。
  - 操作: `workflow next issue-execution --format json` を実行する。
  - 期待結果: selected step は `runtime` として扱われ、worker は `dev-coder`、reasoning effort は `medium`、verification は `unit_tests`、reviewer は `code-reviewer` になる。
  - 観測点: JSON の `step_assurance.selected_step.task_kind`、`worker`、`reasoning_effort`、`verification`、`reviewers`。
- AC-002:
  - アクター: SpecDock operator
  - 前提: plan step に `security/privacy-sensitive として過剰に分類しない` のような否定文があるが、肯定的な security evidence はない。
  - 操作: `workflow next issue-execution --format json` を実行する。
  - 期待結果: その否定文だけでは `security-sensitive` / `xhigh` に昇格しない。
  - 観測点: JSON の `step_assurance.selected_step.task_kind` と `reasoning_effort`。
- AC-003:
  - アクター: SpecDock operator
  - 前提: plan step が authentication / authorization / permissions / `security_review` / `privacy_review` などの肯定的 high-risk evidence を含む。
  - 操作: `workflow next issue-execution --format json` を実行する。
  - 期待結果: `security-sensitive` / `xhigh` に routing され、verification に `security_review` と `privacy_review` が含まれる。
  - 観測点: JSON の `step_assurance`。
- AC-004:
  - アクター: SpecDock operator
  - 前提: explicit docs-only plan step が存在する。
  - 操作: `workflow next issue-execution --format json` を実行する。
  - 期待結果: `doc-writer` / `low` / `docs_inspection` / `spec-reviewer` の既存 docs-only routing が維持される。
  - 観測点: JSON の `step_assurance`。
- AC-005:
  - アクター: SpecDock operator
  - 前提: plan step が migration / rollback の肯定的 evidence を含む。
  - 操作: `workflow next issue-execution --format json` を実行する。
  - 期待結果: `migration` として routing され、verification に `rollback_plan` が含まれる。
  - 観測点: JSON の `step_assurance`。
- AC-006:
  - アクター: maintainer
  - 前提: regression tests と既存 routing tests が存在する。
  - 操作: targeted pytest を実行する。
  - 期待結果: 新規 regression と既存 routing tests が成功する。
  - 観測点: `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`。

## 例外・エッジケース
- EC-001:
  - 条件: runtime evidence と docs-only weak phrase が同じ step block にある。
  - 期待: runtime を優先する。
  - 観測点: selected task kind。
- EC-002:
  - 条件: high-risk word が forbidden changes / stop conditions / 否定文にだけ出ている。
  - 期待: high-risk word だけで security-sensitive にしない。
  - 観測点: selected task kind。
- EC-003:
  - 条件: affirmative security evidence と runtime evidence が同居する。
  - 期待: security-sensitive を優先する。
  - 観測点: selected task kind と verification obligations。

## 調査・判断の根拠
- `spec-dock/active/issue/discussions/20260624t062218z-research-manual-test-summary.md`
- `spec-dock/active/issue/discussions/20260624t062221z-research-runtime-routing-failure-analysis.md`
- `spec-dock/active/issue/discussions/20260624t062338z-research-mt009-runtime-task-routing-failure.md`
- `spec-dock/active/issue/discussions/20260624t062339z-research-mt024-bug-exploration-routing-failure.md`
- `spec-dock/active/issue/discussions/20260624t062220z-disc-routing-repair-design-options.md`

## 未確定事項
- なし。explicit `task_kind` / `risk_tags` field 化は follow-up 候補として扱い、この issue では実施しない。
