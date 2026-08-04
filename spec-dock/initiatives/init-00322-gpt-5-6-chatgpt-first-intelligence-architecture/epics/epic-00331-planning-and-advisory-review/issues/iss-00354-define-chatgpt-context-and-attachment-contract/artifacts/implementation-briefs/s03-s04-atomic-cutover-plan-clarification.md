# iss-00354 — S03/S04 atomic cutover plan clarification

| 項目                                             | 確認値                                                                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Repository                                     | `chemitaro/spec-dock`                                                                                                           |
| Branch                                         | `codex/iss-00354-chatgpt-context-contract`                                                                                      |
| Upstream                                       | `origin`                                                                                                                        |
| Verified source HEAD                           | `a2bc5e00cf7aefe049c234bfe0207f992077af8f`                                                                                      |
| GitHub comparison                              | branch tip と指定 HEAD は `identical` / ahead `0` / behind `0`                                                                      |
| Issue / parents                                | `iss-00354` / `epic-00331` / `init-00322`                                                                                       |
| 文書の効力                                          | read-only plan clarification。repository、正本文書、Candidate、report、code、tests を変更しない                                                 |
| Requested authoring model                      | `GPT-5.6 Luna` / Reasoning Effort `Max`                                                                                         |
| Measured model evidence for this clarification | thread 上の model identity は `GPT-5.6 Pro`。browser picker label、wrapper の target/resolved model、Reasoning Effort receipt は**未確認** |
| Model claim boundary                           | `Luna` / `Max` の実測成功を主張しない。後続 gate は wrapper が実際に記録した evidence を正とする                                                            |

この補正は approved requirement/design の「minimal body + original direct paths」「generated input pack の廃止」を変更しない。現行 `plan.md` の S03/S04 実行カードを、exact HEAD の producer/contract/consumer 依存関係に合わせて実行可能にするための最小補正である。

## Decision and rationale

### Decision

S03 と S04 は、**一つの deployable change-set、一つの exact-HEAD review target、一つの rollback unit として atomic cutover する**。

ただし、責務と closure evidence は統合しない。

* `cl-s03-path-input` は application 側の path-only contract、caller、source-preflight/transport-state 分離を所有する。
* `cl-s04-direct-transport` は infra 側の repeated direct `--file` operands、generated pack 廃止、transport regressions を所有する。
* canonical test ID は既存どおり `tc-s03-001` と `tc-s04-001` を保持する。
* Red は責務別に先行作成できるが、Green と closure は同一 resulting HEAD で同時に成立させる。
* 片方だけが Green の状態を implementation-ready、commit candidate、review-ready、closed と記録しない。
* compatibility property、dual-write、path-to-bytes 再構成、一時 pack、deprecated attachment payload は置かない。

この判断は新アーキテクチャではない。approved requirement の REQ-004〜007、approved design の path-only synthesized operation、および current plan の S03/S04 target を、現行コードの実依存に合わせて一つの変更境界へ束ねるだけである。

### Rationale

exact HEAD では、旧入力契約は三層にまたがっている。

1. `application/issue_planning_prompt.py` が `PlanningPromptAttachment.content`、`SynthesizedPlanningPrompt.attachments`、`.exact_attachments` を定義し、canonical/relevant source を読取り・decode・scan して materialized payload を生成する。
2. `application/issue_planning.py` が Review/Revision の Candidate、Review、canonical targets、onboarding、reviewed identity を bytes 化し、transport 前に attachment bytes を scan/hash 再照合する。
3. `infra/issue_planning_chatgpt.py` が `_write_transport_pack` で `context-NNN.md`、exact files、manifest、provenance、source-manifest、stale-if を生成し、Oracle へ一つの pack path だけを渡す。

したがって S03 の四ファイルだけで payload fields を消すと caller が壊れ、S04 の infra だけを先に変えると direct paths の producer が不足する。独立 Green を作るには、正本が禁止する compatibility bridge が必要になる。atomic cutover なら、application producer、synthesized contract、infra consumer を同時に hard cutover できる。

### Atomicity invariants

