# 補助アーティファクト: 実装対応表・Oracle 0.17 Test Matrix

> **implementation aid / non-canonical / Red Team レビュー対象外**  
> `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` のcross-reference。review対象四文書が優先する。

## 1. Module-by-module delta

| Module | Keep | Existing #354 change | Oracle 0.17 addition |
|---|---|---|---|
| `application/issue_planning_prompt.py` | typed identity/output | minimal body + path tuple | prompt corpus/digest contract |
| `application/issue_planning.py` | lifecycle/pre-postflight | path assembly/thread policy | recovery decision integration / attempt budget |
| `domain/issue_planning_contracts.py` | Candidate/Review/Human/result | operation/thread types | stage/failure/recovery content-free types |
| `infra/issue_planning_chatgpt.py` | PATH Oracle/managed Chrome/env/one submit/stage-blind hardcoded harvest | remove prompt pack/direct paths/generic recovery argv | profile registry/stage decoder/direct-inline bounded loop/profile-owned harvest-capture builders |
| `infra/issue_planning_oracle_artifact.py` | strict bounded snapshot | output safety unchanged | 0.16/0.17 version-dispatched readers |
| `commands/issue_planning.py` | command family | context manifest hard cutover | no retry override flags |
| resources | authority/output meaning | per-operation prompt/attachments | 0.17 failure/recovery operator guidance |
| docs/skills | exact source/direct Oracle/Human gate | Option A/C/Blue-Red | profile/stage/withdrawal guidance |

## 2. Profile tests

| Test | Expected |
|---|---|
| exact `0.16.1` | existing profile accepted |
| exact `0.17.0` before registration | submission 0 / unsupported |
| exact `0.17.0` with complete profile | help/schema checks then invoke |
| `0.17.1` / `0.18.0` unknown | fail-closed |
| missing required root/session flag | fail-closed |
| executable identity changes after preflight | prompt submission 0 |
| Oracle config file contains model | explicit profile model argv wins; config not deleted |
| temporary HOME isolation attempted | test failure |

## 3. Prompt exactness tests

```python
@pytest.mark.parametrize("case", PROMPT_CASES)
def test_prompt_is_one_exact_argv_operand(case, fake_oracle):
    outcome = invoke(case.text)
    assert fake_oracle.prompt_calls == [case.text]
    assert fake_oracle.shell is False
    assert outcome.private_evidence[0].prompt_sha256 == sha256(case.text.encode("utf-8"))
```

Cases:

- ASCII short control。
- Japanese / Unicode / combining characters。
- quotes / backticks / `$()` literal。
- Markdown fences / JSON snippets。
- trailing newline true / false。
- representative Issue #354 brief。

No test should assert ChatGPT answer text as prompt reconstruction proof. Browser receiptのsubmission / mismatch stageを使用する。

## 4. Recovery decision table

| # | Model | Attach | Reconstruct | Submitted | Response | Artifact | Budget | Action | Harvest/Capture |
|---:|---|---|---|---|---|---|---:|---|---|
| 1 | unknown | n/a | n/a | unknown | n/a | n/a | 1 | capability block | `0/0` |
| 2 | transient fail | n/a | n/a | false | false | none | 1 | new execution same model | `0/0` |
| 3 | transient fail | n/a | n/a | false | false | none | 0 | block model reason | `0/0` |
| 4 | verified | direct fail | n/a | false | false | none | 1 | new execution inline | `0/0` |
| 5 | verified | direct fail | n/a | false | false | none | 0 | block attachment reason | `0/0` |
| 6 | verified | prepared | mismatch | false | false | none | 1 | block reconstruction reason | `0/0` |
| 7 | verified | prepared | ok | true | false | none | any | profile harvest | `1/0` max |
| 8 | verified | prepared | ok | true | true | pending | any | profile capture | `0/1` max |
| 9 | verified | prepared | ok | true | true | invalid | any | reject exact artifact reason | additional `0/0` |
| 10 | verified | prepared | ok | true | true | snapshotted | any | accept | `0/0` |

Invariant tests:

- all internal classes with submitted=false or unknown call both builders zero times。
- action 2 or 4 consumes the only automatic new-execution token。
- after any `Submitted=true`, actions 2/4 cannot be constructed。
- action 6 never chooses inline/model retry。
- successful submission count <= 1。
- total Oracle executions <= 2。

## 5. No-prewalk / original path proof

Monkeypatch/spy:

```python
def fail_tree_access(*_args, **_kwargs):
    raise AssertionError("attachment directory must remain opaque")

for name in ("rglob", "iterdir", "read_bytes", "read_text", "stat", "resolve"):
    monkeypatch.setattr(Path, name, fail_tree_access)
```

`Path.__fspath__` / string conversionに必要なoperationを過剰patchしない。direct / inline argv bothでtop-level path stringが同じであることを
assertする。FIFOは作成だけしopenしない。

## 6. Stage decoder fixtures

Sanitized fixture set:

