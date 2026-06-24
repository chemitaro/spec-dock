---
種別: research
ID: "20260624t062218z-research"
タイトル: "Manual Test Summary"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md"
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
reflected_to: []
---

# 20260624t062218z-research Manual Test Summary

## 調査目的
- Epic 00224 の手動テスト結果を iss-00237 の issue-local artifact として保存し、routing failure 分析の起点にする。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/test-plan.md`
- 検証手順:
  - 手動テストの PASS / FAIL / BLOCKED / SKIPPED を issue scope に転記した。
  - FAIL / BLOCKED / SKIPPED を、後続 research の分析対象として分割した。

## facts / 観測できた事実
- 総合判定は条件付き不合格。
- 結果数:
  - PASS: 21
  - FAIL: 2
  - BLOCKED: 1
  - SKIPPED: 1
  - 合計: 25
- PASS した代表観点:
  - docs-only task は `doc-writer` / `low` / `docs_inspection` / `spec-reviewer` に routing された。
  - security-sensitive task は `dev-coder` / `xhigh` / `unit_tests` / `security_review` / `privacy_review` / code-qa-spec reviewers に routing された。
  - scaffold requirement / scaffold plan は execution に進まず fail closed した。
  - context packet / runbook は source hash と exclusion categories を含み、generated projection は Git dirty を作らなかった。
  - malformed `assurance.json` は `classification-required` / `authority-invalid` で止まった。
  - PR observation focused regression は `10 passed, 505 deselected`。
  - live PR #236 は `MERGEABLE` / `CLEAN`、4 checks success。
- FAIL:
  - MT-009: runtime task routing が期待と異なる。
  - MT-024: bug exploration で同じ routing defect を再確認。
- BLOCKED:
  - MT-003: 空の initialized workspace では `validate` が `No nodes found.` で exit 1。
- SKIPPED:
  - MT-015: symlink abuse は routing defect 発見後、同じ trial repo への破壊的ノイズを避けて未実施。

## inference / 推測
- routing defect は context routing matrix ではなく、plan block から `task_kind` を推定する前段の heuristic にある可能性が高い。
- runtime-path と test obligation がある task を docs-only に落とすことは、Epic 00224 の目的である「軽量化しつつ重い作業は重く扱う」に直接反する。
- MT-003 は product bug というより、空 workspace と initialized-but-empty workspace の validation semantics の問題である可能性が高い。
- MT-015 は未実施なので、routing 修正後に fresh trial repo で再実施するべき manual regression である。

## unverified / 未検証事項
- routing defect の修正案を実装した場合、existing docs-only / migration / security-sensitive tests に regression がないか。
- `_classify_task_kind` の heuristic 修正だけで十分か、plan schema に explicit `task_kind` field を導入すべきか。
- symlink abuse が current implementation で本当に fail closed するか。

## implications / 判断への含意
- iss-00237 では、まず analysis artifact と修正設計を固定する。
- 実装修正に進む場合は、少なくとも以下の regression tests が必要。
  - negated security / privacy wording does not escalate.
  - runtime allowed paths and unit test obligation select runtime.
  - docs-only verification phrase alone does not force docs-only when runtime paths exist.
  - explicit security / privacy / authz language still escalates to security-sensitive.
