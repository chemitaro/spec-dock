# Script design reference

## Purpose

Define a thin script/orchestration design for ChatGPT-first planning.

## Responsibilities

- Validate target arguments.
- Check GitHub sync or accept explicit lower-authority local-context mode.
- Resolve repository and branch.
- Collect operator intent and development background.
- Gather target artifacts and parent context.
- Build required artifact list.
- Build ChatGPT prompt/context.
- Invoke configured backend command.
- Store returned ZIP/tree output.
- Run adoption-review checks.

## Non-responsibilities

- Do not implement a local planning engine.
- Do not encode the old token-saving workflow as script branches.
- Do not auto-fallback to manual planning.
- Do not mark reviewer pass or execution readiness.

## CLI Shape

```text
spec-dock chatgpt plan --target initiative|epic|issue --id <id> \
  --operator-intent <file-or-text> \
  --development-background <file-or-text> \
  [--input-context-type requirement-heavy|draft-heavy|context-heavy] \
  [--local-context]
```

## Backend Command

The backend command must be configurable through environment, config, or CLI argument. Personal absolute paths must not be hard-coded.

If no backend command is configured, fail with a clear diagnostic.

## Sync Policy

Default is GitHub-synced mode. If local and remote differ, stop unless the user explicitly selects lower-authority local-context mode.

## Adoption Review

The script should validate:

- required files exist;
- no forbidden authority claims appear;
- Issue Planning has no separate workflow-mode language for different input sources;
- `information_insufficient` is handled as a valid stop;
- final quality Issue policy appears in Epic Planning outputs when required.
