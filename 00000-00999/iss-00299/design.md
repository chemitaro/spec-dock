---
種別: 設計書（Issue）
ID: "iss-00299"
タイトル: "Prompt Pack Constraints"
関連GitHub: ["#299"]
状態: "planning-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00299 Prompt Pack Constraints — 設計

## 0. 設計結論

`authoring pack prepare` は、iss-00298 の preflight evidence を受け取り、ChatGPT evidence lane に渡す deterministic prompt pack tree を生成する installed runtime command として実装する。

責務は prompt pack input generation と safe output constraints guidance に限定する。backend invocation、ZIP review/stage、candidate/adoption validation、canonical adoption、`.assurance.json` mutation、reviewer pass / execution-ready / PR-ready / PR delivery claim は実装しない。

## 1. Architecture boundary

採用する layer:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  commands/
    authoring.py
  application/
    authoring_pack/
      pack_prepare.py
      github_sync_preflight.py          # existing from iss-00298, read as input contract
  domain/
    authoring_pack/
      prompt_pack_contract.py           # new or equivalent
      safe_output_constraints.py        # new or equivalent
      source_manifest.py                # existing/reused
      zip_contract.py                   # new or extended guidance-only contract
      preflight_contract.py             # existing/reused
  presentation/
    authoring_pack/
      pack_prepare_renderer.py          # new or equivalent
      diagnostics.py                    # extended if needed
      cli_json.py                       # if existing convention exists
      cli_text.py                       # if existing convention exists
```

Dogfood mirror:

```text
spec-dock/scripts/spec_dock_runtime/...
```

Compatibility / helper surface:

```text
src/spec_dock/assets/spec_dock/scripts/authoring-pack/prepare_chatgpt_authoring_pack.py
spec-dock/scripts/authoring-pack/prepare_chatgpt_authoring_pack.py
```

`src/spec_dock/assets/spec_dock/...` を source of truth とし、`spec-dock/...` は dogfood validation mirror として更新する。

## 2. CLI design

### 2.1 Command

```bash
./spec-dock/scripts/spec-dock authoring pack prepare \
  --preflight <preflight.json> \
  --output-dir <path> \
  [--format text|json]
```

追加可能な明示 input:

```bash
  [--mode initiative|epic|issue|selected-skeleton]
  [--source-manifest <source-manifest.json>]
  [--stale-if <stale-if.json>]
```

原則:

* `--force` は追加しない。
* stale / blocked / rejected を bypass する flag は追加しない。
* `local-context` は preflight evidence の `evidence_mode` と provenance で表現する。

### 2.2 Output status

| status     | 意味                                                   |     exit |
| ---------- | ---------------------------------------------------- | -------: |
| `pass`     | command-local prompt pack generation pass            |        0 |
| `fail`     | input schema / required metadata failure             | non-zero |
| `blocked`  | required observation / provenance unavailable        | non-zero |
| `stale`    | preflight/source hash/profile-like snapshot mismatch | non-zero |
| `rejected` | unsafe path / forbidden claim / unsafe output target | non-zero |

`pass` は adoption、reviewer pass、execution-ready、PR-ready を意味しない。

## 3. Domain model

### 3.1 PromptPackPrepareRequest

```python
@dataclass(frozen=True)
class PromptPackPrepareRequest:
    preflight_path: Path
    output_dir: Path
    output_format: Literal["text", "json"] = "text"
    mode: Literal["initiative", "epic", "issue", "selected-skeleton"] | None = None
    source_manifest_path: Path | None = None
    stale_if_path: Path | None = None
```

### 3.2 PromptPackPrepareResult

```python
@dataclass(frozen=True)
class PromptPackPrepareResult:
    status: Literal["pass", "fail", "blocked", "stale", "rejected"]
    authority: Literal["evidence_only"]
    adoption_status: Literal["unreviewed"]
    bundle_generation_not_promotion: bool
    evidence_mode: Literal["github-synced", "local-context"]
    sync_state: str
    github_sync: str
    output_root: str
    output_files: tuple[str, ...]
    source_manifest_hash: str | None
    blockers: tuple[str, ...]
    remediation: tuple[str, ...]
