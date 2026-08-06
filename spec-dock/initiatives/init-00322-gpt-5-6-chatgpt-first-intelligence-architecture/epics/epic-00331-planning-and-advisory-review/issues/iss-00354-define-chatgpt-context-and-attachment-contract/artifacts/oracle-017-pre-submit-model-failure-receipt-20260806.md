# S10 Oracle 0.17.0 pre-submit evidence receipt

- Oracle source HEAD: `9fb87d9326ab1c07216f1eb904917013df6d9270`
- Oracle package version: `0.17.0`
- Execution: direct browser CLI, managed Oracle Chrome profile, explicit accepted model alias `gpt-5.4`
- Scenario: model picker cannot resolve `Thinking 5.4`; the prompt is not submitted
- Prompt submission outcome: `promptSubmitted=false`
- Session terminal status: `error`
- Error category: `browser-automation`
- Error stage: `execute-browser`
- Error classification observed by Oracle: model selection failure (available labels did not include the requested model)
- Artifact inventory in terminal `meta.json`: absent
- Warning inventory in terminal `meta.json`: absent

## Sanitized source evidence

The terminal Oracle `meta.json` contained the following non-sensitive shape:

```json
{
  "status": "error",
  "mode": "browser",
  "browser": {
    "runtime": {
      "promptSubmitted": false
    }
  },
  "error": {
    "category": "browser-automation",
    "details": {"stage": "execute-browser"}
  }
}
```

The receipt intentionally omits the session handle, browser target identifiers, local profile path, URL, prompt text, and timestamps.

## Remote transfer source test

Oracle source test command:

```text
pnpm exec vitest run tests/remote/server.test.ts --reporter=dot
```

Result: `1` test file passed, `5` tests passed.

The source test suite proves that the remote descriptor can carry `transferStatus=ready` and that client-side transfer failures produce the warning code `remote-artifact-transfer-failed`. It does not prove that these states are persisted into local browser session `meta.json`.

## Interpretation

- This is an Oracle-produced positive fixture for the pre-submit `false` branch.
- A normal completed browser run separately produced `promptSubmitted=true` and a local transcript artifact with `transfer.status=not-needed`.
- No local producer for `artifact transfer.status=ready` or `failed` was observed in the session metadata path; the remote test evidence remains separate from local persistence.
- S10 can now characterize the model-selection pre-submit false branch. The artifact-pending and transfer-failed persistence gap remains unresolved.
