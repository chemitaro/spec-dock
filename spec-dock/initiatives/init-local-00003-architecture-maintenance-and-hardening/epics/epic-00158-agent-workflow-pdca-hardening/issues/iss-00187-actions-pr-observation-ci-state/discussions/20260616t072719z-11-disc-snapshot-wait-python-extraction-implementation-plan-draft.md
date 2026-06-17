---
種別: discussion
ID: "20260616t072719z-11"
タイトル: "PR observation snapshot/wait Python extraction implementation plan draft"
状態: "draft"
作成日: "2026-06-16"
作成者: "implementation-planner draft via orchestrator"
対象Issue: "iss-00187"
created_by_role: "implementation-planner"
scope_id: "iss-00187"
source_paths:
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
  - "spec-dock/active/issue/discussions/20260616t072719z-10-disc-snapshot-wait-python-extraction-architecture-draft.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh"
intended_targets:
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "passed by orchestrator diff review against current canonical docs"
adoption_ledger_note: "Adoption authority is recorded in report.md EAL-031, Spec Authoring Gate S300+ addendum, Delegated Draft Evidence, and D-015."
---

# PR observation snapshot/wait Python extraction implementation plan draft

## 位置づけ

このドラフトは、`iss-00187` の追加 follow-up として、既存 S200+ lane の末尾に S300+ を追記するための実装計画案である。

対象は、provider-side PR observation assets のうち、まだ大きな Python heredoc を残している次の 2 つに限定する。

- `fetch_pr_observation_snapshot.sh`
- `wait_pr_observation.sh`

目的は、公開 shell command contract を維持したまま、非自明な Python logic を standalone Python module/script へ抽出し、wrapper を fixed CLI / validation / adjacent entrypoint invocation に戻すこと。

このドラフトは S201-S204 の完了や正しさを裏書きしない。canonical `plan.md` へ統合する場合は、既存 S200+ の末尾に S300+ として追記し、S200+ の既存 closure evidence を上書きしない。

## 推奨ステップ

1. S300: characterization / current heredoc inventory
2. S310: `fetch_pr_observation_snapshot.sh` extraction
3. S320: `wait_pr_observation.sh` extraction
4. S390: provider/mirror/docs/scaffold sync
5. S399: final QA / PR observation gate

```text
S300
  -> S310
      -> S320
          -> S390
              -> S399
```

S310 は wait が呼び出す snapshot wrapper の contract を先に安定させるため、S320 より先に行う。

## 追加テスト契約

| Test ID | Step | Contract |
|---|---|---|
| `tc-s300-001` | S300 | heredoc inventory and behavior-test mapping recorded |
| `tc-s300-002` | S300 | existing snapshot/wait focused tests identified |
| `tc-s310-001` | S310 | snapshot public CLI and fixed `gh` call preserved |
| `tc-s310-002` | S310 | invalid snapshot inputs rejected before `gh` |
| `tc-s310-003` | S310 | snapshot out artifacts remain compatible |
| `tc-s310-004` | S310 | head revalidation / stale head behavior preserved |
| `tc-s310-005` | S310 | collector failures produce JSON with redacted stderr hash |
| `tc-s310-006` | S310/S390 | `pr_observation_snapshot.py` ships by init/update |
| `tc-s320-001` | S320 | wait public CLI validation preserved |
| `tc-s320-002` | S320 | wait stdout/stderr/progress/out contract preserved |
| `tc-s320-003` | S320 | quiet and same-fingerprint gate preserved |
| `tc-s320-004` | S320 | timeout preserves latest payload |
| `tc-s320-005` | S320 | S204 `review_completion_unknown` timing preserved |
| `tc-s320-006` | S320 | late submitted/unresolved review overrides unknown candidate |
| `tc-s320-007` | S320/S390 | `pr_observation_wait.py` ships by init/update |
| `tc-s390-001` | S390 | provider/mirror changed files match |
| `tc-s390-002` | S390 | docs describe standalone snapshot/wait Python entrypoints |
| `tc-s399-001` | S399 | final focused/broad validation and PR latest-head evidence complete |

## S300 - Characterization / current heredoc inventory

### Behavior goal

現在残っている heredoc と既存テスト契約を棚卸しし、S310/S320 が behavior-preserving extraction であることを検証できる状態にする。

### Target files

- `fetch_pr_observation_snapshot.sh`
- `wait_pr_observation.sh`
- `pr_observation_checks.py`
- `tests/unit/infra/test_init_update.py`

### Delegated role

- `dev-coder` for characterization evidence only

### Forbidden changes

- implementation behavior change 禁止
- S201-S204 完了の追認・再判定をこの step で行わない

### Red / alternative evidence

- extraction 専用 module asset tests は現時点では absent でよい
- behavior preservation は existing green characterization を採用可

### Green verification

```sh
rg -n "python3 - <<|'PY'|PY$" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
```

Focused existing snapshot/wait tests mapping を report に記録する。

### Review / commit gate

- code-reviewer inspect-only pass
- characterization-only commit は任意。canonical plan が要求しない場合は no-op evidence とする

## S310 - Extract `fetch_pr_observation_snapshot.sh`

### Behavior goal

`fetch_pr_observation_snapshot.sh` の payload-building heredoc と metadata JSON parsing heredoc を `scripts/lib/pr_observation_snapshot.py` へ移し、shell wrapper は argument validation と adjacent Python entrypoint 呼び出しに限定する。

### Target files

- provider `fetch_pr_observation_snapshot.sh`
- provider `scripts/lib/pr_observation_snapshot.py`
- `tests/unit/infra/test_init_update.py`

