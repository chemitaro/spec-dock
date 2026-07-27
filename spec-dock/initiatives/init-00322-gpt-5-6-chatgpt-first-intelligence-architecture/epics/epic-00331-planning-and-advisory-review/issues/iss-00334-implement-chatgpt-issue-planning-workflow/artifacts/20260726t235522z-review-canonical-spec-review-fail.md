---
種別: "fresh canonical spec review"
Issue: "iss-00334"
reviewer_role: "spec-reviewer"
review_status: "fail"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_head: "eadbfa544ad972c799162552f5684482d26e89b5"
created_at_utc: "2026-07-26T23:55:22Z"
authority: "read-only reviewer verdict"
---

# iss-00334 fresh canonical spec review — FAIL

## Scope

Canonical Issue `requirement.md`、`design.md`、`plan.md`、`report.md`、parent Epic三文書、Issue `.assurance.json`、Issue workflow／phase／authoring docs、archive／multi-file transaction関連sourceをread-onlyで確認した。

## Verdict

- `review_status: fail`
- Requirement: fail
- Design: fail
- Plan: fail
- Closure Index: fail
- Assurance: fail
- Report: fail
- overall confidence: `0.99`

public adoption/readiness route、transaction safety、archive closure、Closure Index schema、step ownership、live-operation boundary、source binding、canonical authority state、Main-owned assurance/report evidenceにP1 blockerが残る。所有文書を修正し、Main-owned metadata/evidenceを更新した後のfresh spec-reviewer再審査が必要である。

## Findings

### P1-01 Public apply route

`design.md`のpublic commandがcreate／revise／reviewだけで、S06もcommand handlerを変更対象に含めないため、REQ-009〜REQ-013のHuman decision取込、採用、validation、publication、readinessをofficial Skillから呼び出す経路がない。Designがsupported callable surfaceと入出力を所有し、Planがhandler、help、positive／negative E2Eを実装対象へ追加する必要がある。

### P1-02 Crash-safe adoption transaction

REQ-010のfixed-order atomic replacementに対して、stage／backup／commit順、途中crash、rollback失敗、再実行時の既採用判定が未定義である。S06はexisting `runbook_store.py` stage／backup／restore behaviorのbounded shared primitive reuseとfailure-injection testsを所有する必要がある。

### P1-03 Complete REQ-022 archive closure

absolute／backslash／NUL、hardlink／device／FIFO／socket、casefold／Unicode collision、encryption／nested archive、executable／binary、全resource limitなど、REQ-022の各classにplanned verification pathとpartial-output absenceが必要である。

### P1-04 Schema-complete Closure Index

各required rowにspec link、observable input/state、locked expectation、bug class guarded、required、evidence level、closure evidence、ownerが必要である。material obligationを集約せず、AC／EC／Design／riskへ個別traceする必要がある。

### P1-05 S02 ownership

S02は`tests/cli_runtime/test_chatgpt_planning.py`でassertionを要求する一方、exact targets／allowed pathsはSkill／Promptだけであり実行不能である。docs ownershipとtest ownershipを一致させる必要がある。

### P1-06 S09 operation boundary

S09はtest fileだけをtargetにしながらHuman Gate、canonical adoption、push/publicationを同じpytest commandへ混在させている。hermetic test implementationと、Human-selected target／authorization／mutable destinations／rollback／evidence captureを持つMain-owned live operation gateを分離する必要がある。

### P1-07 Current source binding

canonical RequirementとReportのsource HEADがreview対象HEADと不一致である。current source refreshを行い、Requirement binding、assurance source binding、Reportのfresh-review evidenceを同じplanning baselineへ揃える必要がある。

### P1-08 Canonical authority state

canonical三文書が`draft`／candidate／unreviewedを自己宣言する一方、ReportはHuman adoption済みと記録しており矛盾する。三文書はcurrent canonical stateだけを所有し、Candidate provenanceはReportへ分離する必要がある。

### P1-09 Assurance and Report evidence

`.assurance.json`はprovisional standard、Reportはfrontmatter choice、mandatory ledger template、古いassurance observationを残す。Mainはcurrent docsへのclassify／compose結果、standardからstrict手動強化する理由・delta・revert condition、specialist evidence、本review verdict、next actionを実値で記録する必要がある。

## Required next action

MainがP1-01〜P1-09を所有文書へ反映し、assuranceをcurrent三文書SHAへ再束縛し、Reportからreadiness用placeholderを除去する。その後、別のfresh `spec-reviewer`がcanonical setを再審査する。

このartifactはread-only reviewer resultであり、canonical修正、reviewer pass、execution readiness、PR readiness、Issue completionを主張しない。
