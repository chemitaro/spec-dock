# S09 Oracle 0.17.0 inline attachment characterization receipt

## Scope

これは `iss-00354` の S09 で、Oracle 0.17.0 の text attachment inline transport を、既存の ZIP artifact identity と分離して観測した sanitized receipt である。モデル選択の成功証跡ではなく、inline attachment capability、completed status、成果物 inventory の観測だけを記録する。

## Sanitized observation

| 項目 | 観測結果 |
|---|---|
| Oracle version | `0.17.0` |
| engine | `browser` |
| attachment option | `--browser-attachments never`（inline-compatible text attachment） |
| requested model | `gpt-5.6` |
| model strategy | `current` |
| model selection evidence | `verified=false`（このrunのモデル証跡へ昇格しない） |
| prompt submitted | `true` |
| response | `response-complete=true` |
| artifact kind | `zip` |
| logical filename | `oracle-017-attachment-characterization.zip` |
| internal root | `oracle-017-attachment-characterization` |
| artifact size | `483` bytes |
| artifact SHA-256 | `9566748c79c49e5369d36fff3c76d2cb65250dc281fdaca563c5c0be3bd827a2` |
| ZIP validation | `type=zip`, `ok=true` |
| ZIP entries | `oracle-017-attachment-characterization/MANIFEST.md`, `oracle-017-attachment-characterization/payload.txt` |
| manifest observation | `oracle-version=0.17.0`, `response-complete=true`, `artifact-kind=zip`, `attachment-mode=native` |
| payload observation | `attachment-characterization-ok` |
| top-level status | `completed` |
| characterization status | `supported` for inline text delivery; model selection remains separate |

## Sanitized invocation contract

```text
oracle
  --engine browser
  --model gpt-5.6
  --browser-model-strategy current
  --browser-attachments never
  --file <inline-compatible-text-file>
  --slug <session-id>
  --prompt <exact-prompt>
  --write-output <output-path>
```

The completed session metadata used the same core fields as the direct ZIP receipt: `id`, `status`, `mode`, `artifacts[]`, and file artifact `kind`, `path`, `sizeBytes`, `sha256`, `validation.ok`. The artifact was saved by the browser-download path and validated as ZIP. No transcript, URL, absolute path, session handle, or attachment contents are included here.

## Profile binding boundary

- `inline_mode_characterized=true` for the observed text-file path only. This does not authorize inline fallback for a different file type or a failed `always` upload.
- The separate `--browser-attachments always` observations remain pre-submit UI failures and are not converted into success evidence.
- `oracle session <id> --harvest --no-recover` is the only observed same-session recovery command. The no-attachment and inline runs both produced a completed response and a validated ZIP; the profile may bind harvest and capture to this same builder as one recovery primitive, but no independent artifact-pending state was fabricated.
- The stage decoder may accept the exact top-level metadata `status=completed` and reject missing, non-string, or unknown values. `promptSubmitted` and model-selection evidence remain browser runtime receipts, not artifact status fields.
- The inline run's `current` strategy has `verified=false`; the verified `GPT-5.6 Sol` model evidence is retained only from the separate `select` run in `s09-oracle-017-native-rerun-20260806.md`.

## Evidence source

- PATH Oracle native browser inline run with one text attachment and completed ZIP output
- session metadata artifact inventory (`sizeBytes`, SHA-256, ZIP validation)
- separate direct 0.17.0 rerun receipt for verified model selection and same-session harvest
