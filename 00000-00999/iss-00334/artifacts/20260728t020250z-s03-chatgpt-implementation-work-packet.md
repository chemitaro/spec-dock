---
created_by_role: chatgpt-pro
scope_id: iss-00334
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_stage.py
  - artifacts/20260727t024714z-chatgpt-blue-bounded-correction-followup.md
intended_targets:
  - iss-00334/S03
adoption_status: execution-input
reflected_to: []
diff_guard_result: passed
source_head: 530cca24943892dd440ca67823a9d68dfc46763d
oracle_sessions:
  - iss00334-s03-implementa-brief
  - required-repository-connector-context-github-108
model_selection:
  initial: requested=Pro; resolved=Pro; verified=yes
  followup: requested=Pro; resolved=unavailable; verified=no
---

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a680265-c7dc-83ee-876e-8928246192e3

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached follow-up as the complete instruction. Re-evaluate the prior S03 stop under the Human-authorized JIT step-artifact boundary and return only the requested replacement packet or minimal unresolved choice.

## Answer

# S03 Replacement Implementation Work Packet

## 1. Scope confirmation and exact GitHub HEAD evidence

### Verified execution identity

| Field                      | Verified value                                        |
| -------------------------- | ----------------------------------------------------- |
| Repository                 | `chemitaro/spec-dock`                                 |
| Current branch             | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Default branch             | `main`                                                |
| Required HEAD              | `530cca24943892dd440ca67823a9d68dfc46763d`            |
| Observed branch comparison | `identical`; ahead `0`, behind `0`                    |
| Observed HEAD              | `530cca24943892dd440ca67823a9d68dfc46763d`            |

The exact HEAD exists, records S02 as committed and published, and explicitly hands execution to S03.

### Re-evaluation result

**The prior S03 stop is withdrawn.**

The Human-authorized JIT boundary explicitly permits this execution artifact to fix the smallest internal v1 encodings, schemas, helper boundaries, and test parameters needed to implement the already-approved S03 outcome. It does not permit changing the public command family, named identity fields, lifecycle success pair, Human authority, Issue scope, or later-step boundaries.

All twelve previously identified gaps are **implementation-local**. No unresolved Human product-semantic choice remains.

This conclusion is consistent with the canonical Plan: each implementation step must receive one exact, bounded execution artifact containing allowed paths, tests, ordering, stop conditions, and worker instructions; that artifact concretizes the step without expanding its scope.

### S03 boundary

This packet authorizes only:

* parsing an already-received S02 Planner payload;
* validating and normalizing exactly three Markdown documents;
* Runtime-owned Candidate controls and identity derivation;
* one named Issue Candidate ZIP validation profile using the existing authoring-pack ZIP engine;
* repository-external temporary construction;
* validation-before-publication;
* atomic no-replace publication;
* `ok/candidate_created` only after successful publication;
* S03 Red-first tests and direct S01/S02/shared-authoring-pack regressions.

The canonical S03 milestone requires those exact outcomes and tests.

S04 Review/revision, S05 Human Gate/apply, S06 projection and runtime wiring, live ChatGPT dogfood, canonical mutation, Git mutation, commit, and push remain excluded.

---

## 2. Repository findings and reuse map

### Existing owners and compatibility rules

| Existing owner                                                    | Current contract                                                                                                                                                                        | S03 action                                                                                                                                |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `application/issue_planning.py` — `PlanningCreateRequest`         | Already carries only `issue_id` and explicit `output_dir`.                                                                                                                              | Reuse unchanged.                                                                                                                          |
| `application/issue_planning.py` — `resolve_existing_issue_target` | Resolves exactly one existing Issue, validates parents and path containment, rejects symlinked/incomplete canonical targets, and returns the three canonical paths in UTF-8 byte order. | Reuse for Issue identity and canonical front-matter baseline. Do not add Seed behavior.                                                   |
| `application/issue_planning.py` — `run_issue_planning_transport`  | Owns S02 Git preflight, `PlanningContext`, Prompt synthesis, source-manifest comparison, and backend invocation.                                                                        | Call once. Do not duplicate Git or backend handling.                                                                                      |
| `domain/issue_planning_contracts.py` — `PlanningSourceEvidence`   | Binds repository, branch, upstream, equal local/remote HEADs, source-manifest hash, snapshot ID, and fetched-remote disposition.                                                        | Reuse byte-for-byte as the source of Candidate baseline fields.                                                                           |
| `domain/issue_planning_contracts.py` — `PlanningInvocationResult` | Keeps the extracted payload only in non-serialized `transient_payload`; response SHA is separately recorded.                                                                            | Require exact successful evidence before parsing. Never persist the raw payload.                                                          |
| `domain/issue_planning_contracts.py` — `IssueCandidateIdentity`   | Already fixes all named identity fields and the only permitted transport alias: the logical stem followed by one space and a positive `(N)` suffix.                                     | Reuse unchanged. S03 derives its values; it does not change fields or alias grammar.                                                      |
| `domain/issue_planning_contracts.py` — canonical identity JSON    | Existing identity digests use compact, sorted UTF-8 JSON **without** a trailing LF.                                                                                                     | Do not modify this helper or existing digest bytes. Candidate control JSON uses a separate LF-terminated encoder.                         |
| `application/issue_planning_prompt.py`                            | Loads `planner-prompt.md` verbatim into the closed Prompt, adds exact source identity, and retains the existing outer response frame.                                                   | No code change required. Update only the provider Planner resource with the inner three-document grammar.                                 |
| `planner-prompt.md`                                               | Currently constrains authority and scope but provides no inner document framing.                                                                                                        | Add the exact grammar in Section 3.                                                                                                       |
| `domain/authoring_pack/zip_contract.py` — `review_pack_input`     | The current no-argument path is hard-coded to the generic authoring-pack root and metadata.                                                                                             | Add an optional named profile seam. Calling `review_pack_input(path)` without a profile must execute the existing generic path unchanged. |
| `domain/authoring_pack/zip_contract.py` — safety loop             | Already checks encryption, symlink mode, executable permission, nested archive suffixes, entry/total size, UTF-8, exact duplicate names, and CRC through archive reads.                 | Reuse and extend only for the named Issue Candidate profile with its stricter inventory/collision/resource checks.                        |
| `infra/clock.py`                                                  | Provides an injectable second-resolution local-zone ISO timestamp.                                                                                                                      | Application receives the callable; Candidate domain converts the instant to UTC once. Do not change the shared clock.                     |
| `candidate_contract.py`                                           | Validates Initiative/Epic decomposition candidates, not Issue Planning ZIPs.                                                                                                            | Read-only. Do not overload it.                                                                                                            |
| `pack_stage.py`                                                   | Stages generic authoring packs and creates unrelated reports/adoption files.                                                                                                            | Read-only. Do not call it.                                                                                                                |
| `binary_artifact_publisher.py`                                    | Its public guard is tied to repository Workbench Markdown and repository-contained destinations; its low-level no-replace mechanics are private.                                        | Compatibility reference only. Do not bypass its guard or import private methods.                                                          |

