---
種別: 実装報告書（Issue）
ID: "iss-00064"
タイトル: "Update User Facing Docs Help"
関連GitHub: ["#64"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-11"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00064 Update User Facing Docs Help — 実装報告（LOG）

## 実装サマリー
- dependency metadata unification と command-first mutation の利用者向け導線を、provider-side docs / dogfooding mirror / skill guidance に揃える issue として実施する。
- 本 report では spec review、step review、verification、final close evidence を記録する。

## 実装記録（セッションログ）

### 2026-04-11 11:00 - 11:30

#### 対象
- Step: contract setup
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- `iss-00063` の discussion に残した利用者向け docs gap analysis を根拠に、`iss-00064` の requirement / design / plan を docs/help/skill 整合 issue として具体化した。
- active issue を `iss-00064` に設定し、branch `iss-00064-update-user-facing-docs-help` を作成して checkout した。
- 誤作成した duplicate issue `iss-00065` は close + delete で整理した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock active set iss-00064 --github
./spec-dock/scripts/spec-dock close iss-00065
./spec-dock/scripts/spec-dock delete iss-00065 --yes
git checkout -b iss-00064-update-user-facing-docs-help

active issue: iss-00064
current branch: iss-00064-update-user-facing-docs-help
duplicate issue iss-00065: closed and deleted
```

#### 変更したファイル
- `spec-dock/.../iss-00064-update-user-facing-docs-help/requirement.md` - issue requirement を具体化
- `spec-dock/.../iss-00064-update-user-facing-docs-help/design.md` - docs/help/skill 修正方針を具体化
- `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md` - step / review / verification plan を具体化
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md` - 初期ログを記録

#### コミット
- 未実施

#### メモ
- 次に SG1 spec review を実施し、pass までブラッシュアップする。

---

## 省略/例外メモ
- `apply_patch` がこのセッションでは file open error を返したため、issue docs のみ shell redirect で安全に上書きした。runtime / docs 実装本体はこの後 sub-agent に委任する。

---

### 2026-04-11 11:30 - 11:45

#### 対象
- Step: SG1 spec review
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- spec reviewer から 3 件の指摘を受領した。
- P1 指摘に対応して、workflow 文書を in-scope に追加し、provider-side / mirror / skill の対象ファイル集合を固定した。
- P2 指摘に対応して、S99 に docs-only diff boundary gate を追加し、runtime 実装領域が差分に含まれた場合は fail とする契約へ更新した。

#### 実行コマンド / 結果
```bash
spec review (SG1)

review_status=fail
findings:
- workflow docs を対象として明示すること
- review 対象ファイル集合を閉じること
- docs-only boundary の diff gate を追加すること
```

#### 変更したファイル
- `spec-dock/.../iss-00064-update-user-facing-docs-help/design.md` - 対象ファイル集合と verification mapping を固定
- `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md` - workflow docs を in-scope 化し、review pass 条件と docs-only diff gate を追加
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md` - review fail と修正内容を追記

#### コミット
- 未実施

#### メモ
- 修正後の SG1 再レビューを実施する。

### 2026-04-11 11:45 - 12:05

#### 対象
- Step: SG1 spec review re-run
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- review 指摘を受けて `design.md` と `plan.md` を再整理した。
- QG1 の grep / command evidence を closed target file set に限定した。
- `Optional Tests` を `tests/test_init_update.py` と `tests/cli_runtime/test_wrappers.py` に固定した。
- `deps.json` / `meta.json` の扱いを blanket ban ではなく legacy framing contract と strict current-doc set へ分離した。
- `report.md` の ownership separation を required heading で機械検証できる設計に更新した。

#### 実行コマンド / 結果
```text
spec review (SG1 re-run)

review_status=pass
findings=[]
reviewer=Bohr
focus:
- QG1 file-set scoping
- fixed Optional Tests
- legacy-name semantic exception handling
- report ownership separation
```

#### 変更したファイル
- `spec-dock/.../iss-00064-update-user-facing-docs-help/design.md` - legacy framing / report contract / concrete test surface を明文化
- `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md` - QG1 closed-set verification / fixed Optional Tests / report ownership check を具体化
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md` - SG1 re-run pass を追記

#### コミット
- 未実施

#### メモ
- 次は issue docs を SG1 pass 状態でコミットし、S01 の実装を dev coder に委任する。

### 2026-04-11 12:05 - 12:35

#### 対象
- Step: S01 / RG1
- AC/EC: AC-001, AC-002, AC-003, EC-002

#### 実施内容
- provider-side docs SoT 10 ファイルを current contract に更新した。
- `./spec ...` を `./spec-dock/scripts/spec-dock ...` に統一した。
- `guide.md` / `reference_deps.md` / `reference_sync.md` / `reference_github.md` で `.meta.json` top-level `depends_on` と command-first mutation を明示した。
- `README.md` / workflow 群 / reference 群に `deps add/remove/check` と `validate` / `sync --github` の導線を追加した。
- `workflow_tree.md` は実ファイル名が `workflow-tree.md` のため、その実体に対して修正した。

#### 実行コマンド / 結果
```bash
rg -n '\./spec\s' src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,reference_deps.md,reference_sync.md,reference_github.md}
# result: no output

rg -n 'deps\.json|meta\.json' src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md}
# result: no output

python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure
# result: OK

python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs
# result: OK
```

#### レビュー結果
```text
RG1 implementation review
review_status=pass
reviewer=Heisenberg
findings=[]
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/workflow-tree.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- `src/spec_dock/assets/spec_dock/docs/reference_github.md`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`

#### コミット
- 未実施

#### メモ
- 次は S02 として dogfooding mirror / old docs を current contract に揃える。

### 2026-04-11 12:35 - 13:10

#### 対象
- Step: S02 / RG2
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002

#### 実施内容
- dogfooding mirror docs 10 ファイルを provider-side docs SoT と整合する内容に更新した。
- `workflow-issue.md` / `workflow-adr.md` / `sync.md` / `spec-dock-guide-old.md` を deprecated / historical alias または shortcut として再整理した。
- old/secondary docs では current doc link、current command path、legacy framing を明示した。
- `sync.md` と `spec-dock-guide-old.md` で `.meta.json` top-level `depends_on` と `deps add/remove/check` の command-first mutation を追記した。
- `Optional Tests` 2 ファイルは変更不要だったため no-op とした。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests.test_init_update.TestInitUpdate.test_reference_sync_doc_matches_bundled_asset \
  tests.test_init_update.TestInitUpdate.test_reference_deps_doc_matches_bundled_asset \
  tests.test_init_update.TestInitUpdate.test_workflow_issue_doc_matches_bundled_asset \
  tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure \
  tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs
# result: Ran 6 tests ... OK
```

#### レビュー結果
```text
RG2 implementation review
review_status=pass
reviewer=Gauss
findings=[]
```

#### 変更したファイル
- `spec-dock/docs/README.md`
- `spec-dock/docs/guide.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow-issue.md`
- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_initiative.md`
- `spec-dock/docs/workflow-tree.md`
- `spec-dock/docs/workflow_adr.md`
- `spec-dock/docs/workflow-adr.md`
- `spec-dock/docs/reference_deps.md`
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/sync.md`
- `spec-dock/docs/spec-dock-guide-old.md`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`

#### コミット
- 未実施

#### メモ
- 次は S03 として skills / optional tests / final QA evidence を閉じる。

### 2026-04-11 13:10 - 14:10

#### 対象
- Step: S03 / RG3 / QG1 preparation
- AC/EC: AC-001, AC-002, AC-003, EC-003

#### 実施内容
- skill への command guidance を role-based minimal policy に整理した。
- `spec-dock-issue-execution` のみ concrete `deps add/remove/check` と `validate` / `sync --github` を保持し、hub / host adapter は docs 参照中心へ戻した。
- user follow-up を受けて duplication を再評価し、過剰な同文コマンド block を削減した。
- `tests/test_init_update.py` の checked-in dogfooding snapshot 定数に `iss-00064` を追加した。
- `.meta.json` only contract に合わせて runtime subprocess parity tests の fixture を `deps.json` から `.meta.json` へ更新した。
- QG1 実測中に `./spec-dock/...` を誤検知する `./spec\b` regex を発見したため、`plan.md` の strict negative check を `./spec(\s|$)` へ補正した。

#### 実行コマンド / 結果
```bash
rg -n '\./spec(\s|$)' src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md} spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md} src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md .agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md
# result: no output

rg -n 'deps\.json|meta\.json' src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md} spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md} src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md .agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md
# result: no output

./spec-dock/scripts/spec-dock --help
# result: ok; commands include new, active, delete, close, sync, deps, import, validate, doctor

./spec-dock/scripts/spec-dock deps --help
# result: ok; deps subcommands include check, add, remove

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=23

./spec-dock/scripts/spec-dock sync --github
# result: spec-dock: ok (sync) ... active unchanged (matched id in branch: iss-00064)

python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers
# result: Ran 117 tests in 13.274s\n# result: OK
```

#### レビュー結果
```text
RG3 implementation review
review_status=pass
reviewer=Ptolemy
findings=[]
```

#### 変更したファイル
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md`
- `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md`
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- `tests/test_init_update.py`
- `tests/cli_runtime/test_wrappers.py`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`

#### コミット
- 未実施

#### メモ
- 次は QA reviewer による QG1 判定と、S99 final diff review quality gate を行う。

## Docs-Only Sanity Checks (iss-00064)
- この issue で保持する正本証跡は docs/help/skill follow-up に対する sanity check のみ。
- 実測済み command evidence:
  - `./spec-dock/scripts/spec-dock --help`
  - `./spec-dock/scripts/spec-dock deps --help`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
- 実測済み test evidence:
  - `python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers`
- 実装判断:
  - skills は role-based minimal policy とし、具体 command block は `spec-dock-issue-execution` に限定した。
  - hub / host adapter は current runtime path guardrail と docs reference を持つ薄い adapter とした。

## Canonical Evidence Owners (read-only references)
- `iss-00060`
  - provider-side dependency reference docs refresh の canonical owner。
- `iss-00062`
  - hard cutover `validate` / `sync` readiness と dependency metadata cutover evidence の canonical owner。
- `iss-00063`
  - final regression parity / close review / epic close evidence の canonical owner。
- `iss-00064`
  - 上記 owner を置き換えず、利用者向け docs/help/skill の follow-up sanity check と wording alignment のみを扱う。

### 2026-04-11 14:10 - 14:35

#### 対象
- Step: QG1 hardening follow-up
- AC/EC: EC-003

#### 実施内容
- QA review の non-blocking 指摘を受けて、QG1 regex を future rerun でも有効な形に修正した。
- checked-in `.agents` mirror skill の parity coverage を `tests/test_init_update.py` に追加した。
- full optional test suite を再実行し、117 tests の成功を再確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers
# result: Ran 117 tests in 12.440s
# result: OK
```

#### レビュー結果
```text
QG1 QA review
review_status=pass
reviewer=Fermat
findings:
- [P2] strict current-doc grep regex correction in plan.md
- [P2] checked-in mirror parity coverage for hub/issue skills
resolution:
- both addressed before close-out
```

#### 変更したファイル
- `tests/test_init_update.py`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`

#### コミット
- 未実施

#### メモ
- 次は S99 final diff review quality gate を実施する。


### 2026-04-11 14:36 - 14:55

#### 対象
- Step: S99 close-out verification
- AC/EC: EC-003

#### 実施内容
- user follow-up を受けて、skill command guidance の duplication を final close 条件として再点検した。
- final reviewer では、issue-execution にのみ concrete command block を残し、hub / host adapter は runtime path guardrail と docs reference のみに留める方針が regression なく維持されていることを確認した。
- full target suite、runtime help、`validate`、`sync --github` を再実測し、close-out 時点の working tree 差分が docs/help/skill follow-up と parity test hardening のみであることを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers
# result: Ran 117 tests in 12.648s
# result: OK

./spec-dock/scripts/spec-dock --help
# result: ok; commands include new, active, delete, close, sync, deps, import, validate, doctor

./spec-dock/scripts/spec-dock deps --help
# result: ok; deps subcommands include check, add, remove

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=23

./spec-dock/scripts/spec-dock sync --github
# result: spec-dock: sync: active unchanged (matched id in branch: iss-00064)
# result: spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md
```

#### レビュー結果
```text
S99 final diff QA review
review_status=pass
reviewer=Ohm
findings=[]
residual_risks:
- 一部は文字列断片一致ベースの検証のため、意味同等な wording 変更には検出粒度が粗い可能性がある。
```

#### 変更したファイル
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md`
- `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md`
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- `tests/test_init_update.py`
- `tests/cli_runtime/test_wrappers.py`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/design.md`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md`
- `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`

#### コミット
- 未実施

#### メモ
- 実装・review・verification は完了。残作業は final commit と clean tree 確認のみ。
