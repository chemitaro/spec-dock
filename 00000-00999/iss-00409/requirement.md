---
種別: 要件定義書（Issue）
ID: "iss-00409"
タイトル: "SpecDock CLI Scope Active Work Redesign"
関連GitHub: ["#409"]
状態: "draft"
原稿状態: "Issue #409 正本へ採用・実装前"
最終更新: "2026-09-24"
親: ["epic-00356", "init-local-00003"]
基準Repository: "chemitaro/spec-dock"
実装調査基準Branch: "codex/scope-start-finish-analysis"
実装調査基準Commit: "eeb3e5965f0cb42de9a24081bfaea15e27fd4451"
---

# SpecDock CLI 案Bの全面採用と安全な一括切替 — 要件定義

本書は Issue #409 の実装前の正本です。CLI案Bと本依頼に列挙された製品方針は利用者が採用済みです。Issue #409 は Epic #356／Initiative init-local-00003 の下に作成され、`issue start` によりactiveに設定されています。

本書は成果・振る舞い・受入条件の正本です。構造と契約の詳細は[設計書](design.md)、実装順と検証は[実装計画書](plan.md)に分離します。[説明HTML](artifacts/cli-redesign-guide.html)は人間向けの説明資料であり、新たな仕様の決定権を持ちません。

Authoring根拠: `spec-dock/docs/authoring/requirement.md`、`scope-layering.md`、`artifacts.md` と `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`。取得したZIPの三文書を Issue #409 の正本へ明示的に取り込み、HTMLを同IssueのArtifactとして配置しました。

## 目的

Initiative・Epic・Issueのどの階層でも、利用者と自動実行agentが「何を対象に、どの状態を、どの外部副作用を伴って変更するか」を実行前に理解できるCLIに統一します。作業開始と終了を三階層で対称にし、選択・完了・Git作業場所・ローカル削除を独立して扱えるようにします。

未公開の個人用ツールとして、同一の実装作業と一回の調整された切替で新体系へ移行します。公開版の複数リリースや長期互換期間は設けません。ただし、速度を優先して既存データ、他worktree、導入済みconsumerの安全性を犠牲にしません。

関係者の成果は次の三点です。利用者は結果と残る状態を予測できます。実装agentは共通selector・JSON・終了コードを使って対象を取り違えずに実行できます。新規参加者は会話履歴なしで仕様と移行を理解できます。

## 背景

基準コミットには、repo-local runtimeの15コマンド系統・28実行leafと、別のinstaller入口があります。現行実装では、作業lifecycleはIssueのみ、finishは全active解除、deleteはGitHub close後にローカル削除、通常syncはbranchからactiveを推定、worktree createはbootstrapを実行し得ます。これは現行コードの事実です。根拠と対象fileはDesignの「Current / Target」にまとめています。

本書が定める新体系は採用済みの将来仕様であり、実装調査基準コミットで実装済みという意味ではありません。Issue #409 の作成・開始と本書の採用は完了しています。新CLIのアプリケーションコードと導入済みconsumerはまだ変更していません。

## 観測可能な要件

### R-01 操作体系と対象の明示

`scope`はInitiative・Epic・Issueそのもの、`active`は選択、`work`は複合開始・終了、`branch`は対応Git branchを扱います。`dependency`、`artifact`、`worktree`、`workbench`、`workspace`、`installation`を同じ文法原則で提供します。`help`と`completion`も含めます。`active set`を維持し、`active select`へ改名しません。

指定対象には完全なScope IDまたは完全修飾GitHub参照を使います。現在選択中の対象には `@current`、祖先または該当階層には `@initiative` / `@epic` / `@issue` を明示します。引数の省略、裸の番号、文章中のID、曖昧なworktree名から対象を勝手に選びません。親とArtifact配置先も明示します。

### R-02 Scopeの作成・取込・表示・変更

