---
種別: 実装計画書（Issue）
ID: "iss-00036"
タイトル: "Timestamp Based Discussion and ADR Naming"
関連GitHub: ["#36"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-28"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00036 Timestamp Based Discussion and ADR Naming — 実装計画（Execution Contract）

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
  - `adr / disc / research / note` を同一 timestamp-prefix contract に統一する
  - 原本は常に `discussions/` に置く
  - pre-contract sequential docs は grandfathered として残し、自動 rename しない
  - `sync` の mirror 本体変更は行わない

## マイルストーン一覧
- M1:
  - 対象:
    - discussion filename allocator の timestamp 化
  - exit:
    - `new doc` が 4 type すべてで timestamp-prefix basename を生成し、same scope / same `ts` collision を create lock 内の suffix 選択で吸収できる
- M2:
  - 対象:
    - validation / docs boundary / parity
  - exit:
    - validate と docs/test expectation が新 naming contract に揃う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `new doc adr|disc|research|note` が `discussions/` に timestamp-prefix basename を生成する
  - closes:
    - AC-001
    - EC-001
  - review gate:
    - 4 type 共通 grammar と path assertions が green
- S02:
  - 観測可能な振る舞い:
    - same-second collision が same scope / same `ts` の family domain で、create lock により直列化された suffix 選択として `-01-`, `-02-` で deterministic に吸収される
  - closes:
    - AC-002
    - EC-003
    - EC-004
  - review gate:
    - collision-focused CLI/application regressions が green
- S03:
  - 観測可能な振る舞い:
    - validate が新 timestamp contract を検査し、legacy sequential docs は grandfathered、malformed discussion-doc candidate は error、unrelated file は ignore として扱う
  - closes:
    - AC-003
    - EC-002
  - review gate:
    - validate / legacy boundary tests が green で、docs evidence は S90 に委譲されている
- S90:
  - 観測可能な振る舞い:
    - naming docs / workflow docs / rules docs が 4 type timestamp contract に揃う
  - closes:
    - AC-004
  - review gate:
    - provider + dogfooding docs parity 確認
- S99:
  - 観測可能な振る舞い:
    - final diff と review verdict が issue scope と一致し、workflow-required final commands まで完了している
  - closes:
    - AC-001
    - AC-002
    - AC-003
    - AC-004
  - review gate:
    - spec review / implementation review / QA review pass

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S90
- EC-001 -> S01
- EC-002 -> S03
- EC-003 -> S02
- EC-004 -> S02

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S02 後、S03 後
  - scope:
    - allocator / validation boundary の layering と contract drift 有無
- QG1 QA review:
  - timing:
    - S03 後
  - scope:
    - timestamp collision / legacy grandfathering / validate coverage
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

### S01 — `new doc` generates timestamp-prefixed filenames for the full discussion doc family
- target:
  - sequential allocation を timestamp allocation に置き換え、4 type 全体を同一 contract へ乗せる
- design refs:
  - `design.md` の filename contract / allocator contract
- step boundary:
  - create path と create-side parser に限定し、validate / docs parity は後続 step に分離する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — timestamp allocator and create path
- purpose:
  - basename 生成規則を `<ts>-<kind>-<slug>.md` へ切り替え、4 type 共通化する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`

##### I1 — timestamp basename replaces sequence basename
- slice goal:
  - `new doc adr|disc|research|note` の生成先と basename を timestamp-prefix に切り替える

###### Red
- failing test:
  - 4 type の generated filename assertion を timestamp-prefix へ更新 / 追加
- expected failure:
  - 現行は `NNN-type-slug.md` を返すため失敗する

###### Green
- minimum implementation:
  - create-side regex / planner / result doc_id を timestamp contract に置き換える
  - template placeholders (`<ADR_ID>` など) へ新 `doc_id` が入るよう置換 contract を更新する
- pass condition:
  - create-side new-doc tests が green

###### Refactor
- cleanup target:
  - allocator helper と parser helper の共通化
- invariants to keep green:
  - 4 type surface は維持
  - 原本 path は `discussions/` のまま
  - slug kebab-case validation は維持

#### step gate
- review:
  - 4 type family が split されていない
- expected tests:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09`
- verification command:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09`
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — same-second collisions are absorbed with deterministic suffixes
- target:
  - 同秒並行作成の collision を same scope / same `ts` domain で `-01-`, `-02-` により吸収し、suffix 選択は create lock / create critical section 内で直列化して race を残さない
- design refs:
  - `design.md` の collision basename / allocation contract
- step boundary:
  - timestamp collision と overflow failure に限定し、legacy validate は S03 へ分離する

#### B1 — same-second suffix allocation
- purpose:
  - same scope / same `ts` domain の 2 件目以降に対する suffix 採番を、既存 create lock による直列化前提で固定する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_new.py`

##### I1 — same-second suffix allocation
- slice goal:
  - 同秒 / 同scope / cross-type でも、create lock 通過順に deterministic な suffix を割り当て、collision form の identity と exhaustion failure を固定する

###### Red
- failing test:
  - same-second 固定 clock で `adr`, `disc`, `research`, `note` の collision suffix tests を追加
  - allocation が create critical section 内で行われる前提を確認する regression を追加
  - `01..99` を使い切ったときの suffix exhaustion test を追加
- expected failure:
  - 現行は同名 path 衝突か、timestamp helper 未実装で失敗する

###### Green
- minimum implementation:
  - same scope / same `ts` domain の追加 file に対して、create lock 内で `01..99` を探索する helper を導入し、使い切った場合は explicit failure にする
- pass condition:
  - collision tests が green

###### Refactor
- cleanup target:
  - suffix allocation と basename formatting の分離
  - standard form / collision form の doc identity 表現を helper に集約
- invariants to keep green:
  - no sequential fallback
  - same-second 以外では suffix を付けない

#### step gate
- review:
  - same-second collision 吸収が create lock 前提で deterministic で、cross-type collision も吸収できる
- expected tests:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09`
- verification command:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09`
- report update:
  - `./spec-dock/active/issue/report.md`

### S03 — validate aligns with timestamp grammar and legacy grandfathering
- target:
  - validate が新 grammar を検査し、legacy sequential docs / malformed discussion-doc candidate / unrelated file の境界を固定する
- design refs:
  - `design.md` の validation contract / legacy boundary
- step boundary:
  - validate logic、legacy classification、関連 tests に限定する。docs evidence は S90 へ分離する

#### B1 — validation grammar update
- purpose:
  - sequential duplicate validation を timestamp contract へ置き換え、legacy sequential は grandfathered、malformed discussion-doc candidate は explicit error、unrelated file は ignore に振り分ける
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_new.py`

##### I1 — timestamp validation and grandfathering
- slice goal:
  - timestamp files は validate 対象、sequential legacy は grandfathered、discussion-doc intent を持つ malformed filename は error、unrelated nonconforming は ignore の境界を固定する

###### Red
- failing test:
  - timestamp malformed / malformed discussion-doc candidate / duplicate timestamp suffix / legacy sequential coexistence tests を追加
- expected failure:
  - 現行 validate は duplicate sequence だけを見ており、新 contract に一致しない

###### Green
- minimum implementation:
  - validation parser を timestamp contract へ切り替え、legacy sequential / malformed candidate / unrelated file の判定を追加する
- pass condition:
  - validate-related tests が green

###### Refactor
- cleanup target:
  - filename parser 共通化、error message の安定化
- invariants to keep green:
  - rules.md 等の nonconforming files は ignore
  - timestamp-like / discussion-doc-like malformed filename は explicit error
  - grandfathered files を自動 rename しない

#### step gate
- review:
  - validate が新規 contract、grandfathered boundary、malformed candidate error、unrelated file ignore に整合している
- expected tests:
  - `python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09`
- verification command:
  - `python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09`
- report update:
  - `./spec-dock/active/issue/report.md`

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / rules
- 対応:
  - `reference_naming.md` を timestamp-prefix grammar と `doc_id`/filename stem boundary に合わせて更新する
  - `workflow_{initiative,epic,issue}.md` と `rules/*/discussions.md` の `new doc` 説明を timestamp contract に揃える
  - provider と dogfooding mirror の parity を確認する
  - `iss-00035` の ADR 集約 scan が参照する前提として、ADR 原本が `discussions/` にあることを docs 上でも明確化する
- review gate:
  - docs diff / parity evidence が green

### S99 — final diff review quality gate
- branch diff scope:
  - `new doc` naming create path
  - validate
  - naming/workflow docs
  - relevant tests / parity tests
- required validation:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate`
  - 必要なら `python -m unittest tests.test_init_update`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
- reviewer approvals:
  - spec review `pass`
  - implementation/code review `pass`
  - QA review `pass`

## final exit contract
- AC/EC 達成:
  - 4 type discussion doc family が timestamp-prefix naming に統一されている
  - same-second collisions が suffix で吸収される
  - suffix exhaustion は explicit failure として扱われる
  - validate が新 contract と grandfathered boundary に整合する
- docs impact resolved:
  - naming / workflow / rules docs が provider と dogfooding で一致している
- final diff approved:
  - reviewer verdict と report evidence が一致している