```

### 3.3 AuthorityBoundary

固定値:

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

### 3.4 SafeOutputConstraints

必須 field:

```json
{
  "expected_zip_root": "specdock-authoring-pack/",
  "required_metadata": [
    "manifest.json",
    "provenance.json",
    "source-manifest.json",
    "stale-if.json",
    "safe-output-constraints.md",
    "adoption/adoption-map.json",
    "adoption/eal-candidates.json"
  ],
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true,
  "forbidden_authority_claims": [
    "canonical adoption",
    ".assurance.json mutation",
    "authorized_profile decision",
    "reviewer pass",
    "execution-ready",
    "PR-ready",
    "PR delivery"
  ],
  "forbidden_payloads": [
    "raw transcript",
    "secret",
    "credential",
    "private key",
    "host-local absolute path",
    "path traversal",
    "hidden path",
    "nested archive",
    "binary",
    "executable",
    "symlink"
  ]
}
```

### 3.5 Provenance contract

`github-synced`:

```json
{
  "evidence_mode": "github-synced",
  "sync_state": "synced",
  "github_sync": "verified",
  "requested_ref": "...",
  "effective_ref": "...",
  "local_head": "...",
  "remote_head": "...",
  "source_manifest_hash": "..."
}
```

`local-context`:

```json
{
  "evidence_mode": "local-context",
  "sync_state": "local_context",
  "github_sync": "not_verified",
  "provided_context_paths": ["..."],
  "diff_summary": "...",
  "unsynced_reason": "...",
  "adoption_requires": "explicit_eal_disposition"
}
```

## 4. Generated prompt pack tree

Runtime-generated prompt pack root is an output directory selected by caller. Inside it:

```text
<output-dir>/
  .specdock-authoring-pack
  manifest.json
  provenance.json
  source-manifest.json
  stale-if.json
  safe-output-constraints.md
  chatgpt-use-prompt.md
  expected-output-contract.md
  diagnostics.json              # only when non-pass or when explicit diagnostics enabled
```

The ChatGPT output requested by the prompt must use:

```text
specdock-authoring-pack/
  manifest.json
  provenance.json
  source-manifest.json
  stale-if.json
  safe-output-constraints.md
  adoption/adoption-map.json
  adoption/eal-candidates.json
  summaries/
  candidates/
  drafts/
  selected-skeleton-fill/section-fills.json
```

This Issue only writes the prompt pack input. It does not validate or extract the ChatGPT ZIP/tree output.

## 5. Use case flow

```text
1. CLI parser builds PromptPackPrepareRequest.
2. Application service loads preflight JSON.
3. Domain validator checks required fields:
   - status
   - evidence_mode
   - sync_state
   - github_sync
   - authority
   - source_manifest_hash / source_hashes
4. If preflight status != pass:
   - return stale / blocked / fail result according to input status.
   - write diagnostics only if safe.
5. Validate output directory:
   - explicit path required.
   - path traversal / host-local unsafe forms rejected.
   - canonical docs target rejected.
6. Build PromptPackMetadata:
   - manifest
   - provenance
   - source manifest snapshot
   - stale-if
   - authority boundary
