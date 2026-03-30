---
種別: 実装計画書（Issue）
ID: "iss-00037"
タイトル: "Migration Guardrails and Validation Hardening"
関連GitHub: ["#37"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00037 Migration Guardrails and Validation Hardening — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
- 制約:
  - old workspace 自動移行 tooling は追加しない
  - `iss-00038` / `iss-00040` の ownership を侵食しない
  - true runtime defect が見つかったら stop / escalate する

## マイルストーン一覧
- M1:
  - 対象:
    - migration boundary evidence inventory の固定
  - exit:
    - clause-1/2/3 ごとの current evidence / missing evidence / owner が整理されている
- M2:
  - 対象:
    - clause-1 / clause-2 の docs + validate boundary hardening
  - exit:
    - forced backward compatibility 非維持と in-place 自動移行非保証が reviewer に追え、README contradiction の最小 correction owner も固定される
- M3:
  - 対象:
    - clause-3 の non-destructive evidence hardening
  - exit:
    - fail-fast / warning / no-auto-repair 境界が tests と command evidence で観測できる
- M4:
  - 対象:
    - final closure bundle
  - exit:
    - clause-by-clause evidence set と final review record が揃う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - clause-1/2/3 の current implementation status と gap が issue scope で明示されている
  - closes:
    - なし（baseline / inventory）
  - review gate:
    - inventory と ownership boundary が spec review 可能な形で残っている
- S02:
  - 観測可能な振る舞い:
    - clause-1 と clause-2 の docs / validate boundary が reviewer にとって自明になり、README contradiction の最小 boundary correction も本 issue scope で扱われる
  - closes:
    - AC-001
    - AC-002
    - EC-002
  - review gate:
    - `README.md` / `spec-dock/docs/README.md` / reference docs の minimal docs diff と targeted create / import / validate evidence が揃う
- S03:
  - 観測可能な振る舞い:
    - clause-3 の fail-fast / warning / no-auto-repair 境界が tests と command results で観測できる
  - closes:
    - AC-003
  - review gate:
    - targeted tests と command evidence が揃う
- S04:
  - 観測可能な振る舞い:
    - `iss-00037` の final closure bundle だけで clause-1/2/3 を再判定できる
  - closes:
    - AC-004
    - EC-001
  - review gate:
    - report / final review に owner と evidence set が揃う

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S04
- EC-001 -> S04
- EC-002 -> S02

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前に pass を取得する
    - S01 完了後に issue scope と evidence inventory の妥当性を再確認する
  - scope:
    - clause mapping
    - ownership boundary
    - verification matrix
- RG1 code review:
  - timing:
    - S02 完了後
    - S03 完了後
    - S99 前の final review
  - scope:
    - docs / validate / tests diff が migration boundary から逸脱していないか
- QG1 QA review:
  - timing:
    - S03 完了後
    - S99 前の final review
  - scope:
    - targeted tests
    - `validate` / `sync` command evidence
- step approval loop:
  - SG1/spec review pass を取得するまで実装を開始しない
  - S01 後は SG1/spec review approval を `report.md` に記録してから S02 を開始する
  - S02 後は RG1/code review pass を `report.md` に記録してから S03 を開始する
  - S03 後は RG1/code review pass と QG1/QA review pass を `report.md` に記録してから S04 を開始する
  - S04 後は final RG1/code review pass と final QG1/QA review pass を `report.md` に記録してから close / commit する

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
- migrate ではなく boundary hardening を扱う issue なので、true runtime defect を見つけた場合は、この issue では runtime behavior を広げず、所見を `report.md` に残して人間判断で別 issue 化または scope update を行う。

## 実装ステップ

### S01 — clause inventory and ownership lock
- target:
  - existing reports
  - current docs
  - current validate / sync preflight tests
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/plan.md`
- step boundary:
  - current implementation status を clause-1/2/3 ごとに分解し、この issue で閉じる gap だけを確定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — evidence inventory
- purpose:
  - 既存 issue の成果を migration boundary の観点で再整理する
- files:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/initiatives/.../iss-00034.../report.md`
  - `spec-dock/initiatives/.../iss-00035.../report.md`
  - `spec-dock/initiatives/.../iss-00036.../report.md`
  - `spec-dock/initiatives/.../iss-00040.../report.md`

##### I1 — map clause to evidence
- slice goal:
  - clause-1/2/3 ごとの current evidence と missing evidence を列挙する

###### Red
- failing test:
  - なし
- expected failure:
  - evidence ownership が曖昧なままだと reviewer が close 判定できない

###### Green
- minimum implementation:
  - requirement / design / plan / 必要なら discussion に evidence matrix を反映する
- pass condition:
  - `iss-00037` の scope と ownership boundary が固定される

###### Refactor
- cleanup target:
  - issue docs 間の表現統一
- invariants to keep green:
  - `iss-00038` / `iss-00040` の ownership を侵食しない

#### step gate
- review:
  - spec review で issue scope と evidence inventory が pass
- expected tests:
  - なし
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — clause-1 and clause-2 docs plus validate hardening
- target:
  - minimal boundary docs
  - README boundary correction
  - validate regressions
- design refs:
  - `spec-dock/active/issue/design.md`
  - `README.md`
  - `spec-dock/docs/README.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_naming.md`
  - `tests/cli_runtime/test_validate.py`
- step boundary:
  - forced backward compatibility 非維持と in-place 自動移行非保証を、docs / validate / tests の正本へ揃える
  - clause-2 acceptance は named docs diff（`README.md` / `spec-dock/docs/README.md` / reference docs）と current create / import / validate reject evidence で discharge し、新しい update-migration runtime path は作らない

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — clause-1 wording and validate mapping
- purpose:
  - legacy sequential grandfathering と non-forced-compatibility を reviewer に追える形にする
- files:
  - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
  - `spec-dock/docs/reference_naming.md`
  - `tests/cli_runtime/test_validate.py`

##### I1 — close clause-1 wording gaps
- slice goal:
  - legacy docs は grandfathered、ただし新規採番 / auto-rename / backward compatibility 強制維持はしないと明示する

###### Red
- failing test:
  - 必要なら naming / validate targeted regression 1 本
- expected failure:
  - wording だけでは足りず、validate 側の観測点が不足していることが分かる

###### Green
- minimum implementation:
  - docs wording と targeted validate coverage を最小差分で追加 / 修正する
- pass condition:
  - clause-1 の docs + validate evidence が揃う

###### Refactor
- cleanup target:
  - provider / dogfooding wording の同期
- invariants to keep green:
  - full docs parity refresh は `iss-00038` に残す

#### B2 — clause-2 update non-guarantee
- purpose:
  - `spec-dock update` による in-place 自動移行非保証を docs / tests で観測可能にし、README contradiction の最小 correction owner を `iss-00037` に固定する
- files:
  - `README.md`
  - `spec-dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `spec-dock/docs/reference_github.md`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_s08.py`
  - `tests/cli_runtime/test_validate.py`

##### I1 — close clause-2 wording gaps
- slice goal:
  - current repo mismatch や legacy linkage mismatch が auto-migrate ではなく reject / fail-fast であることと、README surface でも `update` 非保証が truthfully 読めることを固定する

###### Red
- failing test:
  - local-only / legacy unscoped / malformed scope validate regressions のうち不足分 1 本
- expected failure:
  - `update` 非保証または fail-fast 境界の観測点不足が再現する

###### Green
- minimum implementation:
  - `README.md` / `spec-dock/docs/README.md` / reference docs の最小 wording correction と targeted validate coverage を補完する
- pass condition:
  - clause-2 の parent epic acceptance が、named docs diff + current create / import / validate reject evidence だけで判定できる

###### Refactor
- cleanup target:
  - wording の重複と曖昧な migration 表現の解消
- invariants to keep green:
  - `update` を migration ツールとして誤解させない
  - full docs parity refresh は `iss-00038` に残す

#### step gate
- review:
  - RG1 code review pass
- expected tests:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08 -v`
  - `python -m unittest tests.cli_runtime.test_validate -v`
- report update:
  - `./spec-dock/active/issue/report.md`

### S03 — clause-3 non-destructive boundary hardening
- target:
  - validate
  - sync preflight
  - command evidence
- design refs:
  - `spec-dock/active/issue/design.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `tests/cli_runtime/test_validate.py`
  - 必要なら `tests/cli_runtime/test_sync.py`
- step boundary:
  - legacy mismatch を silent auto-repair せず、warning / fail-fast / no-write のどれで観測するかを固定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — validate and sync preflight evidence
- purpose:
  - checked-in data 無断破壊を目的にしない境界を observable にする
- files:
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_sync.py`
  - 必要なら related runtime modules

##### I1 — prove no-auto-repair path
- slice goal:
  - malformed / legacy mismatch は non-zero または warning で止まり、暗黙書き換えをしないことを固定する

###### Red
- failing test:
  - clause-3 を直接表す targeted regression 1 本
- expected failure:
  - no-write または warning/fail-fast classification の不足が再現する

###### Green
- minimum implementation:
  - validation / sync preflight / test expectation を最小差分で補完する
- pass condition:
  - clause-3 の targeted tests が pass する

###### Refactor
- cleanup target:
  - evidence wording と test naming の明確化
- invariants to keep green:
  - self-healing mutation path を追加しない

#### step gate
- review:
  - RG1 code review pass
  - QG1 QA review pass
- expected tests:
  - `python -m unittest tests.cli_runtime.test_validate -v`
  - 必要に応じて `python -m unittest tests.cli_runtime.test_sync -v`
  - `./spec-dock/scripts/spec-dock validate`
- report update:
  - `./spec-dock/active/issue/report.md`

### S04 — final closure bundle and evidence handoff
- target:
  - issue report
  - final review packet
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/plan.md`
- step boundary:
  - reviewer が `iss-00037` だけで clause-by-clause close readiness を再確認できる状態にする

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — evidence packaging
- purpose:
  - clause evidence と ownership boundary を final close-out 用に束ねる
- files:
  - `spec-dock/active/issue/report.md`
  - 必要なら `spec-dock/active/epic/plan.md`

##### I1 — prepare final closure packet
- slice goal:
  - clause-1/2/3 ごとに docs / tests / command evidence を参照可能にする

###### Red
- failing test:
  - なし
- expected failure:
  - evidence が散在して final close review できない

###### Green
- minimum implementation:
  - report / final review notes / close criteria を追記する
- pass condition:
  - issue close readiness が packet 化される

###### Refactor
- cleanup target:
  - close evidence の重複削除
- invariants to keep green:
  - `iss-00038` final docs parity scope を奪わない

#### step gate
- review:
  - final RG1/code review pass
  - final QG1/QA review pass
- expected tests:
  - S02 / S03 の required evidence が再参照可能
- report update:
  - `./spec-dock/active/issue/report.md`

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - `iss-00037` では migration boundary に直接関係する minimal docs diff のみを扱う
  - repo entrypoint `README.md` と `spec-dock/docs/README.md` の contradictory wording correction は S02 の boundary scope に含める
  - provider-side docs と checked-in dogfooding docs は必要箇所だけ同期する
  - full docs parity refresh は `iss-00038` の scope として維持する

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00037` で触れた docs / tests / minimal runtime diff
- required validation:
  - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08 -v`
  - `python -m unittest tests.cli_runtime.test_validate -v`
  - 必要に応じて `python -m unittest tests.cli_runtime.test_sync -v`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer approvals:
  - SG1 spec review pass
  - final RG1 code review pass
  - final QG1 QA review pass

## 未確定事項
- なし:
  - current plan は evidence hardening のみを扱う

## final exit contract
- AC/EC 達成:
  - clause-1/2/3 が docs / validate / tests / command evidence に 1 対 1 で対応づく
  - maintainer / reviewer が narrative 依存なしで migration boundary を再判定できる
  - `iss-00038` / `iss-00040` との ownership boundary が崩れていない
- docs impact resolved:
  - minimal boundary docs diff が provider / dogfooding で整合している
  - README contradiction correction は S02 の narrow boundary scope として完了している
- final diff approved:
  - S99 required validation と reviewer approvals が揃っている
