# epic-00224 stdout guidance handoff 再手動テスト実施記録

## 環境

- メイン checkout: `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock`
- ブランチ: `iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files`
- テスト対象 commit: `3d0a2bb893189c70cbbd037106e501522794bdc3`
- Trial repo: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/workspaces/trial-local-repo`
- Evidence directory: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/evidence/`
- 実施日: 2026-06-26 JST
- 外部 GitHub mutation: なし

## 結果

| ID | Status | Observed result |
|---|---|---|
| MT-G01 | PASS | dogfooding mirror の `guidance --help` は `issue-planning` / `issue-execution` を表示し、active issue なしの `guidance issue-execution` は `state=no-active` / `next_action=issue-start-required` を stdout に返した。 |
| MT-G02 | PASS | `workflow --help` は `status` のみを表示し、`workflow next issue-execution` は invalid choice で終了した。 |
| MT-G03 | PASS | provider / dogfooding mirror の issue planning / execution skill は `guidance issue-planning` / `guidance issue-execution` を参照し、runbook projection file を agent handoff の正本として読む指示は見つからなかった。 |
| MT-G04 | PASS | `uv run python -m spec_dock.cli init <trial>` が成功し、installed runtime の `guidance --help` も期待通り表示された。 |
| MT-G05 | PASS | fake `gh` と `--github-issue` で `init-09001` / `epic-09002` / `iss-09004` を作成し、node 作成後の `validate` は成功した。 |
| MT-G06 | PASS with note | lifecycle guard により通常の `issue start` / `active set` は未準備 issue を blocked とした。`active set --force --no-checkout` で active にした後、`guidance issue-planning` は scaffold requirement に対する planning guidance を返した。 |
| MT-G07 | PASS | 最小の requirement / plan / report と assurance classification 後、`guidance issue-execution` は `ready` / `execution-ready` を返し、`dev-coder` / `medium` / `unit_tests` を stdout に表示した。 |
| MT-G08 | PASS | `spec-dock/active/current-runbook.md` / `.json` は生成され、`Human-facing projection; not agent handoff authority.` と `authority: non-canonical` を含んだ。同等の guidance は stdout から取得できた。 |
| MT-G09 | PASS | `iss-99999` / `stale-next-action` を含む stale projection を配置した後でも、再実行した stdout は `active_issue: iss-09004` / `next_action: execution-ready` を返し、stale 値を採用しなかった。 |
| MT-G10 | PASS | `spec-dock/active/current-runbook.json` を外部 symlink にした状態で `guidance issue-execution` は exit 0。stdout は ready guidance を返し、projection は `written: false` と symlink拒否エラーを表示した。外部 target file は作られなかった。 |
| MT-G11 | PASS | context packet write failure focused regression は `1 passed`。runbook projection failure と異なり、context packet failure は fail closed のまま維持される。 |
| MT-G12 | PASS | routing focused regression は `4 passed, 22 deselected`。runtime / docs-only / negated security / security-sensitive の退行は見つからなかった。 |
| MT-G13 | PASS | 今回変更面の CLI regression は `17 passed`。`tests/cli_runtime/test_workflow.py` と `tests/cli_runtime/test_wrappers.py` が成功した。 |
| MT-G14 | PASS | メイン checkout の `git status --short --branch` は branch 行のみ。手動テスト artifact は ignore 対象のため、tracked へ含める場合は明示的な `git add -f` が必要。 |

## コマンド記録

- `./spec-dock/scripts/spec-dock guidance --help`
- `./spec-dock/scripts/spec-dock guidance issue-execution`
- `./spec-dock/scripts/spec-dock workflow --help`
- `./spec-dock/scripts/spec-dock workflow next issue-execution`
- `uv run python -m spec_dock.cli init manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/workspaces/trial-local-repo`
- `env PATH=<fake-bin>:$PATH ./spec-dock/scripts/spec-dock new initiative --title "Manual Workflow Trial" --github-issue 9001`
- `env PATH=<fake-bin>:$PATH ./spec-dock/scripts/spec-dock new epic --initiative 9001 --title "Adaptive Guidance Manual Trial" --github-issue 9002`
- `env PATH=<fake-bin>:$PATH ./spec-dock/scripts/spec-dock new issue --epic 9002 --title "Runtime Guidance Manual Task" --github-issue 9004`
- `./spec-dock/scripts/spec-dock validate`
- `env PATH=<fake-bin>:$PATH ./spec-dock/scripts/spec-dock issue start iss-09004`
- `env PATH=<fake-bin>:$PATH ./spec-dock/scripts/spec-dock active set --id iss-09004 --force --no-checkout`
- `./spec-dock/scripts/spec-dock guidance issue-planning`
- `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-09004 --format json`
- `./spec-dock/scripts/spec-dock guidance issue-execution`
- `uv run pytest tests/cli_runtime/test_workflow_context_routing.py::TestWorkflowContextRouting::test_context_packet_write_failure_blocks_ready_issue_execution`
- `uv run pytest tests/cli_runtime/test_workflow_context_routing.py -k "assurance_policy_matrix or negated_security_phrase or runtime_path_overrides or docs_only"`
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_wrappers.py`
- `git status --short --branch`

## 証跡

- `evidence/mt-g01-guidance-help.txt`
- `evidence/mt-g01-no-active-guidance.txt`
- `evidence/mt-g02-workflow-help.txt`
- `evidence/mt-g02-workflow-next-rejected.txt`
- `evidence/mt-g03-skill-handoff-rg.txt`
- `evidence/mt-g04-init.txt`
- `evidence/mt-g04-installed-guidance-help.txt`
- `evidence/mt-g05-new-initiative.txt`
- `evidence/mt-g05-new-epic.txt`
- `evidence/mt-g05-new-issue-runtime.txt`
- `evidence/mt-g05-validate.txt`
- `evidence/mt-g06-issue-start.txt`
- `evidence/mt-g06-active-set.txt`
- `evidence/mt-g06-active-set-force.txt`
- `evidence/mt-g06-guidance-planning-scaffold.txt`
- `evidence/mt-g07-assurance-classify.json`
- `evidence/mt-g07-guidance-execution-ready.txt`
- `evidence/mt-g08-current-runbook-md-head.txt`
- `evidence/mt-g08-current-runbook-json-pretty.txt`
- `evidence/mt-g09-guidance-after-stale-projection.txt`
- `evidence/mt-g09-current-runbook-json-after-refresh.txt`
- `evidence/mt-g10-guidance-with-symlinked-projection.txt`
- `evidence/mt-g11-context-packet-fail-closed-pytest.txt`
- `evidence/mt-g12-routing-regression-pytest.txt`
- `evidence/mt-g13-quality-gate-pytest.txt`
- `evidence/mt-g14-main-status.txt`