三階層の新規作成では `github` または `local` backendを明示します。GitHub失敗をlocal作成に置き換えません。EpicとIssueは正しいkindの親を必須にします。GitHubからの取込は既存Issueの読取り確認であり、新規Issue作成・remote編集・本文の仕様化を行いません。titleを明示必須とし、foreign repositoryの取込は拒否します。

Scopeの一覧・指定表示・title編集を提供します。title編集でID、slug、path、canonical branch、GitHub側titleを自動改名しません。

### R-03 選択と三階層の作業開始

選択は一つのworktree内の文脈です。対象とその祖先を選択し、対象より下位の選択を解除します。`active set`はGitHub照会・依存判定・checkout・完了を行いません。

`work start`は三階層で共通に、対象の開始条件を確認し、名前付きcanonical branchを作成またはcheckoutした後、対象をactiveにします。新規branchには明示baseを要求します。一つのScopeには一つのcanonical branchだけを認めます。既存branchをreset・奪取・暗黙改名しません。dirty状態や他worktreeでの使用を無視しません。

親Scopeの計画を開始するために、子の作業完了を要求しません。開始に必要な前提依存と、子孫の実行順序・進捗は別に表示します。

### R-04 正常終了・Close・Reopen・Delete

`work finish`は対象をcompletedにします。対象がactiveチェーンにあるときだけ、その対象以下を解除し、祖先を残します。無関係な選択を消しません。未完了・取り止め・状態不明の子孫が残る親を正常完了にしません。空の親は、他の前提を満たせば完了可能です。子の完了集計だけで親自身を完了済みにしません。

Closeは対象の終端状態だけを変更し、activeを変更しません。`scope close TARGET`で`--reason`を省略すると`completed`と等価です。取り止めの`not-planned`は`--reason not-planned`を明示した場合だけ選択します。Reopenは対象だけをopenへ戻します。正常完了と取り止めを区別し、取り止めを依存の完了条件とみなしません。

Deleteはローカルの対象と、その操作で明示された所有物の削除です。GitHub Issueを閉じず、Git branchを削除しません。子孫、active、境界を跨ぐ依存の扱いは個別の明示許可を要求します。

### R-05 支援機能の副作用分離

Dependencyの追加・除去からGitHub全体の再取得を起動しません。Artifactは証跡のまま保持し、作成typeやfile名を採用の根拠とみなしません。保存済みArtifactのopen-world互換性と、任意拡張子のopaque file importを維持します。

Worktreeの寿命とScopeの寿命を分けます。createはbootstrapを行わず、bootstrapは別の明示操作です。removeはbranchを残し、利用中・dirty・未追跡・ignoredな利用者payloadを保護します。Workbench copyは明示scopeの一回限りのコピーであり、同期でも正本への採用でもありません。

Syncは生成状態の再構築です。active推定を行わず、既定はcache利用です。GitHub読取りはsourceで明示します。ValidateとDoctorは診断のみです。

### R-06 安定した入出力と回復

全leafに共通のhelp構造、JSON envelope、終了コード、非対話規則、変更操作のdry-runを提供します。JSONモードは確認への同意を意味しません。`--yes`は対象・整合性・セキュリティガードを迂回しません。非対話でcurrent系selectorを使う変更には期待する中心対象の明示が必要です。

部分成功と成否不明を、変更前の失敗から区別します。remote操作済みなのに未実施と報告せず、解決済みの明示IDを使って回復を案内します。終了直後に `@current` が祖先へ移ることを考慮し、同じ動的selectorで再試行させません。

未完了journalによる全変更の停止は、固定対象を使う明示的な復旧手順を持つ操作に限定します。その他の変更操作はatomic/CAS/identity検証と操作別の部分失敗診断で扱い、成否が不明な作成・外部効果を自動で再実行して二重適用しません。`workbench copy`と`worktree bootstrap`の任意・部分的な効果は自動rollbackや盲目的な再実行をせず、実施済み範囲を確認してから明示的に再実行します。これらの操作だけを理由に、無関係な変更を復旧不能なjournalで全体停止しません。

