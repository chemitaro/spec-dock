---
種別: research
ID: "20260624t062338z-research"
タイトル: "MT009 Runtime Task Routing Failure"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["MT-009", "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py"
  - "tests/cli_runtime/test_workflow_context_routing.py"
reflected_to: []
---

# 20260624t062338z-research MT009 Runtime Task Routing Failure

## 調査目的
- MT-009 で runtime task が期待した `dev-coder` / `medium` / `unit_tests` に routing されなかった原因を特定する。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
- 検証手順:
  - 手動テストで観測された 2 回の MT-009 routing 結果を比較した。
  - `_select_step` と `_classify_task_kind` の判定順序を読んだ。
  - context routing matrix と existing tests を確認した。

## facts / 観測できた事実
- `domain/context_routing.py` の routing matrix 自体は正しい。
  - `TaskKind.RUNTIME` は `dev-coder`、`medium`、`recent_fork`、`unit_tests`、`code-reviewer`。
  - `TaskKind.DOCS_ONLY` は `doc-writer`、`low`、`minimal_packet`、`docs_inspection`、`spec-reviewer`。
  - `TaskKind.SECURITY_SENSITIVE` は `dev-coder`、`xhigh`、`security_review` / `privacy_review` を含む。
- runtime task kind を決める前段は `application/context_packets.py` の `_classify_task_kind(text)`。
- 現在の `_classify_task_kind` は次の単純な包含判定である。
  - `security` または `privacy` を含めば `security-sensitive`
  - `migration` または `rollback` を含めば `migration`
  - `docs-only`、`docs impact`、`doc-writer` を含めば `docs-only`
  - それ以外は `runtime`
- MT-009 の最初の入力では、禁止事項として「security/privacy-sensitive として過剰に分類しない」を書いたため、否定文にもかかわらず `security-sensitive` / `xhigh` に上がった。
- 否定的な security wording を除去した後、plan 内に `docs-only verification` という template-derived phrase が残っていたため、runtime paths と unit test obligation があるにもかかわらず `docs-only` に落ちた可能性が高い。
- existing test `test_workflow_next_routes_plan_derived_task_kinds` は marker 文字列だけを与える test で、否定文、allowed paths、unit test obligation、docs-only verification phrase の競合を cover していない。

## inference / 推測
- root cause は routing matrix ではなく、plan block 全体を単純 substring で読む heuristic の脆弱性。
- `docs-only verification` は「docs-only task で使う検証欄」という template language であり、task kind を docs-only と確定させる evidence としては弱い。
- `security/privacy-sensitive として過剰に分類しない` のような否定文は、現在の実装では高リスク語としてのみ扱われる。
- runtime task kind は、対象 path、委任ロール、test obligation、Green verification、明示 task marker を総合して決める必要がある。

## unverified / 未検証事項
- manual trial repo の runtime issue block から `docs-only verification` 以外のどの語が docs-only 判定に寄与したか。
- heuristic 修正だけで future templates の表現揺れに耐えられるか。
- explicit field 方式へ移行する場合の template / docs / tests / migration 影響。

## edge cases / 具体シナリオ
- 否定文:
  - `security/privacy-sensitive として過剰に分類しない`
  - `This is not a privacy task`
  - 期待: security-sensitive へ escalation しない。ただし別の肯定的 evidence があれば escalation する。
- runtime path + docs-only verification phrase:
  - allowed paths に `spec-dock/scripts/spec_dock_runtime/**` や `tests/**` があり、文中に `docs-only verification` がある。
  - 期待: runtime として扱う。
- docs-only true positive:
  - allowed paths が `docs/**` / `*.md` だけで、worker が `doc-writer`、verification が `docs_inspection`。
  - 期待: docs-only として扱う。

## implications / 判断への含意
- 修正は `_classify_task_kind` 周辺に閉じられる可能性が高い。
- 最小修正案:
  - 否定文の近傍 window を除外する。
  - docs-only 判定を runtime / migration / security より弱い signal にする。
  - runtime paths / unit_tests / dev-coder / code-reviewer を runtime positive signal として docs-only より優先する。
- より堅い設計案:
  - plan step に machine-readable `task_kind` / `risk_tags` / `worker_hint` を導入し、heuristic は fallback に限定する。
- 推奨:
  - この Epic の current scope では heuristic を補強し、explicit field 化は follow-up ADR / issue に分離する。
