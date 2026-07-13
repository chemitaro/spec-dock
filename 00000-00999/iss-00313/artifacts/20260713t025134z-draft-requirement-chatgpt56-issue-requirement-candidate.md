---
種別: 要件定義書（Issue候補）
ID: "iss-00313"
タイトル: "PR Merge Preparer の修復回数制限を廃止し、証拠駆動の継続判定へ置換する"
関連GitHub: ["#313"]
状態: "draft-candidate"
作成者: "ChatGPT 5.6 Pro"
最終更新: "2026-07-13"
親: ["epic-00158", "init-local-00003"]
authority: "evidence_only"
adoption_status: "unreviewed"
candidate_profile: "strict"
profile_authority: "recommendation_only"
source_manifest_hash: "5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d"
---

# iss-00313 PR Merge Preparer の修復回数制限を廃止し、証拠駆動の継続判定へ置換する — Issue 要件定義候補

> この文書は evidence-only / unreviewed の authoring candidate である。local integration decision、`.assurance.json` mutation、`assurance profile` decision、fresh reviewer approval、implementation handoff eligibility、pull-request handoff eligibility、pull-request handoff を表さない。

## 0. 文書の位置づけ

### 0.1 この文書が定義すること

- `github-pr-merge-preparer` の blocking repair continuation に必要な観測可能な workflow outcome。
- 固定 attempt cap と同一 failure-family 再発停止を廃止した後の安全な継続条件。
- integrated PR repair batch と ChatGPT consultation の必須 evidence boundary。
- main orchestrator、ChatGPT、repair worker、`github-pr-observation`、human gate の責務境界。
- provider source、templates、dogfooding mirror、tests の受け入れ条件。
- compatibility、failure / recovery、security / privacy、scope escalation 条件。

### 0.2 この文書が定義しないこと

- ChatGPT API、browser automation、connector、runtime command の実装方法。
- `github-pr-observation` の stdout JSON schema または GitHub API collection logic。
- repair worker が個々の product defect をどう修正するか。
- GitHub review reply / resolve / dismiss、merge、branch deletion、issue close / finish。
- canonical docsへの自動採用、profile authorization、reviewer verdict。

## 1. 結論と Issue 境界

### 1.1 境界判定

- 判定: `single_issue_coherent`
- Parent: `epic-00158`
- Epic repair: 推奨しない
- `information_insufficient`: 該当しない

この Issue は、次の単一 outcome に閉じる。

> blocking PR repair を、固定回数で機械的に打ち切らず、同時に blind / unbounded retry にもせず、current observation、integrated batch analysis、fresh ChatGPT consultation、materially distinct repair strategy、scope / safety gate に基づいて継続または human gate と判定できる。

skill、agent prompt、repair-batch templates、tests はこの outcome を実行・記録・検証する同一 contract surface である。

### 1.2 境界を破る条件

次が必要になった場合、この Issue 内で吸収せず、plan amendment / follow-up Issue / ADR / Epic repair のいずれかへ送る。

- ChatGPT invocationを SpecDock runtime / CLI に実装する。
- consultationの永続化用に新しい machine-readable schemaまたはDBを導入する。
- `github-pr-observation` stdout JSONへ judgment fieldsを追加する。
- GitHub review conversation mutation、merge、branch deletion、issue lifecycle mutationを追加する。
- 複数の unrelated skillsへ共通 retry frameworkを導入する。
- secrets / authentication materials / private data を consultation payloadへ送る必要が生じる。
- forward-only migrationまたは既存 artifact の破壊的変換が必要になる。

## 2. 概要

### 2.1 目的

現行 `github-pr-merge-preparer` は blocking repair loop に、P0、同一 family の P1、invocation total の固定 attempt capを置き、同一 `root_cause_family` が repair commit後に再発すると human gateへ停止する。この count-based policy は、修正可能な failureであっても、証拠や新しい strategyを評価する前に継続を打ち切る。

本 Issue は固定回数を continuation authority から外し、blocking batch 全体への ChatGPT consultationと main orchestrator の明示 dispositionを含む evidence-gated policyへ置換する。

### 2.2 完了後に観測できること

- skill本文から固定 P0 / P1 / total attempt capが消えている。
- 同一 family 再発だけでは repair loopを停止しない。
- blocking repair delegation前に current integrated batchを対象とした ChatGPT consultationが要求される。
- materially changed evidence、family classification、または strategyがある場合、consultation freshnessが再評価される。
- consultation outputは提案証拠であり、orchestrator dispositionなしにworkerへ渡らない。
- iteration index / attempt countは記録できるが、limitまたはapproval authorityではない。
- no viable new strategy、stale/unsafe evidence、scope expansion、既存hard stopはhuman gateへ進む。
- repair batchはconsultation、strategy delta、disposition、re-observation result、continuation decisionを監査可能に記録する。
- provider sourceとinstalled/dogfooding mirrorが一致し、generated batchにも同じ契約が現れる。

