# S09 Oracle 0.17.0 native characterization rerun receipt

## Scope

これは `iss-00354` の S09 で、PATH Oracle 0.17.0 のブラウザ実行、ZIP成果物のメタデータ、同一セッションの harvest を再観測した sanitized receipt である。個人設定や raw transcript は含めず、仕様採用・実装完了・レビューPASS・S09 closureそのものの証跡とは分離して扱う。

## Sanitized observation

| 項目 | 観測結果 |
|---|---|
| Oracle version | `0.17.0` |
| engine | `browser` |
| requested model | `gpt-5.6` |
| observed model | `GPT-5.6 Sol` |
| model strategy | `select` |
| model verified | `true` |
| prompt submitted | `true` |
| response | `response-complete=true` |
| artifact kind | `zip` |
| logical filename | `oracle-017-characterization.zip` |
| internal root | `oracle-017-characterization` |
| artifact size | `427` bytes |
| artifact SHA-256 | `58dd6373901a1ce4cf3dd0e3bd642d91d3fb27be19407c3f0354fcb8cd43bc4b` |
| ZIP validation | `type=zip`, `ok=true` |
| ZIP entries | `oracle-017-characterization/MANIFEST.md`, `oracle-017-characterization/payload.txt` |
| manifest observation | `oracle-version=0.17.0`, `response-complete=true`, `artifact-kind=zip`, `attachment-mode=none` |
| payload observation | `characterization-ok` |
| same-session harvest | `oracle session <id> --harvest --no-recover` を実行し、同じ応答本文と同一成果物 identity を再取得 |
| characterization status | `supported_with_gap` |

## Sanitized invocation and metadata shape

The successful rerun used the following option contract. Values that identify a local session, prompt, or filesystem location are redacted while option names and observed operands are preserved.

```text
oracle
  --engine browser
  --model gpt-5.6
  --browser-model-strategy select
  --browser-attachments never
  --timeout 120m
  --http-timeout 120m
  --slug <session-id>
  --prompt <exact-prompt>
  --write-output <output-path>
```

The observed session metadata had this sanitized core shape:

```json
{
  "id": "<session-id>",
  "status": "completed",
  "mode": "browser",
  "artifacts": [
    {
      "kind": "file",
      "path": "<session-root>/artifacts/oracle-017-characterization.zip",
      "sizeBytes": 427,
      "sha256": "58dd6373901a1ce4cf3dd0e3bd642d91d3fb27be19407c3f0354fcb8cd43bc4b",
      "validation": {"type": "zip", "ok": true},
      "transfer": {"status": "not-needed"},
      "origin": {"mode": "local"}
    }
  ]
}
```

The browser runtime receipt separately recorded `promptSubmitted=true` and model selection `{requestedModel: "GPT-5.6 Sol", resolvedLabel: "GPT-5.6 Sol", strategy: "select", verified: true}`. The added `transfer` and `origin` fields are recorded only to establish their presence; the reader must not use them as path or validation authority.

## Profile boundary

- 0.17.0 の root help、session help、モデル選択、prompt submission、completed response、ZIP成果物の logical filename / internal root / size / SHA / ZIP structure、同一セッション harvest を同一観測系列で確認した。
- 成果物の実体は Oracle の session artifact inventory に保存され、ZIP validation と SHA-256 が一致した。新規の capture option を推測せず、観測済みの同一セッション harvest を harvest/capture recovery の境界として扱う。
- `--browser-attachments always` の追加観測は、送信前の model selector UI failure および rate-limit UI failure で終了し、attachment transport の成功証跡には昇格しない。既存の EAL-008 にある 0.17.0 の directory / multiple-path attachment capability evidence と区別して保持する。
- 0.16.1 の profile と既存 reader は変更せず、0.17.0 の profile/reader を実装する際は、この receipt と既存の 0.17.0 help/attachment evidence だけを根拠にする。未知の schema field、API fallback、個人設定の上書きは追加しない。

## Evidence source

- PATH Oracle native browser rerun: completed response and ZIP artifact inventory
- same-session harvest: one successful `--harvest --no-recover` execution
- model evidence: browser model-selection receipt (`GPT-5.6 Sol`, `select`, `verified=true`)
- attachment follow-up failures: pre-submit observations only; not adopted as successful transport evidence