### Smallest correct placement

1. **Application orchestration:** extend `application/issue_planning.py`.
2. **Pure S03 domain contract:** add `domain/issue_planning_candidate.py`.
3. **Shared ZIP profile seam:** minimally extend `domain/authoring_pack/zip_contract.py`.
4. **Filesystem/ZIP implementation:** add `infra/issue_planning_candidate.py`.
5. **Prompt grammar:** update only provider `planner-prompt.md`.
6. **Tests:** add/extend only the exact files in Section 4.

### Historical Candidate-control compatibility reference

The historical artifact’s Candidate-control section is used only as a compatibility reference for compact canonical JSON, timestamp-based v1 naming, checksums excluding their own file, detached external ZIP SHA, and atomic no-overwrite publication.

Current S03 concretization intentionally differs in four bounded ways:

* inventory is exactly the canonical seven files; optional package artifacts are not permitted;
* `internal_root` is stored **without** a trailing slash because the current `IssueCandidateIdentity` accepts a normalized relative path;
* `SOURCE-BASELINE.json` additionally binds the complete S02 source evidence and exact Planner payload digest;
* the placeholder map admits a closed dynamic declaration schema because the current canonical S03 tests require dynamic-positive and remaining-token-negative fixtures.

---

## 3. Exact S03 contracts and sequencing

### 3.1 Classification of the twelve prior gaps

| Prior gap                                      | Classification         | Exact S03 decision                                                                                                                                 |
| ---------------------------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Three-document payload grammar              | `implementation-local` | Use the line-delimited closed grammar in §3.2 and add it to `planner-prompt.md`.                                                                   |
| 2. Front matter and completeness               | `implementation-local` | Use the current Japanese front-matter key sets/types, compare against current canonical values, and apply the bounded completeness oracle in §3.3. |
| 3. Internal root                               | `implementation-local` | Derive it from the v1 logical filename stem, without a trailing slash.                                                                             |
| 4. Create version and logical filename         | `implementation-local` | Initial create version is `1`; use one UTC second timestamp and the template in §3.4.                                                              |
| 5. Candidate ID                                | `implementation-local` | `<issue-id>-v1-<timestamp-token>`.                                                                                                                 |
| 6. `SOURCE-BASELINE.json`                      | `implementation-local` | Use the closed schema in §3.5.2.                                                                                                                   |
| 7. `MANIFEST.json`                             | `implementation-local` | Use the closed schema and exact seven-entry inventory in §3.5.3.                                                                                   |
| 8. `CHECKSUMS.sha256`                          | `implementation-local` | Use the two-space, LF-only, root-relative form in §3.5.5.                                                                                          |
| 9. `PLACEHOLDER-ORACLE-MAP.json`               | `implementation-local` | Use the closed file/token declaration schema in §3.5.4; create emits an empty declaration list.                                                    |
| 10. Identity versus external ZIP SHA order     | `implementation-local` | Keep ZIP SHA out of the archive; derive it from final staged ZIP bytes and place it only in detached `IssueCandidateIdentity` and command output.  |
| 11. Timestamp, uniqueness, and reproducibility | `implementation-local` | Capture one operation instant; all other bytes are deterministic functions of normalized inputs and that instant.                                  |
| 12. Success output and failure reasons         | `implementation-local` | Use the exact output keys and closed status/reason table in §3.8.                                                                                  |

The decisions above do not change the canonical identity field set, mandatory Candidate inventory, atomic publication rule, generic-authoring-pack compatibility rule, or `ok/candidate_created` lifecycle meaning. Those are already fixed by the canonical design.

---

### 3.2 Exact Planner inner payload grammar

S02 continues to own and remove the existing outer response frame. The S03 parser receives only `PlanningInvocationResult.transient_payload`; it does not inspect the outer role or source-HEAD marker.

The inner payload is exactly:

```text
<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=requirement.md>>>
<complete requirement.md bytes, ending with LF>
<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=requirement.md>>>
<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=design.md>>>
<complete design.md bytes, ending with LF>
<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=design.md>>>
<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=plan.md>>>
<complete plan.md bytes, ending with LF>
<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=plan.md>>>
```

Parser rules:

1. Decode as strict UTF-8.
2. Reject UTF-8 BOM, NUL, and every `\r`; v1 payloads are LF-only.
3. Require the exact order `requirement.md`, `design.md`, `plan.md`.
4. Require exactly one start and one matching end marker per document.
5. Permit no byte before the first start marker or after the final end marker.
6. Require every document body to end with one LF immediately before its end marker.
7. Reject duplicate, missing, reordered, unknown, or fourth documents.
8. Reject any body line beginning with either reserved marker prefix:

   * `<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1`
   * `<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1`
9. Markers are transport syntax and are never written to the Candidate.
10. Parser output is an immutable three-entry object keyed by the canonical filenames.

`planner-prompt.md` must include this grammar verbatim and instruct the Planner to return no prose, code fence, explanation, or fourth object outside it.

---

### 3.3 Front matter and substantive completeness

#### Current-canonical front-matter baseline

Before invoking the backend, Runtime reads the three current canonical documents through the already-resolved canonical paths and parses their front matter using the same closed parser used for the response.

The three current documents must agree on:

* `ID`;
* `タイトル`;
* `状態`;
* `作成者`;
* `親`.

File-specific values must be:

| File             | `種別`           | `依存`                              |
| ---------------- | -------------- | --------------------------------- |
| `requirement.md` | `要件定義書（Issue）` | key absent                        |
| `design.md`      | `設計書（Issue）`   | `["requirement.md"]`              |
| `plan.md`        | `実装計画書（Issue）` | `["requirement.md", "design.md"]` |

The current canonical files demonstrate these Japanese key sets and value types.

If the current canonical baseline is malformed or internally inconsistent, return:

