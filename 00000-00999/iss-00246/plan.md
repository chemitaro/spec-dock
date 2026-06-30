---
種別: 実装計画書（Issue）
ID: "iss-00246"
タイトル: "Dogfooding Update Runtime Mirror Sync"
関連GitHub: ["#246"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00246 Dogfooding Update Runtime Mirror Sync — Issue 実装計画

## 1. この計画で満たす要件ID

| 要件 | 対応 Closure | 主な検証 |
|---|---|---|
| RQ-001 / AC-001 | CLOS-001 | stale runtime file refresh test |
| RQ-002 / AC-002 | CLOS-002 | inventory-driven dogfooding parity test |
| RQ-003 / AC-003 | CLOS-003 | update preservation regression |
| RQ-004 / AC-004 | CLOS-004 | cache exclusion assertions |
| RQ-005 / AC-005 | CLOS-005 | local/package update smoke |
| RQ-006 / AC-006 | CLOS-006 | report evidence ledger |

## 2. 実行方針

本 Issue は TDD/characterization-first で進める。最初に stale runtime mirror が update で provider bytes へ戻ることを focused test で固定し、次に checked-in dogfooding parity を provider inventory 由来へ広げる。Red が production defect を示した場合のみ `src/spec_dock/cli.py` または `pyproject.toml` を最小修正する。現行 production code がすでに Green の場合は、test/parity hardening と report evidence を成果とし、code no-op を明記する。

## 3. 変更許可範囲

| 種別 | パス | 許可する変更 |
|---|---|---|
| tests | `tests/unit/infra/test_init_update.py` | update/parity/package smoke regression の追加・既存 helper の最小整理 |
| installer | `src/spec_dock/cli.py` | test が示す defect を直す最小変更のみ |
| package metadata | `pyproject.toml` | runtime asset が配布物から漏れている場合の最小修正のみ |
| dogfooding mirror | `spec-dock/scripts/spec_dock_runtime/**` | provider runtime と一致させる必要がある場合のみ |
| issue docs | `spec-dock/active/issue/{requirement,design,plan,report}.md` | 実行証跡、判断、closure の更新 |

## 4. 禁止変更

| 対象 | 禁止理由 | 必要になった場合 |
|---|---|---|
| `spec-dock update` の command name / required args | public CLI contract 変更になる | 停止して requirement/design を更新し、再レビュー |
| `spec-dock/initiatives/**` の preservation contract | user-authored data loss risk | 停止して別 Issue または strict 引き上げ |
| live GitHub network 前提の test | hermetic regression にならない | fake/stub/isolated local target へ置換 |
| manual copy only の恒久対応 | Issue #246 の再発防止にならない | regression test または installer fix へ戻す |

## 5. Spec-Locked Closure Index

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug / risk guarded | Required | Owner step | Evidence level | Planned verification evidence path | Report evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| CLOS-001 | `requirement.md` AC-001 / `design.md` DES-001 | target repo with stale `spec-dock/scripts/spec_dock_runtime/application/workflow.py` | `spec-dock update <target>` refreshes stale runtime file to provider bytes | update success leaves stale runtime mirror | yes | S01 | focused pytest / CLI-like unit | `tests/unit/infra/test_init_update.py` focused test output | `report.md` Step Contract Closure / Test Contract Closure |
| CLOS-002 | `requirement.md` AC-002 / `design.md` DES-002 | provider runtime inventory and checked-in dogfooding mirror inventory | cache-excluded runtime path set and bytes match; subset map omission cannot pass | new provider runtime file omitted from mirror parity | yes | S02 | focused pytest / inspection | `tests/unit/infra/test_init_update.py` parity test output | `report.md` Closure Coverage / Test Contract Closure |
| CLOS-003 | `requirement.md` AC-003 / `design.md` DES-003 | target repo containing user-authored data and unmanaged marker before update | update preserves user-authored data and unmanaged marker while refreshing managed runtime | runtime refresh deletes initiatives or unmanaged files | yes | S01 | focused pytest plus existing preservation regression | S01 focused test and relevant existing preservation tests | `report.md` Step Contract Closure |
| CLOS-004 | `requirement.md` AC-004 / `design.md` DES-002 | provider runtime tree containing generated cache artifacts | cache artifacts are ignored by update/parity and do not create false failures | `__pycache__` / `.pyc` copied or compared as source | yes | S02 | focused pytest / structural inspection | S02 parity helper assertions | `report.md` Test Contract Closure / Discovered Tests |
| CLOS-005 | `requirement.md` AC-005 / `design.md` DES-004 | local checkout or package-like installer with stale isolated target | package/local update path includes runtime assets and refreshes stale file | `uvx --from .`-like path misses packaged runtime assets | yes | S03 | package-like smoke or approved equivalent | S03 isolated package-like smoke, or package data inspection plus update behavior test | `report.md` Command Evidence / Test Contract Closure |
| CLOS-006 | `requirement.md` AC-006 / `design.md` DES-005 | implementation findings, no-op/code-change decision, final verification results | root cause, code/no-op rationale, and AC closure evidence are recorded | issue completes without durable evidence of what was fixed or proven | yes | S04 / S90 / S99 | docs inspection / review gate | `report.md` decision ledger, closure coverage, final quality gate | `report.md` Decision Ledger / Final Quality Gate |

## 6. 実装ステップ

### S01: stale runtime mirror refresh を characterization する

#### behavior goal

`spec-dock update <target>` が managed runtime mirror を provider 正本へ戻し、同時に user-authored data preservation を壊さないことを固定する。

#### planned contract

- scope: `tests/unit/infra/test_init_update.py` の focused update regression。
- test obligation: AC-001 の positive refresh と AC-003 の preservation guard を同一 target で観測する。
- red or alternative evidence requirement: `red-required`。既存 code が Green の場合は characterization Green とし、sensitivity は stale fixture の更新 assertion で担保する。
- green verification: focused pytest で stale runtime file bytes と preservation marker を確認する。
- refactor guardrail: test helper 整理は同一 file 内に限定し、production code へ進むのは Red が installer defect を示す場合だけ。
- amendment trigger: update preservation が壊れる、または public CLI contract 変更が必要になる場合は plan/design amendment と再レビュー。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md` AC-001/AC-003、`design.md` DES-001/DES-003、this `plan.md` S01、`tests/unit/infra/test_init_update.py`
- allowed paths: `tests/unit/infra/test_init_update.py`; Red が production defect を示した場合のみ `src/spec_dock/cli.py`
- forbidden changes: `spec-dock/initiatives/**` data mutation、CLI command/argument rename、live network dependency、S02/S03 の parity/package smoke scope の先取り
- acceptance criteria: CLOS-001 と CLOS-003 が focused pytest で close できる
- required tests or docs-only verification: S01 focused pytest、必要なら既存 update preservation test selection
- reviewer focus: `code-reviewer` は test sensitivity、preservation regression、production change 最小性を確認する
- stop conditions: stale file fixture が provider bytes と比較できない、許可パス外変更が必要、update が user-authored data を消す
- output required: changed files、pytest result、Red/Green 判定、production fix 有無、unresolved risks、`report.md` に転記する Ledger Note

#### 具体テストケース一覧

- `tc-s01-001` acceptance: stale runtime file が update で provider bytes に戻る
  - 前提: temp target の `spec-dock/scripts/spec_dock_runtime/application/workflow.py` を provider 正本と異なる stale content にする。
  - 操作: current checkout の `spec-dock update <target>` 相当を実行する。
  - 期待結果: target runtime file が `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py` と byte-level で一致する。
  - 失敗検出: stale content が残る、file が欠落する、または provider bytes と異なる内容になる。
  - 検証方法: `tests/unit/infra/test_init_update.py` の focused pytest。
  - 関連 closure id: `CLOS-001`

- `tc-s01-002` regression: runtime refresh は user-authored data を消さない
  - 前提: temp target に existing initiative data、active metadata、unmanaged marker を置いたうえで runtime file を stale にする。
  - 操作: `spec-dock update <target>` 相当を実行する。
  - 期待結果: stale runtime file は provider bytes へ戻り、user-authored data と unmanaged marker は残る。
  - 失敗検出: runtime は更新されるが `spec-dock/initiatives/**` または unmanaged marker が消える。
  - 検証方法: S01 focused pytest、必要なら既存 preservation regression の targeted selection。
  - 関連 closure id: `CLOS-003`

#### step closure contract

- closes: CLOS-001, CLOS-003
- close condition: `tc-s01-001` と `tc-s01-002` が pass し、production code 変更の有無が report に記録されている。

#### report evidence destination

`report.md` の実装記録、TDD / Red / Green / Refactor Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage。

#### step gate

S01 が fail したまま S02/S03 へ進まない。production defect が見つかった場合は S04 で最小修正し、S01 を再実行する。

### S02: checked-in dogfooding runtime parity を inventory-driven にする

#### behavior goal

checked-in dogfooding runtime mirror parity を provider runtime inventory 由来にし、subset map 漏れと generated cache false positive を防ぐ。

#### planned contract

- scope: `tests/unit/infra/test_init_update.py` の dogfooding parity helper/test。
- test obligation: AC-002 の full runtime inventory parity と AC-004 の cache exclusion。
- red or alternative evidence requirement: `characterization-first`。現在 drift がなければ Green でも、future missing/extra/content drift を検出できる assertion にする。
- green verification: provider/dogfood runtime の relative path set と bytes が一致し、cache suffix/directory が除外される。
- refactor guardrail: 既存 subset map を残す場合は目的を分離し、二重管理による stale list を作らない。
- amendment trigger: provider/dogfood に意図的な非対称 file が必要と判明した場合は design/plan amendment と再レビュー。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md` AC-002/AC-004、`design.md` DES-002、this `plan.md` S02、`tests/unit/infra/test_init_update.py`
- allowed paths: `tests/unit/infra/test_init_update.py`; actual drift がある場合のみ `spec-dock/scripts/spec_dock_runtime/**`
- forbidden changes: provider runtime behavior change、manual copy only の恒久対応、generated cache の checked-in 化、live network dependency
- acceptance criteria: CLOS-002 と CLOS-004 が parity test で close できる
- required tests or docs-only verification: focused parity pytest、cache exclusion inspection
- reviewer focus: `code-reviewer` は inventory completeness、cache ignore correctness、false green/false failure risk を確認する
- stop conditions: generated cache 以外の extra/missing file の扱いに設計判断が必要、allowed paths 外の runtime design 変更が必要
- output required: changed files、pytest result、parity inventory rule、ignored cache rule、unresolved drift、`report.md` に転記する Ledger Note

#### 具体テストケース一覧

- `tc-s02-001` acceptance: runtime parity は provider inventory 全体を比較する
  - 前提: provider runtime tree と checked-in dogfooding mirror tree が存在する。
  - 操作: dogfooding runtime parity test を実行する。
  - 期待結果: generated cache を除く provider/dogfood relative path set と bytes が一致する。
  - 失敗検出: missing file、extra file、content drift、または subset map にない file の未検出。
  - 検証方法: `tests/unit/infra/test_init_update.py` の focused parity pytest。
  - 関連 closure id: `CLOS-002`

- `tc-s02-002` regression: generated cache は parity/update source として扱わない
  - 前提: provider または dogfooding runtime tree に `__pycache__` / `.pyc` / `.pyo` 相当の generated artifact がある。
  - 操作: parity helper が比較対象 inventory を作る。
  - 期待結果: generated cache は比較対象から除外され、cache 差分だけで parity failure にならない。
  - 失敗検出: cache file が path set に入り false failure になる、または cache file が source としてコピー対象扱いされる。
  - 検証方法: focused pytest または helper-level structural assertion。
  - 関連 closure id: `CLOS-004`

#### step closure contract

- closes: CLOS-002, CLOS-004
- close condition: `tc-s02-001` と `tc-s02-002` が pass し、generated cache 除外 rule が report に記録されている。

#### report evidence destination

`report.md` の Test Contract Closure、Closure Coverage、Discovered Tests、Decision Ledger。

#### step gate

S02 が fail した場合、actual drift を provider 正本へ合わせるか design amendment へ戻すまで S99 へ進まない。

### S03: local checkout/package update smoke を追加する

#### behavior goal

Issue #246 の観測経路に近い local checkout/package 由来 update が runtime asset を含み、stale target を refresh できることを確認する。

#### planned contract

- scope: `tests/unit/infra/test_init_update.py` の package-like smoke または approved equivalent。
- test obligation: AC-005 の package/local update path。
- red or alternative evidence requirement: `red-required` が望ましい。実行コストが過大な場合だけ `covered-existing` または package data inspection + S01 update behavior の組み合わせを approved alternative として report に記録する。
- green verification: isolated target の stale runtime file が package/local installer 経路で provider bytes へ戻る。
- refactor guardrail: live network を使わず、local build/install helper または package data inspection に閉じる。
- amendment trigger: `uvx --from .` exact reproduction が hermetic test では不可能で、代替証跡でも AC-005 を説明できない場合。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md` AC-005、`design.md` DES-004、this `plan.md` S03、`pyproject.toml`、existing isolated install helpers in `tests/unit/infra/test_init_update.py`
- allowed paths: `tests/unit/infra/test_init_update.py`; package data defect が示された場合のみ `pyproject.toml`
- forbidden changes: network-required smoke、published package dependency、global environment mutation、unrelated packaging metadata churn
- acceptance criteria: CLOS-005 が package-like smoke または explicitly justified equivalent で close できる
- required tests or docs-only verification: package-like focused pytest、または package data inclusion inspection + S01 update behavior result
- reviewer focus: `code-reviewer` は hermeticity、package asset inclusion sensitivity、代替証跡の妥当性を確認する
- stop conditions: live GitHub/network が必要、test が host environment に依存して不安定、package metadata public contract 変更が必要
- output required: chosen evidence path、commands/results、changed files、代替証跡を使う場合の rationale、`report.md` に転記する Ledger Note

#### 具体テストケース一覧

- `tc-s03-001` acceptance: package-like update path でも runtime file が provider bytes に戻る
  - 前提: local checkout または build artifact 由来 installer と、stale runtime file を持つ isolated target がある。
  - 操作: package-like `spec-dock update <target>` を実行する。
  - 期待結果: target runtime file が provider runtime file と byte-level で一致する。
  - 失敗検出: packaged asset missing、stale content remaining、local direct path と package path の挙動差。
  - 検証方法: isolated focused pytest。重すぎる場合は approved alternative として package data inspection + S01 focused pytest を併記する。
  - 関連 closure id: `CLOS-005`

#### step closure contract

- closes: CLOS-005
- close condition: `tc-s03-001` または approved equivalent が pass し、選択した証跡経路が report に記録されている。

#### report evidence destination

`report.md` の Command Evidence、Test Contract Closure、Decision Ledger、Closure Coverage。

#### step gate

S03 の証跡が package/local 経路を説明できない場合、S99 へ進まず plan amendment または test strategy 再設計へ戻す。

### S04: production defect がある場合だけ最小修正する

#### behavior goal

S01-S03 の Red が production defect を示した場合だけ、root cause に対応する最小修正を行う。すべて Green の場合は approved-no-op として evidence を残す。

#### planned contract

- scope: Red の root cause に対応する最小 file set。
- test obligation: 修正対象 closure の failing test を Green にする。no-op の場合は no-op rationale と S01-S03 Green evidence を固定する。
- red or alternative evidence requirement: `covered-existing`。S01-S03 の Red/Green が S04 の入力証跡。
- green verification: 対象 focused tests の再実行。
- refactor guardrail: Issue #246 の runtime mirror update/parity 以外へ広げない。
- amendment trigger: public CLI contract、workspace layout、migration、security/privacy に触れる必要が出た場合。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md` RQ-006/AC-006、`design.md` DES-005、S01-S03 test results
- allowed paths: `src/spec_dock/cli.py`, `pyproject.toml`, `src/spec_dock/assets/spec_dock/**`, `spec-dock/scripts/spec_dock_runtime/**`, `tests/unit/infra/test_init_update.py`, `report.md`
- forbidden changes: unrelated refactor、manual sync only without regression、GitHub state mutation、destructive workspace cleanup
- acceptance criteria: failing closure tests pass, or no production defect found and approved-no-op is justified by S01-S03 evidence
- required tests or docs-only verification: affected focused pytest selection, `git diff --check`, no-op inspection when applicable
- reviewer focus: `code-reviewer` は root cause と最小性、`spec-reviewer` は requirement/design/plan 逸脱有無を確認する
- stop conditions: root cause が plan の想定外、allowed paths 外変更が必要、no-op rationale が AC-001/AC-005 を説明できない
- output required: root cause classification、changed files or no-op rationale、verification result、rollback/revisit note、`report.md` に転記する Ledger Note

#### 具体テストケース一覧

- `tc-s04-001` approved-no-op / fix confirmation: root cause と code/no-op 判定を閉じる
  - 前提: S01-S03 の test/inspection evidence が揃っている。
  - 操作: Red があれば最小修正して該当 focused tests を再実行し、Red がなければ no-op rationale を `report.md` に記録する。
  - 期待結果: root cause が installer defect、package data defect、dogfooding drift、test coverage gap、または approved-no-op として分類される。
  - 失敗検出: production change の理由が不明、または no-op が AC-001/AC-005 の証跡で支えられていない。
  - 検証方法: focused pytest result と `report.md` Decision Ledger inspection。
  - 関連 closure id: `CLOS-006`

#### step closure contract

- closes: CLOS-006 and any reopened closure from CLOS-001/CLOS-002/CLOS-004/CLOS-005
- close condition: root cause classification と code/no-op 判定が report に残り、該当 focused tests が pass している。

#### report evidence destination

`report.md` の Spec Interpretation / Decision Ledger、Evidence Adoption Ledger、Step Contract Closure、Closure Coverage。

#### step gate

S04 で plan 外の設計判断が必要になった場合、実装を止めて requirement/design/plan amendment と spec-reviewer re-review を行う。

### S90: docs / workflow 影響を判断する

#### behavior goal

Issue #246 の変更が user-facing docs、workflow docs、template/skill text に影響するかを判断し、必要な場合だけ docs 更新へ進める。

#### planned contract

- scope: docs impact inspection and, if needed, docs-only update delegation.
- test obligation: docs-only / approved-no-op alternative evidence。
- red or alternative evidence requirement: `inspect-only`。
- green verification: docs no-op rationale または docs diff + spec alignment review。
- refactor guardrail: code/test hardening のみなら persistent docs を変更しない。
- amendment trigger: operator-visible diagnostic や public update contract 文言が追加され、既存 docs と矛盾する場合。

#### delegation contract

- delegated role: `doc-writer` only if persistent docs/templates/skills need changes; otherwise main orchestrator records docs no-op in issue report
- input docs: S01-S04 results、`requirement.md` AC-006、`design.md` risks、relevant docs under `spec-dock/docs/**`
- allowed paths: docs update が必要な場合のみ relevant provider-side docs/templates/skills; issue report evidence is always allowed
- forbidden changes: source code/test changes、unrelated docs cleanup、workflow policy rewrite not required by this Issue
- acceptance criteria: CLOS-006 has docs impact result and no unreviewed docs obligation remains
- required tests or docs-only verification: docs inspection, `git diff --check`, spec-reviewer docs/spec alignment if docs changed
- reviewer focus: `spec-reviewer` verifies docs no-op or docs update aligns with requirement/design
- stop conditions: persistent docs change requires scope beyond Issue #246、doc-writer unavailable for required docs update
- output required: docs impact decision、changed docs or no-op rationale、review result、`report.md` note

#### 具体テストケース一覧

- `tc-s90-001` inspect-only: docs impact is resolved
  - 前提: S01-S04 の root cause と implementation result が report に記録されている。
  - 操作: update/public contract、diagnostic、template/skill text への影響を inspection する。
  - 期待結果: docs no-op または必要 docs update が明示され、必要 update は spec alignment review 対象になる。
  - 失敗検出: operator-visible behavior が変わったのに docs 影響が未判断、または docs no-op rationale がない。
  - 検証方法: `report.md` docs impact section inspection、必要なら docs diff review。
  - 関連 closure id: `CLOS-006`

#### step closure contract

- closes: CLOS-006 docs impact portion
- close condition: docs no-op or docs update evidence is recorded, and required review status is not pending.

#### report evidence destination

`report.md` Final Quality Gate / Docs Impact Resolution、Decision Ledger。

#### step gate

S90 が未解決のまま S99 final quality gate を pass しない。

### S99: final quality gate

#### behavior goal

Issue 完了可能性を、tests、SpecDock validation、diff hygiene、closure evidence、reviewer gates で確認する。

#### planned contract

- scope: final verification and review gating.
- test obligation: all required closures CLOS-001 through CLOS-006 have evidence.
- red or alternative evidence requirement: `covered-existing` for focused tests; `inspect-only` for ledger completeness.
- green verification: required commands pass and reviewer gates have pass or explicitly recorded non-blocking status.
- refactor guardrail: final gate で新規 scope を増やさない。finding が出たら該当 step に戻す。
- amendment trigger: closure evidence missing、reviewer fail、validation fail、or package/local smoke alternative not accepted.

#### delegation contract

- delegated role: `qa-reviewer` for test sufficiency, `code-reviewer` for integrated diff, `spec-reviewer` for requirement/design/plan/report alignment
- input docs: final diff, `requirement.md`, `design.md`, `plan.md`, `report.md`, focused test output, validation output
- allowed paths: read-only for reviewers; main orchestrator may update issue report with review evidence
- forbidden changes: reviewer agents do not edit files, reviewer pass is not a substitute for missing tests/evidence
- acceptance criteria: all required closure rows are closed or blocking finding is resolved by returning to owning step
- required tests or docs-only verification: `uv run pytest tests/unit/infra/test_init_update.py -q` or justified narrowed selection, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, `git status --short`
- reviewer focus: QA checks obligation coverage; code-reviewer checks implementation diff; spec-reviewer checks AC/design/plan/report closure consistency
- stop conditions: any reviewer `fail`, validation failure caused by this Issue, missing closure evidence, uncommitted unexpected files outside planned scope
- output required: commands/results、review statuses、remaining risks、commit/no-op candidate state、`report.md` final quality gate update

#### 具体テストケース一覧

- `tc-s99-001` gate: required verification commands pass
  - 前提: S01-S90 が完了し、report に closure evidence が記録されている。
  - 操作: required focused pytest、`spec-dock validate`、`git diff --check`、`git status --short` を実行する。
  - 期待結果: commands が pass し、status には planned files 以外の予期しない差分がない。
  - 失敗検出: test/validate/diff check failure、または unexpected dirty file。
  - 検証方法: command output を `report.md` Final Quality Gate に記録する。
  - 関連 closure id: `CLOS-001`, `CLOS-002`, `CLOS-003`, `CLOS-004`, `CLOS-005`, `CLOS-006`

- `tc-s99-002` gate: reviewer gates are satisfied
  - 前提: final diff と report evidence が揃っている。
  - 操作: required reviewer gates を read-only で実行する。
  - 期待結果: required reviewer が pass し、non-blocking residual risk は report に残る。
  - 失敗検出: reviewer fail、reviewer unavailable without explicit risk acceptance、または pass claim without fresh review evidence。
  - 検証方法: reviewer result を `report.md` Final Quality Gate に記録する。
  - 関連 closure id: `CLOS-006`

#### step closure contract

- closes: final closure confirmation for CLOS-001 through CLOS-006
- close condition: required commands and reviewer gates pass, report has closure coverage and final quality evidence.

#### report evidence destination

`report.md` Final Quality Gate、Reviewer Gate Status、Milestone / Commit Candidate Gate、Closure Coverage。

#### step gate

Any fail returns to the owning step. S99 cannot be used to waive missing implementation, test, or evidence obligations.

## 7. Review and Delegation Gate Notes

ユーザーは fresh な spec-reviewer による requirement/design/plan review を必須として明示した。実装開始前に spec-reviewer pass を `report.md` へ記録し、実装後の final verification では qa-reviewer / code-reviewer / spec-reviewer gate を必要に応じて再実行する。Delegated worker output は reviewer pass の代替ではない。

## 8. Open Questions

現時点でユーザーへの確認が必要な open question はない。技術的な未確定事項は S01-S04 で検証する。

## 9. Exit Criteria

- CLOS-001 から CLOS-006 が `report.md` で closed と記録されている。
- focused test が Green。
- `spec-dock validate` が Green。
- reviewer gate が必要な場合は fresh pass が記録されている。
- code no-op の場合でも、その理由と検証結果が report に記録されている。
