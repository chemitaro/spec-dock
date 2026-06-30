---
種別: 実装計画書（Issue）
ID: "iss-00252"
タイトル: "Compile Grade Aware Issue Planning Guidance"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00252 Compile Grade Aware Issue Planning Guidance — Issue 実装計画書（Strict）

## 1. 実装戦略

ADR と Epic design の grade matrix を、agent-facing guidance と docs に落とす。runtime wording と docs wording が分岐しないよう、source-of-truth surface を先に確認する。

## 2. マイルストーン

| Milestone | 成果 | 検証 |
|---|---|---|
| M0 | current guidance / docs / skill wording の baseline | inspection |
| M1 | grade selection と authority split を guidance に追加 | focused tests / docs inspection |
| M2 | requirement / design / plan authoring rules を追加 | docs / skill inspection |
| M3 | specialist 推奨 / 必須 / fallback wording を追加 | guidance regression |
| M90 | provider / dogfooding mirror parity | parity inspection |
| M95 | strict spec review | spec-reviewer pass |
| M99 | issue-local handoff gate | focused tests, `./spec-dock/scripts/spec-dock validate` |

## 3. Behavior Backlog

| Behavior | 内容 | Closure |
|---|---|---|
| B-001 | guidance が grade matrix を返す | AC-001 |
| B-002 | Lite non-default と unknown -> Standard 以上を示す | AC-002 / AC-003 |
| B-003 | `authorized_profile` と manual escalation の分離を示す | AC-004 |
| B-004 | Standard の specialist 推奨 / skip reason を示す | AC-005 |
| B-005 | Strict / Critical の specialist fallback evidence を示す | AC-006 |
| B-006 | G2 / G3 が参照できる wording を固定する | AC-007 |

## 4. 変更対象

- issue-planning guidance source
- issue planning skill handoff docs
- `workflow_spec_authoring.md` and phase docs
- provider / dogfooding mirror
- relevant guidance tests

## 5. 禁止変更

- `new doc` draft routing を変更しない。
- readiness classifier を変更しない。
- Fresh `spec-reviewer` gate を弱めない。

## 6. Review / commit gate

- M1〜M3 は docs / guidance wording の coherent diff として review する。
- M99 で実行した command、未実施理由、provider / dogfooding parity を `report.md` に記録する。

## 7. 実装ステップ / 実行ステップ契約（Executable Step Contract）

