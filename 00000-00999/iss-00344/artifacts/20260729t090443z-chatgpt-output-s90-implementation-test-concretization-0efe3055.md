# Issue 344 S90 Documentation-Test Recommendation

## Recommendation

Proceed with **one aggregate, source-level semantic assertion** named:

```text
TestInitUpdate::test_shipped_docs_describe_workbench_readme_boundary
```

Place it immediately after the existing canonical Workbench README asset test in `tests/unit/infra/test_init_update.py`. The test should:

1. Read the four provider documents directly.
2. Read the canonical root `.workbench/README.md` only as a reference/precondition.
3. Check a small shared vocabulary across all four documents.
4. Apply role-specific assertions to each document.
5. Aggregate all missing or deprecated semantics into one diagnostic failure.
6. Avoid Markdown parsing, temporary installation, runtime invocation, or exact-sentence snapshots.

This matches the approved S90 sequence: `dev-coder` adds only the semantic assertion and records a valid Red; `doc-writer` then changes only the four provider documents to make it Green. The canonical README remains read-only, and any need to change it is an amendment trigger.

The GitHub connector resolved commit `0efe3055860706a9f4b68ae1ddaa767371079b03`, and the branch comparison reported that commit and `iss-00344-workbench-shell-scaffolding` as identical.

No repository patch or canonical README modification was made.

## Current-state findings

The active requirement defines nine canonical guidance elements: temporary/worktree-local/disposable/non-canonical status, direct-README-only tracking, ignored payload, explicit repo-local import, node-only manual copy, Git-ignore security limits, evidence-only authority, linked-worktree checkout, and prohibition on treating Workbench content as canonical input. It separately requires optional presence, no backfill, opaque source-wins copying, and no hook/watch/sync/copy-back.

The current canonical root README already expresses the intended operator boundary: only its direct `README.md` is tracking-eligible; other entries are ignored; Git ignore is not a security boundary; tracked README files arrive through normal checkout; node payload transfer is an explicit one-shot helper; root is excluded; and there is no automatic synchronization.

The existing test `test_workbench_readme_assets_are_byte_identical_and_complete` already verifies the four canonical assets are byte-identical and checks representative canonical fragments. The S90 test should therefore **not** repeat byte parity, line endings, package inventory, or canonical fragment completeness.

| Document                     | Current finding                                                                                                                                                                                                                                                                       | S90 implication                                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `docs/README.md`             | Describes the Workbench as wholly “Git 管理外,” even though the direct README is now tracked. It documents the existing specialized `artifact import chatgpt-output`, but not the planned generic file import or the #345/#346 boundary.                                                 | Replace the obsolete whole-directory Git statement and add the compact current boundary plus delivery-status note.        |
| `docs/guide.md`              | Calls the Workbench an experimental, wholly Git-untracked area. Its copy and evidence discussion is useful, but it lacks the new tracked README shell, fresh/future generation, security statement, and explicit #345/#346 availability boundary.                                     | Correct the conceptual model while retaining the existing specialized ChatGPT-output lane.                                |
| `docs/reference_worktree.md` | The one-shot, source-wins, destination-only, root-excluded, no-sync mechanics are already substantially correct. It does not say that tracked README files arrive through checkout, does not distinguish README from ignored payload, and does not explain security/import authority. | Preserve the existing operational mechanics and add only the missing README/security/authority boundary.                  |
| `templates/README.md`        | Says new nodes do not receive a template-derived `README.md`. Without qualification, that now conflicts with generation of `.workbench/README.md` for future nodes.                                                                                                                   | Narrow the statement to the node-root README and explicitly describe the Workbench README exception and no-backfill rule. |

The requirement expressly assigns generic file import to Issue #345 and candidate-wheel consumer E2E, integrated dogfood, opt-in full regression, and residual Epic delivery to Issue #346.

## Semantic assertion design

The test should inspect provider source assets rather than initializing a temporary repository. S03 already owns package/distribution coverage, while S95 owns checked-in dogfood projection. S90 is a static operator-document contract. The test file already uses direct provider-document reads for comparable documentation assertions.

An implementation-ready method shape is:

