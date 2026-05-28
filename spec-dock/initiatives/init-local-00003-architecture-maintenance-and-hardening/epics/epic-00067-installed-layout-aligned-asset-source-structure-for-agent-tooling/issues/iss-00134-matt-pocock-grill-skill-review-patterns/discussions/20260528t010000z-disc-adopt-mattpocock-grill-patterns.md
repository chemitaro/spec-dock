---
種別: disc
ID: "disc-20260528t010000z"
タイトル: "Adopt Matt Pocock grill patterns in spec-dock"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t004419z", "research-20260528t005900z"]
authority: "proposed"
derived_from:
  - "discussions/20260528t005900z-research-chatgpt-mattpocock-integration-patterns.md"
  - "discussions/20260528t005600z-scratch-chatgpt-initial-analysis-response.md"
reflected_to:
  - "requirement.md"
---

# disc-20260528t010000z Adopt Matt Pocock grill patterns in spec-dock

## 位置づけ
- 用途: Matt Pocock `grill-me` / `grill-with-docs` pattern を spec-dock に取り込む場合の選択肢、推奨案、未決事項を整理する。
- authority: proposed。まだ `requirement.md` / `design.md` / `plan.md` には反映していない。

## 議題
- spec-dock の要件定義壁打ち workflow として、Matt Pocock skills のどの pattern を採用・変形すべきか。
- それを skill、phase、discussion template、agent role のどの surface に置くべきか。

## 背景
- `iss-00134` の issue docs は現時点で scaffold に近く、要件定義・設計・計画を具体化する必要がある。
- Matt Pocock skills の source capture は `discussions/mattpocock-skills-source/` に取り込み済み。
- ChatGPT 初回分析では、`grill-with-docs` を基礎にした spec-dock-native docs-aware clarification workflow が推奨された。
- active epic の provider authority は `src/spec_dock/assets/install_root/` であり、shipped skill を追加する場合は provider-side source を先に編集する必要がある。

## 選択肢
- Option A: `grill-me` を直接 import する
  - Pros:
    - 小さく単純。
    - one-question-at-a-time interview の核を取り込みやすい。
  - Cons:
    - spec-dock の active docs / discussions / ADR workflow と自然に接続しない。
    - chat-only の壁打ちに寄り、artifact-driven workflow になりにくい。
  - Assessment:
    - primary approach としては不採用。

- Option B: `grill-with-docs` を直接 import する
  - Pros:
    - docs-aware であり、domain language / ADR sparse usage / code cross-reference の発想が spec-dock と近い。
  - Cons:
    - root `CONTEXT.md` 前提が強い。
    - inline docs update は spec-dock の authority / lifecycle approval と衝突しうる。
    - research/disc/interview/adr の artifact taxonomy にそのまま対応しない。
  - Assessment:
    - 直接 import ではなく、spec-dock-specific transformation が必要。

- Option C: `spec-dock-requirement-grill` を新設する
  - Pros:
    - Matt Pocock の essence を保ちながら、spec-dock の active issue docs と discussion artifacts に合わせられる。
    - provider-side `install_root` に shared skill として置ける。
    - global `CONTEXT.md` authority を増やさずに済む。
  - Cons:
    - skill design、stop conditions、output artifacts、template 追加の設計が必要。
    - 既存 `consultant` / `deep-consultant` / `spec-manager` との責務重複を整理する必要がある。
  - Assessment:
    - 推奨。

## 推奨案
- `grill-with-docs` を primary inspiration として、spec-dock-native skill `spec-dock-requirement-grill` を設計する。
- `grill-me` は次の sub-pattern として取り込む。
  - one-question-at-a-time interview
  - decision tree traversal
  - shared-understanding stop condition
  - repo/docs で答えられることを人に聞かない
- root `CONTEXT.md` を新しい正本にせず、context source set は次を優先する。
  - active issue docs
  - parent epic / initiative docs
  - issue-local discussions
  - `.agent` generated state
  - relevant source / tests
- 初期実装は shared skill 先行とし、new Codex agent は後続判断にする。

## 未決事項
- `issue clarify` を CLI command にするか、skill / prompt workflow に留めるか。
- `requirement-grill-facilitator` agent を追加するか、既存 agent に skill を読ませるか。
- grill workflow 用 discussion templates を新設するか、既存 `interview` / `disc` / `research` templates の guidance 追加で足りるか。
- issue-local term を parent-level vocabulary に昇格する条件をどう定義するか。
- Matt Pocock skills の exact text reuse に関する license / attribution 方針。

## 次アクション
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `spec-dock-requirement-grill` を候補 skill として requirement/design に入れる。
  - `grill-with-docs` の直接移植ではなく spec-dock-specific transformation を採用方針にする。
  - `CONTEXT.md` ではなく active docs + discussions を context source set にする制約を固定する。
- 追加で作る discussion docs:
  - `spec-dock-requirement-grill` の `SKILL.md` 詳細設計 research/disc。
  - `CONTEXT.md` semantics を spec-dock context source set へ写像する research。
  - `issue clarify` lifecycle phase の設計 discussion。
  - license / copy policy research。
