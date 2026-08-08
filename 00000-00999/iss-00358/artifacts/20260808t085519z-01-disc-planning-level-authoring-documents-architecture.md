---
種別: disc
ID: "20260808t085519z-01-disc"
タイトル: "Planning Level Authoring Documents Architecture Proposal"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-08-08"
親: ["iss-00358"]
関連:
  - "iss-00357"
  - "20260808t083300z-interview"
  - "20260808t085519z-interview"
authority: "proposed"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT proposal session: required-repository-connector-context-repository-58"
reflected_to: []
---

# 20260808t085519z-01-disc Planning Level Authoring Documents Architecture Proposal

## 位置づけ

- Product Ownerの回答「RuntimeのProfile / Assurance / routingは完全撤去するが、Issueのlevelに応じたPlan完成基準は複数のAuthoring documentとして残したい」を、実装可能なAuthoring Kit構造へ整理する提案Evidenceである。
- 同じ元ChatGPTスレッドの`Pro`へbest practiceを依頼し、その回答をローカルのIssue 357 / 358調査と照合してsynthesisした。
- Oracle実行記録は`target=Pro`、内部requested keyは`gpt-5.5-pro`、resolved labelは取得不能、model verificationは`no`だった。したがって、厳密に「ChatGPT 5.6 Proである」とは証明せず、同じスレッドのChatGPT Proによる提案として扱う。
- Canonical Requirement / Design / Planは未変更であり、Epic Requirement Reviewの`fail`も未解決である。

## 対象論点

- RuntimeへWorkflow stateを戻さず、`light` / `standard` / `strict` / `critical`ごとのPlan作成基準を提供する方法。
- Canonical `plan.md`の数、Guideのファイル構成、level選択の記録方法、Issue 357〜360の所有境界。

## derived question sheets / research

- `20260808t083300z-interview`:
  - Runtime上のProfile / Assurance / `draft-*` routingは完全撤去する。
  - Plan guidanceはlevel別文書を検討する、というユーザー回答を記録した。
- `20260808t082616z-research`（Issue 358）:
  - Template / Guide / Artifact semanticsとRuntimeとの結合を調査した。
- Issue 357の同時刻Research:
  - RuntimeがPlanning policyを解釈しない境界、Historical read compatibilityを調査した。

## synthesis

### 合意済み

- `.assurance.json`、`authorized_profile`、Issue Grade、profile classification、`draft-design` / `draft-plan` routingは新規Surfaceから完全に外す。
- 新しいcommand、metadata field、hidden authority、gate、state machineは作らない。
- Existing node-local dataとHistorical Artifactは自動削除・書換えしない。
- level別の違いは「作業完了時のあるべき状態、Planning depth、検証義務」を示すAuthoring documentとして残す。

### 未合意

- 共通Base Guide + level別Completion Guide方式を正式採用するか。
- Canonical `plan.md`を一つに保つか、level別Plan fileを生成するか。

## 選択肢 / tradeoff

| 選択肢 | 構成 | 長所 | 問題 | 評価 |
|---|---|---|---|---|
| A. 別Plan Template / 別Plan file | `plan-light.md`等を生成 | level固有の形を直接提示できる | routing、正本選択、共通部重複、level変更時の再生成が必要 | 非推奨 |
| B. 単一巨大Guide | 一つのGuideに4 levelを全掲載 | ファイル数が少ない | 毎回全levelを読み、規則混在・肥大化・編集競合が起きる | 非推奨 |
| C. 共通Base + level別Completion Guide | 一つのCanonical `plan.md`、共通Guide、4つのlevel文書 | Runtime不要、正本一つ、progressive disclosure、共通部を一箇所化 | Linkと差分文書の整合テストが必要 | 推奨 |

## 推奨アーキテクチャ

```text
各Issue
└── plan.md                         # Canonical planは常に一つ
      ├── docs/authoring/plan.md    # 全level共通の書き方
      └── issue-plan-levels/<selected>.md
            ├── light.md
            ├── standard.md
            ├── strict.md
            └── critical.md
```

- `plan.md`のPathをlevelで変えない。
- `new issue`は常に一種類の`templates/issue/plan.md`からScaffoldする。
- level変更は通常のMarkdown編集とGit diffで表現し、Runtime stateを作らない。
- 「Profile」は旧Runtime契約と混同するため、新概念は`Planning Level`、文書は`Completion Guide`と呼ぶ。
- Legacy tokenの`lite`をaliasとしてRuntimeへ残さず、新文書では`light`を使う。

## 推奨File Tree

### Provider source

```text
src/spec_dock/assets/spec_dock/
├── templates/issue/plan.md
└── docs/authoring/
    ├── plan.md
    └── issue-plan-levels/
        ├── light.md
        ├── standard.md
        ├── strict.md
        └── critical.md
```

