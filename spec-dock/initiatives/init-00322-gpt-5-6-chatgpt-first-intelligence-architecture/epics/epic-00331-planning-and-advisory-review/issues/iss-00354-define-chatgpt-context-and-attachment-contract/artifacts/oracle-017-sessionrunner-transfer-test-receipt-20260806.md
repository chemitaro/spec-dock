# Oracle 0.17.0 sessionRunner / remote transfer test receipt

- Oracle source HEAD: `9fb87d9326ab1c07216f1eb904917013df6d9270`
- Oracle package version: `0.17.0`
- Command: `pnpm exec vitest run tests/cli/sessionRunner.test.ts tests/remote/server.test.ts --reporter=dot`
- Result: `2` test files passed, `42` tests passed

## What the tests establish

- `tests/cli/sessionRunner.test.ts` verifies that a browser result containing normal runtime, warnings, and artifacts is propagated to the final session update in the mocked session store.
- `tests/remote/server.test.ts` verifies completed artifact transfer and remote transfer warning behavior, including the `remote-artifact-transfer-failed` warning path.

## What the tests do not establish

The combined test run does not provide a producer-integrated local session `meta.json` fixture that persists either of the following closed states:

- artifact transfer `ready` or `streaming` as a local pending state
- artifact transfer `failed` or an equivalent persisted local warning for a failed transfer

The remote event and warning assertions therefore remain separate transport evidence. They are not promoted to the SpecDock recovery taxonomy and do not unblock S10.
