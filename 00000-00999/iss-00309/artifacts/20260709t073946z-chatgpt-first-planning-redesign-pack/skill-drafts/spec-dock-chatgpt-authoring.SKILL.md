---
name: spec-dock-chatgpt-authoring
description: Compose ChatGPT-first planning requests for SpecDock and review generated artifacts before adoption.
---

# spec-dock-chatgpt-authoring

## Purpose

Use this skill as the shared ChatGPT-first evidence lane for SpecDock planning.

It prepares prompt/context packets for ChatGPT GPT-5.5 Pro Extended, receives ZIP/tree style planning artifacts, and helps the calling planning skill review whether those artifacts are adoptable.

This skill is evidence-only. It does not own canonical adoption, reviewer gates, assurance state, execution readiness, PR readiness, Issue finish, or Epic completion.

## Default Route

The default route is ChatGPT-first:

1. Confirm repository and branch context.
2. Confirm GitHub sync or explicitly mark a lower-authority local-context run.
3. Collect operator intent and development background.
4. Compose the required artifact list.
5. Compose the input context.
6. Ask ChatGPT to generate artifacts or return `information_insufficient`.
7. Review the output before adoption.

## Fallback Route

Do not automatically switch to manual planning.

Manual fallback is allowed only when:

- ChatGPT, browser automation, backend command, or provider state is hard or unrecoverably unavailable; and
- the human explicitly approves manual fallback.

Tab saturation, timeout, slow response, transient browser failure, and validation rejection require wait/retry/recover first.

## ChatGPT Request Contract

Every request should include:

- repository;
- branch;
- target type;
- target identifier;
- GitHub sync state;
- operator intent;
- development background;
- planning objective;
- required artifacts;
- input context;
- input context type when relevant;
- information insufficient policy;
- output format expectations.

## Prompt Principles

- Tell ChatGPT what must be produced, not how to internally reason.
- Do not pass token-saving manual workflow complexity as the main instruction.
- Keep grade and quality-gate choices as planning considerations, not hard-coded local branching.
- Preserve human intent in free-form fields.
- Prefer ZIP/tree output when many files are required.

## Information Insufficient Policy

If the input cannot support formal planning, ChatGPT must return:

```yaml
status: information_insufficient
missing_information:
  - ...
questions:
  - ...
```

Do not fabricate requirement/design/plan artifacts in this state.

## Adoption Review

Before writing canonical files, check:

- all required artifacts exist;
- artifacts are internally consistent;
- forbidden authority claims are absent;
- manual fallback is not treated as automatic;
- Issue Planning does not introduce separate workflow modes for different input sources;
- `information_insufficient` is respected when present.

## Prohibited

- Claiming reviewer pass.
- Mutating `.assurance.json`.
- Marking execution-ready or merge-ready.
- Finishing Issue/Epic lifecycle.
- Creating PR delivery claims.
