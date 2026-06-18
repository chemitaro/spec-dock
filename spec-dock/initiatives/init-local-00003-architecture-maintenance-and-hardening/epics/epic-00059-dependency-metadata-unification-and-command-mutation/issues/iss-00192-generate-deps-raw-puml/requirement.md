---
種別: 要件定義書（Issue）
ID: "iss-00192"
タイトル: "Generate Raw Dependency View"
関連GitHub: ["#192"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["epic-00059", "init-local-00003"]
---

# iss-00192 Generate Raw Dependency View — 要件定義（何を、なぜ行うか）

## 目的
- `sync` が生成する human-facing artifact として `spec-dock/deps-raw.puml` を追加し、`.meta.json.depends_on` に保存された raw direct dependency を構造付きで確認できるようにする。
- 既存の issue-level effective dependency view とは別に、initiative / epic / issue をまたぐ direct dependency intent を人間とエージェントが読み取れるようにする。
- dependency の正本、mutation contract、readiness 判定は変更しない。

## 背景・現状
- 現状の挙動:
  - `sync` は `spec-dock/.agent/deps-issues.json` と `spec-dock/deps-issues.puml` を生成する。
  - 既存の `deps-issues` view は todo issue-only の effective graph であり、実行可否判定に合わせた issue-level dependency を表す。
  - `.meta.json.depends_on` は initiative / epic / issue node 間の direct dependency を保持できる。
- 現状の課題:
  - initiative / epic / issue をまたぐ raw direct dependency を、仕様ツリー構造の中で確認しにくい。
  - parent-level dependency と issue-level dependency が同じ effective issue graph に還元されるため、元の direct intent を人間が追いにくい。
- 情報源:
  - GitHub issue `#192`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_deps.md`
  - `discussions/20260617t154655z-research-raw-dependency-view-clarification-research.md`
  - `discussions/20260617t154656z-interview-raw-dependency-view-scope-question.md`
  - `discussions/20260618t001154z-disc-raw-dependency-view-visual-mock.md`
  - `discussions/20260618t002930z-deps-raw-flat-visual-simulation.puml`
  - `discussions/20260618t003500z-interview-deps-raw-discovery-surface.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock maintainer
  - SpecDock を使って issue / epic / initiative の依存関係を整理する agent
- 代表シナリオ:
  - `deps add/remove` 後に、raw direct dependency がどの node 間に保存されたかを視覚的に確認する。
  - epic 間、initiative 間、issue 間、mixed node-kind dependency を、issue-level effective graph へ還元される前の形で確認する。
  - dependency preflight failure 時に、raw dependency artifact が stale のまま残っていないことを確認する。

## スコープ
- 必須:
  - `./spec-dock/scripts/spec-dock sync` 実行時に `spec-dock/deps-raw.puml` を生成する。
  - `deps-raw.puml` は `.meta.json.depends_on` に保存された direct dependency edge を表示する。
  - `deps-raw.puml` は dependency-focused subset として、direct dependency に参加する node と、その祖先 initiative / epic package を表示する。
  - initiative / epic は PlantUML package として nested structure を表現し、issue は package 内の要素として表示する。
  - dependency edge は既存 `deps-issues.puml` と同じく human-facing の `blocks` 表現を基本にする。
  - issue->issue、epic->epic、initiative->initiative、epic->issue、issue->epic など、node-kind pattern が異なる dependency を、package endpoint / rectangle endpoint / nested package structure で読み分けられるようにする。
  - Visual design は、既存 `deps-issues.puml` に近い `left to right direction`、`skinparam linetype ortho`、`--> : blocks` を基本にする。
  - initiative / epic package は色で強調せず、issue の state color と dependency edge を主な視覚強調にする。
  - dashboard と `sync` 完了メッセージから `deps-raw.puml` の存在を発見できる。
  - generated artifact として `spec-dock/.gitignore` に追加する。
- 禁止:
  - `deps check` の実行可否判定ロジックを変更しない。
  - `deps add/remove` の mutation contract を変更しない。
  - 既存の `spec-dock/deps-issues.puml` と `spec-dock/.agent/deps-issues.json` の意味を変更しない。
  - `.meta.json.depends_on` 以外の dependency storage / fallback を追加しない。
- 対象外:
  - raw dependency view の JSON artifact 追加。
  - dependency weight / priority / severity など新しい依存意味論。
  - full canonical tree view の追加。必要なら将来の follow-up とする。

## 境界
- 常に行う:
  - Provider-side runtime source を正本として変更する。
  - Dogfooding workspace は検証対象として扱う。
  - `deps-raw.puml` は raw direct dependency visualization であり、readiness source of truth ではないことを保つ。
  - deps preflight failure 時は stale artifact を残さず、既存 disabled artifact と同等に原因を確認できる output を生成する。
- 判断が必要:
  - なし。
- 行わない:
  - dependency graph の validation rule をこの issue で拡張しない。
  - issue-level effective dependency view を raw direct dependency view で置き換えない。

## 非交渉制約
- `.meta.json.depends_on` を canonical dependency storage とする親 Epic の contract を維持する。
- `deps-issues.puml` は todo issue-only effective graph のまま維持する。
- `deps-raw.puml` は generated artifact であり、手編集を前提にしない。

## 前提
- `sync` の deps preflight が成功している場合は、raw direct dependency graph も安全に描画できる。
- `sync --force` のように deps preflight failure を許容して artifact を上書きする場合は、raw dependency view も disabled artifact として上書きする。
- Existing generated artifact pipeline は `ArtifactBundle` / `artifact_writer` / presentation renderer を通じて root `spec-dock/` と `.agent/` に artifact を出力する。
- valid tree に raw direct dependency が 1 件もない場合も、`deps-raw.puml` は生成する。この場合は stale graph や空ファイルではなく、依存がないことを示す placeholder note を表示する。

## 受け入れ条件
- AC-001:
  - アクター: SpecDock user
  - 前提: valid な `.meta.json.depends_on` direct dependency を持つ tree がある。
  - 操作: `./spec-dock/scripts/spec-dock sync` を実行する。
  - 期待結果: `spec-dock/deps-raw.puml` が生成される。
  - 観測点: file existence と sync output / dashboard discovery。
- AC-002:
  - アクター: SpecDock user
  - 前提: issue->issue direct dependency がある。
  - 操作: `deps-raw.puml` を確認する。
  - 期待結果: source / target issue と祖先 initiative / epic package が表示され、dependency は `blocks` direction で確認できる。
  - 観測点: PlantUML text。
- AC-003:
  - アクター: SpecDock user
  - 前提: epic->epic または initiative->initiative direct dependency がある。
  - 操作: `deps-raw.puml` を確認する。
  - 期待結果: parent-level dependency が issue-level dependency と視覚的に区別できる。
  - 観測点: PlantUML package endpoint と nested package structure。
- AC-004:
  - アクター: SpecDock user
  - 前提: epic->issue または issue->epic の mixed node-kind direct dependency がある。
  - 操作: `deps-raw.puml` を確認する。
  - 期待結果: mixed dependency が issue->issue dependency と視覚的に区別できる。
  - 観測点: PlantUML package endpoint / rectangle endpoint と nested package structure。
- AC-005:
  - アクター: SpecDock maintainer
  - 前提: 既存 `deps-issues.puml` / `.agent/deps-issues.json` の fixture がある。
  - 操作: `sync` を実行する。
  - 期待結果: 既存 artifact の projection / node set / edge semantics は変わらない。
  - 観測点: 既存 regression tests。
- AC-006:
  - アクター: SpecDock user
  - 前提: deps preflight が失敗する tree がある。
  - 操作: `sync --force` を実行する。
  - 期待結果: `deps-raw.puml` は stale graph を残さず、deps disabled 状態と原因を確認できる内容で上書きされる。
  - 観測点: PlantUML text。
- AC-007:
  - アクター: SpecDock maintainer
  - 前提: `deps-raw.puml` が generated artifact として生成される。
  - 操作: `spec-dock/.gitignore` または Git ignore 判定を確認する。
  - 期待結果: `spec-dock/deps-raw.puml` は generated artifact として ignore 対象になる。
  - 観測点: `.gitignore` content または `git check-ignore spec-dock/deps-raw.puml`。

## 例外・エッジケース
- EC-001:
  - 条件: direct dependency に参加する node が initiative または epic で、配下 issue が存在しない。
  - 期待: raw direct dependency participant として表示される。issue-level expansion が空でも raw intent は確認できる。
  - 観測点: PlantUML package / node / edge。
- EC-002:
  - 条件: direct dependency に参加しない issue / epic / initiative が tree に存在する。
  - 期待: `deps-raw.puml` には表示しない。ただし dependency participant の祖先 package は表示する。
  - 観測点: PlantUML text。
- EC-003:
  - 条件: closed issue または done-only branch の node が direct dependency に参加している。
  - 期待: raw direct dependency participant として表示される。todo projection ではなく raw direct graph であるため、done status だけを理由に除外しない。
  - 観測点: PlantUML text。
- EC-004:
  - 条件: valid tree に `.meta.json.depends_on` direct dependency が 1 件もない。
  - 期待: `deps-raw.puml` は生成され、依存がないことを示す placeholder note を表示する。stale graph、空ファイル、生成スキップにはしない。
  - 観測点: PlantUML text と file existence。

## 入力→出力例
- EX-001:
  - 入力:
    - `iss-00302.depends_on = ["iss-00301"]`
  - 出力:
    - `deps-raw.puml` に `iss-00301` と `iss-00302` が同じ epic package 内の要素として表示され、`iss-00301 --> iss-00302 : blocks` 相当の edge が表示される。
- EX-002:
  - 入力:
    - `epic-00201.depends_on = ["epic-00202"]`
  - 出力:
    - `deps-raw.puml` に両 epic package と祖先 initiative package が表示され、package endpoint と `blocks` edge によって epic-level dependency と分かる。

## 用語（ドメイン語彙）
- raw direct dependency:
  - `.meta.json.depends_on` に保存された node-level direct dependency。issue-level effective graph へ compile される前の依存意図。
- issue-level effective graph:
  - `deps check` や `deps-issues.puml` が使う、実行可否判定向けの issue-only dependency graph。
- dependency-focused subset:
  - direct dependency の source / target node と、その表示に必要な祖先 initiative / epic package だけを含む view。
- blocks direction:
  - human-facing PlantUML で prerequisite から dependent へ向ける表示方向。既存 `deps-issues.puml` と同じ読み方。

## 未確定事項
- Q-001:
  - 質問: `deps-raw.puml` の表示対象は full tree か dependency-focused subset か。
  - 回答: dependency-focused subset を採用する。
  - 証跡: `discussions/20260617t154656z-interview-raw-dependency-view-scope-question.md`
  - 状態: resolved
- Q-002:
  - 質問: node-kind pattern ごとの視覚区別を具体的にどの PlantUML 表現へ落とすか。
  - 回答: `left to right direction`、`skinparam linetype ortho`、`--> : blocks` を基本にし、initiative / epic は白背景 package、issue は state color 付き rectangle として表示する。initiative / epic package 自体の色強調は行わない。
  - 証跡: `discussions/20260618t001154z-disc-raw-dependency-view-visual-mock.md`, `discussions/20260618t002930z-deps-raw-flat-visual-simulation.puml`, `report.md` D-002 / EAL-002
  - 状態: resolved
- Q-003:
  - 質問: `deps-raw.puml` の発見導線を dashboard / sync output / context pack のどこまで含めるか。
  - 回答: Option B を採用し、dashboard と `sync` 完了メッセージに含める。context pack / active-none guidance はこの issue の必須範囲に含めない。
  - 証跡: `discussions/20260618t003500z-interview-deps-raw-discovery-surface.md`, `report.md` D-003 / EAL-003
  - 状態: resolved
