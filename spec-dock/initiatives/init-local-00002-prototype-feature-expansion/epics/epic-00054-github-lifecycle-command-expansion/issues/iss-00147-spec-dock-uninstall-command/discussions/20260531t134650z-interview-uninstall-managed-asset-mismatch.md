---
種別: interview
ID: "20260531t134650z-interview"
タイトル: "Uninstall managed asset mismatch"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["iss-00147"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00147"
created_at: "2026-05-31THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260531t134650z-interview Uninstall managed asset mismatch

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - uninstall が current managed files を削除する条件と manual review 条件が変わる。
  - `design.md`:
    - content comparison、manifest ownership、mismatch reporting、directory cleanup の設計が変わる。
  - `plan.md`:
    - tests / edge cases / dry-run expected output が変わる。
  - `ADR`:
    - 現時点では不要。
- chat 上の軽微な一問では足りない理由:
  - `.agents/skills/**` や `.codex/agents/**` は SpecDock 由来の開発用 noise だが、`.github/workflows/ci.yml` などは repo 側で編集・流用される可能性もあり、差分がある file を自動削除するかは data loss risk に関わるため。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner
- 何を明確にする質問か:
  - install_root の current managed files について、shipped asset と内容が違う場合も uninstall で削除するか、残して manual review に回すかを確定する。
- 回答が後続判断へ与える影響:
  - managed asset removal の安全性、noise removal の完全性、dry-run / report の分類、tests が変わる。

## 質問 (必須)
- 質問:
  - uninstall は、current managed asset として manifest / install_root に含まれる file でも、現在の shipped asset と内容が異なる場合は自動削除しますか？
- 回答してほしいこと:
  - Option A / B / C から選ぶか、別案があれば「差分あり managed file」の扱いを教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `src/spec_dock/assets/install_root/`: current managed assets として `.agents/skills/**`, `.codex/agents/**`, `.github/agents/**`, `.codex/prompts/**`, `.codex/rules/**`, `.github/workflows/ci.yml` が含まれる。
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`: bootstrap-only は `.codex/config.toml` のみで、obsolete exact paths も定義されている。
  - `src/spec_dock/cli.py`: update は current managed files を source asset から copy する。bootstrap-only は既存 file がある場合 skip する。
  - `20260531t134004z-interview-uninstall-user-owned-asset-boundary.md`: bootstrap-only / user-owned files は content match based removal として user-approved。
- local context で解決できたこと:
  - update semantics 上、current managed files は installer-owned として扱われる。
  - ただし uninstall は destructive removal であり、current managed files に user edits や product reuse がある場合の扱いは別途決める必要がある。
- まだ人間判断が必要な理由:
  - noise removal を優先して managed file を強く消すか、user edit protection を優先して mismatch を残すかは product policy である。

## 回答案 (必須)
- Option A:
  - manifest-owned removal: current managed file は内容差分があっても自動削除する。installer-owned なので uninstall は強く取り除く。
- Option B:
  - content-match removal: current managed file も shipped asset と完全一致する場合だけ削除し、差分がある場合は残して manual review に回す。
- Option C:
  - category-based removal: `.agents/skills/**`, `.codex/agents/**`, `.github/agents/**` のような agent/skill noise は差分があっても削除し、`.github/workflows/ci.yml` や config/rules/prompts は content mismatch の場合だけ残す。

## Codex の分析 (必須)
- 判断軸:
  - uninstall の目的達成度、user edit protection、implementation complexity、dry-run の説明しやすさ、再install後の復元性。
- tradeoff:
  - Option A は開発用 noise を最も確実に取り除くが、編集済み managed file を失う可能性がある。
  - Option B はもっとも安全だが、編集済み agent file が残って noise removal が不完全になる可能性がある。
  - Option C は目的に沿いやすいが、category rule が増え、将来 asset 追加時に分類が必要になる。
- リスク:
  - 差分あり agent file を残すと、uninstall 後も sub-agent / skill が discovery され続ける。
  - 差分あり CI / config / prompt file を消すと、product repo の運用設定を失う。
- 具体シナリオ / edge case:
  - product repo が `.github/workflows/ci.yml` を SpecDock 由来から編集して流用している。
  - `.codex/agents/spec-manager.toml` をユーザーが調整しているが、uninstall の目的上は残るとノイズになる。
  - `.agents/skills/spec-dock-issue-planning/SKILL.md` が編集されているが、product の runtime agent には不要。

## Codex の推奨案 (必須)
- 推奨:
  - Option C。
- 理由:
  - 今回の primary objective は agent / skill noise removal なので、agent and skill assets は強く削除する方が目的に合う。
  - 一方で CI / config / prompt / rule のように product repo へ流用されやすいものは、content mismatch を preserve した方が安全。
- 未回答時の影響:
  - requirement の削除条件と design の inventory classification を固定できず、plan に進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option C を採用する。
  - `.agents/skills/**`, `.codex/agents/**`, `.github/agents/**` のような agent / skill assets は、現在の shipped asset と内容が異なる場合でも uninstall で削除する。
  - CI / config / prompt / rule のように product repo へ流用されやすい files は、現在の shipped asset と内容が異なる場合は自動削除せず、manual review 対象として残す。
- 回答日時:
  - 2026-05-31

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - uninstall 実行後、削除された agent / skill / runtime files に由来する空 directory を自動削除するか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、current managed asset mismatch の扱いは category-based removal として確定した。
  - primary objective である agent / skill noise removal を優先し、agent / skill assets は content mismatch があっても削除する。
  - product repo へ流用されやすい CI / config / prompt / rule などは content mismatch 時に preserve し、user edit や product-specific adaptation の誤削除を避ける。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - agent / skill assets は uninstall の core removal target とし、content mismatch があっても削除対象にする。
  - CI / config / prompt / rule など product reuse 可能な assets は、content match する場合だけ自動削除し、mismatch は preserve + manual review にする。
  - dry-run / execution result は removed / preserved-manual-review / skipped を分類して表示する。
- `design.md`:
  - uninstall inventory は category-based に分類し、agent / skill paths と product-reusable paths を分ける。
  - content comparison は product-reusable paths と bootstrap-only paths の自動削除判定に使う。
  - mismatch preservation と manual review reporting を設計対象にする。
- `plan.md`:
  - content mismatch agent / skill removal、content mismatch CI/config/prompt/rule preservation、dry-run reporting を test obligation に含める。
- `ADR`:
  - 現時点では不要。
- reflected_to 更新方針:
  - requirement authoring 時に `requirement.md` と `report.md` の Evidence Adoption Ledger / Spec Authoring Gate へ反映する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
