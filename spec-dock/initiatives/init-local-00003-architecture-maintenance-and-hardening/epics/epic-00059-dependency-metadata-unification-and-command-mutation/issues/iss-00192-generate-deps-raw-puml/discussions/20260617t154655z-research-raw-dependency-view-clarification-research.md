---
種別: research
ID: "20260617t154655z-research"
タイトル: "Raw Dependency View Clarification Research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00192"]
関連: []
authority: "synthesized"
derived_from:
  - "GitHub #192"
  - "spec-dock/docs/reference_sync.md"
  - "spec-dock/docs/reference_deps.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py"
  - "tests/cli_runtime/test_sync.py"
reflected_to:
  - "20260617t154656z-interview"
---

# 20260617t154655z-research Raw Dependency View Clarification Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00192` の GitHub issue 本文、親 Epic、既存 sync/deps 実装を照合し、`deps-raw.puml` の要件具体化前に source-grounded に解ける事項と、人間判断が必要な事項を分ける。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub issue `#192`: `deps-raw.puml` の背景、スコープ、受け入れ条件。
  - `spec-dock/active/issue/{requirement,design,plan}.md`: import 直後の scaffold 状態で、詳細要件は未反映。
  - `spec-dock/active/epic/{requirement,design}.md`: `.meta.json.depends_on` を dependency SoT とし、`deps add/remove/check` と downstream `sync` / `validate` / `active` の整合を守る親文脈。
  - `spec-dock/docs/reference_sync.md`: 既存 generated artifacts、`--force` 時の deps disabled artifact、`deps-issues.puml` の位置づけ。
  - `spec-dock/docs/reference_deps.md`: node-level direct dependency と issue-level compiled dependency の契約。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`: `ArtifactBundle` を作り、index/tree/deps/dashboard を一括 render/write する経路。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`: `index-all/index/tree/deps-issues` payload 作成と `render_deps_issues_artifact`。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`: `tree*.puml` と `deps-issues.puml` の既存 PlantUML renderer。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py`: root 直下 artifact の write path。
  - `tests/cli_runtime/test_sync.py`: `deps-issues.puml`, `tree*.puml`, dashboard, gitignore の期待値。
- 検証手順:
  - active issue start 後に active docs / parent docs を確認。
  - GitHub issue body を一次情報として確認。
  - `rg` と targeted `sed` で sync/deps/puml writer と既存テストを確認。
- 実験条件:
  - 実装変更はまだ行っていない。調査と unanswered interview artifact 作成のみ。

## facts / 観測できた事実 (必須)
- `iss-00192` の canonical `requirement.md` / `design.md` / `plan.md` は import scaffold のままで、GitHub issue body の内容を requirement authoring へ採用する必要がある。
- GitHub issue `#192` は、`sync` が `spec-dock/deps-raw.puml` を生成すること、raw direct dependency を initiative / epic / issue の抽象度を問わず描画すること、既存 `deps-issues.puml` と `.agent/deps-issues.json` の意味を変えないことを要求している。
- `reference_sync.md` は現行 generated artifacts として `.agent/index-all.json`, `.agent/tree-all.json`, `.agent/index.json`, `.agent/tree.json`, `.agent/deps-issues.json`, `tree-all.puml`, `tree.puml`, `deps-issues.puml`, `dashboard.md` を列挙している。
- `reference_sync.md` は `deps-issues.puml` を todo issue-only 依存図として説明し、JSON の `depends_on` direction と PlantUML の `blocks` direction を分けている。
- `reference_deps.md` は direct dependency の canonical storage を node 直下 `.meta.json.depends_on` とし、initiative / epic / issue node 間の direct edge を保存できる契約を持つ。
- 現在の `render_deps_issues_artifact` は `index.json` の todo projection から issue node だけを抽出して `deps-issues` payload と puml を作っている。
- 現在の writer は `ArtifactBundle` に含まれる artifact を root `spec-dock/` と `.agent/` に書き出す。`deps-raw.puml` を追加するには contracts / writer / sync bundle / tests / docs / gitignore の追随が必要になる。
- `--force` で deps preflight が失敗した場合、既存 artifact は placeholder / disabled output で stale artifact を避ける契約になっている。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `deps-raw.puml` は machine-facing JSON を新設するより、human-facing PlantUML artifact として `deps-issues.puml` / `tree*.puml` と同じ presentation layer に置くのが自然。
  - raw direct dependency の材料は `index-all.json` / `tree-all.json` に含まれる compiled issue edge ではなく、`.meta.json.depends_on` の node-level resolutions を参照する必要がある。
  - 既存の `deps-issues.puml` は todo issue-only として維持し、`deps-raw.puml` は issue readiness 判定や dashboard summary の source of truth にしない方が安全。
  - `--force` 失敗時は `deps-issues.puml` と同様に disabled artifact を上書き生成するのが既存 contract と合う。
