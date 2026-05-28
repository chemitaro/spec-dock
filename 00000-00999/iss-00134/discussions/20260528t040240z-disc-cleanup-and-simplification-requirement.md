---
kind: disc
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T04:02:40Z
created_by: codex
status: answered
authority: user-approved
derived_from:
  - 20260528t035117z-disc-deep-consultant-template-workflow-followup.md
reflected_to:
  - requirement.md
---

# cleanup and simplification requirement

## 位置づけ

この文書は、ユーザー指示により追加された要件判断を記録する。
今回の grill-style clarification workflow / template / skill / agent 変更では、新しい機能や文書を追加するだけでなく、不要になった workflow、document、文言、矛盾、重複を整理することも要件に含める。

## ユーザー指示

workflow、skill、agent などを変更していくと、矛盾点、使わなくなった残骸、複雑になった document や workflow が残る。

それらは context を圧迫するだけでなく、agent の生産性を低下させ、agent の挙動がおかしくなる可能性がある。

したがって、機能や要件を追加するだけでなく、不要な workflow、不要な document、不要な文言、文章がないかを見直して整理することを要件に追加する。

## 採用判断

採用。

今回の issue では、次を requirement に含める。

- 追加する workflow / template / skill / agent guidance と矛盾する既存 guidance を見直す。
- 使われなくなる複数質問型 interview guidance などを整理する。
- 重複 template や重複 document concept を増やさない。
- agent の判断を迷わせる古い文言、不要な例、曖昧な trigger rule を残さない。
- context 圧迫や agent productivity 低下につながる documentation bloat を避ける。
- cleanup / simplification を設計と実装計画の明示的な作業対象にする。

## 要件への含意

`requirement.md` には、cleanup / simplification を必須 scope、受け入れ条件、設計で具体化する事項として反映する。

これは単なる後片付けではなく、agent-facing workflow の品質要件である。
