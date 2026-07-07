# Runtime promotion criteria draft

## Non-decision statement

この文書は runtime promotion を承認しません。`scripts/authoring-pack/` の dogfood-only helper を、将来 runtime / formal workflow へ昇格するか、保留するか、却下するかを判断するための基準案です。

## Scope

- 対象: ChatGPT authoring pack dogfood workflow の検証結果。
- 非対象: `src/spec_dock/**` の runtime shipping、正式 workflow adoption、PR delivery、backend command adapter 実装。

## Promote criteria

Promote を検討できるのは、少なくとも次を満たした場合です。

- Scenario A candidate-only pack validation が pass している。
- Scenario B selected-profile fill validation が pass している。
- Scenario C stale / mismatch / unsafe-claim negative probes が fail-closed である。
- `canonical_written=false`、`assurance_mutated=false`、`reviewer_pass_claimed=false` が確認されている。
- ChatGPT profile suggestion が advisory-only に留まっている。
- authoring-pack manual suite、`git diff --check`、`spec-dock validate` が pass している。
- dogfood workflow docs、prompt contract、EAL examples、manual fallback notes がある。
- backend command adapter / invocation contract が個人環境固有 wrapper path に依存せず検証済みである。
- manual fallback が documentation だけでなく、少なくとも代表的な unavailable path で実地確認されている。
- fresh reviewer gates が pass している。

## Defer criteria

次のいずれかが残る場合は、formal runtime promotion を保留します。

- human edit burden が未計測。
- manual fallback success rate が未計測。
- reviewer repair loop の横断集計定義が未固定。
- backend command adapter / invocation contract が `iss-00293` に残っている。
- dogfood sample が単一 Epic に偏っている。
- runtime user experience / operational cost が未評価。

現時点の推奨 stance は `defer formal runtime promotion` です。

## Reject criteria

次のいずれかが発生した場合は、runtime promotion を却下または再設計します。

- ChatGPT output が reviewer pass、canonical adoption、`.assurance.json` mutation、runtime availability を主張する。
- stale / mismatch / unsafe-claim negative probe が adoption eligible になる。
- generated ZIP または staged artifact が canonical docs を直接上書きする。
- `authorized_profile` が ChatGPT output で変更される。
- shipped runtime path が scope amendment と fresh reviewer gate なしに変更される。
- raw transcript、host-local absolute path、secret-looking content が durable evidence に残る。

## Evidence matrix

| criterion | evidence | current result | implication |
|---|---|---|---|
| Scenario A pass | `iss-00288` report | pass | positive |
| Scenario B pass | `iss-00289` report | pass | positive |
| Scenario C fail-closed | `iss-00290` report | pass | positive |
| docs readiness | `iss-00291` report | pass | positive |
| backend adapter readiness | Epic plan / `iss-00293` docs | deferred | defer |
| manual fallback exercised | current repo evidence | unmeasured | defer |
| human edit burden | current repo evidence | unmeasured | defer |

## Re-evaluation trigger

- `iss-00293` final quality gate passes.
- backend command adapter is verified.
- manual fallback unavailable path is exercised.
- reviewer repair loop and human edit burden are measured or explicitly waived by a reviewed follow-up.
