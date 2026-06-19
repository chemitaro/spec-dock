---
種別: interview
ID: "20260619t002903z-interview"
タイトル: "Dependency PlantUML closed node policy"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00209"]
関連: []
scope: "issue"
scope_id: "iss-00209"
created_at: "2026-06-19T00:29:03Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260619t002903z-interview Dependency PlantUML closed node policy

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
    - `deps-issues.puml` / `deps-raw.puml` の表示対象と非表示対象。
  - `design.md`:
    - high-level node visual state、filtering predicate、edge filtering、JSON と PUML の責務境界。
  - `plan.md`:
    - presentation tests、sync integration tests、manual fixture update の期待値。
  - `ADR`:
    - 現時点では不要の見込み。ただし high-level lifecycle policy へ広がる場合は ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - 回答によって表示から消える node / edge が変わり、agent-facing JSON contract と human-facing PUML contract の境界にも影響するため。

## 質問の目的 (必須)
- 対象者:
  - Product owner / workflow owner.
- 何を明確にする質問か:
  - GitHub 上は open のままだが、配下 issue が全て done または todo issue が 0 件になった epic / initiative を、dependency PlantUML で表示し続けるべきか。
- 回答が後続判断へ与える影響:
  - `deps-issues.puml` と `deps-raw.puml` の high-level filtering policy、manual test fixture、requirements / design / tests を確定する。

## 質問 (必須)
- pressure-test question:
  - GitHub open の epic / initiative が「まだ課題として残っている」一方で、配下に表示すべき open issue がない場合、その high-level node は dependency PlantUML に残すべきですか。
- 質問:
  - `deps-issues.puml` / `deps-raw.puml` の表示対象から、GitHub status が closed の node だけでなく、「open だが配下 todo issue が 0 件の epic / initiative」も非表示にしますか。
- 回答してほしいこと:
  - Option A/B/C のどれを採用するか、または別案。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - `tests/cli_runtime/test_sync.py`
  - `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md`
- local context で解決できたこと:
  - closed issue / closed epic / closed initiative は原則 PUML 表示から外したい。
  - `deps-issues.puml` では `raw_direct` を前面に出さず、blocking は `blocks` として見せたい。
  - `deps-raw.puml` は metadata raw edge view なので、edge label は `raw_direct` でよい。
  - `deps-raw.puml` の epic / initiative は package 表現に統一する。
- まだ人間判断が必要な理由:
  - GitHub open high-level node を表示するかどうかは、コード上の事実ではなく、workflow と可視化 UX の意思決定だから。

## 回答案 (必須)
- Option A:
  - Strict leaf-actionable projection: closed node と、open だが配下 todo issue が 0 件の epic / initiative を非表示にする。empty open epic は「issue breakdown 前の active high-level blocker」として表示する。
- Option B:
  - GitHub status projection: GitHub open の epic / initiative は、配下 todo issue が 0 件でも表示する。closed node だけ非表示にする。
- Option C:
  - Hybrid with explicit stale/open parent marker: GitHub open だが配下 todo issue が 0 件の epic / initiative は通常非表示。ただし dependency edge の endpoint になっていて説明が必要な場合だけ、軽量 marker として表示する。

## Codex の分析 (必須)
- 判断軸:
  - 読みやすさ、workflow truthfulness、epic close 運用への圧、dependency explanation、JSON / PUML contract の分離。
- tradeoff:
  - Option A は図が最も読みやすいが、GitHub open parent が図から消える。
  - Option B は GitHub state に忠実だが、ユーザーが避けたい「epic が残り続ける」ノイズが残る。
  - Option C は説明力と読みやすさの折衷だが、例外表示ルールが増える。
- リスク:
  - Option A/C では、GitHub 上の open high-level work が PlantUML だけでは見えなくなる可能性がある。
  - Option B では、done issue を消しても empty / all-done epic package が残り続け、今回の UX 改善目的を弱める。
- 具体シナリオ / edge case:
  - Empty open epic: newly created / not yet broken down。表示する。
  - Open epic with all descendant issues done: GitHub close 未処理か、まだ親レベル課題が残っている状態。表示するかがこの質問の核心。
  - Closed epic with all done children: 非表示。
  - Open mixed epic: package は表示し、done issue は非表示、open/ready/blocked issue だけ表示。

## Codex の推奨案 (必須)
- 推奨:
  - Option A を推奨。
- 理由:
  - 今回の主目的は dependency PlantUML を「今動けるもの / ブロックされているもの」中心にすることなので、leaf actionable な todo がない high-level node は表示ノイズになりやすい。GitHub open parent の監査は dashboard / index-all / GitHub 側で確認できるため、dependency PUML に残す必然性は低い。
- 未回答時の影響:
  - high-level filtering predicate が決まらず、requirement / design / tests の確定に進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User accepted the distinction between GitHub lifecycle and dependency view lifecycle, and clarified that this policy also affects blocker logic, not only rendering.
- 回答:
  - Adopt Option A for dependency PlantUML visibility: closed nodes and GitHub-open high-level nodes with all descendant issues done should not remain visible as active dependency items. Empty GitHub-open epic / initiative remains active because it represents pre-breakdown high-level work.
- 回答日時:
  - 2026-06-19

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Whether `iss-00209` should amend its scope to include readiness authority / blocker logic changes, or whether that logic should be split into a prerequisite follow-up issue.

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - User confirmed the core visibility policy and expanded it to blocker logic. The answer is required to define the issue requirements and design.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Add accepted lifecycle / visibility distinction and high-level dependency cases.
- `design.md`:
  - Define `lifecycle_state` versus `dependency_disposition` and how PUML filtering consumes readiness authority.
- `plan.md`:
  - Add tests for empty open high-level nodes, all-descendant-done high-level nodes, and rendering behavior.
- `ADR`:
  - Not required yet; issue-local and reversible unless this becomes a cross-workflow lifecycle policy.
- reflected_to 更新方針:
  - Update after the remaining scope question is answered.
- adoption reflection:
  - Pending canonical authoring.

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
