# GPT-5.6 Prompt Tuning Evaluation

## Scope

- Source branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- Planning source HEAD: `a50f9a1de7301f0c64f0f1d23092bd7ee888043e`
- ChatGPT session: `iss00334-prompt-tuning`
- Model evidence: `requested=Pro`、`resolved=Pro`、`verified=yes`
- GitHub connector evidence: exact branch／HEAD identical、`ahead_by=0`、`behind_by=0`、default branch unused
- Theme: role resourceをtask固有の責務へ限定し、共通のformal output、Human authority、mutation boundaryをtransportへ一度だけ置く

## Deterministic verification

| Gate | Result |
|---|---|
| Red-first | `3 failed, 20 passed`。共有境界重複、`as Planner`外部参照、Planner文字数超過を検出 |
| Focused Prompt tests | `23 passed` |
| Relevant regression | `66 passed, 4 skipped` |
| Ordinary PR fast lane | `1096 passed, 2119 skipped` |
| Ruff | PASS |
| Build | wheel／sdist PASS |
| SpecDock validate | `nodes=227` |
| Provider／dogfood parity | 4/4 byte-identical |
| Diff scope | exact 9 paths |
| `git diff --check` | PASS |

## Prompt size

| Scenario | Baseline | Candidate | Reduction |
|---|---:|---:|---:|
| Median Planner | 3,784 | 3,246 | 538 |
| Adversarial Reviewer | 3,978 | 3,603 | 375 |
| Semantic Revision edge | 3,169 | 3,146 | 23 |
| **Total** | **10,931** | **9,995** | **936 (8.6%)** |

Static resource size:

| Resource | Baseline | Candidate |
|---|---:|---:|
| Planner | 1,216 | 659 |
| Reviewer | 1,655 | 1,261 |
| Revision | 768 | 726 |
| Transport | 799 | 818 |

## Blind A/B evaluation

評価者にはbaseline／candidateの由来を渡さず、A／Bとして同じcritical checklistで評価した。Bがcandidateである。

| Scenario | A | B | Critical failures A | Critical failures B | Preferred |
|---|---:|---:|---:|---:|---|
| Median Planner | 97 | 99 | 0 | 0 | B |
| Adversarial Reviewer | 98 | 99 | 0 | 0 | B |
| Semantic Revision edge | 85 | 100 | 2 | 0 | B |

PlannerとReviewerはcritical contractを両variantが保持し、Bは反復を減らした点で僅差優位だった。RevisionのAはcompanion要件を`as Planner`へ外部参照して自己完結していなかった。Bは必須subject、subordinate authority、4 PlantUML roleを明示し、このcritical failureを閉じた。

## Adopted result

Candidate Bを採用する。public CLI／schema、synthesizer、adapter、exact GitHub gate、default-branch prohibition、attachment trust boundary、Human-only mutation authority、typed ZIP／closed JSON、fail-closed behaviorは変更していない。

本artifactはPrompt tuningの実証記録であり、canonical Requirement／Design／append-only Planを変更しない。artifact自体の追加ReviewはHuman指示により不要である。

## Operator-side wrapper observation

`chatgpt-use` wrapperはPromptへcurrent branchとdefault branchを自動挿入し、current branchを開けない場合のdefault fallbackを記述する。今回のtask Promptはexact branch／HEAD以外を明示禁止し、ChatGPT回答もexact branch／HEAD identicalおよびdefault branch unusedを確認したため採用した。ただし、exact-branch-only planningでwrapper前置きとtask Promptが競合し得る点は、wrapper interfaceの改善候補として残る。
