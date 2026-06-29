---
種別: research
ID: "20260624t062339z-research"
タイトル: "MT024 Bug Exploration Routing Failure"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["MT-024", "tests/cli_runtime/test_workflow_context_routing.py"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
  - "tests/cli_runtime/test_workflow_context_routing.py"
reflected_to: []
---

# 20260624t062339z-research MT024 Bug Exploration Routing Failure

## 調査目的
- MT-024 の bug exploration で確認された routing failure を、追加 regression test と修正設計へ接続する。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
- 検証手順:
  - MT-024 の観測内容を MT-009 と照合した。
  - `_select_step`、`_completed_step_ids`、`_classify_task_kind` の current tests を確認した。

## facts / 観測できた事実
- MT-024 は MT-009 の runtime routing failure を bug exploration として再確認した。
- existing tests には次の guard が既にある。
  - scaffold report text の `S01, S02, ...` だけでは completed と扱わない。
  - Red phase の `pass` だけでは step completed と扱わない。
  - `## S01` / `### S02` heading selection は機能している。
- 一方で、routing heuristic の競合条件は未検証。
  - negated security / privacy wording
  - runtime allowed paths
  - `unit_tests` obligation
  - docs-only verification phrase
  - explicit `dev-coder` / `code-reviewer` hints

## inference / 推測
- MT-024 の failure は selector の step skip 問題ではなく、selected step block の kind classification 問題として扱うべき。
- 既存の completion / heading tests は維持しつつ、routing conflict cases を同じ `test_workflow_context_routing.py` に追加するのが自然。
- bug exploration の期待文にある「scaffold report text を completion と扱わない」は既に automated test があるため、今回の新規修正対象からは外してよい。

## unverified / 未検証事項
- manual test で使った exact plan block を fixture 化した場合、現行 main checkout の tests でも同じ failure が再現するか。
- Japanese negative phrasing と English negative phrasing の両方をどこまで support するか。

## regression test candidates
- `test_workflow_next_runtime_paths_override_docs_only_verification_phrase`
  - plan に `spec-dock/scripts/spec_dock_runtime/...`、`tests/...`、`unit_tests`、`docs-only verification` を含める。
  - 期待: `task_kind=runtime`、`worker=dev-coder`、`verification=["unit_tests"]`。
- `test_workflow_next_negated_security_phrase_does_not_escalate`
  - plan に `not security-sensitive` または `security/privacy-sensitive として過剰に分類しない` を含める。
  - 期待: その phrase だけでは `security-sensitive` にならない。
- `test_workflow_next_affirmative_security_phrase_still_escalates`
  - plan に `authentication`、`authorization`、`permissions`、`security_review` を含める。
  - 期待: `security-sensitive` / `xhigh`。

## implications / 判断への含意
- MT-024 は MT-009 と同じ fix scope に統合してよい。
- ただし test naming では「bug exploration」として、誤分類の再現に加え、既存の selector / completion safeguards が壊れていないことを守る。
- 修正後は MT-015 の symlink abuse retest を fresh trial repo で追加実施する。
