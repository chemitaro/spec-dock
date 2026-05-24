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