```python
def test_shipped_docs_describe_workbench_readme_boundary(self) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    provider_root = repo_root / "src" / "spec_dock" / "assets" / "spec_dock"

    doc_paths = (
        "docs/README.md",
        "docs/guide.md",
        "docs/reference_worktree.md",
        "templates/README.md",
    )
    texts = {
        relative_path: (provider_root / relative_path).read_text(encoding="utf-8")
        for relative_path in doc_paths
    }
    canonical_text = (
        provider_root
        / "templates"
        / "root"
        / ".workbench"
        / "README.md"
    ).read_text(encoding="utf-8")

    failures: list[str] = []

    def matches(
        text: str,
        alternatives: tuple[tuple[str, ...], ...],
    ) -> bool:
        return any(
            all(fragment in text for fragment in alternative)
            for alternative in alternatives
        )

    def require(
        path: str,
        concept: str,
        alternatives: tuple[tuple[str, ...], ...],
    ) -> None:
        if not matches(texts[path], alternatives):
            failures.append(f"{path}: missing {concept}")

    def forbid(path: str, concept: str, fragment: str) -> None:
        if fragment in texts[path]:
            failures.append(f"{path}: deprecated {concept}: {fragment!r}")

    artifact_import_command = (
        "./spec-dock/scripts/spec-dock artifact import file ..."
    )
    workbench_copy_command = (
        "./spec-dock/scripts/spec-dock workbench copy "
        "--scope <full-id> --to <linked-worktree>"
    )

    # Canonical README is a read-only S90 precondition, not an S90 edit target.
    for fragment in (artifact_import_command, workbench_copy_command):
        assert fragment in canonical_text, (
            "canonical Workbench README changed; return to planning instead "
            f"of repairing shipped docs around missing fragment: {fragment!r}"
        )

    # Minimal common identity and Git boundary in every shipped document.
    for path in doc_paths:
        require(path, "optional status", (("optional",),))
        require(path, "temporary status", (("temporary",), ("一時",)))
        require(path, "worktree-local status", (("worktree-local",),))
        require(path, "disposable status", (("disposable",), ("破棄可能",)))
        require(path, "non-canonical status", (("non-canonical",),))
        require(
            path,
            "direct README tracked / other payload ignored boundary",
            (
                (
                    ".workbench/README.md",
                    "README-only tracking",
                    "ignored payload",
                ),
                (
                    ".workbench/README.md",
                    "direct",
                    "Git tracking",
                    "ignore",
                ),
            ),
        )

    # Shell generation and compatibility belong in the overview/guide/template docs.
    for path in ("docs/README.md", "docs/guide.md", "templates/README.md"):
        require(
            path,
            "fresh root, future nodes, optional presence, and no-backfill",
            (
                (
                    "fresh root",
                    "future",
                    "Initiative",
                    "Epic",
                    "Issue",
                    "no-backfill",
                ),
                (
                    "fresh",
                    "future",
                    "Initiative",
                    "Epic",
                    "Issue",
                    "existing",
                    "追加しない",
                ),
            ),
        )

    # Security and authority must be visible on operator-facing surfaces.
    for path in (
        "docs/README.md",
        "docs/guide.md",
        "docs/reference_worktree.md",
    ):
        require(
            path,
            "Git ignore is not a security boundary",
            (("Git ignore", "security boundary"),),
        )
        require(
            path,
            "read/import authorization is evidence-only, not canonical",
            (("read / import", "evidence-only", "canonical"),),
        )

    # Worktree reference owns detailed checkout/copy mechanics.
    require(
        "docs/reference_worktree.md",
        "tracked README checkout versus manual ignored-payload copy",
        (("linked worktree", "tracked", "README.md", "Git checkout"),),
    )
    require(
        "docs/reference_worktree.md",
        "node-only one-shot copy with root excluded",
        (
            (
                "Initiative",
                "Epic",
                "Issue",
                "ignored payload",
                "one-shot",
                "root",
                "対象外",
            ),
        ),
    )
    require(
        "docs/reference_worktree.md",
        "opaque source-wins behavior preserving destination-only entries",
        (("source-wins", "destination-only", "README", "filter"),),
    )
    require(
        "docs/reference_worktree.md",
        "no hook/watch/sync/copy-back",
        (("automatic hook", "watch", "sync", "copy-back"),),
    )

    # The docs entrance owns the transitional sibling-Issue availability note.
    require(
        "docs/README.md",
        "Issue #345 planned and unimplemented generic file import",
        (
            (
                artifact_import_command,
                "Issue #345",
                "planned",
                "unimplemented",
            ),
            (
                artifact_import_command,
                "iss-00345",
                "計画",
                "未実装",
            ),
        ),
    )
    require(
        "docs/README.md",
        "repo-local generic import is not a global-installer dispatch",
        (
            ("repo-local runtime", "global installer", "not available"),
            ("repo-local runtime", "global installer", "dispatch はない"),
            ("repo-local runtime", "global installer", "未提供"),
        ),
    )
    require(
        "docs/README.md",
        "Issue #346 consumer E2E and full-regression handoff",
        (
            (
                "Issue #346",
                "consumer E2E",
                "full regression",
                "deferred",
            ),
            (
                "iss-00346",
                "consumer E2E",
                "full regression",
                "責務",
            ),
        ),
    )
    require(
        "docs/reference_worktree.md",
        "root durable-file route remains planned under Issue #345",
        (
            (artifact_import_command, "Issue #345", "unimplemented"),
            (artifact_import_command, "iss-00345", "未実装"),
        ),
    )

    # Context-specific migration guards, not a global ban on these words.
    forbid(
        "docs/README.md",
        "whole Workbench described as Git-untracked",
        "Workbench は experimental、Git 管理外",
    )
    forbid(
        "docs/guide.md",
        "whole Workbench described as Git-untracked",
        "Git 管理外の disposable な一時作業場",
    )
    forbid(
        "templates/README.md",
        "ambiguous claim that future nodes receive no README",
        "新規ノードにはテンプレ由来の `README.md` は生成されません。",
    )

    assert not failures, (
        "shipped Workbench documentation boundary mismatch:\n- "
        + "\n- ".join(failures)
    )
```

