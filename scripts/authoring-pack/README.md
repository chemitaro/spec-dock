# ChatGPT authoring pack preparation

This directory contains dogfood-only helpers for preparing and reviewing evidence-only prompt packs for ChatGPT Use.

The helpers in this directory are not SpecDock runtime commands and are not shipped under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.

## Scope

- Observe repository ref, source hashes, and local assurance state before prompting ChatGPT.
- Generate a prompt pack only when preflight status is `pass`.
- Review a returned ChatGPT ZIP or an already isolated tree before any local adoption work.
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
