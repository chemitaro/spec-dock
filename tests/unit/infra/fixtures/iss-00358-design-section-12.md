<!-- Copied from iss-00358 design.md at 573902fd7 before the canonical cutover moved specs off main. -->

## 12. Epic-level IC-1 contract input

358は次の値をmachine-readableな契約入力として提供する。Epic orchestratorは、358と関係するRuntime / scaffold Issueが完了した後にこの入力を消費し、実生成との照合を別のEpic-level統合確認として行う。358のIssue完了は、その後続確認に依存しない。

```text
scope_files = [requirement.md, design.md, plan.md, report.md]
contract_version = s09-2026-08-11
consumer = epic-00356-authoring-integration
report_required_headings = [Outcome, Verification, Residual Risks / Follow-ups]
report_optional_heading = Notes
report_empty_content_valid = true
report_runtime_gate = false
current_artifact_types = [blank, research, interview, disc, decision-candidate, adr]
issue_plan_files = [plan.md]
base_plan_guide = docs/authoring/issue-plan.md
level_guides = docs/authoring/issue-plan-levels/{light,standard,strict,critical}.md
planning_level_runtime_owned = false
```

IC-1はEpic orchestratorが後続で行う文書上の統合確認であり、358のRuntime gateではない。content / Guide / heading mismatchは358へ、copy / parser / filename mismatchは該当Runtime Issueへroutingする。統合確認が未実施でも、358-owned contract入力と本Issueの品質ゲートがpassすれば358は完了できる。
