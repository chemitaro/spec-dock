---
種別: 実装計画書（Issue）
ID: "iss-00035"
タイトル: "Sync ADR Symlink Mirror"
関連GitHub: ["#35"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00035 Sync ADR Symlink Mirror — 実装計画（Execution Contract）

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
- 制約:
  - clear-then-rebuild
  - flat `spec-dock/adrs/<basename>` layout
  - collision preflight before clear
  - collision failure preserves prior `spec-dock/adrs/`
  - no manifest / no silent overwrite / no legacy rescue

## マイルストーン一覧
- M1:
  - 対象:
    - mirror source 判定と collision preflight
  - exit:
    - valid source だけを採用し、collision failure で `adrs/` 不変をテストで確認できる
- M2:
  - 対象:
    - clear-then-rebuild / stale cleanup / non-symlink fallback
  - exit:
    - success path と warning path の filesystem 終状態がテストで確認できる
- M3:
  - 対象:
    - review / docs impact / final regression
  - exit:
    - targeted tests と final diff review が通る

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `sync` が mirror source を multi-scope scan + path/basename/front matter/parent-match contract で判定し、basename collision を clear 前に failure にする
  - closes:
    - AC-001, EC-001, EC-002, EC-004, EC-005
  - review gate:
    - source inclusion / exclusion と collision preservation がテストで見える
- S02:
  - 観測可能な振る舞い:
    - `sync` 成功時に flat mirror を clear-then-rebuild し、rename/delete 後 stale link を残さない
  - closes:
    - AC-001, AC-002, EC-003
  - review gate:
    - flat layout と stale cleanup がテストで見える
- S03:
  - 観測可能な振る舞い:
    - symlink unsupported classifier のときだけ空 directory + warning success になり、それ以外の symlink / write failure は hard failure になる
  - closes:
    - AC-003, EC-006
  - review gate:
    - warning / exit=0 / empty-dir 終状態がテストで見える

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S02
- AC-003 -> S03
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S02
- EC-004 -> S01
- EC-005 -> S01
- EC-006 -> S03

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - 各 step の Green 後
  - scope:
    - step が closes する AC/EC と failure semantics
- QG1 QA review:
  - timing:
    - S03 完了後
  - scope:
    - collision preservation / stale cleanup / non-symlink warning success の検証十分性
- SG1 spec review:
  - timing:
    - S90 後、S99 前
  - scope:
    - requirement / design / plan / report の整合

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

### S01 — mirror source preflight と collision preservation
- target:
  - source scan helper
  - front matter / basename 判定
  - collision preflight
  - collision failure contract
- design refs:
  - `source selection contract`
  - `collision contract`
- step boundary:
  - clear-then-rebuild 成功 path までは入れず、preflight failure semantics に閉じる

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — source inclusion / exclusion
- purpose:
  - valid source と ignored source の境界を固定する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`

##### I1 — valid/invalid source scan
- slice goal:
  - initiative / epic / issue を横断して、path + basename + front matter + parent-match contract で source を選別する

###### Red
- failing test:
  - 複数 scope の valid ADR は採用され、legacy ADR / malformed front matter / unrelated file / parent mismatch source は mirror source から除外される test
- expected failure:
  - 現行 sync には source scan がなく test が落ちる

###### Green
- minimum implementation:
  - source descriptor と source preflight helper を追加する
- pass condition:
  - source inclusion / exclusion tests が green

###### Refactor
- cleanup target:
  - parse helper の責務分離
- invariants to keep green:
  - legacy non-inclusion
  - basename-only 採用をしない
  - path-parent mismatch 非採用

#### B2 — collision failure semantics
- purpose:
  - collision を clear 前 failure に固定する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`

##### I1 — collision preflight
- slice goal:
  - basename collision が `adrs/` 不変のまま failure になる

###### Red
- failing test:
  - collision source 2件で `sync` failure、既存 `adrs/` state preserved、non-zero or equivalent failure evidence を確認する test
- expected failure:
  - 現行 sync は collision preflight を持たない

###### Green
- minimum implementation:
  - mirror path 集合の衝突検出と failure result を追加する
- pass condition:
  - collision preservation tests が green

###### Refactor
- cleanup target:
  - failure reason 文言と helper 名称
- invariants to keep green:
  - clear 前 failure
  - no silent overwrite

#### step gate
- review:
  - source selection / collision semantics review
- expected tests:
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — flat mirror rebuild と stale cleanup
- target:
  - `spec-dock/adrs/<basename>` rebuild
  - stale symlink cleanup
- design refs:
  - `mirror layout contract`
  - `rebuild contract`
- step boundary:
  - success path のみ。non-symlink warning path は S03 に分離する

#### B1 — rebuild success path
- purpose:
  - flat mirror を clear-then-rebuild で再生成する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`

##### I1 — flat mirror creation
- slice goal:
  - valid sources から `spec-dock/adrs/<basename>` symlink を生成する

###### Red
- failing test:
  - sync 後に flat mirror symlink 群が存在する test
- expected failure:
  - 現行 sync は `adrs/` を作らない

###### Green
- minimum implementation:
  - preflight success 後の clear / mkdir / symlink create を追加する
- pass condition:
  - flat mirror test が green

###### Refactor
- cleanup target:
  - relative symlink helper の共通化
- invariants to keep green:
  - basename preserved
  - flat layout

##### I2 — stale cleanup
- slice goal:
  - rename/delete 後 stale link が残らない

###### Red
- failing test:
  - 旧 basename の symlink が 2回目 sync 後に消える test
- expected failure:
  - 現行 sync は stale cleanup をしない

###### Green
- minimum implementation:
  - clear-then-rebuild 成功 path を完成させる
- pass condition:
  - stale cleanup tests が green

###### Refactor
- cleanup target:
  - directory cleanup helper
- invariants to keep green:
  - success path では stale symlink 不残存

#### step gate
- review:
  - rebuild / stale cleanup review
- expected tests:
  - `tests/cli_runtime/test_sync.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
- report update:
  - `./spec-dock/active/issue/report.md`

### S03 — non-symlink warning success
- target:
  - symlink unsupported fallback
  - warning surface
- design refs:
  - `non-symlink contract`
- step boundary:
  - symlink unsupported classifier と hard failure の境界に限定する

#### B1 — empty-dir warning success
- purpose:
  - symlink 非対応環境で failure にせず deterministic end state を残す
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`

##### I1 — fallback path
- slice goal:
  - unsupported classifier のときだけ empty `adrs/` + warning + exit=0 を固定し、その他の symlink / write failure は hard failure にする

###### Red
- failing test:
  - unsupported classifier では warning success と空 directory、unrelated symlink/write failure では hard failure を確認する test
- expected failure:
  - 現行 sync は fallback を持たない

###### Green
- minimum implementation:
  - unsupported classifier だけを warning success に変換する
- pass condition:
  - non-symlink fallback tests が green

###### Refactor
- cleanup target:
  - classifier と warning code / message の一貫化
- invariants to keep green:
  - empty-dir end state
  - exit=0
  - non-unsupported failure は hard fail

#### step gate
- review:
  - fallback / warning review
- expected tests:
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
- report update:
  - `./spec-dock/active/issue/report.md`

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs
- 対応:
  - issue report を更新する
  - 後続 docs parity issue で扱う境界を崩さず、必要なら issue-local report に mirror contract の最終 evidence を残す

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00035` 実装 diff 全体
- required validation:
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
  - `tests/cli_runtime/test_sync.py`
  - issue に追加した targeted tests
- reviewer approvals:
  - implementation review pass
  - QA review pass
  - spec review pass

## 未確定事項
- なし:
  - requirement / design に必要な execution contract は固定済み

## final exit contract
- AC/EC 達成:
  - flat mirror / stale cleanup / non-symlink fallback / collision preservation がテストで閉じている
- docs impact resolved:
  - report に実行結果と reviewer verdict が残っている
- final diff approved:
  - `S99 final diff review quality gate` が pass している