The important design choices are:

* **One test, one failure report:** all four documents can be repaired from one Red output.
* **Stable concepts, not prose snapshots:** the assertions use normative terms and alternative token groups rather than exact paragraphs.
* **Shared and role-specific checks:** the test does not require every document to duplicate all implementation details.
* **Canonical README as precondition only:** a missing canonical anchor causes an explicit return-to-planning failure rather than inviting S90 to edit it.
* **No parser or dependency:** plain text checks match the repository’s existing documentation-test style.

## Expected Red

I did not execute the test. Static inspection indicates that the proposed test would be validly Red before any documentation edit for documentation-specific reasons:

* All four documents lack a consistent direct `.workbench/README.md` versus ignored-payload summary.
* `docs/README.md` and `docs/guide.md` still characterize the whole Workbench as Git-untracked.
* `docs/reference_worktree.md` has the correct existing copy mechanics but lacks normal README checkout, README-filter avoidance, security, and import-authority language.
* `templates/README.md` contains the ambiguous no-README statement.
* None of the four currently carries the required transitional statement that generic `artifact import file` is #345-owned and unimplemented, while candidate-wheel consumer E2E and opt-in full regression remain #346-owned.
* The canonical README precondition should pass because both exact repo-local commands are present.

The Red is invalid if it arises from a missing path, decoding failure, altered canonical README, runtime behavior, or a test construction error.

## Per-document minimal delta