| Step | Milestone | 対応Behavior | Source of truth / 入力 | 許可パス | 禁止パス / 禁止変更 | 実装内容 | Red / 代替証跡 | Green 検証 | Reviewer focus | Report destination |
|---|---|---|---|---|---|---|---|---|---|---|
| S00 | M0 | B-001〜B-006 | Epic #224 requirement/design/plan、ADR `20260630t111316z`、現行 provider/dogfooding docs、issue-planning skill | read-only inspection | implementation change | current guidance / docs / skill wording の baseline を確認し、既存 wording gap と owner surface を report に記録する | inspect-only | report の S00 evidence に対象ファイル、既存 wording、gap を記録 | 調査が G1 scope に閉じているか | `report.md#実装記録` / S00 |
| S01 | M1 | B-001 / B-002 / B-003 | ADR の grade selection / authority split、Epic design の Grade-Aware Authoring Router | `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`; `spec-dock/docs/workflow_spec_authoring.md`; 必要なら `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`; `.agents/skills/spec-dock-issue-planning/SKILL.md` | draft routing implementation、report evidence enforcement、automatic Lite default、ADR meaning change | grade matrix、Lite non-default、unknown -> Standard 以上、`authorized_profile` と manual escalation の分離を durable wording と skill first-read/stop condition に追加する | docs inspection: 現行 wording が AC-001〜AC-004 を満たさない箇所を S00/S01 evidence に記録 | provider/dogfooding docs parity、skill parity、`rg` で required wording を確認 | AC-001〜AC-004 が過不足なく表現され、G2/G3/G4 実装に踏み込まないか | TDD table、Closure Coverage C-001〜C-003 |
| S02 | M2 | B-004 / B-005 | ADR の grade別 specialist / fallback rule、Epic design の Evidence / Role Coordination | `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`; `phase_design.md`; `phase_plan_issue.md`; dogfooding mirror; issue-planning skill | runtime enforcement、new doc routing、report gate validation | requirement/design/plan authoring rules、Standard の specialist 推奨/未使用理由、Strict/Critical の specialist 原則必須/利用不可時 fallback evidence を phase docs と skill に追加する | docs inspection: specialist/fallback wording gap を report に記録 | `rg` で Standard / Strict / Critical / fallback / report evidence wording を provider/dogfooding 両方で確認 | AC-005/AC-006 が gradeごとに読め、過剰に委任必須化しないか | TDD table、Closure Coverage C-004 |
| S03 | M3 | B-006 | G2 / G3 / G4 の issue requirement/design/plan draft、Epic plan G2〜G4 | same docs / skill touched in S01-S02 | G2/G3/G4 の実装本体 | downstream G2/G3/G4 が参照できる stable terms（draft routing、report evidence gate、integrated smoke）と stop condition を整える | wording inspection: downstream reference 不足を report に記録 | `rg` inspection で G2/G3/G4 reference terms が docs/skill に存在することを確認 | AC-007 が G2/G3/G4 すべてを含むか | Closure Coverage C-005 |
| S90 | M90 | all | provider side as source of truth、dogfooding mirror | provider docs/skill、dogfooding docs/skill、tests if changed | source-of-truth inversion | provider / dogfooding mirror parity を確認し、必要なら provider から dogfooding へ同期する | docs inspection | `diff` / `rg` inspection、`./spec-dock/scripts/spec-dock validate` | provider優先とdogfooding整合が守られているか | Closure Coverage C-090 |
| S95 | M95 | all | current diff、active issue artifacts | read-only review | self-pass claim | fresh spec review を実行し、fail finding は修正して再レビューする | review request | `review_status: pass` | G1 scope、closure index、execution readiness、branch baton | Reviewer Gate Status |
| S99 | M99 | all | report evidence、test/lint outputs、git diff、fresh final reviewers | changed files only | unrecorded verification、dirty handoff、reviewer gate bypass | issue-local handoff gate を実行し、qa-reviewer / issue-wide code-reviewer / final spec-reviewer の三者 pass 後に commit candidate を確定する | N/A | focused tests、`make lint`、`validate`、`git diff --check`、three-reviewer final gate | 検証証跡、未実施理由、三者 reviewer pass が report にあるか | M99 closure / commit candidate |

### Spec-Locked Closure Index

| Closure ID | 対応AC | 対応Step | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Report ledger destination |
|---|---|---|---|---|---|---|---|---|---|
| C-001 | AC-001 | S01 | `requirement.md#6` / AC-001 | Lite / Standard / Strict / Critical の requirement / design / plan / review / report evidence rules が確認できる | docs / skill text に grade matrix がある | grade-aware guidance absence | yes | docs inspection + rg | Closure Coverage / Test Contract Closure |
| C-002 | AC-002 / AC-003 | S01 | `requirement.md#6` / AC-002-003 | Lite は automatic default ではなく、unknown / ambiguous は Standard 以上へ倒れる | docs / skill text に Lite non-default と unknown fallback がある | accidental Lite default | yes | docs inspection + rg | Closure Coverage / Test Contract Closure |
| C-003 | AC-004 | S01 | `requirement.md#6` / AC-004 | `authorized_profile` は runtime template / guidance / obligation authority、manual escalation は gate strengthening と読める | docs / skill text に authority split がある | authority override confusion | yes | docs inspection + rg | Closure Coverage / Test Contract Closure |
| C-004 | AC-005 / AC-006 | S02 | `requirement.md#6` / AC-005-006 | Standard は specialist 推奨/未使用理由、Strict/Critical は原則必須/利用不可時 fallback evidence を示す | phase docs / skill text に specialist rule と report destination がある | missing specialist evidence | yes | docs inspection + rg | Closure Coverage / Test Contract Closure |
| C-005 | AC-007 | S03 | `requirement.md#6` / AC-007 | G2 draft routing、G3 report evidence gate、G4 smoke matrix が参照できる stable wording を提供する | docs / skill text に downstream reference terms がある | downstream wording drift | yes | docs inspection + rg | Closure Coverage / Test Contract Closure |
| C-090 | docs parity | S90 | `design.md#8` | provider と dogfooding mirror の該当 docs / skill が整合する | provider/dogfooding file comparison | source-of-truth drift | yes | diff / rg / validate | Closure Coverage |
| C-095 | reviewer gate | S95 | `plan.md#7` | fresh `spec-reviewer` が pass する | reviewer output | stale/self review | yes | reviewer pass | Reviewer Gate Status |
| C-099 | final handoff | S99 | `plan.md#7` | focused tests、lint、validate、report evidence、qa-reviewer / code-reviewer / spec-reviewer pass、commit candidate が揃う | command outputs / reviewer outputs / git status | dirty, unverified, or unreviewed handoff | yes | command + three-reviewer gate | Reviewer Gate Status / Milestone Commit Candidate Gate |