### 2.3 完了後に観測できてはいけないこと

- 「P0は1回」「P1は2回」「合計4回」など、固定回数をstop authorityとする文言。
- 「同一 familyが再発した」という理由だけの自動停止。
- ChatGPT recommendationの自動採用、fresh reviewer approval扱い、repair authorization扱い。
- verbatim model conversation record、secret、authentication material、asymmetric signing material、host-local absolute pathのbatch/canonical docsへの保存。
- consultation不可をsilent bypassしてrepair delegationする挙動。
- P2 / P3 findingだけを理由にbranch mutationする挙動。
- merge / auto-merge / thread resolve / issue finishなどの新しいGitHub mutation。

### 2.4 Issue の種類

- [x] 既存振る舞いの変更
- [x] 既存振る舞いの不具合修正 / policy hardening
- [x] 仕様・文書の明確化
- [x] テンプレート変更
- [x] workflow / skill / agent導線の変更
- [ ] runtime CLI挙動変更
- [ ] migration / persistence変更
- [ ] security-sensitive implementation

## 3. 背景・現状

### 3.1 Current workflow contract

`github-pr-merge-preparer` は、PR作成または発見、latest-head observation、CI / Codex review triage、blocking repair delegation、push確認、re-observation、merge-prepared evidence報告を調整する。merge自体、review reply / thread resolution / dismissal、issue closeは所有しない。

現行の fix-loop policy は概ね次の通りである。

- P0: default 1 autonomous repair attempt。ただし trivial / local の例外あり。
- same failure familyのP1: default 2 attempts。
- total autonomous repair attempts: default 4 per invocation。
- repair commit後に同じ `root_cause_family` が再発した場合は停止。
- permission/auth、external/flaky、base conflict、unknown failure、requirement expansion、breaking/migration/secret/deployment impact、ambiguous review intent、platform-only conversation resolution等はhuman gate。

repair-batch templateも、同一 family再発とloop-limit到達をStop Conditionsとして持つ。

### 3.2 問題

- 回数はfailureの修復可能性、新しいevidence、strategy qualityを表さない。
- 一回目のfixが不完全だった場合と、root-cause hypothesisが誤っていた場合と、同じ症状の別原因を区別できない。
- 複数blocking findingを個別コメント単位で扱うと、共有root causeとcross-file contractを見落とす。
- capだけを削除するとblind retryやrunaway mutationを許すため、代替のsemantic termination gateが必要になる。
- ChatGPT-first authoring/evidence boundaryがrepositoryに導入された後も、repair loop側にはintegrated consultationとorchestrator dispositionの明示契約がない。

### 3.3 根拠・情報源

#### Parent

- `epic-00158/requirement.md`
  - `E-RQ-001`: skills own operational workflow spine。
  - `E-RQ-005`: ChatGPT / delegated output is evidence until main-orchestrator adoption。
  - `E-RQ-007`: provider source authority + dogfooding mirror verification。
  - `E-AC-004`: missing / stale / failed / unavailable / denied 等はpassではない。
- `epic-00158/design.md`
  - provider source-first、canonical docs main-orchestrator-owned、external/delegated outputは採用前evidence。
- `epic-00158/plan.md`
  - Issueはsmall/reviewable、parent trace、provider/mirror verification、rollback/compatibility/EALを持つ。

