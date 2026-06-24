---
種別: research
ID: "20260624t062221z-research"
タイトル: "Runtime Routing Failure Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["MT-009", "MT-024", "_classify_task_kind"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py"
  - "tests/cli_runtime/test_workflow_context_routing.py"
  - "deep-consultant:019ef84b-72cc-7d80-a111-fa09dd5d2c87"
reflected_to: []
---

# 20260624t062221z-research Runtime Routing Failure Analysis

## 調査目的
- MT-009 / MT-024 の runtime routing failure を横断し、修正すべき実装箇所、修正設計、回帰テストを明確にする。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - deep-consultant analysis `019ef84b-72cc-7d80-a111-fa09dd5d2c87`
- 検証手順:
  - context routing matrix と step classification の責務を切り分けた。
  - 手動テストの誤分類パターンを `_classify_task_kind` の current heuristic と照合した。

## facts / 観測できた事実
- `TaskKind.RUNTIME` が渡れば routing matrix は正しい obligations を返す。
- 誤分類は `application/context_packets.py` の `_classify_task_kind(text)` で起きている。
- current heuristic:
  - `security` / `privacy` を含むと `security-sensitive`
  - `migration` / `rollback` を含むと `migration`
  - `docs-only` / `docs impact` / `doc-writer` を含むと `docs-only`
  - それ以外は `runtime`
- この heuristic は section meaning、negation、allowed paths、test obligation を見ない。
- MT-009 の2段階の失敗:
  - 否定文に含まれる `security/privacy-sensitive` で `xhigh` に過剰分類。
  - 否定文除去後、runtime paths と `unit_tests` があるにもかかわらず `docs-only verification` phrase で docs-only に過小分類。

## consultant synthesis
- deep-consultant の結論:
  - routing policy 本体ではなく、step block から `TaskKind` を推定する heuristic が主因。
  - `workflow_state.py` は requirement scaffold 判定のみで、今回の task kind routing には直接関与しない。
  - `docs-only verification` は分類 signal から外すべき。
  - runtime evidence と negated high-risk evidence を分けるべき。
- 採用判断:
  - 採用する。ローカルコード読みの結果と一致する。
  - 実装方針は「heuristic 補強をこの issue の推奨修正にする。explicit `task_kind` field 化は follow-up design」とする。

## root cause
- semantic classifier ではなく substring classifier であること。
- docs-only / security / privacy の語が、task intent ではなく禁止事項、停止条件、template label、検証欄に出た場合も同じ重みで扱われること。
- runtime は positive signal として検出されず、fallback に過ぎないこと。

## recommended fix
- `_classify_task_kind` を evidence-based classifier に置き換える。
- high-risk positive evidence:
  - `security_review`, `privacy_review`, `authentication`, `authorization`, `permissions`, `privilege`, `secret`, `credential`
- high-risk negation / exclusion:
  - `not security`, `not privacy`, `security/privacy-sensitive として過剰に分類しない`, `扱わない`, `ではない`, `forbidden changes`, `停止条件`
- runtime positive evidence:
  - `dev-coder`, `code-reviewer`, `unit_tests`, `tests/`, `src/`, `spec_dock_runtime`, `commands/`, `runtime command behavior`
- docs-only positive evidence:
  - explicit task marker `docs-only`
  - `委任ロール: doc-writer`
  - allowed paths が docs / md のみ
  - verification が `docs_inspection` のみ
- docs-only weak / ignored evidence:
  - `docs-only verification`
  - `tests または docs-only verification`
  - generic template labels
- precedence:
  1. affirmative security / privacy / authz evidence
  2. migration / rollback evidence
  3. runtime positive evidence
  4. explicit docs-only evidence
  5. runtime default

## regression test plan
- Add CLI runtime tests in `tests/cli_runtime/test_workflow_context_routing.py`.
  - runtime paths + `unit_tests` + `docs-only verification` -> runtime.
  - negated security/privacy phrase alone does not escalate.
  - affirmative authentication/authorization/permissions still escalates.
  - explicit docs-only remains docs-only.
  - migration/rollback remains migration.
- If classifier is extracted to smaller helpers, add unit tests for classifier precedence.

## risks
- Negation detection can create false negatives for real security work if too broad.
- Section-aware parsing is safer than global text ignore, but larger.
- Changing heuristic may alter routing for existing plans; tests must protect docs-only / migration / security true positives.
- Long-term explicit field design may be needed if heuristic keeps growing.

## implications / 判断への含意
- iss-00237 で実装修正まで行う場合は、scope を `_classify_task_kind` と `test_workflow_context_routing.py` に絞るのが最小。
- ただし user が「まず分析」としているため、現時点では discussion artifact に設計を固定し、実装修正は次の承認で行う。
