---
種別: interview
ID: "20260617t000333z-interview"
タイトル: "Scope Boundary For Timestamp Collision Prevention"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00188"
created_at: "2026-06-17T00:03:33Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260617t000227z-research"
reflected_to: []
---

# 20260617t000333z-interview Scope Boundary For Timestamp Collision Prevention

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
    - #188 の scope / non-scope、受け入れ条件、対象生成経路を決める。
  - `design.md`:
    - 既存 `new doc` allocator の追加 hardening だけで閉じるか、skill / workflow guidance まで command-first に寄せるかを決める。
  - `plan.md`:
    - テスト義務と変更対象ファイルが大きく変わる。PR repair batch + repair unit の再現 test を入れるかどうかに影響する。
  - `ADR`:
    - 既存 naming contract を変える判断ではないため、現時点では ADR 不要の見込み。
- chat 上の軽微な一問では足りない理由:
  - 回答が implementation scope、docs/skill asset impact、test obligation、report adoption evidence を変えるため。

## 質問の目的 (必須)
- 対象者:
  - maintainer / issue owner
- 何を明確にする質問か:
  - #188 が閉じるべき範囲を、runtime allocator に限定するか、agent-facing skill / workflow による manual timestamp reuse prevention まで含めるか。
- 回答が後続判断へ与える影響:
  - Option A なら runtime tests/docs の追加が中心になる。
  - Option B なら `github-pr-merge-preparer` などの skill asset と provider install_root / dogfooding mirror の更新も対象になる。
  - Option C なら broader artifact allocator API / command surface を設計する可能性がある。

## 質問 (必須)
- pressure-test question:
  - #188 の目的は「既存 `new doc` allocator が duplicate timestamp を作らないことをさらに固定する」ことですか、それとも「SpecDock が提供する skills / workflows が discussion artifact を複数作るときも、手作業の `<ts>` 再利用を禁止し、`spec-dock new doc` または shared allocator 経由に寄せる」ことまで含めますか。
- 質問:
  - この issue では、PR repair batch / repair unit などの agent-facing workflow guidance まで修正対象に含めますか。
- 回答してほしいこと:
  - A/B/C のどれに近いか。必要なら境界条件も指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue #188 body
  - `spec-dock/docs/reference_naming.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_validate.py`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `spec-dock/active/issue/discussions/20260617t000227z-research-timestamp-collision-source-grounding.md`
- local context で解決できたこと:
  - Validator の duplicate timestamp rejection は正しい既存 contract として維持する。
  - Runtime `new doc` は create lock、same-second suffix allocation、pre/post duplicate guard、parallel create test を既に持つ。
  - Failure example は runtime allocator 経由ではなく、同じ `<ts>` を複数 filename に再利用した manual / workflow generation 由来である可能性が高い。
- まだ人間判断が必要な理由:
  - #188 の GitHub body は "tooling, scripts, skills, or generated workflows" と広く書いているが、実装修正をどこまで一つの issue に含めるかは product/workflow scope 判断になる。

## 回答案 (必須)
- Option A:
  - Runtime-only hardening。既存 `new doc` allocator / duplicate guard / validation の regression coverage を補強し、docs に「生成は `new doc` 経由」と明記する。PR repair skill の具体修正は follow-up。
- Option B:
  - Recommended scope。Runtime regression に加えて、SpecDock-shipped skills / workflow guidance が manual `<ts>` reuse を促さないようにし、少なくとも `github-pr-merge-preparer` の PR repair batch / repair unit guidance を command-first または per-artifact allocator-first に更新する。
- Option C:
  - Broader product change。複数 discussion artifact を一括生成する public command / allocator API を設計し、skills はそれを呼ぶ。大きくなりやすく、#188 単独では過剰な可能性がある。

## Codex の分析 (必須)
- 判断軸:
  - 再現 failure を実際に防ぐか。
  - 既存 naming contract を変えずに閉じられるか。
  - one issue として reviewable な差分に収まるか。
  - provider source と dogfooding mirror の境界を守れるか。
- tradeoff:
  - Option A は小さいが、今回の実害である PR repair workflow の再発を防ぎきれない。
  - Option B は再発源に届くが、runtime + skill/docs の複数 surface を触る。
  - Option C は長期的にはきれいだが、public command/API 設計が膨らむ。
- リスク:
  - `new doc` は explicit basename override を持たないため、既存 skill が求める exact filename を完全には維持できない可能性がある。
  - Manual file write を完全禁止すると、delegated authoring など既存 workflow との整合確認が必要になる。
- 具体シナリオ / edge case:
  - 同一 PR observation loop で PR repair batch と複数 repair unit を同じ秒に作る場合、manual `<ts>` reuse だと validate が壊れる。per-artifact `new doc disc` なら suffix が付く。

## Codex の推奨案 (必須)
- 推奨:
  - Option B
- 理由:
  - #188 の failure は core runtime より skill/workflow guidance 由来の可能性が高く、そこを scope 外にすると「validator は正しいが生成側がまた壊す」状態が残る。
  - 一方で public batch allocator API まで広げると issue が大きくなるため、まずは existing `new doc` allocator を正本生成経路として使わせる方向が最小に見える。
- 未回答時の影響:
  - 要件の MUST / OUT OF SCOPE と plan の test obligation を確定できないため、canonical requirement authoring に進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Root problem is not merely suffix collision. The root problem is that skills/workflows manually construct timestamped filenames.
  - Discussion artifacts under `discussions/` should be generated by SpecDock script/runtime, not by hand-assembling filenames in skill instructions.
  - This root-cause correction is in scope for this issue even though it broadens the original framing.
  - Keep suffix allocation as a safety fallback, but normal generation should avoid suffixes where possible because suffix-less and suffixed names do not sort in true creation order.
  - Prefer a compact mechanical strategy that reduces timestamp collisions without unnecessarily lengthening filenames. Candidate ideas include sleeping on collision, adding one or two sub-second digits, or encoding sub-second time compactly. The user wants analysis and proposal before locking the exact design.
- 回答:
  - Include agent-facing skill/workflow correction in #188. Eliminate manual timestamped filename construction from skills where SpecDock can generate the artifact. Also analyze a better normal-case timestamp allocation strategy so suffixes remain a fallback rather than the default same-second collision path.
- 回答日時:
  - 2026-06-17

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
  - `report.md` Evidence Adoption Ledger / Spec Authoring Gate
- 採用 / 棄却 / deferred の理由:
  - The answer identifies a root cause that local source research also supports: runtime `new doc` already has collision handling, while skill guidance still describes manual `<ts>-...` filenames. This materially changes requirement scope and design direction, so it must be adopted into canonical issue docs.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Scope must include eliminating manual timestamped filename construction from SpecDock-provided artifact creation guidance for workflows such as PR repair batch / repair unit.
  - Requirements should distinguish normal-case collision avoidance from suffix fallback safety.
- `design.md`:
  - Design must propose a runtime/script-owned artifact creation path and evaluate compact timestamp collision avoidance strategies: wait-on-collision with existing grammar, sub-second precision, or compact sub-second token.
- `plan.md`:
  - Plan should include tests for multiple artifacts created in one operation/workflow and skill/docs contract checks that no shipped guidance instructs agents to reuse one `<ts>` manually.
- `ADR`:
  - likely none unless timestamp grammar changes in a durable/backward-impacting way.
- reflected_to 更新方針:
  - Update after canonical requirement/design/plan adoption.
- adoption reflection:
  - Record in `report.md` Evidence Adoption Ledger and Spec Authoring Gate when canonical docs are updated.

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
