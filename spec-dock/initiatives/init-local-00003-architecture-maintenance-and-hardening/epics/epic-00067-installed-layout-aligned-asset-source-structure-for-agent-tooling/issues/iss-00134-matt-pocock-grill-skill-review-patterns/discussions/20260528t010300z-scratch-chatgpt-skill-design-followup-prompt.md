---
種別: scratch
ID: "scratch-20260528t010300z"
タイトル: "ChatGPT follow-up prompt for spec-dock-requirement-grill skill design"
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t005900z", "disc-20260528t010000z"]
authority: "raw"
derived_from:
  - "discussions/20260528t005900z-research-chatgpt-mattpocock-integration-patterns.md"
  - "discussions/20260528t010000z-disc-adopt-mattpocock-grill-patterns.md"
reflected_to: []
---

# scratch-20260528t010300z ChatGPT follow-up prompt for spec-dock-requirement-grill skill design

## メモ

前回の分析ありがとう。次の P0 follow-up として、抽象論ではなく、実際に spec-dock に入れる `spec-dock-requirement-grill` skill の設計に進んでください。

# 現時点の採用方針
- `grill-me` の単純移植ではなく、`grill-with-docs` を spec-dock-native に変形する。
- skill 名は暫定 `spec-dock-requirement-grill`。
- root `CONTEXT.md` を新しい正本にしない。
- context source set は active issue docs、parent epic/initiative docs、issue-local discussions、`.agent` generated state、relevant source/tests。
- workflow は chat-only にせず、research / interview / disc / ADR candidate / requirement-design-plan patch proposal へ落とす。
- provider-side source path は `src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md`。

# 今回あなたに設計してほしいもの
1. `spec-dock-requirement-grill/SKILL.md` の実際のドラフト。
2. skill が読むべき input sources の優先順位。
3. skill が作成・更新してよい output artifacts。
4. one-question-at-a-time interview の運用ルール。
5. repo/docs で答えられることを人に聞かないための local inspection rule。
6. unresolved ambiguity を requirement/design/plan に混ぜないための guardrails。
7. ADR triage への接続条件。
8. stop conditions と completion criteria。
9. 既存 `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-execution` / `spec-dock-adr-facilitation` との責務境界。
10. shipped asset として入れる場合の最初の implementation slice。

# 制約
- Markdown は spec-dock の skill としてそのまま使える粒度で書いてください。
- ただし Matt Pocock skills の原文を逐語コピーしないでください。現時点では license / exact copy policy が未確認なので、essence を spec-dock の言葉で設計してください。
- `CONTEXT.md` mandatory にしないでください。
- human に質問する場合は一度に 1 問だけ。
- source で確認できる事実は先に確認する contract にしてください。
- discussion artifact は source of truth ではなく、adoption / reflection を経て requirement/design/plan/ADR に反映される、という関係を守ってください。

# 望ましい出力形式
- Proposed `SKILL.md` draft
- Design notes
- Responsibility boundaries
- Artifact contract
- First implementation slice
- Risks / unresolved questions
- Next follow-up prompt