```text
rejected / planning_context_rejected
```

and do not invoke the backend.

#### Required Planner front matter

`requirement.md`:

```yaml
---
種別: 要件定義書（Issue）
ID: "<exact current Issue ID>"
タイトル: "<exact current Issue title>"
状態: "<exact current canonical state>"
作成者: "<exact current canonical author>"
最終更新: "<YYYY-MM-DD>"
親: ["<exact parent Epic ID>", "<exact parent Initiative ID>"]
---
```

`design.md`:

```yaml
---
種別: 設計書（Issue）
ID: "<exact current Issue ID>"
タイトル: "<exact current Issue title>"
状態: "<exact current canonical state>"
作成者: "<exact current canonical author>"
最終更新: "<YYYY-MM-DD>"
依存: ["requirement.md"]
親: ["<exact parent Epic ID>", "<exact parent Initiative ID>"]
---
```

`plan.md`:

```yaml
---
種別: 実装計画書（Issue）
ID: "<exact current Issue ID>"
タイトル: "<exact current Issue title>"
状態: "<exact current canonical state>"
作成者: "<exact current canonical author>"
最終更新: "<YYYY-MM-DD>"
依存: ["requirement.md", "design.md"]
親: ["<exact parent Epic ID>", "<exact parent Initiative ID>"]
---
```

Validation and normalization rules:

* exact key set and exact key order;
* no duplicate or unknown keys;
* `種別` is the exact unquoted fixed string shown above;
* scalar values are JSON-quoted strings;
* array values are JSON-style arrays of quoted strings;
* `ID`, title, state, author, dependency, and parent values must match the current canonical baseline;
* `最終更新` must be a valid Gregorian `YYYY-MM-DD`, but its submitted value is not retained;
* Runtime re-emits the front matter and sets `最終更新` to the operation timestamp’s UTC date;
* Runtime preserves the validated semantic body bytes, changes line endings only by rejecting non-LF input, and emits exactly one final LF;
* copied `状態` is document metadata, not Review or Human approval evidence.

#### Substantive completeness oracle

After front matter:

1. The first nonblank line must be one H1, beginning `# ` and containing both the exact Issue ID and title.
2. Exactly one H1 is allowed.
3. At least one H2 section is required.
4. Every H2 section must contain at least one substantive line before the next H1/H2 or end of file.
5. A substantive line is nonblank and is not:

   * a Markdown heading;
   * a fence delimiter consisting only of backticks or tildes;
   * an HTML comment line.
6. List items, table rows, blockquotes, and content inside code/PlantUML fences count as substantive.
7. Heading-only, fence-only, comment-only, or empty H2 sections are rejected.
8. No required section names are invented; semantic section naming remains Planner-owned within the Issue scope.

Any payload/front-matter/completeness failure returns:

```text
rejected / planner_response_rejected
```

with content-free finding codes only.

---

### 3.4 Candidate naming, operation timestamp, and deterministic bytes

After output-directory preflight and successful document parsing/normalization, obtain one clock value and convert it to UTC.

Exact forms:

```text
created_at_utc = YYYY-MM-DDTHH:MM:SSZ
timestamp_token = YYYYMMDDtHHMMSSz
version = 1
logical_filename =
  <timestamp_token>-<issue-id>-issue-planning-candidate-v1.zip
candidate_id =
  <issue-id>-v1-<timestamp_token>
internal_root =
  <timestamp_token>-<issue-id>-issue-planning-candidate-v1
observed_transport_filename =
  logical_filename
```

`internal_root` has no trailing slash in `MANIFEST.json` or `IssueCandidateIdentity`. ZIP entry names use:

```text
<internal_root>/<relative-entry-path>
```

A create operation never invents a `(N)` suffix. If the logical filename already exists, it returns `rejected/output_collision`. The closed `(N)` grammar is accepted only when validating a later observed transport filename against an existing logical filename.

#### Reproducibility classification

| Field or bytes                                                           | Classification                                                        |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| Parsed semantic body bytes                                               | Deterministic from exact Planner payload                              |
| Normalized front matter                                                  | Deterministic from current canonical baseline plus UTC operation date |
| Source baseline                                                          | Deterministic from S02 evidence, context, and exact payload digest    |
| Placeholder map emitted by create                                        | Deterministic empty declaration                                       |
| Manifest and checksums                                                   | Deterministic                                                         |
| ZIP entry order, names, permissions, compression, comments, extra fields | Deterministic                                                         |
| `created_at_utc` / `timestamp_token`                                     | Intentionally operation-unique                                        |
| Candidate ID, logical filename, internal root                            | Deterministic functions of the operation timestamp                    |
| Temporary directory name                                                 | Ephemeral, non-identity, never serialized                             |
| UUID/random Candidate ID                                                 | Not used                                                              |
| External ZIP SHA-256                                                     | Deterministic from actual staged ZIP bytes                            |

For a fixed normalized input set and fixed operation timestamp, the generated ZIP bytes must be identical.

---

### 3.5 Exact Candidate controls

#### 3.5.1 Canonical control JSON bytes

`SOURCE-BASELINE.json`, `MANIFEST.json`, and `PLACEHOLDER-ORACLE-MAP.json` use a separate `CanonicalControlJsonV1` encoder:

1. UTF-8, no BOM.
2. Exactly one top-level JSON object.
3. Closed required keys; no unknown or duplicate keys.
4. Object keys recursively sorted by UTF-8 byte order.
5. Arrays remain in schema-defined order; validators reject unsorted arrays rather than silently sorting.
6. Compact separators `,` and `:` with no insignificant whitespace.
7. Non-ASCII characters are emitted directly, not `\u`-escaped.
8. Integers only; no floating-point numbers, `NaN`, or infinity.
9. Exactly one final LF.
10. Existing identity canonical JSON remains unchanged and LF-free.

#### 3.5.2 `SOURCE-BASELINE.json`

Exact top-level keys:

```json
{
  "canonical_issue_paths": [
    "<design path>",
    "<plan path>",
    "<requirement path>"
  ],
  "dependency_ids": [],
  "issue_id": "iss-00334",
  "parent_epic_id": "epic-00331",
  "parent_initiative_id": "init-00322",
  "planner_payload_sha256": "<64 lowercase hex>",
  "planner_payload_size": 1,
  "relevant_paths": [],
  "remote_head": "<40 lowercase hex>",
  "remote_head_disposition": "fetched_remote_tracking_ref",
  "schema_version": "spec-dock.issue-candidate-source-baseline.v1",
  "snapshot_id": "<64 lowercase hex>",
  "source_branch": "<named branch>",
  "source_head": "<40 lowercase hex>",
  "source_manifest_hash": "<64 lowercase hex>",
  "source_repository": "<lowercase owner/repository>",
  "upstream": "origin/<named branch>"
}
```