### Delegated role

- `dev-coder`

### Forbidden changes

- snapshot classification behavior の変更禁止
- checks/review collector semantics の変更禁止
- public flags / stdout JSON / stderr diagnostics / out artifact names の変更禁止
- new dependency 禁止

### Red / alternative evidence

- `pr_observation_snapshot.py` asset presence test should fail or be absent before extraction
- existing snapshot behavior tests are characterization evidence if already green before extraction

### Green verification

- focused snapshot tests
- invalid input rejects before `gh`
- stale head / final head revalidation tests
- collection failure JSON and secret redaction tests
- `git diff --check`

### Review / commit gate

- code-reviewer pass focused on shell/Python boundary, temp/out artifact compatibility, fixed API surface, secret redaction
- S310 commit only after reviewer pass and clean check

## S320 - Extract `wait_pr_observation.sh`

### Behavior goal

`wait_pr_observation.sh` の poll loop、snapshot invocation orchestration、quiet/same-fingerprint stability、zero-check grace、review-completion timing、progress rendering、out artifact handling を `scripts/lib/pr_observation_wait.py` へ移す。

### Target files

- provider `wait_pr_observation.sh`
- provider `scripts/lib/pr_observation_wait.py`
- `tests/unit/infra/test_init_update.py`

### Delegated role

- `dev-coder`

### Forbidden changes

- S204 timing constants / semantics の変更禁止
- `review_completion_unknown` を pass / merge-ready にしない
- trigger script semantics の変更禁止
- snapshot script public contract の変更禁止

### Red / alternative evidence

- `pr_observation_wait.py` asset presence test should fail or be absent before extraction
- existing wait tests are before/after characterization evidence

### Green verification

- wait stdout/stderr/out contract
- quiet / same fingerprint behavior
- timeout keeps latest payload
- S204 review-completion timing tests
- late review feedback overrides unknown candidate
- `git diff --check`

### Review / commit gate

- code-reviewer pass focused on polling semantics, timeout handling, progress line budget, non-pass safety
- S320 commit only after reviewer pass and focused tests

## S390 - Mirror / docs / scaffold sync

### Behavior goal

provider extraction files、dogfooding mirror、operator docs、init/update scaffold output を整合させる。

### Target files

- provider/mirror `SKILL.md`
- mirror `fetch_pr_observation_snapshot.sh`
- mirror `wait_pr_observation.sh`
- mirror `scripts/lib/pr_observation_snapshot.py`
- mirror `scripts/lib/pr_observation_wait.py`
- focused asset tests

### Delegated roles

- `doc-writer` for docs
- `dev-coder` or `utility-worker` for mechanical mirror/scaffold verification

### Forbidden changes

- behavior change 禁止
- S310/S320 implementation logic の docs step 内修正禁止

### Green verification

- provider/mirror `cmp -s`
- init/update asset presence tests
- `git diff --check`

### Review / commit gate

- spec-reviewer for docs
- code-reviewer for mirror/scaffold sync
- S390 commit after both reviewer gates pass

## S399 - Final QA / PR observation gate

### Behavior goal

S300+ lane 全体を quality gate で閉じ、doc-only final commit 後に PR latest head/check/mergeability を再確認する。

### Delegated roles

- `qa-reviewer`
- `code-reviewer`
- `spec-reviewer`

### Required checks

```sh
uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_snapshot or pr_observation_wait or review_completion_unknown or issue_187"
uv run pytest tests/unit/infra/test_init_update.py -q
git diff --check
./spec-dock/scripts/spec-dock validate
```

Provider/mirror comparisons are also required for changed assets.

### PR evidence

- final docs/report-only commit 後、PR latest head SHA、checks、mergeability、PR observation result を再確認する
- stale pre-final PR observation は final evidence として使わない
- `review_completion_unknown` が出る場合は non-pass human gate として報告し、GitHub mergeability/check state と区別する

### Commit gate

- final evidence commit only after reviewers pass
- uncommitted S310/S320 behavior changes を S399 に混ぜない

## 順序制約と stop conditions

- If extraction requires changing public shell flags, stop for design amendment.
- If new Python files are not shipped by current install/update asset machinery, stop and fix scaffold asset inclusion before continuing.
- If S310 or S320 reveals behavior differences in existing tests, treat as extraction regression unless explicitly accepted by code-reviewer.
- If `fetch_pr_review_snapshot.sh` changes become necessary to preserve snapshot behavior, stop and split a separate follow-up or amend scope.
- Any reviewer `fail` blocks commit for that step until bounded follow-up and fresh pass.

## Direct target / follow-up target

Direct target:

- `fetch_pr_observation_snapshot.sh`
- `wait_pr_observation.sh`

Follow-up target:

- `fetch_pr_review_snapshot.sh`
- `trigger_codex_review.sh`

理由:

- `fetch_pr_review_snapshot.sh` は review lifecycle collector であり、current-boundary semantics の blast radius が大きい。
- `trigger_codex_review.sh` は review initiation であり、observation snapshot/wait aggregation とは責務が異なる。
- すべてを一括で抽出すると、PR observation 自体を final evidence として使いにくくなる。

## canonical `plan.md` への採用案

採用する場合は、既存 S299 の末尾に S300+ として追記する。

- S300: heredoc inventory / characterization
- S310: snapshot extraction
- S320: wait extraction
- S390: docs/mirror/scaffold sync
- S399: final QA / PR observation gate

既存 S200+ の実施済み step を書き換えない。

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed by this draft.