1. **No partial closure:** `cl-s03-path-input` と `cl-s04-direct-transport` は同じ implementation HEAD でのみ close する。
2. **No runtime bridge:** old payload fields と new path fieldsを同時に受理する production API を作らない。
3. **No hidden fallback:** generated pack、copy、ZIP、inline transport、attachment drop、alternate backend を rollback/fallback として残さない。
4. **One prompt remains:** prompt は一つの `str`、Oracle argv は一つの `--prompt`、`shell=False` を維持する。
5. **Original paths remain:** direct operand は caller が選択した incoming `Path` を順序どおり `str(path)` にしたものだけとする。
6. **Output path is unchanged:** Oracle session output の private staging、typed ZIP/JSON snapshot、Candidate/Review publication validationは変更しない。
7. **Later milestones remain later:** thread continuity は S06、profile/stage/recovery は S09〜S10、browser formal evidence は S11、artifact reader は S12 の責務のままとする。

### Source-preflight and attachment-transport boundary

次の二つを明示的に分離する。

| Boundary                      | 保持する責務                                                                                                               | S03/S04 で除去する責務                                                                                                              |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Source preflight / postflight | repository、branch、upstream、HEAD、source path set、source manifest、remote parity、postflight freshness、publication guard | なし。既存 exact GitHub gate を維持する                                                                                                |
| Attachment transport state    | operation resource directory と required dynamic original paths の順序付き tuple                                           | source hashes、decoded source text、attachment bytes、classification、source label、per-input digest、generated transport manifest |
| Lifecycle validation          | Candidate loader、Review parser/digest、revision request parser、typed identity equality、stale checks                   | validated objectから transport 用 bytes/file を再生成すること                                                                           |
| Public evidence               | content-free status/reason、typed output identity、source evidence                                                     | raw prompt、attachment content、private path、session/thread handle、transcript                                                  |

Source preflight が source files を既存手段で検証することと、attachment transport が path target を walk/open/hash しないことは矛盾しない。前者は exact source gate、後者は Oracle input transport である。S03/S04 では、prompt synthesis 後の `_attachments_match_source_manifest` による二重読取り・再hashを廃止する。preflight 後に source が変化した場合は、既存 postflight/publication guard が output を stale として不採用にする。snapshot、copy、pack を追加してその race を隠さない。

### Candidate, Review, revision request, and identity

* Candidate、Review JSON、revision request は、既存 lifecycle validator による typed validationを維持したうえで、transport には選択済みの original path を渡す。
* Candidate member を transport のために抽出しない。Candidate bytesを新しい fileへ書かない。
* Review の `ReviewedPlanningIdentity` は application が従来どおり構築・保持する。
* `reviewed-identity.json` と `reviewed-identity-sha256.txt` は生成しない。
* Reviewer への identity は、approved minimal body の identity category 内で、既存 `ReviewedPlanningIdentity.to_dict()` の canonical JSON shape と既存 `identity.sha256` を deterministic に描画する。これは新しい file formatでも attachment inline fallbackでもない。
* Review response は従来どおり closed JSON parser で読み、body に提示した typed identity と完全一致させる。
* Semantic Revision の selected findings と preserved assumptions は既存 revision-scope bodyに残し、Candidate、Review、revision request の本文を bodyへ埋め込まない。

## Amended S03/S04 scope table

### Step-boundary amendment

| Slice                | Canonical owner                          | Allowed behavior change                                                               | Required Red                                                           | Required Green                                                                  | Closure rule                              | Rollback / stop                                           |
| -------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| Plan authorization   | `plan.md` / `report.md`                  | S03/S04 を atomic execution boundary として承認し、union allowlist と same-HEAD closure を記録    | current blocked scope と canonical IDs の不一致を確認                          | amendment が fresh exact-HEAD gateを通り、EAL blockを後続実装へ引き渡せる                       | code変更前の prerequisite。S03/S04 closureではない | amendment未採用なら実装開始しない                                     |
| S03 contract         | `cl-s03-path-input` / `tc-s03-001`       | `SynthesizedPlanningPrompt` を path-only にし、application callers が original paths を構成する | payload fields、bytes producer、source rehash、path inspectionを検知する tests | application boundaryで prompt + ordered paths + output expectationだけを backendへ渡す | S04と同じ resulting HEADでのみ close            | path materialization、new identity file、S05変更が必要なら両方stop   |
| S04 transport        | `cl-s04-direct-transport` / `tc-s04-001` | infra が各 path を repeated `--file` operandとして渡し、input packを生成しない                       | one-pack argv、pack files、copy/ZIP/hash/tree accessを検知する tests          | exact argv、one prompt、no pack、existing output staging/regressions pass          | S03と同じ resulting HEADでのみ close            | direct multi-path契約が無効、またはpackが必要なら両方stop                 |
| Combined integration | 両 closure                                | application producerからinfra argvまで同一 path identity/orderを追跡する                         | current bytes→pack pathがRedになる                                         | Planning/Review/Revisionの代表 input が direct operandsになる                          | focused/static/full gateを同じ HEADで記録       | 片方のtest failureで両方pending                                 |
| Evidence handoff     | `report.md`                              | exact base/result HEAD、files、tests、no-bridge search、model evidenceを記録                 | stale alias・未解決EALを検知                                                  | two closure rowsが同一 HEADを参照し、S05 input contractを明記                              | fresh review後もHuman/owning workflowとは分離   | private evidence、未確認model claim、stale sourceなら記録をcloseしない |

