---
種別: 要件定義書（Issue）
ID: "iss-00415"
タイトル: "共通CLI刷新後の操作案内・補完契約の整合"
関連GitHub: ["#415"]
状態: "実装承認済み"
最終更新: "2026-10-06"
親: ["epic-00080", "init-00079"]
---

# iss-00415 共通CLI刷新後の操作案内・補完契約の整合 — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)。実現方法は[設計](design.md)、実装順序と確認方法は[計画](plan.md)に分離します。

> 2026-10-06、ユーザーが本書と実装計画に沿う実装・完了を承認しました。仕様策定時点では各実装・適用は未実施でした。現在の実施状態と実測は[Plan](plan.md)と[Report](report.md)を参照します。仕様採用だけを実装・実環境適用・Issue完了の証拠にはしません。

## 目的

CLI刷新後に利用者が接する診断、README、CLI参照、Sync説明、agent入口、shell補完、GitHub Aboutを、現在の外部installed CLIの操作契約へ整合させます。利用者が提示された案内から安全な次の操作を判断でき、提示された実行例・補完が既存の受付条件と矛盾しない状態が、一つのend-to-endの成果です。

本IssueはSD-OPS-001〜007をまとめます。七つの症状が同じ関数の不具合であるとは主張しません。「同じCLI刷新に対する利用者向け操作契約の整合」という一つの成果に束ねることは、今回の明示的な依頼に基づく範囲決定です。新しいCLI体系、状態管理制度、skill配置方式は設計しません。

## 背景

### 検証した基準と情報の区分

| 項目 | 基準・扱い |
|---|---|
| Repository | `chemitaro/spec-dock` |
| 対象branch | `codex/iss-00415-cli-refresh-specs` |
| expected full SHA | `95ec39b751054bf48098215fc077fe7b8f533f62` |
| GitHub connectorで取得したbranch-tip full SHA | `95ec39b751054bf48098215fc077fe7b8f533f62`。2026-10-06の本依頼で新しく照会し完全一致を確認しました |
| 対象Issue | `iss-00415`／GitHub #415。指定canonical directoryの`.meta.json`にある親・linkageを基準にします |
| 現行3文書 | 同じ仕様策定seedです。実装済み仕様や異なる三つの完成文書ではありません |
| 親のOPEN確認 | init-00079／epic-00080のGitHub OPENは、今回ユーザーが確認済みと提示した観測です。本書作成時の再実行結果ではありません |
| 既存調査 | 下記二つの実在Artifactを材料として、採用範囲だけを本書へ再記述します |
| 調査・検証の限界 | sourceとテストコードの読取り、基準blobとの内容照合です。pytest、SpecDock CLI、wheel build、実shell補完は今回実行していません |

採用先canonical directory（repository rootからのpath）は次です。

```text
spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00415-cli-refresh-operational-contract-alignment/
```

以後の`repo-root:`表記は「このrepository rootからのpath」を明示する注記であり、`repo-root`というdirectoryを作る指示ではありません。行番号は上記基準SHAの本文行番号です。

### 根拠資料

| 根拠ID | 実在する参照先 | 本Issueでの扱い |
|---|---|---|
| B-01 | [ローカル照合結果](artifacts/20261006t035502z--verified-report.md) | mainの`0e7dc86841cb48d011270a1a2165cb6406ac0cea`を対象とした過去の観測。七件の範囲と未検証事項を確認します |
| B-02 | [外部分析原文](artifacts/20261006t035503z--chatgpt-report.md) | advisoryです。未採用の廃止・global化提案を本Issueの義務へ昇格させません |
| B-03 | Initiativeの[Requirement](../../../../requirement.md)・[Design](../../../../design.md)・[Plan](../../../../plan.md) | repo内で対処する保守課題、provider-first、証拠と責務の分離を継承します |
| B-04 | Epicの[Requirement](../../requirement.md)・[Design](../../design.md)・[Plan](../../plan.md) | E-RQ-001〜004の範囲限定と具体的Issue文書の要求を継承します |
| B-05 | [Issue 413 recovery planning pack](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/README.md)の[Requirement](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/requirement.md)・[Design](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/design.md)・[Plan](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/plan.md) | 外部package、直接対象、観測Sync、局所static更新、保全の背景契約です。当時のrollout状態・試験・reviewを現在の実績へ転記しません |
| B-06 | `repo-root: AGENTS.md`、`src/spec_dock/`、`tests/` | 現在の責務・受付・配布・試験の実装根拠です。具体的なpathとsymbolは設計の根拠表に示します |

