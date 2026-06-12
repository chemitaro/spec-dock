---
種別: 実装計画書（Issue）
ID: "iss-00184"
タイトル: "Rename Spec Dock Hub Skill"
関連GitHub: ["#184"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00184 Rename Spec Dock Hub Skill — 実装計画（実行契約 / Execution Contract）

この計画は、旧 hub skill `spec-driven-tdd-workflow` を current runtime / discovery / docs / tests surface から退役し、canonical hub skill `spec-dock-hub` へ完全移行するための実行契約である。

`report.md` は observed evidence ledger とし、実行結果、Red / Green / Refactor evidence、reviewer verdict、closure delta、commit evidence は `report.md` に記録する。実装中に plan 外の仕様差分が見つかった場合は、この plan を amend し fresh `spec-reviewer` を通すまで実装で吸収しない。

## この計画で満たす要件ID

- AC:
  - AC-001: `spec-dock-hub` の name / description から SpecDock hub であることを判断できる。
  - AC-002: 旧名参照の current surface と historical evidence の分類が design / plan / report に残る。
  - AC-003: hub は route selector + global invariant surface に留まり、leaf workflow spine を吸収しない。
  - AC-004: provider-side asset と dogfooding mirror の整合、sync、validate の証跡が残る。
  - AC-005: current entry は新名に統一され、旧名は historical evidence または cleanup rationale としてのみ残る。
  - AC-006: `spec-dock update` 後に新 hub が current installed hub となり、旧 hub path は current managed entry / compatibility alias として残らない。
- EC:
  - EC-001: 旧 path 依存は alias ではなく docs / tests / bundled asset references の更新で統合する。
  - EC-002: `spec-dock-hub` の短い名前を、heading / description / first-read bullets の hub / route selector / global invariant wording で補う。
  - EC-003: generated / historical artifact にだけ残る旧名は current surface negative gate から除外し、必要な rationale を report に残す。
- 制約:
  - 互換 alias、forwarding skill、stub、symlink、旧名の current discovery entry は作らない。
  - Provider-side source of truth は `src/spec_dock/assets/install_root/`。
  - `.agents/skills/` は dogfooding mirror / parity target。
  - Historical specs / discussions / reports は機械 rewrite しない。
  - Fresh reviewer pass なしに次 phase / execution readiness を主張しない。

## 依存関係から導く実装順序

- 参照元:
  - `design.md` の依存関係分析、module dependency diagram、file change plan。
  - `discussions/20260612t-plan-draft-spec-dock-hub-full-migration.md` の delegated plan draft。
- 順序ルール:
  - provider/mirror hub identity を先に固定する。
  - installer/update cleanup contract は新旧 path が確定してから固定する。
  - docs と tests は current contract を追う downstream として更新する。
  - dogfooding sync / validate と current-surface negative inspection は最後に行う。

```text
reviewed requirement/design
  -> S01 provider + mirror hub skill rename and text
  -> S02 installer/update cleanup contract
  -> S03 current docs references
  -> S04 tests/harness expectations
  -> S05 dogfooding sync/validate and current-surface inspections
  -> S90 docs impact resolution
  -> S99 final quality gate
```

## ステップ一覧

- S01 Provider / Mirror Hub Skill Rename:
  - 観測可能な振る舞い: provider と mirror の current hub skill が `spec-dock-hub` として存在し、旧 directory は current path として残らない。
  - 依存: reviewed requirement/design。
  - unblock: S02, S03, S04, S05。
  - 対象ファイル: provider skill path、dogfooding mirror skill path。
  - 閉じる要件: AC-001, AC-003, AC-004, EC-002。
  - レビューゲート: `spec-reviewer` + `code-reviewer`。
- S02 Installer / Update Cleanup Contract:
  - 観測可能な振る舞い: new install は `spec-dock-hub` を current managed skill とし、update は old exact hub path を obsolete managed file として削除する。
  - 依存: S01。
  - unblock: S04, S05。
  - 対象ファイル: `src/spec_dock/cli.py`, `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`, focused tests。
  - 閉じる要件: AC-006, EC-001。
  - レビューゲート: `code-reviewer`。
- S03 Current Docs References:
  - 観測可能な振る舞い: current docs は hub entry を `spec-dock-hub` として表示し、旧名を current entry として提示しない。
  - 依存: S01。
  - unblock: S05, S90。
  - 対象ファイル: `README.md`, `src/spec_dock/assets/spec_dock/docs/README.md`, `spec-dock/docs/README.md`。
  - 閉じる要件: AC-002, AC-005。
  - レビューゲート: `spec-reviewer`。
- S04 Tests / Harness Expectations:
  - 観測可能な振る舞い: tests / harness は `spec-dock-hub` を current expected value とし、旧 exact path cleanup を検出できる。
  - 依存: S01, S02。
  - unblock: S05, S99。
  - 対象ファイル: `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_wrappers.py`, `tests/unit/infra/test_init_update.py`。
  - 閉じる要件: AC-004, AC-006, EC-001。
  - レビューゲート: `code-reviewer`。
- S05 Dogfooding Sync / Validate And Inspections:
  - 観測可能な振る舞い: dogfooding workspace と current-surface inspection が full migration を示す。
  - 依存: S01-S04。
  - unblock: S90, S99。
  - 対象: generated dogfooding outputs if produced by `sync`, validation evidence, report evidence。
  - 閉じる要件: AC-002, AC-004, AC-005, EC-003。
  - レビューゲート: `code-reviewer` if generated/runtime diff is non-trivial; `spec-reviewer` if docs/spec references change。
- S90 Docs Impact Resolution:
  - 観測可能な振る舞い: docs impact が S03 で閉じている、または追加 current docs を doc-writer が更新し spec-reviewer が確認する。
  - 依存: S05。
  - unblock: S99。
  - 閉じる要件: AC-005, EC-003。
  - レビューゲート: `spec-reviewer`。
- S99 Final Quality Gate:
  - 観測可能な振る舞い: issue-wide tests / inspections / final reviewers が pass し、execution completion に必要な report evidence が揃う。
  - 依存: S01-S05, S90。
  - 閉じる要件: all AC / EC。
  - レビューゲート: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`。

## 要件 ↔ ステップ対応

- AC-001 -> S01, S04, S99
- AC-002 -> S03, S05, S90, S99
- AC-003 -> S01, S99
- AC-004 -> S01, S04, S05, S99
- AC-005 -> S03, S05, S90, S99
- AC-006 -> S02, S04, S05, S99
- EC-001 -> S02, S04, S99
- EC-002 -> S01, S99
- EC-003 -> S05, S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-ac-001 | S01/S04 | hub identity | acceptance | AC-001 | `spec-dock-hub` name/path/description identifies SpecDock hub route selector and global invariant surface | provider/mirror `SKILL.md`, installed skill inventory | unclear hub discovery / wrong entry skill | yes | inspect-only + pytest | report Step/Test Contract Closure |
| cl-ac-002 | S03/S05 | reference classification | acceptance | AC-002 | old-name references are classified as current update targets, cleanup metadata, tests, or historical evidence | scoped `rg`, report rationale | stale references treated as current or historical evidence rewritten | yes | inspect-only | report Closure Coverage |
| cl-ac-003 | S01/S99 | hub/leaf boundary | acceptance | AC-003 | hub keeps route selector + global invariant role and does not absorb leaf workflows | skill text diff and reviewer check | hub/leaf responsibility regression | yes | inspect-only + reviewer | report Reviewer Gate Status |
| cl-ac-004 | S01/S04/S05/S99 | provider/mirror validation | acceptance | AC-004 | provider/mirror parity, sync, and validate evidence are recorded; S01/S04 provide partial evidence, and final closure is allowed only after S05/S99 sync/validate evidence | `cmp`, focused tests, `sync`, `validate` | provider/mirror drift | yes | command | report Test Contract Closure |
| cl-ac-005 | S03/S05/S90 | current surface migration | acceptance | AC-005 | current surface uses new name; old name remains only historical or cleanup/test evidence | positive/negative `rg` with exception list | mixed naming in current docs/discovery | yes | inspect-only | report Closure Coverage |
| cl-ac-006 | S02/S04 | update cleanup | acceptance | AC-006 | update installs new hub and removes obsolete old managed exact file path | update prune fixture, manifest path, installed skill inventory | existing consumers retain both hub skills | yes | pytest + inspect-only | report Test Contract Closure |
| cl-ec-001 | S02/S04 | old path dependencies | negative | EC-001 | old path dependencies are updated without alias or forwarding skill | focused pytest and path inspection | compatibility alias hides broken references | yes | pytest | report Test Contract Closure |
| cl-ec-002 | S01 | short-name clarity | edge | EC-002 | `spec-dock-hub` text says hub / route selector / global invariant | provider/mirror skill text | name is still vague | yes | inspect-only + reviewer | report Step Contract Closure |
| cl-ec-003 | S05/S90 | historical evidence boundary | edge | EC-003 | historical references are excluded from current-surface negative gate and documented as non-current | `rg spec-dock/initiatives` exclusion evidence | false failure or destructive historical rewrite | yes | inspect-only | report Closure Coverage |

## レビュー / QA ゲート方針

- Per-step reviewer gate:
  - code / runtime / tests / scaffold behavior を含む step は `code-reviewer` pass を必要とする。
  - docs-only / skill-text-only / template-only step は `spec-reviewer` docs/spec alignment pass を必要とする。
  - 両方を含む step は reviewer focus を両方明記するか、実装時に step amendment で分割する。
- QG1 final QA:
  - `qa-reviewer` が test sufficiency、integration test 追加要否、manual/inspection coverage を確認する。
- CG1 final code review:
  - issue-wide `code-reviewer` が統合 diff、installer/update behavior、shipped scaffold path risk を確認する。
- SG1 final spec review:
  - `spec-reviewer` が requirement / design / plan / report / implementation / tests / docs 整合を確認する。
- Reviewer failure handling:
  - fail は bounded follow-up として該当 step の worker へ戻す。
  - plan 外の requirement/design gap なら plan amendment と fresh reviewer pass を先に行う。

## 実行ルール（全ステップ共通）

- 親 Codex は implementation files / tests / shipped docs / skill text を直接編集しない。実装は `dev-coder` / `doc-writer` に委任する。
- 各 implementation step は `1 implementation step = 1 review scope = 1 commit` を標準とする。
- Delegated worker output は reviewer pass の代替ではない。
- Worker は `Ledger Note` または `No material implementation decisions beyond the approved plan.` を返す。
- 実行結果は `report.md` の Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status、Step Commit Gate に記録する。
- 次の発見は plan amendment と re-review を必要とする:
  - planned current-surface path list 外に old-name current reference がある。
  - `host-adapters/meta.json` obsolete exact cleanup が current managed target validation と衝突する。
  - provider/mirror parity が rename 後に成立しない。
  - tests を通すために compatibility alias / forwarding skill が必要になる。
  - historical evidence と current surface の境界が不明になる。
  - `spec-dock sync` が canonical requirement/design/plan/report を予期せず rewrite する。

## 実装ステップ

### 実装ステップ S01 — Provider / Mirror Hub Skill Rename And Skill Text

- 振る舞いの目標:
  - current provider and dogfooding skill surfaces expose `spec-dock-hub` as the SpecDock hub skill.
- design 参照:
  - `design.md` sections: 採用方針、インターフェース契約、ディレクトリ / ファイル変更計画。
- 依存:
  - reviewed requirement/design。
- unblock:
  - S02, S03, S04, S05。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` deletion only
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md` deletion only
- 計画済み契約:
  - scope:
    - Provider authority と dogfooding mirror の directory rename。
    - frontmatter `name: spec-dock-hub`。
    - heading / description / first-read bullets で SpecDock Hub、route selector、global invariant surface を明示。
  - テスト義務:
    - closure id: cl-ac-001, cl-ac-003, cl-ac-004, cl-ec-002。
    - coverage rationale: skill discovery と hub/leaf boundary はユーザー価値の中心であり、文字列 inspection と reviewer check で閉じる。
  - Red / 代替証跡の要件:
    - inspect-only: 旧 path が current provider/mirror skill directory として存在し、新 path が存在しないことを実装前 characterization として記録する。
  - Green 検証:
    - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md`
    - `rg -n "name: spec-dock-hub|SpecDock Hub|route selector|global invariant" src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md`
    - `test ! -e src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `test ! -e .agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - Refactor / cleanup guardrail:
    - Leaf skills and workflow semantics are not redesigned.
  - report 証跡の記録先:
    - Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status.
  - amendment trigger:
    - old directory must remain for technical reasons, provider/mirror cannot be byte-equivalent, or hub text needs leaf workflow content.

#### 委任契約（delegation contract）

- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `iss-00164` requirement/design as boundary reference, current provider/mirror `SKILL.md` files.
- 許可 paths:
  - S01 target files only.
- 禁止 changes:
  - Runtime code, tests, README/docs, `src/spec_dock/cli.py`, `host-adapters/meta.json`, canonical issue docs, historical specs.
- 受け入れ条件:
  - cl-ac-001, cl-ac-003, cl-ac-004, cl-ec-002 close conditions pass.
- 必須 verification:
  - Green commands listed above.
- reviewer focus:
  - `spec-reviewer`: wording and hub/leaf boundary.
  - `code-reviewer`: shipped asset path behavior and deletion of old current path.
- 必須出力:
  - changed files, deleted paths, verification result, unresolved risks, Ledger Note or no material decision note.
- 停止条件:
  - Allowed paths are insufficient, compatibility alias is needed, or boundary wording conflicts with `iss-00164`.

#### 具体テストケース一覧

- `tc-s01-001` inspect-only: hub skill is renamed in provider and mirror
  - 前提: old provider/mirror `spec-driven-tdd-workflow/SKILL.md` exists and new path does not.
  - 操作: provider and mirror directories are renamed to `spec-dock-hub`, frontmatter and heading are updated.
  - 期待結果: new provider/mirror paths exist, old provider/mirror paths do not.
  - 失敗検出: both old and new hub paths remain, or current hub remains discoverable under old path.
  - 検証方法: `test` path checks and `rg` on new files.
  - 関連 closure id: cl-ac-001, cl-ec-002
- `tc-s01-002` inspect-only: hub/leaf boundary remains intact
  - 前提: existing hub body routes to leaf skills.
  - 操作: rename text without moving leaf workflow details into hub.
  - 期待結果: hub text still describes route selector / global invariant and points to leaf skills for task-specific workflows.
  - 失敗検出: hub begins to own issue planning/execution/clarification workflow steps directly.
  - 検証方法: skill text inspection and `spec-reviewer` gate.
  - 関連 closure id: cl-ac-003

#### ステップ完了契約

- closure id:
  - cl-ac-001, cl-ac-003, cl-ec-002
  - cl-ac-004 partial evidence only: provider/mirror byte parity; final closure waits for S05/S99 sync/validate evidence.
- close 条件:
  - S01 verification commands pass and required reviewers pass. Do not mark cl-ac-004 fully closed in this step.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - none after reviewer pass; otherwise bounded follow-up.

#### ステップゲート

- step reviewer gate:
  - reviewer: `spec-reviewer` and `code-reviewer`
  - pass 条件: both return `review_status: pass`
  - re-review rule: fix via delegated follow-up and rerun until pass.
- commit / no-op gate:
  - closure state: committed
  - commit 範囲: S01 files only.
  - no-op の場合: not expected. If no files change, record approved-no-op rationale, checked paths, diff-clean command, and reviewer confirmation before moving to S02.

### 実装ステップ S02 — Installer / Update Cleanup Contract

- 振る舞いの目標:
  - New installs manage `spec-dock-hub`; updates prune old exact managed hub path without compatibility.
- design 参照:
  - `design.md` インターフェース契約、manifest cleanup design、AC-006 mapping。
- 依存:
  - S01。
- unblock:
  - S04, S05。
- 対象ファイル:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - focused assertions/fixtures in `tests/unit/infra/test_init_update.py` as needed.
- 計画済み契約:
  - scope:
    - `_MANAGED_SKILL_NAMES` uses `spec-dock-hub`.
    - `spec-driven-tdd-workflow` is not a current managed/discovery skill.
    - `.agents/skills/spec-driven-tdd-workflow/SKILL.md` is added to `managed_assets.obsolete_exact_file_paths` or equivalent exact-file cleanup contract.
    - `_LEGACY_MANAGED_SKILL_NAMES` may retain old name only as cleanup metadata, not compatibility.
  - テスト義務:
    - closure id: cl-ac-006, cl-ec-001。
    - coverage rationale: existing consumer update is the highest-risk path because both old and new hub skills could coexist.
  - Red / 代替証跡の要件:
    - covered-existing / red-required: before implementation, identify failing existing tests or add/update a focused test that seeds the old path and expects pruning.
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "managed or obsolete or manifest or prunes or skill"`
    - Inspect build plan / manifest assertions for old exact path.
  - Refactor / cleanup guardrail:
    - Do not rewrite installer architecture or broaden obsolete cleanup policy.
  - report 証跡の記録先:
    - TDD evidence, Test Contract Closure, Delegated Worker Evidence, Reviewer Gate Status.
  - amendment trigger:
    - manifest obsolete path overlaps current managed path, or cleanup requires directory-wide deletion.

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `src/spec_dock/cli.py`, `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`, relevant tests.
- 許可 paths:
  - S02 target files only.
- 禁止 changes:
  - Skill text, docs, harness outside focused S02 assertions, compatibility alias, broad update policy rewrite.
- 受け入れ条件:
  - cl-ac-006 and cl-ec-001 close conditions pass.
- 必須 verification:
  - Focused pytest command and inspection of exact obsolete path.
- reviewer focus:
  - `code-reviewer`: installer/update semantics, manifest validation, no compatibility reintroduction.
- 必須出力:
  - changed files, tests run, pre-change failure or characterization, green result, unresolved risks.
- 停止条件:
  - Allowed paths are insufficient, test fixture cannot distinguish obsolete managed path from custom skill, or old name must remain current.

#### 具体テストケース一覧

- `tc-s02-001` acceptance: update prunes old managed hub file and installs new hub
  - 前提: temp target contains `.agents/skills/spec-driven-tdd-workflow/SKILL.md` and a custom skill.
  - 操作: run update using local provider assets.
  - 期待結果: `.agents/skills/spec-dock-hub/SKILL.md` exists, old exact hub file is removed, custom skill remains.
  - 失敗検出: old and new hub skills coexist or custom skills are removed.
  - 検証方法: focused `tests/unit/infra/test_init_update.py` fixture and pytest.
  - 関連 closure id: cl-ac-006
- `tc-s02-002` negative: obsolete exact path is cleanup metadata, not current managed path
  - 前提: manifest contains `.agents/skills/spec-driven-tdd-workflow/SKILL.md` as obsolete exact path.
  - 操作: build/update managed asset plan.
  - 期待結果: old path is in obsolete exact rel paths and not in current managed targets.
  - 失敗検出: manifest validation accepts overlap with current managed path or treats old name as discoverable.
  - 検証方法: focused manifest/build-plan assertions.
  - 関連 closure id: cl-ec-001

#### ステップ完了契約

- closure id:
  - cl-ac-006, cl-ec-001
- close 条件:
  - Focused tests pass and code-reviewer passes.
- report evidence:
  - TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - none after update-prune and manifest validation pass.

#### ステップゲート

- step reviewer gate:
  - reviewer: `code-reviewer`
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure state: committed
  - commit 範囲: S02 files only.

### 実装ステップ S03 — Current Docs References

- 振る舞いの目標:
  - Current docs show `spec-dock-hub` as the hub entry and do not advertise old name as current entry.
- design 参照:
  - `design.md` file change plan and AC-005 / EC-003 mapping.
- 依存:
  - S01。
- unblock:
  - S05, S90。
- 対象ファイル:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `spec-dock/docs/README.md`
- 計画済み契約:
  - scope:
    - Replace current hub entry/path references with `.agents/skills/spec-dock-hub/SKILL.md`.
    - Do not add old-name compatibility guidance.
  - テスト義務:
    - closure id: cl-ac-002, cl-ac-005。
  - Red / 代替証跡の要件:
    - inspect-only: current docs contain old hub name before change.
  - Green 検証:
    - `rg -n "spec-dock-hub" README.md src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md`
    - `! rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" README.md src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md`
  - Refactor / cleanup guardrail:
    - Do not rewrite historical specs or unrelated docs.
  - report 証跡の記録先:
    - Step Contract Closure, Closure Coverage, Reviewer Gate Status.
  - amendment trigger:
    - additional current docs surfaces appear outside design scope.

#### 委任契約（delegation contract）

- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, current docs target files.
- 許可 paths:
  - S03 target files only.
- 禁止 changes:
  - Historical evidence, implementation code, tests, skill text, canonical issue docs.
- 受け入れ条件:
  - cl-ac-002 and cl-ac-005 close conditions pass.
- 必須 verification:
  - Docs positive/negative `rg` commands.
- reviewer focus:
  - `spec-reviewer`: docs/spec alignment and historical boundary.
- 必須出力:
  - changed docs, inspection results, no compatibility wording confirmation.
- 停止条件:
  - Docs require old-name current compatibility wording.

#### 具体テストケース一覧

- `tc-s03-001` inspect-only: current docs point to new hub
  - 前提: current docs mention old hub path.
  - 操作: update current docs references to `spec-dock-hub`.
  - 期待結果: docs show new hub path/name and no current old hub entry.
  - 失敗検出: user-facing docs still route agents to old hub name.
  - 検証方法: positive/negative `rg` over S03 target files.
  - 関連 closure id: cl-ac-005

#### ステップ完了契約

- closure id:
  - cl-ac-002, cl-ac-005
- close 条件:
  - docs inspection passes and spec-reviewer passes.
- report evidence:
  - Step Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - additional docs discovered later are handled in S90 or plan amendment.

#### ステップゲート

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure state: committed
  - commit 範囲: S03 files only.

### 実装ステップ S04 — Tests / Harness Expectations

- 振る舞いの目標:
  - Tests and runtime harness encode `spec-dock-hub` as current managed skill and detect old-path cleanup regressions.
- design 参照:
  - `design.md` test strategy and file change plan.
- 依存:
  - S01, S02。
- unblock:
  - S05, S99。
- 対象ファイル:
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - Update expected managed skill names and installed path assertions.
    - Update provider/mirror parity and bundled asset inventories.
    - Update routing contract tests to read `spec-dock-hub`.
    - Add or adjust update-prune fixture for old exact path deletion.
  - テスト義務:
    - closure id: cl-ac-001, cl-ac-004, cl-ac-006, cl-ec-001。
  - Red / 代替証跡の要件:
    - covered-existing / red-required: record pre-change failures or characterization for old expected path assertions.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_wrappers.py`
    - `uv run pytest tests/unit/infra/test_init_update.py -k "managed or skill or bundled or parity or routing or prunes or obsolete or manifest or README"`
  - Refactor / cleanup guardrail:
    - Do not delete unrelated coverage or broadly rewrite test helpers.
  - report 証跡の記録先:
    - TDD evidence, Test Contract Closure, Closure Delta if tests are added/renamed, Reviewer Gate Status.
  - amendment trigger:
    - tests can pass only by leaving old compatibility alias.

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 changed files, target tests.
- 許可 paths:
  - S04 target files only.
- 禁止 changes:
  - Production code, docs, skill files, broad unrelated test rewrites.
- 受け入れ条件:
  - cl-ac-001, cl-ac-004, cl-ac-006, cl-ec-001 close conditions pass.
- 必須 verification:
  - Focused pytest commands.
- reviewer focus:
  - `code-reviewer`: test sensitivity, expected inventory correctness, update-prune fixture validity.
  - `qa-reviewer` may inspect later at S99 for test sufficiency.
- 必須出力:
  - changed tests, red/characterization evidence, green commands, unresolved risks.
- 停止条件:
  - Expected inventory conflicts with installer behavior or test fixture cannot model old managed path safely.

#### 具体テストケース一覧

- `tc-s04-001` acceptance: wrapper tests use new hub skill
  - 前提: generated target contains installed managed skills.
  - 操作: wrapper test reads the hub skill file.
  - 期待結果: test reads `.agents/skills/spec-dock-hub/SKILL.md`.
  - 失敗検出: harness/test still expects old path.
  - 検証方法: `uv run pytest tests/cli_runtime/test_wrappers.py`.
  - 関連 closure id: cl-ac-001
- `tc-s04-002` acceptance: bundled and parity tests cover new managed inventory
  - 前提: provider assets and expected managed skill names are loaded.
  - 操作: unit infra tests inspect bundled skills and provider/mirror parity.
  - 期待結果: `spec-dock-hub` is expected current managed skill and old path is not current.
  - 失敗検出: bundle inventory still contains old hub as current path.
  - 検証方法: focused `tests/unit/infra/test_init_update.py` pytest.
  - 関連 closure id: cl-ac-004
- `tc-s04-003` negative: old hub path is pruned on update
  - 前提: existing target has old hub skill file and custom skill.
  - 操作: run update test fixture.
  - 期待結果: new hub exists, old exact hub path is removed, custom skill remains.
  - 失敗検出: compatibility alias remains or custom skill is deleted.
  - 検証方法: focused update-prune test.
  - 関連 closure id: cl-ac-006, cl-ec-001

#### ステップ完了契約

- closure id:
  - cl-ac-001, cl-ac-006, cl-ec-001
  - cl-ac-004 partial evidence only: test/harness coverage of managed skill inventory; final closure waits for S05/S99 sync/validate evidence.
- close 条件:
  - Focused tests pass and code-reviewer passes. Do not mark cl-ac-004 fully closed in this step.
- report evidence:
  - TDD evidence, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - none after focused and broadened fallback tests pass.

#### ステップゲート

- step reviewer gate:
  - reviewer: `code-reviewer`
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure state: committed
  - commit 範囲: S04 files only.

### 実装ステップ S05 — Dogfooding Sync / Validate And Current-Surface Inspections

- 振る舞いの目標:
  - local dogfooding workspace and scoped inspections prove the full migration without rewriting historical evidence.
- design 参照:
  - `design.md` test strategy, migration, historical evidence boundary.
- 依存:
  - S01, S02, S03, S04。
- unblock:
  - S90, S99。
- 対象:
  - generated dogfooding outputs from `./spec-dock/scripts/spec-dock sync`, if any.
  - report evidence updated by main orchestrator.
- 計画済み契約:
  - scope:
    - Run sync/validate after current assets/docs/tests are changed.
    - Record positive/negative current-surface inspections.
    - Treat `spec-dock/initiatives/**` old-name matches as historical exclusion evidence, not failures.
  - テスト義務:
    - closure id: cl-ac-002, cl-ac-004, cl-ac-005, cl-ec-003。
  - Red / 代替証跡の要件:
    - inspect-only: pre-change current-surface `rg` shows old name; historical `rg` shows expected past evidence.
  - Green 検証:
    - `./spec-dock/scripts/spec-dock sync`
    - `./spec-dock/scripts/spec-dock validate`
    - `git diff --check`
    - positive/negative scoped `rg` commands from S99.
  - Refactor / cleanup guardrail:
    - Do not manually rewrite historical specs or generated data unrelated to sync.
  - report 証跡の記録先:
    - Closure Coverage, Test Contract Closure, Reviewer Gate Status, session log command evidence.
  - amendment trigger:
    - sync rewrites canonical issue docs unexpectedly or validation fails for unrelated reason.

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder` for generated diff inspection if sync changes managed outputs.
  - Parent orchestrator may run operational commands and record report evidence.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, current diff after S01-S04.
- 許可 paths:
  - generated dogfooding outputs produced by sync, and report evidence by main orchestrator.
- 禁止 changes:
  - manual historical rewrite, canonical specs by delegated worker, compatibility alias.
- 受け入れ条件:
  - cl-ac-002, cl-ac-004, cl-ac-005, cl-ec-003 close conditions pass.
- 必須 verification:
  - sync, validate, diff-check, scoped `rg`, `cmp`.
- reviewer focus:
  - `code-reviewer` if generated/runtime diff is non-trivial.
  - `spec-reviewer` if docs/spec references change.
- 必須出力:
  - command results, generated diff summary, allowed old-name exception list.
- 停止条件:
  - old-name current reference remains outside cleanup metadata/tests, or sync modifies canonical planning docs.

#### 具体テストケース一覧

- `tc-s05-001` command: dogfooding sync and validate pass
  - 前提: S01-S04 are committed or ready in the current worktree.
  - 操作: run `./spec-dock/scripts/spec-dock sync` and `./spec-dock/scripts/spec-dock validate`.
  - 期待結果: both commands pass and generated diff is expected.
  - 失敗検出: dogfooding scaffold is stale or invalid after rename.
  - 検証方法: command output recorded in `report.md`.
  - 関連 closure id: cl-ac-004
- `tc-s05-002` inspect-only: current-surface old-name matches are only allowed exceptions
  - 前提: all current references have been updated.
  - 操作: run scoped positive and negative `rg`.
  - 期待結果: new name appears in current surfaces; old name appears only in cleanup metadata and tests/fixtures that assert pruning.
  - 失敗検出: README/docs/skill current discovery still advertises old hub name.
  - 検証方法: scoped `rg` commands and exception list.
  - 関連 closure id: cl-ac-005, cl-ec-003

#### ステップ完了契約

- closure id:
  - cl-ac-002, cl-ac-004, cl-ac-005, cl-ec-003
- close 条件:
  - sync, validate, diff-check, `cmp`, and scoped inspections pass. This is the first step where cl-ac-004 may be fully closed.
- report evidence:
  - Test Contract Closure, Closure Coverage, session log, Reviewer Gate Status if reviewer required.
- 残リスク:
  - any unexpected generated diff triggers review or plan amendment.

#### ステップゲート

- step reviewer gate:
  - reviewer: `code-reviewer` and/or `spec-reviewer` only if generated/runtime/docs diff is non-trivial.
  - pass 条件: required reviewer returns pass, or report records approved-no-op rationale for no reviewer-required diff.
- commit / no-op gate:
  - closure state: committed if sync changes files; approved-no-op if no file changes and evidence proves no-op.

## ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）

- 対象:
  - Known current docs: `README.md`, `src/spec_dock/assets/spec_dock/docs/README.md`, `spec-dock/docs/README.md`。
  - Additional current docs/templates/skill references discovered by S05 scoped inspection.
- 対応:
  - If S03 covers all current docs and S05 finds no additional current docs references, record approved-no-op rationale in `report.md`.
  - If additional current docs references are found within design scope, delegate to `doc-writer` and run `spec-reviewer`.
  - If additional surface exceeds design scope, amend plan and re-review before editing.
- doc update owner:
  - `doc-writer` when updates are required.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs align with requirement/design/plan and old-name current docs entries are gone.
- 具体テストケース:
  - `tc-s90-001` inspect-only: docs impact is fully resolved
    - 前提: S05 scoped inspection has run.
    - 操作: classify any remaining old-name docs references.
    - 期待結果: current docs are updated or no-op rationale is recorded; historical evidence is preserved.
    - 失敗検出: current docs still route agents to old hub name.
    - 検証方法: scoped `rg` and `spec-reviewer`.
    - 関連 closure id: cl-ac-005, cl-ec-003

## 最終品質ゲートステップ S99（final quality gate）

- branch diff 範囲:
  - Provider/mirror skill rename, installer/update cleanup contract, docs current references, tests/harness, generated dogfooding outputs, issue docs/report evidence.
- 必須 validation:
  - `uv run pytest tests/cli_runtime/test_wrappers.py`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "managed or skill or bundled or parity or routing or prunes or obsolete or manifest or README"`
  - If focused selection is brittle or misses renamed tests:
    - `uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py`
  - If runtime harness impact is broader:
    - `uv run pytest tests/cli_runtime`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- final inspections:
  - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md`
  - `rg -n "spec-dock-hub|SpecDock Hub" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - Allowed old-name matches:
    - `_LEGACY_MANAGED_SKILL_NAMES` only if cleanup metadata.
    - `managed_assets.obsolete_exact_file_paths` exact path.
    - test names / fixtures / assertions that seed and verify obsolete old managed path pruning.
  - Historical exclusion evidence:
    - `rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" spec-dock/initiatives`
    - This is not a failure condition by itself.
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: closure index coverage, missing high-value tests, integration test need, old-name negative inspection exceptions.
  - pass 条件: `review_status: pass`
- final code review gate:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated diff, installer/update semantics, scaffold asset path behavior, test sensitivity, no compatibility alias.
  - pass 条件: `review_status: pass`
- final spec review gate:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs consistency and all AC/EC closure.
  - pass 条件: `review_status: pass`
- final commit gate:
  - commit 範囲: after all step commits and final report evidence, create final commit if the workflow requires a final integrated commit.
  - final report ledger:
    - Record final reviewer verdicts, closure coverage, final validation commands, final commit scope, and post-commit external evidence destination.
  - post-commit external evidence destination:
    - final response / PR / issue comment as applicable.

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking implementation detail:
  - `_LEGACY_MANAGED_SKILL_NAMES` に旧名を残すかは S02 実装時に cleanup test と照合して決める。ただし残す場合も compatibility surface ではない。

## 最終完了条件

- AC/EC 達成:
  - all closure ids in Spec-Locked Closure Index are closed in `report.md`.
- docs 影響解決:
  - S90 is passed or approved-no-op with spec-reviewer evidence.
- 全 implementation step 完了:
  - S01-S05 are `committed` or valid `approved-no-op`.
- final quality gate pass:
  - `qa-reviewer`: pass
  - issue-wide `code-reviewer`: pass
  - final `spec-reviewer`: pass
- required validation:
  - Focused pytest / fallback pytest as applicable, sync, validate, diff-check, `cmp`, scoped `rg`.
- final report ledger:
  - Implementation Delegation Gate, Delegated Worker Evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status, Step Commit Gate, Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit evidence destinations are filled.
- final clean state:
  - no unintended staged / unstaged changes after final commit or approved-no-op closeout.