| Document                     | Minimal change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `docs/README.md`             | Replace the current Workbench high-frequency bullets with a compact operator summary: optional/temporary/worktree-local/disposable/non-canonical; fresh root and future nodes receive direct `.workbench/README.md`; existing scopes receive no backfill; the direct README is tracked and other payload is ignored; tracked README arrives by checkout; only node payload uses manual one-shot copy; root is excluded; no hook/watch/sync/copy-back; Git ignore is not security; read/import is evidence-only. Keep the existing `artifact import chatgpt-output` command as the implemented specialized Markdown lane. Add the exact generic file-import invocation with an explicit **Issue #345 planned/unimplemented, repo-local only, no global-installer dispatch** qualifier. Add one adjacent sentence assigning candidate-wheel consumer E2E and opt-in full regression to Issue #346. |
| `docs/guide.md`              | Replace the obsolete conceptual paragraphs at the current Workbench section. Preserve semantic opacity, disposability, source-wins copying, and evidence-only adoption. Add fresh/future shell generation, optional/no-backfill status, direct README tracking versus ignored payload, linked-worktree checkout, security, and read/import authority. Distinguish the implemented `chatgpt-output` import from the planned generic file import. A brief #345/#346 availability sentence is sufficient; the detailed handoff can remain in `docs/README.md`.                                                                                                                                                                                                                                                                                                                                      |
| `docs/reference_worktree.md` | Preserve the existing operational copy description. Prepend that the tracked direct README arrives in every linked worktree through normal checkout, while ignored payload does not. State that manual copy is intended for node-scoped ignored payload, but remains an opaque whole-tree source-wins operation: no README-specific filter and destination-only entries remain. Keep root excluded. Add explicit no-hook/watch/sync/copy-back language, the Git-ignore security warning, and evidence-only/read-import authority. For the root durable-file route, show the exact repo-local generic command and mark it #345-owned and currently unimplemented.                                                                                                                                                                                                                                 |
| `templates/README.md`        | Replace the ambiguous “new nodes receive no README” sentence with: ordinary node-root `README.md` is not generated, but fresh root and future Initiative/Epic/Issue templates do generate direct `.workbench/README.md`. State that existing scopes are not backfilled, presence remains optional, the direct README is tracked, and other Workbench payload is ignored. Link to `docs/guide.md` and `docs/reference_worktree.md` for detailed copy/security/authority rules instead of duplicating them.                                                                                                                                                                                                                                                                                                                                                                                        |

## Shared versus role-specific guidance

The **shared minimum**, repeated compactly in all four documents, should be:

> Workbench is optional, temporary, worktree-local, disposable, and non-canonical. The direct `.workbench/README.md` is the README-only tracking surface; other Workbench payload is ignored.

That common sentence prevents each document from reconstructing a different Git or authority model.

Role ownership should remain distinct:

| Surface                      | Role-specific responsibility                                                                                                                               |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/README.md`             | Operator entrypoint, current availability, exact commands, and #345/#346 delivery boundary.                                                                |
| `docs/guide.md`              | Conceptual lifecycle: shell generation, optional/no-backfill status, semantic opacity, authority, and evidence adoption.                                   |
| `docs/reference_worktree.md` | Checkout versus copy, node/root distinction, one-shot source-wins behavior, destination-only preservation, and automation exclusions.                      |
| `templates/README.md`        | Which templates generate the shell, future-node behavior, existing-scope no-backfill, and distinction between node-root README and `.workbench/README.md`. |

This division satisfies the requirement that the shipped docs be consistent without forcing four near-identical policy essays. The active requirement calls for consistent shell, Git, copy, security, authority, and Issue-boundary semantics, not identical document bodies.

## Deprecated wording disposition

| Existing wording                                           | Disposition                                                                                                                                                                                                                                                          |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Whole Workbench described as `Git 管理外`                     | **Replace.** It is now false because the direct `.workbench/README.md` is tracking-eligible. “README以外の payload は ignored” remains valid.                                                                                                                            |
| `Workbench（experimental）` or an experimental section label | **Do not globally test-ban it.** `experimental` is a maturity label, not itself a semantic contradiction. Where it appears inside the obsolete “experimental and wholly Git-untracked” sentence, rewrite the whole sentence around the approved `optional` boundary. |
| `新規ノードにはテンプレ由来の README.md は生成されません`                        | **Narrow, do not simply delete.** Preserve the original node-root README meaning and state the `.workbench/README.md` exception.                                                                                                                                     |
| Root date-bucket guidance                                  | **Non-normative.** It may remain as an optional local organization example, but it must not replace the durable-file route, imply root bulk copy, or appear as an authority rule. Do not make it a test anchor.                                                      |
| Existing `artifact import chatgpt-output` documentation    | **Retain.** It is a distinct implemented specialized Markdown lane and must not be renamed to or conflated with the #345 generic file import.                                                                                                                        |
| Generic `artifact import file` wording                     | **Add with an availability qualifier.** Use the exact repo-local invocation and state that #345 owns the planned/unimplemented implementation; do not imply global-installer dispatch.                                                                               |
| Candidate-wheel consumer E2E/full regression               | **Keep explicitly deferred to #346.** S90 documentation and its static semantic test do not implement or execute those lanes.                                                                                                                                        |

## Test-lane handoff

The `dev-coder` handoff should be bounded as follows:

* **Only allowed file:** `tests/unit/infra/test_init_update.py`.
* **Only intended addition:** the exact test method named in the plan; no reusable parser, no production helper, no docs edits, no canonical README edit.
* **Placement:** immediately after `test_workbench_readme_assets_are_byte_identical_and_complete`.
* **Required Red command:**

```bash
uv run pytest \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_shipped_docs_describe_workbench_readme_boundary
```

* **Required Red evidence:** aggregated diagnostics identify current documentation semantics, while the canonical README preconditions pass.
* **Reviewer focus:** requirement traceability, role-specific proportionality, absence of exact-prose overconstraint, exact four target paths, and a Red caused only by current docs.

The plan requires this test-only Red to receive a fresh `code-reviewer` pass before the docs lane starts. The `dev-coder` must not edit the four docs, and the `doc-writer` must not edit the Python test.

## Docs-lane handoff

The `doc-writer` handoff should allow only:

```text
src/spec_dock/assets/spec_dock/docs/README.md
src/spec_dock/assets/spec_dock/docs/guide.md
src/spec_dock/assets/spec_dock/docs/reference_worktree.md
src/spec_dock/assets/spec_dock/templates/README.md
```

The writer should receive:

* The reviewed Red test and its complete diagnostics.
* The active requirement’s nine guidance elements.
* The canonical root README as a read-only terminology reference.
* The per-document role allocation above.
* Explicit instructions to retain the specialized `artifact import chatgpt-output` lane and distinguish it from generic import.
* Explicit instructions not to edit runtime code, package configuration, tests, Issue specifications, dogfood mirrors, or any of the four canonical Workbench README assets.

The docs lane is complete when the exact semantic assertion becomes Green, the four-document diff is locally minimal, deprecated wording has a recorded context-specific disposition, and a fresh `spec-reviewer` confirms authority, security, root/node copy, and sibling-Issue boundaries.

## Verification and stop conditions

Run the focused checks:

```bash
uv run pytest \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_shipped_docs_describe_workbench_readme_boundary

