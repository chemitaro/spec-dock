---
種別: interview
ID: "20260809t004834z-interview"
タイトル: "Target Artifact Surface Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-08-09"
親: ["iss-00357"]
関連:
  - "iss-00358"
  - "iss-00359"
  - "iss-00360"
  - "20260808t082616z-research"
  - "20260808t162136z-interview"
scope: "issue"
scope_id: "iss-00357"
created_at: "2026-08-09T00:48:34Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT Use Strict session: required-strict-github-connector-verificati-3"
  - "verified GitHub repository: chemitaro/spec-dock"
  - "verified branch: main"
  - "verified expected SHA: fc15d782e6ad927c618af6f2774f72ad7507af87"
  - "ChatGPT Use Strict follow-up session: required-strict-github-connector-verificati-5"
  - "follow-up verified expected SHA: 1c8a8b25470f5b374e44623349d157499df99768"
reflected_to: []
---

# 20260809t004834z-interview Target Artifact Surface Interview

## 位置づけ

- Active SelectionとWork Startを分離するOption A採用後、ChatGPT Use StrictがGitHub上の最新commitを再調査し、残存Gapの第1位として選定した。
- Currentの新規作成SurfaceとHistorical Evidenceの読取り互換性を分け、provider固有のChatGPT / PR Workflow契約をStorage Coreから除去するかを決める。
- 回答後はこのArtifactへ記録し、commit・push後に同じChatGPTスレッドへStrictで返す。Canonical docsへの反映は別工程とする。

## 正式質問として扱う理由

- `requirement.md`:
  - Storage Coreが新規作成・Importで保証するArtifact Surfaceと、Historical Evidenceの保持契約を決める。
- `design.md`:
  - Current creatable type、Historical recognizable type、generic import、parser / domain / applicationの責務境界を決める。
- `plan.md`:
  - provider固有Command・Template・Rule・Testの削除、Historical file保持、generic importの安全性回帰を決める。
- chat上の軽微な一問では足りない理由:
  - Issue 357のRuntime、Issue 358のArtifact semanticsとGuide、Issue 359のGrilling Skill、Issue 360のPrune / Migrationに同時に影響する。

## 質問の目的

- 対象者:
  - SpecDockのProduct Ownerであるユーザー。
- 何を明確にする質問か:
  - Targetの新規Artifact type、Import Surface、provider固有Surface、Historical Evidence互換性をどの構成にするか。
- 回答が後続判断へ与える影響:
  - Issue 357 / 358のRequirement / Design / Planと、Issue 359 / 360へのhandoffを固定する。

## 質問

- pressure-test question:
  - 外部インテリジェンスの交換可能性を目標にしながら、ChatGPT専用ImportやPR Workflow専用ArtifactをCurrent Surfaceに残すと、provider固有契約がStorage Coreへ再侵入しないか。
- 質問:
  - Targetの新規Artifact Surfaceを、どの構成にしますか？
- 回答してほしいこと:
  - Option A、B、Cのいずれかを選択してほしい。

## source-grounded context

- ChatGPT Use StrictはGitHub connectorで`chemitaro/spec-dock`の`main`先端が期待SHA `fc15d782e6ad927c618af6f2774f72ad7507af87`と完全一致することを確認し、そのcommitだけを参照した。
- 親Epic DesignはGrillingが`interview`または`analysis` Artifactを作るとするが、現行Runtimeに`analysis` typeは存在しない。
- 現行のDirect Artifactは`blank`、`research`、`interview`、`disc`、`decision-candidate`、`pr-repair-batch`、`adr`である。
- `pr-repair-batch`はPR observation、P0 / P1、merge-prepared、ChatGPT consultation gate等の削除対象Workflowへ強く結合している。
- CLIにはprovider固有の`artifact import chatgpt-output`とprovider-neutralな`artifact import file`が並存する。
- Generic `artifact import file`はroot / Initiative / Epic / Issueを対象とし、明示ファイルをopaque evidenceとして保存する実装を持つ。
- Existing ArtifactはProductの歴史的証跡であり、Current Surfaceから外す場合も削除やMalformed扱いをせず保持する必要がある。

## 回答案

