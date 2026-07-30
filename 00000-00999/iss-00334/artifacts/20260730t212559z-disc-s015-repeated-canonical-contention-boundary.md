---
種別: disc
ID: "20260730t212559z-disc"
タイトル: "S015 repeated canonical contention boundary"
状態: "accepted"
作成者: "codex-main"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: ["PR-351"]
authority: "issue-local-orchestrator-decision"
derived_from:
  - "fresh S015 spec-reviewer finding"
  - "requirement.md commit前失敗時の復元契約"
  - "design.md restore_mismatch recovery contract"
reflected_to:
  - "report.md Spec Interpretation / Decision Ledger"
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md"
  - "20260730t192855z-review-pr-351-s009-s015-local-closure-evidence.md"
---

# S015 repeated canonical contention boundary

## 対象論点

S015のone-shot exchange-back中に、同じcanonical pathnameへ別のatomic editorが
もう一度置換を行った場合、その最新attachmentをcanonical pathnameへ自動的に
戻し続けることまで、現IssueのP0／P1契約に含めるかを判断する。

## 観測した状態

S015は、最初のexchangeで実際にworkspaceへ移動した並行attachmentを捕捉し、
canonicalがexact staged objectのままである場合に限りone-shot exchange-backを
実施する。交換直前に第三のattachmentへ再置換された場合、交換後の検証は失敗し、
`recovery_required/restore_mismatch`でcommit／pushを行わず停止する。

この競合では、第三のattachmentはprivate workspaceに残り、先に捕捉した
並行attachmentがcanonical pathnameに戻る可能性がある。最新attachmentを破棄は
しないが、継続中の非協調的な置換のもとでcanonical pathnameが常に最新attachmentを
指すことまでは保証しない。

## 判断

- S015で修正する範囲は、exchange開始前に発生した一回の通常並行置換を、
  実際にdisplaceしたattachmentへbindして復元するところまでとする。
- compensation中に再度canonicalが置換された場合は、観測済みbytesとdurable
  evidenceを保持し、`recovery_required/restore_mismatch`で自動継続を停止する。
- 自動retry loop、cooperative lock、kernel CAS、retained storageを追加しない。
- repeated contention下でcanonical pathnameが常に最新attachmentを指す保証は、
  現IssueのP0／P1 acceptance contractへ追加しない。

## 根拠

- canonical Requirement／Designは、commit前の復元を確認できない場合に
  `recovery_required`で停止することを要求している。
- 現実装は最新attachmentを削除せず、commit／pushも行わないため、未検知の
  data lossやunauthorized deliveryにはならない。
- 競合が止まらない間もpathnameの最新性を保証するには、協調locking、retained
  storage、再試行上限、Human recovery authorityを含む別のconcurrency contractが
  必要であり、defect-only reviewの範囲を超える。

## 残余リスクと運用

- repeated contention発生時、canonical pathnameは先に捕捉したattachmentを指し、
  最新attachmentはprivate workspaceへ保持されることがある。
- 状態は`recovery_required/restore_mismatch`として表面化し、Humanが保存された
  evidenceを確認して復旧する。
- この残余リスクだけを理由に現PRへbranch mutationやarchitecture追加を行わない。
- 将来、無停止のmulti-writer保証が必要になった場合だけ、独立Issueとして
  concurrency authority、locking／CAS、retention／purge、retry policyを設計する。

## Oracle local configuration boundary

本判断はOracle境界を変更しない。PATHで解決されたローカルOracleは自身の通常
native configを利用でき、SpecDockはこれを上書き、無効化、隔離、強制しない。
formal workflowに必須の値だけを明示fieldからdirect argvへ渡す。
