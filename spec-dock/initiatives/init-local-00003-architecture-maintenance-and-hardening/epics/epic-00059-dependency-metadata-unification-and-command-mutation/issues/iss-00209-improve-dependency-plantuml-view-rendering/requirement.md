---
種別: 要件定義書（Issue）
ID: "iss-00209"
タイトル: "Improve dependency PlantUML view rendering"
関連GitHub: ["#209"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["epic-00059", "init-local-00003"]
---

# iss-00209 Improve dependency PlantUML view rendering — 要件定義

## 目的
- GitHub lifecycle state と依存関係上の blocker 判定を分離し、high-level dependency の readiness 判定と PlantUML 表示を同じ解釈で一貫させる。
- `deps check` / `active set` / `issue start` / `.agent/deps-issues.json` / `deps-issues.puml` / `deps-raw.puml` が、GitHub open の high-level node でも dependency 上は satisfied になりうることを正しく扱えるようにする。
- 完了済み issue や resolved high-level dependency で図が溢れないようにし、依存関係図を「今実施できるもの / 今ブロックしているもの」を読むための作業面に戻す。

## 背景・現状
- `iss-00207` により、empty open epic / initiative などの high-level dependency を node blocker として扱う基礎ロジックは修復された。
- その後の realistic manual test で、ready / blocked / done / satisfied context が混在する状態は確認できた。
- しかし PlantUML 表示には、完了済み issue、closed / done high-level node、satisfied dependency context が残りやすく、実作業に必要な dependency view が読みづらい。
- さらに議論の結果、これは表示だけではなく blocker 判定の問題でもあることが分かった。
- GitHub issue の `open` / `closed` は lifecycle fact であり、SpecDock dependency readiness 上の `blocking` / `satisfied` と同義ではない。
- 特に、GitHub open の epic / initiative でも配下 issue が存在し、それらが全て done / closed であれば、その high-level dependency は blocker ではなく satisfied と扱う必要がある。

## Source-Grounded Clarification
- 採用済み interview:
  - `discussions/20260619t002903z-interview-dependency-plantuml-closed-node-policy.md`
  - `discussions/20260619t010926z-interview-dependency-disposition-scope-amendment.md`
- 採用済み research:
  - `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md`
- 採用判断:
  - Option A を採用し、`iss-00209` は rendering-only ではなく readiness authority と rendering の一体改善として扱う。

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock を使って issue / epic / initiative の依存関係を確認する開発者および AI agent。
- 代表シナリオ:
  - 次に開始可能な issue を `deps check` / `active set` / `issue start` で判断する。
  - `deps-issues.puml` で、今ブロックしている issue と high-level dependency を確認する。
  - `deps-raw.puml` で、`.meta.json.depends_on` に保存された raw direct dependency を監査する。

## スコープ
- 必須:
  - `lifecycle_state` と `dependency_disposition` を分離する。
  - high-level dependency target の blocker / satisfied 判定を `dependency_disposition` として表現する。
  - GitHub open かつ descendant issue が 0 件の epic / initiative は引き続き blocker とする。
  - GitHub open かつ descendant issue が存在し、その全てが done / closed の epic / initiative は blocker ではなく satisfied とする。
  - `deps check --json` が high-level dependency disposition を説明できるようにする。
  - `active set` / `issue start` は更新後の readiness authority を消費し、all-done high-level dependency では開始可能、empty open high-level dependency では開始不可にする。
  - `.agent/deps-issues.json` は lifecycle fact と dependency disposition を machine-readable に持つ。
  - `deps-issues.puml` は active readiness / blocker view として、done issue、closed high-level node、GitHub-open all-descendant-done high-level node、satisfied-only edge を active node / active edge として表示しない。
  - `deps-raw.puml` は active raw direct dependency view として、active / blocking / actionable な `.meta.json.depends_on` direct edge を確認できる一方、done issue / closed high-level node / resolved-only high-level context を表示ノイズとして残さない。
  - provider-side docs と dogfooding docs を更新し、GitHub lifecycle と dependency disposition の違いを説明する。
  - focused automated tests と realistic manual test evidence を更新する。
- 禁止:
  - `.meta.json.depends_on` storage format を変更しない。
  - `deps add/remove` の mutation contract を変更しない。
  - GitHub issue lifecycle の close / reopen policy をこの issue で変更しない。
  - 表示都合だけで readiness authority と矛盾する PUML を生成しない。
- 対象外:
  - 新規 GUI / Web UI の追加。
  - `deps-raw-all.puml` など別名の新 artifact 追加。
  - GitHub 上の epic / initiative close 運用ルールの強制。
  - 完全な raw metadata 監査 view の新設。完全監査は `.meta.json.depends_on`、`.agent/index-all.json`、必要に応じた future follow-up で扱う。

## Dependency Disposition Rules
- `dependency_disposition`:
  - `blocking`: high-level dependency が対象 issue の開始を止める。expanded high-level dependency の場合は、high-level container 自体ではなく descendant issue blockers として表現してよい。
  - `satisfied`: high-level dependency は満たされており、対象 issue の開始を止めない。
  - `indeterminate`: high-level dependency の状態が不明であり、fail-closed で扱う。
- `disposition_basis`:
  - `empty_open_container`: child issue が存在せず、lifecycle は open。
  - `empty_unknown_container`: child issue が存在せず、lifecycle は unknown。
  - `lifecycle_closed`: lifecycle が closed。
  - `local_done`: local status が done。
  - `all_descendant_issues_done`: child issue が存在し、全て done / closed。
  - `descendant_issue_open`: child issue に open / ready / blocked issue がある。
  - `descendant_issue_unknown`: child issue に unknown status がある。
- `descendant issue`:
  - epic の場合: full graph 上で `epic_id` がその epic を指す issue。
  - initiative の場合: full graph 上で `initiative_id` がその initiative を指す issue。
  - todo projection ではなく full graph で数える。done issue が todo projection から消えていても descendant issue count には含める。
- `node_blocker`:
  - high-level container 自体が blocker surface になる場合だけ使う。
  - empty / unknown high-level container は `node_blocker` になる。
  - descendant issue が存在する high-level dependency は、unresolved descendant issue を issue-level blockers として表現し、container を `node_blocker` にしない。

## 判定表
| high-level dependency target | lifecycle_state | descendant issue count | descendant issue states | dependency_disposition | blocker surface |
|---|---|---:|---|---|---|
| epic / initiative | open | 0 | N/A | blocking | node_blocker |
| epic / initiative | unknown | 0 | N/A | indeterminate | node_blocker |
| epic / initiative | closed | any | any | satisfied | none |
| epic / initiative | done | any | any | satisfied | none |
| epic / initiative | open | >0 | all done / closed | satisfied | none |
| epic / initiative | open | >0 | any open / ready / blocked | blocking | descendant issue blockers |
| epic / initiative | open | >0 | any unknown | indeterminate | descendant issue unknown |

## 受け入れ条件
- AC-001: Empty open high-level dependency blocks.
  - アクター: developer / agent
  - 前提: target issue depends on a GitHub-open epic or initiative that has no descendant issues in the full graph.
  - 操作: `deps check --json` or `active set` / `issue start`.
  - 期待結果: target is not ready; node blocker is reported with `dependency_disposition=blocking` and `disposition_basis=empty_open_container`.
  - 観測点: JSON output, exit code, active set error, issue start rejection.
- AC-002: GitHub-open all-done high-level dependency is satisfied.
  - アクター: developer / agent
  - 前提: target issue depends on a GitHub-open epic or initiative that has descendant issues in the full graph and every descendant issue is done / closed.
  - 操作: `deps check --json` or `active set` / `issue start`.
  - 期待結果: target is not blocked by that high-level node; satisfied dependency context reports `disposition_basis=all_descendant_issues_done`.
  - 観測点: JSON output, exit code, active set success, issue start success.
- AC-003: Lifecycle and disposition are both visible to machine consumers.
  - アクター: agent
  - 前提: high-level node is GitHub open but dependency satisfied.
  - 操作: read `.agent/deps-issues.json`.
  - 期待結果: payload preserves lifecycle fact and dependency disposition without conflating them.
  - 観測点: `lifecycle_state`, `lifecycle_source`, `dependency_disposition`, `disposition_basis`.
- AC-004: `deps-issues.puml` remains an actionable readiness view.
  - アクター: developer
  - 前提: graph contains done issues, closed high-level nodes, empty open high-level blockers, and GitHub-open all-done high-level dependencies.
  - 操作: render / inspect `deps-issues.puml`.
  - 期待結果: active blockers and executable issues are visible; done issue, closed high-level node, GitHub-open all-descendant-done high-level node, and satisfied-only edge are omitted from the active graph; blocking edges are labeled as `blocks`, not user-facing `raw_direct`.
  - 観測点: PlantUML text and manual visual inspection.
- AC-005: `deps-raw.puml` remains a raw direct dependency view.
  - アクター: developer
  - 前提: `.meta.json.depends_on` contains issue, epic, and initiative direct edges.
  - 操作: render / inspect `deps-raw.puml`.
  - 期待結果: active raw direct edges are represented as `raw_direct`; epic / initiative nodes use package representation; done issue, closed high-level, and resolved-only high-level noise is not carried into the active raw view.
  - 観測点: PlantUML text and manual visual inspection.
- AC-006: Existing storage and mutation contracts remain unchanged.
  - アクター: developer / agent
  - 前提: dependency metadata exists in `.meta.json.depends_on`.
  - 操作: `deps add/remove/check`, `sync`, `validate`.
  - 期待結果: no storage migration or mutation API change is required.
  - 観測点: tests and docs.

## 例外・エッジケース
- EC-001: child issue existence must be based on the full graph, not todo projection.
  - 条件: all descendant issues are done and absent from todo projection.
  - 期待: high-level node is not misclassified as empty open.
  - 観測点: regression test.
- EC-002: unknown child issue status is fail-closed.
  - 条件: high-level dependency has child issues but at least one child status is unknown.
  - 期待: dependency is not silently treated as satisfied.
  - 観測点: domain and application tests.
- EC-003: closed high-level node with no child issues is satisfied.
  - 条件: target issue depends on a GitHub-closed empty epic.
  - 期待: dependency is satisfied and does not block.
  - 観測点: `deps check --json`.
- EC-004: raw dependency audit is not the readiness authority.
  - 条件: `deps-raw.puml` shows a raw direct edge whose dependency is already satisfied.
  - 期待: `deps-issues.json` and `deps check` remain the readiness authority. Complete raw metadata audit remains available from `.meta.json.depends_on` / `.agent/index-all.json`, not from the active `deps-raw.puml` subset.
  - 観測点: docs and generated artifacts.

## 入力→出力例
- EX-001:
  - 入力: `iss-00301 depends_on epic-00202`; `epic-00202` is GitHub open; child issues `iss-00401`, `iss-00402` are done.
  - 出力: `iss-00301` is ready with satisfied dependency `epic-00202`, basis `all_descendant_issues_done`.
- EX-002:
  - 入力: `iss-00301 depends_on epic-00202`; `epic-00202` is GitHub open; it has no child issues.
  - 出力: `iss-00301` is blocked by `epic-00202`, basis `empty_open_container`.

## 用語
- TERM-001: `lifecycle_state`
  - GitHub / local lifecycle fact. It does not alone decide blocker readiness.
- TERM-002: `dependency_disposition`
  - Readiness interpretation for dependency evaluation: `blocking`, `satisfied`, or `indeterminate`.
- TERM-003: `disposition_basis`
  - The reason for dependency disposition, such as `empty_open_container` or `all_descendant_issues_done`.
- TERM-004: `deps-issues`
  - Machine and human readiness / blocker view. It is the default authority for whether an issue is actionable.
- TERM-005: `deps-raw`
  - Active raw direct dependency visualization. It helps inspect current actionable `.meta.json.depends_on` edges but is not the complete metadata audit surface or readiness authority.

## 未確定事項
- none
