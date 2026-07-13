---
種別: interview
ID: "20260712t235757z-interview"
タイトル: "Initial Workbench Copy File Policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-12"
親: ["epic-00312"]
関連: []
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-12T23:57:57Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md"
reflected_to:
  - "epic-00312 requirement/design/plan authoring input"
  - "epic-00312 report.md Evidence Adoption Ledger"
---

# 20260712t235757z-interview Initial Workbench Copy File Policy

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
    - Workbenchの低摩擦性とcopy時の安全・対象file contract。
  - `design.md`:
    - Copy validator、filesystem traversal、許容file kind、failure contract。
  - `plan.md`:
    - Experimental copy command Issueの実装量、fixture、negative test matrix。
  - `ADR`:
    - 現時点では不要。Epic内の可逆なexperimental contractとして扱う。
- chat 上の軽微な一問では足りない理由:
  - 回答により主要目的である「雑に使える」の意味と、copy commandの受け入れ条件・実装範囲が変わり、複数canonical artifactへ反映する必要がある。

## 質問の目的 (必須)
- 対象者:
  - Product owner / maintainer。
- 何を明確にする質問か:
  - 初期experimental `workbench copy`がどの種類のlocal fileをcopy対象にするか。
- 回答が後続判断へ与える影響:
  - Exact local snapshotを優先するか、text-only safety gateを優先するかを決める。

## 質問 (必須)
- pressure-test question:
  - Workbenchに画像、binary、archive、生成物、秘密情報候補が混在している場合でも、local worktree間の忠実なsnapshotとしてコピーしたいか。
- 質問:
  - 初期の`workbench copy`は、通常ファイルを形式不問でそのままコピーする方針と、text系ファイルだけを安全検査してコピーする方針のどちらにしますか。
- 回答してほしいこと:
  - Option A / B / Cの選択、または境界の修正。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Epic 00312 research baseline、親Initiative、Epic 259 / 295 / 107、managed gitignore、metadata / source-manifest recursive walkers、worktree tests。
- local context で解決できたこと:
  - WorkbenchはGit ignored / disposable / non-canonical、copyは明示実行・単一scope・no overwrite・no sync、raw ZIPはexternal quarantineである。
- まだ人間判断が必要な理由:
  - 実際にWorkbenchへ入れたいfile kindと、低摩擦性に対してどこまでcopy時検査を許容するかはrepository sourceから判断できない。

## 回答案 (必須)
- Option A:
  - **忠実なlocal snapshot（推奨）**。Symlink、special file、nested `.git`、path escapeだけを拒否し、通常ファイルは拡張子を問わずコピーする。秘密情報や大容量fileを置かない責任はWorkbench利用者が持つ。
- Option B:
  - **Text-only安全コピー**。Markdown / text / JSON / YAML / diffなどのallowlist、secret scan、file / total size capを初期必須にし、binary / image / archiveを拒否する。
- Option C:
  - **二段階**。通常はAでlocal snapshot、`--safe-text-only`のような明示modeだけBを提供する。ただしexperimental v1のCLIとtest matrixが増える。

## Codex の分析 (必須)
- 判断軸:
  - Workbenchの低摩擦性、ローカル間copyで増える実際のsecurity boundary、予測可能性、実装量、将来拡張性。
- tradeoff:
  - Aは最も単純で「どんどんぶっこむ」に整合するが、不要なlarge / secret fileも複製しうる。Bは安全だが、Workbenchとcopy結果が一致せず、file catalog管理が新たに必要になる。Cは柔軟だが初期には過剰。
- リスク:
  - Aでは別worktreeへの秘密情報複製と容量増加。Bでは必要資料の欠落とfalse positive。Cではexperimental featureの肥大化。
- 具体シナリオ / edge case:
  - UI screenshot、SQLite調査file、large ChatGPT output、`.env`、symlinked directory、raw ZIPがScope-local Workbenchに混在するケース。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。ただしraw archiveのquarantine原則は維持し、symlink / special file / nested `.git` / destination overwriteは必ず拒否する。
- 理由:
  - Copy元と先はいずれも同一利用者のlocal ignored areaであり、初期機能の目的は内容審査ではなくworktree分岐時の欠落防止である。Safety catalogはdogfoodで必要性が実証されてから追加できる。
- 未回答時の影響:
  - Requirement / design / Issue slicingの骨格は進められるが、copy commandのacceptance criteriaとtest obligationを確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 2026-07-13のチャット回答。複雑な除外・選択ロジックを入れず、Workbench directoryを内容ごとごっそりcopyする方針を指定した。
- 回答:
  - File type、拡張子、`.git`、binary、archiveなどで選別しない。
  - Workbenchに存在するものはすべて持っていく。
  - Destination Workbenchが既に存在しうるため、directory自体の置換ではなく、内容をdestinationへcopy / pasteして配置する。
  - WorkbenchはGit管理外の雑な作業領域であり、copy commandもその性質に合わせて単純にする。
- 回答日時:
  - 2026-07-13 Asia/Tokyo

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Scopeに閉じないroot Workbenchをworktree間でどうhandoffするか。Root全体copyは広すぎ、Scope ID管理は二重treeになるため、topicのscope-local attachを標準にするか、root topic単位copy commandを持つか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Product ownerの明示回答であり、低摩擦という主要目的、copy commandの実装境界、test obligationを直接決めるため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Scope-local copyはWorkbench全体を形式不問でcopyし、file allowlist / denylist / secret scan / size-based selectionを要件にしない。
- `design.md`:
  - Copy implementationはWorkbench subtreeの内容を解釈しない。Directoryが既存でも内容配置を許す。Nested `.git`等もcopy対象から除外しない。
- `plan.md`:
  - Experimental copy Issueからcontent classification / secret scanner / archive validatorを除外し、recursive copyとdestination merge/collision semanticsのtestsに集中する。
- `ADR`:
  - 現時点では不要。Experimental Epic内で変更可能なcopy contractとして所有する。
- reflected_to 更新方針:
  - Canonical authoring時にrequirement / design / planへ採用し、report EALへ本artifact pathと採用判断を記録する。
- adoption reflection:
  - 当初のOption Aに含めたsymlink / nested `.git` / special-file除外も採用しない。CopyとWorkbench placement policyは分離し、copy commandは存在する内容を選別しない。

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