### Step Cards

#### S00 Baseline Inspection

- planned contract:
  - scope: 現行 docs / skill / guidance wording の baseline と gap を調査する。
  - test obligation: inspect-only。変更前の authority surface と wording gap を report に固定する。
  - red or alternative evidence requirement: `inspect-only`
  - green verification: `report.md` の S00 evidence に対象ファイル、既存 wording、gap、non-scope を記録する。
  - refactor guardrail: 実装変更を行わない。
  - amendment trigger: baseline 調査で ADR と Epic design の意味衝突を見つけた場合は execution に進まず plan amendment / ADR amendment を検討する。
- delegation contract:
  - delegated role: N/A（orchestrator read-only inspection）
  - input docs: Epic #224 requirement/design/plan、ADR `20260630t111316z`、active issue docs、provider/dogfooding docs、issue-planning skill。
  - allowed paths: read-only。report evidence のみ記録可。
  - forbidden changes: docs / skill / runtime implementation change。
  - acceptance criteria: C-001〜C-005 の source surface と gap が report に記録される。
  - required tests or docs-only verification: `rg` inspection。
  - reviewer focus: S00 の調査が G1 scope に閉じているか。
  - stop conditions: ADR meaning conflict、G2/G3/G4 implementation が必要、source-of-truth が特定できない。
  - output required: inspected files、gap summary、no-op / next-step decision、unresolved risks。
- 具体テストケース一覧:
  - `tc-s00-001` inspection: baseline owner surface を固定する
    - 前提: active issue は `iss-00252`。
    - 操作: provider/dogfooding docs と issue-planning skill を `rg` で確認する。
    - 期待結果: G1 が触る owner surface と gaps が `report.md` に記録される。
    - 失敗検出: 実装前に owner surface が曖昧なまま S01 に進む。
    - 検証方法: report inspection。
    - 関連 closure id: C-001〜C-005
- step closure contract:
  - close condition: S00 evidence が report にあり、G1 scope 外の実装が始まっていない。
  - report evidence destination: TDD table、Discovered Tests、Step Contract Closure。

#### S01 Grade Selection / Authority Split

- planned contract:
  - scope: grade matrix、Lite non-default、unknown -> Standard 以上、`authorized_profile` / manual escalation split を docs / skill wording に追加する。
  - test obligation: docs-only verification と必要な focused guidance regression。
  - red or alternative evidence requirement: `inspect-only`
  - green verification: provider/dogfooding docs parity、skill parity、required wording の `rg` inspection。
  - refactor guardrail: ADR の meaning を変えない。automatic Lite default を導入しない。
  - amendment trigger: Lite default、authority override、runtime routing 変更が必要になった場合。
- delegation contract:
  - delegated role: doc-writer
  - input docs: `requirement.md` AC-001〜AC-004、ADR、Epic design、`workflow_spec_authoring.md`、issue-planning skill。
  - allowed paths: `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`、`spec-dock/docs/workflow_spec_authoring.md`、必要な issue-planning skill mirror。
  - forbidden changes: runtime routing、draft generation、report enforcement、ADR rewrite、parent direct implementation without Parent Implementation Exception。
  - acceptance criteria: C-001、C-002、C-003。
  - required tests or docs-only verification: `rg` で `Lite`、`Standard`、`Strict`、`Critical`、`authorized_profile`、`manual escalation` 相当の日本語 wording を確認。
  - reviewer focus: AC-001〜AC-004 が過不足なく表現され、G2/G3/G4 実装に踏み込まないか。
  - stop conditions: required wording を日本語で自然に置けない、skill と docs が矛盾、許可パス外変更が必要、doc-writer 委任が利用不可で Parent Implementation Exception が未記録。
  - output required: delegated worker summary、changed files、wording summary、rg results、unresolved risks、report evidence。親は delegated output の採用・統合のみを行う。親が直接編集する場合は `report.md` の Parent Implementation Exception に approved-local-execution と許可ファイル、検証、reviewer gate を記録してから行う。
