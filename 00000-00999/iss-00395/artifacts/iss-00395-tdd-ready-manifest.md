---

kind: "tdd-ready-pack-manifest"
issue: "iss-00395"
title: "Issue #395 Code-free TDD Readiness Pack Manifest"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_tip_sha: "25b33cfaf6214d8c78494f0e0520ef8738bc862f"
verified_tip_tree: "ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
canonical_adoption_required: true
distribution_file_count: 6
archive_name: "iss-00395-tdd-ready-pack.zip"
archive_member_root: "artifacts/"
authority: "advisory-provenance-and-packaging-contract"
---

# Issue #395 Code-free TDD Readiness Pack Manifest

## 1. Purpose

このmanifestは、verified commit `25b33cfaf6214d8c78494f0e0520ef8738bc862f`をauthority sourceとして作成した、Issue #395の分析書、TDD実装準備版Requirement、Design、Plan、LunaMax handoff、および本manifestの配布構成を固定します。

本packはrepositoryのcanonical文書を自動的に置換しません。Product/test/ledger/dogfood mutation、commit、push、PR、merge、Issue state変更を許可しません。

## 2. Source identity

| Field                    | Value                                                                     |
| ------------------------ | ------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                     |
| Branch                   | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Verified tip             | `25b33cfaf6214d8c78494f0e0520ef8738bc862f`                                |
| Verified tree            | `ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8`                                |
| Parent elaboration input | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                                |
| Parent elaboration tree  | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`                                |
| P392 entry               | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |
| P392 tree                | `190bc566a18cd84813c4b7c043f8724e275cb55d`                                |

GitHub connectorでtarget branchを直接取得し、default branchへfallbackせず、branch-tip SHAのbyte-for-byte一致を確認しています。

## 3. Exact distribution files

ZIP memberは次の6 regular Markdown filesだけです。Member orderもこの順です。

| Order | Path                                               | Role                                                                 | SHA-256                                                            |
| ----: | -------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------ |
|     1 | `artifacts/iss-00395-plan-review-analysis.md`      | 現行packの判定、根拠、問題点、改訂判断                                                | `98cada2a70be0536230041874e54341c9e9f363710cdcc85293687e31fcc546b` |
|     2 | `artifacts/iss-00395-requirement-tdd-ready.md`     | Value、behavior、acceptanceのcanonical replacement candidate            | `65f13cb4d2951d278568f25d7afda706585f722855a4b66c7ef80cf98097ba28` |
|     3 | `artifacts/iss-00395-design-tdd-ready.md`          | Boundary、responsibility、invariant、state transition、testable contract | `0906faea23cc14f82d216ff90ae80aafb8200091966d84e32131b807ada6f4d7` |
|     4 | `artifacts/iss-00395-plan-tdd-ready.md`            | Code-free TDD execution order、RED/GREEN/evidence/stop                | `3cba536f01fcf645a5d03a823d152268dbb930994e0c154734b5caced93a89c0` |
|     5 | `artifacts/iss-00395-lunamax-handoff-tdd-ready.md` | Dispatch、authority、scope、return、human boundary                       | `e359f549ec090c9ed1cc8c17eb4ddf6783ef6897a75971e42d1fb4e09b2c439f` |
|     6 | `artifacts/iss-00395-tdd-ready-manifest.md`        | 本packのidentity、member、integrity、exclusion contract                   | Self-hashはarchive外のdelivery metadataへ記録                            |

## 4. Responsibility separation

| File        | Must contain                                                                   | Must not contain                                 |
| ----------- | ------------------------------------------------------------------------------ | ------------------------------------------------ |
| Analysis    | Verdict、facts、inference、trade-off、residual risk                                | Implementation authorization                     |
| Requirement | Value、observable behavior、acceptance、non-goals                                 | Method body、shell runner、commit/PR script        |
| Design      | Boundaries、responsibilities、invariants、state/data transition、testable contract | Finished implementation code                     |
| Plan        | Purpose、precondition、target、RED、minimal intent、GREEN、evidence、stop             | Long Bash/Python/JSON program                    |
| Handoff     | Packet、permissions、scope、return/evidence、terminal point                        | Planの全文複製、merge operation                        |
| Manifest    | File list、hashes、byte/ZIP contract、exclusions                                  | Canonical authority replacement、permission grant |

## 5. Preserved semantic contract

Six files間で次が一致しなければなりません。

* Exact 15 regression rows
* Entry 14 active / 1 resolved
* Target 0 active / 15 resolved
* 14 fixed-in-place / 1 superseded
* Row 2 read-only successor
* Row 3 identity/publication separation
* Rows 4–11 descriptor-bound test-double seam
* Row 12 no-edit guard
* Rows 13–15 observer migration
* Ledger last transition
* Complete dogfood projection
* Timing 243、required-fast 4、policy/workflow/wire no-touch
* Same-tip B1/B2
* Human merge only
* `implementation_allowed=false`
* `owner_decisions_required=[]`

## 6. Byte contract

All members use:

* UTF-8 without BOM
* LF line endings
* No NUL byte
* Exactly one terminal LF
* Markdown front matter beginning and ending with exact `---`
* YAML safe-parseable front matter
* No embedded binary or symlink

SHA-256 is calculated from exact file bytes, excluding path names.

## 7. ZIP contract

Archive name is `iss-00395-tdd-ready-pack.zip`.

The archive contains exactly six members under `artifacts/` and no explicit directory entry. It excludes:

* Product source
* Test source
* Ledger、timing、policy、workflow
* Existing canonical Issue files
* Attachment bundle
* Nested archive
* Raw logs、verifier artifacts、review receipts
* Cache、temporary files、backup files
* Credentials、tokens、private keys、`.env`
* Absolute paths、`..` traversal、duplicate or case-conflicting members
* Symlink、device、FIFO

Member bytes must be byte-for-byte equal to the source Markdown files and must match the recorded SHA-256 values for files 1–5. Manifest self-hash and final ZIP hash are recorded in delivery metadata because embedding either value inside the manifest would create self-reference.

## 8. Validation requirements

Before delivery, verify:

1. Exact six files exist
2. UTF-8/LF/terminal-LF contract
3. Front matter YAML parses
4. Common identity and permission fields agree
5. No implementation code fences are present in Requirement、Design、Plan、handoff
6. Plan contains each TDD step's purpose、precondition、target、RED、minimal intent、GREEN、evidence、stop
7. Handoff does not duplicate implementation scripts
8. Exact ZIP member set and order
9. ZIP integrity test passes
10. Archived bytes equal source bytes
11. SHA-256 records match
12. Product/test/ledger/timing/policy/workflow and Git state are unchanged

## 9. Operations not performed

* Product source modification
* Test modification
* Ledger modification
* Dogfood update
* Timing、policy、workflow、wire modification
* Managed metadata modification
* Commit、push、PR create/update
* Merge、revert
* Issue close、#396 start

## 10. Final state

| Field                                   | Value |
| --------------------------------------- | ----- |
| Distribution files materialized         | true  |
| ZIP created                             | true  |
| Canonical Issue docs adopted            | false |
| Independent specification review passed | false |
| Implementation allowed                  | false |
| Owner decisions required                | empty |
| Human merge only                        | true  |