### Responsibility split

| Concern                                       | `cl-s03-path-input`        | `cl-s04-direct-transport`                  |
| --------------------------------------------- | -------------------------- | ------------------------------------------ |
| Synthesized contract                          | Owns                       | Consumes only                              |
| Application caller assembly                   | Owns                       | Does not reinterpret                       |
| Source evidence separation                    | Owns                       | Receives separate `PlanningSourceEvidence` |
| Review/Revision original path selection       | Owns                       | Preserves exactly                          |
| Prompt body / typed identity rendering        | Owns                       | Passes exact prompt unchanged              |
| Oracle executable/capability/Chrome preflight | Regression only            | Owns existing behavior                     |
| Direct `--file` argv                          | Supplies ordered tuple     | Owns exact operand expansion               |
| Generated input pack removal                  | Requires no payload fields | Owns physical deletion                     |
| Output staging and typed snapshot             | No change                  | Regression owner                           |
| Retry/inline/profile/stage decoder            | Forbidden                  | Forbidden in this cutover                  |
| Application tests                             | Primary owner              | Integration consumer                       |
| Infra/integration tests                       | Contract fixture provider  | Primary owner                              |

### Operation-specific path assembly

Path order is part of the contract. No deduplication、sort、resolve、absolute化、expanduser、existence/type checkを direct path assemblerで行わない。

| Operation                | Ordered `attachment_paths`                                                                                                                                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Planning                 | provider-managed `planning/attachments/` directory; then preflight-selected canonical Issue paths; then relevant source paths; then already-authorized operator-supplied paths when that existing application surface supplies them                                       |
| Archive Candidate Review | provider-managed `review/attachments/` directory; then `request.candidate_path` exactly once                                                                                                                                                                              |
| Git-bound Review         | provider-managed `review/attachments/` directory; then the canonical target paths selected by the existing target resolver; then `request.candidate_path` exactly once. Candidate onboarding is consumed from the original Candidate, not extracted into a transport file |
| Semantic Revision        | provider-managed `revision/attachments/` directory; then `request.candidate_path`; then the exact Review path selected by existing `PlanningRevisionEvidenceInput` resolution; then `request.request_path`                                                                |
| Mechanical Revision      | no ChatGPT transport change; existing mechanical lane remains outside S03/S04 direct Oracle invocation                                                                                                                                                                    |

Repository-relative canonical paths stay lexical and are interpreted under the existing Oracle subprocess `cwd=repo_root`. External Candidate/Review/request paths remain the incoming `Path` objects selected by the existing request/evidence logic. The contract does not promise preservation of CLI token spelling that was already lost before construction of the incoming `Path`; S05 owns any CLI surface migration.

### Red / Green / closure state machine

```text
plan amendment adopted
  -> S03 Red + S04 Red confirmed
  -> one atomic implementation change-set
  -> combined focused tests Green
  -> static/repository gates Green
  -> exact resulting HEAD pushed and re-verified
  -> fresh read-only code review gate
  -> cl-s03-path-input and cl-s04-direct-transport close on that same HEAD
  -> S05 receives path-only application request / direct transport contract
```

At no point may `S03=closed, S04=pending` or `S04=closed, S03=pending` be recorded.

## Contract migration sequence

### 0. Pre-implementation authorization gate

Before production code changes:

1. Verify branch and HEAD against the implementation prompt. This brief is bound to `a2bc5e00cf7aefe049c234bfe0207f992077af8f`; a later branch tip requires a new comparison and delta review.
2. Adopt the minimal `plan.md` / `report.md` amendment described below.
3. Confirm S01 capability evidence and S02 closure evidence remain present and are not reopened.
4. Confirm no unrelated worktree changes are mixed into the atomic change-set.
5. Record requested model separately from measured wrapper/browser evidence. Missing Luna/Max evidence is `未確認`, not success.

