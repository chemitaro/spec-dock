---
種別: interview
ID: "20260713t001708z-interview"
タイトル: "Scope Workbench Copy Collision Policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: []
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T00:17:08Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260712t235757z-interview-initial-workbench-copy-file-policy.md"
  - "artifacts/20260713t000250z-interview-root-workbench-cross-worktree-handoff.md"
reflected_to:
  - "epic-00312 requirement/design/plan authoring input"
  - "epic-00312 report.md Evidence Adoption Ledger"
---

# 20260713t001708z-interview Scope Workbench Copy Collision Policy

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Existing destination Workbenchへ全内容を配置するときの結果契約。
  - `design.md`:
    - Recursive directory mergeと同名path collisionのdeterministic semantics。
  - `plan.md`:
    - Copy commandのpositive / collision / partial failure tests。
  - `ADR`:
    - 現時点では不要。
- chat 上の軽微な一問では足りない理由:
  - 同名fileを上書きするか保持するかでデータ消失、command idempotency、failure contractが変わる。

## 質問の目的 (必須)
- 対象者:
  - Product owner / maintainer。
- 何を明確にする質問か:
  - SourceとdestinationのScope-local Workbenchに同じrelative pathがある場合のcopy結果。
- 回答が後続判断へ与える影響:
  - Copy commandが通常の上書きcopy、衝突時fail、既存優先mergeのどれになるかを固定する。

## 質問 (必須)
- pressure-test question:
  - Destinationに`notes.md`があり、Sourceにも別内容の`notes.md`がある状態でWorkbench全体を配置するとき、どちらを残すか。
- 質問:
  - Scope-local Workbench copyで同名pathが衝突した場合、Sourceで上書きしますか、commandを停止しますか、それともDestinationを保持してSource側をskipしますか。
- 回答してほしいこと:
  - Option A / B / Cの選択、または別の単純なcollision semantics。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - 回答済みfile policyとroot handoff interview、current worktree runtime、ユーザーの「directory置換ではなく全fileを配置する」回答。
- local context で解決できたこと:
  - Workbench全体を形式不問でcopyし、Destination Workbenchが存在していてもdirectory自体を置換せず内容を配置する。
- まだ人間判断が必要な理由:
  - 「配置」が同名fileの上書きまで含むかは明示されておらず、repository sourceからProduct ownerの期待を決められない。

## 回答案 (必須)
- Option A:
  - **Source優先で上書き（推奨）**。Directoryを再帰mergeし、同名fileはSource内容で置換する。通常のcopy/pasteに近く、最も単純。
- Option B:
  - **衝突時に全体fail**。事前走査で一件でも同名pathがあれば何もcopyしない。データ保護は強いが、雑なWorkspaceでは頻繁に停止しうる。
- Option C:
  - **Destination優先でskip**。新しいpathだけ追加し、同名pathは既存を保持する。Commandは成功するがSource文脈が欠落しうる。

## Codex の分析 (必須)
- 判断軸:
  - 単純性、copy/pasteの直感、既存target data保護、再実行時の予測可能性。
- tradeoff:
  - Aは単純だがtargetの同名fileを失う。Bは安全だが事前collision scanとmanual cleanupが必要。Cは非破壊だがcopy結果がSourceのsnapshotにならない。
- リスク:
  - Aの意図しない上書き、Bの高頻度block、Cのsilent omission。
- 具体シナリオ / edge case:
  - File対directory collision、再実行、partial copy中のI/O failure、同名nested `.git` directory。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - ユーザーが求める「複雑な判断をせず、Workbenchごとcopy/pasteする」に最も一致する。Experimental / disposable areaなので、copy前backupやcontent mergeをcommand責務にしない。
- 未回答時の影響:
  - Copy commandの最終acceptance criteriaとatomicity / collision testsを確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 2026-07-13のチャット回答。
- 回答:
  - Option Aを採用する。
  - Scope-local Workbenchを再帰的にmergeし、同じrelative pathのfileはSource側で上書きする。
  - Destinationにしかないfileは残し、Sourceに存在するfile / directoryはすべてDestinationへ配置する。
- 回答日時:
  - 2026-07-13 Asia/Tokyo

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Experimental Workbenchをconsumerへどの段階で公開するか。`init/update`で全consumerへ配布するがexperimental表記にするか、dogfooding repo専用で開始するか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Product ownerが明示的に選択し、copy commandの結果契約、failure handling、testsを決めるため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - CopyはDestination Workbenchの既存内容を保持しつつSource内容を全配置し、同名fileはSource優先で上書きする。
- `design.md`:
  - Recursive directory merge / source-wins file replacementをdeterministic contractとして固定する。Content-level mergeは行わない。
- `plan.md`:
  - File追加、nested directory merge、same-path overwrite、file-directory collision、再実行、I/O failureをcopy command Issueのtest seedにする。
- `ADR`:
  - 現時点では不要。
- reflected_to 更新方針:
  - Canonical authoring時にrequirement / design / planへ反映し、report EALへ本artifactを採用証跡として記録する。
- adoption reflection:
  - Option Aを採用。Destination全体の置換やcontent mergeはせず、filesystem tree mergeとSource優先上書きに限定する。

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
- 追加で作る artifacts:
  - ...
