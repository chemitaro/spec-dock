# 補助アーティファクト: Oracle 0.17.0 Failure Classification and Recovery Table

> **non-canonical / Red Team レビュー対象外**  
> `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` の実装者向けcross-reference。review対象四文書が優先する。

## 1. Source baseline correction

Current source HEAD `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` is stage-blind: nonzero/timeout or nonterminal session state can invoke
`_recover_same_session` without decoding submission evidence, and the generic adapter constructs
`oracle session <session-id> --harvest --no-recover` directly. Target implementation removes that command construction from
generic code and delegates version-specific harvest/capture argv exclusively to the selected compatibility profile.

## 2. Observed external evidence

| Observation | Provenance | What it proves | What it does not prove |
|---|---|---|---|
| reconstruction mismatch across direct/inline/none | external local wrapper run | failure can occur before submission and is not obviously attachment-specific | direct SpecDock adapter root cause |
| standard/project both failed | external local wrapper run | target variation alone did not recover those runs | target URL is irrelevant in all states |
| select/current both failed | external local wrapper run | strategy variation alone did not recover those runs | model selection implementation is correct |
| `promptSubmitted=false` | external local wrapper receipt | no ChatGPT response/ZIP was generated in those runs | exact direct Oracle metadata field |
| short smoke verified `GPT-5.6 Sol` | external local wrapper run | one model selection success occurred | stable mapping for logical Pro |
| `Available: Got it.` then retry success | external local wrapper run | one transient-looking failure occurred | root cause or generally safe retry rule |

## 3. Internal classes and authoritative public mapping

| Internal failure class | Public status | Public reason | Contract status |
|---|---|---|---|
| executable / managed Chrome unavailable | `blocked` | `oracle_unavailable` | existing reason retained |
| `profile_unsupported` / required capability missing / `prompt_submitted=unknown` / required profile builder missing | `blocked` | `oracle_capability_unsupported` | existing reason retained; allowed many-to-one capability family |
| `model_selection_unavailable` after the permitted retry is unavailable or exhausted | `blocked` | `oracle_model_selection_unavailable` | new public reason |
| `attachment_submission_failed` after the permitted inline path is unavailable or exhausted | `blocked` | `oracle_attachment_submission_failed` | new public reason |
| `prompt_reconstruction_mismatch` | `blocked` | `oracle_prompt_reconstruction_mismatch` | new public reason |
| `generation_incomplete` after one characterized same-session harvest | `blocked` | `oracle_generation_incomplete` | new public reason |
| characterized recovery command cannot be executed safely, or same-session state remains undecidable for infrastructure reasons | `blocked` | `oracle_session_recovery_required` | existing reason retained; not a known-stage catch-all |
| `output_download_failed` after one characterized same-session capture | `blocked` | `oracle_output_download_failed` | new public reason |
| expected artifact absent after terminal capture | `rejected` | `oracle_artifact_missing` | existing reason retained |
| multiple candidate artifacts | `rejected` | `oracle_artifact_ambiguous` | existing reason retained |
| path / mode / size / SHA / validation / ZIP / JSON defect | `rejected` | `oracle_artifact_rejected` | existing reason retained; allowed many-to-one validation family |

The mapping is closed and authoritative. The five stage-specific classes—model selection, attachment submission,
prompt reconstruction, generation, and output download—must not be collapsed into one another, into
`oracle_capability_unsupported`, or into `oracle_session_recovery_required`. Many-to-one normalization is allowed only for the
three explicitly listed same-semantics families: capability/profile validation, runtime unavailability, and artifact validation.
An unknown internal failure class has no default public mapping and must fail the mapper contract before serialization.

## 4. Recovery algorithm

```text
if profile/preflight invalid:
    BLOCK oracle_capability_unsupported
elif prompt_submitted is not true:
    # false or unknown: no same-session command is legal
    harvest_calls = 0
    capture_calls = 0
    if prompt_submitted is unknown:
        BLOCK oracle_capability_unsupported
    elif reconstruction mismatch:
        BLOCK oracle_prompt_reconstruction_mismatch
    elif retryable model failure and new_execution_budget == 1:
        NEW_EXECUTION_SAME_MODEL
    elif direct attachment failure and profile.inline_mode_characterized and budget == 1:
        NEW_EXECUTION_INLINE
    else:
        BLOCK with the exact model/attachment stage reason
else:
    if response not completed:
        run profile.harvest_argv_builder(session_id) once
        if still known generation-incomplete:
            BLOCK oracle_generation_incomplete
    elif artifact pending/download-failed:
        run profile.capture_argv_builder(session_id) once
        if still known download-failed:
            BLOCK oracle_output_download_failed
    elif artifact valid:
        ACCEPT
    else:
        REJECT with exact oracle_artifact_* reason
```

A builder missing from an otherwise selected profile is a capability defect. A builder that exists but cannot be safely executed,
or leaves session state undecidable for infrastructure reasons, maps to `blocked` / `oracle_session_recovery_required`.

## 5. Attempt budget examples

### Model retry success

```text
Attempt 1: model unavailable, submitted=false -> new execution, budget 0; harvest/capture 0
Attempt 2: verified -> submitted=true -> profile recovery if needed -> artifact -> accept
```

### Direct to inline

```text
Attempt 1: direct attachment failure, submitted=false -> inline new execution, budget 0; harvest/capture 0
Attempt 2: inline prepared -> submitted=true -> profile recovery if needed
```

### Reconstruction mismatch

```text
Attempt 1: mismatch, submitted=false -> block; retry/harvest/capture 0
```

### Submission unknown

```text
Attempt 1: submission evidence unknown -> capability unsupported; retry/harvest/capture 0
```

### Download failure

```text
Attempt 1: submitted=true -> response=true -> download failed
Same session: profile capture command once -> valid ZIP, oracle_output_download_failed, or oracle_artifact_* reject
```

## 6. Invocation-level mandatory assertions

- all failure classes × `prompt_submitted=False|None` -> harvest builder 0, capture builder 0。
- post-submit generation -> profile harvest exact argv 1, generic hardcoded argv 0。
- post-submit download -> profile capture exact argv 1, generic hardcoded argv 0。
- total automatic new executions <= 1; total successful submissions <= 1。
- unknown internal public-mapping input is rejected; no generic default reason。