- 具体テストケース一覧:
  - `tc-s01-001` docs: grade matrix が確認できる
    - 前提: provider / dogfooding docs が存在する。
    - 操作: grade matrix wording を追加し、`rg` で確認する。
    - 期待結果: Lite / Standard / Strict / Critical の authoring rule が docs / skill から読める。
    - 失敗検出: 一律 Strict または旧 step-centric planning に戻る wording。
    - 検証方法: docs inspection + `rg`。
    - 関連 closure id: C-001
  - `tc-s01-002` docs: Lite non-default と unknown fallback
    - 前提: grade 判断が曖昧な issue。
    - 操作: docs / skill wording を確認する。
    - 期待結果: Lite は明示根拠がある場合のみ、unknown / ambiguous は Standard 以上と読める。
    - 失敗検出: Lite automatic default に読める wording。
    - 検証方法: docs inspection + `rg`。
    - 関連 closure id: C-002
  - `tc-s01-003` docs: authority split
    - 前提: `authorized_profile` と manual escalation が同時に出る。
    - 操作: docs / skill wording を確認する。
    - 期待結果: `authorized_profile` は runtime/template/guidance obligation authority、manual escalation は gate strengthening と読める。
    - 失敗検出: manual escalation が authority override と読める wording。
    - 検証方法: docs inspection + `rg`。
    - 関連 closure id: C-003
- step closure contract:
  - close condition: C-001〜C-003 が report の Closure Coverage に pass として記録される。
  - report evidence destination: TDD table、Test Contract Closure、Closure Coverage。

#### S02 Authoring Rules / Specialist Fallback

- planned contract:
  - scope: requirement/design/plan authoring rule、Standard specialist 推奨/未使用理由、Strict/Critical specialist 原則必須/利用不可時 fallback evidence を docs / skill に追加する。
  - test obligation: docs-only verification と skill wording inspection。
  - red or alternative evidence requirement: `inspect-only`
  - green verification: provider/dogfooding docs parity、skill parity、specialist/fallback/report evidence wording の `rg` inspection。
  - refactor guardrail: G3 の report evidence enforcement を実装しない。
  - amendment trigger: report validation runtime change、new doc routing implementation、role policy rewrite が必要になった場合。
- delegation contract:
  - delegated role: doc-writer
  - input docs: AC-005〜AC-006、ADR、Epic design、`phase_requirement.md`、`phase_design.md`、`phase_plan_issue.md`、issue-planning skill。
  - allowed paths: provider/dogfooding phase docs、issue-planning skill mirror。
  - forbidden changes: runtime enforcement、new doc routing、report gate validation。
  - acceptance criteria: C-004。
  - required tests or docs-only verification: `rg` で Standard / Strict / Critical / specialist / fallback / report evidence wording を確認。
  - reviewer focus: specialist rule が gradeごとに読め、過剰に委任必須化しないか。
  - stop conditions: role unavailable handling が曖昧、G3 enforcement に踏み込む必要がある、skill/docs parity が崩れる。
  - output required: changed files、wording summary、rg results、fallback evidence destination、report evidence。
- 具体テストケース一覧:
  - `tc-s02-001` docs: Standard specialist 推奨と未使用理由
    - 前提: Standard issue の design / plan authoring。
    - 操作: phase docs / skill wording を確認する。
    - 期待結果: specialist 推奨条件と未使用理由の report destination が読める。
    - 失敗検出: Standard で specialist が常に必須、または不要理由が不要に見える wording。
    - 検証方法: docs inspection + `rg`。
    - 関連 closure id: C-004
  - `tc-s02-002` docs: Strict / Critical fallback evidence
    - 前提: specialist が unavailable / denied / host conflict。
    - 操作: phase docs / skill wording を確認する。
    - 期待結果: 原則必須、利用不可時の manual fallback evidence と report destination が読める。
    - 失敗検出: fallback が無証跡で許可される wording。
    - 検証方法: docs inspection + `rg`。
    - 関連 closure id: C-004
- step closure contract:
  - close condition: C-004 が report の Closure Coverage に pass として記録される。
  - report evidence destination: TDD table、Test Contract Closure、Closure Coverage。

