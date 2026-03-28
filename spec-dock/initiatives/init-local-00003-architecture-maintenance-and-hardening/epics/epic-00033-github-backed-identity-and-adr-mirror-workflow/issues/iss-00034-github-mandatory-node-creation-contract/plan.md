---
種別: 実装計画書（Issue）
ID: "iss-00034"
タイトル: "GitHub Mandatory Node Creation Contract"
関連GitHub: ["#34"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-28"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00034 GitHub Mandatory Node Creation Contract — 実装計画（Execution Contract）

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
  - local-only success path を残さない
  - canonical repo scope は `origin` basis で fail-closed
  - docs impact は boundary/canonical scope の最小差分に限る

## マイルストーン一覧
- M1:
  - 対象:
    - canonical repo scope resolver と create mode contract の固定
  - exit:
    - resolver failure/reject 条件と create default のテストが先に赤緑で通る
- M2:
  - 対象:
    - validation / docs boundary / final quality gate
  - exit:
    - GitHub mandatory create contract が tests と docs diff で観測できる
- M3:
  - 対象:
    - foreign issue URL import の是正と review log の再整流
  - exit:
    - `iss-local-*` fallback を再導入しない strict reject contract が tests / docs / report で一貫する

## 引き継ぎチェックリスト
- 準備完了:
  - [x] `requirement.md` を最新の corrective scope に更新した
  - [x] `design.md` を latest repo context と strict reject 方針に更新した
  - [x] `plan.md` に追加作業 `M3 / S04` を追記した
  - [x] 分析シート [002-disc-foreign-issue-import-identity-conflict-analysis.md](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00034-github-mandatory-node-creation-contract/discussions/002-disc-foreign-issue-import-identity-conflict-analysis.md) を正本として残した
  - [x] spec review を `pass` まで完了した
  - [x] QA/test strategy review を `pass` まで完了した
  - [x] repo-context consistency review を `pass` まで完了した
- 実装担当者の未着手作業:
  - [x] S01 canonical repo scope resolver
  - [x] S02 GitHub mandatory node creation
  - [x] S03 validation / migration boundary pre-guard
  - [ ] S04 foreign issue URL strict reject correction
  - [ ] S90 docs impact resolution
  - [ ] S99 final diff review quality gate

## 現在の repo 実装状態
- 完了済み:
  - S01:
    - `repo_context.py` に current repo scope 解決があり、`create` 前に fail-closed で参照される
  - S02:
    - `new initiative` / `new epic` / `new issue` は GitHub mandatory で、`local_only` は reject される
  - S03:
    - `domain/validation.py` に GitHub mandatory linkage validation が入っている
- 未完了:
  - S04:
    - foreign issue URL import の strict reject への是正
  - S90:
    - provider / dogfooding docs / report の最小差分更新
  - S99:
    - 最終 diff review と完了証跡の確定

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - canonical repo scope resolver が `origin` basis で fail-closed に動作する
  - closes:
    - EC-001, EC-002
  - review gate:
    - resolver tests と設計整合の確認
- S02:
  - 観測可能な振る舞い:
    - `new initiative` / `new epic` / `new issue` が GitHub mandatory で動作し、local-only create を reject する
  - closes:
    - AC-001, AC-002, EC-003
  - review gate:
    - create contract tests と `.meta.json.github.issue_number` / `.meta.json.github.repo_owner` / `.meta.json.github.repo_name` persistence 確認
- S03:
  - 観測可能な振る舞い:
    - validation / migration boundary の先行ガードが create contract と整合し、single-repo contract と矛盾する exemption を残さない
  - closes:
    - AC-003
  - review gate:
    - validate / boundary docs diff / migration tests の確認
- S04:
  - 観測可能な振る舞い:
    - foreign issue URL import が strict reject に是正され、`iss-local-*` fallback を再導入しない
  - closes:
    - AC-004, EC-004
  - review gate:
    - import reject tests と docs / report の整合確認

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S01 + S02
- AC-003 -> S03
- AC-004 -> S04
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S02
- EC-004 -> S04

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - 各 step gate ごと
  - scope:
    - create contract / resolver / validation の layering と fail-fast policy
- QG1 QA review:
  - timing:
    - S04 後
  - scope:
    - targeted unittest output と reject path coverage
- SG1 spec review:
  - timing:
    - design/plan 固定時と S99 前
  - scope:
    - requirement / design / plan / docs impact の整合

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

## 実装ステップ

### S01 — canonical repo scope resolver becomes fail-closed
- target:
  - `origin` から canonical repo scope を一意解決し、不正な remote 状態を create 前に reject できるようにする
- design refs:
  - `repo_context.py` resolver contract
  - `create_node.py` precheck / plan_node_creation
- step boundary:
  - resolver / normalization / failure reason の追加に限定し、CLI default 切り替えは S02 で行う

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — repo scope resolution
- purpose:
  - `origin` missing / non-GitHub / fetch-push mismatch / configured mismatch / cross-repo reject を実装可能な helper 契約へ落とす
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
  - `tests/cli_runtime/test_runtime_new_s08.py`

##### I1 — resolver failure paths
- slice goal:
  - missing / invalid `origin` が曖昧な `None` ではなく fail-fast condition として観測できる

###### Red
- failing test:
  - `origin` missing / non-GitHub remote / fetch-push mismatch を追加
- expected failure:
  - 現行 resolver が条件を区別できず、期待エラーにならない

###### Green
- minimum implementation:
  - origin fetch/push の取得と canonical `owner/repo` 正規化 helper を追加し、失敗時に create へ error を返す
- pass condition:
  - resolver reject tests が通る

###### Refactor
- cleanup target:
  - resolver result / error message の重複整理
- invariants to keep green:
  - lowercase canonical comparison
  - existing issue create path の正常系は壊さない

#### step gate
- review:
  - canonical repo scope resolver が requirement の失敗条件を全て表現している
- expected tests:
  - resolver 追加 tests が exit=0
- verification command:
  - `python -m unittest tests.cli_runtime.test_runtime_new_s08`
- observes:
  - EC-001 / EC-002 と、AC-002 の resolver 失敗条件
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — node creation becomes GitHub mandatory for initiative / epic / issue
- target:
  - initiative / epic / issue の default mode を GitHub create に寄せ、`--no-github` を explicit contract error にする
- design refs:
  - `commands/new.py`
  - `create_node.py::_resolve_github_mode`
  - `.meta.json.github.issue_number` / `.meta.json.github.repo_owner` / `.meta.json.github.repo_name` persistence rules
- step boundary:
  - command / application create contract と persistence に限定し、validate hardening は S03 へ分離する

#### B1 — CLI and create contract
- purpose:
  - parser/help/default behavior と runtime mode resolution を一致させる
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_s08.py`

##### I1 — default GitHub create for initiative / epic
- slice goal:
  - `new initiative` / `new epic` / `new issue` が no flag でも GitHub mandatory contract で動き、`--no-github` は全 node kind で reject される

###### Red
- failing test:
  - initiative / epic / issue の default create behavior と `--no-github` reject tests を追加
- expected failure:
  - 現行は initiative / epic が `local_only` default であり、issue でも `--no-github` が成功経路として残るため失敗する

###### Green
- minimum implementation:
  - command layer と `_resolve_github_mode()` を更新
- pass condition:
  - default mode / reject tests が通る

###### Refactor
- cleanup target:
  - duplicate error message の整理
- invariants to keep green:
  - issue create default は維持
  - `--github-issue` link_existing は維持

##### I2 — same-repo linkage and reject boundaries
- slice goal:
  - `--github-issue` same-repo success と configured scope mismatch / cross-repo target reject を create contract に固定する

###### Red
- failing test:
  - `new issue --github-issue <same-repo issue>` success、configured scope mismatch reject、cross-repo target reject tests を追加
- expected failure:
  - 現行 contract では create boundary と repo scope reject 証跡が不足する

###### Green
- minimum implementation:
  - create precheck と same-repo comparison を整備し、link_existing / reject 条件を固定する
- pass condition:
  - same-repo success / mismatch reject tests が通る

###### Refactor
- cleanup target:
  - same-repo 判定と error mapping の整理
- invariants to keep green:
  - canonical lowercase basis comparison
  - GitHub mandatory default contract

##### I3 — `.meta.json` canonical scope persistence
- slice goal:
  - create success 時に first node binding と lowercase canonical `.meta.json.github.repo_owner` / `.meta.json.github.repo_name`、および `.meta.json.github.issue_number` 保存が観測できる

###### Red
- failing test:
  - first node binding と canonical scope persistence tests を追加
- expected failure:
  - 現行 persistence / scope resolution が要求粒度に届かない

###### Green
- minimum implementation:
  - create plan / stored meta への canonical scope 保存を確定
- pass condition:
  - created `.meta.json` assertions が通る

###### Refactor
- cleanup target:
  - persistence helper と normalization 呼び出しの整理
- invariants to keep green:
  - `.meta.json.github.issue_number` と `.meta.json.github.repo_owner` / `.meta.json.github.repo_name` の一貫性

#### step gate
- review:
  - create contract が initiative / epic / issue で統一されている
- expected tests:
  - default mode / `--no-github` reject / same-repo success / configured mismatch reject / cross-repo reject / persistence tests が exit=0
- verification command:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08`
- observes:
  - AC-001、AC-002 の create contract、EC-003
- report update:
  - `./spec-dock/active/issue/report.md`

### S03 — validation and migration boundary pre-guard align with create contract
- target:
  - GitHub mandatory contract を validation と最小 docs diff へ反映し、legacy mismatch を explicit に扱えるようにする
- design refs:
  - `domain/validation.py`
  - create contract boundary docs
- step boundary:
  - validation error surface、boundary docs diff、migration contract tests に限定する

#### B1 — validation hardening
- purpose:
  - local-only node 禁止と repo scope ambiguity を validation で観測可能にしつつ、single-repo contract と矛盾する exemption を残さない
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `tests/cli_runtime/test_runtime_new_s08.py`
  - `tests/cli_runtime/test_new.py`

##### I1 — validation catches disallowed create state
- slice goal:
  - old contract state が silent pass しない

###### Red
- failing test:
  - local-only node / ambiguous linkage / legacy mismatch の `new` contract error と `validate` validation error expectation tests を追加
- expected failure:
  - 現行 validation は mandatory contract を表現しない

###### Green
- minimum implementation:
  - validation に mandatory contract checks を追加し、legacy mismatch の error/warning 区分を explicit error に固定する
  - malformed partial scope を fail-closed にし、S04 の import strict reject と矛盾する exemption を残さない
- pass condition:
  - targeted validation tests が通る

###### Refactor
- cleanup target:
  - error wording と duplicate checks の整理
- invariants to keep green:
  - existing github linkage uniqueness は維持
  - sync-generated artifact の既存契約は壊さない

#### step gate
- review:
  - AC-003 の先行ガードが docs/tests/validate で揃っている
- expected tests:
  - validation / migration contract tests が exit=0
  - sync 本体コマンドと sync-generated artifact への適用範囲を広げていないことが diff / targeted regression で確認できる
- verification command:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08`
- supporting checks:
  - `./spec-dock/scripts/spec-dock validate`
- observes:
  - AC-003 と validation 境界
- report update:
  - `./spec-dock/active/issue/report.md`

### S04 — foreign issue URL import is corrected to strict reject
- target:
  - `initiative / epic / issue` node に対する foreign issue URL import を strict reject へ是正し、`iss-local-*` fallback を再導入しない
- design refs:
  - `commands/import_cmd.py`
  - `application/import_node.py`
  - `application/create_node.py`
  - `002-disc-foreign-issue-import-identity-conflict-analysis.md`
- step boundary:
  - foreign issue URL reject / no-write guarantee / docs and report 整流に限定し、external reference model や multi-repo support は扱わない

#### B1 — import contract correction
- purpose:
  - `--allow-foreign-url` を compatibility success path ではなく explicit reject path に揃える
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/import_cmd.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `tests/cli_runtime/test_import.py`
  - `tests/cli_runtime/test_runtime_import_s10.py`
  - `tests/test_init_update.py`

##### I1 — foreign issue URL reject and no-write guarantee
- slice goal:
  - current repo と異なる GitHub issue URL を import しようとした場合、`iss-local-*` fallback を作らず non-zero で止める

###### Red
- failing test:
  - foreign issue URL import success / `iss-local-*` fallback を期待しているテストを reject / no-write expectation に置き換える
- expected failure:
  - 現行は foreign import success と `iss-local-*` fallback を許してしまう

###### Green
- minimum implementation:
  - foreign issue URL を node identity に変換しないよう import/create seam を整理し、single-repo policy の reject error を返す
- pass condition:
  - targeted import tests が通り、新規 node / meta / symlink が作られない

###### Refactor
- cleanup target:
  - `--allow-foreign-url` error message と helper 呼び出しの整理
- invariants to keep green:
  - same-repo import / link_existing は壊さない
  - `iss-local-*` fallback は存在しない

#### B2 — docs and review log correction
- purpose:
  - 仕様逆行を前提にした記録を是正し、最新の accepted contract と一致させる
- files:
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00034-github-mandatory-node-creation-contract/discussions/002-disc-foreign-issue-import-identity-conflict-analysis.md`

##### I1 — docs are realigned to strict reject
- slice goal:
  - user-facing docs と issue-level report/discussion が `iss-local-*` fallback を正当化しない

###### Red
- failing check:
  - docs diff review で foreign import success を許す記述が残っている
- expected failure:
  - 現行 docs / review log は仕様逆行 fix を一時的に肯定している

###### Green
- minimum implementation:
  - docs と issue report を strict reject / corrective review cycle へ読み替える
- pass condition:
  - docs diff review で accepted contract と矛盾する記述が解消される

###### Refactor
- cleanup target:
  - 似た説明の重複を減らし、`002-disc` を分析の正本に寄せる
- invariants to keep green:
  - accepted ADR / epic / issue requirement と矛盾しない

#### step gate
- review:
  - foreign issue URL import の是正が tests / docs / review記録で一貫している
- expected tests:
  - `tests/cli_runtime/test_import.py`
  - `tests/cli_runtime/test_runtime_import_s10.py`
  - relevant `new` regressions
- verification command:
  - `python -m unittest tests.cli_runtime.test_import tests.cli_runtime.test_runtime_import_s10 tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08`
- supporting checks:
  - `./spec-dock/scripts/spec-dock validate`
- evidence note:
  - `tests.test_init_update` は `iss-00034` acceptance gate には含めない。S04 strict reject correction とは独立した pre-existing baseline failures が残っており、この issue では cleanup scope に含めない。
- observes:
  - AC-004、EC-004、および `iss-local-*` fallback 不在
- report update:
  - `./spec-dock/active/issue/report.md`

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - issue docs と foreign issue strict reject に直接関係する最小 docs
- 対応:
  - create contract と foreign issue strict reject を参照する最小 docs 差分のみ更新する
  - full parity refresh は `iss-00038` に渡し、この issue では未完了でも境界逸脱にしない
  - 更新候補:
    - `spec-dock/active/issue/{requirement,design,plan}.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
    - `spec-dock/docs/workflow_issue.md`
    - `spec-dock/active/issue/report.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00034-github-mandatory-node-creation-contract/discussions/002-disc-foreign-issue-import-identity-conflict-analysis.md`
- verification command:
  - `git diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md src/spec_dock/assets/spec_dock/docs/reference_github.md spec-dock/docs/workflow_issue.md spec-dock/active/issue/report.md`
- observes:
  - docs diff が boundary/canonical scope と foreign strict reject の最小更新に留まり、accepted contract と矛盾しないこと

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00034` ブランチ差分全体
- required validation:
  - targeted unittest output（create / resolver / validation / import strict reject）
  - docs diff が boundary/canonical scope の最小更新に留まっていること
  - import / sync 関連ロジックへ不要な差分が入っていないこと
- verification command:
  - `python -m unittest tests.cli_runtime.test_import tests.cli_runtime.test_runtime_import_s10 tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08`
- supporting checks:
  - `./spec-dock/scripts/spec-dock validate`（iss-00034 の create / validation boundary pre-guard に関する issue-specific supporting evidence。sync-generated artifact regeneration は scope 外のため `sync --github` は required evidence に含めない）
  - `git diff --stat`
- evidence note:
  - `tests.test_init_update` は unrelated baseline failures が未解消のため informational check に留め、S99 acceptance evidence には採用しない。
- reviewer approvals:
  - implementation review
  - spec review
  - 必要なら QA review

## 未確定事項
- なし:
  - issue 着手に必要な execution contract は固定する

## final exit contract
- AC/EC 達成:
  - AC-001/002/003/004 と EC-001/002/003/004 に対応する tests / docs diff / validation evidence が揃う
- docs impact resolved:
  - boundary/canonical scope の最小 docs diff が反映され、full parity work は `iss-00038` へ残せている
- scope boundary preserved:
  - foreign issue strict reject に必要な import 是正だけを扱い、multi-repo support / external reference model / sync-generated artifact regeneration は持ち込まない
- final diff approved:
  - S99 を通過し、reviewer が実装開始・継続可能と判断できる