### R-07 一括切替とデータ保全

変更された旧コマンドを新しい副作用へ黙ってaliasしません。副作用を維持できる入口以外は無変更で停止し、新しい入力方法を提示します。全旧28leafの対応を文書と回帰テストで追跡します。

providerの配布元、同repository内のdogfooding workspace、別repositoryの導入済みconsumer、各Git common directoryの全worktreeを区別して棚卸しします。旧writer停止・バックアップ・復元確認・固定bundle配布・schema移行・全作業場確認・再開を一回の切替作業として行います。未確認のwriterを残したまま新データの書込みを開始しません。

Updateは固定供給元から明示versionまたはcommitを解決し、journalと回復経路を持ちます。Uninstallはツールだけを削除します。移行も更新も既存仕様・Artifact・Workbenchの内容を勝手に正規化・削除しません。

## スコープ

### 対象範囲

対象は案Bの全42業務leafとhelp・completion、共通selector・入出力・安全境界、三階層lifecycle、local backend、対応branch管理、依存、Artifact、Worktree、Workbench、生成状態、診断、導入・更新・削除、既存データの移行です。詳細なコマンド文法はDesignに一元化します。

長寿命worktreeと現在のfile-based仕様構造を維持します。正本三文書のauthoring上の責務と、Artifactが自動的にauthorityにならない契約を維持します。

### 対象外

アプリケーションコードの実装・実行は今回の文書作成には含みません。採用案の再比較、`active select`への改名、公開版の長期deprecation、複数リリースへの先送りは行いません。

実装対象にも、PR作成・merge・push・自動commit、Scopeのkind変更・階層move、複数canonical branch、複数GitHub repositoryへの透過routing、localとGitHubの双方向status同期、local ScopeのGitHubへの自動昇格、root Workbench一括copy、Artifact本文の自動採用、履歴Git commitの書換え、権限を持つ利用者による旧Python直接実行の完全防止は含みません。

## 失敗・境界条件

対象なし・曖昧・誤kind・誤親・誤repository、activeなし、並行変更、未充足依存、閉じたScope、欠損schema、参照切れ、branch衝突、dirty checkout、他worktree使用、再実行、remote timeout、disk full、permission error、process停止、symlink/hardlink/path差替えを扱います。

親完了の保証は、その操作が観測した仕様snapshotとremote応答に対するものです。外部のGitHub利用者が直後に子をreopenすることをローカルツールが禁止できるとは主張しません。再観測時に不整合を表示し、黙って修正しません。

データ移行前後では旧writerとの混在を許可しません。古いruntimeは新しいmarkerを知らないため、marker設置だけでは安全になりません。停止・起動経路の切替・履歴branchの扱いを含めて受け入れを判断します。

## 受け入れ条件

以下は観測結果に対する条件です。どのmoduleで実現するかはDesign、どの順番でテストを実装するかはPlanに置きます。AC番号は本原稿内の識別子であり、実在するIssue IDではありません。

