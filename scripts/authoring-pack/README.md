# ChatGPT authoring pack preparation

This directory contains dogfood-only helpers for preparing and reviewing evidence-only prompt packs for ChatGPT Use.

The helpers in this directory are not SpecDock runtime commands and are not shipped under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.

## Scope

- Observe repository ref, source hashes, and local assurance state before prompting ChatGPT.
- Generate a prompt pack only when preflight status is `pass`.
- Review a returned ChatGPT ZIP or an already isolated tree before any local adoption work.
- Stage a passing reviewed tree into dry-run diffs, fixed-name staged artifacts, and unreviewed EAL candidates.
- Validate selected-profile skeleton section fills against local assurance and selected skeleton evidence.
- Validate candidate-only Epic-to-Issue output as issue candidates with advisory profile recommendations only.
- Keep ChatGPT output as `authority: evidence_only`.
- Keep `authorized_profile` controlled by local assurance, not ChatGPT.

## Non-scope

- Canonical document overwrite.
- Reviewer-gate completion claims.
- Pull Request creation.
- Tracked workspaces or fixtures under `manual-tests/`.

## Example

```bash
python scripts/authoring-pack/prepare_chatgpt_authoring_pack.py \
  --config tests/fixtures/authoring_pack/valid/iss-00284-preflight-input.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00284-prompt-pack
```

```bash
python scripts/authoring-pack/review_chatgpt_authoring_pack.py \
  --input /tmp/specdock-authoring-pack/result.zip \
  --preflight /tmp/specdock-authoring-pack/iss-00284-prompt-pack/preflight.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00285-review
```

```bash
python scripts/authoring-pack/stage_chatgpt_authoring_pack.py \
  --review-report /tmp/specdock-authoring-pack/iss-00285-review/validation-report.json \
  --pack-tree /tmp/specdock-authoring-pack/iss-00285-extract/specdock-authoring-pack \
  --issue-dir spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering \
  --output-dir /tmp/specdock-authoring-pack/iss-00286-stage
```

```bash
python scripts/authoring-pack/validate_selected_skeleton_fill.py \
  --review-report /tmp/specdock-authoring-pack/iss-00285-review/validation-report.json \
  --pack-tree /tmp/specdock-authoring-pack/iss-00287-extract/specdock-authoring-pack \
  --assurance spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00287-implement-profile-controlled-selected-skeleton-fill-validation/.assurance.json \
  --selected-skeleton /tmp/specdock-authoring-pack/iss-00287-selected-skeleton.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00287-selected-fill-validation
```

```bash
python scripts/authoring-pack/validate_issue_candidates.py \
  --review-report /tmp/specdock-authoring-pack/iss-00285-review/validation-report.json \
  --pack-tree /tmp/specdock-authoring-pack/iss-00288-extract/specdock-authoring-pack \
  --expected-parent-epic epic-00283 \
  --expected-requirement E-RQ-011 \
  --expected-acceptance E-AC-007 \
  --expected-acceptance E-AC-011 \
  --output-dir /tmp/specdock-authoring-pack/iss-00288-issue-candidates
```
