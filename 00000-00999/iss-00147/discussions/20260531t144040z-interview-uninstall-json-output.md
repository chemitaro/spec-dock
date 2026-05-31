---
kind: interview
scope: issue
scope_id: iss-00147
title: "Uninstall command JSON output scope"
status: answered
created_at: "2026-05-31T14:40:40Z"
question_id: "Q-001"
source_paths:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/plan.md
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
---

# Interview: uninstall command JSON output scope

## 背景
- `design.md` の未確定事項 `Q-001` は、`spec-dock uninstall` の初回実装で machine-readable `--json` output を含めるかどうか。
- 現在の requirement は operator-visible な dry-run plan / result summary を要求しているが、machine-readable output は明示要求していない。
- 回答前の plan は `--json` を scope 外 / follow-up 候補として扱っていた。

## 質問
`spec-dock uninstall` の初回実装に `--json` output を含めますか。

## 選択肢
- A:
  - 初回実装では human-readable output のみとし、`--json` は follow-up 候補にする。
- B:
  - 初回実装から `--json` output を追加し、plan/result の machine-readable contract と tests も今回 scope に含める。

## 推奨
- A。
- 理由:
  - 今回の primary objective は agent / skill noise removal と安全な repo-local uninstall であり、machine-readable output は必須受け入れ条件ではない。
  - `--json` を今回含めると、result schema、互換性、help/docs、tests の契約が増える。

## 回答
- B。
- `spec-dock uninstall` は agent が実行する可能性があるため、初回実装から JSON output を必ず実装する。
- `--json` は dry-run plan と apply result の両方で machine-readable output を返し、runtime wrapper からも forwarding する。
