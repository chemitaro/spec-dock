---
種別: 要件定義書（Issue）
ID: "iss-00235"
タイトル: "Repair high level dependency source projection"
関連GitHub: ["#235"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-26"
親: ["epic-00059", "init-local-00003"]
---

# iss-00235 Repair high level dependency source projection — 要件定義（何を、なぜ行うか）

## 目的
- Initiative / epic 自体が direct `depends_on` を持つ場合に、その依存が `deps check` と sync artifact から消えないようにする。
- `.meta.json.depends_on` に保存済みの high-level source dependency が issue-level projection で落ち、未解決依存があるのに `ready: true` と見える false-ready を防ぐ。
- Raw metadata audit と issue readiness projection の責務を分け、実装者・agent・ユーザーが保存済み raw dependency と readiness blocker をそれぞれ確認できるようにする。

## 背景・現状
- GitHub issue #235 では、`deps add --from init-01926 --to epic-01937` などの操作が `result=updated` となり、source `.meta.json.depends_on` に direct dependency が保存された。
- しかし `deps check --id init-01926 --github --json` は `ready: true`、`effective_depends_on: []`、`dependency_contexts: []` を返し、保存済み依存を確認できなかった。
- 手動再現でも、empty high-level source `init-00001` が target epic `epic-00002` に依存する raw metadata を持つ状態で、`deps check --id init-00001 --no-github --json` は empty dependency result を返した。
- 根本原因の調査は `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md` に記録済み。
- 以前試した実装は方式に問題があったため破棄し、本 issue は SpecDock の issue planning / execution workflow に沿って requirement / design / plan を再作成してから実装する。

## スコープ
- 必須:
  - High-level source node (`initiative` / `epic`) 自体の direct `depends_on` を `deps check --id <initiative|epic> --json` で機械可読に確認できる。
  - High-level source node の direct dependency が未解決の場合、`deps check` は `ready: false` または同等の machine-readable non-ready status を返す。
  - `sync` 後の `.agent/index-all.json` で、保存済み raw direct dependency を `nodes[<source>].depends_on` と `nodes[<target>].type` の join により機械可読に監査できる。
  - Empty high-level source と non-empty high-level source の両方で、source node 自体の raw direct dependency が失われない。
  - Satisfied / done / closed dependency であっても、complete raw audit から保存済み raw edge が消えない。
  - Existing issue source -> high-level target readiness behavior を維持する。
  - Regression tests は `--no-github` で再現でき、GitHub live state に依存しない。
- 禁止:
  - Synthetic / fake issue を作って high-level source dependency を表現する。
  - `.meta.json.depends_on` の storage format を変更する。
  - `deps-issues.json` を complete raw node graph dump に変更する。
  - `effective_depends_on` の既存 issue-level readiness 意味を曖昧にする。
  - GitHub live mutation や external product repo 変更を行う。
- 対象外:
  - `deps-raw.puml` を complete raw audit artifact として再設計すること。
  - Legacy `deps.json` の復活。
  - Workflow lifecycle / active checkout semantics の変更。

## 境界
- 常に行う:
  - Provider source of truth under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` を変更する。
  - Runtime behavior と generated artifact contract を focused tests で固定する。
  - `report.md` に workflow authoring / execution evidence を残す。
- 判断が必要:
  - Raw audit を `.agent/index-all.json` のどの schema に置くか。
  - `deps check` JSON で high-level source direct dependencies をどの field / context shape で表すか。
- 行わない:
  - Dogfooding workspace `spec-dock/` の generated runtime 実装を source of truth として直接修正する。
  - `deps-raw.puml` の保証範囲をこの issue で拡大する。

## 非交渉制約
- Raw dependency audit と issue readiness projection は責務を分ける。
- JSON contract の変更は additive / backward-compatible を優先する。
- 既存 `iss-00207` の issue source -> high-level target blocker behavior を regression させない。
- Issue planning は `spec-dock-issue-planning` の actor sequence に従い、requirement / design / plan それぞれ fresh `spec-reviewer` pass を取得する。
- Issue execution は `spec-dock-issue-execution` に従い、1 implementation step ずつ delegated implementation、reviewer pass、commit gate を閉じる。

## 前提
- `.meta.json.depends_on` への保存自体は成功している。
- `deps_reader` は raw node dependency を内部的には読めている。
- 現在の問題は storage ではなく projection / inspection / artifact contract の欠落である。

## 受け入れ条件
- AC-001: `deps check` exposes high-level source direct dependencies
  - アクター: SpecDock CLI user / agent
  - 前提: `init-00001` 自体の `.meta.json.depends_on` が `["epic-00002"]` を持ち、`init-00001` 配下に issue が存在しない。
  - 操作: `./spec-dock/scripts/spec-dock deps check --id init-00001 --no-github --json`
  - 期待結果: JSON output が `init-00001 -> epic-00002` の direct dependency を機械可読に返す。
  - 観測点: `deps check` JSON。
- AC-002: `deps check` does not false-ready unresolved high-level source dependencies
  - アクター: SpecDock CLI user / agent
  - 前提: AC-001 と同じ graph で、target epic が未解決状態。
  - 操作: `./spec-dock/scripts/spec-dock deps check --id init-00001 --no-github --json`
  - 期待結果: JSON output は unresolved direct dependency を blocker または unresolved context として返し、かつ top-level `ready` を `false` にする、または同等の machine-readable non-ready status を返す。
  - 不合格条件: 未解決 direct dependency を表示していても、readiness status が dependency-free / ready と解釈できる状態。
  - 観測点: command exit status / JSON `ready` / dependency context。
- AC-003: Full-history sync artifact exposes raw high-level source edges
  - アクター: Agent / downstream tooling
  - 前提: AC-001 と同じ graph。
  - 操作: `./spec-dock/scripts/spec-dock sync --no-github`
  - 期待結果: `.agent/index-all.json` が `nodes["init-00001"].depends_on=["epic-00002"]` を含み、target kind は `nodes["epic-00002"].type` から取得できる。
  - 不合格条件: `.agent/index-all.json` の source node payload に `depends_on` がなく、別 artifact だけで確認できる状態。
  - 観測点: generated `.agent/index-all.json`。
- AC-004: Existing issue readiness behavior remains intact
  - アクター: SpecDock CLI user / agent
  - 前提: issue source が high-level target に依存する既存 scenarios。
  - 操作: existing focused domain / infra / CLI runtime tests。
  - 期待結果: issue-level blockers / node blockers / satisfied dependencies の既存 semantics が regression しない。
  - 観測点: `tests/unit/domain/test_deps.py`, `tests/unit/infra/test_deps_reader_topology.py`, `tests/cli_runtime/test_deps.py`, `tests/cli_runtime/test_sync.py`。

## 例外・エッジケース
- EC-001: Empty high-level source
  - 条件: Source initiative / epic に descendant issue がない。
  - 期待: Direct dependency が inspectable で、silent `ready: true` empty result にならない。
  - 観測点: `deps check --json`, full-history artifact。
- EC-002: Non-empty high-level source
  - 条件: Source initiative / epic に descendant issue がある。
  - 期待: Parent node 自体の raw direct dependency と descendant issue readiness projection が混同されない。
  - 観測点: `deps check --json`, existing readiness fields。
- EC-003: Satisfied / done / closed target
  - 条件: Target dependency が readiness 上は satisfied。
  - 期待: Active blockers からは外れても、complete raw audit からは消えない。
  - 観測点: full-history raw dependency artifact。
- EC-004: Existing issue-source high-level target
  - 条件: Issue が empty/open/closed high-level target に依存する。
  - 期待: `iss-00207` で固定した node blocker / satisfied dependency semantics が維持される。
  - 観測点: existing domain / infra / CLI tests。

## 用語（ドメイン語彙）
- Raw node dependency:
  - `.meta.json.depends_on` に保存される direct node-to-node dependency。
- Issue readiness dependency:
  - Issue を source として評価する blockers / satisfied dependencies / node blockers。
- High-level source:
  - `initiative` または `epic` 自体が dependency source になる状態。
- Complete raw audit:
  - Active blocker か satisfied かに関係なく、保存された raw node dependency を machine-readable に確認できる artifact。
- False-ready:
  - 保存済み未解決 dependency があるにもかかわらず、`deps check` が依存なしの `ready: true` を返す状態。

## 未確定事項
- なし。Raw audit の具体 schema と `deps check` JSON の field / context shape は design で決める。