Rules:

* exact 17-key object;
* `source_*`, `remote_head`, `upstream`, `snapshot_id`, and disposition derive only from `PlanningSourceEvidence`;
* `source_head == remote_head`;
* `upstream == "origin/" + source_branch`;
* canonical paths are the existing resolver’s exact UTF-8-ordered tuple;
* dependency IDs and relevant paths are unique and already UTF-8 sorted;
* `planner_payload_sha256` is SHA-256 of the exact `transient_payload`;
* it must equal `PlanningInvocationResult.response_sha256`;
* `planner_payload_size == len(transient_payload)`;
* the outer-frame byte count is not stored;
* no absolute path, output directory, raw payload, transcript, backend stderr, token, or credential is stored.

#### 3.5.3 `MANIFEST.json`

Exact top-level structure:

```json
{
  "candidate": {
    "candidate_id": "<issue-id>-v1-<timestamp-token>",
    "created_at_utc": "<YYYY-MM-DDTHH:MM:SSZ>",
    "internal_root": "<logical filename stem>",
    "issue_id": "<issue-id>",
    "logical_filename": "<timestamp>-<issue-id>-issue-planning-candidate-v1.zip",
    "version": 1
  },
  "checksum_algorithm": "sha256",
  "checksum_file": "CHECKSUMS.sha256",
  "entries": [
    {
      "checksum_covered": false,
      "content_mode": "static",
      "path": "CHECKSUMS.sha256",
      "role": "checksums"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "MANIFEST.json",
      "role": "manifest"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "PLACEHOLDER-ORACLE-MAP.json",
      "role": "placeholder-map"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "SOURCE-BASELINE.json",
      "role": "source-baseline"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "design.md",
      "role": "design"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "plan.md",
      "role": "plan"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "requirement.md",
      "role": "requirement"
    }
  ],
  "placeholder_oracle_map_sha256": "<SHA-256 of exact map bytes>",
  "schema_version": "spec-dock.issue-candidate-manifest.v1",
  "source_baseline_sha256": "<SHA-256 of exact baseline bytes>"
}
```

Rules:

* exact seven Candidate files; optional files and directory entries are forbidden;
* entries are ordered by `path.encode("utf-8")`;
* every role and path appears exactly once;
* `CHECKSUMS.sha256` is the sole entry with `checksum_covered=false`;
* `content_mode` is `static` or `dynamic`;
* only `requirement.md`, `design.md`, and `plan.md` may be `dynamic`;
* an entry is `dynamic` exactly when the placeholder map declares that path;
* S03 create emits an empty map, so all seven entries are `static`;
* external ZIP SHA and observed transport filename are not stored in the archive;
* no file size or checksum is duplicated into MANIFEST; those are verified through `CHECKSUMS.sha256`.

#### 3.5.4 `PLACEHOLDER-ORACLE-MAP.json`

S03 create emits:

```json
{
  "files": [],
  "schema_version": "spec-dock.issue-candidate-placeholder-map.v1"
}
```

The v1 validator accepts this closed entry shape for parameterized oracle fixtures:

```json
{
  "path": "design.md",
  "tokens": [
    "{{SPECDOCK_EXAMPLE_TOKEN}}"
  ]
}
```

Rules:

* exact top-level keys `files` and `schema_version`;
* exact file-entry keys `path` and `tokens`;
* `files` ordered by UTF-8 path bytes, unique;
* allowed paths are only the three canonical Markdown filenames;
* tokens are ordered by UTF-8 bytes, unique;
* token grammar:

```regex
\{\{SPECDOCK_[A-Z][A-Z0-9_]{0,63}\}\}
```

* only declared `dynamic` files are scanned;
* in a dynamic file:

  * a token-like match not listed for that file is `undeclared_placeholder`;
  * a listed token still present is `remaining_placeholder`;
  * all declared tokens absent after rendering is valid;
* static files are verified only by their checksum and are never token-scanned;
* therefore, a static exact-hash Markdown example containing `{{SPECDOCK_LITERAL_EXAMPLE}}` remains valid;
* Runtime’s direct front-matter renderer needs no placeholders, so normal create emits `files: []`.

#### 3.5.5 `CHECKSUMS.sha256`

Exact line form:

```text
<64 lowercase hexadecimal SHA-256><two ASCII spaces><entry path><LF>
```

Coverage and ordering:

```text
MANIFEST.json
PLACEHOLDER-ORACLE-MAP.json
SOURCE-BASELINE.json
design.md
plan.md
requirement.md
```

Rules:

* root-relative paths only;
* UTF-8 ASCII subset and LF-only;
* exactly two ASCII spaces between digest and path;
* sorted by `path.encode("utf-8")`;
* exactly one line per covered entry;
* final LF required;
* `CHECKSUMS.sha256` does not contain its own checksum;
* reject missing, extra, duplicate, uppercase, malformed, root-prefixed, CRLF, blank, or trailing-space lines;
* each digest covers the exact uncompressed file bytes.

---

### 3.6 Candidate identity derivation

Identity finalization order is exact:

1. Validate and normalize the three documents.
2. Capture the one UTC operation timestamp.
3. Generate `SOURCE-BASELINE.json`.
4. Generate `PLACEHOLDER-ORACLE-MAP.json`.
5. Generate `MANIFEST.json`, including hashes of the preceding two controls.
6. Generate `CHECKSUMS.sha256`, covering every file except itself.
7. Build the deterministic ZIP.
8. Validate the ZIP through the named Issue Candidate profile.
9. Compute SHA-256 and byte count from the closed staged ZIP.
10. Re-read validated controls from the staged ZIP and derive:

    * Issue ID, Candidate ID, version, logical filename, internal root from MANIFEST;
    * source repository, branch, HEAD from SOURCE-BASELINE;
    * observed transport filename from the actual basename;
    * ZIP SHA from actual staged ZIP bytes.
11. Construct the existing `IssueCandidateIdentity`.
12. Verify:

    * create observed filename equals logical filename;
    * manifest/root/name/timestamp/version relations;
    * source evidence and payload binding;
    * actual ZIP SHA;
    * exact seven-entry inventory.
