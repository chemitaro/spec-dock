---
種別: ADR
ID: "20260831t152024z-adr"
タイトル: "Single Implementation Unit and Provider Hard Cutover Policy"
状態: "superseded"
決定日: "2026-08-31"
最終更新: "2026-09-02"
対象: ["epic-00384", "iss-00392"]
superseded_by: "20260902t070000z-adr-multi-issue-epic-integration-branch-and-rolling-wave-elaboration-policy.md"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

## Status

本ADRは[Multi-Issue Epic Integration Branch and Rolling-Wave Elaboration Policy](20260902t070000z-adr-multi-issue-epic-integration-branch-and-rolling-wave-elaboration-policy.md)によりsupersedeされた。Historical decision recordとして削除しないが、current implementation、Issue boundary、merge topology、rollback、closureのauthorityではない。

## Superseded decisions

次の決定は撤回する。

- GitHub #392を唯一のimplementation-and-verification Issueとすること。
- S30、S60、S80をmainへの三つのmerge gateとすること。
- Multiple implementation Issuesが必然的にmultiple writersとunsafe main stateを生むという前提。
- Failure terminalizationとfinal provider-gate cutoverを#392内部stepとして所有させること。
- 未達を常に#392だけでforward-fixすること。

Epic integration branchへdependency順にhuman mergeし、各merge後GREENを要求することで、mainへ中間stateを公開せず三つの独立rollback unitを成立させる。

## Historical decisions re-adopted elsewhere

以下は本ADRから直接継承されるのではなく、新accepted ADR、parent R/D/P、normative artifactsで明示的に再採用される。

- Four fixed roots、two fixed skill slots、strict installation record。
- Immutable `seed_policy`とexact resume tuple。
- Exact clean `0.2.3` migration。
- Tooling-only uninstall、durable tooling-absent record、purge removal。
- Closed lifecycle wireとfilesystem safety。
- Protected data、owner-bound workspaces、complete dogfood convergence。
- One Linux packaging producer、same-artifact consumers、stable qualification。
- No-gap required-context transition、actual-byte evidence、human-only merge。

## Historical non-authority

このADRを前提に作成されたsingle-Issue HTML、handoff、Issue #392の旧scope、#388〜#390のhistorical nodesは現状説明の資料であり、current authorityではない。Contradiction時は新ADRとcurrent parent contractsが優先する。

`owner_decisions_required=[]`.
