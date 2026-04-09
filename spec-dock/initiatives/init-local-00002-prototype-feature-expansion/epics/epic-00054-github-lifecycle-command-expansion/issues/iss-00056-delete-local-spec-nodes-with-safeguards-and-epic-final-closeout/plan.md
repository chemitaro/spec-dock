---
種別: 実装計画書（Issue）
ID: "iss-00056"
タイトル: "Delete Local Spec Nodes With Safeguards And Epic Final Closeout"
関連GitHub: ["#56"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00056 Delete Local Spec Nodes With Safeguards And Epic Final Closeout — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
  - EC-005
  - EC-006
  - EC-007
  - EC-008
  - EC-009
  - EC-010
- 制約:
  - delete is destructive
  - remote close-only
  - recursive opt-in required
  - explicit `--yes` required
  - `--force` is bounded to active/deps conflicts
  - issue56 owns epic final close-out

## マイルストーン一覧
- M1:
  - 対象:
    - delete preflight / selector contract / metadata barrier / remote-close barrier / mutation seam を固定する
  - exit:
    - selector / active/deps/recursive/path-missing/confirmation / metadata-validation / remote-failure と subtree-wide remote-close barrier の扱いが tests で固定される
- M2:
  - 対象:
    - issue target delete を end-to-end で通す
  - exit:
    - issue delete + remote close-only + local mutation assertions が通る
- M3:
  - 対象:
    - parent recursive delete と epic final close-out を完了する
  - exit:
    - subtree delete、docs parity、`validate` / `sync --github`、issue56 report を正本とした epic final close-out evidence が完了する
- M4:
  - 対象:
    - live manual defect remediation と regression re-validation を完了する
  - exit:
    - target `.meta.json` parse failure 時の `delete --json` が structured payload を返し、manual rerun で defect が再現しない

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - upstream / prerequisite / lower-dependency slice から先に step を組む
  - downstream / dependent slice は前提が固まってから置く
  - step ordering notes:
  - S01 で destructive preflight と subtree-wide remote-close barrier と delete seam を固めてからでないと、S02/S03 の実行順が不安定になる
  - S02 は leaf issue delete を先に通し、S03 で parent recursive と epic close-out を載せる
  - live manual defect は close-out 後に見つかったため、既存 S01-S03 の記録は保持したまま S04 で remediation と rerun を積み増す
  - S90/S99 は issue56 自身と epic final close-out の両方を閉じるため必須

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - delete preflight が selector/active/deps/recursive/path-missing/confirmation/metadata-validation/remote-failure を制御し、subtree-wide remote-close barrier を含む mutation 前安全境界を固定する
  - closes:
    - EC-001
    - EC-002
    - EC-003
    - EC-004
    - EC-005
    - EC-006
    - EC-007
    - EC-008
    - EC-009
  - review gate:
    - RG1
    - QG1
    - SG1
- S02:
  - 観測可能な振る舞い:
    - issue target delete が remote close-only と local directory removal を一貫して実行できる
  - closes:
    - AC-001
  - review gate:
    - RG2
    - QG2
    - SG2
- S03:
  - 観測可能な振る舞い:
    - parent recursive delete と partial failure handling と epic final close-out gate が issue56 の中で完結する
  - closes:
    - AC-002
    - AC-003
    - EC-010
    - 制約一式
  - review gate:
    - RG3
    - QG3
    - SG3
- S04:
  - 観測可能な振る舞い:
    - target-local metadata edge でも `delete --json` の structured contract が崩れず、manual rerun で live defect が解消される
  - closes:
    - live-manual-defect-01
  - review gate:
    - RG4
    - QG4
    - SG4

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S03
- AC-003 -> S03
- live-manual-defect-01 -> S04
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01
- EC-005 -> S01
- EC-006 -> S01
- EC-007 -> S01
- EC-008 -> S01
- EC-009 -> S01
- EC-010 -> S03
- 制約(delete is destructive / remote close-only / recursive opt-in required / issue56 owns epic final close-out) -> S01, S02, S03
- 制約(delete is destructive / remote close-only / recursive opt-in required / explicit `--yes` required / `--force` is bounded to active/deps conflicts / issue56 owns epic final close-out) -> S01, S02, S03

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S01 完了後
  - scope:
    - selector contract / preflight / guardrail / explicit `--yes` / bounded `--force` / subtree-wide metadata barrier / subtree-wide remote-close barrier / delete seam / active snapshot strategy
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S01 完了後
  - scope:
    - selector/active/deps/recursive/path-missing/confirmation/metadata-validation/remote-failure coverage と barrier-before-delete coverage
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - S01 完了後
  - scope:
    - delete boundary / selector contract / explicit `--yes` / bounded `--force` / recursive / missing-target / metadata barrier / barrier-before-delete / partial failure の妥当性
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする
- RG2 implementation review:
  - timing:
    - S02 完了後
  - scope:
    - leaf issue delete contract
- QG2 QA review:
  - timing:
    - S02 完了後
  - scope:
    - issue delete end-to-end、remote close-only、filesystem assertions
- SG2 spec review:
  - timing:
    - S02 完了後
  - scope:
    - issue56 が issue target delete を requirement どおりに閉じているか
- RG3 implementation review:
  - timing:
    - S03 完了後
  - scope:
    - parent recursive delete、docs parity、issue56 report を正本とした epic final close-out evidence
- QG3 QA review:
  - timing:
    - S03 完了後
  - scope:
    - subtree delete、partial failure handling、validate/sync evidence、final validation sufficiency
- SG3 spec review:
  - timing:
    - S03 完了後
  - scope:
    - issue56 の final close-out gate が epic-00054 の acceptance を閉じているか
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする
- RG4 implementation review:
  - timing:
    - S04 完了後
  - scope:
    - delete command の target-local metadata parse failure 正規化、CLI wrapper 例外処理、manual defect remediation
- QG4 QA review:
  - timing:
    - S04 完了後
  - scope:
    - `delete --json` target metadata edge regression、manual defect rerun sufficiency
- SG4 spec review:
  - timing:
    - S04 完了後
  - scope:
    - live manual defect が requirement/design の machine-readable contract と整合する形で解消されているか

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

### S01 — delete preflight and safety contract
- target:
  - delete preflight
  - selector contract
  - active/deps/recursive/path-missing/confirmation guardrails
  - subtree metadata validation
  - subtree-wide remote-close barrier
  - active snapshot / restore contract
- design refs:
  - `design.md` の `採用方針 / トレードオフ`
  - `design.md` の `依存関係分析`
  - `design.md` の `インターフェース契約`
- step boundary:
  - actual subtree delete は行わない
  - close command 自体の導入は含めない

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — preflight and delete plan
- purpose:
  - destructive operation 前に全部の guardrail を確定する
- files:
  - `application/contracts.py`
  - `application/ports.py`
  - `application/delete_node.py`
  - `infra/active_store.py`
  - `infra/fs_repo.py`

##### I1 — active/deps/recursive/path-missing guardrails
- slice goal:
  - mutation 前に selector と local guardrail で block すべきケースをすべて弾く
  - staged implementation note として、all-local-guardrails-pass かつ `--yes` 済みの経路は S01 I1 では `confirmation_required` interim placeholder で観測してよい

###### Red
- failing test:
  - selector 未指定 / selector 複数指定
  - malformed `--github-issue`
  - `delete <target> --yes` positional selector wiring
  - `<target>` / `--id` exact-match resolve
  - `--github-issue` normalized resolve
  - ambiguous target
  - unrelated invalid metadata directory is ignored for selector outcome
  - overlapping preflight failures obey requirement precedence
  - active conflict
  - deps conflict
  - subtree-internal dependency edges do not raise dependency conflict
  - missing `--recursive`
  - missing target path
  - missing `--yes`
  - `--force` does not override missing-target / missing `--recursive` / missing `--yes`
- expected failure:
  - preflight contract 未実装

###### Green
- minimum implementation:
  - delete request/result
  - selector normalization / resolver
  - preflight resolver
  - status-specific JSON field matrix / exit-code mapping
  - missing-target error payload contract
  - confirmation-required error payload contract
  - bounded `--force` contract
  - interim placeholder としての preflight-ready path
- pass condition:
  - selector / guardrail / status payload / exit-code tests が通る

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

##### I2 — remote-close barrier and snapshot strategy
- slice goal:
  - subtree の metadata validation と remote close 全成功を local delete 開始条件にし、failure 時に local delete を 0 件に保つ

###### Red
- failing test:
  - would-match target invalid metadata -> `metadata_validation_failed`
  - subtree-wide invalid metadata aggregation with empty remote buckets
  - subtree remote-close-set derivation
  - duplicate linkage dedupe
  - already-closed remote issue noop bucket
  - all required remote closes succeed before first local delete
  - remote close failure aborts local delete
  - active snapshot restore on failure
- expected failure:
  - barrier-before-delete contract 未実装

###### Green
- minimum implementation:
  - subtree metadata validator
  - close target set derivation
  - canonical remote issue identifier dedupe / ordering
  - all-success barrier
  - failure abort path with local delete started count = 0
  - active snapshot/restore path
- pass condition:
  - metadata / barrier / remote failure / snapshot tests が通る

###### Refactor
- 目的:
  - preflight と mutation の責務分離を明確にする
- guardrail:
  - issue delete / parent delete surfaceを先取りしない

#### step gate
- review:
  - RG1 / SG1
- expected tests:
  - selector / preflight precedence / status payload / exit-code / metadata validation / remote failure / snapshot tests
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — issue target delete end-to-end
- target:
  - issue delete command path
  - remote close-only
  - local leaf directory removal
  - issue-target partial-failure handling after local delete
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `変更計画`
  - `design.md` の `テスト戦略`
- step boundary:
  - parent recursive delete は含めない

#### B1 — command surface wiring
- purpose:
  - issue target delete を top-level command として通す
- files:
  - `cli/parser.py`
  - `cli/registry.py`
  - `commands/delete.py`
  - `presentation/cli_text.py`

##### I1 — issue delete success path
- slice goal:
  - issue target delete が explicit `--yes` 下で remote close-only と local delete を一貫して実行する
  - issue target の post-delete active repair failure も structured partial-failure として観測できる

###### Red
- failing test:
  - `delete iss-00056 --yes`
  - `delete --id iss-00056 --yes`
  - `delete --github-issue 56 --yes`
  - `delete --id iss-00056 --recursive --yes` is accepted no-op on recursive flag
  - `--json` success payload field matrix and ordering
- expected failure:
  - command surface / renderer 未実装

###### Green
- minimum implementation:
  - delete command wiring
  - issue delete path
  - `--json` success/failure renderer
- pass condition:
  - issue delete integration + success-payload tests が通る

###### Refactor
- 目的:
  - leaf issue path を parent recursive path から分離して保つ
- guardrail:
  - subtree delete logicをこの step に混ぜない

#### step gate
- review:
  - RG2 / SG2
- expected tests:
  - issue delete integration
  - remote close-only assertions
  - issue-target remote close failure keeps local tree unchanged
  - filesystem assertions
  - `--json` payload assertions
  - `local_delete_partial_failure` payload / exit-code assertions
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S03 — parent recursive delete and epic final close-out
- target:
  - parent recursive delete
  - docs parity
  - epic final review / final validation / close-out
- design refs:
  - `design.md` の `採用方針 / トレードオフ`
  - `design.md` の `要件 / 例外 -> verification mapping`
- step boundary:
  - issue55 を再実装しない
  - issue56 自身の evidence で epic-00054 を閉じる

#### B1 — parent recursive delete
- purpose:
  - epic / initiative subtree を explicit recursive opt-in で削除する
- files:
  - delete command implementation
  - affected tests

##### I1 — subtree delete success path
- slice goal:
  - parent recursive delete が explicit `--yes --recursive` 下で subtree-linked issues を close-only で扱い、all-success barrier 後に deepest-first で local subtree を消す

###### Red
- failing test:
  - `delete --id epic-00054 --recursive --yes`
  - `delete --id init-local-00002 --recursive --yes`
  - childless epic/initiative still requires `--recursive`
  - subtree delete preserves deepest-first / same-depth lexical delete ordering
  - recursive delete with subtree-internal-only dependency edges does not raise dependency conflict
  - no local delete starts before subtree remote-close barrier completes
  - local delete partial failure payload after remote close success
  - dependency scrub failure is reported as `local_delete_partial_failure`
- expected failure:
  - subtree plan / execution 未実装

###### Green
- minimum implementation:
  - recursive subtree resolve
  - deepest-first delete
  - partial failure result / active restore / dependency scrub handling
- pass condition:
  - subtree delete integration tests が通る

###### Refactor
- 目的:
  - subtree planning と execution の読みやすさを保つ
- guardrail:
  - force / recursive / close-only の意味を変えない

#### B2 — epic final close-out
- purpose:
  - issue56 自身で epic-00054 の final evidence をまとめる
- files:
  - provider / dogfooding docs
  - epic report / issue report
  - affected tests

##### I1 — final validation and spec close-out
- slice goal:
  - issue55 prerequisite evidence、docs parity、`validate`、`sync --github`、final spec review を issue56 の `report.md` にまとめ、その gate を満たしたときだけ epic-00054 close-out を行う

###### Red
- failing test:
  - issue55 prerequisite evidence is missing
  - docs parity / final validation gap
- expected failure:
  - final close-out evidence 不足

###### Green
- minimum implementation:
  - issue55 requirement/design/plan pass と issue55 implementation/QA/spec-review evidence の確認 checklist
  - docs refresh
  - final validation evidence
  - final spec review input 整備
  - epic close-out gate checklist
- pass condition:
  - AC-003 と issue55 prerequisite gate の evidence が揃う

###### Refactor
- 目的:
  - final close-out artifact の authority を一意に保つ
- guardrail:
  - review-only issue を新設しない

#### step gate
- review:
  - RG3 / SG3
- expected tests:
  - subtree delete integration
  - partial failure integration
  - full status payload / exit-code contract
  - docs parity
  - `validate`
  - `sync --github`
- report update:
  - reviewer verdict / test結果 / 修正内容 / final close-out evidence を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S04 — live manual defect remediation and rerun
- target:
  - `delete --json` target-local metadata edge remediation
  - targeted regression tests
  - live manual rerun
- design refs:
  - `design.md` の `インターフェース契約`
  - `design.md` の `preflight / mutation state machine`
- step boundary:
  - 既存 S01-S03 の記録は書き換えない
  - remediation は追補 step として積み増す

#### B1 — structured json remediation
- purpose:
  - target `.meta.json` parse failure でも `delete --json` が plain error text へ逃げないようにする
- files:
  - delete command implementation
  - application seam
  - targeted tests

##### I1 — target-local metadata edge normalization
- slice goal:
  - `node_reader.load_node_records()` の例外を delete 専用に吸収し、target-local metadata edge を `metadata_validation_failed` へ正規化する

###### Red
- failing test:
  - broken target `.meta.json` + `delete --id <target> --yes --json` returns structured JSON
  - same edge with positional `<target>` returns structured JSON
  - unrelated malformed node still does not hijack selector outcome
- expected failure:
  - current live defect (`plain error text`) が再現する

###### Green
- minimum implementation:
  - delete wrapper/application seam で target-local metadata parse failure の fallback normalize
  - existing `metadata_validation_failed` field matrix を再利用
- pass condition:
  - targeted automated regressions が通る

###### Refactor
- 目的:
  - delete 以外の command contract を壊さず、exception-to-result 境界を明確にする
- guardrail:
  - `--json` 時の stdout JSON 1件 contract を維持する

#### B2 — manual rerun and evidence closure
- purpose:
  - live manual defect の再現条件で再テストし、summary/checklist を更新する
- files:
  - manual-tests reports
  - issue report

##### I1 — targeted manual rerun
- slice goal:
  - mt-08 を中心に live rerun を行い、manual summary を partial-pass から pass へ更新する

###### Red
- failing test:
  - existing manual evidence で defect-1 が再現済み
- expected failure:
  - old summary remains `partial-pass`

###### Green
- minimum implementation:
  - targeted live rerun
  - execution-log/checklist/summary 更新
- pass condition:
  - mt-08 が pass になり、critical scenarios を含む overall verdict が pass になる

###### Refactor
- 目的:
  - manual defect report と code change の traceability を残す
- guardrail:
  - manual evidence path を固定し、previous run との差分が読める状態にする

#### step gate
- review:
  - RG4 / QG4 / SG4
- expected tests:
  - targeted delete metadata-edge regression
  - affected delete command runtime tests
  - live manual rerun (`mt-08`, 必要なら related scenarios)
- report update:
  - reviewer verdict / manual rerun結果 / defect closure を `./spec-dock/active/issue/report.md` に追記する
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - delete contract、explicit `--yes`、bounded `--force`、recursive safety wording、missing-target fatal error、remote close-only、barrier-before-delete、epic final close-out evidence を provider / dogfooding docs に反映する

### S99 — final diff review quality gate
- branch diff scope:
  - issue56 の delete command / tests / docs / epic final close-out evidence 一式
- required validation:
  - issue56 targeted tests
  - full status payload / exit-code contract
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
- reviewer approvals:
  - RG3 pass
  - QG3 pass
  - SG3 pass
- report update:
  - final diff review verdict / closing evidence / issue55 prerequisite gate evidence / epic close-out gate evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- なし:
  - issue56 は local delete と epic final close-out を同一 issue で閉じる

## final exit contract
- AC/EC 達成:
  - AC-001 / AC-002 / AC-003 / EC-001 / EC-002 / EC-003 / EC-004 / EC-005 / EC-006 / EC-007 / EC-008 / EC-009 / EC-010 が tests / docs / validation evidence で観測可能
- docs impact resolved:
  - delete / selector contract / explicit `--yes` / bounded `--force` / recursive / remote close-only / metadata barrier / partial failure / final close-out wording が docs で一貫している
- final diff approved:
  - RG / QG / SG がすべて pass し、S99 final diff review が承認されている
