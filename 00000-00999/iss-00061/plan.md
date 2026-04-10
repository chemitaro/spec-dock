---
種別: 実装計画書（Issue）
ID: "iss-00061"
タイトル: "Dependency mutation command contract"
関連GitHub: ["#61"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00061 Dependency mutation command contract — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
- 制約:
  - current graph validation 優先
  - remove not-found = error
  - duplicate add は healthy graph 時のみ `result=unchanged`
  - `.meta.json` only
  - no partial write

## マイルストーン一覧
- M1 command contract skeleton:
  - 対象:
    - parser / handler / request-result / renderer / wrapper tests
  - exit:
    - `deps add/remove` が CLI で受理され、success/error contract の骨格が test で固定されている。
- M2 mutation behavior:
  - 対象:
    - application / domain / infra write path / integration fixtures
  - exit:
    - add updated、duplicate unchanged、remove updated、not-found/current-graph-invalid error が integration で通る。
- M3 closure:
  - 対象:
    - docs impact、targeted mutation verification、final diff review、rollback 観点確認
  - exit:
    - required tests が通り、T2 scope の closing evidence が揃っている。

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する。
- sequencing rule:
  - parser だけ先に足しても write/validation order が不明だと contract を固定できないため、application/domain contract と integration test を先に置く。
  - duplicate-edge semantics は current graph validation 順序に依存するため、no-op success より先に preflight error を固定する。
  - remove not-found と non-issue node error は current graph preflight 後の observable behavior として後段で閉じる。
- step ordering notes:
  - S01 が add updated の基礎 contract を固定する。
  - S02 が duplicate add と current graph validation 順序を固定する。
  - S03 が remove success path を閉じる。
  - S04 が remove preflight-first / non-issue node / fail-closed error family と no-write guarantee を閉じる。

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `deps add` が valid edge を追加し、`result=updated` success を返す。
  - closes:
    - AC-001
  - review gate:
    - parser/handler/application/request-result/write path の整合レビュー
- S02:
  - 観測可能な振る舞い:
    - healthy graph 上の duplicate `deps add` が `result=unchanged` success になり、current graph invalid 時はその前に fail-closed error になる。
  - closes:
    - AC-002
    - EC-001
  - review gate:
    - validation order / non-dup invariant レビュー
- S03:
  - 観測可能な振る舞い:
    - healthy current graph かつ existing issue->issue edge に対して `deps remove` が `result=updated` success を返す。
  - closes:
    - AC-003
  - review gate:
    - remove write path / renderer レビュー
- S04:
  - 観測可能な振る舞い:
    - remove not-found、non-issue node input、invalid add request、parser error が deterministic な error/no-write として返る。
  - closes:
    - AC-004
    - EC-002
    - EC-003
    - EC-004
    - EC-005
  - review gate:
    - error contract / exit code / no-write guarantee レビュー

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S04
- EC-001 -> S02
- EC-002 -> S04
- EC-003 -> S04
- EC-004 -> S04
- EC-005 -> S04

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - 各 step の Green/Refactor 後
  - scope:
    - validation order、layering、CLI contract、write path
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする。
- QG1 QA review:
  - timing:
    - S02 完了時と S04 完了時
  - scope:
    - integration fixture の妥当性、stderr/stdout separation、exit code、no-write
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする。
- SG1 spec review:
  - timing:
    - S90 と S99
  - scope:
    - command reference / issue docs / rollback 記述 / closing evidence
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする。

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。
- no-op の場合のみ `report.md` に理由を残し、commit を省略できる。

## 実装ステップ

### S01 — `deps add` updated success
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `変更計画`
- step boundary:
  - add happy path のみを閉じ、duplicate/no-op や remove error family は扱わない。

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — command skeleton and updated write path
- purpose:
  - parser/handler/request-result/write path を最小構成で接続する。
- files:
  - parser / commands / application / infra / presentation / tests

##### I1 — add updated contract
- slice goal:
  - valid edge 追加で exit `0` と `result=updated` を返す。

###### Red
- failing test:
  - `tests/cli_runtime/test_deps.py` に add success integration を追加する。
  - `tests/cli_runtime/test_runtime_deps_s04.py` に wrapper / registry / exit code smoke を追加する。
- expected failure:
  - subcommand 未登録、request type 不在、write path 未実装で失敗する。

###### Green
- minimum implementation:
  - `deps add` parser と typed args を追加する。
  - application use case と `.meta.json` write helper を接続する。
  - success renderer を実装する。
- pass condition:
  - add success integration と wrapper test が通る。

###### Refactor
- 目的:
  - command/application/infra の責務境界を揃える。
- guardrail:
  - add success の観測結果を変えない。
  - delete/sync/validate へ波及させない。

#### step gate
- review:
  - `deps add` の request/result と CLI 出力が既存 command 規約に沿っているか確認する。
- expected tests:
  - `python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04`
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す。
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする。

### S02 — duplicate add no-op with current graph validation first
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_deps.py`
- design refs:
  - `design.md` の `採用方針 / トレードオフ`
  - `design.md` の `要件 / 例外 -> verification mapping`
- step boundary:
  - duplicate add と current graph invalid preflight の順序に限定する。

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — validation order and unchanged contract
- purpose:
  - duplicate edge 判定前に current graph validation を固定する。
- files:
  - application / domain / presentation / tests

##### I1 — duplicate unchanged on healthy graph
- slice goal:
  - healthy graph で同一 add を再実行すると `result=unchanged` を返す。

###### Red
- failing test:
  - duplicate add の success/no-op と storage non-dup invariant を追加する。
- expected failure:
  - duplicate edge が error になるか、重複保存される。

###### Green
- minimum implementation:
  - duplicate 判定と `unchanged` result を追加する。
- pass condition:
  - duplicate add integration が通る。

###### Refactor
- 目的:
  - duplicate 判定を domain helper に寄せ、application は順序制御に集中する。
- guardrail:
  - `result=unchanged` と non-dup invariant を崩さない。

##### I2 — current graph invalid beats duplicate add
- slice goal:
  - graph 破損時は duplicate/no-op に進まず error にする。

###### Red
- failing test:
  - broken graph fixture で duplicate add 実行時に preflight error を期待する test を追加する。
- expected failure:
  - `unchanged` success に流れる、または requested mutation validation が先に走る。

###### Green
- minimum implementation:
  - current graph preflight を requested mutation 判定より前に実行する。
- pass condition:
  - broken graph fixture test が通る。

###### Refactor
- 目的:
  - preflight と requested mutation validation の責務を分離する。
- guardrail:
  - error code/message の観測点を変えない。

#### step gate
- review:
  - validation order と duplicate-edge invariant が requirement と一致しているか確認する。
- expected tests:
  - `python -m unittest tests.cli_runtime.test_deps`
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す。
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする。

### S03 — `deps remove` updated success
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `テスト戦略`
- step boundary:
  - existing edge remove success のみを閉じ、preflight-first error family は S04 で閉じる。

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — remove updated path
- purpose:
  - healthy graph 上の existing issue->issue edge に対する remove command から write path までを success path で閉じる。
- files:
  - commands / application / infra / presentation / tests

##### I1 — remove updated
- slice goal:
  - existing edge を削除し `result=updated` を返す。

###### Red
- failing test:
  - remove success integration と wrapper smoke を追加する。
- expected failure:
  - subcommand 不在、または edge 削除が保存に反映されない。

###### Green
- minimum implementation:
  - `deps remove` parser/handler と remove write path を実装する。
- pass condition:
  - remove success tests が通る。

###### Refactor
- 目的:
  - add/remove 共通の mutation orchestration を整理する。
- guardrail:
  - add contract を壊さない。

#### step gate
- review:
  - add/remove の request/result と renderer が対称になっているか確認する。
- expected tests:
  - `python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04`
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す。
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする。

### S04 — fail-closed error family and no-write guarantee
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `リスク / 移行 / ロールバック`
- step boundary:
  - error contract と no-write を閉じ、downstream parity / repo-wide `validate` evidence には進まない。

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — domain and parser errors
- purpose:
  - remove not-found、non-issue node input、invalid add request、parser error を deterministic に返す。
- files:
  - parser / commands / application / domain / presentation / tests

##### I1 — remove not-found error
- slice goal:
  - edge 不在時に `edge_not_found` error を返し、保存しない。

###### Red
- failing test:
  - healthy graph fixture の remove not-found integration と、broken current graph fixture では `edge_not_found` ではなく preflight error を返す test を追加する。
- expected failure:
  - no-op success になる、または保存が走る。

###### Green
- minimum implementation:
  - current graph preflight 後にのみ edge existence check と error renderer を実装する。
- pass condition:
  - remove not-found test と preflight-priority test が通る。

###### Refactor
- 目的:
  - add/remove 共通 error shape を整える。
- guardrail:
  - remove not-found を success に戻さず、preflight-first 順序も崩さない。

##### I2 — non-issue node kind error
- slice goal:
  - existing non-issue node を `from` / `to` に指定した場合に `unsupported_node_kind` error を返す。

###### Red
- failing test:
  - `from` または `to` に epic/initiative node id を指定した integration test を追加する。
- expected failure:
  - edge existence 判定や requested mutation validation に流れる、または error kind が曖昧になる。

###### Green
- minimum implementation:
  - current graph preflight 後に issue node kind 判定を実装し、`unsupported_node_kind` renderer を追加する。
- pass condition:
  - non-issue node input test が通る。

###### Refactor
- 目的:
  - node resolution と node kind validation の責務を整理する。
- guardrail:
  - `unsupported_node_kind` を `edge_not_found` に丸めない。

##### I3 — invalid add request errors
- slice goal:
  - unresolved/self/cycle add を error にする。

###### Red
- failing test:
  - unresolved/self/cycle fixture を追加する。
- expected failure:
  - write が走るか、error kind が不定になる。

###### Green
- minimum implementation:
  - requested mutation validation を実装する。
- pass condition:
  - invalid add tests が通る。

###### Refactor
- 目的:
  - domain validation helper を再利用可能な形に整理する。
- guardrail:
  - current graph preflight 順序を変えない。

##### I4 — parser error contract
- slice goal:
  - required flag 欠落は argparse exit `2` で止まる。

###### Red
- failing test:
  - `--from` / `--to` 欠落 parser test を追加する。
- expected failure:
  - application まで進む、または error contract が既存 argparse とズレる。

###### Green
- minimum implementation:
  - required flag 定義を追加する。
- pass condition:
  - parser error test が通る。

###### Refactor
- 目的:
  - `deps check` と mutation command の parser help を揃える。
- guardrail:
  - parse error exit `2` を維持する。

#### step gate
- review:
  - error code taxonomy、stderr shape、no-write guarantee、rollback 前提を確認する。
- expected tests:
  - `python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04`
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す。
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする。

### nested の使い方
- `step` は常に使う。
- `block` は必要な時だけ分ける。
- `iteration` は必要な数だけ並べる。
- review / QA / docs / final diff は iteration の外に置く。

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets
- 対応:
  - `deps add/remove` を公開 command surface にした場合、runtime command reference と operator-facing docs の差分要否を確定する。
  - 実装 issue で docs 変更が不要なら、その理由を `report.md` に明記して `none` 扱いの判断根拠を残す。

### S99 — final diff review quality gate
- branch diff scope:
  - T2 mutation contract に含まれる parser / commands / application / domain / infra / presentation / tests / docs 差分
- required validation:
  - `python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04`
- reviewer approvals:
  - implementation review pass
  - QA review pass
  - spec review pass
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す。
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う。

## 未確定事項
- 現時点ではなし。

## final exit contract
- AC/EC 達成:
  - AC-001..004 と EC-001..005 を integration / wrapper test と CLI 観測点で説明できる。
  - duplicate add の `result=unchanged` が current graph validation success 後にのみ成立する。
  - remove not-found が error/no-write として固定され、broken current graph では `edge_not_found` より preflight failure が優先される。
  - non-issue node input が `unsupported_node_kind` として固定されている。
- docs impact resolved:
  - command surface 変更に対する docs 更新要否が判断され、必要なら反映、不要なら理由が `report.md` に残っている。
- final diff approved:
  - parser / handler / application / domain / infra / presentation / tests / rollback 観点のレビューが完了している。
  - downstream parity / repo-wide `validate` evidence / hard cutover judgment は `iss-00062` へ委譲されている。