uv run pytest \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete

git diff --check
git status --short
```

Verify the S90 changed-path boundary:

```bash
git diff --name-only <s90-base-sha>...HEAD
```

Verify that no canonical README changed:

```bash
git diff --exit-code <s90-base-sha>...HEAD -- \
  src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md \
  src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md \
  src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md \
  src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md
```

Stop and return to planning or the owning step when any of the following occurs:

* The new test is Green before docs changes.
* Red is caused by missing files, decoding, path resolution, or canonical README drift rather than current documentation.
* Passing the test would require canonical README, runtime, installer, package, copy, or Git behavior changes.
* A proposed docs edit implies root `workbench copy`, automatic hooks/watch/sync/copy-back, README-specific copy filtering, or backfill.
* Generic file import must be described as implemented or globally dispatchable.
* #345/#346 ownership must change.
* The test requires identical wording in all documents rather than shared semantics.
* The changed-path list contains anything outside the test, four provider docs, and the separately owned Issue evidence.
* Deprecated wording cannot be classified contextually.

These are consistent with the active S90 stop conditions and step gate.

## Assumptions and uncertainty

* The recommendation is based on the GitHub connector’s exact commit view; no local checkout or test execution was performed.
* I did not independently verify that S03 has received formal Step/Milestone Result Approval. The active plan prohibits beginning S90 implementation, review, or commit before that approval.
* There is a deliberate transitional tension: the canonical README uses imperative wording for `artifact import file`, while the active contract says #345 still owns its implementation. Because the plan makes the canonical README read-only in S90, the proportional response is to qualify current availability in the four shipped docs and keep the test’s #345 assertion outside the canonical precondition. If a reviewer judges the standalone canonical README wording unacceptable, S90 must stop for a planning amendment rather than edit it.
* Hardcoding #345/#346 status is intentionally transitional. Those owning Issues should update the docs and this assertion when their availability boundary changes.
* The attached `設計判断と提案.txt` concerns an unrelated exception/failure taxonomy and was not used as evidence for this repository-specific recommendation. 