- Option A — 最小のprovider-neutral Surface:
  - 新規作成可能なTyped Artifactを`blank`、`research`、`interview`、`disc`、`decision-candidate`、`adr`の6種に限定する。
  - `analysis` typeは新設せず、単独調査は`research`、ユーザー質問は`interview`、統合・分析・Reflectionは`disc`を使う。
  - Importは`artifact import file`だけをCurrent Surfaceに残し、`artifact import chatgpt-output`を削除する。
  - `pr-repair-batch`と採用済み方針の`draft-*`を新規作成Surfaceから外す。
  - Existing `pr-repair-batch`、`draft-*`、旧Discussion、ChatGPT出力はHistorical Evidenceとして認識・保持する。
  - Domain上で「Current creatable type」と「Historical recognizable type」を分離する。
- Option B — Provider-neutral Surfaceに`analysis`を追加:
  - Option Aに加えて、新規作成可能な7種目として`analysis`を追加する。
  - `research`・`disc`・`analysis`の排他的な意味、Grillingでの使い分け、Template、Rule、Naming、Testを追加定義する。
  - provider固有Importと`pr-repair-batch`はOption Aと同様にCurrent Surfaceから外す。
- Option C — Specialized Surfaceを一部維持:
  - `artifact import chatgpt-output`と`pr-repair-batch`をCurrent Surfaceに残す。
  - `draft-*`は採用済み方針に従い撤去する。
  - Product-owned ChatGPT / PR Workflow固有のCommand、Application、Template、Rule、TestがCurrent製品境界に残る。

## Codex の分析

- 判断軸:
  - Runtime軽量化、provider neutrality、Artifact typeの重複防止、Historical Evidence互換性、generic importの安全性、Issue間の分担。
- tradeoff:
  - Aは現行の汎用typeを再利用してSurfaceを最小化する。Bは`analysis`という直感的な名称を追加できるが、既存typeとの使い分け規則が増える。Cは現行利便性を残すが、削除対象のProduct-owned Workflowとprovider固有契約を維持する。
- リスク:
  - AでChatGPT専用Importを削除する前に、Workbench source guard、opaque-byte preservation、privacy-safe error、retry / partial cleanupのうちgeneric importにも必要な安全性が保持されるか回帰確認が必要である。
- 具体シナリオ / edge case:
  - Current Surfaceから外れた既存`pr-repair-batch`がnodeに残っていても、`validate`・`sync`・`active set`はそれをHistorical Evidenceとして保持し、Malformedとして失敗しない。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - `research`、`interview`、`disc`で調査・質問・統合分析を表現でき、`analysis`の新設は重複を増やす。`pr-repair-batch`は削除対象PR Workflowへ強く結合し、generic importが存在するためChatGPT専用ImportをCurrent Surfaceに残す必要性が低い。
- 未回答時の影響:
  - Issue 357はCurrent Artifact typeと削除対象Command / Application / Testsを固定できず、Issue 358もArtifact semanticsとGuideの語彙を固定できない。

## 回答後のCLI構文整理

- 位置づけ:
  - ChatGPT Use StrictがGitHub connectorで`main`先端とSHA `1c8a8b25470f5b374e44623349d157499df99768`の完全一致を確認した上で提示したAdvisoryな設計整理である。
  - Product semanticsはユーザー回答で確定済みであり、CLI表記は既存契約との整合から解決できる低影響な設計事項と判定した。
- 推奨Target構文:
  - `spec-dock new artifact [type] (--initiative <id> | --epic <id> | --issue <id>) --title <title> [--slug <slug>]`
  - `type`は省略可能な位置引数とし、省略時は`blank`を既定値にする。
  - 明示的な`blank`指定も維持する。
  - `--type`という二重構文は追加しない。
- 理由:
  - 現行の`new artifact research ...`等を壊さず、位置引数の省略だけを追加できる。
  - ScopeとTitleは既に名前付き引数であり、位置引数を省略可能にしても構文上の曖昧性は生じない。
  - 未知typeとHistorical-only typeはファイル書込み前にParserで拒否できる。
- 必須テス含意:
  - type省略時の`blank`、明示`blank`、残る5つのTyped Artifact、未知type拒否、Historical-only type拒否、Helpの`[type]`とdefault表示、Blank filenameの`blank` token非含有を回帰対象にする。
- adoption status:
  - proposed design resolution。Canonical docsへはまだ未反映。

## 各Issueへの影響