| ID | 条件・観測可能な期待結果 |
|---|---|
| AC-01 | 10業務namespace・42業務leaf・help/completionの全44leafがDesignの一覧と一致します。`active set`は存在し、`active select`は成功しません。旧28leafが漏れなく分類されます。 |
| AC-02 | 各leafのhelpからTarget、Reads、Writes、Does not、Preconditions、Confirmation、Recovery、JSON、Examplesが確認できます。helpとcompletionはprojectなしでも動き、補完が新しい副作用を起動しません。 |
| AC-03 | 完全ID、完全修飾GitHub ref、current系selectorが同じ対象resolver規則に従います。裸番号・文章抽出・target省略・誤kind・foreign ref・曖昧なworktreeを拒否し、変更がありません。 |
| AC-04 | 各kind×github/localで作成でき、backend省略は拒否されます。local作成はGitHubを呼びません。Epic/Issueの親省略または誤kindを拒否します。createは選択・branchを変更しません。 |
| AC-05 | 三階層のGitHub importは明示title・正しい親・同repositoryが必要です。remote書込みゼロです。既存リンクの重複・foreign・PRをIssueとして扱う入力を拒否します。 |
| AC-06 | list/showは無変更であり、指定対象とcurrent対象を区別できます。editはtitleのみを変え、ID・slug・path・branch・GitHub側title・本文のbytesは変えません。 |
| AC-07 | I/E/Qの選択が正しい祖先チェーンになります。setにGitHub照会・checkout・依存判定がありません。clear --fromは対象以下だけ、--allは全解除、無関係な対象は選択を壊しません。 |
| AC-08 | 三階層すべてでstartが対象確認→対応branch確保/checkout→active設定を満たします。親の子孫が未完了でも、その親自身の前提が満たされれば開始できます。closed対象は暗黙reopenしません。 |
| AC-09 | 新branchのbase省略・既存branchへのbase指定・canonical対応の二重登録・他Scopeとのbranch共有・dirty/他worktree衝突を拒否します。branch createはcheckout/active変更なし、branch switchはactive変更なしです。 |
| AC-10 | Issue finishはIssueのみ完了しEpic/Initiative選択を残します。Epic finishはEpic以下を解除しInitiativeを残します。Initiative finishは全解除します。無関係な選択は残り、Git branch/HEADは変わりません。 |
| AC-11 | open、not-planned、unknownの子孫を持つ親finishとcompleted closeを拒否し、子孫を自動closeしません。既にcompletedの親への同じ理由のcloseも現在の子孫状態を再評価してからno-opにします。空の親は完了できます。親自身がopenなら子全完了だけでは親doneと表示しません。 |
| AC-12 | `scope close TARGET`の理由省略はcompleted、not-plannedは明示指定のみです。close/reopenは対象backendの状態だけを変え、activeとGitを変更しません。local完了は保存されます。not-plannedはcompletedとは別で、依存を充足しません。異なる終端理由を黙って上書きしません。 |
| AC-13 | 新deleteでGitHub読書き・branch削除がありません。親のrecursive、選択解除、境界依存の除去が個別に許可されます。未承認時は無変更です。削除失敗時に残存/削除済み/回復先が判別できます。 |
| AC-14 | 全kind間の依存を宣言・表示・検査・除去できます。自己依存/循環を拒否し、重複addはno-op、不存在removeは--missing-okがない限り失敗します。暗黙のGitHub post-syncはありません。 |
| AC-15 | 六種の文書生成、三階層/rootへのgeneric file import、list/showが動作します。source bytesは保存され、sourceを変更しません。保存済みunknown typeの有効Artifactを拒否せず、自動採用しません。機密出力契約を守ります。 |
| AC-16 | worktree createは明示baseから作成し、make/consumer hookを一度も実行しません。list/showは無変更です。Scope finishからworktree作成/削除が起きません。 |
| AC-17 | worktree removeはbranchを残します。main/current/bare/dirty/untracked、未承認locked/ignored payloadを保護します。旧forceで保護を迂回できません。 |
| AC-18 | bootstrapは独立した明示操作です。hook失敗/中断は成功扱いになりません。JSON stdoutにmake出力が混入しません。任意のproject処理が副作用を持ち得ることが実行前に表示されます。 |
| AC-19 | Workbench copyは同repositoryの同Scopeのみです。既定の衝突は変更前に拒否し、overwrite明示時はsource-winsで宛先固有fileを残します。root一括copy・自動sync・正本採用は行いません。 |
| AC-20 | sync既定はcacheで、全sourceでactive/branch/一次仕様を変更しません。GitHub取得失敗をfreshなcacheと偽りません。生成物にsource・stale・validity・生成revisionが出ます。 |
| AC-21 | validate/doctorは診断のみです。空workspaceは既定で有効、--require-nodesで拒否されます。doctorは未完了journalとwriter不整合を診断し、capability probeは完全指定時だけです。 |
| AC-22 | 全44leafでJSON指定時のstdoutが一つのversioned JSON文書です。構文エラー・部分失敗も同じ外枠です。非対話は入力待ちにならず、--jsonは--yesを含意しません。終了コードがDesignと一致します。 |
| AC-23 | init/update/showで固定distributionと適用対象が表示されます。updateはimmutable commitに固定し、供給元変更・壊れたbundle・path差替えを拒否します。journalの各停止点からresume/rollback可能範囲を判別できます。maintenanceからreadyへの復帰は全登録worktreeのIDを列挙した記録を先に残し、途中停止後は同じoperation IDで再開できます。 |
| AC-24 | uninstallはdry-runまたは明示確認の適用です。GitHub/供給元への通信なしでツールのみ除去し、仕様・Artifact・Workbench・回復用backupを保持します。--remove-specsは無変更で拒否します。 |
| AC-25 | 移行前の全対象がinventoryに載り、全writer停止・backup/restore検証後に一回のcoordinated cutoverを実施できます。全worktreeのwriter protocol/必要schemaが揃うまで通常変更を再開できません。 |
| AC-26 | 三文書・Artifact・Workbench・Git ref・index・未追跡/ignored payloadの保全を検証できます。移行対象外のbytesは同一で、変更するmetadataは差分一覧に限られます。移行だけでGitHub状態は変わりません。 |
| AC-27 | 全旧28leafについて、効果維持または無変更の説明付き拒否が確認できます。旧delete/finish/sync/uninstall/createの意味を黙って新効果へ置き換えません。全実行入口・skills・automationの呼出しが更新されます。 |
| AC-28 | 並行writer、current変更競合、checkout後active失敗、remote close後解除失敗、成否不明timeoutで対象と実施済みeffectが保持されます。明示resumeを備えた操作の未完了blocking journalだけが全変更を止め、固定IDと元operationで回復します。その他の部分失敗は同対象の衝突と二重適用を防ぎ、無関係な変更を全体停止しません。 |
| AC-29 | symlink/hardlink、path traversal、異なるinodeへの差替え、credential付きURL、供給元偽装を無変更または明示partialとして扱います。secret、source本文/hash/byte count、リポジトリ外Artifact source絶対pathを出力しません。 |
| AC-30 | provider sourceを先に完成させ、dogfoodingと全consumerを同じfixed bundleへ切り替えられます。consumer固有データをproviderの内容で上書きせず、履歴branchから旧writerが戻る経路を棚卸し・停止できます。 |
| AC-31 | 人間向けHTMLが単独file・offline・スマートフォンで読めます。旧新対照、用語、状態/副作用、正常/失敗、移行手順があり、外部script/image/CDNに依存しません。 |
| AC-32 | 実装・切替完了時に受入条件と検証結果、固定bundle、全対象inventory、backup、未解決journal、残余リスクを引き渡せます。未実行テストを実施済みと扱わず、未確認consumerを完了扱いしません。 |

## 制約・前提

基準SHAはGitHub connectorの指定branch ref取得により今回一致確認済みです。それ以外のbranchは本作業では確認していません。資料に記載するfile pathは基準実装のsource path、または明示的な新設計pathです。実端末のconsumer一覧、worktree一覧、backup先、採用bundleの将来SHAは実施時に採録する値であり、本書では捏造しません。

案Bの採否、local backend、祖先保持、親完了ガード、base必須、固定供給元、一括切替の方針は未決ではありません。実装時に必要なのは切替対象inventory、停止承認、backup保存先、配布candidateの指定です。これらの運用値が欠けても文書の方針を再設計しませんが、実データへの切替は開始しません。

同一Git common directory内のwrite互換性と、独立clone間の業務状態の同期は別です。本作業は前者を保証対象にし、後者を自動実装しません。外部Git操作や利用者自身による旧コード直接実行を完全に封鎖するものではありません。停止・信頼する起動経路・操作時の検証を安全条件として明示します。
