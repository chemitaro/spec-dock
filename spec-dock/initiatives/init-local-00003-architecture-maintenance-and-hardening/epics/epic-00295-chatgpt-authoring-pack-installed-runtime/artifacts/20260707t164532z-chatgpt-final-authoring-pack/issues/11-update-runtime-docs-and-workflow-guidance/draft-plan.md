---
種別: "Issue draft plan"
ID: "epic-00295-11"
Issue候補: "C11"
タイトル: "runtime docs / reference docs / workflow guidance を更新する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md", "draft-design.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C11 runtime docs / reference docs / workflow guidance を更新する — draft plan

## Step sequence

1. runtime docs と reference docs の target files を更新する。
2. workflow docs に skill ordering / stop gates / relay policy を反映する。
3. local-context mode と EAL disposition requirement を文書化する。
4. deferred command warning と manual fallback を追加する。
5. docs consistency checks と git diff --check を実行する。

## Dependencies

- 03-implement-github-sync-preflight
- 07-validate-initiative-epic-and-epic-issue-candidates
- 08-validate-issue-draft-adoption-and-selected-skeleton
- 09-add-chatgpt-authoring-skill-and-update-planning-skills
- 10-implement-approval-check-and-stop-gate-reports

## Verification

- docs trace matrix review
- command example smoke check
- git diff --check
- deferred command wording check
- terminology consistency check

## Finish evidence

- Completed scope summary.
- Files changed / docs changed inventory.
- Test and validation output summary.
- Known residual risks and deferred items.
- Evidence that forbidden authority claims were not introduced.
- Relay evidence: 中間 Issue のため PR delivery は行わない。finish 時に no-per-Issue-PR rationale、local verification、Issue 12 への dependency edge を記録する。

## Relay policy

中間 Issue のため PR delivery は行わない。finish 時に no-per-Issue-PR rationale、local verification、Issue 12 への dependency edge を記録する。

## PR delivery policy

No PR delivery in this intermediate Issue. PR delivery is deferred to Issue 12.
