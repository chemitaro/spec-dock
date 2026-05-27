---
種別: 実装報告書（Issue）
ID: "iss-00130"
タイトル: "Central Worktree Root Placement"
関連GitHub: ["#130"]
状態: "in_progress"
作成者: "iwasawayuuta"
最終更新: "2026-05-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00107", "init-local-00002"]
---

# iss-00130 Central Worktree Root Placement — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合はその旨を明示する。本 issue では D-001 の operational decision を記録しており、未解決の decision entry はない。

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | operation | orchestrator | `uvx --from . spec-dock update .` produced broad dogfooding scaffold churn outside the central-root scope. | Keep full update; revert generated churn; manually mirror only relevant dogfooding runtime/docs files. | Reverted broad generated churn and mirrored only `reference_worktree.md`, `application/ports.py`, `application/worktree.py`, and `cli/bootstrap.py` into the dogfooding workspace. | Keeps provider-side authority while avoiding unrelated scaffold deletion/rename churn in this issue. | applied | `git status --short --branch`; copied relevant provider files to `spec-dock/` dogfooding paths. | none |
| D-002 | resolved | compatibility | code-reviewer | CLI help still advertised sibling placement after runtime/docs switched to central root. | Leave help unchanged because detailed docs are correct; update help in provider and dogfooding parser. | Updated `worktree create` help to say central-root Git worktree in both provider and dogfooding runtime parser files. | CLI help is a user-facing scaffold contract and should not contradict required `SPEC_DOCK_WORKTREE_ROOT` placement. | applied | `rg -n "Create a sibling Git worktree|Create a central-root Git worktree" ...`; mirror parity test passed. | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | `sub-agent` repo-analyst | runtime / tests / docs implementation | Read-only analysis matched approved S01-S05/S90 plan and identified the exact current-code conflicts and test-harness unset-env risk. | subagent notification for repo-analyst `Avicenna`; `tests/cli_runtime/test_worktree.py` exact-env helper | なし |
| EAL-002 | `adopted` | `command` / tests | issue evidence | Targeted worktree runtime tests prove S01-S05 behavior and regression preservation. | `uv run python -m unittest tests.cli_runtime.test_worktree -v` -> OK, 22 tests | なし |
| EAL-003 | `adopted` | `sub-agent` code-reviewer | final code review | Integrated diff reviewer found no P0/P1 issues and confirmed provider/dogfooding mirror parity for changed runtime/docs files. | code-reviewer `Halley` -> `review_status: pass` | なし |
| EAL-004 | `adopted` | `sub-agent` qa-reviewer | test coverage / report cleanup | QA gate passed with P2 recommendations; invalid-label central-root side-effect coverage and decision-ledger cleanup were adopted and targeted tests passed. | qa-reviewer `Locke` -> `review_status: pass`; `uv run python -m unittest tests.cli_runtime.test_worktree -v` -> OK, 22 tests | なし |
| EAL-005 | `adopted` | `sub-agent` code-reviewer | CLI help contract cleanup | Fresh code review passed with P2 stale help wording; provider and dogfooding parser help were updated to central-root wording and parity verified. | code-reviewer `Newton` -> `review_status: pass`; `rg` stale-help check; mirror parity test -> OK | なし |
| EAL-006 | `adopted` | `sub-agent` qa-reviewer | post-cleanup QA review | Fresh QA review passed with only evidence-ledger cleanup; EAL-004 was closed and targeted tests had already passed. | qa-reviewer `Herschel` -> `review_status: pass` | なし |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 仕様準備ゲート（Pre-Implementation Spec Authoring Gate）

### 状態
- 実装は未着手。
- `requirement.md`、`design.md`、`plan.md` を作成済み。
- 実装開始はユーザー承認待ち。

### 参照した入力
- active issue の `discussions/` 配下にある既存議論、調査、ドラフトを読み込み、環境変数必須化、root directory 作成可否、path validation、namespace policy、local shell setup scope を仕様へ反映した。
- 音声入力由来の誤りは `要件定義書` と解釈して補正した。

### 委任と採用
| 識別子 | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-PRE-001 | `adopted` | discussions / research | `requirement.md` | active issue の過去議論とユーザー回答から、worktree root policy の契約を確定できた。 | `discussions/` 配下の調査・ドラフト群 | なし |
| EAL-PRE-002 | `adopted` | `system-architect` | `design.md` | layered runtime architecture に沿い、env lookup boundary と path validation / placement の責務境界を設計へ反映した。 | subagent design draft summary | なし |
| EAL-PRE-003 | `adopted` | `implementation-planner` | `plan.md` | requirement / design の AC・EC を Spec-Locked Closure Index と実装順序へ分解した。 | subagent plan draft summary | なし |
| EAL-PRE-004 | `adopted` | `spec-reviewer` | `requirement.md`, `design.md`, `plan.md` | reviewer findings は canonical docs へ反映し、各フェーズで fresh pass を取得した。 | reviewer pass summaries | なし |