#### Current implementation contract

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md`

#### Historical rationale

- `iss-00178 Review Feedback Triage`
  - batch inventory、repair unit、review-clean / merge-prepared分離、observation collection-only boundary。
  - 当時はrepeated failure classをhuman gateにするfix-loop limitsを採用した。

#### Prompt-pack local context

- `research-pr-merge-preparer-repair-limit-clarification-baseline`
- `interview-same-family-repair-recurrence-continuation-policy`
- `user-proposal-chatgpt-assisted-integrated-pr-repair-batch`
- `research-chatgpt-consultation-integrated-pr-repair-workflow`
- `interview-mandatory-chatgpt-consultation-scope`
- `chatgpt-raw-integrated-pr-repair-workflow-consultation`
- `disc-adopted-integrated-pr-repair-workflow-synthesis`

これらのbodyは未検証であり、filenameとprompt metadataのみをcandidate framingへ使用した。

## 4. 親スコープと継承条件

### 4.1 Parent Initiative

- ID: `init-local-00003`
- 継承制約:
  - architecture maintenance / hardeningの範囲に閉じる。
  - provider sourceとconsumer/dogfooding projectionを混同しない。
  - user-authored / canonical artifactsを破壊しない。

### 4.2 Parent Epic

- ID: `epic-00158`
- Relevant requirement IDs:
  - `E-RQ-001`, `E-RQ-002`, `E-RQ-005`, `E-RQ-007`
- Relevant acceptance IDs:
  - `E-AC-001`, `E-AC-004`, `E-AC-005`, `E-AC-006`, `E-AC-007`
- 継承する契約:
  - skill is first-read workflow authority。
  - docs / templatesはskill authorityを補助し、templatesはauthorityを所有しない。
  - ChatGPT outputはevidence-only。
  - main orchestratorが採否とcanonical reflectionを所有する。
  - provider sourceを先に変更し、mirrorをvalidate / sync / targeted inspectionする。

### 4.3 このIssueで再定義しないもの

- `github-pr-observation` のcollection-only responsibility。
- stdout JSONのauthoritative observation evidence semantics。
- P0/P1 blocking、P2/P3 non-blockingというseverity contract。
- P2/P3だけを理由にbranch mutationしないpolicy。
- merge-preparedとreview-cleanの区別。
- human-only GitHub conversation resolution / merge actions。
- SpecDock canonical authoring / assurance / reviewer workflow。

## 5. Actors、Trigger、代表シナリオ

### 5.1 Actors

| Actor | 責務 | このIssueとの関係 |
|---|---|---|
| Main orchestrator | evidence freshness、triage、consultation disposition、continuation/human-gate判断 | final workflow judgment owner |
| `github-pr-merge-preparer` | pull-request handoff loopのoperational spine | primary changed contract |
| `github-pr-observation` | latest-head CI/review evidence collection | unchanged upstream evidence producer |
| ChatGPT | integrated batchに対するoptions / risks / strategy proposalを生成 | evidence-only consultant |
| Repair worker | approved scopeとstrategyに従いbounded implementationを行う | disposition後のみdelegateされる |
| Human | ambiguous/high-risk/unsupported casesとmergeを判断 | hard gate owner |
| Maintainer/reviewer | skill/template/test contractを検証 | downstream review owner |

### 5.2 Trigger

- latest-head observationにP0/P1、required check failure、merge blocker、またはbranch mutationを要するblocking familyが存在する。
- repair後のre-observationでblocking familyが残存・再発・新規発生する。
- existing repair batchをresumeし、current head / evidence / strategy freshnessを再評価する。

### 5.3 シナリオ SC-001: 初回blocking batch

- Given:
  - latest-head observationが複数のP0/P1またはrequired check failuresを返す。
- When:
  - merge preparerがrepair delegationを検討する。
- Then:
  - current observationの全blocking itemsをintegrated batchにinventoryする。
  - root-cause family、coupling、allowed scope、testsを分析する。
  - sanitized batch evidenceでChatGPT consultationを実施する。
  - orchestratorがrecommendationsをdispositionし、使用するstrategyだけをworker handoffへ変換する。

### 5.4 シナリオ SC-002: 同一familyが再発

- Given:
  - repair commit後のlatest-head observationに同じfamily labelのblockerがある。
- When:
  - continuationを評価する。
- Then:
  - recurrenceだけでは停止しない。
  - stale observation、incomplete implementation、failed hypothesis、new evidence、mis-groupingを分類する。
  - prior strategyとの差分がmaterialで、fresh consultationとscope-safe validation pathがある場合だけ継続できる。
  - materially distinct strategyがない、またはevidenceが不足する場合はhuman gateにする。

### 5.5 シナリオ SC-003: Consultation unavailable / unsafe

- Given:
  - ChatGPT consultationがunavailable、denied、failed、またはsanitized inputを作れない。
- When:
  - blocking repair delegationを行おうとする。
- Then:
  - consultationをpass相当と扱わない。
  - batchにstatus、reason、last safe evidenceを記録する。
  - autonomous repairを開始せずhuman gateへ移る。

### 5.6 シナリオ SC-004: Non-blocking only

- Given:
  - P2/P3、optional check failure、follow-up/no-action itemだけが残る。
- When:
  - merge-preparedを評価する。
- Then:
  - それだけを理由にbranch mutationまたはmandatory repair consultationを開始しない。
  - rationale / residual riskをbatchに残し、既存merge-prepared predicateで判断する。

## 6. 用語

### TERM-001: Fixed attempt limit

P0 1回、same-family P1 2回、total 4回など、iteration countをrepair continuation / stopのauthoritative criterionにするrule。

### TERM-002: Integrated blocking repair batch

current latest-head observationでbranch mutationを要するblocking itemsを、個別コメントではなく、共有root cause、coupling、scope、test obligationsを含む一つのdecision surfaceとして扱うbatch。

### TERM-003: Material change

consultation / strategy freshnessを無効化するほどの意味差分。例:

- head SHAまたはobservation trigger boundaryの変更。
- blockerの追加・削除・severity変更。
- root-cause family groupingの変更。
- prior strategyの失敗または不完全実装の発見。
- allowed paths、requirement、compatibility、security impactの変更。
- validation planの変更。

単なるtimestamp、formatting、説明文の非意味差分はmaterial changeではない。

### TERM-004: Strategy delta

prior attempted strategyに対し、root-cause hypothesis、files/behavior boundary、implementation approach、validation approachのどれが変わるかを明示した差分。単なる言い換えはstrategy deltaではない。

### TERM-005: ChatGPT consultation evidence

sanitized integrated batch inputに対するChatGPTの提案を、provenance、scope、freshness binding、summary、open risksと共に保存したevidence。authorizationまたはcanonical decisionではない。

### TERM-006: Orchestrator disposition

ChatGPT recommendationごとにmain orchestratorが記録する `use` / `partial-use` / `reject` / `defer` / `human-gate`。worker handoffは `use` または明示された `partial-use` の内容だけを根拠にできる。

### TERM-007: Hard human gate

attempt countに関係なくautonomous continuationを禁止する既存または本Issueのsafety condition。

## 7. スコープ

### 7.1 In scope

1. `github-pr-merge-preparer/SKILL.md`
   - fixed count limitsの削除。
   - recurrence analysis / continuation policy。
   - mandatory integrated ChatGPT consultation gate。
   - evidence-only disposition and freshness。
   - semantic stop / human-gate conditions。
2. `agents/openai.yaml`
   - count-boundedと誤読されないevidence-gated repair wording。
3. Skill-local PR repair batch template。
4. Shipped artifact PR repair batch template。
5. Shipped discussion PR repair batch template。
6. Generated artifact / template / installed-copy contractを検証するtargeted tests。
7. Provider-first update後のdogfooding parity、validate、sync、targeted inspection。
8. Existing batch resume compatibilityの文書契約。

### 7.2 Out of scope

- ChatGPT invocation implementation。
- new CLI options、runtime commands、environment variables、config schema。
- machine-readable consultation / retry schema validation。
- observation JSON changes。
- repair worker implementation framework。
- automatic merge / review conversation mutation。
- GitHub issue lifecycle mutation。
- unrelated docs / skillsへのretry policy展開。
- historical artifact bulk migration。
- `.assurance.json` mutation。

### 7.3 Must not change

- `github-pr-observation` collection-only boundary。
- latest-head freshness requirement。
- required / non-required check semantics。
- P0/P1 repair priorityとP2/P3 non-mutation policy。
- merge-prepared / review-clean distinction。
- forbidden writes/actions in current skill。
- branch protection / conversation resolution human gate。
- local integration decision and reviewer authority。

## 8. 要求される振る舞い

### BH-001: Fixed attempt capをcontinuation authorityから除外する

- Given: skillまたはtemplateがrepair iterationを扱う。
- When: continuation / stopを判断する。
- Then: numeric attempt countだけではstop / continueを決めない。
- And: count / iteration indexはtelemetryとして記録してよい。

### BH-002: Blocking itemsをintegrated batchとして評価する

- Given: current observationに複数blocking itemsがある。
- When: repair strategyを作る。
- Then: 全blocking items、shared root cause、coupled files、tests、nonblocking collateralを一つのbatch viewで分析する。
- And: raw findingから直接workerへ委任しない。

### BH-003: Branch-mutating blocking repair前にChatGPT consultationを必須にする

- Given: current batchにbranch mutationを要するblocking itemがある。
- When: workerへrepairをdelegateしようとする。
- Then: current integrated batchにboundしたfresh ChatGPT consultation evidenceが存在する。
- And: unavailable / failed / denied / stale / unsafe consultationはpassではない。

### BH-004: ChatGPT outputをevidence-onlyとしてdispositionする

- Given: consultation outputがある。
- When: strategyを選ぶ。
- Then: orchestratorはrecommendationごとにdispositionとrationaleを記録する。
- And: outputはlocal integration decision、fresh reviewer approval、repair authorizationを自動的に持たない。

### BH-005: 同一family再発を再分析triggerにする

- Given: prior repair後に同一family labelのblocking itemが観測される。
- When: continuationを評価する。
- Then: recurrence class、prior strategy result、new evidence、strategy deltaを分析する。
- And: recurrenceだけではstopしない。

### BH-006: Materially distinct strategyがある場合だけ継続する

- Given: blockerが残る。
- When: autonomous repairを継続する。
- Then: prior strategyとmaterialに異なるbounded strategy、fresh consultation、allowed scope、validation pathがある。
- And: same ineffective strategyの反復はhuman gateにする。

### BH-007: Hard human gateを維持する

- Given: permission/auth、external/flaky、base conflict、unknown failure、requirement expansion、breaking/migration/secret/deployment impact、ambiguous intent、platform-only conversation action、unapproved trigger、stale trigger、resume metadata欠落のいずれかがある。
- When: continuationを評価する。
- Then: attempt countに関係なくhuman gateへ進む。

### BH-008: Consultationとiterationをbatchに監査可能に記録する

- Given: consultationまたはrepair iterationを実施する。
- When: batchを更新する。
- Then: head SHA、observation status、family set、recurrence class、prior/proposed strategy、strategy delta、consultation reference/freshness、orchestrator disposition、fix commit、re-observation、continuation decisionを記録する。
- And: verbatim model conversation recordやunsafe payloadを記録しない。

### BH-009: Provider / mirror / generated outputを同一contractにする

- Given: provider sourceを変更する。
- When: standard update / scaffold / artifact creationとtargeted testsを実行する。
- Then: installed/dogfooding copiesとgenerated repair batchが同じcontinuation / consultation contractを表す。

### BH-010: Existing batchを非破壊でresumeする

- Given: old templateで作られたbatchが存在する。
- When: current workflowでresumeする。
- Then: front matter、inventory、historical evidenceを保持し、current headにboundしたconsultation / continuation ledgerを追記してからrepairを再開できる。
- And: bulk migrationは要求しない。

## 9. 受け入れ条件

### AC-001: Numeric limits removed

- Actor: maintainer / reviewer
- 前提: provider skillと3 templatesを読む。
- 操作: fixed attempt cap / loop limit wordingを検索する。
- 期待結果:
  - P0 1回、same-family P1 2回、total 4回というdefault stop authorityが存在しない。
  - `loop limits reached` がStop Conditionsに存在しない。
  - iteration countはtelemetryでありlimitではないと明示される。
- 関連: `BH-001`

### AC-002: Recurrence is analysis trigger, not automatic stop

- 前提: same `root_cause_family` がrepair後に再発する。
- 操作: skillのcontinuation policyとbatch fieldsを確認する。
- 期待結果:
  - recurrence classification、prior strategy result、strategy delta、consultation freshnessを評価する。
  - recurrenceだけを理由にstopしない。
  - materially distinct strategyがない場合はhuman gateになる。
- 関連: `BH-005`, `BH-006`

### AC-003: Mandatory integrated consultation gate

- 前提: branch mutationを要するblocking batchがある。
- 操作: repair delegation sequenceを確認する。
- 期待結果:
  - triage完了後、worker handoff前にbatch-wide ChatGPT consultationを要求する。
  - consultationはcurrent head / observation / family set / strategy contextへboundされる。
  - consultationなしにraw findingからdelegateできない。
- 関連: `BH-002`, `BH-003`

### AC-004: Consultation freshness

- 前提: head、blocker set、family grouping、prior strategy outcome、allowed scope、validation planのmaterial changeがある。
- 操作: existing consultationを再利用しようとする。
- 期待結果:
  - existing consultationはstaleと判定される。
  - refreshするかhuman gateへ進む。
  - non-materialなformatting差分だけでは不必要にstaleにしない。
- 関連: `BH-003`, `BH-005`

### AC-005: Evidence-only authority

- 前提: ChatGPTがrepair recommendationを返す。
- 操作: worker handoff / batch updateを確認する。
- 期待結果:
  - orchestrator dispositionとrationaleがある。
  - `use` / `partial-use`以外のrecommendationはworker inputにならない。
  - consultationはlocal integration decision、fresh reviewer approval、merge readinessを主張しない。
- 関連: `BH-004`

### AC-006: Semantic continuation gate

- 前提: blocking itemが残る。
- 操作: continuation decisionを評価する。
- 期待結果: continueには全てが必要である。
  1. latest-head observation is fresh。
  2. blocking inventory and family grouping are complete。
  3. hard human gate is absent。
  4. consultation is fresh and safe。
  5. orchestrator disposition identifies a bounded strategy。
  6. strategy has a material delta where prior strategy failed。
  7. allowed paths / requirements / compatibility remain in scope。
  8. validation and re-observation path are explicit。
- 関連: `BH-006`, `BH-007`

### AC-007: Consultation failure is not pass

- 前提: consultation is unavailable / failed / denied / unsafe / stale。
- 操作: repair delegationを試みる。
- 期待結果:
  - no branch mutation is delegated。
  - batchにstatusとreasonを残す。
  - human gateへ進む。
- 関連: `BH-003`, `BH-007`

### AC-008: Hard stops preserved

- 操作: old/new skillのhuman gate categoriesを比較する。
- 期待結果:
  - permission/auth、external/flaky、base conflict、unknown、scope expansion、breaking/migration/secrets/deployment、ambiguous intent、platform-only actions、trigger/resume safetyが弱められていない。
  - count limitsだけが削除される。
- 関連: `BH-007`

### AC-009: Batch evidence contract

- 操作: 3 templatesを確認する。
- 期待結果:
  - `ChatGPT Consultation Gate` または同義sectionがある。
  - `Integrated Repair Strategy` または同義sectionがある。
  - iteration ledgerにhead/family/recurrence/strategy delta/consultation/disposition/fix/re-observation/decisionがある。
  - Stop Conditionsはsemantic hard stopsを表し、numeric capを含まない。
  - verbatim model conversation record貼付禁止が明示される。
- 関連: `BH-008`

### AC-010: Skill / prompt / template alignment

- 操作: `SKILL.md`、`openai.yaml`、3 templatesを横断確認する。
- 期待結果:
  - すべてがevidence-gated / integrated repairを同じ意味で表す。
  - `openai.yaml` がfixed-count bounded repairを暗示しない。
  - templateがskillのworkflow authorityを上書きしない。
- 関連: `BH-001`〜`BH-009`

### AC-011: Generated output regression

- 前提: temp repositoryで`new artifact pr-repair-batch`または既存supported generation pathを実行する。
- 操作: generated Markdownを確認する。
- 期待結果:
  - new continuation / consultation slotsが存在する。
  - old numeric stop markersが存在しない。
  - filename/front matter/type/parent/date behaviorは変わらない。
- 関連: `BH-009`, `BH-010`

### AC-012: Provider / mirror parity

- 前提: provider edits完了。
- 操作: repository-standard `spec-dock update .`、validate、sync、targeted comparisonを行う。
- 期待結果:
  - provider authorityと`.agents/` / `spec-dock/` projectionが一致する。
  - direct mirror-only hand editがない。
  - user-authored issue/artifact dataが保持される。
- 関連: `BH-009`

### AC-013: Non-scope remains unchanged

- 操作: diffを確認する。
- 期待結果:
  - observation script、runtime commands、GitHub mutation logic、assurance metadataに変更がない。
  - P2/P3-only mutation policyに変更がない。
- 関連: `CON-004`, `CON-005`, `CON-009`

### AC-014: Strict candidate plan completeness

- 操作: candidate planをreviewする。
- 期待結果:
  - requirement/design IDsとclosure indexが対応する。
  - step-local delegation contractsとconcrete test casesがある。
  - S90、strict review gate、S99、Final Exit Contractがある。
  - evidence-only / unreviewed statusとadoption gatesが保持される。

## 10. 例外・エッジケース

### EC-001: Stale observation masquerades as recurrence

- 条件: repair後のbatchが旧headのobservationを参照する。
- 期待: recurrence analysisを行わず、latest-head re-observationへ戻る。repairしない。
- 状態変更: branch mutationなし。

### EC-002: Same symptom, different root cause

- 条件: 同じmessage/CI checkだがevidenceが別root causeを示す。
- 期待: familyをsplit/reclassifyし、consultationをrefreshする。旧family countを引き継いでstopしない。

### EC-003: Prior strategy incompletely implemented

- 条件: root-cause hypothesisは有効だがworkerがplanned changeの一部を欠落した。
- 期待: incomplete scopeをevidenceで特定し、fresh consultation/dispositionでbounded completion strategyを選べる。単なる同一手順の無検証再実行は禁止。

### EC-004: Prior strategy disproved

- 条件: re-observationがprior hypothesisを否定する。
- 期待: materially new hypothesis/strategyがなければhuman gate。ある場合はrefresh consultation後に継続可。

### EC-005: Consultation suggests forbidden or expanded scope

- 条件: recommendationがruntime/API/migration/secret/requirement expansionを要求する。
- 期待: recommendationをrejectまたはhuman-gate dispositionにし、workerへ渡さない。必要ならplan amendment/follow-up。

### EC-006: Consultation cannot be safely sanitized

- 条件: diagnosisにsecret/private data/raw proprietary payloadが必要。
- 期待: external consultationを行わずhuman gate。unsafe dataをbatchへ貼らない。

### EC-007: Multiple coupled families

- 条件:一つのchangeが複数familyを同時に閉じる、または別々に修正するとconflictする。
- 期待: integrated batchでcouplingを明示し、一つまたは順序付きrepair unitsへgroupingする。

### EC-008: New blocker introduced by repair

- 条件: re-observationで新しいP0/P1 familyが出る。
- 期待: current batchをmaterially changedとして更新し、consultationをrefreshする。旧consultationの自動再利用禁止。

### EC-009: Optional/nonblocking failures remain

- 条件: blocking itemsはclosedだがP2/P3またはknown optional check failureが残る。
- 期待: rationale/residual riskを記録し、既存merge-prepared policyで判断する。修復回数制限Issueを理由に追加mutationしない。

### EC-010: Existing legacy batch resume

- 条件: consultation sectionsがないold batchをresumeする。
- 期待: existing contentを保持し、current snapshotに対するnew ledgerをappendする。一括rewriteやhistory deletionをしない。

### EC-011: Consultation output conflicts internally

- 条件:複数optionsが相互矛盾し、evidenceで選べない。
- 期待: orchestratorは曖昧なrecommendationを採用せずhuman gateへ進む。

### EC-012: Unlimited iteration concern

- 条件: numeric capがないためloopが長期化する。
- 期待: each iterationはfresh evidence、material strategy delta、explicit validationを要求する。新しいbounded strategyがない時点でsemantic stopする。回数によるpass/stopは導入しない。

## 11. 非機能・品質要求

### 11.1 Auditability

- each branch-mutating repair iterationはhead SHA、strategy、consultation、disposition、commit、re-observationへtraceできる。
- no-action / follow-up / human-gateにもrationaleを要求する。
- observed resultはreport/batch ledgerへ記録し、planを実績台帳にしない。

### 11.2 Compatibility

- existing CLI/API/front matter/filename contractを変更しない。
- historical batchesは読めなくならない。
- old batch resumeはappend-onlyに近い非破壊更新を行う。
- no bulk migration。

### 11.3 Security / Privacy

- verbatim model conversation record、secret、token、authentication material、asymmetric signing material、personal data、host-local absolute pathをconsultation artifactまたはbatchへ保存しない。
- consultation inputは必要最小限にsanitizedする。
- unsafe sanitizationはhuman gate。

### 11.4 Reliability

- consultation unavailable / stale / deniedをpass扱いしない。
- mirror driftをtargeted tests / parity inspectionで検出する。
- generated template contentのpositive markerとforbidden old markerの両方を検査する。

### 11.5 Maintainability

- workflow authorityはskillに置く。
- templatesはevidence slotsを持つが、独立したpolicy authorityにはしない。
- count-based wordingを別surfaceに残さない。
- runtime parser/schemaを追加しない。

### 11.6 Performance / External I/O

- このIssueはruntime performance contractを変更しない。
- automated network callを追加しない。
- actual consultation execution cost/latencyはhost workflow concernであり、このIssueではimplementationしない。

## 12. 制約

### CON-001: Evidence-only authority

ChatGPT outputと本packはevidence-only。canonical reflectionにはmain orchestratorの明示EAL dispositionが必要。

### CON-002: No authorized-profile claim

`strict` はcandidate recommendation。`.assurance.json`、classification、authorized profileを変更または決定しない。

### CON-003: Provider source first

shipped assetのauthorityは`src/spec_dock/assets/**`。dogfooding copiesはgenerated/verification surface。

### CON-004: Observation boundary unchanged

`github-pr-observation`はcollection-onlyであり、consultation/disposition/continuation judgmentを持たない。

### CON-005: GitHub mutation boundary unchanged

merge、auto-merge、branch deletion、review reply/resolve/dismiss、issue close/finishを追加しない。

### CON-006: Consultation is mandatory for blocking branch mutation

blocking repair delegationにはfresh consultation evidenceが必要。failure/unavailable/denied/unsafe/staleはhuman gate。

### CON-007: No numeric stop authority

iteration countはtelemetryのみ。numeric thresholdをstop/continue/approvalへ使用しない。

### CON-008: Semantic termination required

同一strategy反復、新strategy不在、insufficient evidence、scope expansion、hard stopはhuman gate。cap削除をblind retryへ変えない。

### CON-009: Runtime / schema no-change

CLI、runtime、JSON schema、database、network adapterを変更しない。

### CON-010: P2/P3 policy unchanged

P2/P3だけを理由に追加branch mutationしない。

### CON-011: Safe output

verbatim model conversation record、secret、authentication material、asymmetric signing material、absolute host path、nested archive、binary、executable、symlinkをauthoring packへ含めない。

### CON-012: Freshness binding

consultationとcontinuation decisionはcurrent head、observation boundary、blocking set、family grouping、strategy contextにboundする。

## 13. 依存関係

### 13.1 前提

| 種別 | 対象 | 必要理由 | 状態 |
|---|---|---|---|
| Parent Epic | `epic-00158` | skill/evidence/provider authority boundary | mainで確認済み |
| Historical Issue | `iss-00178` | triage batch / root family / merge-prepared baseline | mainで確認済み |
| Current skill | `github-pr-merge-preparer` | fixed-limit baseline | mainで確認済み |
| PR #311 | ChatGPT-first planning/evidence boundary | consultation authority constraint | merged into main |
| Local prompt pack | source manifest and clarification artifact list | local candidate intent | body未検証 |
| Issue #313 | title / existence | task identity | open |

### 13.2 Follow-up candidates

| ID | 内容 | 条件 | Blocking |
|---|---|---|---|
| FU-001 | consultation runtime/adapter automation | host-manual consultationでは不足すると判断された場合 | no; separate Issue |
| FU-002 | machine validation of batch schema | Markdown driftが継続する場合 | no |
| FU-003 | cross-skill evidence-gated retry ADR |複数skillsへ同じpolicyを展開する場合 | no |
| FU-004 | observation schema extension |collection evidenceだけではfreshness binding不能な場合 | design-dependent |

### 13.3 Blockers

Issue境界判断を止めるblockerはない。ただしlocal integration decision前には次が必要である。

- local artifact bodyのinspection。
- explicit EAL disposition。
- local source hash / branch state verification。
- actual assurance/profile workflow。
- fresh requirement/design/plan reviews。

## 14. Grade 判定材料

### 14.1 推奨 grade

- [ ] lite
- [ ] standard
- [x] strict（候補推奨）
- [ ] critical
- [ ] 未判断

### 14.2 理由

- agent workflow policyを変更する。
- shipped skill、agent prompt、3 templates、generated output contractに影響する。
- provider/mirror compatibilityを検証する必要がある。
- failure/recovery、authority、security sanitation、human gateを明示する必要がある。
- rollbackは容易でmigrationなしのためcriticalまでは不要。

### 14.3 Risk facts（候補。assurance decisionではない）

| Risk fact | Candidate value | 理由 |
|---|---|---|
| `docs_only_change` | false | skill/templates/testsを変更する |
| `runtime_behavior_change` | false | CLI/runtime codeは非対象 |
| `public_contract_change` | true | shipped agent workflow/template contractを変更する |
| `migration_or_persistence_change` | false | historical batch bulk migrationなし |
| `rollback_difficulty_high` | false | provider prose/template revert + updateで戻せる |
| `security_or_privacy_sensitive` | false, guarded | secrets送信禁止を明示するがauthentication material handling自体は変更しない |
| `agent_workflow_policy_change` | true | continuation/human-gate contractを変更する |

### 14.4 Critical escalation triggers

- GitHub state mutationを追加する。
- secret / authentication material / private dataを自動収集・送信する。
- destructive migrationを追加する。
- human confirmationなしにhigh-risk strategyを自動実行する。
- rollback不能なpersistent stateを導入する。

## 15. Designへの引き渡し

Designは最低限、次を固定する。

1. count-based policyからsemantic continuation gateへのcontract delta。
2. integrated batch、material change、strategy delta、consultation evidence、orchestrator dispositionの語彙。
3. consultation input sanitization、freshness binding、output retention。
4. recurrence classificationとcontinuation decision table。
5. hard stop preservation。
6. skill / prompt / 3 templatesのresponsibility split。
7. provider-first / mirror update / compatibility strategy。
8. no runtime/schema/GitHub mutation boundary。
9. test implicationsとforbidden-old-marker checks。
10. legacy batch resume、failure/recovery、rollback。

## 16. Candidate assumptions and adoption gate

### ASSUMP-001

Mandatory consultationの範囲を「branch mutationを要する全blocking repair batchのworker delegation前」とした。local `interview-mandatory-chatgpt-consultation-scope` bodyがより狭い/広い場合は、この要件をstaleとして修正する。

### ASSUMP-002

Material change後はconsultation refreshを要求する。単一consultationを無期限再利用しない。

### ASSUMP-003

Raw model conversation recordはこのpackにもbatchにも含めない。保存するのはsanitized summary / provenance / dispositionのみ。

### Adoption gate

- [ ] local artifact bodiesを確認した。
- [ ] EAL candidateごとに明示 dispositionを付けた。
- [ ] assumptionsがadopted synthesisと一致する。
- [ ] canonical requirementへmain orchestratorが反映した。
- [ ] fresh spec reviewを通した。
- [ ] assurance/profile workflowを別途完了した。

未チェックのため、この文書はunreviewed candidateのままである。
