# epic-00224 stdout guidance handoff 再手動テスト計画

## 目的

この再手動テストでは、前回の手動テスト合格後に追加した `guidance` command と skill handoff 修正が、実運用で期待通り働くことを確認する。

主な確認観点は次の通り。

- agent が runbook projection file を二段階参照せず、`spec-dock guidance <target>` の標準出力から現在の案内を取得できること
- `workflow next` が primary surface / fallback alias として残っていないこと
- runbook projection は人間向けの副産物であり、書き込み失敗しても guidance 自体は非ブロックになること
- context packet は agent handoff の正本なので、書き込み失敗時は fail closed のままであること
- 前回修正した runtime/docs/security routing が今回の guidance 経由でも退行していないこと
- issue planning / execution skill が `guidance issue-planning` / `guidance issue-execution` を参照し、agent task checklist への登録を促すこと

## 対象範囲

- provider source:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- dogfooding mirror:
  - `spec-dock/scripts/spec-dock`
  - `spec-dock/scripts/spec_dock_runtime/**`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
- 隔離した trial repository における installed runtime の挙動
- 既存の focused automated regression の再実行

## 対象外

- 新しい GitHub repository の作成
- production GitHub issue / PR への mutation
- dynamic resource allocation policy 全体の再設計
- 前回すでに通過した PR observation fake-gh matrix の全量再実施

## 手動テスト用 workspace

- Root: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/`
- Trial repo: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/workspaces/trial-local-repo`
- Evidence directory: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/evidence/`
- Execution log: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/execution-log.md`
- Summary report: `manual-tests/epic-00224-dynamic-workflow-resource-allocation/retest-20260626-guidance-handoff/summary-report.md`

## 外部 GitHub repository の要否

新しい GitHub repository は不要とする。今回の確認対象は local runtime / installed scaffold / skill handoff で閉じており、`--github-issue <n>` を使った既存番号リンクと local trial repository で再現できる。

## テストマトリクス

| ID | 分類 | シナリオ | 操作 | 期待結果 | 証跡 |
|---|---|---|---|---|---|
| MT-G01 | command surface | dogfooding mirror で guidance command が使える | `./spec-dock/scripts/spec-dock guidance --help` / `guidance issue-execution` | target は `issue-planning` / `issue-execution`、active issue なしでは issue start を促す | `evidence/mt-g01-*` |
| MT-G02 | command removal | `workflow next` が primary / alias として残っていない | `./spec-dock/scripts/spec-dock workflow --help`; `workflow next issue-execution` | help に `next` がなく、`workflow next` は失敗する | `evidence/mt-g02-*` |
| MT-G03 | skill handoff | issue planning / execution skill が guidance stdout を正本にしている | provider と dogfooding mirror の skill を inspect | `guidance issue-planning` / `guidance issue-execution` を実行する指示があり、projection file を読む指示がない | `evidence/mt-g03-*` |
| MT-G04 | fresh install | 現在の provider から trial repo を初期化する | `uv run python -m spec_dock.cli init <trial>` | installed runtime に `guidance` が含まれる | `evidence/mt-g04-*` |
| MT-G05 | real hierarchy | trial repo に実運用風の initiative / epic / issue を作る | `new initiative/epic/issue --github-issue <n>` | hierarchy が作成でき、node 作成後は `validate` が通る | `evidence/mt-g05-*` |
| MT-G06 | planning guidance | scaffold issue を start して planning guidance を取得する | `issue start <issue>`; `guidance issue-planning` | requirement capture / requirement scaffold の案内が stdout に出る | `evidence/mt-g06-*` |
| MT-G07 | execution guidance | 実装可能な runtime task を guidance 経由で取得する | requirement / assurance / plan を最小実体化し `guidance issue-execution` | `dev-coder` / `medium` / `unit_tests` が guidance stdout に出る | `evidence/mt-g07-*` |
| MT-G08 | human projection | guidance 実行時に projection は生成されるが正本ではない | `active/current-runbook.md` / `.json` を inspect | projection は人間向けに存在するが、同じ情報を stdout から得られる | `evidence/mt-g08-*` |
| MT-G09 | stale projection ignored | 古い projection を置いてから guidance を実行する | stale `current-runbook.json` を手動配置し `guidance issue-execution` | stdout と projection が現在の active issue に更新され、古い issue id を採用しない | `evidence/mt-g09-*` |
| MT-G10 | projection failure non-blocking | runbook projection path を unsafe symlink 化する | `current-runbook.json` を外部 symlink にして `guidance issue-execution` | guidance は exit 0 で stdout を返し、projection error は補助情報に留まる | `evidence/mt-g10-*` |
| MT-G11 | context packet fail closed | context packet 書き込み失敗は引き続き blocking | focused regression を実行 | `context-packet-write-failure` 系が fail closed する | `evidence/mt-g11-*` |
| MT-G12 | routing regression | 前回修正した runtime/docs/security routing を focused regression で確認する | `uv run pytest ...` | runtime / docs-only / security-sensitive の誤分類が再発しない | `evidence/mt-g12-*` |
| MT-G13 | quality gate spot check | 今回変更面の automated regression を再実行する | `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_wrappers.py` | 全件成功する | `evidence/mt-g13-*` |
| MT-G14 | cleanup | main checkout の予期しない dirty を確認する | `git status --short --branch` | 手動テスト artifact 以外に予期しない差分がない | `evidence/mt-g14-*` |

## 受け入れ条件

- 全 test case に `PASS` / `FAIL` / `BLOCKED` / `SKIPPED` のいずれかを記録する。
- `FAIL` / `BLOCKED` があれば、観測結果、原因仮説、対応方針を記録する。
- 新しい GitHub repository や production GitHub state を変更しない。
- guidance の正本が stdout であり、projection は human-readable snapshot に限定されることを確認する。
- 手動テスト後に summary report を日本語で作成する。
