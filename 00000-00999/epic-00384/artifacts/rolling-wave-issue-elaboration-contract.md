---
種別: Normative Artifact
ID: "epic-00384-rolling-wave-issue-elaboration-contract-v1"
タイトル: "Rolling-Wave Issue Elaboration Contract"
状態: "draft"
最終更新: "2026-09-08"
対象: ["epic-00384", "iss-00392", "iss-00395", "iss-00396"]
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# Rolling-Wave Issue Elaboration Contract

## 1. Purpose

Current Issue R/D/P define stable acceptance contracts only. They intentionally omit implementation file lists、symbols、test code、exact commands and ordered implementation steps. Parent G0、dependency evidence and an explicit user start request permit formal `issue start` to select the Issue branch/active scope. Detailed R/D/P and handoff are then authored on that branch against the accepted integration tip; independent acceptance is required before Product implementation. Use a new worktree or an existing worktree explicitly selected by the user. The user requested parent commit/push followed by #392 formal start on 2026-09-08; this proceeds only after G0. Product implementation remains outside this task.

## 2. Immutable parent inputs

Elaboration may not change:

- Issue count、IDs、GitHub numbers、dependency direction;
- integration branch and human merge topology;
- stable cross-Issue contracts E384-C-001〜C-012 and parent `E384-QUAL-001`;
- lifecycle wire values and #392 sole-writer/read-only rule;
- 15/14/1 baseline identities and Issue ownership;
- current-policy-through-#395 and consumer-first-#396 rule;
- protected data、compatibility、rollback、recovery and GREEN definitions;
- no-extra-Issue and human-only settings/merge rule。

A required change to any item is a parent stop, not an elaboration choice。

## 3. Start and elaboration gate inputs

Before formal Issue start:

1. Resolve exact current integration branch tip and tree。
2. Require accepted parent G0 with `owner_decisions_required=[]`. For #392, require external `PARENT_FREEZE_SHA` receipt for that accepted parent tip and readback receipts for the post-pass GitHub #384/#392/#395/#396 body projections。
3. Verify predecessor Issue merged and accepted, or #387 completed for #392。
4. Verify current state B0/B1/B2 as applicable is GREEN。
5. Verify Issue metadata ID、GitHub number and `depends_on` relation。
6. Verify no other Issue writer is active。
7. Compare main drift and classify overlap。
8. Re-read root `AGENTS.md` and current parent contracts。
9. Verify current Issue remains open and not already started. Require an explicit user start request; review completion alone does not resume the cancelled start。

After formal start, verify the selected branch/active Issue and perform elaboration there. `issue start` is scope selection, not permission to dispatch a coder. Elaboration/review may leave the Issue active while Product implementation remains prohibited.

## 4. Required elaboration outputs

Before Product implementation, the elaboration pack must produce implementation-ready R/D/P and a Luna Max handoff containing:

- exact base SHA/tree and accepted predecessor evidence;
- observable goal and non-goals copied without semantic change;
- owned/shared/no-touch file inventory;
- component and symbol responsibilities;
- stable input/output schemas and compatibility points;
- for #392, resolved legacy admission, shared runtime/lifecycle coordination, wrapper handoff and interruption/concurrency evidence under E384-RQ-019;
- for #395, the register §6.1 cause-specific repair map, including faithful harness repairs and guarded Product boundaries;
- for #396, exact measurement/evidence implementation and boundary tests that mechanically realize `E384-QUAL-001` without duplicating its policy values, including one role graph per attempt, shared five-run/twenty-window observations and environment capability proof;
- first RED and representative failure evidence;
- complete test ownership and exact test cases;
- exact commands and expected results;
- ordered implementation and verification steps;
- migration/dogfood/update boundary where applicable;
- rollback、forward recovery、cleanup and stop/return procedures;
- Issue PR merge-ready acceptance checklist;
- requirement-to-design-to-plan traceability;
- `owner_decisions_required=[]` or an explicit parent stop。

## 5. Independent review — current authorized route

2026-09-08のユーザー指示により、外部ChatGPT Useが機能しない状況での現在のreview経路は、独立したGPT-6（`gpt-6-astra`）・推論Maxのサブエージェントである。親／Issue draft中の「Strict review」「same-reviewer pass」は、現在の運用では本節の独立性・候補固定・再レビュー条件を満たすreviewを指す。外部ChatGPT Strictを実行したとは主張しない。過去の外部Strict passはその過去SHAだけの証拠として保持する。

- 一つのreview周期の初回はfresh reviewerを使う。修正後は同じreviewerを再利用する。
- 主担当がauthoringと指摘の採否を担当し、reviewerはread-onlyで独立に判断する。主担当自身のself-reviewだけでacceptしない。
- Luna Maxは将来の実装担当である。このEpicのreviewerはGPT-6 Maxとする。
- Reviewはexact base SHA/treeと候補のfile/diff identityへ束縛する。Working-tree review後にcommitする場合、review済み内容との一致を確認し、最終clean pushed tipのreceiptをtracked tree外へ記録する。後続の仕様変更を過去passで認証しない。
- 要件・設計・責務境界・安全な中間状態・testability・互換性・recovery・evidence identity・human gateを確認する。`P0/P1=0` かつ `review_status=pass` がacceptance条件である。
- Epicでは親契約とIssue draft境界をreviewする。まだ存在しないIssue詳細実装手順の欠如は、それ自体をEpicの欠陥としない。
- Issueでは、選択されたIssue branch/worktreeで作られたimplementation-ready R/D/PとLuna Max handoffを独立reviewする。Epic passやdependency `ready=true` はIssue実装許可を代替しない。
- 別環境の新しい担当は、review開始時のユーザー指示を再確認する。明示的な変更がなければ本節の経路を用い、故障した外部経路の再試行を開始条件にしない。

## 6. Allowed rolling-wave choices

The elaborator may choose exact implementation files、symbols、helper decomposition、measurement collector、schema field names、test placement、command sequence and internal checkpoints only when every choice remains inside the Issue boundary and does not change parent behavior or outputs. It may not change or independently restate `E384-QUAL-001` values、population、window、aggregation、platform scope、rejection or forbidden escapes。

## 7. Stop and return

Return to the parent owner without formal start if not yet active, or without Product implementation if already active, when:

- dependency or branch-tip evidence differs;
- current branch is not GREEN;
- stable contract, including `E384-QUAL-001`, cannot be implemented without semantic change or duplicate policy authority;
- required behavior crosses another Issue boundary;
- an active baseline identity changed unexpectedly;
- old consumer removal is required before Issue #396;
- compatibility or rollback becomes ambiguous;
- main drift overlaps a stable contract;
- owner decision is non-empty。

The return payload identifies exact contract ID、expected/actual evidence、scope impact and whether the Issue draft or parent ADR needs revision。

## 8. Current status

The 2026-09-02 parent candidate `1429c2f899c6d2086d5bd03c0dcea01f5b168435` passed external review; the later narrow GPT-6 review also applies only to its recorded candidate. Neither certifies the 2026-09-08 whole-plan changes. No implementation-ready elaboration has been accepted for #392、#395 or #396. #392 is dependency-ready. Both E384-DEC-001/002 were adopted by the user. G0 still requires the exact candidate review/publication receipts. The explicit request to start #392 has been received; after G0, formal start selects its branch in this same worktree, followed by elaboration and independent implementation-readiness review.

`owner_decisions_required=[]`. Both decisions are adopted; do not reopen them without new evidence. See [whole-plan reassessment ADR](20260907t234210z-adr-whole-plan-reassessment-and-executable-gates.md).
