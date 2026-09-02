---
種別: レポート（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "planning-remediation"
最終更新: "2026-09-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
reviewed_candidate_evidence:
  role: "failed-reviewed-candidate-and-remediation-base"
  sha: "ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83"
  tree: "175408f56af05677fce2a42a169f735983a3a0af"
  reviewer: "required-strict-github-connector-verificati-723"
  result: "fail"
  findings: {P1: 1, P2: 1}
parent_freeze_sha: null
---

# Result Summary

## Outcome

- Previous Strict session `required-strict-github-connector-verificati-720`の三Issue粒度判定を採用した。
- `iss-00395` / GitHub #395と`iss-00396` / GitHub #396が実在し、依存は`iss-00395 -> iss-00392`、`iss-00396 -> iss-00395`である。
- `iss-00392` / GitHub #392はFixed Ownership Provider Lifecycle Hard Cutoverへscope縮小して再利用する。
- Single implementation Issueとthree main gatesの旧決定をsupersedeし、Issue PRを依存順にEpic integration branchへhuman mergeする方式を採用した。
- All Issues complete後だけEpic branchをmainへ一度human mergeする。
- Issue #392は未startであり、本reportはimplementation completionを表さない。

## Import and review state

前回multi-Issue replacement packのrepository import、structural validation、commit、pushはfailed reviewed candidate `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83`で完了済みである。再importをcurrent gateにしない。

Reviewer session `required-strict-github-connector-verificati-723`はschema-valid `fail`、P1 x1、P2 x1を返した。P1はqualification predicate omission、P2はpost-import planning/SHA-role driftである。

Dedicated analyst `required-strict-github-connector-verificati-727`のfollow-up execution `required-strict-github-connector-verificati-729`は、live #384/#392の未撤回Product guaranteeをparentへ復元するrequirement-preserving correctionをauthorized routeとして確定した。本remediation candidateは`E384-QUAL-001`をsole normative sourceとして追加し、P2 stateを訂正する。同一reviewer re-reviewは未実施であり、current reviewer gateはfailのままである。

## Identity roles

| Identity | Role | State |
|---|---|---|
| `240e561e94b50250a4a6309452a7fd0fb511458a` / `181f7eb28da0edff3ca1352edf4cb2ae1f21d433` | Previous pack authoring-source provenance | Valid provenance only; never current/freeze identity. |
| `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83` / `175408f56af05677fce2a42a169f735983a3a0af` | Imported failed reviewed candidate and remediation base | Review fail; never `PARENT_FREEZE_SHA`. |
| `CURRENT_INTEGRATION_TIP` | Connector-resolved dynamic branch tip | Resolve at each gate; do not predict in tracked content. |
| `PARENT_FREEZE_SHA` | Exact clean pushed remediation tip accepted by the same reviewer | Currently unset; recorded externally after pass. |

## Verified product baseline

- #387: CLOSED/completed、PR #394経由でmainへmerge済み。
- Current package/dogfood: `0.2.3`。
- Root ledger blob: `f181fd3098ef0cba8d0d17e47d00ea12fbbeb8b5`。
- Current `failure_paths`: 15 total、14 active、1 resolved。
- Timing blob: `bdeeb6238609c38085aaed8023b78319a3dd0c6d`、243 nodes。
- Root ledgerのtop-level 27件集計、old head SHA、historical conclusionはIssue #368 metadataであり、current row-count authorityではない。
- Current PR/main-push Full Regression policy machineryはtransitionalで、Issue #396まで保持する。

## Qualification remediation

`E384-QUAL-001` in Epic Requirement is the sole current normative source of quantitative final qualification values and aggregation semantics. The three-Issue pivot preserves the accepted guarantee and relocates final-gate implementation/evidence ownership from old #392 scope to #396. Derived current-authority documents reference the contract and do not independently define its values.

## Historical non-authority

`artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md`、historical discussions/research、HTML guides、single-Issue guide、CLOSED #388〜#390は削除しない。Current implementation authorityではなく、本remediationでは変更しない。

## Current delivery state

| Item | State |
|---|---|
| Previous replacement pack import/validation/commit/push | Complete at failed candidate `ce7e46...` |
| Current remediation pack | Generated for canonical adoption; not yet imported |
| Same-reviewer Strict gate | Fail; remediation adoption and re-review pending |
| `PARENT_FREEZE_SHA` | Unset |
| GitHub #384/#392/#395/#396 body projection | Pending; prohibited before same-reviewer pass |
| Issue #392 | Open; not started |
| Issue #395 | Open draft scaffold; blocked by #392 |
| Issue #396 | Open draft scaffold; blocked by #395 |
| Product implementation | Not started under this specification |
| Final Epic merge | Not permitted |

## Remaining gates

1. Adopt this complete remediation pack over the canonical Epic paths and verify manifest、hashes、front matter、relative links、single-source semantics。
2. Commit and push one clean specification-only candidate without Product/test/workflow/Issue mutations。
3. Re-run the same reviewer session `required-strict-github-connector-verificati-723` against that exact pushed tip。
4. Require `P0/P1=0` and `review_status=pass`; otherwise remediate and repeat without freezing。
5. Record the accepted tip as external `PARENT_FREEZE_SHA`; do not write the future/pass SHA back into tracked specifications。
6. Project canonical topology and contract references to GitHub #384/#392/#395/#396 bodies, preserving title、state、labels、assignees、milestone、dependency and start status; read back and record an external projection receipt。
7. Only then elaborate Issue #392 against the current integration tip. Do not start implementation until its implementation-ready pack passes its own Strict review。

`owner_decisions_required=[]`.
