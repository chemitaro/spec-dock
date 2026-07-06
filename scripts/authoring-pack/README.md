# ChatGPT authoring pack preparation

This directory contains dogfood-only helpers for preparing evidence-only prompt packs for ChatGPT Use.

The helpers in this directory are not SpecDock runtime commands and are not shipped under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.

## Scope

- Observe repository ref, source hashes, and local assurance state.
- Generate a prompt pack only when preflight status is `pass`.
- Keep ChatGPT output as `authority: evidence_only`.
- Keep `authorized_profile` controlled by local assurance, not ChatGPT.

## Non-scope

- ZIP intake or extraction.
- Canonical document overwrite.
- Reviewer pass claims.
- Pull Request creation.
- Tracked workspaces or fixtures under `manual-tests/`.

## Example

```bash
python scripts/authoring-pack/prepare_chatgpt_authoring_pack.py \
  --config tests/fixtures/authoring_pack/valid/iss-00284-preflight-input.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00284-prompt-pack
```
