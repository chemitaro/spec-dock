---
種別: research
ID: "20260723t084457z-research-issue-planning-workflow-gap-analysis"
タイトル: "iss-00334 現行Issue Planning Workflowの課題・再利用境界調査"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-23"
親: ["iss-00334", "epic-00331", "init-00322"]
scope: "issue"
scope_id: "iss-00334"
authority: "source-grounded-evidence"
canonical_status: "non-authoritative"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_commit: "347c2f79086730ccd7af99ba836d0c1b758f4a95"
derived_from:
  - "AGENTS.md"
  - "iss-00334 requirement.md / design.md / plan.md / report.md"
  - "epic-00331 requirement.md / design.md / plan.md / report.md"
  - "init-00322 requirement.md / design.md / plan.md / accepted ADR 02, 03, 08, 20, 21, 22"
  - "current issue-planning skill, authoring-pack runtime, workflow readiness implementation, tests"
reflected_to: []
---

# 20260723t084457z-research-issue-planning-workflow-gap-analysis

## 位置づけ

- このArtifactは、`iss-00334 Implement ChatGPT Issue Planning Workflow`の具体化に先立ち、現行repositoryで観測できる事実と、親Initiative／Epicで承認済みのvNext契約との差分を整理するsource-grounded researchである。
- 本文は事実、推論、未検証事項、課題、再利用境界、Issue-localな設計への含意を分離する。
- 本文はcanonical `requirement.md`、`design.md`、`plan.md`、accepted ADRを上書きしない。正本候補へ採用する場合は、後続のCandidate authoringとfresh Reviewを経る。
- raw conversation、private reasoning、credential、host-local pathは保存しない。

## 調査目的

1. 現行Issue Planning／authoring-packの責務とvNext target architectureの差分を特定する。
2. 既存機能を無視して新規システムを作らず、再利用可能な決定的primitiveを抽出する。
3. E1-I1で追加・変更するもの、E1-I3まで残すもの、親Epic／Initiativeへrouteするものを分類する。
4. `archive-candidate`と`git-bound`の両経路について、Human Gate、parity、publication、readinessの未実装境界を特定する。
5. Requirement／Design／Plan／Acceptance Criteria／test obligationへ反映すべき課題を整理する。

## source binding

| 項目 | 観測値 |
|---|---|
| repository | `chemitaro/spec-dock` |
| branch | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| exact source commit | `347c2f79086730ccd7af99ba836d0c1b758f4a95` |
| GitHub Issue | `#334 Implement ChatGPT Issue Planning Workflow` |
| target Issue | `iss-00334` |
| parent Epic | `epic-00331 ChatGPT Planning and Advisory Review` |
| parent Initiative | `init-00322 GPT 56 ChatGPT First Intelligence Architecture` |

- branch refとexact source commitは同一であることを確認した。
- `iss-00334`の`requirement.md`、`design.md`、`plan.md`は未具体化scaffold／placeholderを含むため、確定済みIssue仕様として採用しない。

## sources／調査方法

### 正本・決定資料

- repository `AGENTS.md`
- `iss-00334`の`.meta.json`、`requirement.md`、`design.md`、`plan.md`、`report.md`、`artifacts/rules.md`
- `epic-00331`の`requirement.md`、`design.md`、`plan.md`、`report.md`
- `20260720t143411z-adr-issue-planning-walking-skeleton-before-generalization.md`
- `init-00322`のRequirement／Design／Plan／Report
- accepted ADR:
  - Integrated Planning Bundle and plan SSOT
  - Thin `spec-dock-chatgpt` and exact GitHub binding
  - Minimal Persistent State and Workbench boundary
  - Universal Planning Candidate with dual Review transports and dual Revision lanes
  - Scope-specific Planning Adoption Gate
  - Content-addressed Candidate identity and Placeholder Oracle

### 現行実装・テスト