B-01に記録された「3 passed in 2.71s」は、その記録で指定された限定テストの過去結果です。Issue 415のnegative test、現在候補の全件試験、fresh wheel、global package更新の成功ではありません。Artifact内の当時の「Issue/PR未作成」「Workbench」等も、その作成時点の記述として保存します。本Issueの現在位置は上記canonical directoryとGitHub #415です。

### 親から継承しない旧操作記述

親Epic Requirementの`.agent/index.json`観測、active set／validate／syncの組合せ、Epic Designのtree projection更新、親Planの同種記述は、今回の現行操作の受入条件にしません。新規直接対象の取得はStart、Syncは観測という現在の契約を維持します。

これは親の保守目的やIssue分割方針の変更ではありません。親文書を本作業で一括改稿せず、古い操作例をIssue 415へコピーしない境界です。外部consumerのCI・deploy等の障害は対象外です。GitHub Aboutは本製品repositoryの公開説明であり、今回明示的に許可された仕様範囲に含めます。

## 観測可能な要件

<a id="rq-415-001"></a>
### RQ-415-001 legacy metadataの安全な診断（SD-OPS-001）

旧`meta.json`を検出したとき、利用者へ一律rename・上書き・削除を指示しません。変更前の保全、同じdirectoryの既存`.meta.json`の有無・内容の確認、両者がある場合の比較、正本と取り扱いの手動判断を促します。`.meta.json`がない場合も、filename変更だけでschemaや内容が移行できるとは説明しません。

CLIは現在どおり、その検出によってcreate/importを失敗させます。metadataを書き換える、legacyを自動採用する、GitHubにIssueを作る、失敗を成功にする修正はしません。現在の問題は「危険な手作業を誘導し得る文言」であり、「CLIが既存`.meta.json`を上書きする実装不具合」ではありません。

<a id="rq-415-002"></a>
### RQ-415-002 非対話Scope作成例の整合（SD-OPS-002）

READMEの三階層の`scope create ... --json`例に必要な`--yes`を明示し、承認された作成操作の例であることを説明します。実際の操作では返却されたIDと実在する親を使います。`--json`だけで承認を代替したり、`--yes`で安全検査を迂回できると説明したりしません。

CLIの確認guardは変更しません。`--yes`のない非対話作成が失敗する現在の境界を維持します。すべてのコマンドへ機械的に`--yes`を追加することも禁止します。

<a id="rq-415-003"></a>
### RQ-415-003 通常TARGETとimport refの区別（SD-OPS-003）

現行の文法を文書に反映し、文書を成立させるためにparserを拡張しません。

| 用途 | 案内する入力 | 案内しない入力・注意 |
|---|---|---|
| 通常のScope TARGET | 完全なScope ID、`gh:OWNER/REPO#NUMBER`、対象leafで使用可能な`@current`／`@initiative`／`@epic`／`@issue` | 裸の番号、Issue URL、任意filesystem pathを通常TARGETとして宣伝しません |
| `scope import github KIND REF` | `gh:OWNER/REPO#NUMBER`、完全なGitHub Issue URL、または裸番号と`--github-repo OWNER/REPO`の組合せ | 裸番号からrepositoryを暗黙推定しません。異なるrepositoryの指定・矛盾したhintは拒否されます |
| Artifact所有者 | 現行のScope selectorに加え、許可されたArtifact操作だけの`@root` | `@root`をScope作成やStartの対象にしません |

構文として有効でも、対象の存在、選択状態、親子、linkage等の業務条件は別途満たす必要があります。既存local backendの保全互換と、新規local Scope作成の可否を分けます。新規作成はGitHub番号を使います。