13. Publish only after the derived identity is valid.

The ZIP SHA is deliberately detached, avoiding self-reference. The canonical design permits Runtime-owned controls and identity while requiring the external ZIP SHA as part of the final identity.

#### Transport alias compatibility

Given logical filename:

```text
20260728t120000z-iss-00334-issue-planning-candidate-v1.zip
```

accepted observed names are:

```text
20260728t120000z-iss-00334-issue-planning-candidate-v1.zip
20260728t120000z-iss-00334-issue-planning-candidate-v1 (1).zip
20260728t120000z-iss-00334-issue-planning-candidate-v1 (27).zip
```

Reject:

```text
...candidate-v1(1).zip
...candidate-v1 (0).zip
...candidate-v1 (01).zip
...candidate-v1-copy.zip
renamed.zip
subdir/candidate.zip
```

Alias acceptance never waives actual ZIP SHA, internal root, MANIFEST identity, or source binding.

---

### 3.7 Named Issue Candidate ZIP profile and publication sequence

#### Named ZIP profile

Extend `review_pack_input` with an optional keyword-only profile:

```text
review_pack_input(path)
    -> current generic behavior, byte-for-byte compatibility

review_pack_input(path, profile=issue_candidate_v1_profile)
    -> strict Issue Candidate ZIP validation
```

The profile is immutable and supplies:

```text
name = issue-planning-candidate-v1
input_kind = zip only
expected_root = derived internal_root
required_paths = exact seven paths
allowed_suffixes = .md, .json, .sha256
max_file_count = 7
max_entry_bytes = 2_000_000
max_total_bytes = 10_000_000
max_entry_compression_ratio = 100
max_total_compression_ratio = 100
cross_file_validator = Issue Candidate v1 validator
```

Strict profile checks:

* ZIP input only; tree fallback rejected;
* one exact internal root;
* no explicit directory entries;
* no absolute, drive-letter, backslash, empty, `.`, `..`, NUL, hidden, or ambiguous paths;
* no exact duplicate, case-fold collision, or Unicode-NFC collision;
* regular files only; reject symlink, hard-link/special mode, device, FIFO, socket, executable permission;
* no encryption;
* no nested archive;
* no unsupported suffix;
* strict UTF-8 for every file;
* `CHECKSUMS.sha256` must additionally be ASCII;
* CRC/read failure rejected;
* exact inventory;
* entry, total, count, and compression-ratio limits;
* sensitive payload scanner applied without serializing matched values;
* cross-file manifest, checksums, baseline, placeholder, and naming closure.

Generic authoring-pack constants, root, required metadata, result shape, tree behavior, and no-argument call path remain unchanged. The current generic implementation is explicitly rooted in `EXPECTED_OUTPUT_ROOT` and `REQUIRED_METADATA`, so the Issue profile must not replace those module defaults.

#### Safe build and publication sequence

1. Resolve the existing Issue.
2. Parse and validate the current canonical front-matter baseline.
3. Validate the explicit output directory **before backend invocation**:

   * path exists;
   * actual directory;
   * directory itself and every traversed component are non-symlink;
   * neither inside the repository nor an ancestor of the repository;
   * openable through a no-follow directory descriptor.
4. Run the existing S02 transport.
5. Require:

   * `status == "pass"`;
   * `reason == "transport_received"`;
   * non-null source evidence;
   * non-null payload;
   * non-null response SHA;
   * payload SHA equal to the recorded response SHA.
6. Parse and normalize the exact three documents.
7. Capture one operation time and derive v1 name/root/ID.
8. Reject an already-existing final filename.
9. Create a mode-`0700` owned temporary directory as a direct child of the output directory, ensuring the same filesystem.
10. Materialize only the seven internal files.
11. Build the ZIP with:

    * no explicit directory records;
    * UTF-8 entry names;
    * UTF-8 byte-sorted entry order;
    * fixed regular-file mode `0644`;
    * empty ZIP and entry comments;
    * empty extra fields;
    * fixed `ZIP_DEFLATED` compression and one fixed compression level;
    * each entry timestamp set from the one UTC operation instant.
12. Close and file-fsync the staged ZIP.
13. Validate it through the named profile.
14. Compute staged SHA-256 and byte count.
15. Derive and validate detached `IssueCandidateIdentity`.
16. Revalidate the output-directory descriptor identity and final-name absence.
17. Atomically move the staged ZIP to the final name using a platform no-replace primitive:

    * Linux: `renameat2(..., RENAME_NOREPLACE)`;
    * macOS: `renamex_np(..., RENAME_EXCL)`.
18. Do not fall back to `os.replace`, overwrite, copy-to-final, or a partially visible final file.
19. The atomic no-replace move is the final fallible lifecycle step. Once it succeeds, return success.
20. On every earlier failure, remove the owned temporary directory; the final filename remains absent.
21. A collision racing the early check is still rejected by the atomic primitive.
22. Unsupported no-replace publication returns blocked before a final filename is created.

---

### 3.8 Exact result contract

#### Success

Return only after successful atomic publication:

```json
{
  "status": "ok",
  "reason": "candidate_created",
  "issue_id": "iss-00334",
  "output": {
    "candidate_identity": {
      "issue_id": "iss-00334",
      "candidate_id": "<derived>",
      "version": 1,
      "logical_filename": "<derived basename>",
      "observed_transport_filename": "<same basename>",
      "internal_root": "<derived stem>",
      "source_repository": "chemitaro/spec-dock",
      "source_branch": "<branch>",
      "source_head": "<40-hex>",
      "zip_sha256": "<64-hex>"
    },
    "zip_byte_count": 1
  },
  "details": []
}
```

The exact success `output` keys are:

```text
candidate_identity
zip_byte_count
```

No output directory, absolute path, temporary path, transcript, prompt, backend stream, or raw document content is serialized.

#### Closed failure mapping