#### S03 Downstream Stable Wording

- planned contract:
  - scope: G2 draft routing、G3 report evidence gate、G4 smoke matrix が参照できる stable terms と stop condition を整える。
  - test obligation: docs-only verification。
  - red or alternative evidence requirement: `inspect-only`
  - green verification: `rg` inspection で downstream terms が docs / skill に存在する。
  - refactor guardrail: G2/G3/G4 の実装本体に踏み込まない。
  - amendment trigger: downstream issue の scope を変更する必要がある場合。
- delegation contract:
  - delegated role: doc-writer
  - input docs: AC-007、Epic plan G2〜G4、iss-00253〜iss-00255 draft docs。
  - allowed paths: S01/S02 で触る docs / skill。
  - forbidden changes: downstream issue implementation、runtime routing、smoke matrix implementation。
  - acceptance criteria: C-005。
  - required tests or docs-only verification: `rg` で draft routing / report evidence gate / integrated smoke matrix 相当の wording を確認。
  - reviewer focus: AC-007 が G2/G3/G4 すべてを含むか。
  - stop conditions: downstream issue の責務が重複、wording が implementation を要求する。
  - output required: changed files、downstream terms、rg results、report evidence。
- 具体テストケース一覧:
  - `tc-s03-001` docs: downstream terms
    - 前提: G2 / G3 / G4 が後続 issue として残っている。
    - 操作: docs / skill wording を確認する。
    - 期待結果: draft routing、report evidence gate、integrated smoke matrix が stable terms として参照できる。
    - 失敗検出: G4 が欠落する、または G2/G3/G4 の実装を G1 に混ぜる wording。
    - 検証方法: docs inspection + `rg`。
    - 関連 closure id: C-005
- step closure contract:
  - close condition: C-005 が report の Closure Coverage に pass として記録される。
  - report evidence destination: TDD table、Test Contract Closure、Closure Coverage。

#### S90 Parity Gate

- planned contract:
  - scope: provider / dogfooding mirror parity を確認する。
  - test obligation: docs / skill parity inspection。
  - red or alternative evidence requirement: `inspect-only`
  - green verification: `diff` / `rg` inspection、`./spec-dock/scripts/spec-dock validate`。
  - refactor guardrail: source of truth は provider 側を優先する。
  - amendment trigger: provider / dogfooding の構造差が単純 mirror で解決できない場合。
- delegation contract:
  - delegated role: N/A or doc-writer
  - input docs: changed provider/dogfooding files。
  - allowed paths: changed docs / skill mirrors。
  - forbidden changes: unrelated formatting / unrelated generated artifacts。
  - acceptance criteria: C-090。
  - required tests or docs-only verification: `git diff --check`、`./spec-dock/scripts/spec-dock validate`、targeted `rg`。
  - reviewer focus: provider優先とdogfooding整合。
  - stop conditions: mirror mismatch、validate failure、unexplained dogfooding-only change。
  - output required: parity result、commands、risks。
- 具体テストケース一覧:
  - `tc-s90-001` parity: provider / dogfooding mirrors
    - 前提: docs / skill を変更済み。
    - 操作: provider と dogfooding の該当 wording を比較する。
    - 期待結果: 意図した差分以外の不整合がない。
    - 失敗検出: provider だけ更新、または dogfooding だけ更新。
    - 検証方法: `rg` / diff inspection / validate。
    - 関連 closure id: C-090
- step closure contract:
  - close condition: C-090 が pass として記録される。
  - report evidence destination: Closure Coverage、M99 command evidence。

#### S95 Fresh Spec Review

- planned contract:
  - scope: planning / implementation diff の fresh spec review。
  - test obligation: reviewer gate。
  - red or alternative evidence requirement: review request。
  - green verification: `review_status: pass`。
  - refactor guardrail: self-pass claim をしない。
  - amendment trigger: `review_status: fail` または P0/P1 finding が出た場合は修正して再レビュー。`review_status: pass` かつ P2/P3 finding のみの場合は、issue owner が修正を選ぶか、report に follow-up / non-blocking rationale を記録する。
