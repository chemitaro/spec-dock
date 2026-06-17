---
種別: 要件定義書（Issue）
ID: "iss-00193"
タイトル: "Node Level Dependency Mutation"
関連GitHub: ["#193"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["epic-00059", "init-local-00003"]
---

# iss-00193 Node Level Dependency Mutation — 要件定義（何を、なぜ行うか）

## 目的
- `deps add/remove` の mutation surface を issue node 専用から initiative / epic / issue node 共通へ拡張する。
- 利用者が planning 段階で initiative / epic 間の direct dependency intent を command-first に保存できるようにし、`.meta.json.depends_on` の reader contract と CLI mutation contract のずれを解消する。
- 既存 issue-level dependency graph への還元は維持しつつ、raw node-level graph の self / descendant / cycle を保存前に拒否し、将来 child issue が追加された時点で壊れる invalid state を防ぐ。

## 背景・現状
- 現状の挙動:
  - `infra/deps_reader.py` は initiative / epic / issue の `.meta.json.depends_on` を読み、source node と dependency node の配下 issue set を issue-level dependency graph へ還元できる。
  - `reference_deps.md` も `.meta.json.depends_on` の raw value 例として initiative / epic / issue ref を扱っている。
  - 一方で、現行 `deps add/remove` の CLI mutation surface は issue node のみを受け付ける。
  - `deps add --from <epic-id> --to <epic-id>` や `deps remove --from <initiative-id> --to <epic-id>` は `unsupported_node_kind` で拒否される。
- 現状の課題:
  - dogfooding では、issue 分割前の planning 段階で initiative / epic 間の依存を先に固定したい場面がある。
  - 現行 CLI では command-first に設定できないため、直接 `.meta.json` を編集する誘惑が生まれる。
  - reader は node-level dependency を解釈できるのに、writer は issue-level に閉じており、docs / runtime / workflow の contract がずれている。
  - 空の epic / initiative に dependency metadata を保存した後、後から child issue を追加した瞬間に循環や self-edge が顕在化する invalid state は保存前に防ぐ必要がある。
- 再現手順:
  1. SpecDock 管理 repo で existing epic 同士を用意する。
  2. `./spec-dock/scripts/spec-dock deps add --from <epic-id> --to <epic-id>` を実行する。
  3. 現行 runtime は `unsupported_node_kind` を返す。
- 観測点:
  - CLI:
    - `spec-dock: error (deps add) from=<epic-id> to=<epic-id> code=unsupported_node_kind`
  - Metadata:
    - source node 直下 `.meta.json.depends_on` が更新されない。
  - Derived artifacts:
    - `sync` 後の dependency projection へ node-level direct dependency が反映されない。
- 情報源:
  - GitHub Issue #193
  - `spec-dock/active/epic/{requirement,design,plan}.md`
  - `spec-dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `discussions/20260617t000620z-research-issue-193-node-dependency-mutation-research.md`
  - `discussions/20260617t000842z-interview-node-dependency-validation-boundary.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - SpecDock を dogfooding する maintainer / coding agent。
  - issue 分割前に上位 scope の依存関係を整理する planning agent。
- 代表シナリオ:
  - `epic-01930` が `epic-01929` に依存することを、epic 配下 issue が揃う前に command で固定する。
  - `init-01926` が foundation 系 epic に依存することを、initiative 直下 `.meta.json.depends_on` に保存する。
  - 後続の `sync` / `deps check` / raw dependency view が、保存済み direct dependency intent を同じ SoT から読める。

## スコープ
- 必須:
  - `deps add --from <initiative|epic|issue> --to <initiative|epic|issue>` を existing node id に対して動作させる。
  - `deps remove --from <initiative|epic|issue> --to <initiative|epic|issue>` を同じ node-level direct edge に対して動作させる。
  - source node 直下 `.meta.json.depends_on` に direct dependency ref を保存し、remove では同じ direct ref を削除する。
  - Duplicate add は healthy graph に限り success/no-op とし、storage 上の重複を発生させない。
  - Remove は direct edge が存在しない場合、既存 contract 通り `edge_not_found` error とする。
  - Mutation 前に current graph / deps graph を fail-closed に検証する。
  - Raw node-level direct dependency graph の self dependency / ancestor dependency / descendant dependency / cycle を保存前に拒否する。
  - Empty epic / initiative など、対象 node 配下に issue がまだ存在しない場合でも、raw node-level validation を通過する valid direct dependency metadata は保存できる。
  - `reference_deps.md`、`workflow_issue.md`、CLI help text、関連 tests を新 contract に合わせる。
  - 既存 issue->issue add/remove behavior を退行させない。
- 禁止:
  - `.meta.json` 直編集を前提にした運用へ戻さない。
  - `deps.json` fallback read/write や auto-migration を再導入しない。
  - Validation を後続 `sync/check` 任せにして、明らかに invalid な raw node-level cycle を保存しない。
  - Existing issue->issue duplicate add / remove not-found / preflight-first contract を緩めない。
- 対象外:
  - Dependency priority / weight / optional dependency などの新しい依存意味論。
  - `deps check` の readiness 判定ロジック自体の再設計。
  - `deps-raw.puml` の新規生成。これは `iss-00192` で扱う。
  - GitHub Issue lifecycle の変更。

## 境界
- 常に行う:
  - Command-first mutation を正本にする。
  - `.meta.json.depends_on` を canonical storage として扱う。
  - Mutation は保存前に current graph validation と candidate edge validation を行う。
  - Raw node-level direct graph と compiled issue-level graph の両方で invalid state を防ぐ。
  - Source node の direct metadata と inherited / compiled edge を区別する。
- 判断が必要:
  - 追加設計で raw node-level validation helper を domain 層へ置くか、infra reader の resolution result を application 層で検査するか。
  - CLI response detail に node kind をどこまで表示するか。
- 行わない:
  - Child issue がまだないことだけを理由に valid parent-level dependency を拒否しない。
  - Inherited-only edge を remove 対象の direct edge とみなさない。
  - Issue-local implementation のついでに dependency visualization の新 artifact を追加しない。

## 非交渉制約
- Same-repo / GitHub-backed identity contract は維持する。
- `.meta.json` 単一 SoT を維持し、legacy `deps.json` dual-read は持たない。
- Mutation write path は atomic write を維持し、partial write を残さない。
- Raw node-level dependency cycle は、配下 issue が空で compiled issue-level graph が空になる場合でも保存前に拒否する。
- Source node が自身の ancestor または descendant に依存する edge は拒否する。
- Candidate edge が compiled issue-level self-edge を生む場合は拒否する。

## 前提
- `deps_reader.py` は initiative / epic / issue node の `.meta.json.depends_on` を読み、issue-level graph へ還元できる。
- Parent Epic `epic-00059` は command-based mutation、preflight-first validation、duplicate add success/no-op、remove not-found error を既に固定している。
- `iss-00192` は raw dependency visualization を扱う別 issue であり、本 issue は mutation contract の拡張に集中する。

## 受け入れ条件
- AC-001:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Existing initiative / epic / issue node がある。
  - 操作:
    - `./spec-dock/scripts/spec-dock deps add --from <initiative|epic|issue> --to <initiative|epic|issue>` を実行する。
  - 期待結果:
    - Valid node-level direct dependency の場合、source node 直下 `.meta.json.depends_on` に target node id が保存される。
    - CLI は `spec-dock: ok (deps add) from=<source-id> to=<target-id> result=updated` を返す。
  - 観測点:
    - CLI stdout / stderr。
    - source `.meta.json.depends_on`。
    - `./spec-dock/scripts/spec-dock validate`。
- AC-002:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Source node 直下 `.meta.json.depends_on` に direct dependency ref が存在する。
  - 操作:
    - `./spec-dock/scripts/spec-dock deps remove --from <source-id> --to <target-id>` を実行する。
  - 期待結果:
    - Matching direct ref が削除される。
    - CLI は `spec-dock: ok (deps remove) from=<source-id> to=<target-id> result=updated` を返す。
  - 観測点:
    - CLI stdout / stderr。
    - source `.meta.json.depends_on`。
- AC-003:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Same direct dependency が既に source node 直下 `.meta.json.depends_on` に存在する。
  - 操作:
    - 同じ edge を `deps add` する。
  - 期待結果:
    - Healthy graph では success/no-op になり、CLI は `result=unchanged` を返す。
    - `depends_on` 配列に重複 ref を保存しない。
    - Post-sync は既存 unchanged contract に従って skip される。
  - 観測点:
    - CLI stdout。
    - source `.meta.json.depends_on` の before / after。
- AC-004:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Source node 直下には direct edge がないが、parent / compiled graph 上は inherited edge が存在する。
  - 操作:
    - `deps remove --from <source-id> --to <target-id>` を実行する。
  - 期待結果:
    - Inherited-only edge は direct edge とみなされず、`edge_not_found` error で no-write になる。
  - 観測点:
    - CLI stderr。
    - source `.meta.json` の before / after。
- AC-005:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Empty epic / initiative など、source または target node 配下に issue がまだ存在しない。
  - 操作:
    - Raw node-level validation を通過する direct dependency を `deps add` する。
  - 期待結果:
    - Direct dependency metadata は保存される。
    - Issue-level expansion が空の場合は既存 warning contract に従い、保存自体は拒否されない。
  - 観測点:
    - source `.meta.json.depends_on`。
    - `deps check` / `sync` warning。
- AC-006:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Candidate edge が raw node-level cycle を作る。
  - 操作:
    - `deps add` を実行する。
  - 期待結果:
    - 配下 issue の有無に関係なく保存前に拒否される。
    - No-write で終了する。
  - 観測点:
    - CLI stderr error code / message。
    - `.meta.json` before / after。
- AC-007:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Candidate edge が self dependency、ancestor dependency、descendant dependency、または compiled issue-level self-edge を生む。
  - 操作:
    - `deps add` を実行する。
  - 期待結果:
    - 保存前に拒否される。
    - No-write で終了する。
  - 観測点:
    - CLI stderr error code / message。
    - `.meta.json` before / after。
- AC-008:
  - アクター:
    - SpecDock maintainer / downstream coding agent。
  - 前提:
    - Existing issue->issue direct dependency use case がある。
  - 操作:
    - 既存の issue->issue `deps add/remove` scenarios を実行する。
  - 期待結果:
    - Existing behavior が退行しない。
    - Duplicate add、remove not-found、preflight validation failure、write failure の既存 contract が維持される。
  - 観測点:
    - Existing regression tests。
- AC-009:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Runtime docs / help を確認する。
  - 操作:
    - `./spec-dock/scripts/spec-dock deps add --help`、`deps remove --help`、`reference_deps.md`、`workflow_issue.md` を読む。
  - 期待結果:
    - initiative / epic / issue node id を受け付ける表現になっている。
    - Raw node-level validation、empty child issue set、duplicate add、remove direct-edge semantics が説明されている。
  - 観測点:
    - CLI help text。
    - provider-side docs。
    - dogfooding mirror inspection。

## 例外・エッジケース
- EC-001:
  - 条件:
    - `epic-a -> epic-b` と `epic-b -> epic-a` が raw node-level cycle になる。
  - 期待:
    - 配下 issue が空でも `deps add` は cycle として拒否する。
  - 観測点:
    - No-write。
    - CLI error。
- EC-002:
  - 条件:
    - `issue-x -> parent epic-a` のように compiled self-edge を生む。
  - 期待:
    - 保存前に拒否する。
  - 観測点:
    - No-write。
    - CLI error。
- EC-003:
  - 条件:
    - `epic-a -> child issue-x` のような descendant dependency。
  - 期待:
    - 保存前に拒否する。
  - 観測点:
    - No-write。
    - CLI error。
- EC-004:
  - 条件:
    - `epic-a -> parent initiative-a` のような ancestor/container dependency。
  - 期待:
    - Source または target 配下 issue が空でも保存前に拒否する。
  - 観測点:
    - No-write。
    - CLI error。
- EC-005:
  - 条件:
    - Existing raw ref が `123` / `"123"` / `owner/repo#123` / canonical GitHub URL で保存されており、command は node id を指定する。
  - 期待:
    - Direct resolution matching により duplicate add は `result=unchanged`、remove は matching raw ref を削除する。
  - 観測点:
    - `.meta.json.depends_on`。
- EC-006:
  - 条件:
    - Current graph が既に壊れている。
  - 期待:
    - Duplicate add / remove not-found / node-kind 判定より先に `preflight_validate_failed` で no-write になる。
  - 観測点:
    - CLI error。
    - `.meta.json` before / after。

## 入力→出力例（必要時）
- EX-001:
  - 入力:
    - `./spec-dock/scripts/spec-dock deps add --from epic-01930 --to epic-01929`
  - 出力:
    - `spec-dock: ok (deps add) from=epic-01930 to=epic-01929 result=updated`
- EX-002:
  - 入力:
    - `./spec-dock/scripts/spec-dock deps add --from epic-01931 --to epic-01929`
  - 出力:
    - source epic `.meta.json.depends_on` に `epic-01929` が保存される。
- EX-003:
  - 入力:
    - `./spec-dock/scripts/spec-dock deps add --from epic-a --to epic-b` 実行後、`./spec-dock/scripts/spec-dock deps add --from epic-b --to epic-a`
  - 出力:
    - 2つ目の add は raw node-level cycle として error / no-write。

## 用語（ドメイン語彙）
- TERM-001:
  - Direct dependency:
    - Source node 直下 `.meta.json.depends_on` に保存された raw dependency intent。
- TERM-002:
  - Raw node-level graph:
    - initiative / epic / issue node をそのまま vertex とし、`.meta.json.depends_on` の direct ref を edge とする graph。
- TERM-003:
  - Compiled issue-level graph:
    - Raw node-level dependency を source / target 配下 issue set に展開した dependency graph。`deps check` や existing readiness consumer が利用する。
- TERM-004:
  - Inherited-only edge:
    - Source node 自身の `.meta.json.depends_on` には存在しないが、parent scope の dependency によって issue-level graph 上に現れる edge。

## 未確定事項
- なし。
- `20260617t000842z-interview-node-dependency-validation-boundary.md` で Option A が user-approved となり、raw node-level cycle は保存前に拒否する方針に確定した。
