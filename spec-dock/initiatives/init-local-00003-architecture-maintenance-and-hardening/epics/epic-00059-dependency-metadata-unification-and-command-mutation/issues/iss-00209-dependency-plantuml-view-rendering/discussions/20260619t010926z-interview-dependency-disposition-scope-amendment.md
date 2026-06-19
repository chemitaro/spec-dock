---
種別: interview
ID: "20260619t010926z-interview"
タイトル: "Dependency disposition scope amendment"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00209"]
関連: []
scope: "issue"
scope_id: "iss-00209"
created_at: "2026-06-19T01:09:26Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260619t002902z-research"
  - "20260619t002903z-interview"
reflected_to: []
---

# 20260619t010926z-interview Dependency disposition scope amendment

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
    - `iss-00209` のスコープを rendering-only から readiness logic + rendering に広げるか。
  - `design.md`:
    - `dependency_disposition` を readiness authority に導入するか、表示だけで扱うか。
  - `plan.md`:
    - 実装 step、test obligation、review gate、manual test の範囲。
  - `ADR`:
    - 現時点では不要の見込み。scope split が cross-issue policy になる場合だけ候補。
- chat 上の軽微な一問では足りない理由:
  - 回答によって issue の主目的、対象 layer、受け入れ条件、テスト範囲が変わるため。

## 質問の目的 (必須)
- 対象者:
  - Product owner / workflow owner.
- 何を明確にする質問か:
  - `iss-00209` で readiness authority / blocker 判定の設計変更まで扱うか、別 issue に分けるか。
- 回答が後続判断へ与える影響:
  - Requirement / design / plan のスコープ、依存関係、作業順、テスト範囲を確定する。

## 質問 (必須)
- pressure-test question:
  - 表示と blocker 判定を分けると再びズレるリスクがありますが、`iss-00209` の範囲を広げて一体で直しますか。
- 質問:
  - `iss-00209` は `dependency_disposition` を readiness authority に導入し、`deps check` / `active set` / `issue start` / `deps-issues.json` / PlantUML 表示まで一体で扱う issue にスコープ修正してよいですか。
- 回答してほしいこと:
  - Option A/B/C のどれを採用するか、または別案。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md`
- local context で解決できたこと:
  - GitHub lifecycle state と dependency readiness interpretation は分離する必要がある。
  - GitHub open でも all descendant issues done の high-level dependency は blocker ではなく satisfied と扱うべき。
  - Empty open high-level dependency は引き続き blocker と扱うべき。
  - 現行 `requirement.md` の初期スコープには「依存関係ロジックの再修正は対象外」とあるため、scope amendment が必要。
- まだ人間判断が必要な理由:
  - これは issue scope / work breakdown の判断であり、コードからは決められない。

## 回答案 (必須)
- Option A:
  - Scope amendment: `iss-00209` を readiness authority + rendering 一体の修正 issue に広げる。
- Option B:
  - Split: 先に `dependency_disposition` / blocker 判定用の別 issue を作り、`iss-00209` はその後の rendering issue として依存させる。
- Option C:
  - Rendering-only: `iss-00209` は表示だけを修正し、readiness authority 変更は deferred とする。

## Codex の分析 (必須)
- 判断軸:
  - 一貫性、差分サイズ、reviewability、再発リスク、issue scope の明確さ。
- tradeoff:
  - Option A は一貫性が高いが、issue scope が初期想定より広がる。
  - Option B は reviewable だが、実装順と依存 issue 管理が増える。
  - Option C は小さいが、PUML と readiness 判定がズレるリスクが高い。
- リスク:
  - Option A/B では docs と tests の更新範囲が広がる。
  - Option C では `deps check` では blocked なのに PlantUML では消える、またはその逆の矛盾が起きうる。
- 具体シナリオ / edge case:
  - GitHub open all-done epic dependency: `deps check` は ready、PUML では active blocker として出さない。
  - Empty GitHub open epic dependency: `deps check` は blocked、PUML では blocker として出す。
  - Unknown high-level state: fail-closed / indeterminate として扱う。

## Codex の推奨案 (必須)
- 推奨:
  - Option A.
- 理由:
  - 表示と blocker 判定は同じ `dependency_disposition` を消費すべきで、別 issue に分けると中間状態で矛盾しやすい。`iss-00209` はすでにこの問題の議論と evidence を持っているため、scope amendment で一体化する方が自然。
- 未回答時の影響:
  - Requirement を確定できず、design / plan authoring に進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User selected Option A and explicitly confirmed that this is not only visual rendering but must change blocker/readiness logic.
- 回答:
  - Adopt Option A. Amend `iss-00209` scope to include readiness authority / blocker logic and PlantUML rendering as one coherent change.
- 回答日時:
  - 2026-06-19

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
  - Scope decision is required to avoid mismatch between `deps check` / `active set` / `issue start` readiness behavior and PlantUML rendering.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Remove rendering-only scope boundary and define `dependency_disposition` as readiness authority scope.
- `design.md`:
  - Design lifecycle state and dependency disposition as separate concepts consumed by readiness and rendering.
- `plan.md`:
  - Plan domain, application, presentation, docs, and manual verification steps.
- `ADR`:
  - Not required unless the design review finds this should become a cross-workflow lifecycle policy.
- reflected_to 更新方針:
  - Reflect during canonical issue planning.
- adoption reflection:
  - Pending canonical artifact updates.

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
