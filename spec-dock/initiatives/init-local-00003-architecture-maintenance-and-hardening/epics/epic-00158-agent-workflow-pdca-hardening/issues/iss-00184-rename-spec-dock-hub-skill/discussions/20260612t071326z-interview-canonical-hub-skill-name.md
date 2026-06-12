---
種別: interview
ID: "20260612t071326z-interview"
タイトル: "Canonical Hub Skill Name"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["iss-00184"]
関連: []
scope: "issue"
scope_id: "iss-00184"
created_at: "2026-06-12T07:13:26Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: ["20260612t070646z-interview"]
reflected_to: ["requirement.md", "report.md"]
---

# 20260612t071326z-interview Canonical Hub Skill Name

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - canonical name と受け入れ条件の表現が確定する。
  - `design.md`:
    - rename 対象 path、metadata、tests、docs references が確定する。
  - `plan.md`:
    - concrete step / negative inspection / test commands に新旧名を固定できる。
  - `ADR`:
    - 通常は不要。今後 skill naming policy を一般化する場合のみ ADR candidate。
- chat 上の軽微な一問では足りない理由:
  - ユーザーは互換性なしの full migration を明示したため、新 canonical name はすべての現行 surface を置換する durable name になる。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / user.
- 何を明確にする質問か:
  - Full migration 先の canonical skill name。
- 回答が後続判断へ与える影響:
  - directory name、frontmatter `name`、docs references、tests、negative inspection の expected value が決まる。

## 質問 (必須)
- pressure-test question:
  - 名前は短さと明確さを優先するか、workflow / governance の意味も名前に含めるか。
- 質問:
  - 新しい canonical skill name は `spec-dock-hub` で進めてよいですか。
- 回答してほしいこと:
  - yes / no。
  - no の場合は、代替名を一つ指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/issue/requirement.md`
  - `discussions/20260612t070646z-interview-hub-skill-naming-compatibility-direction.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/cli.py`
  - `README.md`
  - `spec-dock/docs/README.md`
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
- local context で解決できたこと:
  - Full migration / no compatibility alias 方針はユーザー回答で確定済み。
  - 現行 hub skill は route selector + global invariant surface。
  - Leaf skill family は `spec-dock-issue-planning`, `spec-dock-issue-execution`, `spec-dock-clarification` など `spec-dock-*` の明示的な名前を使っている。
- まだ人間判断が必要な理由:
  - `spec-dock-hub`、`spec-dock-workflow-hub`、`spec-dock-governance-hub` はいずれも成立するが、どのニュアンスを製品名として採用するかは user-facing naming judgment。

## 回答案 (必須)
- Option A:
  - `spec-dock-hub`: 短く、hub であることが最も明確。leaf skill family と並べたときに入口として見つけやすい。
- Option B:
  - `spec-dock-workflow-hub`: workflow routing の意味を含むが、やや長く、旧 `workflow` 色が残る。
- Option C:
  - `spec-dock-governance-hub`: global invariant / governance を強く出せるが、日常利用には硬く、route selector としての軽さが落ちる。

## Codex の分析 (必須)
- 判断軸:
  - discoverability, brevity, role clarity, consistency with leaf skill names, future-proofing.
- tradeoff:
  - `spec-dock-hub` は最短で直感的だが、governance の意味は description で補う必要がある。
  - `spec-dock-workflow-hub` は workflow を含むが、今回避けたい「TDD/workflow 手法だけの印象」を少し残す。
  - `spec-dock-governance-hub` は統括ルール感が強いが、leaf routing entrypoint としては重い。
- リスク:
  - 名前が長いほど、skill discovery で認識しづらく、参照も冗長になる。
  - 名前が抽象的すぎると、leaf skill への routing hub であることが伝わらない。
- 具体シナリオ / edge case:
  - Agent が skills list だけを見る場合、`spec-dock-hub` は入口として最も見つけやすい。
  - Skill 本文の description で "route selector and global invariant surface" と補えば、governance の意味は保持できる。

## Codex の推奨案 (必須)
- 推奨:
  - `spec-dock-hub`
- 理由:
  - ユーザーの「SpecDock の hub であることが分かるようにしたい」という原要求に最も素直で、leaf skill family とも自然に並ぶ。統括ルール / route selector の意味は description と本文で明示するのがよい。
- 未回答時の影響:
  - design / plan で rename target と test expected value を固定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ユーザーは `spec-dock-hub` を採用すると回答した。
- 回答:
  - `spec-dock-hub` を採用する。シンプルでわかりやすく、良い。
- 回答日時:
  - 2026-06-12

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Full migration 先の canonical skill name を決める user-facing naming judgment であり、ユーザー回答が issue scope と acceptance criteria を確定するため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - canonical name を `spec-dock-hub` として固定し、未確定事項から除く。
- `design.md`:
  - provider / mirror skill directory、frontmatter `name`、README/docs/tests references を `spec-dock-hub` へ移す設計にする。
- `plan.md`:
  - `spec-dock-hub` の positive inspection と旧 `spec-driven-tdd-workflow` の現行 surface negative inspection を固定する。
- `ADR`:
  - なし。Issue-local naming decision として扱う。
- reflected_to 更新方針:
  - `requirement.md` と `report.md` にまず反映し、design / plan authoring 時に詳細化する。
- adoption reflection:
  - `report.md` の Decision Ledger / Evidence Adoption Ledger / Spec Authoring Gate に `spec-dock-hub` 採用を記録する。

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