### 1. Red — lock the target contract before production changes

Add failing tests first in the allowed test files.

`tc-s03-001` must fail because current code still exposes payload fields and reads/materializes attachment content. `tc-s04-001` must fail because current infra still produces one prompt-pack operand.

The Red state may be committed internally only if the branch is not represented as runnable, Green, review-ready, or mergeable. No Red-only or half-cutover commit may be deployed or merged.

### 2. Hard-cut the prompt contract

In `application/issue_planning_prompt.py`:

1. Replace the `synthesize_planning_evidence_prompt` payload-oriented signature with a path-oriented signature in one hard cut. Do not accept old and new arguments concurrently.
2. Make `SynthesizedPlanningPrompt` contain only:

   * `role`
   * `prompt`
   * `attachment_paths`
   * `output_expectation`
3. Make `attachment_paths` a required immutable tuple of `Path`.
4. Keep role/output expectation validation and existing source/operator body limits that govern body data.
5. Remove attachment-content size limits, source file readers, decoded source attachments, content classification, per-input SHA, and transport-specific manifests from prompt synthesis.
6. Keep managed operation resource validation scoped to known `prompt.md` and top-level `attachments/`; do not enumerate that directory.
7. Keep body sensitive scanning for identity/operator/revision strings. Do not scan attachment path names or attachment content.
8. Render existing typed reviewed identity and digest in the minimal body when role is Reviewer; do not add a file.

This is a compile-time/API hard cut inside the same implementation change-set, not a compatibility phase.

### 3. Cut over application callers

In `application/issue_planning.py`:

1. Remove the import and construction of `PlanningPromptAttachment`.
2. `run_issue_planning_transport` continues to create `PlanningSourceEvidence` and `PlanningContext`, but no longer scans or rehashes synthesized attachment payload.
3. Planning passes lexical canonical/relevant paths selected by preflight, plus the managed resource directory.
4. Archive Review passes the original Candidate path.
5. Git-bound Review passes canonical targets and the original Candidate path; it does not read canonical files or Candidate onboarding for transport materialization.
6. Semantic Revision passes the original Candidate, Review, and revision-request paths; it does not attach extracted Candidate documents.
7. Existing Candidate/Review/revision typed validation, stale re-load, postflight, and publication guards stay in place.
8. Existing captured `ReviewedPlanningIdentity` remains application-private and is used to verify the returned Review JSON.
9. Remove transport-only helpers and branches:

   * `_exact_attachments_have_sensitive_content`
   * attachment-content branch of `_attachments_match_source_manifest`, or the helper entirely if no non-transport caller remains
   * `_read_review_supplemental_attachments`
   * generated reviewed-identity byte helpers used only for attachment construction
   * materialization-only review byte limits/constants when no longer referenced
10. Do not alter Apply, mechanical revision, output publication, or public reason mapping.

### 4. Cut over the infra consumer

In `infra/issue_planning_chatgpt.py`:

1. Build Oracle argv from `synthesized.attachment_paths`.
2. Append exactly one `("--file", str(path))` pair per tuple element, preserving order and duplicates.
3. Preserve one `--prompt` operand and its exact string.
4. Preserve executable identity recheck, managed Chrome preflight, sanitized child environment, model selector, model strategy, session slug, timeout behavior, and current 0.16.1 recovery behavior.
5. Keep only output `staging`; remove input `pack`.
6. Delete `_write_transport_pack` and `_write_json` if no other caller remains.
7. Remove input-pack-only imports (`hashlib`, transport-manifest `json` usage, or other imports only when truly unused; JSON needed by Chrome preflight remains).
8. Do not add inline mode, retry loop, profile registry, stage decoder, capture builder, or 0.17 artifact reader here.

### 5. Delete legacy symbols in no-bridge order

The deletion order is logical and must be completed before the first Green commit:

1. Replace all application call sites that construct `PlanningPromptAttachment`.
2. Replace all application/test call sites that consume `.attachments` or `.exact_attachments`.
3. Replace the prompt synthesis function signatures with path-only inputs.
4. Replace infra one-pack argv with repeated direct operands.
5. Delete `_write_transport_pack` and its input-pack helpers.
6. Delete `SynthesizedPlanningPrompt.attachments`.
7. Delete `SynthesizedPlanningPrompt.exact_attachments`.
8. Delete `PlanningPromptAttachment`.
9. Delete remaining materialization-only constants, imports, helpers, and tests.
10. Run a repository search gate; production matches for the deleted symbols and generated pack names must be zero.