| Condition                                                                                                      | Status                                    | Reason                           |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | -------------------------------- |
| S02 blocked/rejected outcome                                                                                   | Preserve existing `blocked` or `rejected` | Preserve the existing S02 reason |
| Canonical front-matter baseline invalid                                                                        | `rejected`                                | `planning_context_rejected`      |
| Payload missing, digest mismatch, malformed document framing, front matter, wrong Issue, or incomplete section | `rejected`                                | `planner_response_rejected`      |
| Output missing, non-directory, symlinked, repository-contained, repository-ancestor, or unsafe ancestry        | `rejected`                                | `candidate_output_rejected`      |
| Existing or raced final filename                                                                               | `rejected`                                | `output_collision`               |
| Named ZIP profile or cross-file validation not `pass`                                                          | `rejected`                                | `archive_rejected`               |
| Temporary directory, control-file, or ZIP write failure before publication                                     | `blocked`                                 | `candidate_build_failed`         |
| Atomic no-replace primitive unsupported or fails without creating the final name                               | `blocked`                                 | `candidate_publication_failed`   |

Rules:

* archive finding codes are placed in `details`; unsafe raw values and paths are not;
* no unknown exception is converted to a lifecycle result—unexpected programming faults propagate;
* no failure result includes `transient_payload`;
* no non-success result leaves the logical final filename;
* `ok` remains non-ready; only later S05 success may return `ready`.

---

## 4. Exact write allowlist and read-only reuse paths

### Exact write allowlist

#### Provider product code/resources

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
├── application/issue_planning.py
├── domain/authoring_pack/zip_contract.py
├── domain/issue_planning_candidate.py          # new
└── infra/issue_planning_candidate.py           # new
```

#### Tests

```text
tests/
├── integration/test_issue_planning_chatgpt_transport.py
└── unit/
    ├── application/test_issue_planning.py
    ├── application/test_issue_planning_prompt.py
    ├── authoring_pack/test_zip_contract_profiles.py   # new
    ├── domain/test_issue_planning_candidate.py        # new
    └── infra/test_issue_planning_candidate.py         # new
```

No other path is authorized.

### Read-only reuse and regression paths

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/
├── reviewer-prompt.md
└── transport-output-contract.md

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
├── application/contracts.py
├── application/issue_planning_prompt.py
├── application/authoring_pack/pack_review.py
├── application/authoring_pack/pack_stage.py
├── cli/bootstrap.py
├── commands/issue_planning.py
├── domain/issue_planning_contracts.py
├── domain/authoring_pack/candidate_contract.py
├── domain/authoring_pack/prompt_pack_contract.py
├── infra/binary_artifact_publisher.py
├── infra/clock.py
├── infra/issue_planning_chatgpt.py
└── presentation/issue_planning.py

tests/
├── cli_runtime/test_chatgpt_cli.py
├── unit/application/test_issue_planning_prompt.py
├── unit/authoring_pack/test_backend_invoke_capture.py
├── unit/commands/test_issue_planning.py
├── unit/domain/test_issue_planning_contracts.py
├── unit/infra/test_issue_planning_chatgpt.py
└── unit/presentation/test_issue_planning.py
```

### Canonical and dogfood paths — strictly read-only

```text
spec-dock/initiatives/.../iss-00334-implement-chatgpt-issue-planning-workflow/
├── requirement.md
├── design.md
├── plan.md
├── report.md
├── .assurance.json
└── artifacts/

spec-dock/scripts/
```

Provider authority remains under `src/spec_dock/assets/`; root `spec-dock/` is not a worker implementation surface.

---

## 5. Red-first test matrix