- 推測の根拠:
  - GitHub issue body が「正本や実行判定を変更しない」「raw dependency intent を構造付きで確認」と明記しているため。
  - 既存 `sync` artifact は stale 防止のため、成功時も force disabled 時も artifact を上書きする設計になっているため。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `deps_reader` が raw node dependency resolution を sync result にどの形で露出しているか、あるいは新たに渡す必要があるか。
  - actual implementation の最小 diff と、既存 test helper で initiative/epic direct dependency を作る具体手順。
  - provider-side docs / dogfooding mirror のどこまでを同一 issue で更新するか。
- 確認できない理由:
  - 現時点では clarification phase であり、requirement / design / plan authoring 前のため、実装詳細調査は必要最小限に留めている。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `deps-raw.puml` に全 canonical node を表示するか、direct dependency に参加する node と祖先 package だけを表示するか。
  - dashboard の discovery を「Observability にリンク追加」だけにするか、raw deps 専用セクション/説明も入れるか。
- pressure-test question として切り出すべき候補:
  - `deps-raw.puml` の表示対象範囲。これは requirement の scope、puml renderer の design、test expectation、可読性に直接影響する。
- 質問せずに解決できた候補:
  - `deps check` / readiness 判定 / `deps-issues.puml` は変更しない。
  - `deps-raw.puml` は root `spec-dock/deps-raw.puml` に生成する。
  - direct dependency edge は `.meta.json.depends_on` に保存された raw direct edge を表示対象にする。
  - preflight failure 時は stale artifact を残さず disabled artifact を上書きする。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `dependency view`: 既存は todo issue-only effective graph、今回の raw view は node-level direct graph。
  - `depends_on` direction と `blocks` direction: JSON は dependent -> prerequisite、PlantUML では human-facing に prerequisite -> dependent の blocks 表示が既存。
- 既存 docs / code / tests / discussions での使われ方:
  - `deps-issues.json` は `edge_direction: depends_on (dependent -> prerequisite)`。
  - `deps-issues.puml` は `prerequisite --> dependent : blocks`。
  - GitHub issue `#192` は raw direct dependency を「矢印」とだけ書いており、direction label は未確定。
- 判断が必要な理由:
  - `deps-raw.puml` で `depends_on` direction をそのまま出すか、既存 puml と揃えて `blocks` direction にするかは、読み手の誤読可能性と受け入れテストに影響する。ただし既存 puml の convention に合わせるなら `blocks` 表示が自然。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Direct dependency が initiative -> initiative, epic -> epic, epic -> issue, issue -> epic のように抽象度をまたぐ。
  - Empty initiative / epic に direct dependency がある。
  - Closed issue / done-only branch に direct dependency がある。
  - deps preflight が失敗して raw graph を安全に描画できない。
- その edge case が requirement / design / plan に与える影響:
  - 表示対象を full tree にするか dependency-focused subset にするかで、empty container / done-only branch の扱いが変わる。
  - disabled artifact の期待値を plan の test obligation に含める必要がある。

## implications / 判断への含意 (必須)
- `requirement.md` には、`deps-raw.puml` が raw direct dependency visualization であり、readiness / `deps check` / compiled issue graph の contract を変更しないことを明記する。
- `requirement.md` または `design.md` では、表示対象範囲を user-approved にする必要がある。
- `design.md` では existing artifact pipeline に合わせ、presentation contract / puml renderer / artifact writer / dashboard discovery / gitignore / tests の変更範囲を明記する。
- `plan.md` では at least:
  - raw direct edge rendering including non-issue nodes。
  - existing `deps-issues` behavior preservation。
  - deps preflight failure disabled output。
  - dashboard or sync output discovery。
  - gitignore update。
  を closure obligation にする。

## リスク/制約 (任意)
- Full tree 表示は仕様全体が大きい repo で読みにくくなる可能性がある。
- Dependency-focused subset 表示は GitHub issue body の「canonical tree」を狭く解釈しすぎる可能性がある。
- Raw direct dependency と compiled issue dependency の意味を混ぜると、`deps check` の readiness 判定が変わったように誤読される。

## 反映先 (任意)
- reflected_to:
  - `20260617t154656z-interview`
  - future `requirement.md`
  - future `design.md`
  - future `plan.md`
  - future `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- GitHub issue `#192`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_deps.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py`