No step introduces an alias property, empty tuple default that masks a missing migration, deprecated wrapper, temporary file bridge, or path-content loader.

### 6. Combined Green

The first valid Green state is the state in which:

* application Planning/Review/Revision callers produce only ordered paths;
* infra consumes those paths directly;
* no generated input pack exists;
* typed lifecycle/output validation remains intact;
* focused tests for both closure IDs pass on the same worktree and commit candidate.

### 7. Refactor

Only after combined Green:

* remove dead imports/constants/helpers;
* simplify duplicated path assembly without changing order/identity;
* retain clear separation between source preflight and transport state;
* retain private/public evidence separation;
* run formatting/type/static checks;
* re-run focused tests after refactor.

### 8. Rollback

Rollback is a reviewed commit-level revert of the entire atomic change-set.

* Do not add a runtime feature flag for old pack behavior.
* Do not retain old fields for emergency fallback.
* Do not automatically downgrade Oracle or select another backend.
* A rollback may restore the prior commit’s implementation by reverting the whole change-set, but the reverted deployment is not evidence that S03/S04 are closed.
* Candidate, Review, S01/S02 evidence, and canonical design remain untouched by either cutover or rollback.

## Tests and closure evidence

### Canonical test contract — `tc-s03-001`

The S03 test family must prove all of the following.

| Test dimension   | Exact assertion                                                                                                                                                                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract shape   | `SynthesizedPlanningPrompt` has no `attachments`, `exact_attachments`, attachment `content`, `classification`, `source_label`, or per-input `sha256`                                                                                                          |
| Path type        | outer value is a tuple; each item is `Path`; invalid element types fail content-free before filesystem work                                                                                                                                                   |
| Identity/order   | incoming `Path` objects are retained in order; duplicate paths remain duplicated                                                                                                                                                                              |
| No normalization | `.resolve()`, `.absolute()`, `.expanduser()`, implicit dedup/sort are not called by the path assembler                                                                                                                                                        |
| Zero inspection  | nested、hidden、symlink、dangling symlink、FIFO、missing path all assemble with `open/read/read_bytes/read_text/iterdir/glob/rglob/stat/lstat/exists/is_file/is_dir/is_symlink/os.walk/os.scandir/copy/zip/hash` call count `0` at the transport assembly boundary |
| Planning caller  | managed directory + canonical/relevant paths reach synthesized operation in specified order                                                                                                                                                                   |
| Review caller    | original Candidate path reaches the synthesized operation; no Candidate bytes/member extraction is used for transport                                                                                                                                         |
| Revision caller  | original Candidate、selected Review、revision request paths reach the synthesized operation in specified order                                                                                                                                                  |
| Source boundary  | `PlanningSourceEvidence` remains separate; source hashes are not copied into the synthesized path contract                                                                                                                                                    |
| Review identity  | existing typed identity and digest are present in prompt body; no generated identity attachment is created                                                                                                                                                    |
| Privacy          | path text is absent from public result/error/report fixtures; raw content is absent from body except approved body fields                                                                                                                                     |
| Existing limits  | dependency/operator body limits remain; no new attachment count/size/path-length limit is invented                                                                                                                                                            |

A prior test that expected source mutation after preflight to be caught by rehashing synthesized bytes must be replaced. The new contract proves no second materialization; create/review/revision postflight tests must continue to reject stale publication.

### Canonical test contract — `tc-s04-001`

| Test dimension          | Exact assertion                                                                                                                                            |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Direct argv             | each `attachment_paths` item becomes one `--file`, `str(path)` pair, in exact tuple order                                                                  |
| One prompt              | `argv.count("--prompt") == 1`; prompt value byte/character semantics are unchanged                                                                         |
| No pack                 | no `prompt-pack` directory、`.specdock-authoring-pack`、`context-NNN.md`、`manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json` is created |
| No input transformation | tree/copy/archive/ZIP/hash/write calls for attachments are `0`                                                                                             |
| Missing/special path    | builder still emits the operand; Oracle owns transport-stage failure classification                                                                        |
| Environment             | `shell=False`, stdin disabled, managed Chrome, executable identity, safe environment remain unchanged                                                      |
| Model                   | existing logical selector/strategy remain unchanged; no `current` or alternate model fallback                                                              |
| Recovery                | current S01/0.16.1 recovery characterization remains unchanged; S03/S04 add no inline/retry/stage policy                                                   |
| Output                  | private output staging and typed authoring ZIP/Review JSON snapshot regressions pass                                                                       |
| Privacy                 | argv/path is not serialized into public result or committed evidence                                                                                       |

