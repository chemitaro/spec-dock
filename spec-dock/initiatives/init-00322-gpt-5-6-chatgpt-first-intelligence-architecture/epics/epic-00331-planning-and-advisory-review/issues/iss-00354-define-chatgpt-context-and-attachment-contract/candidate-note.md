# Candidate Note

## Identity

| Field | Value |
|---|---|
| Logical filename | `iss-00354-oracle-017-compatibility-candidate-v2-20260804t043533z.zip` |
| Internal logical root | `iss-00354-oracle-017-compatibility-candidate-v2-20260804t043533z/` |
| Candidate ID | `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` |
| Candidate version | `v2` / complete replacement of immutable v1 |
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Source HEAD | `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` |
| Generated UTC | `2026-08-04T04:35:33Z` |
| Generated JST | `2026-08-04T13:35:33+09:00` |
| Authority | `historical_immutable_evidence` (not canonical) |
| Adoption status | `deferred` (`evidence_only`; no `planning apply` provenance) |
| Review status | v1 `FAIL`; v2 `PASS` (P0/P1なし) |

## Immutable inputs

| Input | Identity |
|---|---|
| Candidate v1 | `iss-00354-oracle-017-compatibility-candidate-20260804t033922z.zip` |
| Candidate v1 ID | `CAND-ISS-00354-ORACLE017-20260804T033922Z` |
| Candidate v1 SHA-256 | `8f979a5609b5d4dfa899871d50d51a659e273a7191b97e36c4d8de253348d13c` |
| Formal Red Review v1 | `reviews/red-team-review-v1.md` |
| Selected findings | exactly two P1 findings; no P2/P3 or architecture redesign |

Candidate v1、repository、canonical documents、Git/GitHub state were not modified. v2 is a new logical root and archive identity.

Candidate v2 の ZIP bytes と identity は immutable な historical evidence として保持する。Candidate archive 自体は `planning apply` と exact Human decision の証跡がないため canonical へ採用しない。Candidate から採用した判断だけを、後続の current canonical working copy に別途反映し、`report.md` の adoption ledger と current commit history で追跡する。

## Current canonical working-copy binding

| Field | Value |
|---|---|
| Authority | `canonical` for iss-00354 implementation-preparation documents only |
| Adoption status | `fresh_review_pass_recorded` (implementation not started) |
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Last reviewed branch HEAD | `079685b2a38baf9300c5bec7d5589ce9712bc7d3` |
| GitHub parity at last review | `identical` (default branch fallback not used) |

The last reviewed branch tip is the exact HEAD used by the completed v5 Fresh Red Team review. The v5 PASS is recorded in `report.md` as `EAL-005`; it is a review/adoption result only and does not mean implementation, assurance promotion, PR, merge, or Issue close has occurred. Any later repair commit is a new review target and must be checked through GitHub before another fresh review.

## Latest Fresh Review Outcome

| Field | Value |
|---|---|
| Review target | `079685b2a38baf9300c5bec7d5589ce9712bc7d3` |
| Verdict | `PASS` (P0=0 / P1=0) |
| Reviewer evidence | `/private/tmp/iss-00354-chatgpt-review-v5-20260804/review.md` |
| Evidence SHA-256 | `d0a2e1bef291bab88797e166c5e96a368357452f7c2b4ddeaca402dc8bf5ea1a` |
| Adoption boundary | PASS evidence recorded; implementation not started |

## GitHub verification

GitHub Connectorでrepositoryとrequested branchを確認し、branchとrequested source HEADを比較した結果は`identical`
（ahead `0` / behind `0`）だった。default branch fallbackは使用していない。

## P1-only revision summary

1. Current recovery baseline is corrected to stage-blind, hardcoded 0.16.1 harvest behavior. Compatibility profiles now own a declared
   inline capability and exact-version harvest/capture argv builders; false/unknown submission invokes neither builder.
2. One authoritative internal-class -> public status/reason mapping is fixed across requirement/design/plan/ADR, retaining existing reasons,
   adding five stage-specific reasons, and allowing many-to-one only in three same-semantics families.

No other architecture, lifecycle, authority, source identity, or scope decision was changed.

## Review scope and current working-copy binding

Completed formal review target:

1. `requirement.md`
2. `design.md`
3. `plan.md`
4. `decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md`

Review-excluded supporting material:

- `onboarding.md`
- `MANIFEST.json`
- `CHECKSUMS.sha256`
- `reviews/red-team-review-v1.md`
- all files under `artifacts/`
- `candidate-note.md`

Current working-copy binding:

- The exact branch tip is verified through GitHub immediately before each review and recorded in that review's external identity evidence.
- The v4 review target was `bb75f6d5fcd142d8f2d0dd3ff4a06a057b4ee709`; any repair commit after it is a new review target and is not pre-adopted.
- The immutable v2 review remains the historical Candidate review; each current canonical working copy requires a separate fresh exact-HEAD review.

## Integrity controls

- `MANIFEST.json` records identity, immutable v1/review binding, and SHA-256/size for every payload file except the two integrity-control files.
- `CHECKSUMS.sha256` covers every regular file in the logical root except itself, including `MANIFEST.json`.
- The archive SHA-256 is computed only after sealing and is reported in delivery metadata; it cannot be embedded without changing the archive.
- ZIP validation requires one logical root, no absolute/traversal/symlink entries, successful CRC, and exact checksum verification.

## Candidate contents

```text
iss-00354-oracle-017-compatibility-candidate-v2-20260804t043533z/
├── requirement.md
├── design.md
├── plan.md
├── onboarding.md
├── decisions/
│   └── ADR-ISS354-001-oracle-017-browser-compatibility.md
├── reviews/
│   └── red-team-review-v1.md
├── artifacts/
│   ├── context-and-attachment-contract.md
│   ├── decision-and-migration-ledger.md
│   ├── implementation-and-test-matrix.md
│   └── oracle-017-failure-classification.md
├── MANIFEST.json
├── CHECKSUMS.sha256
└── candidate-note.md
```

This expanded manual delivery inventory does not amend the production Issue Planning authoring ZIP schema. The immutable v2 archive remains
historical evidence; current canonical adoption and implementation-preparation status are recorded in `report.md`. Implementation, PR, merge,
and Issue-close actions remain unperformed.