| Test node                                                                               | Required assertion                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_parse_planner_payload_accepts_exact_three_document_grammar`                       | Returns exactly the three body byte sequences in canonical order.                                                                                                                                                                                                                                                       |
| `test_parse_planner_payload_rejects_missing_duplicate_extra_and_reordered_documents`    | Parameterized missing, duplicate, fourth, unknown, and reordered markers; no build call.                                                                                                                                                                                                                                |
| `test_parse_planner_payload_rejects_bom_cr_nul_invalid_utf8_and_reserved_marker_body`   | Every unsafe byte/frame class is rejected.                                                                                                                                                                                                                                                                              |
| `test_planner_prompt_contains_exact_inner_document_contract`                            | Synthesized Planner Prompt contains all six exact markers and canonical order.                                                                                                                                                                                                                                          |
| `test_current_front_matter_baseline_is_closed_and_consistent`                           | Existing three docs establish one Issue/title/state/author/parent baseline and exact dependencies.                                                                                                                                                                                                                      |
| `test_current_front_matter_inconsistency_short_circuits_backend`                        | Invalid source baseline returns `planning_context_rejected`; backend calls `0`.                                                                                                                                                                                                                                         |
| `test_planner_front_matter_rejects_missing_unknown_duplicate_and_wrong_typed_fields`    | Each closed-schema violation is rejected.                                                                                                                                                                                                                                                                               |
| `test_planner_front_matter_rejects_wrong_issue_title_state_author_parent_or_dependency` | Target identity cannot be model-rewritten.                                                                                                                                                                                                                                                                              |
| `test_runtime_normalizes_front_matter_and_utc_update_date`                              | Exact key order/style, current baseline values, operation UTC date, LF-only, one final LF.                                                                                                                                                                                                                              |
| `test_document_completeness_rejects_missing_h1_missing_h2_and_empty_h2`                 | No Candidate for structurally incomplete documents.                                                                                                                                                                                                                                                                     |
| `test_document_completeness_accepts_table_list_and_fenced_content`                      | Legitimate substantive structures count.                                                                                                                                                                                                                                                                                |
| `test_canonical_control_json_is_compact_utf8_sorted_and_lf_terminated`                  | Exact byte contract; duplicate/unknown/float/CRLF variants rejected.                                                                                                                                                                                                                                                    |
| `test_source_baseline_binds_exact_s02_source_evidence_context_and_payload`              | All 17 fields and payload digest/size independently recompute.                                                                                                                                                                                                                                                          |
| `test_v1_naming_uses_one_utc_second_instant`                                            | Manifest timestamp, token, Candidate ID, logical filename, root, and update date are coherent.                                                                                                                                                                                                                          |
| `test_manifest_has_exact_seven_sorted_entries`                                          | No optional, missing, duplicate, or extra files/roles.                                                                                                                                                                                                                                                                  |
| `test_manifest_does_not_contain_external_zip_sha_or_observed_filename`                  | No self-reference or transport observation inside ZIP.                                                                                                                                                                                                                                                                  |
| `test_checksums_cover_every_entry_except_self_in_utf8_order`                            | Exact two-space lines and correct digests.                                                                                                                                                                                                                                                                              |
| `test_placeholder_oracle_accepts_resolved_declared_dynamic_tokens`                      | A declared token absent after rendering passes.                                                                                                                                                                                                                                                                         |
| `test_placeholder_oracle_rejects_remaining_and_undeclared_dynamic_tokens`               | Both negative classes fail closed.                                                                                                                                                                                                                                                                                      |
| `test_placeholder_oracle_does_not_scan_static_literal_examples`                         | Static exact-hash Markdown with placeholder-like example passes.                                                                                                                                                                                                                                                        |
| `test_identity_is_derived_from_controls_and_actual_zip_bytes`                           | All existing identity fields recompute; no model-provided identity is consumed.                                                                                                                                                                                                                                         |
| `test_create_identity_observed_filename_equals_logical_filename`                        | Create does not generate a transport alias.                                                                                                                                                                                                                                                                             |
| `test_transport_alias_accepts_only_space_parenthesized_positive_integer`                | Existing identity grammar remains exact.                                                                                                                                                                                                                                                                                |
| `test_candidate_verifier_rejects_fuzzy_name_wrong_root_repack_and_hash_mismatch`        | Any incompatible identity component is rejected.                                                                                                                                                                                                                                                                        |
| `test_issue_candidate_profile_accepts_exact_generated_zip`                              | Named profile returns `pass`.                                                                                                                                                                                                                                                                                           |
| `test_issue_candidate_profile_rejects_tree_input`                                       | Formal Candidate profile is ZIP-only.                                                                                                                                                                                                                                                                                   |
| `test_issue_candidate_profile_rejects_unsafe_archive_class`                             | Parameterize traversal, absolute, drive, backslash, NUL, hidden, directory record, symlink, special/hard-link mode, executable, encryption, nested archive, binary, CRC, exact duplicate, case-fold collision, Unicode-NFC collision, wrong root, inventory mismatch, checksum mismatch, entry/total/count/ratio limit. |
| `test_issue_candidate_profile_findings_do_not_echo_sensitive_values_or_absolute_paths`  | Details contain safe finding categories only.                                                                                                                                                                                                                                                                           |
| `test_generic_review_pack_input_default_characterization_is_unchanged`                  | Existing no-profile positive and representative negatives retain the same status, findings, root, metadata, tree fallback, and digest.                                                                                                                                                                                  |
| `test_zip_bytes_are_reproducible_for_fixed_inputs_and_timestamp`                        | Two builds are byte-identical.                                                                                                                                                                                                                                                                                          |
| `test_zip_entry_order_permissions_timestamp_comments_and_extra_fields_are_fixed`        | Deterministic archive metadata.                                                                                                                                                                                                                                                                                         |
| `test_output_guard_requires_existing_external_non_symlink_directory`                    | Unsafe destination classes fail before backend invocation.                                                                                                                                                                                                                                                              |
| `test_atomic_publication_never_exposes_partial_final_file`                              | Barrier before no-replace move sees no final; after success sees complete ZIP.                                                                                                                                                                                                                                          |
| `test_atomic_publication_collision_preserves_existing_bytes`                            | Existing file hash unchanged and no alternate `(N)` name.                                                                                                                                                                                                                                                               |
| `test_build_and_validation_faults_leave_final_filename_absent`                          | Parameterized faults through parser, controls, ZIP write, profile, digest, and pre-publication checks.                                                                                                                                                                                                                  |
| `test_unsupported_atomic_publication_leaves_final_absent`                               | No copy/overwrite fallback.                                                                                                                                                                                                                                                                                             |
| `test_create_maps_s02_nonpass_without_candidate_work`                                   | Existing status/reason preserved; parser/build calls `0`.                                                                                                                                                                                                                                                               |
| `test_create_rejects_transient_payload_digest_mismatch`                                 | `planner_response_rejected`, final count `0`.                                                                                                                                                                                                                                                                           |
| `test_create_returns_ok_candidate_created_only_after_atomic_publication`                | Success cannot be emitted before the final move.                                                                                                                                                                                                                                                                        |
| `test_create_success_output_has_only_safe_keys`                                         | Only `candidate_identity` and `zip_byte_count`; no host-private path or raw payload.                                                                                                                                                                                                                                    |
| `test_fake_transport_to_candidate_preserves_source_and_payload_binding`                 | S02→S03 integration produces a verifiable ZIP.                                                                                                                                                                                                                                                                          |
| `test_fake_backend_partial_or_fourth_document_leaves_final_zero`                        | Integration negative path.                                                                                                                                                                                                                                                                                              |
| Existing S01 result/identity tests                                                      | Named identity fields, alias behavior, and `ok` versus `ready` remain unchanged.                                                                                                                                                                                                                                        |
| Existing S02 transport tests                                                            | Git preflight, payload non-serialization, backend classification, and source evidence remain unchanged.                                                                                                                                                                                                                 |

The matrix directly covers every canonical S03 test class, including generic authoring-pack characterization, aliases, dynamic/static placeholders, resource safety, and independent Candidate verification.

---

## 6. Verification commands

### Red-first focused lane

Run after test stubs are written and confirm expected Red failures:

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/authoring_pack/test_zip_contract_profiles.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

### S03 Green lane

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/authoring_pack/test_zip_contract_profiles.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

### S01/S02/Core and shared regression lane

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py
```

### Static checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/authoring_pack/test_zip_contract_profiles.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/integration/test_issue_planning_chatgpt_transport.py

uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
```

### Repository validation and allowlist audit

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
git diff --name-only 530cca24943892dd440ca67823a9d68dfc46763d
```

The final changed-path set must be a subset of the exact Section 4 allowlist.

Do not run the full repository suite merely to close S03; the Plan assigns focused verification to S01–S05 and broader regression/projection work to later milestones.

---

## 7. Forbidden changes

The dev-coder must not:

* alter the public command family or any CLI argument;
* modify `cli/bootstrap.py` or wire `UseCases.planning_create`;
* modify `commands/issue_planning.py` or presentation output;
* change any named field in `PlanningContext`, `PlanningSourceEvidence`, `IssueCandidateIdentity`, Review identity, Human decision, or command result;
* change the existing identity canonical JSON bytes or closed `(N)` alias grammar;
* modify `transport-output-contract.md` or `reviewer-prompt.md`;
* add a fourth document, optional artifact, archive directory entry, or arbitrary root;
* accept model-generated MANIFEST, baseline, placeholder map, checksums, identity, timestamp, Candidate ID, or ZIP;
* store external ZIP SHA inside the ZIP;
* generate UUID/random Candidate IDs;
* auto-increment a filename, add `(N)`, retry under a new name, overwrite, or delete a prior Candidate;
* use `os.replace`, copy-to-final, or any publication fallback that exposes partial bytes or overwrites;
* add a general YAML dependency or open-ended YAML parser;
* create a second generic ZIP engine or safe extractor;
* change generic authoring-pack defaults, root, metadata, tree fallback, result semantics, or existing callers;
* call or modify `pack_stage.py` for S03;
* overload the Initiative/Epic `candidate_contract.py`;
* import private publication helpers from `binary_artifact_publisher.py`;
* token-scan static documents;
* emit dynamic placeholders during normal create;
* serialize the raw Planner payload, Prompt, transcript, stderr, secret match, absolute output path, or temporary path;
* modify canonical `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`, or Issue artifacts;
* modify root dogfood projection files;
* implement S04 Review/revision, S05 Human Gate/apply, rollback, validation/sync, commit, push, S06 projection, or live dogfood;
* create a persistent registry, database, custom Git ref, recovery graph, or new generic workflow abstraction;
* expand the write allowlist after encountering an implementation inconvenience.

---

## 8. Stop conditions

Stop S03 implementation and report the exact condition if:

1. Branch HEAD is no longer `530cca24943892dd440ca67823a9d68dfc46763d`.
2. Any implementation requires a path outside the Section 4 allowlist.
3. The current canonical front-matter baseline cannot be parsed using the closed schema or the three documents disagree on shared identity metadata.
4. The exact three-document grammar cannot be enforced without changing the outer transport contract.
5. A public CLI, command registry, presentation, `UseCases`, or bootstrap change becomes necessary.
6. The named profile cannot preserve the current no-argument generic ZIP behavior.
7. S03 would require modifying the existing named identity fields or success pair.
8. The platform lacks an atomic no-replace move and implementation would otherwise need overwrite or copy fallback.
9. Any handled failure can leave the logical final filename.
10. Independent reconstruction of baseline, manifest, checksums, identity, or ZIP SHA cannot be demonstrated by tests.
11. Normal create would need a dynamic placeholder or optional Candidate file.
12. A raw payload, secret value, private path, or transcript would enter serialized output or diagnostics.
13. Satisfying a test requires S04+, canonical adoption, Git mutation, projection, or live backend execution.
14. Generic authoring-pack characterization changes for any existing fixture.
15. Any test or implementation silently sorts malformed identity arrays, rewrites semantic body content, or repairs malformed model output instead of rejecting it.

---

## 9. Copy-ready `dev-coder` instruction

```text
Role: dev-coder
Task: implement iss-00334 S03 — Create and Candidate Packaging
Repository: chemitaro/spec-dock
Branch: iss-00334-implement-chatgpt-issue-planning-workflow
Required starting HEAD: 530cca24943892dd440ca67823a9d68dfc46763d

This is a bounded implementation task. Implement the replacement S03 work packet exactly. Do not review or amend the canonical specification.

Exact write allowlist:

1. src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
2. src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
3. src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
4. src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
5. src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
6. tests/unit/application/test_issue_planning.py
7. tests/unit/application/test_issue_planning_prompt.py
8. tests/unit/authoring_pack/test_zip_contract_profiles.py
9. tests/unit/domain/test_issue_planning_candidate.py
10. tests/unit/infra/test_issue_planning_candidate.py
11. tests/integration/test_issue_planning_chatgpt_transport.py

No other path may change.

Implementation order:

A. Write Red tests first for:
- exact three-document grammar;
- closed current-Japanese front matter and Runtime normalization;
- substantive completeness;
- canonical control JSON;
- SOURCE-BASELINE, MANIFEST, CHECKSUMS, placeholder map;
- deterministic v1 names and ZIP bytes;
- detached identity and external ZIP SHA;
- closed transport aliases;
- named ZIP profile security classes;
- generic authoring-pack default characterization;
- safe external output, collision, cleanup, and atomic no-replace publication;
- S02→S03 integration and safe result output.

B. Add domain/issue_planning_candidate.py:
- pure payload parser;
- current-front-matter baseline parser;
- Runtime front-matter renderer;
- completeness oracle;
- CanonicalControlJsonV1;
- exact v1 control schemas;
- placeholder oracle;
- cross-file verifier;
- detached IssueCandidateIdentity derivation.

C. Extend domain/authoring_pack/zip_contract.py:
- optional immutable named profile;
- no-argument review_pack_input behavior unchanged;
- one Issue Candidate ZIP profile path using the existing archive traversal/safety engine;
- strict ZIP-only inventory, collision, special-file, CRC, checksum, UTF-8, resource, and cross-file checks.

D. Add infra/issue_planning_candidate.py:
- external output guard;
- same-filesystem owned temporary build;
- deterministic ZIP writer;
- profile validation;
- staged SHA/size;
- platform atomic no-replace move using Linux RENAME_NOREPLACE or macOS RENAME_EXCL;
- no overwrite/copy fallback;
- cleanup before publication on every failure.

E. Extend application/issue_planning.py:
- validate current canonical front matter before backend call;
- validate output directory before backend call;
- invoke existing run_issue_planning_transport exactly once;
- require pass/transport_received plus source evidence and exact payload digest;
- parse, normalize, build, validate, derive identity, publish;
- return only ok/candidate_created after atomic publication;
- preserve S02 status/reason on S02 nonpass;
- use only the closed S03 failure mapping;
- never serialize transient_payload or an absolute path.

F. Update planner-prompt.md with the exact inner document markers and no-output-outside-frame rule. Do not modify the outer transport contract.

G. Run:

uv run pytest \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/authoring_pack/test_zip_contract_profiles.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/integration/test_issue_planning_chatgpt_transport.py

uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py

Run ruff and mypy on the allowlisted Python paths, then:

./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
git diff --name-only 530cca24943892dd440ca67823a9d68dfc46763d

Stop rather than expand scope if:
- HEAD differs;
- a non-allowlisted path appears;
- bootstrap/public CLI wiring is needed;
- generic authoring-pack defaults would change;
- atomic no-replace publication is unavailable and would require overwrite/copy fallback;
- a handled failure could leave the final filename;
- S04+ behavior is required;
- any raw transcript, secret, credential, or host-private absolute path would be serialized.

Do not modify canonical docs, report, assurance, artifacts, root dogfood projection, Git state, remote state, or later-step code.
```