### Dogfood projection

```text
spec-dock/
├── templates/issue/plan.md
└── docs/authoring/
    ├── plan.md
    └── issue-plan-levels/
        ├── light.md
        ├── standard.md
        ├── strict.md
        └── critical.md
```

- Current distributionから`templates/issue-profiles/`と`draft-*` routingを除く。
- Existing consumer内の`.assurance.json`、既存`design.md` / `plan.md`、Historical `draft-*` Artifactは保持する。

## Canonical `plan.md`への明示方法

```markdown
## Planning Level

- 選択Level: standard
- 選択理由: 通常のRuntime変更で、破壊的MigrationやSecurity影響がないため
- 参照Guide: spec-dock/docs/authoring/issue-plan-levels/standard.md
- 引き上げ要因の確認:
  - public contract: なし
  - migration / persistence: なし
  - security / privacy: なし
  - high rollback difficulty: なし
- 再評価条件: 永続化形式または公開CLI変更が必要になった場合はstrictを再検討する
```

- このSectionは通常のMarkdown本文である。
- Runtimeはparse / validate / persist / route / enforceしない。
- `.meta.json`へ複製しない。
- dependency readiness、`issue start` / `finish`、reviewer gateへ利用しない。
- ユーザーが明示したlevelをAgentが黙って下げない。引き下げ提案は、Scope縮小とRisk消失の根拠を`plan.md`へ残す。
- 未指定時のAuthoring上の推奨defaultは`standard`とするが、Runtime defaultにはしない。

## Planning Level別の完成基準

| Level | 作業完了時のあるべき状態 | 必須Planning depth | 検証義務 | Rollback / Migration | Security / Performance / Operability |
|---|---|---|---|---|---|
| light | 局所的成果が完了し、直接ACを観測でき、追加移行・運用作業が残らない | 目的、Scope、対象、短い順序、直接検証、完了条件 | Targeted testまたは明示的manual check、該当Lint / Typecheck | 容易にGit revert可能。Migrationが必要なら原則上位 | Materialな影響がない根拠。Unknownがあれば不可 |
| standard | 通常のFeature / Bug fixがEnd-to-Endで成立し、Code / Test / Docsが整合 | 実装順序、責務境界、主要Error case、Test seam、依存、Verification | Targeted test、影響範囲Regression、静的検査 | Behavior / Config変更の基本Rollback。Reversible migration手順 | 各観点を検討し、非該当なら短い理由 |
| strict | Public contract、Runtime behavior、Data、Compatibilityを含む変更が安全に移行・復旧可能 | As-Is / To-Be、契約差分、Failure mode、Compatibility、Migration、Rollback、Observability、部分失敗 | 関連Unit / Integration / E2E / Negative、Full regression、Migration / Rollback相当検証 | Rollback、Forward recovery、途中失敗回復を具体化 | Materialな観点へTest / Monitoring obligation |
| critical | 高Blast radius、Security / Privacy、破壊的・不可逆変更で封じ込め・回復・監視まで実証 | Threat / Data classification、Staged rollout、Kill switch、Backup / Restore、Incident response、Capacity、Audit | Security、Load / Capacity、Restore / Recovery、Failure injection、post-deploy確認から該当項目 | 未検証Rollbackを主張しない。不能ならForward recoveryと停止条件 | 認可、Secret、PII、Audit、閾値、Alert、Operator actionを具体化 |

### 全level共通

- levelを上げる目的は文章量を増やすことではない。
- 関係しない項目は短い理由付き`N/A`でよい。
- Evidence本文を複製せず、Test、Command、Artifact、Code pathへLinkする。
- Planning LevelはPriority、Severity、Dependency、Implementation readinessを表さない。
- 変更行数ではなく、失敗影響、回復困難性、契約・Data・Securityへの影響で選ぶ。

## Progressive Disclosure

```text
templates/issue/plan.md
  -> docs/authoring/plan.md
      -> docs/authoring/issue-plan-levels/<selected>.md
          -> 必要なDomain固有資料
```

- Thin TemplateにはPlanning Level、Goal、Scope、Implementation sequence、Verification、Rollback / Migration、Completion criteria、Open questionsだけを置く。
- Base GuideはRequirement / Design / Plan境界、Slice、Verification、level選択・変更、anti-patternを一度だけ説明する。
- Level文書はBase Guideを再掲せず、そのlevel固有の完成基準と義務だけを書く。
- `critical`を読むために`standard`と`strict`を順番に読ませない。各level文書はBaseに対する独立差分とする。
- CLI syntaxは複製せず`--help`へ案内する。

## Issue 357〜360の責務分担

