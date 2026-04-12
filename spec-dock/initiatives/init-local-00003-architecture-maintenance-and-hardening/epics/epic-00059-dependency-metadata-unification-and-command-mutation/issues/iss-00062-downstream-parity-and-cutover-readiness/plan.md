---
種別: 実装計画書（Issue）
ID: "iss-00062"
タイトル: "Downstream parity and cutover readiness"
関連GitHub: ["#62"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00062 Downstream parity and cutover readiness — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
  - AC-005
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
  - EC-005
- 制約:
  - `.meta.json` 単一 SoT を崩さない
  - hard cutover judgment は T3 で fixed にする
  - entry 条件は docs 更新 + dogfooding manual fix + `validate` / `sync` evidence
  - `iss-00062/report.md` を cutover evidence の正本にする

## マイルストーン一覧
- M1:
  - 対象:
    - delete scrub 修正と downstream parity regression lock
  - exit:
    - delete / active / sync / validate の targeted tests が `.meta.json` SoT 前提で green になり、shared topology reader 前提が regression として固定される
- M2:
  - 対象:
    - docs / scaffold / report schema / cutover boundary contract 固定
  - exit:
    - `reference_deps.md` / `reference_sync.md` / `workflow_issue.md` の provider-side 正本と dogfooding mirror に SoT / manual fix / evidence owner が反映され、provider templates / init-update coverage が legacy `deps.json` を再seedせず、report fixed key に targeted regression summary を含めて追える
- M3:
  - 対象:
    - checked-in dogfooding data manual fix と cutover evidence 採取
  - exit:
    - `./spec-dock/scripts/spec-dock validate` / `sync` が成功し、`iss-00062/report.md` に judgment fixed が記録される

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
  - `iss-00060/report.md` / `iss-00061/report.md` と provider-side source / focused tests を prerequisite completion の権威ソースとする
- sequencing rule:
  - delete scrub を先に固定し、保存後 graph が壊れないことを保証してから active/sync/validate parity を regression として固める
  - docs / scaffold / report schema は runtime contract が見えた後に固定し、最後に manual fix と command evidence を束ねて judgment を閉じる
- step ordering notes:
  - S01 は S02 の前提になる downstream data integrity を閉じ、post-delete snapshot で `validate` / `sync` / `active set` が deleted node を再観測しないことまで固定する
  - S02 は S03/S04 の validation semantics を決める
  - S03 は S04 の evidence / report 記録形式と scaffold seed boundary を固定する
  - S04 は cutover judgment を実際に fixed にする唯一の step

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - delete 後に dangling dependency を残さず、post-delete validation が `.meta.json` SoT で一致する
  - closes:
    - AC-001
    - EC-001
  - review gate:
    - delete scrub contract と targeted tests が pass
- S02:
  - 観測可能な振る舞い:
    - `active set` / `sync` / `validate` が同一 topology reader 由来の dependency graph を観測する
  - closes:
    - AC-002
    - EC-004
  - review gate:
    - active/sync/validate targeted tests が pass
- S03:
  - 観測可能な振る舞い:
    - docs / scaffold / report schema が hard cutover entry 条件と T3/T4 owner split を正しく案内し、legacy `deps.json` を再seedしない
  - closes:
    - AC-004
    - AC-005
    - EC-003
    - EC-005
  - review gate:
    - docs diff / scaffold diff と report fixed-key contract が reviewer に説明できる
- S04:
  - 観測可能な振る舞い:
    - checked-in dogfooding data manual fix、cutover boundary evidence、`validate` / `sync` 実測、judgment fixed record が揃う
  - closes:
    - AC-003
    - EC-002
  - review gate:
    - entry 条件充足と judgment fixed が `report.md` で追える

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S04
- AC-004 -> S03
- AC-005 -> S03
- EC-001 -> S01
- EC-002 -> S04
- EC-003 -> S03
- EC-004 -> S02
- EC-005 -> S03

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前に pass を取得する
    - S03 完了後に docs / report schema の妥当性を再確認する
  - scope:
    - T3/T4 owner split
    - cutover evidence contract
    - scaffold/template cutover parity
    - step decomposition と verification mapping
- RG1 implementation review:
  - timing:
    - S01 完了後、S02 着手前
    - S02 完了後、S03 着手前
    - S03 完了後、S04 着手前
    - S04 完了後、close / commit 前の final review
  - scope:
    - downstream parity
    - delete scrub contract
    - docs / scaffold / manual-fix boundary
    - no fallback / no dual-read
- QG1 QA review:
  - timing:
    - S02 完了後、S03 着手前
    - S04 完了後、close / commit 前の final review
  - scope:
    - targeted runtime tests
    - cutover boundary tests
    - init/update scaffold regression
    - `validate` / `sync` evidence
- step approval loop:
  - SG1/spec review pass を取得するまで implementation を開始しない
  - S01 後は RG1/code review pass を `report.md` に記録してから S02 を開始する
  - S02 後は RG1/code review pass と QG1/QA review pass を `report.md` に記録してから S03 を開始する
  - S03 後は SG1/spec review re-pass を `report.md` に記録してから S04 を開始する
  - S04 後は final RG1/code review pass と final QG1/QA review pass を `report.md` に記録して close / commit する

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
- cutover entry 条件のどれかが不成立なら `judgment fixed` に進まず、`report.md` に `未完了` または `blocked` と next action を残す。

## 実装ステップ

### S01 — delete scrub parity on `.meta.json`
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - `tests/cli_runtime/test_delete.py`
  - `tests/cli_runtime/test_runtime_delete_s13.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_validate.py`
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - delete が downstream command に対して整合した post-delete graph を残し、その snapshot で `validate` / `sync` / `active set` が deleted node を dependency として観測しないところまでを扱う

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — scrub inbound dependency references
- purpose:
  - 削除対象を参照する node 群の dependency を scrub し、SoT 変更後も dangling edge を残さない
- files:
  - `application/delete_node.py`
  - `infra/fs_repo.py`

##### I1 — fail-closed delete scrub
- slice goal:
  - delete 後に shared topology reader で validate しても整合が崩れない状態を作る

###### Red
- failing test:
  - delete scrub を観測する targeted test
- expected failure:
  - dangling dependency 残存または legacy read path 依存が露出する

###### Green
- minimum implementation:
  - scrub と post-delete validation を `.meta.json` SoT に寄せる
- pass condition:
  - targeted delete tests が pass

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - delete scrub が fail-closed contract を保ち、post-delete downstream command が deleted node を再観測しない
- expected tests:
  - `python -m unittest tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate -v`
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
  - `cutover_entry.targeted_regression_summary.*` に post-delete downstream 検証結果を集約できる形で残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — active/sync/validate parity on shared topology
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_runtime_active_s06.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - `tests/cli_runtime/test_runtime_validate_s02.py`
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - active/sync/validate が同一 topology reader に収束していることを targeted regression で固定し、mismatch が見つかった場合のみ最小修正するところまでを扱う

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — set-active parity
- purpose:
  - readiness と blockers の解釈を `.meta.json` SoT に揃える
- files:
  - `application/set_active.py`
  - `infra/deps_reader.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_runtime_active_s06.py`

##### I1 — ready/blockers consistency
- slice goal:
  - `active set` が same graph を見て判定する

###### Red
- failing test:
  - active parity を観測する targeted test
- expected failure:
  - legacy `deps.json` 依存または graph mismatch が露出する

###### Green
- minimum implementation:
  - shared topology reader 前提に判定を揃える
- pass condition:
  - active targeted tests が pass

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — sync/validate parity
- purpose:
  - sync artifact と validate result が同じ dependency graph を可視化する
- files:
  - `application/sync_state.py`
  - `application/validate_tree.py`
  - `infra/deps_reader.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - `tests/cli_runtime/test_runtime_validate_s02.py`

##### I1 — shared edge/render parity
- slice goal:
  - sync / validate の edge と validation error を一致させる

###### Red
- failing test:
  - sync/validate parity を観測する targeted test
- expected failure:
  - issue edges / blockers / validation message の食い違いが出る

###### Green
- minimum implementation:
  - shared topology reader と `.meta.json` SoT に揃える
- pass condition:
  - sync/validate targeted tests が pass

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - `active set` / `sync` / `validate` が同一 graph を観測している
- expected tests:
  - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_validate_s02 -v`
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S03 — docs, scaffold, and report schema lock
- target:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/deps.json`
  - `src/spec_dock/assets/spec_dock/templates/epic/deps.json`
  - `src/spec_dock/assets/spec_dock/templates/issue/deps.json`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/workflow_issue.md`
  - `tests/test_init_update.py`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - operator docs / scaffold seed / report fixed-key contract を judgment 前に固定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — operator-facing docs update
- purpose:
  - dependency SoT、manual fix、validate/sync evidence の entry 条件を docs に反映する
- files:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/workflow_issue.md`

##### I1 — replace legacy SoT guidance
- slice goal:
  - docs が `.meta.json` SoT と hard cutover policy を案内する

###### Red
- failing test:
  - 該当なし
- expected failure:
  - docs が `deps.json` 前提のまま残る

###### Green
- minimum implementation:
  - `reference_deps.md` に checked-in dogfooding data manual-fix 手順を置く
  - `reference_sync.md` に `validate` / `sync` による cutover verification と evidence 採取手順を置く
  - `workflow_issue.md` に T3/T4 owner split と issue report evidence contract を置く
  - provider docs と dogfooding docs mirror を同じ集合で更新する
- pass condition:
  - reviewer が docs だけで entry 条件、manual fix 手順、T3/T4 owner split、evidence contract を追える

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — scaffold/template legacy seed cleanup
- purpose:
  - fresh scaffold / update path が cutover 後に legacy `deps.json` を再seedしないようにする
- files:
  - `src/spec_dock/assets/spec_dock/templates/initiative/deps.json`
  - `src/spec_dock/assets/spec_dock/templates/epic/deps.json`
  - `src/spec_dock/assets/spec_dock/templates/issue/deps.json`
  - `tests/test_init_update.py`

##### I1 — remove scaffold seed of legacy deps
- slice goal:
  - new init/update path が `.meta.json` only contract と矛盾しない状態にする

###### Red
- failing test:
  - template/init-update で legacy `deps.json` 再seed を観測する regression
- expected failure:
  - new scaffold や update coverage が cutover 後も `deps.json` を要求・生成する

###### Green
- minimum implementation:
  - provider templates と init/update coverage を `.meta.json` only 契約へそろえる
- pass condition:
  - relevant scaffold/update coverage が pass

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B3 — report fixed-key schema lock
- purpose:
  - T3 issue report が cutover evidence の primary owner として機能する形を固定する
- files:
  - `spec-dock/active/issue/report.md`

##### I1 — define evidence keys
- slice goal:
  - S04 で迷わず evidence を記録できる状態にする

###### Red
- failing test:
  - 該当なし
- expected failure:
  - report に必要 evidence が散在し、T3/T4 owner split が曖昧になる

###### Green
- minimum implementation:
  - `report.md` に cutover fixed key 群と targeted regression summary を残す運用を決める
- pass condition:
  - reviewer が `iss-00062` と `iss-00063` の owner split を report shape から説明できる

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - docs / scaffold / report schema が cutover entry 条件と owner split を明示している
- expected tests:
  - docs diff review
  - `python -m unittest tests.test_init_update -v` の relevant scaffold/update coverage
  - report schema review
- report update:
  - reviewer verdict / docs差分 / scaffold差分 / fixed key 一覧 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
  - `report.md` には `cutover_entry.docs_update.paths`、`cutover_entry.docs_update.pass`、`cutover_entry.manual_fix.paths`、`cutover_entry.manual_fix.pass`、`cutover_entry.boundary_tests`、`cutover_entry.validate.command`、`cutover_entry.validate.exit_code`、`cutover_entry.validate.pass`、`cutover_entry.sync.command`、`cutover_entry.sync.exit_code`、`cutover_entry.sync.pass`、`cutover_entry.targeted_regression_summary.scope`、`cutover_entry.targeted_regression_summary.results`、`cutover_entry.targeted_regression_summary.pass`、`cutover_entry.entry_conditions_pass`、`cutover_judgment.owner_issue_id`、`cutover_judgment.owner_role`、`cutover_judgment.verdict`、`cutover_judgment.fixed_at`、`cutover_judgment.follow_up_issue_id`、`cutover_judgment.notes` を固定キーで残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S04 — dogfooding manual fix and cutover judgment fixation
- target:
  - `spec-dock/initiatives/**/.meta.json`
  - `spec-dock/initiatives/**/deps.json`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - checked-in dogfooding data を cutover に追従させ、validate/sync evidence と judgment verdict まで閉じる

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — manual fix checked-in data
- purpose:
  - dogfooding workspace の checked-in dependency data を `.meta.json` SoT へ追従させる
- files:
  - `spec-dock/initiatives/**/.meta.json`
  - `spec-dock/initiatives/**/deps.json`

##### I1 — remove legacy dependency files
- slice goal:
  - checked-in data から legacy `deps.json` を取り除く

###### Red
- failing test:
  - cutover boundary を観測する targeted test または inspection
- expected failure:
  - legacy file 残存により boundary miss が出る

###### Green
- minimum implementation:
  - `.meta.json` へ dependency data を手動移行し、legacy `deps.json` を削除する
- pass condition:
  - manual fix 対象 path が report に列挙できる

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — collect cutover evidence and fix judgment
- purpose:
  - `validate` / `sync` 実測と final readiness verdict を T3 owner として固定する
- files:
  - `spec-dock/active/issue/report.md`
  - relevant changed files

##### I1 — validate and sync evidence
- slice goal:
  - entry 条件を実測で満たしたと示す

###### Red
- failing test:
  - 該当なし
- expected failure:
  - 該当なし

###### Green
- minimum implementation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - boundary tests / docs update / manual fix / targeted regression summary の結果を report に集約する
- pass condition:
  - `entry_conditions_pass=true` 相当の結論と `cutover_judgment.verdict` が report で追える

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - T3 owner として judgment fixed を正当化できる evidence bundle が揃っている
- expected tests:
  - cutover boundary tests
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- report update:
  - reviewer verdict / test結果 / evidence / judgment verdict / no-op 理由を `./spec-dock/active/issue/report.md` に残す
  - `report.md` には S03 で固定した cutover fixed key を実値で埋め、`cutover_entry.targeted_regression_summary.*` に post-delete / parity regression 要約を残し、`cutover_judgment.owner_issue_id=iss-00062`、`cutover_judgment.owner_role=T3 integration owner`、`cutover_judgment.follow_up_issue_id=iss-00063` を明示する
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
  - `reference_deps.md` / `reference_sync.md` / `workflow_issue.md` の provider docs と dogfooding docs mirror の双方で `.meta.json` SoT、manual fix、cutover evidence owner が一致していることを確認する

### S99 — final diff review quality gate
- branch diff scope:
  - runtime downstream parity 変更
  - docs / dogfooding data / report 更新
- required validation:
  - S01 targeted delete tests
  - S02 targeted active/sync/validate tests
  - cutover boundary tests
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- reviewer approvals:
  - implementation review
  - QA review
  - spec review
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- なし:
  - cutover evidence owner と report fixed key はこの plan で固定する

## final exit contract
- AC/EC 達成:
  - AC-001〜AC-004 と EC-001〜EC-004 の evidence が `report.md` で追える
- docs impact resolved:
  - provider docs と dogfooding docs mirror が `.meta.json` SoT / manual fix / owner split を案内している
- judgment fixed:
  - `iss-00062/report.md` に entry 条件充足と `cutover_judgment.verdict` が記録されている
- final diff approved:
  - S99 quality gate を通過している
