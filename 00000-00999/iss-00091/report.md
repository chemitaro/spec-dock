---
種別: 実装報告書（Issue）
ID: "iss-00091"
タイトル: "Default Github State Commands"
関連GitHub: ["#91"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-11"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00090", "init-local-00003"]
---

# iss-00091 Default Github State Commands — 実装報告（LOG）

## 実装サマリー (任意)
- `sync` / `deps check` / `active set` の CLI default を GitHub live state enabled に反転し、明示 opt-out として `--no-github` を追加した。
- `--github` は後方互換 flag として維持し、`--github --no-github` は argparse の mutually exclusive error として固定した。
- provider assets と dogfooding mirrors の docs / skill / context-pack guidance を GitHub default と `--no-github` opt-out の語彙に同期した。

## 実装記録（セッションログ） (必須)

### 2026-05-11 17:28 JST

#### 対象
- Step: S01, S02, S03, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, EC-001, EC-002, EC-003

#### 実施内容
- `commands/sync.py`, `commands/deps.py`, `commands/active.py` で `--github` / `--no-github` を mutually exclusive group にし、request bool は no-flag と `--github` で GitHub enabled、`--no-github` で disabled になるようにした。
- provider runtime と dogfooding mirror の command files を同一契約に更新した。
- CLI runtime tests に default GitHub path、`--no-github` cache path、mutual exclusion、`new ... --no-github` rejected contract の regression を追加・更新した。
- provider docs / dogfooding docs / installed skill asset / checked-in skill mirror / context-pack guidance を `sync` default GitHub と `--no-github` opt-out へ更新した。
- 新しい GitHub issue-list cache file は追加していない。`--offline` も導入していない。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_sync tests.cli_runtime.test_deps tests.cli_runtime.test_active -v
# Ran 144 tests ... OK

python -m unittest tests.cli_runtime.test_new -v
# Ran 35 tests ... OK

python -m unittest tests.cli_runtime.test_wrappers -v
# Ran 6 tests ... OK

python -m unittest tests.cli_runtime.test_runtime_delete_s13 -v
# Ran 48 tests ... OK

python -m unittest tests.test_init_update -v
# Ran 163 tests ... OK

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=39

./spec-dock/scripts/spec-dock sync --no-github --no-update-active
# spec-dock: ok (sync) wrote=...

rg --files | rg '[A-Z]'
# Existing uppercase paths only: README.md / LICENSE / AGENTS.md and existing README.md files under shipped/docs/manual paths.

git diff --name-only | rg -n "cache|issue-list|github.*list|index-all"
# no matches

