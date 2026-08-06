# Oracle 0.17.0 local session metadata transfer-failure receipt

- Oracle source HEAD: `9fb87d9326ab1c07216f1eb904917013df6d9270`
- Oracle package version: `0.17.0`
- Exercise: temporary local harness invoking the native `createRemoteBrowserExecutor` and `performSessionRun` path with a fake bridge that emits an `artifact-ready` event and then fails the artifact HTTP transfer
- Input and transport details are intentionally omitted; the harness used only redacted prompt and local temporary storage

## Sanitized terminal result

```json
{
  "sessionStatus": "completed",
  "browserWarnings": [],
  "artifactTransferStatuses": ["not-needed"]
}
```

## Interpretation

- The remote client reaches its transfer-failure handler, but the browser session runner does not carry the resulting `BrowserRunResult.warnings` into its returned browser execution result.
- The final local session metadata therefore contains neither the `remote-artifact-transfer-failed` warning nor an artifact with transfer status `failed`.
- This is a producer-integrated negative receipt for the S10 transfer-failed persistence gap. It does not justify a SpecDock-side inferred mapping or a production implementation without an upstream Oracle producer change or another exact persisted discriminator.
