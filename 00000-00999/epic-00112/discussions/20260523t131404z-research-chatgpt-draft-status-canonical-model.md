---
type: research
source: chatgpt-5.5-pro
created_at: 2026-05-23T13:14:04+09:00
epic: epic-00112
topic: draft-status canonical artifact model
chatgpt_thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a11a48b-a948-83a6-9c43-246846c9dc02
status: current
---

# ChatGPT 5.5 Pro 調査: draft-status canonical artifact model

## 依頼内容

専門 author が `design.md` / `plan.md` そのものを draft として作成・更新し、main orchestrator が final authority を保持するモデルを、ゼロベースで評価した。

## 回答の要点

このモデルは採用可能。ただし、canonical path の draft は「最新案の所在地」としてだけ権威を持ち、承認済み判断、実装許可、phase 完了の権威は持たない、という意味づけが必要。

推奨される 3 layer は次の通り。

1. Evidence layer: child reports、repo analysis、research、trade-off、pre-review。
2. Draft canonical artifact layer: `design.md` / `plan.md` を `status: draft` として専門 author が更新。
3. Authority layer: main orchestrator の final review、promotion、approved status。

## 推奨された semantic rule

> canonical path の draft は最新案の所在地としてのみ権威を持つ。承認済み判断・実装許可・phase 完了の権威は持たない。

## 実装への示唆

- `system-architect` は `design.md` draft の author。
- `implementation-planner` は `plan.md` draft の author。
- main orchestrator は final owner。
- spec-reviewer final pass と main promotion がない draft は implementation-ready ではない。
- discussions-only の設計案は発見性と統合性が弱いため、長期的には draft canonical artifact model の方が良い。

## 判断

ChatGPT 5.5 Pro は、draft canonical artifact model を肯定した。ただし、その肯定は「draft を非権威として強制できる gate がある」ことを前提としている。
