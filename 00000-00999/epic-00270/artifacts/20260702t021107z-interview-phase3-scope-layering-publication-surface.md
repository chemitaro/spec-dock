---
種別: interview
ID: "20260702t021107z-interview"
タイトル: "Phase 3 Scope Layering Publication Surface"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t020503z-01-disc"
  - "20260702t020436z-01-disc"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T02:11:07Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t020503z-01-disc-phase3-scope-authority-model.md"
  - "artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md"
reflected_to:
  - "artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md"
---

# 20260702t021107z-interview Phase 3 Scope Layering Publication Surface

## 正式質問として扱う理由

- 影響する artifact:
  - `design.md`:
    - Initiative / Epic / Issue / Issue Plan / Report の責務境界をどこまで設計判断として持つかに影響する。
  - `plan.md`:
    - どの Issue が docs/templates/skills/tests を更新するかに影響する。
  - `ADR`:
    - scope-layering model をこの Epic 外でも使う durable rule にするなら ADR 候補になる。
- chat 上の軽微な一問では足りない理由:
  - V3 は「scope-layering は別IssueではなくEpic design/planで扱う」とするが、実装後にユーザーやエージェントがどこを正本として参照するかは未確定。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - scope-layering / work hierarchy responsibility model を、どの公開面で維持するか。
- 回答が後続判断へ与える影響:
  - 新規 reference doc を追加するか、workflow docs と templates に分散して埋め込むか、ADR化するかが変わる。

## 質問

- pressure-test question:
  - downstream coding agents が「これは Initiative / Epic / Issue / Plan / Report のどこに書くべきか」で迷ったとき、最初に見る正本はどこにあるべきですか。
- 質問:
  - scope-layering / Initiative-Epic-Issue責務モデルは、どの surface として公開・維持するのがよいですか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 `epic-level-planning-analysis.md` と `upstream-abstraction-model.md` は、scope-layering model を Epic design/plan の前提として提示している。
  - V3 `suggested-file-map.md` には `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md  # if added` が候補として出ている。
  - 既存 `workflow_initiative.md` / `workflow_epic.md` / `phase_plan_epic.md` は責務境界を一部持つが、一覧性のある scope-layering reference ではない。
  - `decision-routing.md` は判断の行き先を扱うが、scope別artifact責務の全体表そのものではない。
- local context で解決できたこと:
  - scope-layering を decision-only Issue として作るのは避ける。
  - canonical Epic design/plan には少なくとも採用判断を入れる必要がある。
  - 長期的に再利用するなら provider-side docs へ入れる方が後続エージェントに優しい。
- まだ人間判断が必要な理由:
  - 新しい docs reference を増やすか、既存 workflow docs への分散更新に留めるかは、運用上の好みと保守コストの判断を含む。

## 回答案

- Option A:
  - 新しい provider docs reference、例: `docs/authoring/scope-layering.md` を追加し、workflow/template/skills から参照する。Canonical Epic design/plan はその採用判断と要約を持つ。
- Option B:
  - 新しい reference doc は作らず、`workflow_initiative.md` / `workflow_epic.md` / `workflow_issue.md` / phase docs / templates に必要箇所だけ分散して埋め込む。
- Option C:
  - ADRとして固定し、docs/templates/skills はADR参照にする。長期ルールとして強く扱う。

## Codex の分析

- 判断軸:
  - 後続エージェントの見つけやすさ。
  - docsの重複と保守コスト。
  - ルールの強さ。
  - このEpic内だけの設計判断か、今後のSpecDock全体の規約か。
- tradeoff:
  - Option A は見つけやすく、V3の `scope-layering.md if added` とも一致する。docsが1つ増えるが、参照先を集約できる。
  - Option B はファイル追加が少ないが、責務モデルが分散して後続エージェントが迷いやすい。
  - Option C は強いが、ADRにするほど不可逆/驚きのある判断かはやや微妙。ADRだけだと日常のテンプレート利用者に届きにくい。
- リスク:
  - Option Aでreference docを作る場合、workflow docsと矛盾しないようテスト/grep smokeが必要。
  - Option Bは同じ表現を複数箇所に散らして drift しやすい。
  - Option CはADR乱立になる可能性がある。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - 今回のEpic目的は上流計画ガバナンスなので、scope-layering model は後続エージェントが直接参照できる docs reference にする価値が高い。
  - Canonical Epic docs には要約と採用判断だけ置き、詳細は reference doc に逃がせるため、前回採用した「中程度のcanonical detail」と整合する。
  - ADR化は、scope-layering docの中でさらに長期/高影響な判断が出た場合に限定できる。
- 未回答時の影響:
  - Issue 03 の docs/skills 更新範囲と Issue 05 の smoke test 観点が固定できない。

## ユーザー回答

- answer capture:
  - Human decision: adopt the fresh deep-consultant recommendation as an ADR.
  - Adopt constrained Option A: create one provider-side `docs/authoring/scope-layering.md` reference as the reusable rule; keep existing workflow/docs/skills/templates thin and link to it; do not use ADR as day-to-day publication surface.
- 回答:
  - `scope-layering / Initiative-Epic-Issue責務モデル` は1つのprovider-side referenceとして公開・維持し、この採用判断をADRとして固定する。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Spec-reviewer / smoke test が scope-layering violation をどの程度 fail するべきか。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `design.md` / `plan.md` / possible `docs/authoring/scope-layering.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Fresh deep-consultant recommendation was accepted by the user and captured as an accepted ADR.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Scope/non-goal には軽く影響。
- `design.md`:
  - Scope authority model の公開面として `docs/authoring/scope-layering.md` を採用することを明記する。
- `plan.md`:
  - Issue 03/05 のdocs/test範囲に `scope-layering.md` 作成、薄いリンク、smoke checks を含める。
- `ADR`:
  - `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md` として採用済み。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - Accepted ADRへ反映済み。Canonical docs/report ledgerへの反映は次工程。