### レビューゲート
| フェーズ | レビュアー | 鮮度 | 状態 | 対応内容 |
|---|---|---|---|---|
| requirement | `spec-reviewer` | fresh | passed | 親 Epic の sibling-placement supersession と local setup evidence scope を追記して再レビューを通過した。 |
| design | `spec-reviewer` | fresh | passed | invalid-root / mkdir failure の error guidance に env var 名、解決後 path、原因、setup 例を明記して再レビューを通過した。 |
| plan | `spec-reviewer` | fresh | passed | PR delivery gate、`.zshenv` inspection、S03-S05 / S06 / S90 の delegation contract と report evidence ordering を補強して再レビューを通過した。 |

## 実装サマリー (任意)
- `worktree create` の配置先を required `SPEC_DOCK_WORKTREE_ROOT` based central root に変更した。
- `EnvironmentGateway` port を追加し、missing / blank / invalid root を Git mutation 前に fatal にする runtime boundary と tests を追加した。
- Provider docs、dogfooding docs、親 Epic docs を central root contract に更新し、legacy sibling placement を future fallback ではなく historical boundary として明示した。

### セッションログ（2026-05-27 実装 / S01-S06 / S90）

#### 対象
- Step: S01, S02, S03, S04, S05, S06, S90
- AC/EC: AC-001..AC-009, EC-001..EC-005
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S01` .. `S90`
  - closure ids: slci-001 .. slci-012

#### 実施内容
- S01:
  - `EnvironmentGateway.getenv(name)` を追加し、runtime bootstrap で `os.environ.get` adapter を wiring した。
  - `SPEC_DOCK_WORKTREE_ROOT` missing / blank は Git / directory / bootstrap side effect 前に fatal とした。
- S02:
  - `~` expansion、absolute path validation、file / broken symlink rejection、directory symlink acceptance、namespace mkdir failure guidance を追加した。
- S03:
  - placement を `$SPEC_DOCK_WORKTREE_ROOT/<main-worktree-basename>/<main-worktree-basename>-<id>` に変更した。
  - old sibling container fallback は実装していない。
- S04:
  - label / id / branch naming、retryable collision、non-retryable failure、bootstrap status behavior を central root 配置で維持した。
- S05:
  - linked worktree からの実行でも main worktree basename を namespace に使い、branch prefix は実行元 current branch を維持するテストを更新した。
- S06:
  - `printenv SPEC_DOCK_WORKTREE_ROOT` は `/Users/iwasawayuuta/workspace/worktrees`。
  - `/Users/iwasawayuuta/.zshenv` に `export SPEC_DOCK_WORKTREE_ROOT="${SPEC_DOCK_WORKTREE_ROOT:-$HOME/workspace/worktrees}"` が存在する。
  - `/Users/iwasawayuuta/workspace/worktrees` は現時点では未作成。runtime tests により valid env root / namespace は command が作成可能であることを確認した。
- S90:
  - `reference_worktree.md`、親 Epic requirement/design/plan、dogfooding runtime mirror を central root contract に更新した。

#### 実行コマンド / 結果
```bash
uv run python -m unittest tests.cli_runtime.test_worktree -v

Ran 22 tests in 9.964s
OK
```

```bash
git worktree add /private/tmp/specdock-iss130-red HEAD
cp tests/cli_runtime/test_worktree.py /private/tmp/specdock-iss130-red/tests/cli_runtime/test_worktree.py
uv run python -m unittest \
  tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_create_requires_env_without_side_effects \
  tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_create_rejects_relative_root_without_side_effects \
  tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_create_uses_central_root_auto_id_and_branch \
  tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_create_normalizes_container_from_linked_worktree \
  -v

FAILED (failures=3, errors=1)
```

Red evidence details:
- old HEAD returned exit code `0` for missing `SPEC_DOCK_WORKTREE_ROOT`.
- old HEAD returned exit code `0` for relative `SPEC_DOCK_WORKTREE_ROOT`.
- old HEAD output used sibling `/sample-repo-worktrees/sample-repo-wt1` instead of central root.
- old HEAD did not create the expected central-root linked checkout for linked-worktree invocation.

```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=67
```

```bash
./spec-dock/scripts/spec-dock sync