| Fixture | Stage/evidence |
|---|---|
| `017-model-unavailable.json` | model unverified, submitted=false |
| `017-attachment-direct-failed.json` | model verified, direct failed, submitted=false |
| `017-reconstruction-mismatch.json` | mismatch, submitted=false |
| `017-submitted-running.json` | submitted=true, response=false |
| `017-response-download-pending.json` | response=true, artifact pending |
| `017-completed-authoring-zip.json` | artifact downloaded/validated |
| `017-completed-review-json.json` | review payload available |
| `017-schema-unknown.json` | decoder must reject |

Fixture names are proposed test assets, not claims about actual Oracle filename/field names. S09 must generate them fromactual sanitized observations.

## 7. Model tests

- logical `pro` -> profile-specific exact argv。
- `model_verified=false|unknown` cannot produce pass。
- non-empty observed label required。
- observed label binds tosame execution as submission。
- external observation `GPT-5.6 Sol` may appear in evidence test data, not generic model enum。
- retry retains identical logical selector / strategy。
- `current` / default / alternate model invocation count 0。

## 8. Direct / inline tests

- direct primary for static directory + dynamic Candidate/Review paths。
- direct classified failure + submitted=false + budget -> inline exactly once。
- inline uses same prompt digest and same ordered path tuple。
- no file read/copy/archive/temp input pack。
- inline not selected for mismatch/model/download/artifact error。
- formal operation never removes required paths。
- no third attempt after inline failure。

## 9. Same-session tests

- characterization proves current stage-blind behavior calls `_recover_same_session` without submission evidence。
- migration removes generic literal `session` / `--harvest` / `--no-recover` argv assembly。
- 0.16.1 profile builder returns the former exact command; 0.17 builders return characterized fixture commands only。
- every failure class with submitted=false or unknown -> harvest builder 0 / capture builder 0; no cleanup exception。
- submitted=true + response=false -> selected profile harvest exact argv once; prompt command exactly once。
- submitted=true + response=true + artifact pending -> selected profile capture exact argv once。
- missing builder -> capability unsupported before same-session command invocation。
- executable identity must still match for profile recovery command。
- invalid session metadata -> exact artifact/session result; no new execution。

## 10. Artifact reader and public mapping tests

Retain:

- contained session root / no symlink traversal。
- bounded metadata/artifact bytes。
- size + SHA verification。
- one expected ZIP / one Review payload。
- ZIP path/compression/entry limits。
- strict JSON duplicate/unknown/non-finite rejection。

Add:

- exact profile/reader/version/recovery-builder binding。
- 0.17 pending/downloadfailed/completed state decoding。
- cross-version fixture rejection。
- response complete but download remains failed after profile capture -> `blocked/oracle_output_download_failed`。
- profile command cannot execute safely -> `blocked/oracle_session_recovery_required`。
- terminal capture but no expected file -> `rejected/oracle_artifact_missing`。
- exact status/reason assertion for every REQ-030 row。
- five new reasons accepted; existing reasons retained。
- many-to-one accepted only for capability/profile、runtime unavailable、artifact validation families。
- unknown internal class rejected before public serialization。

## 11. Browser smoke matrix

| Run | Prompt | Target kind | Attachment | Expected evidence |
|---|---|---|---|---|
| B-01 | short control | standard | none diagnostic | browser/model/reconstruct/submit/response |
| B-02 | short control | project | none diagnostic | same, target category only |
| B-03 | representative | standard | required direct | full through artifact capture |
| B-04 | representative | project | required direct | full through artifact capture |
| B-05 | representative | selected target | inline diagnostic only if classified direct failure | one recovery max |
| B-06 | authoring output | accepted target | required direct | logical filename/root/SHA/ZIP validation |

External wrapper results can pre-populate a hypothesis ledger but cannot mark B-01–B-06 pass。

## 12. Privacy assertions

Search serialized public result / report summary for absence of:

- raw prompt substring。
- external personal wrapper absolute path。
- Oracle home / session directory。
- raw target URL / project identifier。
- browser endpoint。
- provider handle / transcript。
- attachment filenames where content-free reason does not require them。

Allowed content-free values:

- profile ID/version。
- stage enum / failure class。
- logical model / observed label / verified bool。
- target kind category。
- attachment mode。
- counts / digest / byte length。
- retry count。

## 13. Authoritative mapping reference

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

## 14. Focused commands

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py -q
uv run pytest tests/unit/application/test_issue_planning.py -q
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
uv run pytest tests/unit/infra -k 'oracle and (profile or session or artifact or download)' -q
uv run pytest tests/unit/commands/test_issue_planning.py -q
uv run pytest tests/cli_runtime/test_chatgpt_cli.py -q
uv run pytest tests/integration/test_issue_planning_e2e.py -q
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate
git diff --check
```

## 15. Stop matrix

| Condition | Action |
|---|---|
| exact branch/HEAD mismatch | stop; no default branch |
| 0.17 version/help/schema incomplete | block profile |
| submission evidence unknown | block profile |
| model verification unavailable | block profile |
| representative reconstruction mismatch | stop / investigate; no auto retry |
| inline requires materialization/drop | disable inline / stop |
| post-submit needs new execution | stop / redesign |
| output validator regression | stop |
| provider projection mismatch | stop before review |
| private evidence leak | stop / repair |
| P0/P1 review finding | repair + fresh review |
