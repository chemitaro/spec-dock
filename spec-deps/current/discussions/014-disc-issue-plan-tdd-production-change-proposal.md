---
種別: disc
ID: "014-disc-issue-plan-tdd-production-change-proposal"
タイトル: "issue plan TDD 方針を production docs へ反映する修正案"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00021"]
関連: [
  "010-disc-phase-plan-shrink-proposal",
  "011-disc-scope-specific-plan-playbook-drafts",
  "012-disc-plan-playbook-responsibility-redistribution",
  "013-disc-issue-plan-tdd-embedding-best-practice",
  "#21",
  "https://github.com/chemitaro/spec-dock/issues/21"
]
---

# 014-disc issue plan TDD 方針を production docs へ反映する修正案

## 結論
- 採用するべき production 反映方針は、`plan` の 4 層構成と issue TDD 埋め込み方針を同時に反映する案である。
- つまり、次をまとめて行うのが最善である。
  - shared [phase_plan.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/phase_plan.md) を縮退する
  - `phase_plan_initiative.md` `phase_plan_epic.md` `phase_plan_issue.md` を新設する
  - [workflow_issue.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/workflow_issue.md) は TDD policy の正本として保つ
  - [issue/plan.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/templates/issue/plan.md) に `iteration = 1 tdd cycle` を反映する
- これにより、shared の汚染を防ぎつつ、issue 実装計画書に TDD を強制力のある構造として組み込める。

## 今回の修正で固定したいこと
- `plan` の shared axiom と scope-specific authoring rule を分ける
- issue plan は execution contract として扱う
- issue TDD は「補足説明」ではなく nested structure に埋め込む
- cadence policy の正本は workflow に残し、plan playbook / template はその構造化に集中する

## fixed contract

### plan 4 層モデル
- `phase_plan.md`: shared axiom
- `phase_plan_<scope>.md`: scope ごとの plan authoring contract
- `workflow_initiative.md` / `workflow_epic.md`: lifecycle / governance
- `workflow_issue.md`: lifecycle / governance / execution policy
- `templates/<scope>/plan.md`: 実案件で埋める schema

### issue plan の nested semantics
- `milestone = review / QA の区切り`
- `step = 1 observable behavior`
- `block = optional concern group`
- `iteration = 1 tdd cycle`
- `Red / Green / Refactor = iteration の内部フェーズ`

### ownership
- `workflow_initiative.md` / `workflow_epic.md`
  - lifecycle / governance の正本
  - execution policy は持たない
- `workflow_issue.md`
  - TDD cadence policy の正本
  - `step = 1 observable behavior` invariant の正本
  - review / fix / re-review / report / commit rhythm の正本
- `phase_plan_issue.md`
  - `workflow_issue.md` の policy と invariant を `plan.md` にどう埋め込むかの正本
- `templates/issue/plan.md`
  - 実案件で埋める器

## 修正対象

### 新設するファイル
- `src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`

### 更新するファイル
- `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md`

## ファイル別修正案

### 1. `phase_plan.md`
目的
- shared axiom へ縮退する

入れること
- plan の目的
- `target / decomposition / sequence / gate / dependency / exit`
- `shared minimum gate`
- `scope-specific readiness contract`
- `final exit contract`
- scope 別 plan playbook へのリンク

削ること
- issue 専用の nested 説明
- TDD cadence の説明
- `S90` `S99` の detail
- template section の詳細列挙

期待効果
- shared doc の context 汚染を止める

### 2. `phase_plan_initiative.md`
目的
- roadmap / milestone / epic readiness の authoring contract を定義する

入れること
- milestone の切り方
- epic portfolio の粒度
- strategy / investment gate
- epic readiness contract
- final exit contract

入れないこと
- issue step
- TDD
- commit cadence

### 3. `phase_plan_epic.md`
目的
- issue decomposition / integration / rollout の authoring contract を定義する

入れること
- issue slicing 方針
- tranche / integration checkpoint
- rollout / observability / migration gate
- issue readiness contract
- final exit contract

入れないこと
- issue 内 TDD
- step / block / iteration

### 4. `phase_plan_issue.md`
目的
- issue 実装計画書を TDD ベースの execution contract として書くための正本にする

入れること
- `block = optional concern group`
- `iteration = 1 tdd cycle`
- `Red / Green / Refactor = iteration の内部フェーズ`
- iteration ごとに failing test を 1 本ずつ進めること
- `workflow_issue.md` が持つ `step = 1 observable behavior` invariant を plan.md の step 設計へどう落とすか
- `step gate / milestone gate / S90 / S99` の置き方
- review / QA / docs / final diff を TDD cycle の外に置く原則

