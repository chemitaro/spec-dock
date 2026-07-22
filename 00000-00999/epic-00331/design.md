---
種別: 設計書（Epic）
ID: "epic-00331"
タイトル: "ChatGPT Planning and Advisory Review"
関連GitHub: ["chemitaro/spec-dock#331"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
依存: ["requirement.md"]
親: ["init-00322"]
candidate_semantic_key: "planning-and-advisory-review"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/design.md"
---

# epic-00331 ChatGPT Planning and Advisory Review — 設計（どう実現するか）

## 1. Actor Journey

```text
Issue Planning Workflow usage after implementation:
Issue／Seed → Planning Candidate or exact git-bound Planning state
→ fresh Planning Review PASS on the exact reviewed identity
→ Human Issue Plan Adoption and Implementation-Start Authorization bound to that identity
→ archive: deterministic canonical adoption + candidate-to-canonical parity
   or git-bound: exact reviewed-content canonical／commit parity
→ required validation／planning publication
→ execution-ready

Initiative Portfolio Planning Workflow usage after implementation:
Goal → Initiative Bundle → Epic Bundles → Issue Projection
→ Consolidation → Candidate ZIP → Review → Human Approval
→ Epic／Issue Node materialization

Targeted Review:
Target＋Perspective → ChatGPT advisory Review → result
```

## 2. Walking Skeleton Strategy

最初のvertical sliceは`Implement ChatGPT Issue Planning Workflow`とする。Adapter、Git binding、Oracle、Prompt、file placement、Planning Review、tests、docs、projectionを一つのIssueで実装する。汎用CLI skeleton、Inventory schema、Metrics基盤等を先行Issueにしない。

二つ目の利用例でInitiative／Epic Portfolio Planningへ拡張し、そこで初めて共通化が必要な部分を抽出する。

### 2.1 Planning lifecycleとWorkflow capability implementationの境界

```text
現在のInitiative／Epic Planning
→ このCandidateで完了しHumanが承認する

各IssueのPlanning
→ 各Issue開始時にJITで行う

Epic 1 implementation Issues
→ 上記Planningを実行可能にする再利用可能なSpecDock Workflowを実装する
```

Epic 1の各Issueは、current Portfolio replanning、downstream Issue Requirement／Design／Plan pre-authoring、Human approval bypass、Planning-only completionをIssue-localに禁止する。実装中にmaterialなPortfolio gapを発見した場合は、下位Issue内で構造を変更せず、上位Planningへescalateする。

Dogfood Planningは、実装したWorkflowのAcceptance Evidenceであり、Issueの主成果物ではない。

## 3. Universal Planning Candidate Workflow

```text
Scope Planning output
→ Scope-minimal immutable Candidate
→ Skill chooses archive-candidate or git-bound Review
→ fresh Reviewer
→ P0／P1: Skill chooses Semantic or Mechanical Revision lane
→ complete new Candidate identity／bounded Git correction
→ fresh Review
→ PASS
→ Scope positive Human Gate
→ deterministic canonical adoption／parity
```

### 3.1 Scope packages

- Issue Candidate: `requirement.md`、`design.md`、`plan.md`、source baseline、manifest／checksums。
- Epic Candidate: Epic三文書、Issue Boundary Map、関連ADR、source baseline、manifest／checksums。
- Initiative Candidate: Thin Initiative Bundle、全Epic Bundle、Issue Boundary Maps、dependency、ADR、materialization contracts。

### 3.2 Review mode selection

- archive-candidate is default for pre-canonical semantic iteration。
- git-bound fallback requires a material reason: actual path／CI、GitHub inline review、compliance candidate commit、non-deterministic placement、ZIP inspection limits。
- canonical mechanical correction prefers git-bound。
- canonical semantic correction creates a new Candidate from current canonical state。
- Checkpoint／Delivery／PR／Epic Review remains git-bound。

### 3.3 Revision lane selection

Semantic Revision changes Requirement／Architecture／slice／dependency／authority／Acceptance Criteria／Gate／Workflow and is performed by ChatGPT Blue Team as a complete replacement Candidate.

Mechanical Revision is allowed only when path／field／old-new literal／meaning invariant／diff budget are closed before editing. It may be performed by Main／Codex／deterministic script. Any ambiguity routes to Semantic Revision. Both lanes create a new Candidate identity and require fresh Review.

### 3.4 Adoption parity

ZIP Review PASS is not a permanent substitute for repository Review. It can be adopted without a second complete Semantic Review only under unchanged source HEAD、closed binding、Candidate-external diff 0、byte／semantic parity、validate／sync PASS. Otherwise the Workflow returns to a new Candidate or fresh Git-bound Review.

### 3.5 Issue Planning positive gate

Issue Candidate Review PASS is not `execution-ready`. The required paths are:

```text
archive: PASS on exact logical filename／ZIP SHA → Human approves exact logical filename／ZIP SHA → deterministic canonical adoption → candidate-to-canonical parity → required validation／planning publication → execution-ready

git-bound: PASS on exact reviewed HEAD／exact target paths → Human approves exact reviewed HEAD／exact target paths → exact reviewed-content canonical／commit parity → required validation／planning publication → execution-ready
```

The workflow records Human identity／time and the complete reviewed identity, including exact target paths for git-bound mode. Review-only, Human-Gate-only, parity-only, wrong-identity, source-drift, semantic-adoption-diff, parity-failure, and validation／planning-publication-failure fixtures must not start Executor. `PLANNING-ADOPTION-GATE.md` and ADR 21 are authority.

## Closed Planning Adoption negative-fixture matrix

E1-I1 is the producer implementation authority. Its local Design explicitly requires every fixture below; no central-reference shortcut is allowed.

| ID | Required rejected condition | Expected result |
|---|---|---|
| `PA-NF-01` | archive Review PASSだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-02` | git-bound Review PASSだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-03` | Human Gateだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-04` | parityだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-05` | wrong logical Candidate filenameまたはwrong Candidate SHAでadoption／startを要求する | reject |
| `PA-NF-06` | wrong reviewed HEADまたはwrong exact target pathsでadoption／startを要求する | reject |
| `PA-NF-07` | source drift後にreview identityを再確立せずadoption／startを要求する | reject |
| `PA-NF-08` | adoption中にsemantic mutationが発生した内容からstartを要求する | reject |
| `PA-NF-09` | parity failure後に`execution-ready`／Executor startを要求する | reject |
| `PA-NF-10` | validationまたはplanning-publication failure後に`execution-ready`／Executor startを要求する | reject |

Both E1-I1 producer and E2-I1 consumer acceptance must prove every row independently; central-reference-only or generic `negative fixtures` wording is non-conforming.

## 4. Planning Prompt Contract

共通fragment:

- Goal／Scope identity。
- Authoritative repository context。
- Hierarchical Depth Contract。
- Slicing Contract。
- Evidence／success criteria。
- Output contract。
- final self-review requirement。

Initiative Promptは全Epic BundleとIssue Boundaryまで、Epic PromptはIssue Seedsまで、Issue Promptは実装計画までを要求する。

## 5. Review Contract

Planning Review入力:

- 対象Bundle。
- 親Contract。
- Initiative時は全Epic Bundles、Issue Boundary Maps、dependency、ADR。
- source repository branch／HEAD。

Perspective:

- specification。
- architecture。
- executability。
- decomposition-quality。
- repository-conventions（適用時）。

archive Planning Reviewはlogical Candidate filename、observed transport filename、Candidate ZIP SHA、internal root、MANIFEST identity、exact source HEAD snapshotへbindする。closed`(N)`aliasだけをnormalizeできる。git-bound Planning Reviewはreviewed HEAD、target paths、必要なsemantic BASEへbindする。Reviewerはどちらのmodeでも変更せずfindingとverdictだけを返す。exact content identityを検査できない場合は`insufficient-evidence`とし、同じFormal identityのまま別transportへsilent fallbackしない。Dynamic placeholderは`PLACEHOLDER-ORACLE-MAP.json`だけをauthorityとし、static fileのliteral exampleはexact hashで扱う。


## 6. Skill／Wrapper Boundary

Planning SkillはScope package、Review mode、Revision lane、Human Gateを判断する。Oracle wrapper／scriptはrepository context injection、file attachment、SHA、safe extraction、result retrieval、parityを決定的に実行する。wrapperへsemantic materiality classifierを持たせない。

## 7. Materialization

Portfolio materialization uses one Candidate-SHA ledger and the following explicit subcontracts:

```text
C0 Node input／source／template／Artifact preflight
→ old Portfolio retirement
→ 3 Epic／7 Issue create／bind
→ Runtime scaffold exact verification
→ exact 9 dependencies
→ Initiative replacement
→ bound Epic replacement
→ Artifact placement／Epic-local ADR accepted render
→ pre-commit report disposition
→ one commit／push／remote verification
```

All Node inputs come from `NODE-MATERIALIZATION-MAP.json`; exact source Runtime pure validation runs before destructive mutation. New Epic docs do not assume absent destinations: `new epic` scaffold bytes must be `runtime-scaffold-exact` before approved binding templates can replace them. Every Artifact follows filename-derived identity and `ARTIFACT-MATERIALIZATION-MAP.json` disposition. Epic-local ADRs remain proposal templates until exact Human approval and then use `EPIC-ADR-ADOPTION.md` to render accepted canonical front matter and mirror eligibility. Initiative report remains pre-commit and publication observations remain in Git／remote／Workbench ledger.

Remote Issue bindings use link-existing recovery; valid local Nodes are never recreated. All file replacement resumes from actual bytes and uses Human-approved rollback for partial cleanup or unwind.

## 8. Sensitive Data and Process Invocation

- Planner／Reviewer Prompt、Operator Context、GitHub外file、Oracle／Human Relay package、Workbench、Candidate ZIP、Artifactへsensitive dataを含めない。Humanが必要と判断した情報は最小redacted subsetだけを使う。
- Oracle wrapper、backend、helperのprocess launchはdirect argvをdefaultとし、Prompt／pathをshell command stringへ補間しない。
- shell semanticsが不可避な例外は、Human-approved Design、固定command template、untrusted input拒否／encoding、injection regression test、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とする。
- secret fixture、`.env` path、shell metacharacterを含むPrompt／pathを使ったnegative testsと、shell exception rollback drill／evidence checkをE1-I1のacceptance evidenceへ含める。

## 9. Error and Recovery

- GitHub access failure: fail closed。
- Oracle transport failure: session recovery／Human Relay。
- ZIP semantic failure: `insufficient-evidence`。non-formal diagnostic後に新しい完全ZIPとfresh Formal Reviewへ戻る。
- Review P0/P1: Semantic findingはChatGPT complete revision、closed mechanical findingはdeterministic local revision。いずれもnew identity／fresh Review。
- Human rejection: feedback→new ZIP→fresh Review。
- Runtime `pre_github_fail`: precondition修正後に同createをretry。
- `post_github_remote_only_fail`: remote numberをledgerへbindし、`--github-issue`でresumeまたはverified close後にbinding clear。
- post-GitHub local／cleanup failure: `doctor`でlocal stateを分類し、valid Nodeならno-rerun、absentならlink-existing、partialならHuman-approved bounded cleanupまたはblocked investigation。
- post-sync failure: valid Node bindingを保持し`sync`からresume。createし直さない。
- dependency／Bundle placement failure: existing edge／hashを照合しmissing／absentだけをresumeする。
- どのmaterialization failureでもcommit／pushせず、Candidate ZIPとWorkbench ledgerを保持する。

## 10. Distribution

同一Issueでprovider、installed、dogfood projection、tests、docsを更新する。projectionだけの独立Issueを作らない。E1-I3はplanning-specific legacy surfaceだけをmutation対象とし、remaining shared／execution／delivery surfaceはEpic 3へ明示的に委譲する。