### Required focused commands

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  -q
```

Read-only regression for unchanged domain limits/contracts:

```bash
uv run pytest tests/unit/domain/test_issue_planning_contracts.py -q
```

S01/S02 regression subset:

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  -q
```

Static/repository gates:

```bash
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate .
git diff --check
```

Legacy-removal search gate:

```bash
rg -n \
  "PlanningPromptAttachment|exact_attachments|synthesized\.attachments|_write_transport_pack|context-[0-9]{3}\.md|source-manifest\.json|stale-if\.json" \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  tests
```

Expected result:

* production code: zero matches for all deleted contract/pack symbols;
* tests: only explicit negative assertions or historical fixture text may remain;
* no compatibility implementation match is permitted.

### Closure evidence

Both closure rows must record the same values for:

* base HEAD;
* resulting implementation HEAD;
* branch comparison;
* changed-file set;
* focused test command and result;
* static/repository gate result;
* legacy-removal search result;
* rollback unit;
* fresh review target;
* requested model;
* wrapper/browser measured model label and verification state;
* Reasoning Effort evidence or `未確認`.

`cl-s03-path-input` additionally records path spy counts、path order/object identity、caller matrix。
`cl-s04-direct-transport` additionally records exact argv、no-pack filesystem assertions、one-prompt and output regression results。

### Fresh ChatGPT review gate

After the complete change-set is pushed:

1. Re-verify repository、branch、exact pushed HEAD through GitHub.
2. Run one fresh, read-only code review covering both closure responsibilities and the union allowlist.
3. Request `GPT-5.6 Luna` / Reasoning Effort `Max`, but record only the wrapper/browser evidence actually returned.
4. When picker label、resolved model、verification flag、effort receipt are absent, record `未確認`; do not infer Luna/Max.
5. Review output alone does not adopt canonical documents、authorize implementation completion、merge、or close the Issue.
6. Any required production change outside the allowlist returns to plan amendment; it is not silently accepted as review repair.
7. After repair, use a new exact HEAD and a new fresh review gate.

### Minimal `plan.md` amendment

Only the following planning semantics need amendment:

1. Mark S03/S04 as one atomic execution boundary.
2. Replace the separate S03/S04 write allowlists with the union implementation allowlist in this brief.
3. Retain `cl-s03-path-input` / `tc-s03-001` and `cl-s04-direct-transport` / `tc-s04-001`.
4. State that both closures close on the same HEAD or neither closes.
5. Change migration order from separate S03 then S04 to atomic S03/S04, followed by S05.
6. Add the no-bridge rollback/stop conditions.
7. Do not change requirement、design、ADR、S05+ architecture.

### Minimal `report.md` amendment

1. Preserve all existing S01/S02 evidence and their historical review records.
2. Keep the current S03 blocked advisory as historical evidence; add a new adoption entry for the approved atomic-cutover amendment rather than rewriting the historical observation.
3. Update the S03/S04 delegation gate from blocked/pending to approved atomic scope only after plan amendment adoption.
4. Add one Closure Delta stating:

   * canonical S03 ID is `cl-s03-path-input`;
   * canonical S04 ID is `cl-s04-direct-transport`;
   * any pending `cl-s04-profile` label is a stale alias and must not be closed;
   * if historical S02 evidence uses `cl-s02-profile`, map it non-semantically to canonical `cl-s02-resources` without reopening or changing S02 evidence.
5. Add separate closure rows for S03 and S04, bound to the same implementation HEAD.
6. Record source/resulting HEAD、tests、search gate、fresh review gate、model evidence boundary.
7. Do not add raw prompt、path、session/thread identifier、transcript、or private browser evidence.

### S05 handoff contract

S05 receives:

* a path-only synthesized application contract;
* deterministic operation-specific original path ordering;
* a direct Oracle adapter with repeated `--file` operands;
* no generated input pack or legacy attachment payload API;
* unchanged typed output and exact source gates.

S05 still owns CLI/parser cutover, old `--context-manifest` removal, optional repeatable path options, and any raw CLI token semantics. S03/S04 must not pre-implement those changes.

## Stop conditions and unresolved risks

### Mandatory stop conditions

