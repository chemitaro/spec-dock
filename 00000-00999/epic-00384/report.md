---
種別: レポート（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "planning"
最終更新: "2026-09-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# Result Summary

## Outcome

- Previous Strict session `required-strict-github-connector-verificati-720`の三Issue粒度判定を採用した。
- `iss-00395` / GitHub #395と`iss-00396` / GitHub #396が実在し、依存は`iss-00395 -> iss-00392`、`iss-00396 -> iss-00395`であることを確認した。
- 既存`iss-00392` / GitHub #392はnodeを再利用するが、scopeをFixed Ownership Provider Lifecycle Hard Cutoverへ縮小する。
- Single implementation Issueとthree main gatesの旧決定をsupersedeし、Issue PRを依存順にEpic integration branchへhuman mergeする方式を採用した。
- All Issues complete後だけEpic branchをmainへ一度human mergeする。
- Issue #392は未startであり、本reportはimplementation completionを表さない。

## Verified baseline

- Repository: `chemitaro/spec-dock`
- Branch: `codex/epic-00384-provider-test-strategy-planning`
- Full SHA: `240e561e94b50250a4a6309452a7fd0fb511458a`
- Tree: `181f7eb28da0edff3ca1352edf4cb2ae1f21d433`
- #387: CLOSED/completed、PR #394経由でmainへmerge済み
- Current package/dogfood: `0.2.3`
- Root ledger blob: `f181fd3098ef0cba8d0d17e47d00ea12fbbeb8b5`
- Current `failure_paths`: 15 total、14 active、1 resolved
- Timing blob: `bdeeb6238609c38085aaed8023b78319a3dd0c6d`
- Timing nodes: 243
- Current PR/main-push Full Regression policy machinery: transitional and retained until Issue #396

## Baseline correction

Root ledgerのtop-levelにはIssue #368時点の27件集計、old head SHA、historical conclusionが残る一方、current `failure_paths`は15行である。新しいregisterはtop-level historical metadataをcurrent admission authorityから外し、exact 15-row payloadだけをcurrent regression baselineとする。旧27-row conditional registerとfuture #387 admission modelはcurrent authorityではない。

## Supersession

`artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md`はstatus `superseded`へ変更する。Technical decisionsは新しいaccepted ADRで必要なものだけ明示的に再採用する。

Historical discussions、research、HTML guides、single-Issue guide、CLOSED #388〜#390は削除しない。ただしcurrent implementation authorityではない。

## Current delivery state

| Item | State |
|---|---|
| Parent multi-Issue specification | Draft replacement pack generated; repository import and Strict review pending |
| Issue #392 | Open; not started |
| Issue #395 | Open draft scaffold; blocked by #392 |
| Issue #396 | Open draft scaffold; blocked by #395 |
| Product implementation | Not started under this specification |
| Final Epic merge | Not permitted |

## Remaining gates

1. Import this replacement pack and verify manifest/blob/links.
2. Independently Strict-review parent R/D/P、ADRs、contracts and three Issue drafts.
3. Record `PARENT_FREEZE_SHA` only after acceptance.
4. Elaborate Issue #392 against that exact current integration tip.
5. Do not start implementation before its issue-start elaboration gate passes.

`owner_decisions_required=[]`.