| Issue | 所有 | 所有しない |
|---|---|---|
| 357 | RuntimeからAssurance / classification / routingを除去。単一Templateを読むmechanism、Historical read compatibility | Planning Levelの意味、level文書本文、Skill、Installer prune |
| 358 | 単一`plan.md` Template、共通Plan Guide、4 Level Guide、Docs navigation | Parser / Registry、Runtime routing / metadata、Skill実装、Prune実行 |
| 359 | 2つのSpecDock SkillからAuthoring KitへのPointer、選択level文書の読み方 | level分類・強制、自動Plan生成、level本文複製 |
| 360 | Fresh / update / uninstall inventory、obsolete managed asset prune、provider / dogfood / installed parity | Runtime / Authoring semanticsの再設計 |

## Canonical反映候補

### Requirement候補

- Planning LevelはIssue Planのdocumentation-only概念である。
- 各IssueのCanonical Planは`plan.md`一つだけである。
- Runtimeはlevelを分類・保存・選択・強制しない。
- 新規Issueは単一Templateから生成する。
- levelと理由は`plan.md`本文に明示し、未指定時のAuthoring推奨は`standard`とする。
- Existing Assurance / Profile / Draft Evidenceは自動削除・書換えしない。

### Design候補

- `Planning Level = visible Markdown selection`。
- `Canonical output = exactly one plan.md`。
- `Runtime visibility / machine enforcement = none`。
- `History = Git diff`。
- `Historical compatibility = preserve but do not interpret`。

### Acceptance Criteria候補

- Provider / dogfoodにBase Guideと4 Level Guideが存在する。
- Issue Plan Templateは一つだけで、`plan-light.md`等は存在しない。
- Runtime sourceにlevel選択、parsing、routing、start / finish制御がない。
- `.assurance.json`がなくてもFresh Issueが生成できる。
- Historical dataが存在してもvalidate / active / deps /通常Artifact作成が旧Workflow評価を再開しない。
- Current Template / GuideからAssurance、Grade gate、Reviewer gate、Promotion、EAL必須化、Delegated Authoring、PR readinessを除く。
- Initiative / Epic PlanへIssue Planning Levelを要求しない。

## テスト義務候補

- Provider / dogfood byte parity。
- Base Guideから4 Level GuideへのLink validity。
- Issue Plan Templateが一つだけで、level別Canonical Planがない。
- Runtime内にPlanning Level routingがない。
- `plan.md`のlevel記述を変えても`deps`、`issue start` / `finish`の結果が変わらない。
- Historical `.assurance.json`と`draft-*`を持つconsumer fixtureを破壊しない。
- Updateがobsolete managed profile TemplateだけをPruneし、user-owned文書を削除しない。
- Current navigationから旧Workflow entrypointへ到達しない。

## Pressure Test

- 過度な文書化:
  - 4 levelのChecklistをPlanへ転記せず、選択GuideへのLinkと該当事項だけを書く。
- Level inflation:
  - Defaultは`standard`。高levelはFailure costがMaterialなときだけ選ぶ。
- `light`の乱用:
  - Public contract、Migration、Security、不可逆性、重大Unknownがあれば`light`にしない。
- High levelの儀式化:
  - 無関係なLoad test等を強制せず、非該当理由を短く書く。
- Agentの自己都合によるdownshift:
  - 黙って変更せず、Scope縮小とRisk消失の根拠をGit diffに残す。
- Readinessとの混同:
  - levelはdependency-ready / implementation-ready / review passを表さない。

## ADR triage

- ADR candidateか:
  - yes
- hard to reverse:
  - medium。配布するAuthoring contractとSkill参照Pathになるため、後からの変更は広く波及する。
- surprising without context:
  - yes。旧Runtime Profileを撤去しながら同名に近い4 level文書を残すため、境界説明が必要である。
- real tradeoff:
  - yes。正本一つとprogressive disclosureを優先し、level別Canonical Plan生成を捨てる。
- ADR化判断:
  - Product Ownerが提案を採用した後、Issue Designへの記載で十分か、長期ADRが必要かを判断する。

## 推奨案

- Option C「共通Base Guide + 4つのlevel別Completion Guide」を採用する。
- Canonical `plan.md`は各Issueに一つだけ保つ。
- Runtimeはlevelを一切認識しない。
- 選択level、理由、risk factors、再評価条件は`plan.md`本文とGit履歴に残す。

## 未採用 / deferred

- 未採用:
  - level別Canonical Plan fileとRuntime routing。
  - 単一巨大Guide。
- deferred:
  - 本提案のProduct Owner採否。
  - 採用後のADR要否。
  - Issue 357固有のthin `issue finish` semantics。

## 次アクション

- `20260808t085519z-interview`で推奨アーキテクチャの採否を確認する。
- 採用後、同じChatGPTスレッドへ回答を返し、Issue 358のCanonical authoring briefへ進める。
