---
種別: interview
ID: "20260619t063309z-interview"
タイトル: "Issue 211 Scope Pressure Test"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00211"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00211"
created_at: "2026-06-19T06:33:09Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: ["20260619t063017z-research", "20260619t063303z-disc"]
reflected_to: []
---

# 20260619t063309z-interview Issue 211 Scope Pressure Test

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
    - Issue 211 の scope / non-scope / acceptance criteria を、skill-only か docs reference 追加込みかで変える。
  - `design.md`:
    - 変更対象を `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` だけにするか、`workflow_epic.md` も含めるかで structure / flow / test strategy が変わる。
  - `plan.md`:
    - 実装 step、review step、verification command、snapshot / dogfooding check の範囲が変わる。
  - `ADR`:
    - 現時点では不要。回答が広範な workflow architecture change を要求する場合のみ再検討する。
- chat 上の軽微な一問では足りない理由:
  - この判断は変更ファイル、acceptance criteria、テスト obligation、Issue 210 の handoff consumption を変えるため、回答前の source-grounded 記録と回答後の採用証跡が必要。

## 質問の目的 (必須)
- 対象者:
  - Issue owner / product owner。
- 何を明確にする質問か:
  - Issue 211 の成果物を、新 `spec-dock-epic-execution` skill の追加に閉じるか、Epic workflow reference の最小追加まで含めるか。
- 回答が後続判断へ与える影響:
  - requirement / design / plan の scope と acceptance criteria、実装委任範囲、spec-review の観点、検証コマンドが確定する。

## 質問 (必須)
- pressure-test question:
  - Issue 211 の実装範囲は、skill-only 最小追加に寄せますか。それとも `workflow_epic.md` の Epic execution reference 追加まで含めますか。
- 質問:
  - Issue 211 はどちらのスコープで要件定義しますか。
- 回答してほしいこと:
  - Option A / Option B / Option C のいずれか、または調整案。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue #211
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `20260619t063017z-research-issue-211-clarification-source-review.md`
  - `20260619t063303z-disc-issue-211-clarification-synthesis.md`
- local context で解決できたこと:
  - `spec-dock-epic-execution` は既存 skill を置き換えない coordinator とする。
  - PR merge はしない。merge-ready preparation は `github-pr-merge-preparer` へ委譲する。
  - Runtime CLI command 追加は必須ではない。
  - Provider-side installed skill source は `src/spec_dock/assets/install_root/.agents/skills/`。
- まだ人間判断が必要な理由:
  - GitHub #211 は docs 更新を「必要なら」としており、skill-only で十分か、Epic workflow reference まで固定すべきかは owner-intent / scope tradeoff で決める必要がある。

## 回答案 (必須)
- Option A:
  - Skill-only 最小追加。新 `spec-dock-epic-execution` skill、dogfooding mirror、必要な provider tests / snapshots を中心にする。
- Option B:
  - Skill + `workflow_epic.md` 最小 reference。新 skill に加えて、Epic planning handoff 後の Epic execution lifecycle / completion gate / PR merge-preparer handoff を `workflow_epic.md` に短く追加する。他 docs は明確な欠落がある場合だけ最小更新。
- Option C:
  - Broad docs update。GitHub #211 に列挙された `workflow_issue.md` / `workflow_spec_authoring.md` / `decision-routing.md` / `reference_github.md` まで横断更新する。

## Codex の分析 (必須)
- 判断軸:
  - First-read skill の実用性。
  - Repo docs を source of truth とする一貫性。
  - Issue 210 handoff との接続。
  - 変更範囲と test obligation の増加。
- tradeoff:
  - Option A は小さいが workflow reference との接続が弱い。
  - Option B は Issue 210 から Issue 211 への自然な接続を作りつつ、docs 横断更新を抑えられる。
  - Option C は包括的だが、Issue 211 が workflow docs cleanup に膨らむ。
- リスク:
  - Skill に lifecycle semantics を詰め込みすぎると docs と drift する。
  - Docs 更新を広げすぎると主目的である coordinator skill 追加がぼやける。
  - Skill-only にしすぎると Epic planning handoff 後の実行基準が repo docs に残らない。
- 具体シナリオ / edge case:
  - Active issue が残っている Epic を実行しようとする場合。
  - 複数 ready issue がある場合。
  - 全 Issue 完了後に Epic-level review が fail する場合。
  - PR observation / checks / review threads が fail または timeout する場合。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - Issue 210 が Epic planning completion / handoff を定義し、execution coordinator は later Issue として残したため、Issue 211 では skill と `workflow_epic.md` reference の両方で最小限接続するのが最も整合的。
  - Existing skills の詳細責務は置き換えず、Epic-level orchestration semantics だけを `workflow_epic.md` に置ける。
  - Option C より scope を抑えられる。
- 未回答時の影響:
  - requirement / design / plan に入れる docs update 範囲を確定できないため、canonical docs authoring に進むと過不足が出る。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ユーザーは Option B を採用すると回答した。
- 回答:
  - Option B: 新 `spec-dock-epic-execution` skill に加えて、`workflow_epic.md` に Epic execution lifecycle / completion gate / PR merge-preparer handoff の短い reference section も追加する。他 docs は明確な欠落がある場合だけ最小更新する。
- 回答日時:
  - 2026-06-19T06:37:57Z

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Option B は Issue 210 の Epic planning handoff と Issue 211 の Epic execution coordinator を最小 docs surface で接続し、かつ broad docs cleanup へ膨らむことを避けるため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Scope に new `spec-dock-epic-execution` skill と `workflow_epic.md` minimal reference update を含める。
  - Non-scope に runtime CLI command 追加、Issue planning / Issue execution / PR merge-preparer の置換、PR merge、広範な docs cleanup を置く。
- `design.md`:
  - Provider-side skill path、dogfooding mirror、`workflow_epic.md` reference section、existing skill handoff、test strategy を設計対象に含める。
- `plan.md`:
  - Skill authoring、workflow_epic minimal reference、mirror / scaffold tests、spec-review / verification を step 化する。
- `ADR`:
  - 不要。既存 workflow family への leaf coordinator skill 追加として扱う。
- reflected_to 更新方針:
  - 回答採用後に canonical docs と `report.md` Evidence Adoption Ledger を更新する。
- adoption reflection:
  - Requirement / design / plan authoring 時に Option B を前提として反映する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  - Not needed for this pressure-test question.
- 詳細 tradeoff:
  - See `20260619t063303z-disc-issue-211-clarification-synthesis.md`.
- 後続 reflection proposal:
  - Option B を canonical docs と `report.md` Evidence Adoption Ledger に反映する。
- 追加で作る discussion docs:
  - None planned unless the answer exposes a new high-impact ambiguity.
