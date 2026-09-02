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
  role: "failed-reviewed-candidate-and-current-remediation-base"
  sha: "177937163526c369108c97ef7c024adb3dd05f77"
  tree: "ec47247721e71d410a2553c8c94e24d7fa20726c"
  reviewer: "required-strict-github-connector-verificati-723"
  execution: "required-strict-github-connector-verificati-740"
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

前回multi-Issue replacement packのrepository import、structural validation、commit、pushはinitial failed reviewed candidate `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83`で完了した。その後、qualification remediation packはfull SHA `177937163526c369108c97ef7c024adb3dd05f77`、tree `ec47247721e71d410a2553c8c94e24d7fa20726c`へcanonical adoption、structural validation、commit、push済みである。いずれも再importをcurrent gateにしない。

Dedicated analyst `required-strict-github-connector-verificati-727`のfollow-up execution `required-strict-github-connector-verificati-729`は、live #384/#392の未撤回Product guaranteeをparentへ復元するrequirement-preserving correctionをauthorized routeとして確定した。そのcorrectionにより`E384-QUAL-001`はsole normative sourceとなり、final-gate implementation/evidence ownershipは#396へ移管された。

同じreviewer conversation `required-strict-github-connector-verificati-723`のexecution `required-strict-github-connector-verificati-740`は、exact SHA `177937163526c369108c97ef7c024adb3dd05f77`をreviewし、schema-valid `fail`、P1 x1、P2 x1を返した。P1はitem 11のchronological unfiltered rolling-twenty populationに対して全memberのoverall final-gate success/accepted predicateが欠落していること、P2はcurrent adoption/commit/push/review state driftである。Review 740はcompleted historyであり、本three-file correctionのparent adoptionと同一reviewer re-reviewは未実施である。

## Identity roles

| Identity | Role | State |
|---|---|---|
| `240e561e94b50250a4a6309452a7fd0fb511458a` / `181f7eb28da0edff3ca1352edf4cb2ae1f21d433` | Previous pack authoring-source provenance | Valid provenance only; never current/freeze identity. |
| `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83` / `175408f56af05677fce2a42a169f735983a3a0af` | Initial imported failed reviewed candidate and prior remediation base | Historical fail; never `PARENT_FREEZE_SHA`. |
| `177937163526c369108c97ef7c024adb3dd05f77` / `ec47247721e71d410a2553c8c94e24d7fa20726c` | Adopted qualification remediation and reviewer execution `required-strict-github-connector-verificati-740` candidate | Review fail; current remediation base; never `PARENT_FREEZE_SHA`. |
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

Review 740 confirmed that item 11 already fixes an unfiltered latest-twenty chronological population. The bounded correction therefore changes no numeric value or population semantics: item 12 requires every window member's overall final-gate result to be successful and accepted, and item 13 rejects the window when any member is failed or non-accepted.

## Historical non-authority

`artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md`、historical discussions/research、HTML guides、single-Issue guide、CLOSED #388〜#390は削除しない。Current implementation authorityではなく、本remediationでは変更しない。

## Current delivery state

| Item | State |
|---|---|
| Initial multi-Issue pack import/validation/commit/push | Complete at failed candidate `ce7e46...` |
| Qualification remediation pack adoption/validation/commit/push | Complete at reviewed candidate `177937163526c369108c97ef7c024adb3dd05f77` |
| Same-reviewer execution `required-strict-github-connector-verificati-740` | Complete; schema-valid fail, P1 x1, P2 x1 |
| Current bounded three-file correction | Authorized; parent adoption/structural validation/commit/push/re-review pending and not claimed by this report |
| `PARENT_FREEZE_SHA` | Unset |
| GitHub #384/#392/#395/#396 body projection | Pending; prohibited before same-reviewer pass |
| Issue #392 | Open; not started |
| Issue #395 | Open draft scaffold; blocked by #392 |
| Issue #396 | Open draft scaffold; blocked by #395 |
| Product implementation | Not started under this specification |
| Final Epic merge | Not permitted |

## Remaining gates

1. Adopt the bounded three-file correction for Epic `requirement.md`、`plan.md`、`report.md` and perform parent-owned structural validation without changing any other canonical or Product surface。
2. Commit and push one clean specification-only candidate without Product/test/workflow/GitHub Issue mutations。
3. Re-run the same reviewer conversation `required-strict-github-connector-verificati-723` against that exact pushed tip。
4. Require `P0/P1=0` and `review_status=pass`; otherwise remediate and repeat without freezing。
5. Record the accepted tip as external `PARENT_FREEZE_SHA`; do not write the future/pass SHA back into tracked specifications。
6. Project canonical topology and contract references to GitHub #384/#392/#395/#396 bodies, preserving title、state、labels、assignees、milestone、dependency and start status; read back and record an external projection receipt。
7. Only then elaborate Issue #392 against the current integration tip. Do not start implementation until its implementation-ready pack passes its own Strict review。

`owner_decisions_required=[]`.
