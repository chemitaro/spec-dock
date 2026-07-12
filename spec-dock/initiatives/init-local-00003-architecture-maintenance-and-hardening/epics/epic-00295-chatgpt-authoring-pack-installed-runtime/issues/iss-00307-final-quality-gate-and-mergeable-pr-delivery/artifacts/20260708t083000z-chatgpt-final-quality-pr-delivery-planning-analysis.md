---
種別: research
created_by_role: ChatGPT-Use / GPT-5.5 Pro Extended
scope_id: iss-00307
source_paths:
  - /private/tmp/codex-agent-work/iss-00307-planning/prompt.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/issue/artifacts/20260707t171321z-draft-requirement-final-quality-gate-and-mergeable-pr-delivery-draft-requirement.md
  - spec-dock/active/issue/artifacts/20260707t171321z-01-draft-design-final-quality-gate-and-mergeable-pr-delivery-draft-design.md
  - spec-dock/active/issue/artifacts/20260707t171322z-draft-plan-final-quality-gate-and-mergeable-pr-delivery-draft-plan.md
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_applicable_external_read_only_analysis
authority: evidence_only
---

# ChatGPT final quality / PR delivery planning analysis

## 概要

ChatGPT Use / GPT-5.5 Pro Extended に、`iss-00307` の正式な要件・設計・実装計画の具体化を依頼した。回答は evidence-only であり、canonical adoption、reviewer pass、execution-ready、PR-ready、merge-ready を主張しない。

## 採用候補

- `iss-00307` は通常の実装Issueではなく、Epic 00295全体の closure / repair / PR delivery gate として扱う。
- C01〜C11 の completion evidence、deferred PR delivery rationale、dependency edge、blocking gap を closure index として確認する。
- branch が `main` に対して diverged / behind の場合、main 取り込み後に full final gate を再実行する。
- local wrapper dependency concern を final gate 対象に含める。
  - shipped runtime / docs / skills に `/Users/...` や `.codex/skills/chatgpt-use/scripts/oracle-chatgpt` の必須依存を残さない。
  - backend command は `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` で解決し、未設定は fail-closed にする。
- final quality gate を次の6 gateに分ける。
  1. Closure Index Gate
  2. Installed Surface Gate
  3. Runtime Contract Gate
  4. Evidence Safety Gate
  5. Documentation / Skill Consistency Gate
  6. PR Delivery Gate
- final verification は `git diff --check`、`spec-dock validate`、authoring help、backend unset fail-closed、local-context、ZIP safety、candidate / draft / approval validators、installed asset simulation、docs / skills / runtime consistency、deferred command absence、PR observationを含める。

## 注意点

- ChatGPT は branch compare を `ahead_by=25 / behind_by=1 / status=diverged` と観測した。これは最終PR readiness前にローカルで再確認し、必要なら main を取り込む。
- ChatGPT はローカルコマンド、CI、reviewer gate、PR observation を実行していない。記載されたコマンドは提案であり、観測済みpass evidenceではない。
- `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` は、deferred / non-scope として維持できる。

