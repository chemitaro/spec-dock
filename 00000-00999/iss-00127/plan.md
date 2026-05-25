---
種別: 実装計画書（Issue）
ID: "iss-00127"
タイトル: "Scoped Discussion Draft Authoring Correction"
関連GitHub: ["#127"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00127 Scoped Discussion Draft Authoring Correction — 実装計画

## この計画で満たす要件ID
- AC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011
- EC: EC-001, EC-002, EC-003, EC-004, EC-005
- 制約:
  - canonical docs は main orchestrator single-writer authority。
  - sub-agent は target scope `discussions/` 直下の flat Markdown draft / analysis / discussion-local report を直接作成・編集できる。
  - proposal-only は標準運用にしない。
  - `iss-00126` historical artifacts は削除・rename・validation failure 化しない。

## 依存関係から導く実装順序
- S01 Runtime command contract:
  - 依存: design の CLI / domain contract。
  - unblock: manifest success path retirement と diff guard behavior。
  - 対象ファイル: runtime delegated_authoring command/application/domain/parser と runtime tests。
- S02 Shipped authoring contract:
  - 依存: S01 の user-facing behavior。
  - unblock: skills / adapters / workflow docs / templates の旧契約削除。
  - 対象ファイル: provider install_root assets、provider spec_dock docs/templates。
- S03 Dogfooding mirror and parity:
  - 依存: S01 / S02。
  - unblock: local `.agents` / `.codex` / `spec-dock` mirror consistency。
  - 対象ファイル: dogfooding mirror、parity tests。
- S90 Docs impact resolution:
  - 依存: S01-S03。
  - unblock: docs impact が残っていないこと。
- S99 Final quality gate:
  - 依存: S01-S90。
  - unblock: PR-ready state。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `delegated-authoring manifest` は deprecated / blocked / no artifact になり、`delegated-authoring diff-guard` が allowed / forbidden diff を判定する。
  - 閉じる要件: AC-003, AC-007, AC-009, EC-002, EC-004
  - レビューゲート: code-reviewer
- S02:
  - 観測可能な振る舞い: shipped skills/adapters/docs/templates が scope-local `discussions/` direct-write contract と canonical single-writer authority を説明し、asset wording tests が新 contract を固定する。
  - 閉じる要件: AC-001, AC-002, AC-004, AC-005, AC-006, AC-008, EC-001, EC-003, EC-005
  - レビューゲート: spec-reviewer and code-reviewer
- S03:
  - 観測可能な振る舞い: provider assets と dogfooding mirror が一致し、asset parity tests が新 contract を固定する。
  - 閉じる要件: AC-010
  - レビューゲート: code-reviewer または spec-reviewer
- S90:
  - 観測可能な振る舞い: docs impact が解消され、旧 manifest/Profile/canonical draft write contract が新規成功経路として残っていない。
  - 閉じる要件: AC-001, AC-002, AC-006, AC-008
  - レビューゲート: spec-reviewer
- S99:
  - 観測可能な振る舞い: targeted tests、validation、review gates が pass し、PR 作成可能である。
  - 閉じる要件: AC-011
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S02, S90
- AC-002 -> S02, S90
- AC-003 -> S01, S02
- AC-004 -> S02
- AC-005 -> S02
- AC-006 -> S02, S90
- AC-007 -> S01
- AC-008 -> S02, S90
- AC-009 -> S01
- AC-010 -> S03
- AC-011 -> S99
- EC-001 -> S02
- EC-002 -> S01
- EC-003 -> S02, S90
- EC-004 -> S01
- EC-005 -> S02, S90

## 仕様固定クロージャ索引
| ID | Step | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | acceptance | AC-009 | `manifest` command は non-zero / deprecated / blocked で artifact を生成しない | valid-looking old manifest args | 旧 manifest success path の復活 | yes | red-required | CLI / domain test output |
| tc-002 | S01 | acceptance | AC-007 | target scope `discussions/` 直下の naming-rule compliant new `.md` create は diff-guard pass | issue scope with new flat discussion draft named `<ts>-<kind>-<slug>.md` or `<ts>-<nn>-<kind>-<slug>.md` | 正当な discussion draft の false reject | yes | red-required | CLI / domain test output |
| tc-003 | S01 | negative | AC-007, EC-002 | canonical docs / src / tests / config / `.agents` / `.codex` / `.env*` diff は diff-guard fail | forbidden path diff | forbidden delegated output の採用 | yes | red-required | CLI / domain test output |
| tc-004 | S01 | negative | AC-007, EC-004 | nested dir / symlink / non-md / naming-rule noncompliant md / delete / rename / unallowlisted existing discussion update / dirty-baseline discussion / non-editable new discussion state claim は fail | malformed discussion diff | layout drift と過剰編集 | yes | red-required | domain / CLI test output |
| tc-005 | S02 | acceptance | AC-001, AC-002 | system-architect / implementation-planner skills は canonical direct-write を許さず、scope-local flat `discussions/` direct-write を許す | skill text inspection | 権限境界の逆戻り | yes | inspect-only | rg / asset test / spec-reviewer |
| tc-006 | S02 | acceptance | EC-001 | static adapter は broad write と canonical target write を許可しない | adapter TOML inspection | broad permission の正当化 | yes | inspect-only | asset test / inspection |
| tc-007 | S02 | acceptance | AC-004, AC-008 | report templates は manifest-heavy required fields を標準契約にせず、Evidence Adoption Ledger と lightweight provenance を中心にする | report template inspection | 複雑 metadata contract の残存 | yes | inspect-only | asset test / spec-reviewer |
| tc-008 | S03 | acceptance | AC-010 | provider assets と dogfooding mirror が一致する | update / sync / parity tests | provider/mirror drift | yes | covered-existing | tests/test_init_update.py / sync |
| tc-009 | S90 | acceptance | AC-006, EC-003 | ADR / discussion / canonical authority boundary と historical grandfathering が docs に残る | docs inspection | 過去証跡の破壊・authority 混同 | yes | inspect-only | spec-reviewer |
| tc-010 | S99 | acceptance | AC-011 | targeted tests、validate、sync、doctor、diff check、review gates が pass | final working tree | integration regression | yes | covered-existing | final report ledger |

## 実装ステップ S01 — Runtime delegated-authoring behavior
- 振る舞いの目標:
  - `delegated-authoring manifest` を fail-closed stub に変更し、新規 artifact を生成しない。
  - `delegated-authoring diff-guard` を追加し、delegated output の path-level eligibility を判定する。
- design 参照:
  - `design.md` の「インターフェース契約」「依存関係分析」。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
  - `tests/domain_runtime/test_delegated_authoring.py`
- Red / 代替証跡の要件:
  - red-required: 旧 manifest success path tests を新 expectation に書き換え、実装前に fail を確認する。
  - red-required: diff-guard allowed / forbidden tests を追加し、実装前に fail を確認する。allowed case は `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md` 命名規則に適合した file だけを使う。
- 実装範囲:
  - allowed paths: 対象 runtime / runtime tests のみ。
  - forbidden changes: docs / skills / adapter / mirror 変更は S02/S03 へ送る。
- Green 検証:
  - `python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v`
- report 証跡の記録先:
  - Session Log、TDD Evidence、Step Contract Closure、Test Contract Closure、Reviewer Gate Status。
- amendment trigger:
  - git status parsing だけでは symlink / rename / baseline status を判定できない場合。
  - diff-guard が canonical docs を更新する必要が出た場合。

### S01 委任契約
- 委任ロール: dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`
- 許可 paths:
  - S01 対象ファイルのみ。
- 禁止 changes:
  - provider docs / skills / adapters / dogfooding mirror。
- 必須出力:
  - changed files、test result、unresolved risks。
- 停止条件:
  - diff-guard scope resolution が active scope と `.meta.json` の両方で確定できない。

### S01 具体テストケース一覧
- `tc-s01-001` acceptance: manifest command is deprecated and writes no artifacts
  - 前提: temp repo に `iss-00003` scope と valid-looking old input authority file がある。
  - 操作: `spec-dock delegated-authoring manifest --role system-architect --scope iss-00003 --target design --host-surface cli --input-authority-file <file>` を実行する。
  - 期待結果: command は non-zero、stdout は `spec-dock: blocked (delegated-authoring manifest)`、`status=deprecated`、`reason=deprecated_scope_local_discussion_drafts` を含み、`discussions/delegated-authoring/` は作成されない。
  - 失敗検出: 旧 manifest/profile/probe/session artifact 生成 success path の復活を検出する。
  - 検証方法: `tests/cli_runtime/test_delegated_authoring.py` と `tests/domain_runtime/test_delegated_authoring.py`。
  - 関連 closure id: `tc-001`
- `tc-s01-002` acceptance: diff-guard allows naming-rule compliant discussion draft create
  - 前提: target issue scope に `discussions/20260525t010203z-disc-agent-draft.md` または `discussions/20260525t010203z-01-disc-agent-draft.md` が新規追加されている。
  - 操作: `spec-dock delegated-authoring diff-guard --scope iss-00003` を実行する。
  - 期待結果: command は exit 0 で `spec-dock: ok (delegated-authoring diff-guard)` を出力する。
  - 失敗検出: 正当な flat discussion draft が rejected される false positive を検出する。
  - 検証方法: CLI test と domain classifier test。
  - 関連 closure id: `tc-002`
- `tc-s01-003` negative: diff-guard rejects forbidden paths
  - 前提: worktree diff に target issue `design.md`、`src/`、`tests/`、`.agents/`、`.codex/`、`.env.local` のいずれかが含まれる。
  - 操作: `spec-dock delegated-authoring diff-guard --scope iss-00003` を実行する。
  - 期待結果: command は non-zero で forbidden category detail を出力する。
  - 失敗検出: sub-agent output が canonical docs、implementation、tests、config、secret-adjacent path を変更しても採用資格ありになる回帰を検出する。
  - 検証方法: CLI test と domain classifier test。
  - 関連 closure id: `tc-003`
- `tc-s01-004` negative: diff-guard rejects malformed discussion diffs
  - 前提: target scope `discussions/` 配下に nested path、symlink、non-md、命名規則不適合 `.md`、delete、rename、allowlist されていない既存 discussion update、dirty-baseline discussion、または non-editable state claim を持つ新規 discussion がある。
  - 操作: domain classifier または CLI diff-guard を実行する。
  - 期待結果: それぞれ rejected / ineligible と判定され、detail に理由が残る。
  - 失敗検出: layout drift、同名既存 file の無断編集、非 Markdown 出力の採用を検出する。
  - 検証方法: `tests/domain_runtime/test_delegated_authoring.py`。
  - 関連 closure id: `tc-004`

### S01 step closure contract
- closure ids: `tc-001`, `tc-002`, `tc-003`, `tc-004`
- close 条件:
  - manifest stub と diff-guard allowed / forbidden cases の tests が pass する。
  - runtime command は no artifact side effect を守る。
- report evidence:
  - TDD Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status。
- refactor guardrail:
  - manifest-heavy rendering helpers は必要最小限の deprecated compatibility だけ残し、S01 で docs / skills / adapter wording へ広げない。

### S01 step gate
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: runtime command/application/domain/parser と runtime tests。
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 runtime / runtime tests / report evidence。

## 実装ステップ S02 — Shipped authoring contract
- 振る舞いの目標:
  - shipped skills / adapters / workflow docs / templates を、scope-local `discussions/` direct-write と canonical single-writer authority に揃える。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md`
  - `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md`
- Red / 代替証跡の要件:
  - inspect-only: `rg` で old manifest/Profile/canonical draft write wording を棚卸しする。
  - covered-existing / update-required: `tests/test_init_update.py` の asset wording assertions を新 contract へ更新する。
- 実装範囲:
  - allowed paths: S02 対象 provider assets と relevant asset tests。
  - forbidden changes: runtime behavior 変更は S01 へ戻す。
- Green 検証:
  - `python -m unittest tests.test_init_update -v` の targeted relevant tests。時間が長い場合は impacted test methods を先に実行し、S99 で broader run を行う。
  - `rg` inspection for forbidden old wording。
- report 証跡の記録先:
  - Evidence Adoption Ledger、Session Log、Docs Impact Resolution、Reviewer Gate Status。
- amendment trigger:
  - report template の required fields を削ることで workflow_issue.md の mandatory ledger semantics と衝突する場合。

### S02 委任契約
- 委任ロール: doc-writer
- 入力 docs / source of truth:
  - `requirement.md`, `design.md`, `plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/active/issue/discussions/rules.md`
  - accepted ADR and V2 discussion draft under `spec-dock/active/issue/discussions/`
- 許可 paths:
  - S02 provider docs / skills / adapters / templates。
- 禁止 changes:
  - runtime source / runtime tests。
- acceptance criteria:
  - closure ids `tc-005`, `tc-006`, `tc-007`, `tc-009` are satisfied.
  - old canonical direct-write / manifest-heavy success wording is absent except grandfathered historical references that are explicitly labeled as historical.
- required tests or docs-only verification:
  - `rg` inspection for old wording.
  - relevant `tests/test_init_update.py` asset wording / scaffold assertions.
  - spec-reviewer and code-reviewer pass for the mixed docs / asset-test step.
- reviewer focus:
  - spec-reviewer: requirement / design / docs alignment、旧権限契約の残存、user 方針との整合。
  - code-reviewer: `tests/test_init_update.py` の scaffold behavior assertions と shipped asset parity への影響。
- stop conditions:
  - docs change requires runtime behavior change outside S02.
  - required report template simplification conflicts with workflow_issue mandatory evidence semantics.
  - validation or relevant asset tests cannot be run or interpreted.
- output required:
  - changed files list.
  - docs/spec alignment summary.
  - `rg` inspection result and relevant test result.
  - unresolved risks or `No material implementation decisions beyond the approved plan.`
  - report evidence to update for Step Contract Closure, Test Contract Closure, Closure Coverage, and Reviewer Gate Status.

### S02 具体テストケース一覧
- `tc-s02-001` inspect-only: skills describe scope-local discussion direct-write and forbid canonical docs
  - 前提: provider skills for system-architect / implementation-planner are updated.
  - 操作: skill text と asset assertions を確認する。
  - 期待結果: canonical `requirement.md` / `design.md` / `plan.md` / `report.md` direct edit success path はなく、target scope `discussions/` flat Markdown direct-write が許可されている。
  - 失敗検出: 旧 verified task manifest / Permission Profile / canonical draft write 成功契約の残存を検出する。
  - 検証方法: `rg` inspection、`tests/test_init_update.py` の asset wording assertion、spec-reviewer。
  - 関連 closure id: `tc-005`
- `tc-s02-002` inspect-only: static adapters do not grant broad or canonical target write
  - 前提: provider `.codex/agents/system-architect.toml` と `implementation-planner.toml` are updated.
  - 操作: adapter TOML と repo guidance を確認する。
  - 期待結果: broad write、canonical target write、`.codex/permission-probe-evidence` natural output path、manifest/Profile/probe success prerequisite が削除されている。
  - 失敗検出: static adapter が broad permission を許可して post-run guard で正当化する回帰を検出する。
  - 検証方法: asset test、`rg` inspection、code-reviewer。
  - 関連 closure id: `tc-006`
- `tc-s02-003` inspect-only: report templates use lightweight adoption evidence
  - 前提: provider report templates and active-none reports are updated.
  - 操作: Evidence Adoption Ledger / Delegated Draft Evidence の required fields を確認する。
  - 期待結果: manifest path/hash、Permission Profile hash、probe/session invocation を standard required fields とせず、discussion draft provenance、diff-guard result、orchestrator adoption ledger を中心にしている。
  - 失敗検出: 複雑 metadata contract の標準要件への残存を検出する。
  - 検証方法: asset test、spec-reviewer。
  - 関連 closure id: `tc-007`
- `tc-s02-004` inspect-only: authority boundary and grandfathering are documented
  - 前提: workflow docs and discussion rules are updated.
  - 操作: ADR / discussion / canonical authority boundary と historical `iss-00126` grandfathering を確認する。
  - 期待結果: accepted ADR は architecture decision authority、discussion draft は evidence、canonical docs は implementation / phase authority と説明され、historical artifacts は削除・rename・validation failure 化しない。
  - 失敗検出: authority 混同や過去証跡破壊につながる docs drift を検出する。
  - 検証方法: `rg` inspection、spec-reviewer。
  - 関連 closure id: `tc-009`

### S02 step closure contract
- closure ids: `tc-005`, `tc-006`, `tc-007`, `tc-009`
- close 条件:
  - provider skills/adapters/docs/templates が requirement/design と整合する。
  - relevant `tests/test_init_update.py` assertions が新 contract を固定する。
- report evidence:
  - Docs Impact Resolution、Step Contract Closure、Test Contract Closure、Reviewer Gate Status。
- refactor guardrail:
  - docs-only text の修正で runtime behavior を変更しない。test assertion update は shipped asset contract の固定に限定する。

### S02 step gate
- step reviewer gate:
  - reviewers: spec-reviewer and code-reviewer
  - review 範囲: shipped docs / skills / adapters / templates / asset tests。
  - pass 条件: both `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 provider assets / asset tests / report evidence。

## 実装ステップ S03 — Dogfooding mirror and parity
- 振る舞いの目標:
  - provider changes を local dogfooding mirror に反映し、consumer workspace と shipped asset の差分意図を一致させる。
- 対象ファイル:
  - `.agents/skills/spec-dock-system-architect/SKILL.md`
  - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.codex/AGENTS.md`
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
  - `spec-dock/docs/**`
  - `spec-dock/templates/**`
  - `spec-dock/system/active-none/**`
  - `spec-dock/scripts/spec_dock_runtime/**`
  - `tests/test_init_update.py`
- Red / 代替証跡の要件:
  - covered-existing: provider/mirror parity assertions。
  - inspect-only: `git diff --name-status` で provider と mirror の対応を確認する。
- Green 検証:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock doctor`
  - impacted installer/update tests。
- amendment trigger:
  - `spec-dock update .` が current issue docs を上書きする可能性がある場合は実行前に停止し、sync / manual mirror only に切り替える。

### S03 委任契約
- 委任ロール: dev-coder または doc-writer
- 入力 docs / source of truth:
  - `requirement.md`, `design.md`, `plan.md`
  - S01 and S02 changed provider assets.
  - provider source paths under `src/spec_dock/assets/install_root/` and `src/spec_dock/assets/spec_dock/`.
  - dogfooding mirror paths `.agents/`, `.codex/`, and `spec-dock/`.
- 許可 paths:
  - S03 対象 mirror と parity tests。
- 禁止 changes:
  - active issue `requirement.md` / `design.md` / `plan.md` / `report.md` の内容変更は parent orchestrator が行う。
- acceptance criteria:
  - closure id `tc-008` is satisfied.
  - provider and dogfooding mirror reflect the same runtime / skill / adapter / docs / template contract.
  - `sync`, `validate`, and `doctor` pass or any limitation is recorded as non-blocking with rationale.
- required tests or docs-only verification:
  - impacted provider/mirror parity tests in `tests/test_init_update.py`.
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock doctor`
  - `git diff --name-status` inspection for provider / mirror correspondence.
- reviewer focus:
  - provider / mirror drift、consumer scaffold impact。
- stop conditions:
  - mirror update would overwrite active issue canonical docs.
  - provider/mirror drift cannot be reconciled without changing accepted design.
  - required parity verification cannot run or yields ambiguous output.
- output required:
  - changed files list grouped by provider and mirror.
  - sync / validate / doctor / parity test results.
  - drift summary and unresolved risks.
  - report evidence to update for Step Contract Closure, Test Contract Closure, Closure Coverage, and Reviewer Gate Status.

### S03 具体テストケース一覧
- `tc-s03-001` acceptance: provider and dogfooding mirror are synchronized
  - 前提: S01/S02 provider assets are updated.
  - 操作: dogfooding `.agents` / `.codex` / `spec-dock` mirror を provider から同期し、parity tests または diff inspection を実行する。
  - 期待結果: mirror は provider contract と一致し、active issue docs 以外に意図しない drift がない。
  - 失敗検出: provider だけ更新され、local dogfooding workspace が旧契約を出し続ける回帰を検出する。
  - 検証方法: `tests/test_init_update.py` impacted parity tests、`./spec-dock/scripts/spec-dock sync`、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock doctor`。
  - 関連 closure id: `tc-008`

### S03 step closure contract
- closure ids: `tc-008`
- close 条件:
  - provider/mirror parity is verified.
  - sync / validate / doctor are pass or any non-blocking limitation is recorded in report.
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status。
- refactor guardrail:
  - `spec-dock update .` が active issue docs を上書きする懸念がある場合は実行せず、manual mirror update と sync / validate / doctor に留める。

### S03 step gate
- step reviewer gate:
  - reviewer: code-reviewer for scaffold/runtime mirror changes; spec-reviewer if only docs mirror changes remain.
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 mirror / parity test / report evidence。

## ドキュメント影響の解消ステップ S90
- 対象:
  - docs / templates / workflow / skill / adapter guidance。
- 対応:
  - AC/EC と design の authority boundary が docs に反映されていることを確認する。
  - `rg` で旧成功経路の語彙を確認し、historical reference 以外に残る場合は修正または report に理由を記録する。
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: `review_status: pass`

## 最終品質ゲートステップ S99
- branch diff 範囲:
  - active issue docs、runtime、provider assets、dogfooding mirror、tests。
- 必須 validation:
  - `python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v`
  - impacted `tests.test_init_update` tests、可能なら `python -m unittest discover -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock doctor`
  - `git diff --check`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: obligation coverage と missing high-value tests。
  - pass 条件: `review_status: pass`
- final code review gate:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff。
  - pass 条件: `review_status: pass`
- final spec review gate:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
  - pass 条件: `review_status: pass`
- final commit gate:
  - report ledger を最終更新し、コミット後 `git status --short` を確認する。

## 最終完了条件
- AC/EC 達成:
  - AC-001..AC-011 と EC-001..EC-005 が report closure で pass または justified no-op。
- docs 影響解決:
  - S90 spec-reviewer pass。
- 全 implementation step 完了:
  - S01-S03 committed / approved-no-op。
- final quality gate pass:
  - qa-reviewer pass、code-reviewer pass、spec-reviewer pass。
- PR:
  - main 向け PR を作成し、merge-prepared 状態を確認する。

## Final Exit Contract
- `report.md` に S01-S03 / S90 / S99 の observed evidence、closure coverage、reviewer gates、commit/no-op evidence が記録されている。
- `git status --short` が意図した未コミット差分なし、または PR 作成直前に最終 commit 済みである。
- main 向け PR が作成され、CI / checks / reviewer feedback の状態を確認済みである。
- unresolved `Status=open` decision ledger entry、blocking Evidence Adoption Ledger entry、failed reviewer gate が残っていない。

## 追加実装計画追補 S04 — Agent permission taxonomy and scoped-write execution correction

この追補は、S01-S03 / S90 / S99 実施後に判明した requirement / design の矛盾を解消する追加修正作業である。既存の実施済みステップは編集せず、追加ステップとして扱う。

- 追加背景:
  - `discussions/20260524t235542z-disc-agent-permission-classification-gap-analysis.md` により、`system-architect` / `implementation-planner` が read-only static fallback として扱われ、target `discussions/` へ実際に write できない gap が確認された。
  - read-only specialist、full workspace-write worker、scoped-write delegated authoring agent、canonical authority の分類が正本に固定されていなかった。
- 振る舞いの目標:
  - `system-architect` / `implementation-planner` を scoped-write delegated authoring agent として実装し、target scope `discussions/` direct child の flat Markdown だけを書ける本命 execution path を成立させる。
  - static `.codex/agents/*.toml` は broad write を許可しない read-mostly fallback として維持し、fallback と本命 scoped-write execution を混同しない。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - scoped invocation / permission context を生成または記録する runtime / workflow / adapter files
  - dogfooding mirror: `.codex/agents/system-architect.toml`, `.codex/agents/implementation-planner.toml`, `.agents/skills/spec-dock-system-architect/SKILL.md`, `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `tests/test_init_update.py`
  - 必要に応じて `tests/cli_runtime/test_delegated_authoring.py` / `tests/domain_runtime/test_delegated_authoring.py`
- Red / 代替証跡の要件:
  - red-required: 現状の static adapter inspection では `system-architect` / `implementation-planner` に `write` permission がなく、scope-local direct-write contract を満たさないことを確認する。
  - red-required: scoped-write execution path が存在しない、または target `discussions/` への write-capable contract を検証できないことを確認する。
  - inspect-only fallback: host が実際の sub-agent permission sandbox を test から起動できない場合、生成される scoped permission context / invocation artifact / adapter contract を fixture として検査する。
- Green 検証:
  - `system-architect` / `implementation-planner` の本命 execution path では、resolved target scope `discussions/` direct child への naming-rule compliant Markdown create が許可される。
  - canonical `requirement.md` / `design.md` / `plan.md` / `report.md`、implementation files、tests、config、`.agents`、`.codex`、`.github`、`.env*`、nested directory、per-agent directory、run/task directory、`discussions/delegated-authoring/` はこの 2 role から write 不可である。
  - `researcher` / `consultant` / `deep-consultant` / `repo-analyst` / reviewers / `pr-monitor` / `spark-worker` は read-only static specialist のままである。
  - `dev-coder` / `doc-writer` / worker 系は full workspace-write worker として別分類に残る。
  - post-run `delegated-authoring diff-guard` は scoped-write output の採用資格を検査するが、actual write-capable execution path の代替とは扱わない。
- amendment trigger:
  - host が exact target `discussions/` write root を表現できないことが確認された場合、static adapter に broad write を足して解決せず、requirement/design/report に blocker または follow-up decision として記録する。
  - scoped execution path が runtime command ではなく orchestrator workflow の責務になる場合、workflow docs と tests の対象を更新する。

### S04 委任契約
- 委任ロール:
  - dev-coder for runtime / tests / permission context generation.
  - doc-writer for shipped skill / adapter / workflow wording.
- 入力 docs / source of truth:
  - `requirement.md` の Agent 権限分類、AC-002、EC-001、Q-002。
  - `design.md` の D-002、D-003、Agent execution surfaces、Agent permission dependency。
  - `discussions/20260524t235542z-disc-agent-permission-classification-gap-analysis.md`。
- 許可 paths:
  - S04 対象ファイルに列挙した provider assets、dogfooding mirror、runtime / tests / docs。
- 禁止 changes:
  - S01-S03 / S90 / S99 の既存計画本文を書き換えない。
  - static adapter に repo-wide / `spec-dock/initiatives` broad write を与えない。
  - canonical docs direct-write success path を復活させない。
  - read-only specialist を write-capable にしない。
- acceptance criteria:
  - `system-architect` / `implementation-planner` は read-only specialist ではなく scoped-write delegated authoring agent として分類・実装されている。
  - static fallback と scoped-write execution path が docs / adapter / tests 上で明確に分離されている。
  - target `discussions/` direct child への write-capable contract と forbidden write boundaries が test / fixture / inspection で固定されている。
- required tests or docs-only verification:
  - impacted `tests/test_init_update.py`
  - impacted delegated-authoring CLI / domain tests if runtime helper changes are introduced.
  - `rg` inspection for broad write, canonical direct-write, and read-only specialist regression.
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- reviewer focus:
  - system-architect / implementation-planner が read-only static に戻っていないこと。
  - broad write を safety guard で正当化していないこと。
  - actual write-capable execution path と post-run diff guard の責務が混同されていないこと。
- stop conditions:
  - host permission model の制約により scoped-write execution path を実装できず、代替として broad write を足す必要が出た場合。
  - target `discussions/` direct child だけの write 境界を test / fixture / inspection で観測できない場合。
  - canonical docs direct-write success path の復活が必要になる場合。
- output required:
  - changed files list grouped by provider, mirror, runtime, tests, docs。
  - scoped-write execution path の説明。
  - permission boundary evidence。
  - test / validation results。
  - report evidence to update for Decision Ledger, Evidence Adoption Ledger, Step Contract Closure, Test Contract Closure, Reviewer Gate Status。

### S04 具体テストケース一覧
- `tc-s04-001` acceptance: scoped-write authoring agents are not read-only specialists
  - 前提: system-architect / implementation-planner の provider adapter / skill / execution path が更新済み。
  - 操作: permission taxonomy と execution contract を inspection する。
  - 期待結果: 2 role は scoped-write delegated authoring agent として分類され、target `discussions/` direct child への write-capable path が存在する。
  - 失敗検出: 2 role が read-only static fallback のみで完了扱いになる回帰を検出する。
  - 検証方法: asset tests、fixture inspection、`rg` inspection。
- `tc-s04-002` negative: scoped-write does not become broad write
  - 前提: scoped-write execution path が生成または設定される。
  - 操作: allowed / denied paths を inspection または fixture test で確認する。
  - 期待結果: target `discussions/` direct child の flat Markdown create だけが write allowed であり、canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.github`、`.env*`、nested dirs、`discussions/delegated-authoring/` は denied / ineligible。
  - 失敗検出: static adapter や scoped context が repo-wide / `spec-dock/initiatives` broad write を持つ回帰を検出する。
  - 検証方法: permission fixture tests、asset tests、diff-guard forbidden cases。
- `tc-s04-003` regression: read-only specialists remain read-only
  - 前提: agent taxonomy が docs / assets に反映済み。
  - 操作: researcher / consultant / deep-consultant / repo-analyst / reviewers / pr-monitor / spark-worker の adapter を確認する。
  - 期待結果: これらの agent は read-only static specialist として write permission を持たない。
  - 失敗検出: scoped-write authoring correction の副作用で specialist に write が広がる回帰を検出する。
  - 検証方法: asset tests、`rg` inspection。
- `tc-s04-004` integration: diff guard remains an adoption eligibility check
  - 前提: scoped-write output が target discussion に作成される。
  - 操作: `delegated-authoring diff-guard` を実行する。
  - 期待結果: diff guard は output eligibility を判定するが、write permission の代替として説明されない。
  - 失敗検出: write-capable execution path なしで diff guard pass だけを direct-write 実装完了とみなす回帰を検出する。
  - 検証方法: delegated-authoring tests、docs inspection、report ledger。

### S04 step closure contract
- closure ids: `tc-s04-001`, `tc-s04-002`, `tc-s04-003`, `tc-s04-004`
- close 条件:
  - provider assets / mirror / tests が requirement/design の updated taxonomy と整合する。
  - system-architect / implementation-planner の scoped-write execution path が確認できる。
  - static fallback に broad write が追加されていない。
- report evidence:
  - Decision Ledger、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status。
- refactor guardrail:
  - 旧 manifest-heavy model や canonical direct-write target を復活させない。
  - permission model の変更は scoped-write delegated authoring に限定し、read-only specialist と full workspace-write worker の既存分類を不用意に変えない。

### S04 step gate
- step reviewer gate:
  - reviewers: spec-reviewer, code-reviewer, qa-reviewer
  - review 範囲: updated requirement/design alignment、provider / mirror adapters and skills、permission execution path、tests。
  - pass 条件: all `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S04 requirement/design follow-up, provider / mirror / runtime / tests / report evidence。

## 追加最終ゲート追補
- S04 完了後、既存 S99 / Final Exit Contract に加えて以下を確認する。
  - `report.md` に S04 の observed evidence、Decision Ledger、closure coverage、reviewer gates、commit/no-op evidence が記録されている。
  - `python -m unittest` の impacted tests、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock sync`、`./spec-dock/scripts/spec-dock doctor`、`git diff --check` が pass または limitation が report に記録されている。
  - PR #119 / #128 または後続 PR の状態が、S04 の requirement/design 修正と実装結果を反映している。

## 追加実装計画追補 S05 — Static all discussions write permission correction

この追補は、S04 実装後に判明した運用設計上の過剰複雑性を修正する追加作業である。既存の S01-S04 / S90 / S99 の本文は編集せず、S05 が S04 の `exact file runtime scoped-context` 方針を supersede する。

- 追加背景:
  - `discussions/20260525t010211z-disc-static-all-discussions-write-permission-analysis.md` により、run ごとの `scoped-context --discussion-file` 生成は、単一 file の write boundary としては安全だが、複数 initiative / epic / issue の `discussions/` に連続して draft を残す delegated authoring 運用には過剰に複雑であることが確認された。
  - user decision と更新済み requirement / design により、system-architect / implementation-planner は static adapter で全 scope-local `discussions/` への write capability を持つ delegated authoring agent として扱う。
  - canonical docs、implementation files、tests、config、secrets への write 禁止は維持する。
- 振る舞いの目標:
  - `system-architect` / `implementation-planner` の通常実行は、run ごとの agent setting rewrite や exact-file permission context generation に依存しない。
  - static `.codex/agents/*.toml` は、all scope-local `discussions/` direct-child Markdown authoring を許可する。
  - `spec-dock/initiatives` 全体や repo-wide write のように canonical docs まで含む broad write は採用しない。
  - `delegated-authoring scoped-context --discussion-file` は標準成功経路から外すだけでなく、runtime command / application helper / parser binding / tests / guidance から削除する。deprecated / diagnostic fallback として残さない。
  - post-run diff guard は、actual write permission の代替ではなく、delegated output の採用資格検査として維持する。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
    - remove: `DelegatedAuthoringScopedContextRequest`, `DelegatedAuthoringScopedContextResult`, `_SCOPED_CONTEXT_PERMISSION_PROFILES`, `generate_delegated_authoring_scoped_context`, `_blocked_scoped_context_result`, `_render_scoped_context_toml`, `_resolve_scoped_discussion_file`, `_scoped_discussion_file_error`, and `_toml_string` if no longer used.
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
    - remove: scoped-context imports, `DelegatedAuthoringScopedContextArgs`, command registry entry, argument builder, args factory, runner, expectation helper, and renderer.
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
    - remove: `delegated-authoring scoped-context` subparser binding.
  - dogfooding mirror: `.codex/`, `.agents/`, `spec-dock/docs/`, `spec-dock/scripts/spec_dock_runtime/...`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
  - `tests/domain_runtime/test_delegated_authoring.py`
- Red / 代替証跡の要件:
  - red-required: 現状の static adapter inspection では `system-architect` / `implementation-planner` に all scope-local `discussions/` write capability がなく、run ごとの exact-file context generation を標準経路として要求していることを確認する。
  - red-required: `scoped-context --discussion-file` exact write root 前提の tests / docs / skills が、新方針と矛盾することを確認する。
  - red-required: S04 exact-file context generation code path の存在を `rg` inspection で確認し、削除対象 inventory として report に記録する。
  - feasibility-required: Codex permission profile が `spec-dock/initiatives/**/discussions/` 相当の static write rule を表現できるかを fixture / inspection / documented limitation で確認する。
  - fallback-required: glob 表現が使えない場合でも、`spec-dock/initiatives` 全体 write や repo-wide write へ逃げず、最小代替案を report に記録する。
- Green 検証:
  - `system-architect` / `implementation-planner` は static delegated authoring profile 上、all scope-local `discussions/` direct-child Markdown authoring を許可される。
  - canonical `requirement.md` / `design.md` / `plan.md` / `report.md`、implementation files、tests、config、`.agents`、`.codex`、`.github`、`.env*` は write target にならない。
  - `researcher` / `consultant` / `deep-consultant` / `repo-analyst` / reviewers / `pr-monitor` / `spark-worker` は read-only specialist のままである。
  - `dev-coder` / `doc-writer` / worker 系は full workspace-write worker として別分類に残る。
  - `scoped-context --discussion-file` を標準成功経路として要求する文言、runtime command path、application helpers、exact-file context tests は削除されている。deprecated / diagnostic fallback として残っていない。
  - diff guard は all inspected scope-local `discussions/` の valid draft create/update を許可し、canonical / implementation / config / secret / nested / symlink / non-Markdown / invalid-state output を拒否する。
- amendment trigger:
  - permission profile が all scope-local `discussions/` write を静的に表現できない場合。
  - all discussions write を表現するために canonical docs を含む broad write が必要になる場合。
  - diff guard を single target scope 前提から広げる過程で、既存の baseline safety contract と衝突する場合。
  - S04 exact-file context generation code を削除すると、diff guard / baseline-status / manifest deprecated stub まで壊れることが判明した場合。

### S05 委任契約
- 委任ロール:
  - dev-coder for runtime deletion / tests replacement / permission contract adjustment.
  - doc-writer for shipped skill / adapter / workflow wording.
  - spec-reviewer for requirement/design/plan alignment after implementation.
  - qa-reviewer and code-reviewer for final implementation gate.
- 入力 docs / source of truth:
  - `requirement.md` の Q-002、AC-002、AC-007、EC-001。
  - `design.md` の D-002、D-003、Interface contract、Agent permission dependency。
  - `discussions/20260525t010211z-disc-static-all-discussions-write-permission-analysis.md`。
- 許可 paths:
  - S05 対象ファイルに列挙した provider assets、dogfooding mirror、runtime、tests、workflow docs。
- 禁止 changes:
  - S01-S04 / S90 / S99 の既存計画本文を書き換えない。
  - canonical docs direct-write success path を復活させない。
  - `spec-dock/initiatives` 全体または repo-wide write を system-architect / implementation-planner に与えない。
  - `delegated-authoring scoped-context` を deprecated / diagnostic fallback として残さない。
  - read-only specialist を write-capable にしない。
  - per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` を新規 delegated output として復活させない。
- acceptance criteria:
  - system-architect / implementation-planner の通常 delegated authoring は static all discussions write に基づき、run ごとの exact-file context generation に依存しない。
  - S04 exact-file context generation の runtime code、parser binding、command tests、asset wording は削除されている。
  - canonical single-writer authority と discussions direct-write authority が docs / skills / adapters / tests 上で分離されている。
  - provider assets と dogfooding mirror が同期している。
- required tests or docs-only verification:
  - impacted `tests/test_init_update.py`
  - impacted `tests/cli_runtime/test_delegated_authoring.py`
  - impacted `tests/domain_runtime/test_delegated_authoring.py`
  - `rg` inspection for `scoped-context`, `discussion-file`, `read-mostly fallback`, canonical direct-write, broad write, and read-only specialist regression.
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock doctor`
  - `git diff --check`
- reviewer focus:
  - S05 が S04 の exact-file context 方針を正しく supersede していること。
  - all discussions write が canonical docs write や repo-wide write へ拡大していないこと。
  - diff guard が permission generation の代替ではなく adoption eligibility check として残っていること。
- stop conditions:
  - host permission model の制約により all discussions write を static adapter で表現できず、かつ broad write 以外の代替が見つからない場合。
  - canonical docs direct-write success path の復活が必要になる場合。
- output required:
  - changed files list grouped by provider, mirror, runtime, tests, docs。
  - static all discussions write permission expression or documented limitation。
  - scoped-context runtime command deletion evidence。
  - permission boundary evidence。
  - test / validation results。
  - report evidence to update for Decision Ledger, Evidence Adoption Ledger, Step Contract Closure, Test Contract Closure, Reviewer Gate Status。

### S05 具体テストケース一覧
- `tc-s05-001` acceptance: static all discussions write capability
  - 前提: system-architect / implementation-planner provider adapter が更新済み。
  - 操作: permission profile / developer instructions / skill contract を inspection する。
  - 期待結果: 2 role は all scope-local `discussions/` direct-child Markdown authoring capability を持ち、run ごとの exact-file context generation を標準経路として要求しない。
  - 失敗検出: read-only fallback または `--discussion-file` 必須経路へ戻る回帰を検出する。
  - 検証方法: asset tests、fixture inspection、`rg` inspection。
- `tc-s05-002` negative: all discussions write does not become broad write
  - 前提: static delegated authoring profile が更新済み。
  - 操作: allowed / denied paths を inspection または fixture test で確認する。
  - 期待結果: scope-local `discussions/` direct child Markdown authoring だけが allowed であり、canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.github`、`.env*` は denied / ineligible。
  - 失敗検出: `spec-dock/initiatives` 全体または repo-wide write の混入を検出する。
  - 検証方法: permission fixture tests、asset tests、diff-guard forbidden cases。
- `tc-s05-003` regression: scoped-context is not the standard path
  - 前提: runtime / docs / skills が更新済み。
  - 操作: `scoped-context --discussion-file` の扱いを tests と docs で確認する。
  - 期待結果: command は runtime surface から削除され、deprecated / diagnostic fallback としても残っていない。通常 delegated authoring の完了条件になっていない。
  - 失敗検出: exact direct child 1 file context generation が再び標準成功経路になる回帰を検出する。
  - 検証方法: CLI tests、docs inspection、`rg` inspection。
- `tc-s05-003a` cleanup: obsolete scoped-context code and tests are removed
  - 前提: S04 exact-file scoped-context implementation が存在する。
  - 操作: provider runtime、dogfooding mirror、tests、adapter/skill/workflow docs を `rg` で検索する。
  - 期待結果: `DelegatedAuthoringScopedContextRequest`、`generate_delegated_authoring_scoped_context`、`delegated_authoring_scoped_context` command spec、`scoped-context` parser binding、`--discussion-file` exact-context tests、runtime scoped context guidance が削除されている。残るのは historical report / discussion evidence と、削除済みであることを説明する S05 docs のみである。
  - 失敗検出: 使われない command code、helper function、test fixture、guidance wording が残る回帰を検出する。
  - 検証方法: `rg` inspection、CLI test update、asset wording tests。
- `tc-s05-004` integration: diff guard supports inspected discussions without replacing permission
  - 前提: sub-agent output が scope-local `discussions/` に作成される。
  - 操作: diff guard を実行する。
  - 期待結果: diff guard は valid discussion draft create/update を eligible とし、forbidden paths を rejected / ineligible とする。diff guard は write permission generation の代替として説明されない。
  - 失敗検出: write-capable execution path なしで diff guard pass だけを実装完了とみなす回帰を検出する。
  - 検証方法: delegated-authoring CLI / domain tests、docs inspection、report ledger。
- `tc-s05-005` regression: other agent taxonomy remains stable
  - 前提: agent taxonomy が docs / assets に反映済み。
  - 操作: read-only specialist と full workspace-write worker の adapters / docs を確認する。
  - 期待結果: read-only specialist は write permission を持たず、full workspace-write worker は既存分類のまま残る。
  - 失敗検出: S05 の副作用で unrelated agent の write boundary が変わる回帰を検出する。
  - 検証方法: asset tests、`rg` inspection。

### S05 step closure contract
- closure ids: `tc-s05-001`, `tc-s05-002`, `tc-s05-003`, `tc-s05-003a`, `tc-s05-004`, `tc-s05-005`
- close 条件:
  - provider assets / mirror / tests が requirement/design の static all discussions write 方針と整合する。
  - `scoped-context --discussion-file` の runtime command path と exact-file context generation tests が削除されている。
  - canonical docs direct-write success path と broad write が復活していない。
- report evidence:
  - Decision Ledger、Evidence Adoption Ledger、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status。
- refactor guardrail:
  - 旧 manifest-heavy model、canonical direct-write target、exact-file runtime context code path を復活させない。
  - permission model の変更は system-architect / implementation-planner の scoped delegated authoring に限定し、read-only specialist と full workspace-write worker の既存分類を不用意に変えない。

### S05 step gate
- step reviewer gate:
  - reviewers: spec-reviewer, code-reviewer, qa-reviewer
  - review 範囲: updated requirement/design/plan alignment、provider / mirror adapters and skills、runtime scoped-context handling、diff guard behavior、tests。
  - pass 条件: all `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S05 plan follow-up, provider / mirror / runtime / tests / report evidence。

## 追加最終ゲート追補 S05
- S05 完了後、既存 S99 / S04 final gate に加えて以下を確認する。
  - `report.md` に S05 の observed evidence、Decision Ledger、closure coverage、reviewer gates、commit/no-op evidence が記録されている。
  - `python -m unittest` の impacted tests、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock sync`、`./spec-dock/scripts/spec-dock doctor`、`git diff --check` が pass または limitation が report に記録されている。
  - PR #119 / #128 または後続 PR の状態が、S05 の requirement/design/plan 修正と実装結果を反映している。

## 追加実装ステップ S06: `draft-requirement` / `draft-design` / `draft-plan` discussion doc creation

### S06 目的
- `spec-dock new doc` で `draft-requirement` / `draft-design` / `draft-plan` を作成できるようにする。
- 既存 canonical requirement / design / plan template を source としつつ、生成物は discussion-local evidence として `discussions/` に配置する。
- `system-architect` / `implementation-planner` が structured draft artifact を作れる標準経路を提供する。

### S06 対象ファイル
```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- commands/new.py
|-- application/contracts.py
|-- application/create_node.py
|-- domain/validation.py
`-- application/sync_state.py

src/spec_dock/assets/spec_dock/templates/
|-- initiative/{requirement,design,plan}.md
|-- epic/{requirement,design,plan}.md
`-- issue/{requirement,design,plan}.md

src/spec_dock/assets/spec_dock/docs/rules/
|-- initiative/discussions.md
|-- epic/discussions.md
`-- issue/discussions.md

spec-dock/                         # dogfooding mirror equivalents

tests/
|-- cli_runtime/test_new.py
|-- cli_runtime/test_runtime_new_doc_s09.py
|-- cli_runtime/test_validate.py
|-- cli_runtime/test_delegated_authoring.py
`-- test_init_update.py
```

### S06 作業順序
1. Characterization / Red
   - `new doc draft-requirement` / `new doc draft-design` / `new doc draft-plan` が現状 unknown type で失敗することを確認する。
   - 現行 discussion filename validators が `draft-requirement` / `draft-design` / `draft-plan` を許可していないことを確認する。
2. Runtime type expansion
   - `commands/new.py` の help / doc type list に `draft-requirement` / `draft-design` / `draft-plan` を追加する。
   - `application/contracts.py` の `CreateDiscussionDocRequest.doc_type` を更新する。
   - `application/create_node.py` の creatable doc type list と filename regex を更新する。
3. Draft rendering implementation
   - draft 専用 template file は追加しない。
   - draft type の場合、scope kind に応じた canonical template source を選ぶ。
   - 選択された既存 canonical template を render し、`discussions/` 直下の `draft-*` filename に配置する。
   - `templates/discussions/draft-requirement.md`、`draft-design.md`、`draft-plan.md` を作らない。
   - scope / parent placeholders を render する。
4. Validation / sync / diff-guard compatibility
   - validation / sync / delegated-authoring diff-guard の discussion filename recognition を `draft-requirement` / `draft-design` / `draft-plan` 対応にする。
   - `draft-requirement` / `draft-design` / `draft-plan` は discussion doc として扱い、canonical artifact として扱わない。
5. Docs and mirror
   - `docs/rules/{initiative,epic,issue}/discussions.md` の catalog と create command examples に `draft-requirement` / `draft-design` / `draft-plan` を追加する。
   - provider asset と dogfooding mirror を同期する。
6. Tests
   - `new doc draft-requirement` / `draft-design` / `draft-plan` の issue / epic / initiative 作成テストを追加する。
   - scope kind ごとの template source selection を固定する。
   - same-second suffix allocation が hyphenated kind で機能することを固定する。
   - `validate` / `sync` / `diff-guard` compatibility を固定する。
   - provider / mirror parity tests を更新する。
7. Report and review
   - `report.md` Decision Ledger / Evidence Adoption Ledger / Step Contract Closure / Test Contract Closure に S06 を記録する。
   - `spec-reviewer`、`code-reviewer`、`qa-reviewer` の順または並列で review gate を通す。

### S06 委任契約
- 委任ロール:
  - dev-coder for runtime / templates / tests implementation.
  - spec-reviewer for requirement/design/plan alignment.
  - code-reviewer for runtime / tests / template rendering review.
  - qa-reviewer for validation coverage and regression risk review.
- 入力 docs / source of truth:
  - 追加要件 S06 in `requirement.md`
  - 追加設計 S06 in `design.md`
  - `discussions/20260525t055851z-research-draft-artifact-template-command-analysis.md` は historical analysis として参照する。ただし discussion-local envelope と draft 専用 template 追加の提案は user clarification により superseded であり、S06 source of truth ではない。
- 禁止 changes:
  - S01-S05 / S90 / S99 の既存計画本文を書き換えない。
  - `new draft` など別 command surface を追加しない。
  - `disc` / `research` の variant として draft artifact を隠さない。
  - canonical docs direct-write success path を復活させない。
  - draft 専用 template file を追加して canonical template と二重管理しない。
- acceptance criteria:
  - `new doc draft-requirement` / `draft-design` / `draft-plan` が initiative / epic / issue の `discussions/` に flat Markdown を作成できる。
  - generated draft は scope-specific canonical requirement / design / plan template source を直接 render した内容を持つ。
  - generated draft の draft 性は `discussions/` 配置、`draft-*` filename、diff guard、report adoption ledger で扱う。
  - `validate` / `sync` / `diff-guard` が新 doc type と整合する。
  - `templates/discussions/draft-requirement.md` / `draft-design.md` / `draft-plan.md` が存在しない。
  - provider assets と dogfooding mirror が同期している。

### S06 具体テストケース一覧
- `tc-s06-001` acceptance: initiative draft requirement creation
  - 前提: initiative scope が存在する。
  - 操作: `new doc draft-requirement --initiative <id> --title "<title>"`
  - 期待結果: initiative `discussions/` に `<ts>-draft-requirement-<slug>.md` が作成され、`templates/initiative/requirement.md` を render した内容を持つ。
- `tc-s06-002` acceptance: issue draft design creation
  - 前提: issue scope が存在する。
  - 操作: `new doc draft-design --issue <id> --title "<title>"`
  - 期待結果: issue `discussions/` に `<ts>-draft-design-<slug>.md` が作成され、`templates/issue/design.md` を render した内容を持つ。
- `tc-s06-003` acceptance: epic draft plan creation
  - 前提: epic scope が存在する。
  - 操作: `new doc draft-plan --epic <id> --title "<title>"`
  - 期待結果: epic `discussions/` に `<ts>-draft-plan-<slug>.md` が作成され、`templates/epic/plan.md` を render した内容を持つ。
- `tc-s06-004` matrix: scope-specific template selection
  - 前提: initiative / epic / issue scopes が存在する。
  - 操作: 各 scope で `draft-requirement` / `draft-design` / `draft-plan` を作成する。
  - 期待結果: scope kind ごとに対応する canonical template source が使われる。
- `tc-s06-005` regression: hyphenated discussion kind naming
  - 前提: same-second collision が起きる。
  - 操作: 同一 timestamp family で `draft-requirement` / `draft-design` / `draft-plan` を作成する。
  - 期待結果: `<ts>-<nn>-draft-requirement-<slug>.md` / `<ts>-<nn>-draft-design-<slug>.md` / `<ts>-<nn>-draft-plan-<slug>.md` が割り当てられ、validate / sync が通る。
- `tc-s06-006` integration: diff guard accepts draft artifact docs
  - 前提: sub-agent output として `draft-requirement` / `draft-design` / `draft-plan` が作成される。
  - 操作: `delegated-authoring diff-guard` を実行する。
  - 期待結果: valid draft create/update は allowed discussion output になり、canonical docs / forbidden paths は従来通り rejected / ineligible。
- `tc-s06-007` negative: no duplicate draft templates
  - 前提: S06 implementation が完了している。
  - 操作: provider / dogfooding mirror の `templates/discussions/` を inspect する。
  - 期待結果: `draft-requirement.md` / `draft-design.md` / `draft-plan.md` は存在せず、既存 canonical templates が唯一の source である。

### S06 required verification
- `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09 -v`
- impacted `tests.cli_runtime.test_validate`
- impacted `tests.cli_runtime.test_delegated_authoring`
- impacted `tests.test_init_update`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync`
- `./spec-dock/scripts/spec-dock doctor`
- `git diff --check`

### S06 step gate
- step reviewer gate:
  - reviewers: spec-reviewer, code-reviewer, qa-reviewer
  - pass 条件: all `review_status: pass`
- report evidence:
  - Decision Ledger: command surface / envelope / template source decisions.
  - Evidence Adoption Ledger: analysis report adoption.
  - Step Contract Closure: `tc-s06-001` through `tc-s06-007`.
  - Test Contract Closure: test commands and results.