7. Render safe output constraints and ChatGPT prompt guidance.
8. Write deterministic files with stable JSON ordering.
9. Return JSON/text diagnostics.
```

## 6. Determinism strategy

* JSON uses sorted keys and stable separators.
* File ordering is fixed.
* Source path ordering is sorted or inherited from source manifest with stable normalization.
* Generated timestamps are either:

  * omitted from deterministic digest, or
  * supplied by input evidence, not wall-clock.
* Tests compare normalized payloads, not filesystem mtime.
* `__pycache__` / `.pyc` / `.pyo` are excluded by source manifest rules.

## 7. Safety / privacy design

Reject or omit:

* absolute paths;
* host-local paths such as drive-letter paths;
* path traversal;
* secret-looking paths;
* raw transcripts;
* credentials;
* tokens;
* private keys;
* hidden paths unless explicitly part of metadata contract and safe;
* symlinks or non-regular files;
* binary payloads.

Diagnostics may mention category names but must not echo secret values.

## 8. Existing behavior migration

Current deferred behavior:

```text
status=deferred
authority=evidence_only
next_issue=iss-00299
reason=not_implemented_in_this_issue
```

After this Issue:

* `authoring pack prepare` no longer uses deferred runner.
* Other authoring commands remain deferred/fail-closed:

  * backend invoke → iss-00300
  * pack review / stage → iss-00301
  * validators → later Issues
  * approval check → later Issue
* CLI help must not imply unsupported commands are implemented.

## 9. Provider / mirror update design

Implementation must update both:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...
spec-dock/scripts/spec_dock_runtime/...
```

If helper compatibility is retained, update both:

```text
src/spec_dock/assets/spec_dock/scripts/authoring-pack/prepare_chatgpt_authoring_pack.py
spec-dock/scripts/authoring-pack/prepare_chatgpt_authoring_pack.py
```

Provider-side files are implementation source. Mirror files are validation target.

## 10. Tests

### Unit / domain tests

* Valid `github-synced` preflight creates expected metadata.
* Valid `local-context` preflight records lower authority provenance.
* Missing required preflight field returns `fail`.
* Preflight `blocked` returns `blocked`.
* Preflight `stale` returns `stale`.
* Forbidden output target returns `rejected`.
* Forbidden authority claim in input contract returns `rejected`.
* Source manifest excludes cache files.

### CLI runtime tests

* `authoring pack prepare --help` lists implemented options.
* Valid fixture returns exit 0 and status `pass`.
* Non-pass fixture returns non-zero and stable diagnostics.
* `--force` is absent.
* Output avoids forbidden authority claims as achieved status.

### Dogfood mirror tests

* `spec-dock/scripts/spec-dock authoring pack prepare ...` works from mirror path.
* Provider and mirror source manifest paths are visible where expected.

## 11. Non-scope guardrails

The implementation must not introduce:

* `authoring backend invoke` implementation.
* ZIP central directory inspection.
* ZIP extraction.
* stage / dry-run diff.
* adoption-map validation.
* candidate validators.
* issue draft adoption validators.
* approval check.
* automatic canonical rewrite.
* `.assurance.json` write.
* PR creation.
* broad bypass flags.

## 12. Failure modes and status mapping

| Failure                            | status     | handling                            |
| ---------------------------------- | ---------- | ----------------------------------- |
| preflight JSON missing             | `fail`     | required input missing              |
| preflight JSON invalid             | `fail`     | schema diagnostics                  |
| preflight status blocked           | `blocked`  | no prompt pack pass                 |
| preflight status stale             | `stale`    | require regeneration/reconciliation |
| local-context provenance missing   | `blocked`  | require explicit provenance         |
| source hash mismatch               | `stale`    | preserve mismatch diagnostics       |
| output path unsafe                 | `rejected` | no write                            |
| canonical docs target              | `rejected` | no write                            |
| forbidden achieved authority claim | `rejected` | no prompt pack pass                 |
| filesystem write unavailable       | `blocked`  | diagnostics only if safe            |

## 13. Reviewer-facing invariants

* Prompt pack generation is evidence-only.
* Prompt pack guidance can list forbidden claims only as prohibitions.
* No generated output claims reviewer pass or readiness.
* `local-context` cannot silently become `github-synced`.
* Provider source and mirror behavior remain aligned.
* `pass` is command-local only.