Stop before implementation, or keep both closures pending, when any condition below holds.

1. GitHub cannot re-verify the named branch and exact implementation base HEAD.
2. The plan/report atomic-scope amendment has not been adopted.
3. Worktree contains unrelated changes that cannot be isolated.
4. Current S01 evidence no longer supports required directory/multiple-path direct transport for the selected Oracle contract.
5. Any implementation requires reading, classifying, scanning, hashing, resolving, copying, renaming, extracting, archiving, or manifesting attachment content for transport.
6. Review identity cannot be conveyed through the already-approved minimal-body identity category without a generated file.
7. A new file schema、sidecar、transport pack、inline content fallback、attachment drop、or alternate backend is proposed.
8. Path-only application callers cannot be made Green without command/CLI changes owned by S05.
9. Direct transport cannot be made Green without profile/stage/recovery/artifact changes owned by S09〜S12.
10. Existing exact GitHub pre/postflight、Candidate/Review/Human binding、closed JSON parser、typed ZIP validator、publication transaction、privacy boundary must be weakened.
11. Tests pass only by retaining legacy payload fields or `_write_transport_pack`.
12. S03 and S04 cannot pass on the same resulting HEAD.
13. Provider source must be bypassed by directly editing installed/dogfood projections.
14. Fresh review requires an out-of-allowlist production repair.
15. Wrapper/browser evidence is insufficient but the report would otherwise claim Luna/Max success.

### Unresolved risks and classification

| Risk                                                                            | Current classification                                           | Required handling                                                                            |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Browser picker label and Reasoning Effort for this clarification                | **未確認**                                                          | Record `GPT-5.6 Pro` as the thread model identity and leave picker/effort fields unconfirmed |
| Representative direct PATH Oracle 0.17 browser success after code cutover       | **未確認 / S11**                                                    | Do not use S03/S04 unit Green as formal 0.17 compatibility PASS                              |
| Remote post-upload attachment failure stage                                     | **未確認 / S10**                                                    | No S03/S04 retry or inline workaround                                                        |
| Exact 0.17 stage/model/session schema                                           | **未確認 / S09〜S12**                                                | Keep current fail-closed version boundary; do not characterize by inference                  |
| Preflight-to-upload source mutation window                                      | accepted consequence of direct path design                       | Do not snapshot/materialize; rely on existing postflight/publication stale rejection         |
| CLI raw token spelling before `Path` construction                               | **未確認 / S05**                                                    | S03 preserves the incoming `Path` object, not unavailable pre-parse text                     |
| Oracle interpretation of lexical relative paths if subprocess cwd changes later | controlled invariant                                             | Keep `cwd=repo_root`; any proposed cwd change requires a new plan review                     |
| Stale closure labels in report                                                  | confirmed for pending S04 alias; historical S02 label may remain | Record Closure Delta; do not renumber or reopen completed evidence                           |
| Projection parity before S07                                                    | expected temporary provider-first state                          | Do not hand-edit projection; S07 owns regeneration/parity closure                            |

## Exact file allowlist and forbidden changes

### Phase A — plan authorization amendment

Write allowlist:

1. `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/plan.md`
2. `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md`

Allowed changes are limited to atomic scope、allowlist、closure coupling、stop/rollback、evidence handoff。No code changes in Phase A.

### Phase B — atomic S03/S04 implementation

Production write allowlist:

1. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
2. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
3. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`

Test write allowlist:

4. `tests/unit/application/test_issue_planning_prompt.py`
5. `tests/unit/application/test_issue_planning.py`
6. `tests/unit/infra/test_issue_planning_chatgpt.py`
7. `tests/integration/test_issue_planning_chatgpt_transport.py`

Evidence-only write after Green:

8. the Issue `report.md`, limited to changed files、test results、closure rows、model evidence boundary、fresh review gate。

### Read/run-only files

These may be inspected or executed but not modified in this cutover:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
* `tests/unit/domain/test_issue_planning_contracts.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py`
* command/CLI tests owned by S05
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
* operation resource `prompt.md` and `attachments/` trees
* provider projection tooling and parity tests
* existing S01/S02 implementation briefs and evidence

If a required production change appears in a read-only file, stop and amend the plan. Do not expand the allowlist during implementation by convenience.

### Forbidden changes

* `requirement.md`
* `design.md`
* Oracle compatibility ADR
* `candidate-note.md`
* Candidate archives or Candidate contents
* parent Epic or Initiative documents
* operation resource wording or inventory
* domain public status/reason mapping
* CLI options/parser/help
* Blue/Red binding/thread persistence
* Oracle version/profile registry
* submission/stage decoder
* inline attachment mode or retry budget
* harvest/capture builders
* Oracle artifact reader/schema
* output ZIP/JSON validators
* Candidate/Review/Human/apply authority
* installed/dogfood runtime files by direct manual edit
* personal wrapper、browser profile、credentials、target URL evidence
* patch bundles、archives、transcripts、session/thread identifiers
* any new attachment file format or generated metadata sidecar

## Implementation handoff checklist

### Authorization and identity

* [ ] GitHub confirms repository `chemitaro/spec-dock`.
* [ ] Current branch is `codex/iss-00354-chatgpt-context-contract`.
* [ ] Implementation base HEAD is re-verified; this brief’s base is `a2bc5e00cf7aefe049c234bfe0207f992077af8f`.
* [ ] Branch comparison uses the named branch; default branch fallback is not used.
* [ ] Phase A plan/report amendment is adopted before code work.
* [ ] Existing S01/S02 closure evidence remains unchanged.
* [ ] No unrelated worktree changes are included.

### Red

* [ ] `tc-s03-001` fails on payload fields/materialization under the current baseline.
* [ ] `tc-s04-001` fails on one-pack argv/generated files under the current baseline.
* [ ] Red tests cover Planning、archive Review、git-bound Review、Semantic Revision.
* [ ] Red tests distinguish managed resource validation from operator/dynamic path inspection.
* [ ] No Red-only state is represented as runnable or closed.

### Green — application

* [ ] `PlanningPromptAttachment` has no production references.
* [ ] `SynthesizedPlanningPrompt` is path-only.
* [ ] `.attachments` and `.exact_attachments` are absent.
* [ ] Planning uses managed directory + canonical/relevant original paths.
* [ ] Review uses original Candidate path and, for git-bound mode, original canonical targets.
* [ ] Semantic Revision uses original Candidate、Review、revision-request paths.
* [ ] Candidate members are not extracted for transport.
* [ ] reviewed identity and digest are rendered in the minimal body, not files.
* [ ] source preflight evidence is not copied into transport state.
* [ ] post-synthesis attachment scan/hash comparison is removed.
* [ ] lifecycle validation and postflight stale checks remain.

### Green — infra

* [ ] Every path becomes an exact repeated `--file` operand.
* [ ] Path order and duplicates are preserved.
* [ ] One exact prompt operand remains.
* [ ] `_write_transport_pack` and input-pack helpers are deleted.
* [ ] No input temporary directory or generated transport metadata exists.
* [ ] No tree/open/copy/ZIP/hash operation is performed for attachment transport.
* [ ] managed Chrome、env、executable identity、model selector、session slug regressions pass.
* [ ] output staging and typed snapshot regressions pass.
* [ ] no retry、inline、profile、stage、artifact-reader scope is introduced.

### Combined verification

* [ ] Focused S03/S04 suite passes on one HEAD.
* [ ] Unchanged domain contract regression passes.
* [ ] S01/S02 regression subset passes.
* [ ] Ruff passes.
* [ ] Mypy passes.
* [ ] SpecDock validate passes.
* [ ] `git diff --check` passes.
* [ ] Legacy-removal `rg` gate has zero production implementation matches.
* [ ] Changed files are exactly within the Phase B allowlist plus evidence-only report update.
* [ ] No private path、raw prompt、transcript、session/thread identifier appears in evidence.

### Closure and review

* [ ] Exact resulting HEAD is pushed and re-verified through GitHub.
* [ ] One fresh read-only review covers the full atomic change-set.
* [ ] Requested model and measured wrapper/browser model evidence are recorded separately.
* [ ] Luna/Max is not claimed without explicit verified evidence.
* [ ] Any repair uses a new exact HEAD and a new fresh review.
* [ ] `cl-s03-path-input` and `cl-s04-direct-transport` cite the same resulting HEAD.
* [ ] `tc-s03-001` and `tc-s04-001` evidence is attached to the correct closure owner.
* [ ] stale `cl-s04-profile` is not closed; canonical `cl-s04-direct-transport` is used.
* [ ] historical S02 closure evidence is preserved; any alias correction is non-semantic.
* [ ] S05 handoff explicitly states path-only application contract and repeated direct Oracle operands.
* [ ] Human adoption、PR、merge、Issue close remain separate decisions.