spec-dock: sync: active unchanged (matched id in branch: iss-00130)
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md
```

```bash
uv run python -m unittest discover -v

Ran 959 tests in 513.104s
FAILED (failures=10)
```

Full suite failure classification:
- All 10 failures are build / isolated wheel tests that invoke `.venv/bin/python3 -m pip`.
- `uv run python -m pip --version` returns `No module named pip`.
- `python -m pip --version` succeeds with pip 24.1.2.
- This is local uv-managed `.venv` tooling state, not observed central-root runtime behavior.

```bash
python -m unittest discover -v

Ran 959 tests in 507.809s
OK
```

Full suite follow-up classification:
- Re-running the same unittest discovery through system Python passed.
- The earlier `uv run` failure is therefore classified as local `.venv` pip state, not a regression in the central-root implementation.

```bash
python -m unittest discover -v

Ran 959 tests in 498.210s
OK
```

Post-cleanup full suite:
- Re-running after invalid-label coverage and parser help cleanup still passed.

```bash
printenv SPEC_DOCK_WORKTREE_ROOT

/Users/iwasawayuuta/workspace/worktrees
```

```bash
sed -n '1,80p' /Users/iwasawayuuta/.zshenv

export SPEC_DOCK_WORKTREE_ROOT="${SPEC_DOCK_WORKTREE_ROOT:-$HOME/workspace/worktrees}"
```

```bash
ls -ld /Users/iwasawayuuta/workspace/worktrees

ls: /Users/iwasawayuuta/workspace/worktrees: No such file or directory
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01-S05 | Red | slci-001..slci-008 | old HEAD + current tests 4 件が expected failure | temporary HEAD worktree + copied current test file | pass | missing env / relative root / central placement / linked normalization が旧 sibling 実装で失敗することを確認 |
| S01-S05 | Green | slci-001..slci-008 | worktree runtime tests 22 件成功 | `uv run python -m unittest tests.cli_runtime.test_worktree -v` | pass | Missing/blank env、path validation、central placement、collision、bootstrap、linked-worktree normalization を含む |
| S06 | Manual | slci-009 | env export present; configured root currently absent but valid root auto-creation is covered by runtime tests | shell inspection / test evidence | pass | user-local path は commit 対象外 |
| S90 | Docs inspection | slci-010..slci-012 | provider docs / dogfooding docs / parent Epic docs updated; stale future sibling contract search limited to legacy wording | `rg` inspection | pass | broad `spec-dock update .` churn は D-001 として抑制 |
| S99 | Validation | slci-012 | validate and sync passed on current working tree | `./spec-dock/scripts/spec-dock validate`; `./spec-dock/scripts/spec-dock sync` | pass | code-reviewer reported a sync failure in a parallel context, but parent rerun succeeded |
| S99 | Full suite | slci-012 | full unittest discover passed through system Python after classifying local `.venv` pip state and after post-QA cleanup | `python -m unittest discover -v` | pass | latest run: 959 tests in 498.210s OK |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | slci-001 | missing / blank env fatal before side effects | `test_worktree_create_requires_env_without_side_effects`, `test_worktree_create_rejects_blank_env_without_side_effects` | pass | exact-env helper added for true unset env |
| S02 | slci-002, slci-003 | invalid roots fatal; `~` and directory symlink accepted | relative/file/broken symlink/dir symlink/tilde tests | pass | error text includes var name, raw/resolved path, cause, setup example |
| S03 | slci-004, slci-005 | central placement and no sibling fallback | central placement test and sibling absence assertions | pass | root/namespace auto-created |
| S04 | slci-006, slci-007 | naming/collision/bootstrap preserved | collision, label, branch slash, bootstrap success/failure/detection tests | pass | bootstrap remains non-fatal |
| S05 | slci-008 | linked invocation normalization | linked worktree runtime test | pass | namespace uses main worktree basename |
| S06 | slci-009 | local setup evidence only | shell env and `.zshenv` inspection | pass | no repo-managed user-local artifact |
| S90 | slci-010..slci-012 | docs/spec parity and scope boundary | docs updates and targeted `rg` inspection | pass | sibling only remains as legacy/future-not wording |

## 実装記録（セッションログ） (必須)

### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S04 | invalid label test should also prove no central-root side effects | qa-reviewer | valid central root を渡し、namespace / worktree / branch / bootstrap side effect がないことを追加確認 | slci-006 | no | `tests/cli_runtime/test_worktree.py` |
| S99 | `uv run` full suite failed because local `.venv` lacks pip | command | system Python で同じ unittest discovery を再実行して pass を確認 | slci-012 | no | `python -m unittest discover -v` -> OK |

### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| slci-001 | S01 | yes | red-required | old HEAD current-test run failed as expected | `test_worktree_create_requires_env_without_side_effects`; `test_worktree_create_rejects_blank_env_without_side_effects` | pass | missing / blank env fatal before side effects |
| slci-002 | S02 | yes | red-required | old HEAD current-test run failed as expected | relative/file/broken-symlink root tests | pass | invalid root errors include env var, raw/resolved path, cause, setup example |
| slci-003 | S02 | yes | red-required | covered by new tests | directory symlink and tilde root tests | pass | accepted valid root variants |
| slci-004 | S03 | yes | red-required | old HEAD current-test run failed as expected | `test_worktree_create_uses_central_root_auto_id_and_branch` | pass | central namespace path created |
| slci-005 | S03/S90 | yes | red-required / inspect-only | old HEAD current-test run failed as expected | sibling absence assertions and docs inspection | pass | no new sibling fallback or migration |
| slci-006 | S04 | yes | covered-existing / red-required | existing label/collision tests updated | invalid label, collision, branch prefix tests | pass | naming and collision rules preserved under central root |
| slci-007 | S04 | yes | covered-existing | existing bootstrap tests updated | bootstrap success/failure/detection/skipped tests | pass | bootstrap remains non-fatal |
| slci-008 | S05 | yes | red-required | old HEAD current-test run failed as expected | linked worktree normalization test | pass | main worktree basename drives namespace |
| slci-009 | S06 | yes | manual-required | N/A | `printenv`, `.zshenv` inspection, root creatability via runtime tests | pass | local setup is evidence only |
| slci-010 | S90 | yes | inspect-only | N/A | docs and parent Epic inspection | pass | central root is future contract |
| slci-011 | S90/S99 | yes | inspect-only | N/A | diff/docs inspection | pass | no list/remove/prune, no `$CODEX_HOME/worktrees` mixing |
| slci-012 | S90/S99 | yes | command evidence | N/A | `validate`, `sync`, targeted and full unittest discovery | pass | provider/dogfooding parity covered by tests |
| slci-013 | S100 | yes | PR evidence | N/A | PR Delivery Gate / Merge Preparation Gate | pending | PR creation and monitoring happen after initial commit/push |

### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| slci-001 | S01 | targeted worktree tests | pass | missing/blank env |
| slci-002 | S02 | targeted worktree tests | pass | invalid root variants |
| slci-003 | S02 | targeted worktree tests | pass | accepted symlink / `~` root |
| slci-004 | S03 | targeted worktree tests | pass | central root path |
| slci-005 | S03/S90 | targeted tests + docs inspection | pass | no sibling fallback |
| slci-006 | S04 | targeted worktree tests | pass | label/id/collision rules |
| slci-007 | S04 | targeted worktree tests | pass | bootstrap semantics |
| slci-008 | S05 | targeted worktree tests | pass | linked invocation |
| slci-009 | S06 | local shell inspection | pass | env export present; root creatability tested |
| slci-010 | S90 | docs/spec inspection | pass | future contract updated |
| slci-011 | S90/S99 | diff/docs inspection | pass | scope exclusions preserved |
| slci-012 | S90/S99 | `validate`, `sync`, unittest | pass | full system-Python suite OK |
| slci-013 | S100 | PR URL / monitor evidence | pending | to be recorded after PR creation |

### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | slci-001..slci-013 | N/A | same | plan closure ids are used directly | no | no |

### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/workspace/tools/spec-dock` | iss-00130 | current session | repo-analyst / system-architect / implementation-planner / spec-reviewer / code-reviewer / qa-reviewer | same repo, active issue, workflow-scoped; parent owns canonical docs and final closure | issue complete / scope change / user revocation | none | proceed |

### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S05/S90 | parent implementation with delegated review | tightly coupled runtime/docs/report integration after approved specs | repo-analyst / code-reviewer / qa-reviewer / spec-reviewer | read-only analysis and review gates | active issue requirement/design/plan | parent edited provider, dogfooding mirror, tests, docs, report | worker direct canonical edits | targeted tests, full suite, validate/sync, reviewer gates | P1 reviewer fail / validation fail | pass/fail findings and ledger notes | pass with P2 QA follow-up adopted |

### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01-S05/S90 | repo-analyst | implementation surfaces and test-harness risks identified | none | read-only | accepted | none | adopted in EAL-001 |
| S99 | code-reviewer | integrated diff satisfies central-root contract and mirror parity | none | read-only diff/test review | pass | none | adopted in EAL-003 |
| S99 | qa-reviewer | no P0/P1 coverage gaps; P2 invalid-label/report cleanup noted | none | read-only QA review | pass | P2 addressed locally | adopted in EAL-004 |
| S99/S100 | spec-reviewer | final report closure and PR evidence gaps found | none | read-only spec review | fail | S100 pending until PR exists | report closure updated; PR evidence deferred to post-PR commit |

### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01-S05/S90 | canonical docs/report and tightly coupled runtime/test/docs integration remained parent-owned per workflow | user instructed workflow execution with subagent use; no waiver | changed files in this issue diff | parent edited canonical specs/report, provider runtime/docs, dogfooding mirror, tests | revert central-root runtime/docs/tests to previous sibling placement | targeted tests, full suite, validate/sync | code-reviewer pass; qa-reviewer pass; spec-reviewer pending S100 | none |

### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S99 | final code review | code-reviewer | fresh | passed | N/A | proceed | no findings |
| S99 | final QA review | qa-reviewer | fresh | passed | N/A | proceed after P2 cleanup | invalid-label central side-effect coverage added |
| S99 | final code review follow-up | code-reviewer | fresh | passed | N/A | proceed after P2 cleanup | central-root help wording updated |
| S99 | final QA review follow-up | qa-reviewer | fresh | passed | N/A | proceed | EAL follow-up closed |
| S99/S100 | final spec review | spec-reviewer | fresh | failed | no | incomplete until PR evidence recorded | report placeholders and S100 evidence gap identified; non-PR report gaps fixed here |

### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S99 | pending initial commit | runtime, tests, docs, specs, report, discussions | pending | pending | N/A | N/A | N/A | N/A |
| S100 | pending post-PR evidence commit | PR delivery / merge-prep evidence in report | pending | pending | N/A | N/A | N/A | N/A |

### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - env gateway port を追加。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py` - required central root validation and placement を実装。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - env gateway を runtime ports に wiring。
- `tests/cli_runtime/test_worktree.py` - central root, invalid env/root, linked invocation, bootstrap/collision preservation tests を更新。
- `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` / `spec-dock/docs/reference_worktree.md` - user-facing central-root contract を更新。
- `spec-dock/active/issue/*.md` / parent Epic docs / `discussions/` - requirement/design/plan/report evidence and supersession context を記録。

### コミット
- pending

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| provider/dogfooding reference docs and parent Epic docs | yes | parent orchestrator | docs updated; `validate` and `sync` pass | pending final S100 rerun |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer `Locke` | whole issue obligation coverage | targeted + full suite sufficient with one P2 coverage improvement | `review_status: pass`; P2 invalid-label coverage adopted | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer `Halley` | issue-wide integrated diff | no findings | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer `Kepler` | requirement / design / plan / report / implementation / tests / docs alignment | report closure placeholders and S100 PR evidence missing; non-PR report gaps fixed here | 1 | pending rerun after PR evidence |

### PR Delivery Gate / Merge Preparation Gate（S100）
| 項目 | 証跡 | 結果 |
|---|---|---|
| PR URL / base / head / issue linkage | pending until PR creation | pending |
| latest pushed head SHA and monitored head match | pending until push / PR monitor | pending |
| CI / PR checks / Codex review state | pending until PR monitor | pending |
| S100 report evidence commit and re-push | pending after PR evidence is recorded | pending |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S01-S99 evidence recorded; S100 pending PR creation | initial implementation commit pending | PR body / final response / report S100 update | pending |

## 遭遇した問題と解決 (任意)
- 問題: `uvx --from . spec-dock update .` が central-root scope 外の dogfooding scaffold churn を発生させた。
  - 解決: D-001 として記録し、広範な生成差分を戻して relevant runtime/docs mirror だけを手動同期した。
- 問題: `uv run python -m unittest discover -v` が local `.venv` の pip 欠落で失敗した。
  - 解決: `python -m unittest discover -v` で同じ suite が成功することを確認し、local tooling state として分類した。

## 学んだこと (任意)
- worktree placement の contract 変更は provider runtime、dogfooding mirror、reference docs、parent Epic docs、issue docs を同時に閉じる必要がある。

## 今後の推奨事項 (任意)
- S100 は PR 作成後に PR URL、head SHA、checks / review 状態、delivery-evidence commit を report に追記してから final spec review を rerun する。

## 省略/例外メモ (必須)
- 該当なし
