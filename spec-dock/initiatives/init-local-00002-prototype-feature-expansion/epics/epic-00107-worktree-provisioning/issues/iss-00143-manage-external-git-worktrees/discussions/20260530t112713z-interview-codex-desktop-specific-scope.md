---
種別: interview
ID: "20260530t112713z-interview"
タイトル: "Codex Desktop specific scope interview"
状態: "answered"
作成者: "Codex"
最終更新: "2026-05-30"
親: ["iss-00143"]
関連:
  - "epic-00107"
scope: "issue"
scope_id: "iss-00143"
created_at: "2026-05-30T11:27:13Z"
created_by_role: "orchestrator"
status: "answered"
adoption_status: "adopted"
reflected_to: []
derived_from:
  - "spec-dock/active/issue/discussions/20260530t000000z-scratch-external-worktree-management.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-research-external-worktree-requirement-analysis.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-01-interview-external-worktree-remove-scope.md"
  - "spec-dock/active/issue/discussions/20260530t111421z-interview-worktree-root-requirement-for-external-management.md"
  - "spec-dock/active/issue/discussions/20260530t112038z-interview-external-worktree-post-remove-cleanup.md"
  - "spec-dock/active/issue/discussions/20260530t112440z-interview-managed-classification-when-root-absent.md"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260530t112713z-interview Codex Desktop specific scope interview

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - Codex Desktop generated worktree を特別扱いするか、Git linked worktree として一般化するかを決める。
  - `design.md`:
    - `$CODEX_HOME/worktrees` detection、Codex-specific metadata、Handoff / environment setup への依存有無を決める。
  - `plan.md`:
    - Codex-specific fixture が必要か、generic Git worktree fixture で十分かを決める。
- chat 上の軽微な一問では足りない理由:
  - intake の動機は Codex Desktop だが、要件に Codex-specific lifecycle を混ぜると scope が広がる。

## 質問の目的

- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - この issue が Codex Desktop worktree を特別検出・特別処理するか。
- 回答が後続判断へ与える影響:
  - requirement の scope / non-scope、実装 fixture、docs wording が決まる。

## 質問

この issue では、Codex Desktop generated worktree を `$CODEX_HOME/worktrees` などで特別扱いしますか？

- Option A:
  - Codex Desktop は動機として明記するが、実装・要件は「同一 repository の Git linked worktree」として一般化する。
  - `$CODEX_HOME/worktrees` detection、Codex Handoff、Codex environment setup、Codex metadata cleanup は scope 外にする。
- Option B:
  - Codex Desktop generated worktree を特別扱いし、`$CODEX_HOME/worktrees` 配下かどうかなどを JSON diagnostic に含める。
  - Codex-specific lifecycle は cleanup しないが、origin detection は行う。

## source-grounded context

- intake memo は Codex Desktop が spec-dock とは独立に Git worktree を作ることを動機としている。
- 親 epic の既存 scope では Codex app managed worktree internals / Handoff / cleanup は out of scope とされていた。
- 今回の先行回答により、remove 対象は all linked worktrees へ広がり、managed classification は SpecDock-created / external の diagnostic として残る。
- Git worktree record だけでも、同一 repo の external worktree は list/show/remove できる。

## Codex の分析

- Option A の利点:
  - 実装と要件が Git の一次情報に閉じる。
  - Codex Desktop の仕様変更に影響されにくい。
  - `Codex Desktop generated worktree` 以外の外部 worktree も同じ contract で扱える。
- Option A のリスク:
  - JSON から「これは Codex Desktop 由来」とまでは分からない。
- Option B の利点:
  - Codex Desktop cleanup という動機に対して、より説明的な diagnostics を出せる。
- Option B のリスク:
  - Codex-specific path / lifecycle assumptions が spec-dock runtime に入る。
  - Handoff や environment setup との境界が曖昧になりやすい。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - この issue の本質は、作成者にかかわらず同一 repo の linked worktree を inspect / cleanup できること。Codex Desktop は代表的な発生源として requirement の背景に残し、実装 contract は Git linked worktree に一般化する方が小さく、将来にも強い。
- 未回答時の影響:
  - requirement の scope / non-scope と docs wording を確定できない。

## ユーザー回答

- 回答:
  - Option A を採用する。
  - Codex Desktop は動機として明記するが、実装・要件は「同一 repository の Git linked worktree」として一般化する。
  - `$CODEX_HOME/worktrees` detection、Codex Handoff、Codex environment setup、Codex metadata cleanup は scope 外にする。
- 回答日時:
  - 2026-05-30

## 追加確認の要否

- 追加確認が必要か:
  - no
  - Codex-specific scope は requirement の背景 / 対象外として記録し、design では Git worktree record 一般の contract に閉じる。

## 採用判断

- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - Codex Desktop は今回の問題を顕在化させる代表的な発生源だが、spec-dock runtime が依存すべき正本は Git worktree record である。Codex-specific lifecycle を要件に混ぜないことで、外部作成 worktree 全般を同じ contract で扱える。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - 背景に Codex Desktop generated worktree を記載する。
  - 必須 scope は「同一 repository の Git linked worktree」として定義する。
  - `$CODEX_HOME/worktrees` detection、Codex Handoff、Codex environment setup、Codex metadata cleanup は対象外にする。
- `design.md`:
  - Git worktree record を source of truth にし、Codex-specific path / metadata detection は実装しない。
- `plan.md`:
  - tests は generic Git linked worktree fixture で閉じ、Codex Desktop specific fixture は不要とする。
- `ADR`:
  - 現時点では不要見込み。
