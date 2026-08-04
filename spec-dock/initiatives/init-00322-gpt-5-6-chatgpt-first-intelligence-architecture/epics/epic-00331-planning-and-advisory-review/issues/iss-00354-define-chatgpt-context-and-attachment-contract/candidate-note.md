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
| Authority | `evidence_only` |
| Adoption status | `unreviewed` |
| Review status | v1 `FAIL`; v2 not yet reviewed |

## Immutable inputs

| Input | Identity |
|---|---|
| Candidate v1 | `iss-00354-oracle-017-compatibility-candidate-20260804t033922z.zip` |
| Candidate v1 ID | `CAND-ISS-00354-ORACLE017-20260804T033922Z` |
| Candidate v1 SHA-256 | `8f979a5609b5d4dfa899871d50d51a659e273a7191b97e36c4d8de253348d13c` |
| Formal Red Review v1 | `reviews/red-team-review-v1.md` |
| Selected findings | exactly two P1 findings; no P2/P3 or architecture redesign |

Candidate v1、repository、canonical documents、Git/GitHub state were not modified. v2 is a new logical root and archive identity.

## GitHub verification

GitHub Connectorでrepositoryとrequested branchを確認し、branchとrequested source HEADを比較した結果は`identical`
（ahead `0` / behind `0`）だった。default branch fallbackは使用していない。

## P1-only revision summary

1. Current recovery baseline is corrected to stage-blind, hardcoded 0.16.1 harvest behavior. Compatibility profiles now own a declared
   inline capability and exact-version harvest/capture argv builders; false/unknown submission invokes neither builder.
2. One authoritative internal-class -> public status/reason mapping is fixed across requirement/design/plan/ADR, retaining existing reasons,
   adding five stage-specific reasons, and allowing many-to-one only in three same-semantics families.

No other architecture, lifecycle, authority, source identity, or scope decision was changed.

## Review scope for next turn

Review target:

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

This expanded manual delivery inventory does not amend the production Issue Planning authoring ZIP schema. It contains no v2 Red verdict,
canonical adoption, implementation claim, patch, commit, push, PR, merge, or Issue-close action.