rootのGitHub連携文書の「固定外部エンジン」を現在の外部installed packageの説明へ改め、裸番号import例へ`--github-repo`を加えます。

<a id="rq-415-004"></a>
### RQ-415-004 Sync文書を観測契約へ整合（SD-OPS-004）

rootのSync文書は、現在のScope状態と同じclone内worktreeの直接対象をその場で観測する操作として説明します。既定のlocal観測と明示的なGitHub観測を分けます。観測できない状態をempty・completed・完全観測とみなさない説明を維持します。

`--source cache`、index/tree等の再生成、現在機能としてのjournal再開・rollbackを実行手順にしません。旧状態をraw/legacy診断で読むことと、旧journalを現行の制御基盤として使うことは別です。履歴への参照は履歴と明示します。

<a id="rq-415-005"></a>
### RQ-415-005 現行agent入口と日時付きrollout履歴を分離（SD-OPS-005）

AGENTSの現在の入口から、2026-10-03の0805限定適用・merge pendingを現在状態として読む表現を外します。PR #414がmergeされた事実と、そのcommitを含むことだけでは他のtool環境・linked worktreeの移行を認定できないことを、別の事実として説明します。

Issue 413 recovery planning pack、実装記録、当時の試験・review・rolloutの原本を変更しません。必要な履歴参照は日時付きの既存原本へ向けます。正式Issue 413 import／Start、package公開、他環境の更新を、本Issueの文書修正から完了扱いにしません。

<a id="rq-415-006"></a>
### RQ-415-006 補完候補とleaf受付条件の整合（SD-OPS-006）

Bash／Zsh／Fishの候補は、現在のleaf別受付条件に合わせます。読取りleafへ`--yes`と同義の`-y`を出さず、`work start`以外へ`--lock-timeout`を出しません。`work start`では両方を維持し、他の変更leafでは受付どおり`--yes`／`-y`を維持します。

44 leafのcatalog、既存の共通optionの位置自由度、inline値、option値とoperandの区別、既存の`--`境界、context-freeなhelp/version/completionを維持します。候補集合を直すために、実行側の受付条件を緩めたり、Git・認証・projectへのアクセスを補完へ追加したりしません。現在の受付分類を、その操作が結果的にunchangedになり得ることだけを理由に変更しません。

<a id="rq-415-007"></a>
### RQ-415-007 GitHub Aboutの整合と独立した適用証拠（SD-OPS-007）

本repositoryのAbout descriptionを、worktree外の通常installed Python CLI、Linux/macOS、明示projectへの静的資産配置という現在の説明へ合わせます。`uvx`でコピーするだけ、`.spec-dock/`、runtime不要という旧紹介を現在の方式として残しません。具体的なdescription候補は設計に置きます。

変更対象は`description`だけです。homepage、topics、可視性、権限、branch設定、その他repository設定は変更しません。実行は後続の明示された実施許可と正規の操作手段を前提にし、変更前観測、送信した値、結果、独立したlive GETによるread-backを記録します。

READMEのcommit、仕様ZIPの生成・採用、PATCH応答だけではAbout更新を完了としません。書込みを実施していない場合は未実施、書込み成否を確認できない場合は確認不能とし、SD-OPS-007の受入は保留します。

<a id="rq-415-008"></a>
### RQ-415-008 配布資産と導入先の整合

配布文書はprovider-firstで変更し、current hashと既知旧hashの根拠を維持します。fresh wheel、worktree外の非editable隔離環境、fresh consumerの内容と実consoleの挙動が一致することを確認します。既知旧版からの静的更新、unknown改変時の停止、backup・復元確認の境界も維持します。

ユーザー共通package更新と、一つの明示したworktreeへのstatic更新を別操作・別証拠にします。sourceの変更、candidate環境へのインストール、他worktreeの更新から、利用者のpackageや対象consumerが更新済みだと推測しません。通常のstatic更新でworkspace宣言、Scope metadata、直接対象、既存成果物を一括置換しません。