- delegation contract:
  - delegated role: spec-reviewer
  - input docs: current diff、active issue docs、Epic docs、ADR。
  - allowed paths: read-only。
  - forbidden changes: file modification、waiver without user approval。
  - acceptance criteria: C-095。
  - required tests or docs-only verification: reviewer output。
  - reviewer focus: G1 scope、closure index、execution readiness、branch baton。
  - stop conditions: reviewer unavailable / denied / `review_status: fail` / P0-P1 finding。
  - output required: findings、review_status、confidence、adoption decision in report。
- 具体テストケース一覧:
  - `tc-s95-001` review: fresh spec-reviewer pass
    - 前提: S00〜S90 evidence が揃っている。
    - 操作: fresh spec-reviewer を実行する。
    - 期待結果: `review_status: pass`。
    - 失敗検出: `review_status: fail`、P0/P1 findings、stale/self review。`review_status: pass` かつ P2/P3 findings のみの場合は report に follow-up / non-blocking rationale を記録する。
    - 検証方法: reviewer output。
    - 関連 closure id: C-095
- step closure contract:
  - close condition: C-095 が pass として記録される。
  - report evidence destination: Reviewer Gate Status。

#### S99 Final Handoff

- planned contract:
  - scope: issue-local final quality gate と commit candidate。
  - test obligation: focused tests、lint、validate、diff clean、qa-reviewer / issue-wide code-reviewer / final spec-reviewer の三者最終品質ゲート。
  - red or alternative evidence requirement: N/A。
  - green verification: required command pass または未実施理由が report にあり、三者 reviewer gate が pass している。
  - refactor guardrail: 未完了差分を次 issue に渡さない。
  - amendment trigger: final gate failure、unrecorded verification、dirty worktree。
- delegation contract:
  - delegated role: qa-reviewer / code-reviewer / spec-reviewer for final gate; N/A for command execution
  - input docs: report evidence、changed files、test/lint outputs。
  - allowed paths: changed files only。
  - forbidden changes: unrelated cleanup、unstaged hidden diff。
  - acceptance criteria: C-099。
  - required tests or docs-only verification: focused tests、`make lint`、`./spec-dock/scripts/spec-dock validate`、`git diff --check`、fresh qa-reviewer pass、fresh issue-wide code-reviewer pass、fresh final spec-reviewer pass。
  - reviewer focus: QA は test sufficiency と behavior coverage、code-reviewer は implementation diff / maintainability / regression risk、spec-reviewer は requirement/design/plan alignment と report evidence completeness。
  - stop conditions: failing command、unrecorded risk、dirty uncommitted diff after commit、いずれかの final reviewer unavailable / denied / failed。
  - output required: command outputs、three reviewer outputs、commit hash、post-commit clean status。
- 具体テストケース一覧:
  - `tc-s99-001` final gate: command evidence
    - 前提: implementation diff と report evidence が揃っている。
    - 操作: focused tests / lint / validate / diff check を実行する。
    - 期待結果: pass または明示された未実施理由。
    - 失敗検出: PR 後 CI で初めて基礎失敗を発見する状態。
    - 検証方法: command output。
    - 関連 closure id: C-099
  - `tc-s99-002` final reviewers: three-reviewer quality gate
    - 前提: command evidence と report ledger が揃っている。
    - 操作: qa-reviewer、issue-wide code-reviewer、final spec-reviewer を fresh に実行する。
    - 期待結果: 3 reviewer が pass し、Reviewer Gate Status に記録される。
    - 失敗検出: test sufficiency、code diff、spec alignment のいずれかが未レビューのまま commit 候補になる。
    - 検証方法: reviewer output。
    - 関連 closure id: C-099
- step closure contract:
  - close condition: C-099 が pass として記録され、commit candidate が作れる。
  - report evidence destination: Milestone / Commit Candidate Gate。

### Plan Amendment Trigger

- draft routing implementation、report evidence enforcement、integrated smoke matrix、または automatic Lite default が必要になった場合は、この Issue で吸収せず G2 / G3 / G4 または Epic planning へ戻す。
- Grade-aware authoring rule の meaning を ADR から変更する必要が出た場合は、ADR amendment を先に行う。

## 8. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00253` に渡せる local closure checkpoint とする。
- M99 通過後、grade-aware guidance、docs / tests、report evidence を commit し、その HEAD から `iss-00253` の branch を開始する。
- G2 / G3 が並列可能に見える場合でも、この Epic PR では抜け漏れ・重複を避けるため default baton order を `iss-00253 -> iss-00254` とする。
