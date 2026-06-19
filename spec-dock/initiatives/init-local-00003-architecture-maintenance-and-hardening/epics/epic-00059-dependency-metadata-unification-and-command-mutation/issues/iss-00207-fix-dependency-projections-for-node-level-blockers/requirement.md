---
種別: 要件定義書（Issue）
ID: "iss-00207"
タイトル: "Fix dependency projections for node level blockers"
関連GitHub: ["#207"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["epic-00059", "init-local-00003"]
---

# iss-00207 Fix dependency projections for node level blockers — 要件定義（何を、なぜ行うか）

## 目的
- node-level dependency の対象が empty open initiative / epic の場合でも、依存元 issue が誤って ready と判定されないようにする。
- `deps-issues` と `deps-raw` の表示から、node-level blocker、満たされた依存、raw direct dependency の関係を追跡できるようにする。
- `deps check`、`active set`、`sync`、PlantUML artifact、docs の依存解釈を揃え、実運用で安全に次の作業候補を判断できる状態にする。

## 背景・現状
- 現状の挙動:
  - `.meta.json.depends_on` は initiative / epic / issue node id を direct dependency として保存できる。
  - runtime は node-level dependency を issue-level dependency map へ compile する。
  - initiative / epic dependency の issue 展開結果が空の場合、`deps_ref_expanded_to_empty` warning を出すが、readiness blocker として扱わない。
  - `deps-issues.json` は `index.json` の todo issue projection から作られ、done prerequisite や high-level dependency context を含まない。
  - `deps-raw.puml` は raw direct edge を表示するが、initiative / epic は package として白背景のまま表示され、state color は issue rectangle のみに適用される。
- 現状の課題:
  - empty open epic に依存している issue が `ready=true` になり、`active set` / `issue start` の readiness guard として危険である。
  - `deps-issues` に表示される node と edge が少なすぎ、依存が消えたように見える。
  - `deps-raw` では high-level node の状態が見えず、blocked / ready / done / unknown を視覚的に判断しにくい。
  - docs は `deps-raw` を raw 確認用、`deps-issues.*` を readiness / blocker authority と説明しているが、現行 `deps-issues` は node-level blocker を表現できない。
- 再現手順:
  1. `taikyohiyou_project` で `iss-01933` に `depends_on: ["epic-01929", "epic-01930"]` を設定する。
  2. `epic-01929` は closed / children done、`epic-01930` は open / child issue なしの状態にする。
  3. `./spec-dock/scripts/spec-dock deps check --id iss-01933 --no-github --json` を実行する。
  4. `spec-dock/.agent/deps-issues.json`、`spec-dock/deps-issues.puml`、`spec-dock/deps-raw.puml` を確認する。
- 観測点:
  - CLI: `deps check` の `ready`、`blockers`、`warnings`、exit code。
  - JSON: `.agent/index*.json`、`.agent/deps-issues.json` の deps / node / edge payload。
  - PlantUML: `deps-issues.puml` と `deps-raw.puml` の node inclusion、edge、state color、edge label。
  - docs: provider-side `reference_deps.md` / `reference_sync.md` の authority 説明。
- CLI exit code contract:
  - `deps check` は対象 issue が blocked / not ready の場合に非 0 を返す。
  - `deps check` は satisfied dependency や warning-only debug context が残るだけの場合、対象 issue が ready なら 0 を返す。
  - `active set` / `issue start` は `deps check` と同じ readiness interpretation に基づいて blocked issue の開始を止める。
- 情報源:
  - `discussions/20260618t145427z-research-node-level-dependency-projection-failure-analysis.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/{check_deps,set_active,sync_state}.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/{json_state,puml}.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/unit/presentation/test_runtime_sync_s07.py`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock で initiative / epic / issue の依存を設定し、次に実行可能な issue を判断する開発者。
  - `deps check`、`active set`、`sync`、`deps-issues.puml`、`deps-raw.puml` を使う AI agent / operator。
- 代表シナリオ:
  - epic 分解前の open epic を blocker として先に置き、その epic が終わるまで dependent issue を開始しない。
  - done prerequisite を含む依存グラフを確認し、依存が満たされたため ready になっているのか、依存が見落とされているのかを判別する。
  - raw node-level dependency と issue-level readiness projection の違いを PlantUML で確認する。

## スコープ
- 必須:
  - empty open / unknown initiative・epic dependency を readiness blocker として扱う。
  - empty done / closed initiative・epic dependency は readiness blocker から外す。
  - non-empty initiative・epic dependency の既存 issue-level child expansion behavior を維持する。
  - `deps check` JSON / text で node-level blocker を追跡できるようにする。
  - `active set` / `issue start` が node-level blocker を readiness guard として扱えるようにする。
  - `sync` generated artifacts で node-level blocker と visual/debug context を失わない。
  - `deps-issues.json` / `deps-issues.puml` で、open issue の readiness と blocker context を追跡できるようにする。
  - `deps-raw.puml` で initiative / epic participant の state を視覚的に確認できるようにする。
  - provider-side docs と dogfooding mirror docs を更新する。
  - provider-side runtime と shipped scaffold asset の差分を揃える。
  - regression tests を追加または更新し、既存 contract 変更を明示する。
- high-level node status source:
  - GitHub-linked node は、取得できる場合は GitHub state / snapshot enrichment を優先して open / closed を判定する。
  - GitHub enrichment が使えない場合は、local SpecDock metadata と descendant issue state から算出できる状態を使う。
  - open / done / closed のどれにも確定できない high-level node は unknown として fail-closed blocker にする。
- 禁止:
  - `.meta.json.depends_on` storage format を破壊的に変更しない。
  - empty initiative / epic dependency の保存自体を validation error にしない。
  - done issue dependency を readiness blocker として復活させない。
  - raw node-level dependency を手動 metadata 編集前提に戻さない。
  - `deps-raw.puml` を readiness authority にしない。
  - unrelated workflow / GitHub lifecycle / worktree lifecycle の挙動を変更しない。
- 対象外:
  - 新しい Graph UI や Web UI の追加。
  - dependency command の add/remove UX 全体の再設計。
  - GitHub issue の close/open 操作。
  - `taikyohiyou_project` 側の依存データ修正。
  - legacy `deps.json` fallback / migration。

## 境界
- 常に行う:
  - node-level direct dependency は storage 上 first-class edge として扱う。
  - readiness 判定では issue-level blocker と unresolved node-level blocker の両方を考慮する。
  - visual artifact は authority と debug context を区別して表示する。
- 判断が必要:
  - `deps-issues.json` の schema version と互換 field の形。
  - `DepsEvaluation.blockers` に node id を含めるか、`node_blockers` として分離するか。
  - high-level package state を descendant aggregate と direct participant state のどちらで算出するか。
- 行わない:
  - implementation step 中の判断で requirement の scope を広げない。必要なら plan amendment と fresh review に戻す。

## 非交渉制約
- provider-side source of truth は `src/spec_dock/assets/spec_dock/...` である。
- dogfooding workspace `spec-dock/...` は secondary verification / mirror として扱う。
- runtime architecture の layer 境界を守り、reader / domain / application / presentation / docs の責務を混ぜない。
- `deps check` / `active set` / `sync` の readiness interpretation は同じ意味になる必要がある。
- `deps-raw.puml` は raw direct dependency の確認用 artifact であり、readiness authority ではない。
- 既存 tests が固定している todo-only behavior を変更する場合は、contract change としてテスト名・期待値・docs を更新する。
- すべての canonical docs 更新は reviewer gate を通す。

## 前提
- `iss-00207` は `epic-00059 Dependency metadata unification and command mutation` 配下の runtime dependency contract 修正 issue である。
- `discussions/20260618t145427z-research-node-level-dependency-projection-failure-analysis.md` は調査 evidence として採用候補にする。
- parent initiative / epic の planning context は approved authority を持つ active context として扱う。
- 本 issue は修正実装に進める executable issue であり、decision-only issue ではない。

## 受け入れ条件
- AC-001: empty open high-level blocker が readiness を塞ぐ
  - アクター: SpecDock operator / AI agent
  - 前提: open issue が child issue 0 件の open epic または initiative に依存している。
  - 操作: `deps check`、`active set`、または通常の execution entrypoint である `issue start` を実行する。
  - 期待結果: 対象 issue は `ready=false` と判定され、blocker として high-level node id が確認できる。
  - 観測点: CLI JSON / text、exit code、`active set` / `issue start` guard。
- AC-002: empty done high-level dependency は満たされた依存として扱う
  - アクター: SpecDock operator / AI agent
  - 前提: open issue が child issue 0 件の closed / done epic または initiative に依存している。
  - 操作: `deps check` または `sync` を実行する。
  - 期待結果: 対象 issue はその high-level node によって blocked されない。ただし raw/debug context では依存関係を追跡できる。
  - 観測点: CLI JSON / text、`deps-issues.json` または `deps-raw.puml`。
- AC-003: non-empty high-level dependency の既存 child issue expansion を維持する
  - アクター: SpecDock operator / AI agent
  - 前提: open issue が child issue を持つ epic または initiative に依存している。
  - 操作: `deps check` または `sync` を実行する。
  - 期待結果: open child issue は issue-level blocker として扱われ、done child issue は readiness blocker から外れる。
  - 観測点: CLI JSON / text、`index*.json`、`deps-issues.json`。
- AC-004: deps-issues は blocker context を失わない
  - アクター: SpecDock operator / AI agent
  - 前提: open issue が done prerequisite、open prerequisite、または high-level node blocker を含む dependency graph に属する。
  - 操作: `sync` を実行して `.agent/deps-issues.json` と `deps-issues.puml` を確認する。
  - 期待結果: open issue の readiness と blocker/satisfied context を追跡でき、edge や node が todo-only filtering によって誤って消えたように見えない。
  - 観測点: `.agent/deps-issues.json`, `deps-issues.puml`。
- AC-005: deps-raw は high-level node participant の state を表示する
  - アクター: SpecDock operator / AI agent
  - 前提: raw direct dependency に initiative / epic endpoint が含まれる。
  - 操作: `sync` を実行して `deps-raw.puml` を確認する。
  - 期待結果: participant の high-level node が derived visual state を持ち、blocked / ready / done / unknown を判別できる。
  - 観測点: `deps-raw.puml` の package color / legend / edge。
- AC-006: docs と tests が新 contract を固定する
  - アクター: future maintainer / AI agent
  - 前提: node-level dependency contract を変更した実装差分がある。
  - 操作: provider-side docs と regression tests を確認する。
  - 期待結果: empty high-level dependency、node-level blocker、`deps-issues` / `deps-raw` の authority 境界が docs と tests で追跡できる。
  - 観測点: `reference_deps.md`, `reference_sync.md`, tests。

## 例外・エッジケース
- EC-001: unknown high-level dependency
  - 条件: dependency target の initiative / epic status が unknown で、child issue expansion が空。
  - 期待: dependent issue は `guard_reason=unknown` 相当で blocked され、operator が status 不明を追跡できる。
  - 観測点: `deps check --json`, CLI text, `deps-issues.json`。
- EC-002: done child issue dependency
  - 条件: dependency target の epic / initiative に done child issue だけがある。
  - 期待: dependent issue は blocked されない。debug/visual context では満たされた依存として追跡できる。
  - 観測点: `deps check --json`, `deps-issues.puml`, `deps-raw.puml`。
- EC-003: raw node-level cycle
  - 条件: initiative / epic / issue の raw direct dependency が cycle を作る。
  - 期待: 既存の fail-closed validation が維持され、readiness projection へ進まない。
  - 観測点: `validate`, `sync`, `deps check` の error。
- EC-004: docs-only generated artifact confusion
  - 条件: `deps-raw.puml` に色が表示される。
  - 期待: docs は `deps-raw.puml` を readiness authority と誤読させず、raw visual/debug artifact と明記する。
  - 観測点: provider-side docs と generated artifacts。

## 入力→出力例
- EX-001: issue -> empty open epic
  - 入力: `iss-00010.depends_on = ["epic-00020"]`, `epic-00020` は open / child issue 0 件。
  - 出力: `iss-00010 ready=false`, blocker に `epic-00020` を含む。
- EX-002: issue -> empty closed epic
  - 入力: `iss-00010.depends_on = ["epic-00021"]`, `epic-00021` は closed / child issue 0 件。
  - 出力: `iss-00010` は `epic-00021` では blocked されない。raw/debug view は direct edge を表示する。
- EX-003: issue -> epic with open child issue
  - 入力: `iss-00010.depends_on = ["epic-00022"]`, `epic-00022` 配下に `iss-00030 open` がある。
  - 出力: `iss-00010` は `iss-00030` によって blocked される。

## 用語（ドメイン語彙）
- TERM-001: node-level dependency
  - `.meta.json.depends_on` に保存される initiative / epic / issue node 間の direct dependency。
- TERM-002: issue-level compiled dependency
  - high-level node dependency を child issue に展開して得られる issue 間 dependency。
- TERM-003: node-level blocker
  - issue-level expansion では表現できないが、readiness を塞ぐ high-level dependency node。
- TERM-004: deps-issues
  - readiness / blocker authority を人間と agent が確認する generated JSON / PlantUML artifact。
- TERM-005: deps-raw
  - raw direct dependency を確認する generated PlantUML artifact。readiness authority ではない。
- TERM-006: satisfied dependency
  - done / closed のため readiness を塞がないが、debug context として表示価値がある dependency。

## 未確定事項
- 現時点で人間への blocking question はない。
- design phase で `DepsEvaluation.blockers` の互換 field 形、`deps-issues.json` schema version、high-level visual state 集約規則を決める。