<a id="rq-415-009"></a>
### RQ-415-009 品質・履歴・完了表示の正確性

通常の`make lint`と`uv run pytest`を維持し、差分検査、変更した境界のnegative test、配布検証を行います。policy skip、regression ledger、旧writer/shared control/cache/journalを復活させません。

観測結果には対象SHA、環境、コマンド、exit、対象test、skip・未実施を対応付けます。文書作成、限定試験、全件試験、実配布、対象worktree適用、About read-back、human mergeを別の状態として記録します。testが存在することや、過去候補のpassを現在のpassとしません。

## スコープ

### 含める変更

七件の診断・例・参照・説明・補完・Aboutと、それらの整合に不可欠なprovider文書、inventory、既存テストの拡充を含めます。対象worktreeへの静的適用は、実施段階で正確なrootと許可を確認した一つだけに限定します。新規機能ではなく、現在の操作契約との不整合を修正します。

### 非対象

root `./spec`の廃止、配布薄いshimの廃止、現役rules symlinkの削除、旧資産の一括削除、無関係なdead code整理、global skill移行、同名local/global skillの優先順位決定、他worktree更新、正式Issue 413 Start、human mergeは対象外です。現在のproject-local skillを維持します。

新しいScope schema、writer protocol、CLI leaf、GitHub repository推定、migration方式、認証・権限変更、release／deploy／package公開制度、Windows対応を追加しません。About以外のGitHub設定は対象外です。

### 維持する境界

通常入口は外部`spec-dock`です。`./spec`、薄いshim、rules symlink、ignoredな旧active投影、現在の直接対象記録を混同しません。新規直接対象取得はStart、Syncは観測、metadataと成果物は保全優先です。既存の失敗・partial・unknownの区別を弱めません。

## 失敗・境界条件

| 条件 | 必要な扱い |
|---|---|
| `meta.json`と妥当な`.meta.json`が同居 | create/importを副作用なしで停止し、両方の保全・比較・人の判断へ戻します |
| `.meta.json`自体が欠落・不正 | 先行する構造検査で停止してよい条件です。必ずlegacy診断へ到達すると仮定せず、検査を迂回しません |
| 非対話createで`--yes`なし | 現在の確認不足の失敗を維持します |
| 通常TARGETへURL／裸番号、importのhint不足・矛盾 | 現在の拒否を維持し、文書側を修正します |
| GitHub観測失敗・worktree観測不完全 | 不明・不完全を保持し、保存cacheで成功にしません |
| static資産のunknown改変・backup不備 | 適用を停止し、現物保全とmanual mergeへ戻します |
| static更新後の部分失敗 | 成立・不明・未実行の効果とbackupを残し、自動rollbackや無条件再実行をしません |
| Aboutの権限不足／読取不能 | 当該stepを保留し、認証設定を勝手に変更しません |
| Aboutの送信後応答不明／read-back不一致 | 成功を断定せず、再GETと競合確認を行い、自動再送・他設定の巻戻しをしません |
| native shellがない | そのshellの実補完確認は未実施です。文字列検査だけで三shell合格としません |

## 受け入れ条件

