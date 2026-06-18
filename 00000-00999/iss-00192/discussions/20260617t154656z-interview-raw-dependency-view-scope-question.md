---
種別: interview
ID: "20260617t154656z-interview"
タイトル: "Raw Dependency View Scope Question"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00192"]
関連: []
scope: "issue"
scope_id: "iss-00192"
created_at: "2026-06-17T15:46:56Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260617t154655z-research"
  - "GitHub #192"
reflected_to:
  - "requirement.md"
  - "report.md"
---

# 20260617t154656z-interview Raw Dependency View Scope Question

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
    - `deps-raw.puml` の表示対象範囲、受け入れ条件、非スコープの明確化。
  - `design.md`:
    - renderer が full tree を描くか dependency-focused subset を描くか、node inclusion rule、empty branch handling。
  - `plan.md`:
    - テスト fixture と expected PlantUML assertion、dashboard discovery assertion。
  - `ADR`:
    - なし。長期 architecture decision ではなく issue-local requirement/design tradeoff。
- chat 上の軽微な一問では足りない理由:
  - 回答によって生成物の形、テスト期待値、読み手の体験、既存 `tree-all.puml` との重複度が変わるため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / product owner。
- 何を明確にする質問か:
  - `deps-raw.puml` に含める node の範囲を確定する。
- 回答が後続判断へ与える影響:
  - requirement の scope、design の inclusion rule、plan の test cases を固定する。

## 質問 (必須)
- pressure-test question:
  - `deps-raw.puml` は「仕様ツリー全体」そのものを raw dependency 付きで描くべきか、それとも「direct dependency に参加する node だけ」を祖先 package 付きで描くべきか。
- 質問:
  - `deps-raw.puml` の表示対象はどちらにしたいですか？
- 回答してほしいこと:
  - Option A / B / C のどれを採用するか。迷う場合は、想定する主な利用シーンを一言添えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#192`: `sync` で `spec-dock/deps-raw.puml` を生成し、initiative / epic / issue の階層と `.meta.json.depends_on` direct dependency を表示する要求。
  - `spec-dock/docs/reference_sync.md`: 既存 human-facing generated artifacts は `tree-all.puml`, `tree.puml`, `deps-issues.puml`, `dashboard.md`。
  - `spec-dock/docs/reference_deps.md`: direct dependency は `.meta.json.depends_on` の node-level edge。downstream は issue-level effective graph に compile する。
  - `presentation/json_state.py`: 既存 `deps-issues` は todo projection / issue-only effective graph から生成。
  - `presentation/puml.py`: 既存 puml renderer は ready board / deps-issues 専用。
  - `infra/artifact_writer.py`: root 直下 artifact write path に `deps-raw.puml` を追加する余地がある。
  - `tests/cli_runtime/test_sync.py`: generated puml / dashboard / gitignore の期待値が既にある。
- local context で解決できたこと:
  - `deps check`, `deps add/remove`, `deps-issues.puml`, `.agent/deps-issues.json` の意味は変更しない。
  - `deps-raw.puml` は human-facing root artifact として扱う。
  - preflight failure 時は既存 artifact と同じく disabled output を上書きするのが自然。
- まだ人間判断が必要な理由:
  - GitHub issue body の「canonical tree」は full tree とも読める一方、raw dependency view の目的だけを考えると dependency-focused subset の方が読みやすい。どちらを product behavior とするかは利用意図の判断になる。

## 回答案 (必須)
- Option A:
  - Full tree: 全 initiative / epic / issue を package nesting で描き、direct dependency edge を追加する。
  - 長所: GitHub issue body の「canonical tree」に最も忠実。閉じ済み node や依存なし node も構造として見える。
  - 短所: 大きい repo では図が肥大化し、raw dependency intent が埋もれやすい。`tree-all.puml` と役割が重なりやすい。