- provider／dogfood `spec-dock-issue-planning` Skill
- provider／dogfood `spec-dock-chatgpt-authoring` Skill
- authoring-pack prepare／invoke／review／stage／candidate validation
- `spec_dock_runtime.application.authoring_pack`
- `spec_dock_runtime.domain.authoring_pack`
- Git fetch policy、source manifest、preflight receipt writer
- workflow readiness／report evidence gate
- CLI runtime、unit、manual、fixture tests

### 分析方法

- Actor／authority／side effect ownershipを比較した。
- Planning正常経路とnegative fixtureを現在の実装へ照合した。
- ChatGPT-facing処理とrepository mutation処理を分離した。
- 再利用可能なprimitiveと、旧semantic workflowに固有のsurfaceを区別した。
- provider authority、installed projection、dogfood projectionの更新面を確認した。

## facts／観測できた事実

### F-001 現行Issue Planningはevidence adoption＋Codex rewrite方式

現行`spec-dock-issue-planning` Skillは、`spec-dock-chatgpt-authoring`へPlanning evidence生成を委譲し、ChatGPT outputをevidenceとして確認した後、Codexがcanonical `requirement.md`、`design.md`、`plan.md`へ採用・再記述する。

これはvNextで採用済みの「ChatGPTが完全Bundleを生成し、Mainは意味内容を再構成せず配置する」契約と一致しない。

### F-002 現行Skillはmanual fallbackを公式経路として保持する

現行Skillはhard／unrecoverable failure時の`spec-dock-issue-planning-manual`を保持する。vNext Initiativeは、旧manual Planning Skillと共有authoring Skillをretireし、Planning Skillが`spec-dock-chatgpt`を直接利用する方針である。

### F-003 既存authoring-packには強い決定的primitiveがある

既存実装とtestsには次が存在する。

- Git fetch／local HEAD／remote HEAD同期preflight
- typed failure classificationとbounded retry
- source manifest／SHA-256／stale検出
- backend commandのdirect argv実行
- attachment存在・通常ファイル検査
- secret-like path／host path／diagnostic redaction
- ZIP path traversal、absolute path、backslash ambiguity、symlink、special file拒否
- duplicate、case-fold、Unicode normalization collision拒否
- nested archive、encrypted entry、executable、binary、non-UTF-8拒否
- file count、size、compression ratio、CRC検査
- safe extraction
- content digest binding
- atomic publicationとnon-owned target保護
- provider／dogfood parity tests

これらはvNext実装で再利用すべきである。

### F-004 現行authoring-packのauthorityはevidence-only

既存prepare／review／stage／approval validationは、`authority=evidence_only`、`canonical_written=false`、`execution_ready=false`等を明示し、ChatGPT outputがcanonical authorityやreadinessを自己主張しないようにしている。

この安全境界は維持すべきだが、vNextのpositive adoption chainは別途追加する必要がある。

### F-005 現行readinessはassurance＋report evidenceから導出される

現在のworkflow stateは永続的な`execution-ready` flagではなく、Requirement／Design／Planのreadiness、`.assurance.json`、`report.md`のEvidence Adoption Ledger、Spec Authoring Gate、Reviewer Gate等から`ready | blocked`を都度導出する。

vNextのpositive gateで必要な次のEvidenceは、現行readinessモデルへ直接表現されていない。

- exact Candidate／reviewed HEAD identity
- fresh Planning Review identity
- Human Issue Plan Adoption and Implementation-Start Authorization
- candidate-to-canonical／reviewed-content parity
- Planning publication local／remote identity

### F-006 親EpicはE1-I1をvertical walking skeletonとして固定する

E1-I1はCLI skeleton、Git binding、Oracle adapter、Prompt、Candidate package、Review、Human Gate、placement、parity、tests、docs、projectionを分割せず、一つのActor Journeyとして完成させる。

先行foundation-only Issueを作らない。共通化はE1-I2という第二のconsumerが現れた時点で抽出する。

### F-007 Review transportは二系統で確定済み

- `archive-candidate`: pre-canonical semantic iterationの既定。exact logical filename、internal identity、source HEAD、external ZIP SHAへbindする。
- `git-bound`: actual repository path、CI、GitHub inline review等がmaterialに必要な場合の正式fallback。exact reviewed HEADとexact target pathsへbindする。