以下は製品・運用の将来の完了条件であり、本書作成時はすべて未検証です。実装stepと検証IDへの完全な対応は[計画の対応表](plan.md#traceability)に置きます。

| AC | Given / When | Then / 観測する結果 | 対応RQ |
|---|---|---|---|
| AC-415-001 | 妥当なschema3 Scopeに旧`meta.json`を同居させ、公開create/importをtext／JSON、apply／dry-runで実行します | legacy検出の失敗、現行exit・error分類、effectsなしを維持します。両file、その他metadata、Git、直接記録、成果物が不変で、remote変更・stage公開がありません。保全・既存file確認・比較・手動判断の案内があり、一律rename案内がありません | RQ-415-001 |
| AC-415-002 | READMEの三階層の作成例を、実Git・stateful gh stubの妥当なfixtureで実行します | `--json --yes`が揃い、返却IDで親子を結び、想定する作成が成功します。`--yes`を外した対照例は確認不足で停止し、remote変更・local公開がありません | RQ-415-002 |
| AC-415-003 | 通常TARGETとimport refの正例・負例、rootの掲載import例を照合します | 文法表の区別、裸番号＋repo、完全ref／URL、hint矛盾の拒否が既存挙動と一致します。固定外部エンジンという現在説明がなく、新規local作成を許す説明もありません | RQ-415-003 |
| AC-415-004 | root Sync文書の現行例とlocal／github／退役cacheの操作を照合します | local／github観測を案内し、保存再生成やjournal replayを約束しません。既存の読取不変・unknown／partialの回帰が維持されます | RQ-415-004 |
| AC-415-005 | AGENTSの現在入口を読み、PR414のmerge証拠と日時付き履歴を照合します | 0805限定適用・merge pendingが現在状態として読まれません。未認定の他環境を移行済みにしません。Issue413 pack・実装記録・調査Artifactの原文bytesが保持されます | RQ-415-005 |
| AC-415-006 | Bash／Zsh／Fishについてcatalog全leafの生成候補と、代表的なnative補完・parserの正負例を検査します | read leafに`--yes`／`-y`なし、Start以外に`--lock-timeout`なし、受理leafの正候補あり。44 leaf、位置自由度、値・operand処理、context-free性、無書込みを維持します | RQ-415-006 |
| AC-415-007 | 後続の許可済みAbout操作で必要ならdescriptionだけを設定し、独立したlive GETを行います | 正確なrepositoryと採用descriptionが一致し、homepage／topics等を本操作で変更していません。変更前・送信または変更なし・read-backを記録します。未実施・確認不能は未達のままです | RQ-415-007 |
| AC-415-008 | 変更provider資産のinventory照合、fresh wheel／外部非editable環境／fresh consumer／既知旧更新／unknown対照を検証します | current bytes/hash一致、正当な旧hash保持、consumerに新説明を配置、公開CLIの変更挙動一致、unknown拒否・保全成功、runtime二重配布なしを確認します。対象worktree適用は別の許可・証拠で確認します | RQ-415-008 |
| AC-415-009 | 現在候補の通常lint・全pytest・差分・対象回帰・実運用証拠をレビューします | 各結果が対象SHA／環境／実exitに対応し、未実施を合格扱いにしません。非対象の変更、履歴改変、policy skip／ledger再導入がありません。About保留等が残ればIssue全体を完了扱いにしません | RQ-415-009 |

## 制約・前提

対応OSはLinux/macOS、Pythonは3.10以上です。公開CLIと静的文書の責務を維持します。試験は一時fixtureとstubで行い、利用者の実Issueを作成・Closeしてテストしません。仕様作成時点では実装・実適用・外部変更の許可を追加取得したものではありません。

### 未決事項の分類

| 区分 | 未決事項 | 本Issueへの影響 |
|---|---|---|
| 実施前に確定する運用入力 | 実装候補SHA／wheel hash、更新する外部tool環境、対象worktreeの絶対root、新しい外部backup先、実施許可、実shell／OS検証環境 | 該当stepの実施条件です。推測で補わず、未確定ならそのstepを保留します |
| About実施判断 | 設計のdescription候補の採否、操作主体・正規手段・必要権限、実施時点 | SD-OPS-007に必要です。ZIP採用だけでは書込み許可・成功にはなりません |
| 将来の別Issue | `./spec`・薄いshimの廃止、global共通skill＋local project情報、同名衝突規則、dead code整理 | 七件の修正に不可欠ではありません。本Issueの開始・終了条件へ追加せず、採用済み決定にも変換しません |
| 別の運用責務 | 他worktree移行、正式Issue413 Start、human merge、package公開 | 本Issueの実装stepとして実行しません。状態を捏造せず、必要時は別の明示依頼へ返します |

七件の必須範囲に関する一般的な再設計判断は不要です。新しい不可逆変更、データ損失、秘密情報の露出、または必須範囲外の移行が必要と判明した場合は、該当作業を停止し、RequirementとPlanning Levelを再評価します。