- Option B:
  - Dependency-focused subset: direct dependency の source/target node と、その祖先 initiative / epic package だけを描く。
  - 長所: raw dependency intent を読みやすい。`tree-all.puml` と役割が分かれる。テストも「edge participants + ancestor packages」として明確。
  - 短所: 依存なし node は表示されないため、完全な canonical tree ではない。
- Option C:
  - Hybrid: default は dependency-focused subset にし、将来 option/別 artifact で full tree を検討する。
  - 長所: 初回 diff を小さくしつつ、将来の full audit view を塞がない。
  - 短所: 今回の issue だけでは full tree 欲求を満たさない。

## Codex の分析 (必須)
- 判断軸:
  - 図の主目的が「全体構造の確認」か「raw direct dependency intent の確認」か。
  - 既存 `tree-all.puml` との重複を許容するか。
  - 大きい repo での読みやすさ。
  - テストで固定すべき expectation の明確さ。
- tradeoff:
  - Full tree は仕様文に忠実だが、dependency view としてはノイズが多くなりやすい。
  - Subset は実用的だが、`canonical tree` という表現を requirement で「参加 node と祖先 package の構造」と明確化する必要がある。
- リスク:
  - Full tree を選ぶと generated artifact が大きくなり、今後 import 済み historical issue が増えるほど読みにくくなる。
  - Subset を選ぶと、ユーザーが「依存なし node も含めた全体 audit」を期待していた場合に不足する。
- 具体シナリオ / edge case:
  - `epic-00059 depends_on epic-00158` のような parent-level edgeだけを確認したい場合、subset は両 epic と祖先 initiative だけを表示すれば十分。
  - 全 issue の中で依存が 2 本しかない場合、full tree では依存 edge を探すのがつらい。
  - Empty epic dependency は subset でも epic package/node を表示すれば raw intent は確認できる。

## Codex の推奨案 (必須)
- 推奨:
  - Option B: Dependency-focused subset。
- 理由:
  - この issue の目的は `tree-all.puml` の代替ではなく、`.meta.json.depends_on` の raw direct intent を人間とエージェントが確認することだから。
  - `deps-raw.puml` という名前からも、依存がない node を網羅するより、raw direct edge とその構造的文脈を読みやすくする方が合う。
  - 既存の full tree は `tree-all.puml` にあるため、役割分担が明確になる。
- 未回答時の影響:
  - requirement / design / plan の acceptance と tests を確定できず、実装に入ると生成物の粒度で手戻りしやすい。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option B を採用する。
  - `deps-raw.puml` は initiative / epic を package として表示し、その中に issue 要素を含める nested structure を描画する。
  - dependency edge は既存 `deps-issues.puml` と同じく `blocks` の表現を基本にする。
  - issue 同士、epic 間、initiative 間など、依存の抽象度が異なる場合は、矢印の形・強さ・見た目を変えて視覚的に区別しやすくする。
- 回答:
  - Option B: direct dependency に参加する node と、その祖先 initiative / epic package だけを表示する。
- 回答日時:
  - 2026-06-18T00:00:00+09:00

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
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - 表示対象範囲と edge 表現は product behavior / acceptance criteria / renderer design / tests に影響するため、ユーザー回答を requirement に採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `deps-raw.puml` は dependency-focused subset として定義する。
  - initiative / epic は package nesting、issue は要素として描画する。
  - direct dependency edge は基本 `blocks` 表現に寄せつつ、dependency の node-kind pattern を視覚的に区別する。
- `design.md`:
  - raw direct dependency participant と ancestor package を抽出する inclusion rule を設計する。
  - edge style / label / line strength などの視覚区別を renderer contract に入れる。
- `plan.md`:
  - issue->issue、epic->epic、initiative->initiative、mixed edge の fixture と PlantUML assertion を固定する。
- `ADR`:
  - none
- reflected_to 更新方針:
  - `requirement.md` と `report.md` に反映済みとして扱う。design / plan は後続 authoring phase で反映する。
- adoption reflection:
  - User-approved scope decision for `deps-raw.puml` rendering.

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
