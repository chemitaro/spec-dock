---
種別: 要件定義書（Issue）
ID: "iss-00303"
タイトル: "Issue Draft Adoption Validation"
関連GitHub: ["#303"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00303 Issue Draft Adoption Validation — Issue 要件定義

## 1. 目的

この Issue は、ChatGPT authoring pack から得た Issue draft requirement / design / plan と selected skeleton fill を、canonical Issue docs へ採用する前に検証する installed runtime gate を実装する。

実装対象は次の 2 command である。

- `./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption`
- `./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill`

これらの command は検証結果と diagnostics を返すだけであり、canonical docs を書き換えない。`.assurance.json` を作成・更新しない。fresh reviewer pass、execution-ready、PR-ready、canonical adoption を主張しない。

## 2. 背景

`iss-00302` では、Initiative/Epic candidates と Epic/Issue candidates を candidate-only evidence として検証する gate を実装した。`iss-00303` はその次の gate であり、Issue node が存在した後に使う。

`validate epic-issue-candidates` は Issue 作成前の候補を扱う。一方、`validate issue-draft-adoption` と `validate selected-skeleton-fill` は、既に存在する Issue node に対して、draft pack と selected skeleton fill が canonical rewrite の input として安全かどうかを確認する。

## 3. 親スコープから継承する境界

- Parent Initiative: `init-local-00003`
- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- ChatGPT output は正本ではなく evidence として扱う。
- `authority: evidence_only` を維持する。
- `adoption_status: unreviewed` を runtime validation success と混同しない。
- runtime command は canonical docs を直接上書きしない。
- runtime command は `.assurance.json` を mutate しない。
- validator pass は reviewer pass / execution-ready / PR-ready / canonical adoption を意味しない。

## 4. Scope

### 4.1 In scope

- `authoring validate issue-draft-adoption` の CLI / application / domain / presentation contract を実装する。
- `authoring validate selected-skeleton-fill` の CLI / application / domain / presentation contract を実装する。
- provider-side installed runtime source under the `src/spec_dock/assets/spec_dock/scripts` tree を更新する。
- dogfood mirror under the `spec-dock/scripts` runtime tree を provider-side source と一致させる。
- compatibility wrapper を追加する。
  - `validate_issue_draft_adoption.py`
  - `validate_selected_skeleton_fill.py`
- focused CLI runtime tests in `tests/cli_runtime/test_authoring.py`
- safe positive / negative fixtures for both validators.
- validator report output under safe non-canonical output targets.
- text / JSON output that distinguishes validation pass from adoption / reviewer pass.

### 4.2 Out of scope

- `authoring adopt`
- automatic canonical docs rewrite
- automatic Issue creation
- automatic `.assurance.json` mutation
- automatic `authorized_profile` decision
- fresh reviewer pass issuance
- execution-ready marking
- PR-ready / merge-ready / PR delivery
- GitHub Issue close / PR creation
- broad `--force` bypass
- per-Issue PR delivery for this intermediate Issue

### 4.3 Unchanged

- `authoring pack review` remains responsible for ZIP/tree safety review.
- `authoring pack stage` remains responsible for staging evidence and dry-run diff, not canonical write.
- `validate initiative-epic-candidates` and `validate epic-issue-candidates` remain candidate-only validators.
- `.assurance.json` remains local assurance state owned by the assurance workflow, not by ChatGPT output.

## 5. Required Behavior

### BH-001: issue draft adoption positive validation

Given:

- review report status is `pass`
- target Issue node exists
- expected Issue ID and parent Epic match
- draft requirement/design/plan files exist and are safe
- draft pack digest matches review/stage evidence
- canonical target mapping is limited to Issue `requirement.md`, `design.md`, `plan.md`, and report evidence notes
- authority fields remain evidence-only
- `.assurance.json` is observation-only
- forbidden authority claims are absent

When:

- user runs `authoring validate issue-draft-adoption`

Then:

- command returns `status=pass`
- output includes draft pack digest, parent trace, canonical target mapping, EAL disposition requirement, and authority boundary fields
- output does not claim canonical adoption, reviewer pass, execution-ready, or PR-ready

### BH-002: issue draft adoption rejects authority violations

Given an adoption input or draft content claims one of canonical adoption, canonical docs written, `.assurance.json` mutation, `authorized_profile` decision, reviewer pass, execution-ready, PR-ready, merge-ready, or PR delivery, the command returns `status=rejected`, records findings, and does not write canonical docs or `.assurance.json`.

### BH-003: selected skeleton fill positive validation

Given selected skeleton evidence exists, `.assurance.json` exists and is read as observation, selected profile matches authorized profile observation, template hash matches selected skeleton, and `section-fills.json` covers required sections exactly, `authoring validate selected-skeleton-fill` returns `status=pass`.

### BH-004: selected skeleton fill detects stale or inconsistent evidence

Selected profile mismatch, authorized profile observation mismatch, template hash mismatch, or selected skeleton hash mismatch returns `status=stale`.

### BH-005: missing or malformed required input is fail-closed

Missing review report, Issue node, adoption input, selected skeleton, `.assurance.json`, or section fill JSON returns `blocked` when it is a missing prerequisite. Malformed schema, missing required schema fields, duplicate section, missing draft, or malformed inventory returns `fail`.

## 6. Status Taxonomy

| status | 用途 |
|---|---|
| `pass` | command-local validation passed. Canonical adoption / reviewer pass ではない。 |
| `fail` | JSON schema failure, missing required field, malformed inventory, duplicate section, missing required draft. |
| `blocked` | required observation unavailable: review report missing, Issue node missing, `.assurance.json` missing, selected skeleton missing, unsupported review status. |
| `stale` | source hash / review digest / draft pack digest / selected profile / template hash / skeleton hash / parent trace mismatch. |
| `rejected` | unsafe path, secret/raw transcript, forbidden authority claim, `.assurance.json` mutation request, canonical write claim, unsafe report path. |
| `unreviewed` | artifact adoption state。command status として success 扱いしない。 |

## 7. Acceptance Criteria

- AC-001: `authoring validate issue-draft-adoption --help` exposes real arguments and no longer says `Deferred`.
- AC-002: `authoring validate selected-skeleton-fill --help` exposes real arguments and no longer says `Deferred`.
- AC-003: issue draft adoption positive fixture returns `status=pass` with authority boundary fields.
- AC-004: selected skeleton fill positive fixture returns `status=pass` with selected profile, template hash, section inventory, and authority boundary fields.
- AC-005: non-pass review report status maps to `blocked`, `stale`, `rejected`, or `fail` as appropriate.
- AC-006: missing Issue node is `blocked`; Issue ID / parent Epic / parent Initiative mismatch is `stale`; validator never creates an Issue node.
- AC-007: expected draft pack digest, source manifest hash, or review digest mismatch returns `stale`. Review digest is supplied by `--expected-review-digest` and compared with the digest computed from `--review-report`.
- AC-008: canonical target mapping is constrained to `requirement.md`, `design.md`, `plan.md`, and report evidence notes. `.assurance.json`, path traversal, absolute path, host-local path, hidden path, and secret-looking paths are `rejected`.
- AC-009: selected skeleton inventory detects missing, extra, duplicate, and empty sections.
- AC-010: selected profile, authorized profile observation, template hash, and selected skeleton hash mismatch return `stale`.
- AC-011: forbidden authority claims are `rejected` and findings do not leak raw secret values or raw transcript content.
- AC-012: `--report-path` under canonical Issue docs, `.assurance.json`, or symlinked paths are rejected; safe report paths under `.specdock-authoring` are allowed.
- AC-013: provider and dogfood runtime paths both expose the implemented behavior.
- AC-014: this intermediate Issue does not create a per-Issue PR and defers PR delivery to `iss-00307`.

## 8. Non-Functional Requirements

- Validation is deterministic.
- Output is machine-readable JSON and reviewer-readable text.
- Diagnostics are stable enough for tests.
- The same input produces the same status / findings.
- Secret-looking payloads, raw transcripts, host-local paths, and credentials are not persisted in reports.
- Runtime command does not write canonical docs.
- Runtime command does not mutate `.assurance.json`.

## 9. Grade

Authorized profile: `standard`

Manual risk note: this Issue touches installed runtime CLI behavior, JSON output contract, `.assurance.json` observation boundary, and forbidden authority claims. Treat the implementation with strict-style test coverage even though the active assurance profile is Standard.

## 10. Dependencies

- `epic-00295` requirement/design/plan authority boundary.
- `iss-00302` candidate validator concepts and test style.
- Existing pack review/stage contract.
- Existing authoring command parser/registry.
- Existing `.assurance.json` observation contract.

## 11. 確定した入力契約

- `authoring validate issue-draft-adoption` は `--input PATH` を必須にする。固定 default path は初期実装では採用しない。
- `--review-report PATH` は必須にする。
- `--expected-review-digest TEXT` は optional にし、指定時は `--review-report` から計算した digest と比較する。
- `--expected-source-manifest-hash TEXT` は optional にし、指定時は adoption input または source manifest observation と比較する。
- `--issue-dir PATH` は必須にする。active issue auto-detection は初期実装に含めない。
- `authoring validate selected-skeleton-fill` は `--input PATH`, `--issue-dir PATH`, `--assurance PATH`, `--selected-skeleton PATH` を必須にする。
- `--adoption-input` alias は初期実装では追加しない。互換 alias が必要になった場合は follow-up とする。

## 12. Open Questions / Uncertainty

- Validator should validate report evidence note targets but must not write `report.md`.
- ChatGPT connector could not open the current branch and inspected default branch fallback. Local attached context is used as supplementary evidence, not GitHub-verified branch evidence.