git status --short
# current uncommitted worktree contains modified implementation/docs/tests/report files only; no new cache file is present
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002, tc-003, tc-004, tc-005 | command parser default true / no-github false / mutual exclusion | `tests.cli_runtime.test_sync`, `test_deps`, `test_active` | pass | application fetch/cache layers unchanged |
| S02 | tc-006, tc-007, tc-008, tc-009 | default GitHub, cache-only opt-out, new rejection, no new cache | runtime tests + diff inspection | pass | `new ... --no-github` rejected tests remain green |
| S03 | tc-010 | docs and skill parity | `tests.cli_runtime.test_wrappers`, `tests.test_init_update` | pass | provider and mirror docs/skills updated |
| S99 | tc-011 | final quality gate | targeted tests, validate, sync, uppercase path check, no-new-cache inspection | pass | full `tests.test_init_update` also passed |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | old no-flag sync was cache-first | `python -m unittest tests.cli_runtime.test_sync -v` via combined command | pass | no-flag sync uses gh stub |
| tc-002 | S01/S02 | yes | red-required | old no-flag local tests expected no gh | `python -m unittest tests.cli_runtime.test_sync -v` via combined command | pass | `sync --no-github` cache path kept |
| tc-003 | S01/S02 | yes | red-required | old deps default was cache-first | `python -m unittest tests.cli_runtime.test_deps -v` via combined command | pass | no-flag deps check uses GitHub snapshots |
| tc-004 | S01/S02 | yes | red-required | old active default was cache-first | `python -m unittest tests.cli_runtime.test_active -v` via combined command | pass | active set default deps guard uses GitHub |
| tc-005 | S01/S02 | yes | red-required | conflict was untested | combined runtime tests | pass | `--github --no-github` exits 2 |
| tc-006 | S02 | yes | covered-existing | existing new rejection contract | `python -m unittest tests.cli_runtime.test_new -v` | pass | no local-only creation revival |
| tc-007 | S02 | yes | covered-existing | existing warning behavior | combined runtime tests | pass | gh fetch failure tests unchanged semantically |
| tc-008 | S02 | yes | red-required | old guard used no-flag | combined runtime tests | pass | guard logs absent under `--no-github` |
| tc-009 | S02/S99 | yes | inspect-required | no cache file expected | `git diff --name-only`, `git status --short`, and `git diff --name-only \| rg -n "cache\|issue-list\|github.*list\|index-all"` | pass | current uncommitted diff/status show modified tracked implementation/docs/tests/report files only; cache-name scan has no matches |
| tc-010 | S03 | yes | inspect-only | docs had `--github` required wording | wrapper/init-update tests + rg stale scan | pass | docs/skill/context guidance updated |
| tc-011 | S99 | yes | manual-required | final evidence required | commands listed above | pass | uppercase check found existing uppercase paths only |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-001..tc-005 | S01 | combined sync/deps/active runtime suite | pass | 145 tests OK |
| tc-006..tc-009 | S02 | new/runtime suites + no-new-cache diff inspection | pass | no new full GitHub issue-list cache |
| tc-010 | S03 | docs/skill parity tests | pass | provider/mirror parity retained |
| tc-011 | S99 | validate + sync --no-github + uppercase path check | pass | existing uppercase paths unchanged |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | re-review required |
|---|---|---|---|---|---|
| changed | tc-002, tc-008 | old without-github test names | tc-002, tc-008 | test names predated explicit `--no-github`; behavior now uses opt-out flag | no |
| added | tc-005 | `*_rejects_github_and_no_github_together` | tc-005 | argparse mutual exclusion regression coverage | no |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/{sync.py,deps.py,active.py}` - GitHub default / `--no-github` / mutual exclusion
- `spec-dock/scripts/spec_dock_runtime/commands/{sync.py,deps.py,active.py}` - dogfooding mirror
- `src/spec_dock/assets/spec_dock/docs/**`, `spec-dock/docs/**`, `src/spec_dock/assets/spec_dock/scripts/README.md`, `spec-dock/scripts/README.md` - docs wording
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`, `.agents/skills/spec-dock-issue-execution/SKILL.md` - skill reminders
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{app.py,application/delete_node.py,application/set_active.py,infra/active_store.py,presentation/json_state.py}` and mirrors - context/recovery guidance
- `tests/cli_runtime/{test_sync.py,test_deps.py,test_active.py,test_validate.py,test_wrappers.py,test_runtime_delete_s13.py}` and `tests/test_init_update.py` - regression and assertion updates
- `spec-dock/active/issue/report.md` - evidence

#### コミット
- 未作成

#### メモ
- `tests/test_init_update -v` の初回実行では、current workspace に追加済みの `epic-00090` / `iss-00091` `.meta.json` が fixed dogfooding snapshot に未反映だったため 1 件失敗。snapshot list / depends_on map を更新し、単体確認後に full `tests.test_init_update` を再実行して pass。

---

## 遭遇した問題と解決 (任意)
- 問題: 既存 active issue / epic の `.meta.json` が dogfooding fixed snapshot に未反映で `tests.test_init_update` が一度失敗。
  - 解決: `tests/test_init_update.py` の checked-in dogfooding snapshot に `epic-00090` / `iss-00091` を追加し、full suite を再実行して pass。

### 2026-05-11 17:43 JST - Review Cycle Follow-up

#### 対象
- Step: S02, S03, S99
- AC/EC: AC-002, AC-004, AC-007, tc-004, tc-008, tc-010, tc-011

#### 実施内容
- `src/spec_dock/cli.py` の installer-generated context-pack renderer を GitHub default / cache-local opt-out 表現へ更新した。
- `tests/test_init_update.py` に fresh init/update context-pack assertion を追加し、bare `sync` が GitHub default、`sync --no-github` が cache/local opt-out として案内されることを固定した。
- `tests/cli_runtime/test_active.py` に no-flag `active set <target>` が hermetic `gh` stub live state を使う regression を追加した。依存 issue が open なら block、closed なら pass し、setup は `--no-github` で real `gh` を避ける。
- `tests/cli_runtime/test_sync.py` の `sync --no-github` cache path に failing/logging `gh` guard を追加し、明示 opt-out で `gh` が呼ばれないことを固定した。
- `src/spec_dock/assets/spec_dock/scripts/README.md` と `spec-dock/scripts/README.md` から `new issue --no-github` の local-only 成功例を削除し、`--no-github` は node creation rejected contract として説明した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_active -v
# Ran 37 tests ... OK

python -m unittest tests.cli_runtime.test_sync -v
# Ran 26 tests ... OK

python -m unittest tests.test_init_update -v
# Ran 163 tests ... OK

rg -n -- "local-only|--no-github.*local-only|state \\(local\\)|state \\(github\\)|sync --github" src/spec_dock/cli.py src/spec_dock/assets/spec_dock/scripts/README.md spec-dock/scripts/README.md tests/test_init_update.py
# only negative assertions in tests/test_init_update.py matched
```

#### 変更したファイル
- `src/spec_dock/cli.py` - installer-generated context-pack command guidance
- `src/spec_dock/assets/spec_dock/scripts/README.md`, `spec-dock/scripts/README.md` - stale local-only new examples removed
- `tests/cli_runtime/test_active.py` - no-flag active set live-state deps guard coverage
- `tests/cli_runtime/test_sync.py` - `sync --no-github` no-gh guard coverage
- `tests/test_init_update.py` - init/update context-pack assertions
- `spec-dock/active/issue/report.md` - review follow-up evidence

### 2026-05-11 18:08 JST - Cycle 2 P2 Recovery Hint Follow-up

#### 対象
- Step: S02, S03
- AC/EC: AC-002, AC-004, tc-008, tc-010

#### 実施内容
- GitHub fetch failure / missing `gh` recovery hints の stale wording を provider と dogfooding mirror で更新した。
- 旧 guidance の no-GitHub recovery hints は、GitHub default 後の contract に合わせて `--no-github` による cache/local state opt-out 表現へ置き換えた。
- `new ... --no-github` は rejected contract のため、共通 `gh` 不在エラーでは `new` の opt-out と誤読されない wording にした。

#### 実行コマンド / 結果
```bash
rg -n -i -- "omit.*github|omitting.*github|without github|without --github|re-run without --github|--no-github' for 'new'|omit '--github'" src/spec_dock spec-dock/scripts spec-dock/docs .agents tests
# no matches

python -m unittest tests.cli_runtime.test_sync -v
# Ran 26 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - GitHub fetch failure recovery hint
- `spec-dock/scripts/spec_dock_runtime/app.py` - dogfooding mirror
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py` - missing `gh` recovery hint
- `spec-dock/scripts/spec_dock_runtime/infra/github_cli.py` - dogfooding mirror
- `spec-dock/active/issue/report.md` - cycle 2 evidence

### 2026-05-11 18:18 JST - Final Verification

#### 対象
- Step: S99
- AC/EC: AC-001 through AC-007, EC-001 through EC-003, tc-001 through tc-011

#### レビュー結果
- Fresh code review cycle 2:
  - result: pass
  - note: P2 recovery hint finding was fixed in the Cycle 2 P2 follow-up.
- Fresh QA review cycle 2:
  - result: pass
  - note: no remaining AC/EC or closure coverage findings.

#### 実行コマンド / 結果
```bash
rg -n -i -- "omit.*github|omitting.*github|without github|without --github|re-run without --github|--no-github' for 'new'|omit '--github'" src/spec_dock spec-dock/scripts spec-dock/docs .agents tests
# no matches

python -m unittest tests.cli_runtime.test_sync tests.cli_runtime.test_deps tests.cli_runtime.test_active -v
# Ran 145 tests ... OK

python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_wrappers tests.cli_runtime.test_runtime_delete_s13 -v
# Ran 89 tests ... OK

python -m unittest tests.test_init_update -v
# Ran 163 tests ... OK

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=39

./spec-dock/scripts/spec-dock sync --no-github --no-update-active
# spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,...

git diff --check
# no output

git diff --name-only | rg -n "cache|issue-list|github.*list|index-all"
# no matches

rg --files | rg '[A-Z]'
# existing uppercase paths only: README.md, LICENSE, AGENTS.md, and existing README.md files
```

#### Final status
- implementation: pass
- code review: pass
- QA review: pass
- no-new-full-cache inspection: pass
- GitHub live network manual sync: not run; hermetic `gh` stubs cover live-state default behavior.

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## 省略/例外メモ (必須)
- GitHub live network を使う手動 `sync` は実行していない。live state default は hermetic gh stubs を使う CLI runtime tests で確認した。