入れないこと
- テストフレームワーク固有説明
- 言語別テクニック
- cadence policy の再定義

重要な注意
- cadence policy の正本は `workflow_issue.md` に残す
- `step = 1 observable behavior` invariant も `workflow_issue.md` が所有する
- `phase_plan_issue.md` は、それらを `plan.md` にどう埋め込むかだけを書く
- `step gate` と `milestone gate` の最小例は `phase_plan_issue.md` に置く

### 5. `workflow_issue.md`
目的
- issue execution policy の正本として残す

残すべきこと
- `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- `1 step = 1 observable behavior`
- final diff review quality gate
- docs impact step

追加するとよいこと
- `iteration = 1 tdd cycle` の ownership は持たず、「issue plan は TDD cycle を plan に埋め込む」とだけリンクで示す
- [phase_plan_issue.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md) への強い導線

### 6. `workflow_initiative.md` / `workflow_epic.md`
目的
- lifecycle / governance に集中させる

追加するとよいこと
- 関連欄に `phase_plan_initiative.md` / `phase_plan_epic.md` を追加
- plan authoring は scope 別 phase playbook を見る導線を入れる
- execution policy は持たないことを暗黙で維持する

### 7. `issue/plan.md`
目的
- TDD を構造として埋め込む

変えるべきこと
- `実行ルール（全ステップ共通）` に次を入れる
  - iteration ごとに failing test は 1 本
  - iteration は `Red -> Green -> Refactor` で閉じる
  - Green は最小実装
  - Refactor は green 維持が前提
- `block` を `optional concern group` として明示する
- `iteration` を `1 tdd cycle` と明示する
- template 例で block の任意性が分かるようにする
  - 単純な step では `B1` は最小 wrapper 1 個でよい
  - 複雑な step だけ block を複数に分ける

推奨形

```md
### S01 — <observable behavior>
- target:
  - ...

#### B1 — <optional concern group>
- purpose:
  - ...

##### I1 — <tdd cycle>
- slice goal:
  - ...

###### Red
- failing test:
  - ...

###### Green
- minimum implementation:
  - ...

###### Refactor
- cleanup target:
  - ...

#### step gate
- review:
  - ...
- report update:
  - ...
- commit decision:
  - ...
```

### 8. `initiative/plan.md` / `epic/plan.md`
目的
- shared 変更に合わせて節名と contract 用語だけを調整する

必要な修正
- `final exit contract` を明示
- `readiness contract` の用語を shared terminology に揃える
- scope 別 phase playbook と齟齬が出ないように節名を最小調整する

### 9. `guide.md` / `README.md`
目的
- 入口導線を迷わせない

追加するとよいこと
- plan だけは `shared + scope-specific` の二段参照だと明記する
- issue plan は TDD ベースの execution contract を持つ、と 1 行で示す

## 実装順
1. `phase_plan_initiative.md` `phase_plan_epic.md` `phase_plan_issue.md` を追加する
2. `workflow_*.md` に scope 別 plan playbook への導線を追加する
3. `issue/plan.md` を TDD 構造に合わせて更新する
4. `initiative/plan.md` `epic/plan.md` を shared terminology に揃える
5. `phase_plan.md` を最後に縮退する
6. `guide.md` と `README.md` を最小更新する

## なぜこの順か
- shared を先に縮退すると、一時的に issue 側の plan 契約が痩せる
- 先に scope-specific playbook を追加してから shared を薄くする方が安全である

## ベストプラクティス
- 1 つの論点を 1 箇所にだけ書く
- issue TDD cadence の正本は `workflow_issue.md` に置き続ける
- issue の step 境界 invariant も `workflow_issue.md` に置き続ける
- `phase_plan_issue.md` は cadence や invariant の再説明ではなく plan への落とし込みに集中する
- template は schema に徹しつつ、`block` の任意性と `iteration` の TDD cycle 性だけは明示する
- review / QA / docs / final diff は TDD cycle の外側に置く

## fixed examples
- `step gate` と `milestone gate` の最小例は `phase_plan_issue.md` に置く
- `issue/plan.md` は placeholder を保ち、単純版の最小サンプルだけを持つ
- 複雑版の説明は template ではなく playbook 側で扱う

## 推奨結論
- この修正案を採用し、次工程では production docs の実反映に進むのが最善である。
- とくに issue 側は、TDD を「実装時の心構え」ではなく **計画書の構造に埋め込まれた実行契約** として扱うべきである。
