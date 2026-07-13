---
種別: 要件定義書（Issue）
ID: "iss-00313"
タイトル: "PR Merge Preparer の修復回数制限を廃止し、証拠駆動の継続判定へ置換する"
関連GitHub: ["#313"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00158", "init-local-00003"]
---

# iss-00313 PR Merge Preparer の修復回数制限を廃止し、証拠駆動の継続判定へ置換する — Issue 要件定義

## 0. 文書の位置づけ

### 0.1 この文書が定義すること

- `github-pr-merge-preparer` の blocking repair continuation に必要な観測可能な workflow outcome。
- 固定 attempt cap と同一 failure-family 再発停止を廃止した後の安全な継続条件。
- integrated PR repair batch と ChatGPT consultation の必須 evidence boundary。
- main orchestrator、ChatGPT、repair worker、`github-pr-observation`、human gate の責務境界。
- provider source、templates、dogfooding mirror、tests の受け入れ条件。
- 互換性、失敗 / 復旧、セキュリティ / プライバシー、スコープ拡大の条件。

### 0.2 この文書が定義しないこと

- ChatGPT API、browser automation、connector、runtime command の実装方法。
- `github-pr-observation` の stdout JSON schema または GitHub API collection logic。
- repair worker が個々の product defect をどう修正するか。
- GitHubレビューへの返信 / 解決 / 却下、マージ、ブランチ削除、Issueのクローズ / 完了。
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
- [ ] セキュリティに関わる実装

## 3. 背景・現状

### 3.1 現行ワークフロー契約

`github-pr-merge-preparer` は、PR作成または発見、latest-head observation、CI / Codex review triage、blocking repair delegation、push確認、re-observation、merge-prepared evidence報告を調整する。merge自体、review reply / thread resolution / dismissal、issue closeは所有しない。

現行の fix-loop policy は概ね次の通りである。

- P0: default 1 autonomous repair attempt。ただし trivial / local の例外あり。
- 同じ失敗ファミリーのP1: デフォルトで2回試行。
- 自律的な修復試行の合計: 1回の呼び出しにつきデフォルトで4回。
- 修復コミット後に同じ `root_cause_family` が再発した場合は停止。
- 権限 / 認証、外部要因 / 不安定性、ベースブランチとの競合、不明な失敗、要件拡大、破壊的変更 / 移行 / シークレット / デプロイへの影響、曖昧なレビュー意図、プラットフォーム上でのみ可能な会話解決等はhuman gate。

repair-batch templateも、同一 family再発とloop-limit到達をStop Conditionsとして持つ。

### 3.2 問題

- 回数はfailureの修復可能性、新しいevidence、strategy qualityを表さない。
- 一回目のfixが不完全だった場合と、root-cause hypothesisが誤っていた場合と、同じ症状の別原因を区別できない。
- 複数blocking findingを個別コメント単位で扱うと、共有root causeとcross-file contractを見落とす。
- capだけを削除するとblind retryやrunaway mutationを許すため、代替のsemantic termination gateが必要になる。
- ChatGPT-first authoring/evidence boundaryがrepositoryに導入された後も、repair loop側にはintegrated consultationとorchestrator dispositionの明示契約がない。

### 3.3 根拠・情報源

#### 親

- `epic-00158/requirement.md`
  - `E-RQ-001`: skillが運用ワークフローの中核を所有する。
  - `E-RQ-005`: ChatGPT / 委譲先の出力はmain orchestratorが採用するまでevidenceである。
  - `E-RQ-007`: provider sourceの権威性 + dogfooding mirrorの検証。
  - `E-AC-004`: missing / stale / failed / unavailable / denied 等はpassではない。
- `epic-00158/design.md`
  - provider source-first、canonical docs main-orchestrator-owned、external/delegated outputは採用前evidence。
- `epic-00158/plan.md`
  - Issueはsmall/reviewable、parent trace、provider/mirror verification、rollback/compatibility/EALを持つ。

#### 現行の実装契約

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md`

#### 過去の設計根拠

- `iss-00178 Review Feedback Triage`
  - バッチ一覧、修復単位、review-clean / merge-preparedの分離、観測の収集専用境界。
  - 当時はrepeated failure classをhuman gateにするfix-loop limitsを採用した。

#### プロンプトパックのローカルコンテキスト

- `research-pr-merge-preparer-repair-limit-clarification-baseline`
- `interview-same-family-repair-recurrence-continuation-policy`
- `user-proposal-chatgpt-assisted-integrated-pr-repair-batch`
- `research-chatgpt-consultation-integrated-pr-repair-workflow`
- `interview-mandatory-chatgpt-consultation-scope`
- `chatgpt-raw-integrated-pr-repair-workflow-consultation`
- `disc-adopted-integrated-pr-repair-workflow-synthesis`

これらのbodyはローカルで確認済みであり、採用済みインタビュー回答と統合分析を本要件へ反映した。

## 4. 親スコープと継承条件

### 4.1 親イニシアチブ

- ID: `init-local-00003`
- 継承制約:
  - architecture maintenance / hardeningの範囲に閉じる。
  - provider sourceとconsumer/dogfooding projectionを混同しない。
  - user-authored / canonical artifactsを破壊しない。

### 4.2 親エピック

- ID: `epic-00158`
- 関連する要件ID:
  - `E-RQ-001`, `E-RQ-002`, `E-RQ-005`, `E-RQ-007`
- 関連する受け入れ条件ID:
  - `E-AC-001`, `E-AC-004`, `E-AC-005`, `E-AC-006`, `E-AC-007`
- 継承する契約:
  - skillは最初に読むべきワークフローの権威である。
  - docs / templatesはskill authorityを補助し、templatesはauthorityを所有しない。
  - ChatGPT outputはevidence-only。
  - main orchestratorが採否とcanonical reflectionを所有する。
  - provider sourceを先に変更し、mirrorをvalidate / sync / targeted inspectionする。

### 4.3 このIssueで再定義しないもの

- `github-pr-observation` の収集専用という責務。
- stdout JSONの権威ある観測evidenceとしての意味論。
- P0/P1はブロッキング、P2/P3は非ブロッキングという重大度契約。
- P2/P3だけを理由にブランチを変更しない方針。
- merge-preparedとreview-cleanの区別。
- 人間のみが行うGitHub上の会話解決 / マージ操作。
- SpecDockのcanonical authoring / assurance / reviewerワークフロー。

## 5. アクター、トリガー、代表シナリオ

### 5.1 アクター

| アクター | 責務 | このIssueとの関係 |
|---|---|---|
| メインオーケストレーター | 証拠の新鮮さ、トリアージ、相談結果の処理、継続または人間ゲートの判断 | ワークフローの最終判断を所有する |
| `github-pr-merge-preparer` | pull requestの引き渡しループにおける運用上の中核 | 主たる変更対象の契約 |
| `github-pr-observation` | 最新headのCI・レビュー証拠の収集 | 変更されない上流の証拠生成元 |
| ChatGPT | 統合バッチに対する選択肢、リスク、戦略案を生成する | 証拠だけを提供する相談役 |
| 修復ワーカー | 承認済みのスコープと戦略に従い、範囲を限定した実装を行う | 判断後にだけ委任される |
| 人間 | 曖昧、高リスク、未対応の事例とマージを判断する | 強制ゲートの所有者 |
| 保守担当者またはレビュー担当者 | スキル、テンプレート、テストの契約を検証する | 後続レビューの所有者 |

### 5.2 トリガー

- latest-head observationにP0/P1、required check failure、merge blocker、またはbranch mutationを要するblocking familyが存在する。
- repair後のre-observationでblocking familyが残存・再発・新規発生する。
- existing repair batchをresumeし、current head / evidence / strategy freshnessを再評価する。

### 5.3 シナリオ SC-001: 初回blocking batch

- 前提:
  - latest-head observationが複数のP0/P1またはrequired check failuresを返す。
- 操作:
  - merge preparerがrepair delegationを検討する。
- 結果:
  - current observationの全blocking itemsをintegrated batchにinventoryする。
  - root-cause family、coupling、allowed scope、testsを分析する。
  - sanitized batch evidenceでChatGPT consultationを実施する。
  - orchestratorがrecommendationsをdispositionし、使用するstrategyだけをworker handoffへ変換する。

### 5.4 シナリオ SC-002: 同一familyが再発

- 前提:
  - repair commit後のlatest-head observationに同じfamily labelのblockerがある。
- 操作:
  - continuationを評価する。
- 結果:
  - recurrenceだけでは停止しない。
  - stale observation、incomplete implementation、failed hypothesis、new evidence、mis-groupingを分類する。
  - prior strategyとの差分がmaterialで、fresh consultationとscope-safe validation pathがある場合だけ継続できる。
  - materially distinct strategyがない、またはevidenceが不足する場合はhuman gateにする。

### 5.5 シナリオ SC-003: Consultation unavailable / unsafe

- 前提:
  - ChatGPT consultationがunavailable、denied、failed、またはsanitized inputを作れない。
- 操作:
  - blocking repair delegationを行おうとする。
- 結果:
  - consultationをpass相当と扱わない。
  - batchにstatus、reason、last safe evidenceを記録する。
  - defaultではautonomous repairを開始せずhuman gateへ移る。
  - humanが対象invocation、許可範囲、根拠、失効条件を明示承認した場合に限り、そのinvocation内で一度だけmanual fallback analysisを用いてrepair delegationを再評価できる。
  - fallbackはChatGPT consultation成功を表さず、次invocationへ持ち越さない。

### 5.6 シナリオ SC-004: Non-blocking only

- 前提:
  - P2/P3、optional check failure、follow-up/no-action itemだけが残る。
- 操作:
  - merge-preparedを評価する。
- 結果:
  - それだけを理由にbranch mutationまたはmandatory repair consultationを開始しない。
  - rationale / residual riskをbatchに残し、既存merge-prepared predicateで判断する。

## 6. 用語

### TERM-001: 固定試行回数制限

P0 1回、same-family P1 2回、total 4回など、iteration countをrepair continuation / stopのauthoritative criterionにするrule。

### TERM-002: 統合blocking repair batch

current latest-head observationでbranch mutationを要するblocking itemsを、個別コメントではなく、共有root cause、coupling、scope、test obligationsを含む一つのdecision surfaceとして扱うbatch。

### TERM-003: 実質的な変更

consultation / strategy freshnessを無効化するほどの意味差分。例:

- head SHAまたはobservation trigger boundaryの変更。
- blockerの追加・削除・severity変更。
- root-cause family groupingの変更。
- prior strategyの失敗または不完全実装の発見。
- 許可されたパス、要件、互換性、セキュリティ影響の変更。
- validation planの変更。

単なるtimestamp、formatting、説明文の非意味差分はmaterial changeではない。

### TERM-004: 戦略差分

prior attempted strategyに対し、root-cause hypothesis、files/behavior boundary、implementation approach、validation approachのどれが変わるかを明示した差分。単なる言い換えはstrategy deltaではない。

### TERM-005: ChatGPT consultation証拠

sanitized integrated batch inputに対するChatGPTの提案を、provenance、scope、freshness binding、summary、open risksと共に保存したevidence。authorizationまたはcanonical decisionではない。

### TERM-006: オーケストレーターのdisposition

ChatGPT recommendationごとにmain orchestratorが記録する `use` / `partial-use` / `reject` / `defer` / `human-gate`。worker handoffは `use` または明示された `partial-use` の内容だけを根拠にできる。

### TERM-007: 強制human gate

attempt countに関係なくautonomous continuationを禁止する既存または本Issueのsafety condition。

### TERM-008: 1回の呼び出しに限定した手動fallback

ChatGPT consultationが利用不能な場合に、humanが対象invocation、許可範囲、根拠、失効条件を明示承認して一度だけ許可するlocal analysis path。consultation成功、恒久waiver、次invocationの許可を意味しない。

## 7. スコープ

### 7.1 スコープ内

1. `github-pr-merge-preparer/SKILL.md`
   - 固定回数制限の削除。
   - 再発分析 / 継続方針。
   - 必須の統合ChatGPT consultation gate。
   - evidence-onlyとしての判断と鮮度。
   - 意味に基づく停止 / human gateの条件。
2. `agents/openai.yaml`
   - 回数制限と誤読されない、evidenceをゲートとする修復表現。
3. スキルローカルのPR修復バッチテンプレート。
4. 配布する成果物用PR修復バッチテンプレート。
5. 配布するディスカッション用PR修復バッチテンプレート。
6. 生成成果物、テンプレート、インストール済みコピーの契約を検証する対象テスト。
7. プロバイダー優先の更新後に行うドッグフーディング同等性検査、validate、sync、対象検査。
8. 既存バッチの再開互換性に関する文書契約。

### 7.2 スコープ外

- ChatGPT呼び出しの実装。
- 新しいCLIオプション、ランタイムコマンド、環境変数、設定スキーマ。
- 機械可読なconsultation / retryスキーマの検証。
- 観測JSONの変更。
- repair workerの実装フレームワーク。
- 自動マージ / レビュー会話の変更。
- GitHub Issueのライフサイクル変更。
- 無関係な文書 / skillへのretry方針の展開。
- 過去の成果物の一括移行。
- `.assurance.json` の変更。

### 7.3 変更禁止

- `github-pr-observation` の収集専用境界。
- latest-headの鮮度要件。
- 必須 / 非必須チェックの意味論。
- P0/P1の修復優先度とP2/P3では変更しない方針。
- merge-prepared / review-cleanの区別。
- 現行skillで禁止されている書き込み / 操作。
- ブランチ保護 / 会話解決のhuman gate。
- ローカルでの統合判断とreviewerの権威。

## 8. 要求される振る舞い

### BH-001: Fixed attempt capをcontinuation authorityから除外する

- 前提: skillまたはtemplateがrepair iterationを扱う。
- 操作: continuation / stopを判断する。
- 結果: numeric attempt countだけではstop / continueを決めない。
- And: count / iteration indexはtelemetryとして記録してよい。

### BH-002: Blocking itemsをintegrated batchとして評価する

- 前提: current observationに複数blocking itemsがある。
- 操作: repair strategyを作る。
- 結果: 全blocking items、shared root cause、coupled files、tests、nonblocking collateralを一つのbatch viewで分析する。
- And: raw findingから直接workerへ委任しない。

### BH-003: Branch-mutating blocking repair前にChatGPT consultationを必須にする

- 前提: current batchにbranch mutationを要するblocking itemがある。
- 操作: workerへrepairをdelegateしようとする。
- 結果: current integrated batchにboundしたfresh ChatGPT consultation evidenceが存在する。
- And: unavailable / failed / denied / stale / unsafe consultationはpassではない。
- And: 例外は明示承認されたone-invocation manual fallbackだけであり、approval evidenceと失効条件をbatchへ記録する。

### BH-004: ChatGPT outputをevidence-onlyとしてdispositionする

- 前提: consultation outputがある。
- 操作: strategyを選ぶ。
- 結果: orchestratorはrecommendationごとにdispositionとrationaleを記録する。
- And: outputはlocal integration decision、fresh reviewer approval、repair authorizationを自動的に持たない。

### BH-005: 同一family再発を再分析triggerにする

- 前提: prior repair後に同一family labelのblocking itemが観測される。
- 操作: continuationを評価する。
- 結果: recurrence class、prior strategy result、new evidence、strategy deltaを分析する。
- And: recurrenceだけではstopしない。

### BH-006: Materially distinct strategyがある場合だけ継続する

- 前提: blockerが残る。
- 操作: autonomous repairを継続する。
- 結果: prior strategyとmaterialに異なるbounded strategy、fresh consultation、allowed scope、validation pathがある。
- And: same ineffective strategyの反復はhuman gateにする。

### BH-007: Hard human gateを維持する

- 前提: permission/auth、external/flaky、base conflict、unknown failure、requirement expansion、breaking/migration/secret/deployment impact、ambiguous intent、platform-only conversation action、unapproved trigger、stale trigger、resume metadata欠落のいずれかがある。
- 操作: continuationを評価する。
- 結果: attempt countに関係なくhuman gateへ進む。

### BH-008: Consultationとiterationをbatchに監査可能に記録する

- 前提: consultationまたはrepair iterationを実施する。
- 操作: batchを更新する。
- 結果: head SHA、observation status、family set、recurrence class、prior/proposed strategy、strategy delta、consultation reference/freshness、orchestrator disposition、fix commit、re-observation、continuation decisionを記録する。
- And: verbatim model conversation recordやunsafe payloadを記録しない。

### BH-009: Provider / mirror / generated outputを同一contractにする

- 前提: provider sourceを変更する。
- 操作: standard update / scaffold / artifact creationとtargeted testsを実行する。
- 結果: installed/dogfooding copiesとgenerated repair batchが同じcontinuation / consultation contractを表す。

### BH-010: Existing batchを非破壊でresumeする

- 前提: old templateで作られたbatchが存在する。
- 操作: current workflowでresumeする。
- 結果: front matter、inventory、historical evidenceを保持し、current headにboundしたconsultation / continuation ledgerを追記してからrepairを再開できる。
- And: bulk migrationは要求しない。

## 9. 受け入れ条件

### AC-001: 数値制限の廃止

- アクター: 保守担当者 / レビュー担当者
- 前提: プロバイダースキルと3つのテンプレートを読む。
- 操作: 固定試行回数上限 / ループ制限の文言を検索する。
- 期待結果:
  - P0 1回、同一ファミリーのP1 2回、合計4回というデフォルトの停止権限が存在しない。
  - `loop limits reached` がStop Conditionsに存在しない。
  - 反復回数はテレメトリであり制限ではないと明示される。
- 関連: `BH-001`

### AC-002: 再発は分析トリガーであり、自動停止ではない

- 前提: 同じ `root_cause_family` が修復後に再発する。
- 操作: スキルの継続ポリシーとバッチフィールドを確認する。
- 期待結果:
  - 再発分類、以前の戦略の結果、戦略差分、相談の鮮度を評価する。
  - 再発だけを理由に停止しない。
  - 実質的に異なる戦略がない場合は人間ゲートになる。
- 関連: `BH-005`, `BH-006`

### AC-003: 必須の統合相談ゲート

- 前提: ブランチ変更を要するブロッキングバッチがある。
- 操作: 修復委任の順序を確認する。
- 期待結果:
  - トリアージ完了後、ワーカーへの引き渡し前にバッチ全体を対象とするChatGPTへの相談を要求する。
  - 相談は現在のhead / 観測 / ファミリー集合 / 戦略コンテキストに結び付けられる。
  - 相談なしに未加工の検出事項から委任できない。
- 関連: `BH-002`, `BH-003`

### AC-004: 相談の鮮度

- 前提: head、ブロッカー集合、ファミリー分類、以前の戦略の結果、許可範囲、検証計画に実質的な変更がある。
- 操作: 既存の相談を再利用しようとする。
- 期待結果:
  - 既存の相談は鮮度切れと判定される。
  - 更新するか人間ゲートへ進む。
  - 実質的でない書式上の差分だけでは不必要に鮮度切れとしない。
- 関連: `BH-003`, `BH-005`

### AC-005: 証拠限定の権限

- 前提: ChatGPTが修復の推奨事項を返す。
- 操作: ワーカーへの引き渡し / バッチ更新を確認する。
- 期待結果:
  - オーケストレーターの採否判断と根拠がある。
  - `use` / `partial-use`以外の推奨事項はワーカーへの入力にならない。
  - 相談はローカルでの統合判断、新たなレビュー担当者の承認、マージ準備完了を主張しない。
- 関連: `BH-004`

### AC-006: 意味に基づく継続ゲート

- 前提: ブロッキング項目が残る。
- 操作: 継続判断を評価する。
- 期待結果: 継続には次のすべてが必要である。
  1. 最新headの観測が新鮮である。
  2. ブロッキング項目の一覧とファミリー分類が完全である。
  3. 強制人間ゲートに該当しない。
  4. 相談が新鮮かつ安全である。
  5. オーケストレーターの採否判断で範囲を限定した戦略が特定されている。
  6. 以前の戦略が失敗した箇所について、戦略に実質的な差分がある。
  7. 許可されたパス / 要求 / 互換性がスコープ内に収まっている。
  8. 検証と再観測の経路が明示されている。
- 関連: `BH-006`, `BH-007`

### AC-007: 相談失敗を合格としない

- 前提: 相談が利用不能 / 失敗 / 拒否 / 危険 / 鮮度切れのいずれかである。
- 操作: 修復の委任を試みる。
- 期待結果:
  - デフォルトではブランチ変更を委任しない。
  - バッチに状態と理由を残す。
  - 人間ゲートへ進む。
  - 人間が1回の呼び出しに限定した手動フォールバックを明示承認した場合だけ、承認範囲内のローカル分析、オーケストレーターの採否判断、範囲を限定した検証を経て委任可否を再評価できる。
  - フォールバックの証拠には承認元、呼び出し識別子、許可範囲、理由、失効条件、手動分析、採否判断を含め、相談成功とは表示しない。
- 関連: `BH-003`, `BH-007`

### AC-008: 強制停止条件の維持

- 操作: 旧スキルと新スキルの人間ゲート分類を比較する。
- 期待結果:
  - 権限 / 認証、外部要因 / 不安定、ベース競合、原因不明、スコープ拡大、破壊的変更 / 移行 / 秘密情報 / デプロイ、意図の曖昧さ、プラットフォーム上でのみ可能な操作、トリガー / 再開の安全性が弱められていない。
  - 回数制限だけが削除される。
- 関連: `BH-007`

### AC-009: バッチ証拠契約

- 操作: 3つのテンプレートを確認する。
- 期待結果:
  - `ChatGPT Consultation Gate` または同義のセクションがある。
  - `Integrated Repair Strategy` または同義のセクションがある。
  - 反復台帳にhead / ファミリー / 再発 / 戦略差分 / 相談 / 採否判断 / 修正 / 再観測 / 判断がある。
  - 停止条件は意味に基づく強制停止を表し、数値上限を含まない。
  - モデルとの会話記録をそのまま貼り付けることの禁止が明示される。
- 関連: `BH-008`

### AC-010: スキル / プロンプト / テンプレートの整合

- 操作: `SKILL.md`、`openai.yaml`、3つのテンプレートを横断確認する。
- 期待結果:
  - すべてが証拠によるゲート / 統合修復を同じ意味で表す。
  - `openai.yaml` が固定回数に制限された修復を暗示しない。
  - テンプレートがスキルのワークフロー権限を上書きしない。
- 関連: `BH-001`〜`BH-009`

### AC-011: 生成出力の回帰検証

- 前提: 一時リポジトリで`new artifact pr-repair-batch`または既存の対応済み生成経路を実行する。
- 操作: 生成されたMarkdownを確認する。
- 期待結果:
  - 新しい継続 / 相談欄が存在する。
  - 旧来の数値による停止マーカーが存在しない。
  - ファイル名 / front matter / 種別 / 親 / 日付の振る舞いは変わらない。
- 関連: `BH-009`, `BH-010`

### AC-012: プロバイダー / ミラーの同等性

- 前提: プロバイダーの編集が完了している。
- 操作: リポジトリ標準の `spec-dock update .`、検証、同期、対象を限定した比較を行う。
- 期待結果:
  - プロバイダーの正本と`.agents/` / `spec-dock/`への投影が一致する。
  - ミラーだけを直接手作業で編集した箇所がない。
  - ユーザーが作成したIssue / 成果物データが保持される。
- 関連: `BH-009`

### AC-013: スコープ外の非変更

- 操作: 差分を確認する。
- 期待結果:
  - 観測スクリプト、実行時コマンド、GitHub変更ロジック、assuranceメタデータに変更がない。
  - P2/P3だけの場合の変更ポリシーに変更がない。
- 関連: `CON-004`, `CON-005`, `CON-009`

### AC-014: 計画専用ゲート — strict計画の完全性

- 操作: 計画案をレビューする。
- 期待結果:
  - 要求 / 設計IDと網羅性索引が対応する。
  - ステップ固有の委任契約と具体的なテストケースがある。
  - S90、strictレビューゲート、S99、最終終了契約がある。
  - 証拠限定の位置付けとローカルでの採用境界が保持される。

## 10. 例外・エッジケース

### EC-001: 鮮度切れの観測を再発と誤認

- 条件: 修復後のバッチが旧headの観測を参照する。
- 期待: 再発分析を行わず、最新headの再観測へ戻る。修復しない。
- 状態変更: ブランチ変更なし。

### EC-002: 同じ症状で異なる根本原因

- 条件: 同じメッセージ / CIチェックだが、証拠が別の根本原因を示す。
- 期待: ファミリーを分割 / 再分類し、相談を更新する。旧ファミリーの回数を引き継いで停止しない。

### EC-003: 以前の戦略の実装不足

- 条件: 根本原因の仮説は有効だが、ワーカーが計画した変更の一部を欠落させた。
- 期待: 不完全な範囲を証拠で特定し、新たな相談 / 採否判断によって範囲を限定した完了戦略を選べる。単なる同一手順の無検証再実行は禁止。

### EC-004: 以前の戦略が反証された場合

- 条件: 再観測が以前の仮説を否定する。
- 期待: 実質的に新しい仮説 / 戦略がなければ人間ゲートとする。ある場合は相談の更新後に継続できる。

### EC-005: 相談が禁止対象またはスコープ拡大を提案

- 条件: 推奨事項が実行時処理 / API / 移行 / 秘密情報 / 要求拡大を要求する。
- 期待: 推奨事項を却下または人間ゲートの採否判断とし、ワーカーへ渡さない。必要なら計画の修正 / フォローアップを行う。

### EC-006: 相談内容を安全にサニタイズできない場合

- 条件: 診断に秘密情報 / 非公開データ / 未加工の専有ペイロードが必要である。
- 期待: 外部への相談を行わず人間ゲートとする。安全でないデータをバッチへ貼らない。

### EC-007: 複数の関連ファミリー

- 条件: 一つの変更が複数のファミリーを同時に解消する、または別々に修正すると競合する。
- 期待: 統合バッチで結合関係を明示し、一つまたは順序付きの修復単位にまとめる。

### EC-008: 修復によって新しいブロッカーが発生

- 条件: 再観測で新しいP0/P1ファミリーが出る。
- 期待: 現在のバッチを実質的な変更ありとして更新し、相談を更新する。旧相談の自動再利用は禁止する。

### EC-009: 任意対応 / 非ブロッキングの失敗が残る場合

- 条件: ブロッキング項目は解消済みだが、P2/P3または既知の任意チェック失敗が残る。
- 期待: 根拠 / 残存リスクを記録し、既存のマージ準備完了ポリシーで判断する。修復回数制限Issueを理由に追加変更しない。

### EC-010: 既存の旧形式バッチの再開

- 条件: 相談セクションがない旧バッチを再開する。
- 期待: 既存内容を保持し、現在のスナップショットに対する新しい台帳を追記する。一括書き換えや履歴削除をしない。

### EC-011: 相談出力内の矛盾

- 条件: 複数の選択肢が相互に矛盾し、証拠で選べない。
- 期待: オーケストレーターは曖昧な推奨事項を採用せず人間ゲートへ進む。

### EC-012: 無制限反復への懸念

- 条件: 数値上限がないためループが長期化する。
- 期待: 各反復では新鮮な証拠、実質的な戦略差分、明示的な検証を要求する。範囲を限定した新しい戦略がない時点で意味に基づき停止する。回数による合格 / 停止は導入しない。

### EC-013: 手動フォールバックの再利用

- 条件: 過去の呼び出しで承認された手動フォールバックを次の呼び出しまたは別のバッチで再利用しようとする。
- 期待: 鮮度切れ / 未承認として拒否し、新しい人間の承認なしに修復を委任しない。

## 11. 非機能・品質要求

### 11.1 監査可能性

- ブランチを変更する各修復反復は、head SHA、戦略、相談、採否判断、コミット、再観測まで追跡できる。
- 対応なし / フォローアップ / 人間ゲートにも根拠を要求する。
- 観測結果はレポート / バッチ台帳へ記録し、計画を実績台帳にしない。

### 11.2 互換性

- 既存のCLI / API / front matter / ファイル名契約を変更しない。
- 過去のバッチは引き続き読める。
- 旧バッチの再開では、追記のみの形式に近い非破壊更新を行う。
- 一括移行は行わない。

### 11.3 セキュリティ / プライバシー

- モデルとの会話記録そのもの、秘密情報、トークン、認証情報、非対称署名用情報、個人データ、ホストローカルの絶対パスを相談成果物またはバッチへ保存しない。
- 相談への入力は必要最小限にサニタイズする。
- 安全にサニタイズできない場合は人間ゲートとする。

### 11.4 信頼性

- 相談が利用不能 / 鮮度切れ / 拒否の場合は合格扱いしない。
- ミラーのずれを対象を限定したテスト / 同等性検査で検出する。
- 生成されたテンプレート内容について、必要なマーカーと禁止された旧マーカーの両方を検査する。

### 11.5 保守性

- ワークフローの権限はスキルに置く。
- テンプレートは証拠欄を持つが、独立したポリシー権限は持たない。
- 回数に基づく文言を別の表層に残さない。
- 実行時パーサー / スキーマを追加しない。

### 11.6 性能 / 外部I/O

- このIssueは実行時性能の契約を変更しない。
- 自動ネットワーク呼び出しを追加しない。
- 実際の相談実行にかかるコスト / 待ち時間はホストワークフロー側の関心事であり、このIssueでは実装しない。

## 12. 制約

### CON-001: 証拠限定の権限

ChatGPTの出力と本パックは証拠限定である。正本への反映にはメインオーケストレーターによる明示的なEAL採否判断が必要である。

### CON-002: 認可済みプロファイルを主張しない

`strict` は推奨案である。`.assurance.json`、分類、承認済みプロファイルを変更または決定しない。

### CON-003: プロバイダーソース優先

配布される成果物の正本は`src/spec_dock/assets/**`である。ドッグフーディング用コピーは生成 / 検証の表層である。

### CON-004: 観測境界を変更しない

`github-pr-observation`は収集専用であり、相談 / 採否判断 / 継続判断を担わない。

### CON-005: GitHub変更境界を変更しない

マージ、自動マージ、ブランチ削除、レビューへの返信 / 解決 / 却下、Issueのクローズ / 完了を追加しない。

### CON-006: ブロッキングなブランチ変更には相談が必須

ブロッキングな修復の委任には新鮮な相談証拠が必要である。失敗 / 利用不能 / 拒否 / 危険 / 鮮度切れの場合、デフォルトでは人間ゲートとする。唯一の例外は、人間が対象の呼び出しに限定して明示承認した1回の呼び出し限定の手動フォールバックであり、恒久的な免除または相談成功として扱わない。

### CON-007: 数値による停止権限を設けない

反復回数はテレメトリとしてのみ扱う。数値しきい値を停止 / 継続 / 承認に使用しない。

### CON-008: 意味に基づく終了条件が必須

同一戦略の反復、新しい戦略の不在、証拠不足、スコープ拡大、強制停止の場合は人間ゲートとする。上限の削除を無条件の再試行に変えない。

### CON-009: 実行時処理 / スキーマを変更しない

CLI、実行時処理、JSONスキーマ、データベース、ネットワークアダプターを変更しない。

### CON-010: P2/P3ポリシーを変更しない

P2/P3だけを理由に追加のブランチ変更を行わない。

### CON-011: 安全な出力

モデルとの会話記録そのもの、秘密情報、認証情報、非対称署名用情報、ホストの絶対パス、入れ子のアーカイブ、バイナリ、実行可能ファイル、シンボリックリンクをオーサリングパックへ含めない。

### CON-012: 鮮度の結び付け

相談と継続判断は、現在のhead、観測境界、ブロッキング項目の集合、ファミリー分類、戦略コンテキストに結び付ける。

## 13. 依存関係

### 13.1 前提

| 種別 | 対象 | 必要理由 | 状態 |
|---|---|---|---|
| Parent Epic | `epic-00158` | skill/evidence/provider authority boundary | mainで確認済み |
| Historical Issue | `iss-00178` | triage batch / root family / merge-prepared baseline | mainで確認済み |
| Current skill | `github-pr-merge-preparer` | fixed-limit baseline | mainで確認済み |
| PR #311 | ChatGPT-firstの計画・証拠境界 | consultation authorityの制約 | mainにマージ済み |
| ローカルプロンプトパック | ソースマニフェストとclarification artifact本文 | operatorの意図と採用された統合結果 | local-contextとして確認済み |
| Issue #313 | タイトル / 存在 | タスク識別 | オープン |

### 13.2 フォローアップ候補

| ID | 内容 | 条件 | Blocking |
|---|---|---|---|
| FU-001 | consultation runtime/adapter automation | host-manual consultationでは不足すると判断された場合 | no; separate Issue |
| FU-002 | machine validation of batch schema | Markdown driftが継続する場合 | no |
| FU-003 | cross-skill evidence-gated retry ADR |複数skillsへ同じpolicyを展開する場合 | no |
| FU-004 | observation schema extension |collection evidenceだけではfreshness binding不能な場合 | design-dependent |

### 13.3 ブロッカー

Issue境界判断を止めるblockerはない。local artifact body inspection、source hash / branch state verification、要件候補の採用判断は完了している。assurance/profile workflowとfresh requirement/design/plan reviewsは後続のplanning gateとして実施する。

本変更は長期運用policyを固定するADR candidateである。ADR facilitationはdesignと並行可能な非blocking planning obligationとし、Issue Execution開始前までに採用ADRまたは「既存ADRで十分」とする根拠を確定する。

## 14. Grade 判定材料

### 14.1 推奨 grade

- [ ] lite
- [ ] standard
- [x] strict（要件上の推奨。正式なprofileはassurance workflowで確定）
- [ ] critical
- [ ] 未判断

### 14.2 理由

- agent workflow policyを変更する。
- shipped skill、agent prompt、3 templates、generated output contractに影響する。
- provider/mirror compatibilityを検証する必要がある。
- failure/recovery、authority、security sanitation、human gateを明示する必要がある。
- rollbackは容易でmigrationなしのためcriticalまでは不要。

### 14.3 Risk facts（assurance入力。assurance decisionではない）

| Risk fact | Candidate value | 理由 |
|---|---|---|
| `docs_only_change` | false | skill/templates/testsを変更する |
| `runtime_behavior_change` | false | CLI/runtime codeは非対象 |
| `public_contract_change` | true | shipped agent workflow/template contractを変更する |
| `migration_or_persistence_change` | false | 過去バッチの一括移行なし |
| `rollback_difficulty_high` | false | providerの文章・テンプレートをrevertして更新すれば戻せる |
| `security_or_privacy_sensitive` | false, guarded | secrets送信禁止を明示するが認証情報の取り扱い自体は変更しない |
| `agent_workflow_policy_change` | true | continuation・human-gateの契約を変更する |

### 14.4 Criticalへのエスカレーショントリガー

- GitHub state mutationを追加する。
- secret / authentication material / private dataを自動収集・送信する。
- destructive migrationを追加する。
- human confirmationなしにhigh-risk strategyを自動実行する。
- rollback不能なpersistent stateを導入する。

## 15. Designへの引き渡し

Designは最低限、次を固定する。

1. count-based policyからsemantic continuation gateへのcontract delta。
2. 統合バッチ、重要な変更、戦略差分、consultation evidence、orchestratorの判断の語彙。
3. consultation入力のサニタイズ、鮮度との紐付け、出力の保持。
4. 再発分類と継続判断表。
5. 強制停止の維持。
6. skill / prompt / 3つのtemplateの責務分担。
7. provider優先 / mirror更新 / 互換性戦略。
8. ランタイム / スキーマ / GitHubを変更しない境界。
9. テストへの影響と旧マーカー禁止のチェック。
10. 旧バッチの再開、失敗 / 復旧、ロールバック。

## 16. 採用判断と後続ゲート

### 採用事項 ADOPT-001

Mandatory consultationの範囲を「branch mutationを要する全blocking repair batchのworker delegation前」とする。これは `interview-mandatory-chatgpt-consultation-scope` の回答と採用済み統合分析に一致する。

### 採用事項 ADOPT-002

Material change後はconsultation refreshを要求する。単一consultationを無期限再利用しない。

### 採用事項 ADOPT-003

Repair batchにはraw model conversationを埋め込まず、sanitized summary / provenance / dispositionを保存する。一方、planning evidenceとしてのChatGPT raw outputはscope-local artifactへ別途保存できる。

### 計画ゲート

- [x] local artifact bodiesを確認した。
- [x] EALにChatGPT evidenceの採否と変換来歴を記録する。
- [x] adopted synthesisとの一致を確認した。
- [x] canonical requirementへmain orchestratorが反映した。
- [ ] fresh spec reviewを通した。
- [ ] assurance/profile workflowを別途完了した。

未完了項目は後続planning phaseのゲートであり、本要件はfresh spec review前のcanonical draftである。