| 選択 | Issue 357 | Issue 358 | Issue 359 / 360 |
|---|---|---|---|
| A | Current creatable typeを6種、Importを`file`だけと定義する。DomainをCurrent creatableとHistorical recognizableに分離し、ChatGPT専用Import、PR repair、`draft-*`作成経路を除去する。 | 6種の意味と使い分けをGuideへ定義し、Epic Designの`analysis`表現を`research` / `disc`へ整理する。 | Issue 359はGrillingで`interview`、調査で`research`、統合で`disc`を使う。Issue 360はobsolete managed assetをpruneしつつnode-local Historical fileを保持する。 |
| B | Aに加えて`analysis`のDomain type、Filename parser、Create contract、Template loader、Testを追加する。 | `analysis`と`research` / `disc`の排他的な意味を定義する。 | Issue 359のArtifact選択ロジックが増え、Issue 360は追加Assetのparityを検証する。 |
| C | ChatGPT専用Import Application、Workbench guard、PR repair Artifact、関連TestをRetained Coreに残す。 | Current Authoring KitにChatGPT / PR repair固有意味論を残す。 | Issue 359がSpecialized Surfaceを説明し、Issue 360はProduct-owned ChatGPT / PR assetを完全にpruneできない。 |

## ユーザー回答

- answer capture:
  - 「オプションAを採用します」と明示された。
  - 加えて、type未指定では`blank`を使い、定型Templateが必要な場合だけtypeを引数で明示するCLIへ変更する意向が示された。
  - `pr-repair-batch`と`draft-*`の削除に賛成することも明示された。
- 回答:
  - Option Aの最小provider-neutral Surfaceを採用する。
  - Currentの新規作成可能Typeは`blank`、`research`、`interview`、`disc`、`decision-candidate`、`adr`の6種とする。
  - `analysis`は追加せず、単独調査は`research`、ユーザー質問は`interview`、統合・分析・Reflectionは`disc`を使う。
  - `new artifact`でtypeを指定しない場合は`blank`を既定値とする。`blank`は記述構造をTemplateで強く拘束せず、モデルの分析能力と対象文脈に応じた柔軟な記述に委ねる。
  - `research`、`interview`、`disc`、`decision-candidate`、`adr`の定型Templateを使いたい場合は、typeをCLI引数で明示する。
  - Importは`artifact import file`だけをCurrent Surfaceに残し、`artifact import chatgpt-output`を削除する。
  - `pr-repair-batch`と`draft-*`を新規作成Surfaceから外す。Existingの対応ArtifactはHistorical Evidenceとして認識・保持する。
  - Domain上で「Current creatable type」と「Historical recognizable type」を分離する。
  - 現行CLIは`new artifact <type>`としてtypeを必須の位置引数にしている。目標CLIでの正確な構文を`--type <type>`の名前付き引数にするか、省略可能な位置引数にするかは、ユーザー回答では明言されていないため後続の設計判断とする。
- 回答日時:
  - 2026-08-09

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次のunanswered `interview`として切り出す質問:
  - `report.md`のTarget semantics、または回答後のStrict再調査でより高影響と判断された一問。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - Issue 357 / 358のRequirement / Design / Plan、Issue 359のSkill契約、Issue 360のPrune / Migration。
- 採用 / 棄却 / deferred の理由:
  - Product OwnerがOption Aを明示採用し、type未指定時の`blank`既定値と、定型Template使用時の明示type指定を追加意図として示したため。
  - Templateへの不要な拘束を避けながら、InterviewやADR等では必要な定型構造を明示的に選べる。
- `report.md` Evidence Adoption Ledger への反映要否:
  - 旧EALを必須化せず、Canonical reflection時に通常の採用証跡を残す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Current Artifact Surface、type未指定時の`blank`既定値、provider neutrality、Historical Evidence保持の契約を採用候補として反映する。
- `design.md`:
  - Current creatable / Historical recognizableの分離、type選択CLI、generic import、parser / domain / applicationの責務を採用候補として反映する。
- `plan.md`:
  - provider固有Surfaceの除去、type省略 / 明示指定のCLIテスト、Historical compatibility、generic importの安全性回帰テストを採用候補として反映する。
- `ADR`:
  - Issue Designで十分に固定できるかをauthoring時に判断する。
- reflected_to 更新方針:
  - Canonicalへ実際に採用した時点で更新する。
- adoption reflection:
  - Interview Artifact上で採用済み。Canonical docsにはまだ未反映。
