---
種別: 実装計画書（Issue）
ID: "iss-00306"
タイトル: "Runtime Workflow Guidance"
関連GitHub: ["#306"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00306 Runtime Workflow Guidance — Issue 実装計画書

## 1. 実装方針

このIssueは docs / workflow guidance の実装を中心に進める。新しいruntime behaviorは追加しない。runtime help wordingが現行実装と明らかに矛盾する場合だけ、behaviorを変えないtext-only correctionを許容する。

中間Issueであるため、このIssueではPR deliveryを行わない。完了後は `issue finish` し、次の `iss-00307` でEpic単位のfinal quality gateとmergeable PR deliveryを実施する。

## 2. 許可変更面

| 種別 | パス | 許可する変更 |
|---|---|---|
| Provider docs | `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md` | ChatGPT authoring evidence lane workflow guideを作成または更新 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md` | backend invocation referenceを作成または更新 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md` | prompt pack / ZIP / staged evidence referenceを作成または更新 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | ChatGPT evidence laneとdraft adoptionへの薄い導線を追加 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | InitiativeからEpic candidate planningへのChatGPT evidence laneとhuman approval gateを追加 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | EpicからIssue candidate planning、Issue draft handoff、relay PR policyを追加 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue draft adoption、validation pass is not reviewer pass、handoff-ready vs execution-readyを追加 |
| Provider docs index | `src/spec_dock/assets/spec_dock/docs/README.md` または `src/spec_dock/assets/spec_dock/docs/guide.md` | 新規reference docsへの導線を追加 |
| Dogfooding mirror | `spec-dock/docs/` | provider docsと対応する内容を反映 |
| Runtime help text | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` と `spec-dock/scripts/spec_dock_runtime/` | 古いhelp wordingのtext-only correctionが必要な場合のみ |

## 3. 禁止変更

- automatic Issue creationの実装。
- ChatGPT outputからcanonical docsへの自動mutation。
- `.assurance.json` mutation。
- reviewer pass、execution-ready、PR-ready、merge-ready automation。
- `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` の実装。
- 中間IssueでのPR作成。
- secret、credential、raw transcript、host-local absolute pathをdurable docsに保存する運用の追加。

## 4. Spec-Locked Closure Index

| closure_id | requirement | design | closes | verification level | required evidence |
|---|---|---|---|---|---|
| CLOS-001 | AC-001, AC-008 | DES-001, DES-005 | provider docsとdogfooding mirror docsにChatGPT authoring pack workflowの発見可能な導線がある | docs inspection, provider/mirror comparison | `report.md` S02/S03 evidence |
| CLOS-002 | AC-002, AC-003 | DES-004 | supported commandsとdeferred commandsが分離され、docs examplesがruntime helpと一致する | command help smoke, grep inspection | `report.md` S04 evidence |
| CLOS-003 | AC-004 | DES-001, DES-005 | `github-synced` と `local-context` のauthority差分が説明される | docs inspection, grep inspection | `report.md` S02/S05 evidence |
| CLOS-004 | AC-005 | DES-001, DES-003, DES-004 | ZIP/tree/staged/candidate/validation outputがevidence-onlyとして説明される | docs inspection, forbidden authority grep | `report.md` S02/S05 evidence |
| CLOS-005 | AC-006 | DES-001, DES-004 | human approval before node creation と Issue draft adoption after node creation の順序が説明される | docs inspection | `report.md` S02/S05 evidence |
| CLOS-006 | AC-007 | DES-001, DES-004 | C11のno-per-Issue-PR relay policyと`iss-00307` deferが説明される | docs inspection, report ledger | `report.md` S05 evidence |
| CLOS-007 | AC-009 | DES-004, DES-005 | required verification commandsとreviewer gateが完了する | command execution, fresh spec-reviewer | `report.md` S05 evidence |

## 5. 実装ステップ契約

### S01: Planning evidenceを確定する

目的:

- ChatGPT Use planning analysis と Issue-local draft artifacts の採否を `report.md` に記録する。
- 外部ChatGPT evidenceはdiff guard対象のdelegated workspace-write outputではなく、main orchestratorが手動採用したevidence-only inputであることを明確にする。

対象:

- `spec-dock/active/issue/report.md`

Delegation:

- 親orchestrator実施。canonical planning docs / reportのsingle-writer作業のため、実装委任は行わない。

Verification:

- `rg -n "not_applicable: external read-only analysis|pending fresh spec-reviewer" spec-dock/active/issue/report.md`
- 出力で外部read-only分析としてのdiff guard対象外理由とreviewer待ち状態だけが確認できることを確認する。

Report evidence destination:

- `report.md` の Evidence Adoption Ledger、Delegated Draft Evidence、Spec Authoring Gate。

Amendment trigger:

- ChatGPT evidenceをdelegated artifact writeとして扱う必要がある場合、plan amendmentとfresh spec-reviewerを先に通す。

Closes:

- CLOS-007 のplanning evidence前提。

### S02: Provider docsを追加・更新する

目的:

- provider-side source of truthに、ChatGPT authoring pack workflow、backend reference、prompt pack / ZIP / staged evidence referenceを追加する。
- 既存workflow docsに薄い導線を追加する。

対象:

- `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
- `src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`

Delegation:

- Primary worker role: `doc-writer`。
- Allowed changes: provider docs only。
- Forbidden changes: runtime code, tests, `.assurance.json`, canonical issue docs outside `report.md` evidence。
- In this session, parent direct implementation is allowed only if recorded as Parent Implementation Exception in `report.md`; otherwise use `doc-writer`.

Verification:

- inspect docs manually for CLOS-001〜CLOS-006。
- `rg -n "github-synced|local-context|evidence-only|authority: evidence_only|reviewer pass|PR-ready|merge-ready|iss-00307" src/spec_dock/assets/spec_dock/docs`

Report evidence destination:

- `report.md` S02 session log and changed files inventory。

Amendment trigger:

- 新runtime behavior、new command、automatic mutation、PR deliveryが必要になった場合はこのIssueを停止し、plan amendmentまたはfollow-up化する。

Closes:

- CLOS-001, CLOS-003, CLOS-004, CLOS-005, CLOS-006。

### S03: Dogfooding mirrorへ反映する

目的:

- provider docsと対応する `spec-dock/docs/` mirrorを更新し、dogfooding workspaceで同じguidanceを検証できるようにする。

対象:

- `spec-dock/docs/workflow_chatgpt_authoring_pack.md`
- `spec-dock/docs/reference_authoring_pack_backend.md`
- `spec-dock/docs/authoring/chatgpt-pack.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/workflow_initiative.md`
- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/README.md`
- `spec-dock/docs/guide.md`

Delegation:

- Same worker role as S02。S02と同じdocs contentをmirrorへ反映する。

Verification:

- provider/mirrorの対応ファイルを `diff -u` または `cmp` で確認する。
- mirrorだけをsource of truthとして扱わないことをreportに記録する。

Report evidence destination:

- `report.md` S03 session log and provider/mirror comparison。

Amendment trigger:

- providerとmirrorで意図的な差分が必要な場合、designに差分理由を追記してfresh spec-reviewerを通す。

Closes:

- CLOS-001。

### S04: Runtime help wordingを確認する

目的:

- docs examplesが実在commandだけを示していることを確認する。
- help textが旧式の “Deferred skeleton” といった誤解を招く表現を残している場合、behaviorを変えないtext-only correctionを実施するかknown riskとして記録する。

対象:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`
- `spec-dock/scripts/spec_dock_runtime/cli/parser.py`
- `spec-dock/scripts/spec_dock_runtime/commands/authoring.py`

Delegation:

- Runtime help textを変更する場合は `dev-coder` またはparent implementation exceptionを記録する。
- docs inspectionのみで変更不要の場合は親orchestratorがreportにapproved-no-op evidenceを記録する。

Verification:

```bash
./spec-dock/scripts/spec-dock authoring --help
./spec-dock/scripts/spec-dock authoring preflight github-sync --help
./spec-dock/scripts/spec-dock authoring pack prepare --help
./spec-dock/scripts/spec-dock authoring backend invoke --help
./spec-dock/scripts/spec-dock authoring pack review --help
./spec-dock/scripts/spec-dock authoring pack stage --help
./spec-dock/scripts/spec-dock authoring validate initiative-epic-candidates --help
./spec-dock/scripts/spec-dock authoring validate epic-issue-candidates --help
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption --help
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill --help
./spec-dock/scripts/spec-dock authoring approval check --help
```

Report evidence destination:

- `report.md` S04 session log。

Amendment trigger:

- help wording correctionがbehavior changeやnew command implementationに広がる場合は停止し、plan amendmentを通す。

Closes:

- CLOS-002。

### S05: 検証・レビュー・中間Issue完了証跡

目的:

- docs / workflow guidanceが要件を満たすことを確認し、fresh reviewer gatesを通す。
- 中間IssueとしてPR deliveryを `iss-00307` へdeferする証跡を残す。

Verification commands:

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify --format json
```

Inspection commands:

```bash
rg -n "authoring adopt|create-issues-from-zip|mark-reviewer-pass|set-authorized-profile|issue-execution-ready|pr-ready" src/spec_dock/assets/spec_dock/docs spec-dock/docs
rg -n "canonical adoption completed|\\.assurance\\.json mutation|authorized_profile decision|execution-ready|PR-ready|merge-ready" src/spec_dock/assets/spec_dock/docs spec-dock/docs
```

Reviewer gates:

- `spec-reviewer`: required. Docs/spec alignment、authority boundary、supported/deferred command separation、evidence mode semantics、relay policyを確認する。
- `code-reviewer`: runtime help textを変更した場合のみrequired。
- `qa-reviewer`: docs-onlyならnot required。runtime help textを変更した場合はhelp smokeとdocs examplesの整合をQA focusにする。

Report evidence destination:

- `report.md` Final Quality Gate、Reviewer Gate Status、Milestone / Commit Candidate Gate。

Amendment trigger:

- reviewerがP1以上のfindingを返した場合は修正し、fresh re-reviewを通す。

Closes:

- CLOS-001〜CLOS-007。

## 6. Required command queue

1. `./spec-dock/scripts/spec-dock assurance verify --format json`
2. `./spec-dock/scripts/spec-dock guidance issue-execution`
3. S02/S03 docs implementation
4. S04 help smoke
5. S05 verification commands
6. fresh reviewers required by S05
7. commit
8. `./spec-dock/scripts/spec-dock issue finish`

## 7. Finish条件

- CLOS-001〜CLOS-007がすべてclosed。
- fresh `spec-reviewer` passがある。
- runtime help textを変更した場合はfresh `code-reviewer` passがある。
- 必須検証がpassしている。
- `report.md` に no-per-Issue-PR rationale、`iss-00307` へのPR delivery defer、検証結果、残リスクが記録されている。
- 実装差分がcommitされている。
- `./spec-dock/scripts/spec-dock issue finish` を実行できる。