両mode間のsilent fallbackは禁止される。

### F-008 Revision laneは二系統で確定済み

- Semantic Revision: ChatGPTが完全な新Candidateを生成する。
- Mechanical Revision: path／field／old-new literal／meaning invariant／diff budgetを事前に閉じられる場合だけMain／scriptが実行できる。

どちらでもCandidate bytes変更はnew identityとfresh Reviewを必要とする。

### F-009 Human GateはReview PASSと別authorityである

Issue Scopeは、Review PASS後にexact reviewed identityへbindしたHuman Issue Plan Adoption and Implementation-Start Authorizationを必要とする。

Review PASSだけ、Human Gateだけ、parityだけでは`execution-ready`へ進めない。

### F-010 Parent EpicはPA-NF-01〜PA-NF-10をlocal normative contractとして要求する

10件を個別fixtureとして実装し、E1-I1 producer acceptanceは10／10 PASS、violations 0を必要とする。中央参照やgenericな`negative fixtures`表現だけでは不適合である。

## issue analysis／見つかった主要課題

### P-001 Authoring authority chainがvNextと不一致

現行は次の経路である。

```text
ChatGPT evidence
→ Codex claim adoption / rewrite
→ report evidence gate
→ local spec reviewer
→ legacy readiness
```

目標は次である。

```text
ChatGPT complete Candidate
→ exact-identity fresh Planning Review
→ exact-identity Human authorization
→ deterministic adoption / parity
→ validation
→ Planning publication
→ derived execution-ready
```

主課題は単なるCLI追加ではなく、authority chainの置換である。

### P-002 ChatGPT transportとrepository mutationの境界が未実装

`spec-dock-chatgpt`はthin Oracle adapterであるべきだが、現行public surfaceはCore `authoring` command群と共有Skillに分散している。

必要な境界:

- `spec-dock-chatgpt`: target／Git binding、Prompt、Oracle、result retrieval
- Core Runtime: ZIP検査、approval evidence検証、canonical adoption、parity、validation、publication verification
- Skill: mode／lane／Human Gate／semantic判断
- Main: repository mutation、commit／push

### P-003 Prompt本文の保守性とidentityが不足

現行prompt生成にはscript内の文字列、prompt pack、docsが混在する。vNextではoperation固有Markdownとprovider-managedなclosed fragment setへ分離し、resource hashとrendered Prompt hashを追跡する必要がある。

公開custom template overrideやraw prompt overrideはformal Workflowの安全契約を弱めるため禁止する。

### P-004 Issue Planning Candidateの完全なdomain contractが不足

既存candidate validationは主にInitiative→Epic、Epic→Issue decomposition candidateを扱う。Issue自身の完全三文書をformal Review／Human Gate／adoptionへ渡すCandidate contractが不足する。

必要な最小package:

```text
requirement.md
design.md
plan.md
SOURCE-BASELINE.json
MANIFEST.json
CHECKSUMS.sha256
```

### P-005 Human authorizationの一次Evidenceとclosed renderが不足

現行approval validationにはHuman evidence検査のprimitiveがあるが、Issue Plan adoptionとimplementation-start authorizationをSkill対話からcaptureし、source record SHAとcanonical approval artifactへbindするvNext contractがない。

### P-006 Candidate-to-canonical／git-bound parityがreadinessへ接続されていない

必要な検査:

- archive: Candidate三文書とcanonical三文書のbyte／closed render parity
- git-bound: reviewed HEADのexact target blobsとpublication HEADの同target blobsの一致
- Candidate-external変更のclosed allowlist
- source drift／wrong identity／semantic mutation rejection

### P-007 Planning publicationのremote identityがreadinessへ接続されていない

必要な成功条件:

- dedicated Planning commit
- named Issue branchへのpush
- local publication commit == remote branch HEAD
- canonical bytes == commit tree bytes
- git-boundではpublication commitのparent == reviewed HEAD
- exact target blobsがreviewed HEADから不変

### P-008 現行readinessとvNext readinessが異なる

