---
type: research
source: chatgpt-5.5-pro
created_at: 2026-05-23T13:14:05+09:00
epic: epic-00112
topic: bounded depth-2 specialist delegation
chatgpt_thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a11a498-2178-83a3-8baa-c99bee6f7d5f
status: current
---

# ChatGPT 5.5 Pro 調査: bounded depth=2 specialist delegation

## 依頼内容

`system-architect` / `implementation-planner` が、子 specialist を直接呼び出して調査・分析・事前レビューを行える depth=2 を採用すべきかを評価した。

## 回答の要点

bounded depth=2 は有効。ただし always-on にせず、複雑度・不確実性・影響範囲に応じて発火する trigger-based model が望ましい。

depth=2 の目的は、親 authoring agent の意思決定品質を上げることであり、子 agent に canonical artifact の author 権限や final reviewer 権限を与えることではない。

## 推奨制約

- max_depth: 2
- child は leaf-only
- child は evidence/report のみ作成
- child は canonical artifact を編集しない
- 1 parent pass あたりの parallel child calls: 3 まで
- 1 artifact あたりの child calls: 6 まで
- preflight review loop: 2 回まで
- deep-consultant call: 1 artifact あたり 1 回を原則
- parent draft iteration: 3 回まで

## spec-reviewer の扱い

parent authoring agent が呼ぶ spec-reviewer は advisory preflight とする。final review と promotion gate は main orchestrator 側の spec-reviewer が担う。

## 判断

depth=2 は採用すべきだが、子 agent は evidence producer に限定する。draft author は親 authoring agent、final owner は main orchestrator、という責任分界を崩さないことが条件。
