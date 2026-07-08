---
種別: 実装計画書（Issue）
ID: "iss-00307"
タイトル: "Final Quality Gate PR Delivery"
関連GitHub: ["#307"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
authorized_profile: "standard"
---

# iss-00307 Final Quality Gate PR Delivery — Issue 実装計画書

## 1. 実装方針

このIssueは、Epic 00295の最終quality gateとPR deliveryを担う。新機能追加を目的にせず、C01〜C11で実装済みのruntime / skills / docs / tests / workflowをEpic単位で検証し、必要なrepairだけを行う。

このIssueではPR deliveryを実施する。中間Issueと違い、deferred PR delivery gateは使わない。

## 2. Spec-Locked Closure Index

| closure_id | requirement | design | closes | evidence level | required evidence |
|---|---|---|---|---|---|
| CLOS-001 | AC-001 | G1 | C01〜C11 completion / deferred PR evidence / dependency closure | inspection + command | Issue closure index in `report.md`; deps check |
| CLOS-002 | AC-002, AC-003 | G6 | baseline validation and whitespace gate | command | `git diff --check`; `spec-dock validate` |
| CLOS-003 | AC-004 | G6 | main sync / divergence handling | command + report | `git fetch`; `rev-list`; merge/re-run evidence if needed |
| CLOS-004 | AC-005, AC-015 | G3, G5 | authoring supported/deferred command inventory consistency | command + inspection | help smoke; docs/skills/runtime grep |
| CLOS-005 | AC-006, AC-007 | G4, local wrapper audit | backend command contract and no hard-coded local wrapper dependency | command + grep | backend unset/override checks; local path grep |
| CLOS-006 | AC-008 | G4 | `local-context` lower-authority evidence mode | command | positive/negative preflight output |
| CLOS-007 | AC-009, AC-010 | G4 | ZIP/tree review, stage, authority boundary | test + command | authoring pytest / fixture output; forbidden claim checks |
| CLOS-008 | AC-011, AC-012, AC-013 | G4 | candidate, draft adoption, approval validators | test + command | authoring pytest / validator commands |
| CLOS-009 | AC-014 | G2 | installed asset simulation | command + inspection | `uvx --isolated --from <absolute-repo-path> spec-dock init <tmp>` and installed file/help checks |
| CLOS-010 | AC-016, AC-017 | G6 | reviewer / CI / PR repair loop and final evidence | reviewer + GitHub | fresh reviewers, PR URL, checks, repair disposition |

## 3. 実装ステップ

### S01: Planning adoption / readiness

目的:

- Issue draft artifactsとChatGPT Use analysisを採否判断し、canonical requirement / design / plan / reportを正式化する。
- assurance classify / compose / verifyを通し、fresh `spec-reviewer`で実装可能な状態にする。

Verification:

```bash
./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json
./spec-dock/scripts/spec-dock assurance verify --format json
./spec-dock/scripts/spec-dock guidance issue-execution
```

Reviewer:

- `spec-reviewer` required before S02.

Closes:

- Planning precondition for CLOS-001〜CLOS-010.

### S02: Closure Index Gate

目的:

- C01〜C11のcompletion evidence、deferred PR delivery rationale、dependency closure、blocking gapを確認する。

Commands / inspection:

```bash
./spec-dock/scripts/spec-dock deps check iss-00307
./spec-dock/scripts/spec-dock validate
rg -n "deferred PR|PR delivery|iss-00307|no-per-Issue-PR|merge-prepared" spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues
```

Report evidence:

- `report.md` Closure Index Gate table.
- Any gap becomes Repair Queue entry.

Closes:

- CLOS-001.

### S03: Branch / main sync gate

目的:

- final PR readiness前にbranchが`main`に対してbehind / divergedしていないことを確認し、必要なら安全に取り込んでfull gateを再実行する。

Commands:

```bash
git fetch origin
git rev-list --left-right --count origin/main...HEAD
git status --short --branch
```

If behind / diverged:

```bash
git merge origin/main
```

After merge:

- rerun S02〜S09. Main取り込み後はClosure Index Gateも含めて再確認し、C01〜C11 completion / dependency closure / blocking gap evidenceが最新mainに対して有効であることを確認してからPR readinessへ進む。

Closes:

- CLOS-003.

### S04: Runtime / backend / local wrapper gate

目的:

- `authoring` command helpとbackend command contractを確認する。
- local wrapper hard-codeが正式shipped surfaceにないことを確認する。

Commands:

```bash
./spec-dock/scripts/spec-dock authoring --help
./spec-dock/scripts/spec-dock authoring preflight github-sync --help
./spec-dock/scripts/spec-dock authoring pack prepare --help
./spec-dock/scripts/spec-dock authoring backend invoke --help
./spec-dock/scripts/spec-dock authoring pack review --help
./spec-dock/scripts/spec-dock authoring pack stage --help
./spec-dock/scripts/spec-dock authoring validate initiative-epic-candidates --help
./spec-dock/scripts/spec-dock authoring validate epic-issue-candidates --help
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption --help
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill --help
./spec-dock/scripts/spec-dock authoring approval check --help
rg -n "/Users/|\\.codex/skills/chatgpt-use/scripts/oracle-chatgpt|oracle-chatgpt" src/spec_dock/assets spec-dock/docs spec-dock/scripts .agents/skills
```

Backend verification:

- unset backend blocks.
- CLI `--backend-command` dry-run overrides env.
- `SPECDOCK_CHATGPT_COMMAND` precedes `ORACLE_CHATGPT_COMMAND`.

Preferred automated evidence:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -k "backend_invoke"
```

Closes:

- CLOS-004, CLOS-005.

### S05: Evidence safety and validator gate

目的:

- GitHub sync preflight、`local-context`、ZIP review/stage、candidate validators、draft adoption validator、approval checkのpositive / negative evidenceを確認する。

Commands:

```bash
uv run pytest tests/cli_runtime/test_authoring.py
```

Additional manual smoke may be used for:

- `authoring preflight github-sync --evidence-mode local-context`
- `authoring pack review` unsafe ZIP fixture
- `authoring approval check` missing approval fixture

Closes:

- CLOS-006, CLOS-007, CLOS-008.

### S06: Installed asset simulation gate

目的:

- provider-side assetsがconsumer repoに導入されることを確認する。

Commands:

```bash
tmp="$(mktemp -d)"
repo_root="$(pwd)"
uvx --isolated --from "$repo_root" spec-dock init "$tmp"
test -f "$tmp/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md"
test -f "$tmp/.agents/skills/spec-dock-initiative-planning/SKILL.md"
test -f "$tmp/.agents/skills/spec-dock-epic-planning/SKILL.md"
test -f "$tmp/.agents/skills/spec-dock-issue-planning/SKILL.md"
test -f "$tmp/spec-dock/docs/workflow_chatgpt_authoring_pack.md"
test -f "$tmp/spec-dock/scripts/spec_dock_runtime/commands/authoring.py"
(cd "$tmp" && ./spec-dock/scripts/spec-dock authoring --help)
```

Automated companion:

```bash
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/unit/infra/test_init_update.py -k "spec-dock-chatgpt-authoring or install_root"
```

Closes:

- CLOS-009.

### S07: Full validation gate

目的:

- final repair前のfull local baselineを確認する。

Commands:

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
uv run pytest tests/cli_runtime/test_authoring.py
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/cli_runtime
```

If time or environment prevents the broader suite:

- Record exact reason.
- Run the narrower suite that covers all changed surfaces.
- Let reviewer decide whether residual risk is acceptable.

Closes:

- CLOS-002, CLOS-004〜CLOS-009.

### S08: Final reviewer gate

目的:

- Epic-wide diffとevidenceをfresh reviewersに確認させる。

Required reviewers:

- `spec-reviewer`: requirement/design/plan/report、Epic closure、authority boundary、docs/skills/runtime consistency。
- `code-reviewer`: runtime / tests / scaffold / docs diffの構造と回帰リスク。
- `qa-reviewer`: test matrix、manual scenario、CI/PR observation十分性。

Finding handling:

- P1以上は修正してfresh re-review。
- P2/P3はblocking判断をreportに記録し、必要なら修正または明示defer。

Closes:

- CLOS-010 pre-PR review portion.

### S09: PR delivery / merge preparation gate

目的:

- Epic単位で1つのmergeable PRを作成し、PR observation / repair loopを通す。

Steps:

1. Ensure branch is clean.
2. Push branch.
3. Create or update PR to `main`.
4. Record PR URL, head SHA, base branch, check status.
5. Observe CI / reviews.
6. Repair blocking CI/reviewer/PR findings.
7. Re-run affected checks and fresh reviewers if needed.
8. Record merge-prepared evidence in `report.md`.

Closes:

- CLOS-010.

## 4. Repair Queue policy

Any failure creates a `report.md` Repair Queue entry:

| ID | Gate | Finding | Severity | Blocking | Owner | Repair action | Re-run command | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|

Completion requires no unresolved blocking entries.

## 5. Deferred items allowed at completion

The following may remain deferred if docs/runtime/tests do not expose them as implemented and report records them as non-blocking:

- `authoring adopt`
- `authoring create-issues-from-zip`
- `authoring mark-reviewer-pass`
- `authoring set-authorized-profile`
- `authoring issue-execution-ready`
- `authoring pr-ready`
- automatic GitHub Issue creation from ChatGPT candidates
- automatic `.assurance.json` mutation from ChatGPT recommendation
- generic external AI provider registry beyond configurable backend command
- raw ZIP durable repository storage contract
- old workspace in-place migration guarantee