現行`workflow status`はreport evidenceとassuranceを中心にreadinessを導出する。E1-I1ではvNext Planning Adoption readiness verifierが必要である。

ただし、E1-I3まで旧surfaceを破壊的に削除しないため、E1-I1では新Skillが新verifierを利用し、legacy guidanceは互換面として残すのが妥当である。

### P-009 Legacy surfaceの削除時期を誤るとwalking skeletonが壊れる

E1-I1でreplacement capabilityを提供し、E1-I2で第二consumerを実証した後、E1-I3がplanning-specific legacy surfaceをretireする。E1-I1で旧Skill／commands／docsを一括削除してはならない。

### P-010 Test architectureがpositive pathだけでは不十分

必要なtest層:

- unit: Prompt resources、identity、safe ZIP、approval、parity、publication verifier
- CLI: `planning create/revise`, `review planning`, adoption／readiness operations
- projection: provider／installed／dogfood parity
- negative: PA-NF-01〜PA-NF-10個別fixture
- integration: fake backend／Oracle session／Git remote
- real-use: eligible real Issueで一方のmodeをend-to-end dogfood

## reuse／change／defer matrix

| Surface | Disposition | 理由 |
|---|---|---|
| Git sync preflight | reuse／adapt | exact branch／HEAD bindingの基盤 |
| Git fetch failure policy | reuse | typed bounded retryとredactionが既にある |
| source manifest／hash | reuse／extend | Candidate source bindingへ転用可能 |
| backend direct argv | reuse／adapt | Oracle thin adapterの安全境界 |
| ZIP central directory safety | reuse／harden | Candidate ZIPのformal identityへ必要 |
| safe extraction | reuse／harden | adoption前の必須検査 |
| atomic publication pattern | reuse | approval artifact／adoption file publicationへ適用 |
| current `spec-dock-chatgpt-authoring` Skill | keep until E1-I3 | E1-I1でreplacementを追加し、E1-I3が削除 |
| manual Planning Skills | keep until E1-I3 | official routeからは使わず、cutoverで削除 |
| old `authoring` commands | compatibility only | vNext official command hierarchyにはしない |
| Evidence Adoption Ledger authoring | do not reuse semantically | complete Bundle＋Human Gateへ置換 |
| local planning reviewer | keep until E1-I3 | fresh ChatGPT Planning Reviewへ置換後に削除 |
| `report.md` as readiness store | do not extend | vNext authorityを複製しない |
| new semantic state DB | prohibited | Initiative ADR 08と矛盾 |
| Portfolio materialization | E1-I2 | E1-I1のScope外 |
| Targeted Review／legacy removal | E1-I3 | E1-I1のScope外 |
| Issue execution／PR delivery | Epic 2／3 | E1-I1のScope外 |

## inference／sourceから導いた設計方針

### I-001 `spec-dock-chatgpt`はChatGPT-facing operationsに限定する

- `planning create`
- `planning revise`
- `review planning`

canonical mutation、commit、push、readiness mutationは持たせない。

### I-002 Promptはclosed manifest＋Markdown fragmentsで合成する

- operation resource
- ordered shared fragments
- required input keys
- output contract kind

だけをmachine-readable manifestに置く。汎用template language、recursive include、operator resource overrideは導入しない。

### I-003 Issue Candidateは単一rootの最小packageとする

formal Candidateにraw transcript、Oracle log、`report.md`、`.meta.json`、`.assurance.json`を含めない。

### I-004 Review resultはstructured JSON＋Human-readable Markdownとする

Runtimeはidentityとschema shapeのみ検証し、findingの意味判断はMain／Skillに残す。

### I-005 Human approvalはWorkbench source JSON＋canonical Markdown evidenceに分ける

- source JSONをSHA-256でbind
- canonical artifactはclosed render
- raw会話全文は保存しない

### I-006 vNext readinessは永続flagではなくderived verifierとする

Candidate／Review／Human Gate／parity／validation／publication Evidenceを入力として、`ready | blocked | stale | insufficient-evidence`を返す。

### I-007 E1-I1はadditive migrationとする

replacementを先に提供し、planning-specific legacy removalはE1-I3へ委譲する。

## unverified／実装時に確認すべき事実

- `spec-dock-chatgpt` executableをpackageへ登録する正確なentrypoint
- Prompt resourceのpackage-data設定とfresh install path
- Core Runtime command名とparser配置
- Issue Candidate／approval／readiness domain objectの既存homeとの適合
- fake bare remoteを用いたpublication verification test harnessの再利用可否
- existing artifact filename parserへ新approval evidence typeを追加する必要性
- exact validation command setとvNext readiness verifierの接続点
- E1-I1で残すcompatibility wrapperの最小inventory
- dogfood実行時点のeligible open Issue一覧

これらはrepository調査・実装設計で解決し、operator value judgmentが不要な限りHumanへ質問しない。

## question candidates／Human decision routing

### 現時点で追加のHuman判断が不要な事項

- Skill／CLI責務
- phase-separated operations
- dual Review transports
- dual Revision lanes
- Human authorizationの対話入口
- Planning publication
- Prompt closed fragment composition
- dogfood targetをJIT選定する方針

### 後で必須となるHuman Gate

1. feature-complete後のexact dogfood Issue選定
2. dogfood Issueのexact reviewed identityへのPlan adoption／implementation-start authorization
3. clarification完了後のCandidate ZIP生成許可

### 条件付きHuman Gate

- shell exception
- byte-exact rollback不能
- parent materializationが必要なSeed
- E1-I1外のlegacy removal
- parent contract変更

## implications／Requirement・Design・Planへの含意

### Requirement

- official Skillとfirst-class deterministic CLI
- complete Issue Planning Bundle
- archive／git-bound positive gate
- Human authorization Evidence
- Planning publication
- derived readiness
- PA-NF-01〜PA-NF-10
- mandatory four non-goals
- sensitive-data exclusion／direct argv
- provider／installed／dogfood parity

### Design

- Skill／ChatGPT CLI／Core Runtime／Oracle／Main／Human責務分離
- Prompt resource architecture
- Candidate／Review／approval／publication identity model
- archive adoption transaction
- git-bound reviewed／publication HEAD model
- readiness verifier
- failure／retry／rollback matrix
- additive migration boundary

### Plan

- vertical walking skeleton順序
- TDD test matrix
- Prompt resource／CLI／Candidate／Review／Human Gate／adoption／publication／readinessの実装tranche
- provider→fresh install→update→dogfood verification
- PA-NF-01〜PA-NF-10
- eligible real Issue dogfood JIT selection
- one branch／one Delivery PR／Human merge

## リスク

- 旧authoring primitiveを捨てて重複実装を作る
- `spec-dock-chatgpt`へsemantic判断やGit mutationが漏れる
- Prompt fragmentを細分化しすぎて最終Promptが読めなくなる
- Review PASSとHuman authorizationを同一authorityとして扱う
- approval artifact追加によりreviewed contentが変化する
- Candidate外diff allowlistが広すぎてsemantic mutationを許す
- legacy readinessとvNext readinessが混在して誤ったstartを許す
- E1-I1でlegacy surfaceを早期削除し、E1-I2／I3を壊す
- dogfood用に新Issueを作りMinimum Sufficient Decompositionを破る

## 反映先候補

- `iss-00334/requirement.md`
- `iss-00334/design.md`
- `iss-00334/plan.md`
- Issue-local supporting artifacts
- provider／installed／dogfood Skill、CLI、Prompt resource、Runtime、docs、tests

## 参考

- `chemitaro/spec-dock@347c2f79086730ccd7af99ba836d0c1b758f4a95`
- `epic-00331` Requirement／Design／Plan
- `init-00322` Requirement／Design／Plan
- accepted ADR 02, 03, 08, 20, 21, 22
- current provider／dogfood Issue Planning Skill
- current authoring-pack application／domain／infra／presentation
- workflow readiness／report evidence implementation
- authoring-pack unit／CLI／manual tests
