# Issue #413 要件定義書

**現在の実装正本と証拠（2026-10-03）**: repository `chemitaro/spec-dock`、branch `codex/iss-00413-external-cli-state` のtip `8606e132327066d56567556e336e4bc1ae6a0b17` をGitHub connectorで完全一致確認しました。製品コードと合意済み仕様の現在正本はこのSHAです。同SHAには既存のFinal Quality Gate v2証拠があり、coverage complete、13 perspective、P0/P1=0、情報提供P2=3です。native macOSは1916 passed / 1 skipped、Linuxは1900 passed / 17 skipped、Python 3.10境界は210 passedです。レビュアー自身がこれらを実行した証拠ではなく、手動14操作も実Gitとstateful gh stubによるものでlive GitHub Close認定ではありません。

**現在のrollout状態**: caller-provided local observationでは、0805 worktreeに外部0.2.4 package、薄いshim、writer宣言と静的資産が適用済みで、240 Scopeのvalidateとempty activeを確認しています。mainとほか3 linked worktreeは未移行で、clone全体のsyncはpartial（exit 7）です。正式なIssue #413 import/Start、人間merge、package publicationは未完了です。GitHub #31はclosed/completed、#356と#413はopenという観測であり、本書は#31のreopenや付替えを指示しません。

**履歴の読み方**: 以下に残る `121228c6`、`3b803ced`、P-18実装前、旧レビュー・旧試験・Windows検討の記述は、その作成時点のraw historyです。現在の完了/保留表示は上記と末尾のcurrent dispositionを優先し、履歴値を消去・改ざんしません。今回の文書差し替えは新しい製品実装、追加review、Final Quality Gate再実施ではなく、将来の文書commitに既存Gate認定を転記しません。

<a id="background"></a>
## 背景・目的

SpecDockはInitiative、Epic、Issueの三階層で仕様・依存・成果物を扱うPython CLIです。`src/spec_dock/` はproviderの開発source、worktree外に通常導入したpackageが実行runtime、`src/spec_dock/assets/` から各consumer worktreeへ置く文書・template・skill・shimは静的資産、`spec-dock/.agent/work-target/` はignoredな直接作業記録です。現在のshimはPATH上の外部consoleへ委譲し、Git common-dirの独自locator/controlやcheckout内Pythonを起動前提にしません。旧shimがlocator/controlを先に要求してhelpへ到達できなかった構造は[基準source S-02/S-03](artifacts/source-basis.md#implementation)に残る歴史的baselineであり、現在実装の説明ではありません。

目的は、通常の外部インストールCLIを使い、Git管理領域の独自運用基盤なしで、複数worktreeの作業対象を混同せず進められることです。全状態を捨てることではありません。worktreeごとの直接対象だけは残します。Startはbranch準備を行い、FinishはGitHubを完了します。通常のファイル編集をCLIの権限管理下に置きません。

## 対象・非対象

対象は起動/配布、直接対象、Start/Finish/active/Sync、その変更に不可避なCLI/context/storage/資産/移行/通常testです。既存Scope、依存、Artifact、Workbenchの業務契約は必要な変更以外維持します。対応OSはLinuxおよびmacOSです。

非対象はWindows対応、daemon、別clone/PC探索、全worktree登録台帳、canonical branch binding台帳、独自Scope採番、永続operation journal、自動resume/rollback、初期cache、Release追加、品質ゲート組織、通常編集の包括的排他です。Windowsを止める代替として別のlock/store/台帳/daemonを追加しません。GitHubへのexactly-once、非協調editor/Git/旧writerの完全封鎖、複数ホスト共有filesystemでの排他は約束しません。今回の文書生成は製品変更・投稿・公開ではありません。

## 用語

| 用語 | 定義 |
|---|---|
| clone | 同じGit common-dirの物理実体を共有する作業場群。同remote URLだけでは同一としない |
| main worktree | Gitの最初の作業場。main branchとは別概念で、制御拠点ではない |
| 直接対象 | そのworktreeで明示選択されたScope一件。親・祖先は表示用文脈で別の直接選択ではない |
| 選択中 | 直接記録が存在すること。Open/ClosedやCodex稼働を意味しない |
| 完了 | backend authorityがcompleted。GitHubではclosedかつstate_reason=completed |
| stale | 記録は残るが現在のcheckoutで対象/祖先等を整合して解決できないこと。空選択とは違う |
| 排他 | 同じcloneの協調Startが重複判定と記録を同時実行しないための短いOS操作 |
| partial / unknown | 効果の一部が成立、または成否を確定できない状態。未実行と混同しない |
| 設計判断 | 確定要求を実現するために本書群で採用した技術上の選択。利用者回答の引用とは区別する |
| 対応OS | 製品業務コマンドの受け入れ対象。LinuxおよびmacOS。help/version/completionのcontext-free性とは別概念 |
| 非対応OS | 製品業務コマンドの動作を保証しないOS。Windowsを含む。代替管理基盤を意味しない |

<a id="priority"></a>
## 要件の優先順位とauthority

最優先はデータ/成果物保全、確定回答、効果の正直な報告です。次に今回の目的である外部CLI、最小直接状態、Startだけの重複防止を満たします。既存の便利機能はこの範囲で維持し、台帳を必要とする旧保証と衝突した場合は変更を明記します。速度の最適化や高度な並行機構より、この小さな保証を優先します。

OS範囲については2026-10-02 JSTの[対応OS決定](artifacts/os-support-decision.md)を最上位authorityとします。そこではWindows対応を撤回し、対応OSをLinuxおよびmacOSへ確定しています。[確定回答](artifacts/user-decisions.md)のQ1〜Q8と合意事項は、それと衝突しない範囲で引き続きauthorityです。実装の事実は、GitHub connectorでrepository・branch・full SHAを一致確認した[検証済みSHA](artifacts/source-basis.md)と、[撤去分析](artifacts/os-support-retirement-analysis.md)によります。旧#409設計、旧#413草案、Windows用Implementation Brief、Windows調査、既存P-01〜P-17の測定ログは経緯・raw evidenceであり、現在のWindows完成義務を復活させるauthorityではありません。以下はすべて必須（MUST）。RQ/ACの既存識別子とリンクを維持します。

<a id="os-support"></a>
## 対応OS・必要原語・非対応OS

製品業務コマンドの対応OSは **LinuxおよびmacOS** です。対象filesystemは、既存directory descriptor、`fstat(st_dev, st_ino)`、nofollowでのdirectory/file open、single-link regular file検査、file/directory `fsync`、未存在名への無上書きrename、既存directory descriptorへの `fcntl.flock` を実用上提供するlocal filesystemです。LinuxとmacOSで同じ抽象名を掲げるだけでなく、各OS/FSで実process・実Git・実consoleの証拠を別に残します。network filesystem、複数host共有mount、異なるOSからの同時mountは保証しません。

Windowsは非対応です。`WindowsDirectory`、`WindowsMutex`、Win32 identity/JSON reader、WAIT_ABANDONED/NTFS lane、Windows work-target storeを完成させる要求は失効します。撤去時にWindowsの代替lock file、PID file、mkdir lock、ACL変更、registry、cache、daemon、別storeを追加しません。

root/leaf help、version、completionは対応OS判定より先に処理し、Git・project・control・認証・通信・filesystem adapterへ到達しません。業務コマンドはutility dispatch後に小さな対応OSguardを一度通し、非対応OSではproject解決、Git/GitHub呼出し、stage作成、branch変更、consumer書込より前に `UNSUPPORTED_PLATFORM`、effects=[]で停止します。Windows全機能のtest/portは要求せず、この副作用前拒否とutility独立だけを境界試験にします。

`specdock.work-target/v1` はversionを増やさず、`clone_identity` と `worktree_identity` を `{platform:"posix", device:<10進文字列>, file_id:<10進文字列>}` に限定します。Scope schema3、既存Scope ID、親子・依存・GitHub linkage、workspace writer protocolは変更しません。Windows形は公開/解除writerが未接続で、実Windows/NTFS合格証拠もないため、未導入形の互換性を新versionやunionで温存しません。ただし、provider fixture、許可対象consumer、保全物のいずれかに実在する `platform:"windows"` のwork-target v1 recordが見つかった場合、P-18を停止し、削除・変換せず別の明示決定へ戻します。

<a id="requirements"></a>
## RQと測定可能なAC

<a id="rq-413-01"></a>
### RQ-413-01 外部CLIと独立したhelp

導入済みの通常consoleから実行し、help/version/completionをGit・control・project・認証・通信に依存させない。

根拠: 利用者の目的・合意8。設計: [D-02](design.md#d-02)。

<a id="ac-413-01"></a>
**AC-413-01** — Git/ghがPATHにない、project指定先が壊れている条件でrootと44 leafのhelp、version、3 shellのcompletionを実consoleで実行し、exit 0、Git/gh呼出し0、consumer書込0を確認する。対応OSguardを含むbusiness/context import・IOへ到達しない。

<a id="ac-413-02"></a>
**AC-413-02** — Linux/macOSでfresh wheelをcheckout外へ非editable installし、provider sourceを参照不能にしても実consoleのScope読取・Start・Finish・Syncが動く。fixed bundle、consumer runtimeの追加コピー、control作成はいずれも0。


<a id="rq-413-02"></a>
### RQ-413-02 保存責任を限定する

通常運用の永続状態を、仕様・成果物・workspace宣言とworktree自身の直接対象一件に限定する。

根拠: 合意3・8・9。設計: [D-03](design.md#d-03)。

<a id="ac-413-03"></a>
**AC-413-03** — help/read/Start/Finish/Syncを含む全公開経路の許可write先を監視し、独自.gitファイル・Git config/refへの独自情報・registry・journal・cache・全worktree名簿の作成更新0を確認する。Git自身のrefs/index等の効果は別に記録する。

<a id="ac-413-04"></a>
**AC-413-04** — 直接対象は自分のspec-dock/.agent/work-target/に0または1件だけ。work-target v1の二identityはplatform=posixと10進device/file_idだけを受理する。選択・解除の前後でtracked metadataと本文のhashが一致し、git statusに記録由来の差分が出ない。保存先がtrackedまたはignoreされていない場合は記録前に拒否する。


<a id="rq-413-03"></a>
### RQ-413-03 同じcloneだけを観測する

Gitが返すmainとlinked worktreeを必要時に観測し、直接対象を各worktreeから読む。別clone・別PCは探索しない。

根拠: Q1・合意3/4。設計: [D-04](design.md#d-04)。

<a id="ac-413-05"></a>
**AC-413-05** — 通常Gitで追加したlinked worktreeを事前登録なしで列挙し、同じremoteの別cloneは列挙しない。main worktree停止や選択なしを制御不備としない。

<a id="ac-413-06"></a>
**AC-413-06** — 空白・改行を含むpath、detached、locked、prunableのGit porcelain -zを扱う。読み取れない行を消さず、Syncはcomplete=falseと不明箇所を返す。Startの重複確認が完全でなければ副作用前に止まる。


<a id="rq-413-04"></a>
### RQ-413-04 直接対象一件と重複禁止

一worktreeに直接対象は同時に一つ。同一直接Scopeの並行開始を防ぎ、同じ親の異なる子は許す。

根拠: Q3・合意5。設計: [D-05](design.md#d-05)。

<a id="ac-413-07"></a>
**AC-413-07** — 同一cloneの別process・別worktreeから同じ直接Scopeを同時Startすると、成立した新規選択は一件だけ。敗者はGit変更・開始記録0。完全ID一致または同一GitHub linkage一致のいずれも衝突とする。

<a id="ac-413-08"></a>
**AC-413-08** — 同じEpic配下のIssue A/Bは並行Startできる。Epic自体の直接選択と子Issueの直接選択は別対象として扱う。親の件数は子の直接対象を集計し、親を暗黙に選択しない。


<a id="rq-413-05"></a>
### RQ-413-05 Startの業務効果を維持する

Startはreadiness確認、必要なbranch作成、checkout、直接対象記録までを行う。記録だけへ縮小しない。

根拠: Q2。設計: [D-06](design.md#d-06)。

<a id="ac-413-09"></a>
**AC-413-09** — 三階層それぞれで新branchの--base必須、任意名指定、既存branchへの明示切替を実Gitで検査する。reset・自動commit・stash・push・branch削除は0。切替先の対象/祖先/schema/linkage不一致と他worktree使用を拒否する。

<a id="ac-413-10"></a>
**AC-413-10** — A選択中の別直接対象Bは--switch-activeなしで拒否する。明示切替はAをCloseしない。AのFinish後は現在branchに留まり、BのStartを切替許可flagなしで受理する。


<a id="rq-413-06"></a>
### RQ-413-06 開始時だけの排他

重複確認からGit効果と開始記録までの必要区間だけを、一つのclone共通OS排他で囲む。

根拠: 合意1/2。設計: [D-05](design.md#d-05)。

<a id="ac-413-11"></a>
**AC-413-11** — Linux/macOSの二process barrier試験で重複走査→branch作成→checkout→記録公開の区間が重ならず、記録公開前にロックを解放する実装を検出する。prompt・GitHub待ちは区間外である。

<a id="ac-413-12"></a>
**AC-413-12** — Linux/macOSでStartがロックを保持していても通常ファイル編集、metadata操作、Sync、Finishはこの共通ロックを取得しない。timeout・取消・process強制終了でdescriptor/flockが解放され、新しいlockファイルや監視processは残らない。


<a id="rq-413-07"></a>
### RQ-413-07 既存activeを最小整合させる

show/clearと動的selectorを維持する。新しい直接対象の獲得はStartだけに集約し、lockを迂回するactive setを設けない。

根拠: 利用者制約6の具体化（設計判断）。設計: [D-07](design.md#d-07)。

<a id="ac-413-13"></a>
**AC-413-13** — active showの空選択は成功。active setは同一の妥当な直接対象へのno-opだけを許し、新規/別対象はWORK_START_REQUIRED、効果0とする。--from-branchは廃止診断で推測しない。

<a id="ac-413-14"></a>
**AC-413-14** — active clear --allおよび--fromが直接対象/祖先に一致する場合は直接記録全体を解除し、親を昇格させない。既知のチェーン外対象はunchanged。不明IDはnot-found。clearはGitHub/branchを変更しない。

<a id="ac-413-15"></a>
**AC-413-15** — Finish Aまたはclear AがAの記録を読み取った後にStart B（またはAの新しい記録）が成立しても、古い解除は新しい記録を削除しない。二つの解除は同じ一件だけに作用する。


<a id="rq-413-08"></a>
### RQ-413-08 Finishは完了とClose

Finishは対象をcompletedにしてGitHub IssueをCloseし、該当する自worktreeの選択だけを解除する。branchに留まる。Releaseを増やさない。

根拠: Q4・Q6・Q7。設計: [D-08](design.md#d-08)。

<a id="ac-413-16"></a>
**AC-413-16** — 三階層のGitHub-backed Finishがstate=closed/state_reason=completedを要求し、確認後に該当選択を解除する。branch/HEADは不変。--yes不足、子孫open/not-planned/unknown、対象not-plannedで変更0。

<a id="ac-413-17"></a>
**AC-413-17** — 既にcompletedなら子孫条件を再検査し、PATCHなしで該当選択だけ解除できる。明示対象が現在チェーン外なら別選択を変えない。work releaseは公開catalogに存在しない。


<a id="rq-413-09"></a>
### RQ-413-09 Start失敗とGit原文

自動巻戻しをせず、成功済み効果と不明を明示する。Git原文と子processの終了値を隠さない。

根拠: Q8。設計: [D-06](design.md#d-06)。

<a id="ac-413-18"></a>
**AC-413-18** — branch作成後のcheckout失敗、checkout後の記録公開失敗を注入する。成功したGit効果が残り、status=partial/exit 6、開始成功false、未公開対象を選択済みとしない。

<a id="ac-413-19"></a>
**AC-413-19** — checkoutの既知複数行stderrをtext stderrまたはJSON error.details.git.stderrへ改変せず保持し、ネイティブreturncodeとCLI exitを区別する。秘密だけの部分秘匿はredacted=trueで明示する。一般文言への置換を失敗とする。

<a id="ac-413-20"></a>
**AC-413-20** — StartのGit前/branch後/checkout後/記録公開直後でprocessを停止する。次processは現存Git/直接記録だけを読む。出力不能な強制終了をJSON契約成功にせず、resume/rollback/旧intent生成0。


<a id="rq-413-10"></a>
### RQ-413-10 GitHub不明結果を保守的に扱う

送信後不明を未送信と断定せず、自動再送・自動解除をしない。

根拠: Q8・合意9。設計: [D-09](design.md#d-09)。

<a id="ac-413-21"></a>
**AC-413-21** — fake ghがClose要求後に応答を失うとPATCHは一回、再GETでも確定不能ならexit 6、effect unknown、選択保持。次の明示Finishは現在状態を確認し、completedなら再PATCHしない。

<a id="ac-413-22"></a>
**AC-413-22** — createの応答不明で正式IDを生成しない。remote成功/local公開失敗は確定refを示し、同Issueの明示importへ誘導する。以前の出力を失ったfresh processが過去送信意図を返すことはない。


<a id="rq-413-11"></a>
### RQ-413-11 選択・状態・プロセスを分ける

Syncは複数選択と親の配下件数を表示するが、選択から完了やCodex稼働を推定しない。

根拠: 合意4/5/6。設計: [D-10](design.md#d-10)。

<a id="ac-413-23"></a>
**AC-413-23** — 選択中かつGitHub closed、未選択かつopen、selectedかつprocess不明を別fieldで表す。PID探索0。--source localではGH状態unknown、--source githubだけ今回のGETを使い、保存cacheを読書きしない。

<a id="ac-413-24"></a>
**AC-413-24** — Syncは自/他worktreeの記録を更新せず、世代・中央active一覧も保存しない。親集計は各対象の現存祖先を根拠にし、未読/不整合時はknown件数とcomplete=falseを出す。別worktreeの全Scopeの内容・実体を横断検証しない。選択IDから現在pathを導出するGitのファイル名検索は許容し、追跡済み・現在の未追跡（ignore対象を含む）の対象を扱う。製品がmetadataとpath安全性を検証する範囲は対象とその祖先に限定し、無関係なScopeの不正な実体によって選択観測を失敗させない。Gitの名前検索は定数時間を保証せず、有限timeout・検索失敗・重複対象・対象/祖先の安全性不明では不完全とする。現在tree全体を表示する通常のScope一覧の検証範囲は変更しない。


<a id="rq-413-12"></a>
### RQ-413-12 三階層と依存を維持する

三階層、実効依存、親自身のcompleted、WaitGraph循環禁止を維持する。

根拠: Q5・合意6。設計: [D-09](design.md#d-09)。

<a id="ac-413-25"></a>
**AC-413-25** — 誤った親kind、親不存在、祖先terminal/unknown、依存の自己/循環/自己待ちを拒否する。親Scope依存を子の完了率やactive件数で代替しない。既存のdeclared/effective表示を維持する。

<a id="ac-413-26"></a>
**AC-413-26** — GitHub-backedの正式create/import/Start/Finishに必要なlive観測ができなければ該当操作を停止する。既存資料の読取と通常本文編集は通信不能でも可能。


<a id="rq-413-13"></a>
### RQ-413-13 新規発行はGitHubだけ

正式な新規Initiative/Epic/IssueはGitHub create/importだけ。既存ID/linkageはそのまま保持する。

根拠: 合意7。設計: [D-09](design.md#d-09)。

<a id="ac-413-27"></a>
**AC-413-27** — scope create KIND --backend githubが返却番号から5桁以上の既存形式IDを作る。importはGETのみ。--backend local、UUID、番号未確定時の発行を拒否し、独自採番と全履歴走査は0。

<a id="ac-413-28"></a>
**AC-413-28** — schema3、旧local綴りのGitHub ID2件、未知任意fieldを保全する。移行で全Scope metadataのbytes/ID/親子/依存/linkageを変更しない。240件という利用者証拠は後続Codexの再検査と区別する。

<a id="ac-413-29"></a>
**AC-413-29** — 現在tree内のID重複、同一GH refの別kind二重登録を拒否する。別branchの同Scopeの存在は正常で、全branch共通の台帳を作らない。


<a id="rq-413-14"></a>
### RQ-413-14 branch切替とstaleを明示する

直接対象はworktreeに残り、checkoutで暗黙選択しない。壊れた/古い記録を空と偽らない。

根拠: Q1/Q3・最小状態の具体化。設計: [D-04](design.md#d-04)。

<a id="ac-413-30"></a>
**AC-413-30** — 普通のGit checkout後も直接記録のbytesは不変。対象/祖先が読めればselectedを維持しbranch差を表示する。対象が消えたらstale、動的selectorは停止、既知の直接ID/refは重複予約として扱う。

<a id="ac-413-31"></a>
**AC-413-31** — 読めない/未知schema/複数記録/identity不一致/消えたworktreeを分類し、自動修復・TTL解除・process推測をしない。helpと独立Scope読取を全体control条件で止めない。


<a id="rq-413-15"></a>
### RQ-413-15 既存CLIと成果物を狭く変更する

公開leafと重要な業務仕様を一覧で扱い、台帳等に依存する部分だけを必要な範囲で置換する。

根拠: 制約9。設計: [D-11](design.md#d-11)。

<a id="ac-413-32"></a>
**AC-413-32** — 基準catalogの44 leafがCLI対応表に一度ずつ存在し、各leafの変更/維持と旧optionの扱いが一意。今回追加leaf=0。旧rootコマンドやreleaseを復活させない。

<a id="ac-413-33"></a>
**AC-413-33** — Artifact六creation type、既存opaque evidence、Workbench copyのerror/overwriteとdest-only保全を維持する。Scope/依存/Artifact/通常編集に共通Startロック・chmod編集禁止・daemonを導入しない。

<a id="ac-413-34"></a>
**AC-413-34** — Git起源のworktree一覧、明示NAMEのcreate、path指定show/remove、明示bootstrapを使え、管理ID/alias/receiptが不要。dry-runでmakeを呼ばず、removeの安全条件とbranch保持を検査する。


<a id="rq-413-16"></a>
### RQ-413-16 移行は保全と局所切替

旧controlを復旧条件にせず、旧writer停止と保全を人間の手順として扱い、workspace契約だけ明示切替する。

根拠: 制約1/8/10。設計: [D-12](design.md#d-12)。

<a id="ac-413-35"></a>
**AC-413-35** — 旧controlなし/正常/破損/pending記録ありをread-only分類できる。対象workspaceはschema3のままwriter_protocolだけ変更する。旧.git独自領域に新しい値を書かず、旧journalをresumeしない。

<a id="ac-413-36"></a>
**AC-413-36** — 旧active/ユーザー成果物を保全し、全worktreeの無差別削除やgit cleanをしない。移行中断後は現workspaceを再観測し、新規操作として未切替/切替済みを区別する。backup不備や旧writer停止不能なら適用を停止する。

<a id="ac-413-37"></a>
**AC-413-37** — package更新は外部環境だけ、installation init/update/uninstallは明示worktreeの既知static資産だけ。未知改変資産、Scope、Artifact、Workbench、直接対象を一括上書き/削除しない。


<a id="rq-413-17"></a>
### RQ-413-17 Linux/macOSの通常試験と実入口で確認する

通常lint/pytestを維持し、Linux/macOSのfresh wheel/clone/linked worktreeと実consoleの動作で受け入れる。非対応OSの全機能portを品質gateへ含めない。

根拠: 制約10・計画要求。設計: [D-13](design.md#d-13)。

<a id="ac-413-38"></a>
**AC-413-38** — make lint、uv run pytest、git diff --checkを全体で実施し、Windows専用source/test/CIの撤去を含む旧保証ごとの削除/更新理由を残す。基準の既存失敗、新しいRed、skip、未実施を別記録し、元logを削除しない。

<a id="ac-413-39"></a>
**AC-413-39** — LinuxおよびmacOSでfresh wheel→checkout外venv→fresh clone+linked→controlなし→help/Start/Finish/Syncを実行する。stateful fake ghとlive環境を区別し、最低Python3.10・CI3.11、OS/FS別の実結果を記録する。Linuxの既存PATH不備runは失敗のまま保全し、検証containerのPATHだけを補正した再実行と分ける。Windows native/NTFSは要求しない。


<a id="rq-413-18"></a>
### RQ-413-18 納品・実装・正式登録を区別する

今回は第三者分析と差替え文書だけ。著述モデルと後続実装の作業契約を分け、製品実装、レビュー、merge、dogfood、正式importの完了証拠を分離する。

根拠: Q&A最終指示・制約10。設計: [D-14](design.md#d-14)。

<a id="ac-413-40"></a>
**AC-413-40** — HTMLが背景/構成/正常/異常/移行/実装順に加え、対応OS=Linux/macOS、Windows義務の失効、P-18の位置を自己完結して説明し、3〜5図、目次、top/engine-history/idsを備える。テンプレート実行JSと共有modalがbyte一致し、実描画は別検証として結果を記録する。

<a id="ac-413-41"></a>
**AC-413-41** — 単一rootのUTF-8 ZIP、schema/examples/リンク/ID対応、manifest sha256/bytes、ZIP CRCと展開bytesが整合する。第三者の差替えpayloadはreport.md、implementation-report.md、既存decision/interview/raw evidenceを生成/上書きしない。ローカル採用版ZIPには保有原文を変更せず収録し、manifestで生成・採用・実測の由来を区別する。

<a id="ac-413-42"></a>
**AC-413-42** — 実装担当は利用者の最新指定gpt-6.1-sol/maxを維持し、本追加分析と後続briefの著述モデルGPT-5.6 Sol / Proと区別する。P-18の実装開始は、更新済み正本を通常pushした後の独立ChatGPT Implementation Brief Strictで具体化し、そのbriefの成功をSpecDock正式Startと呼ばない。human merge・P-16 dogfood適用・P-17既存#413正式import/Startを別の未着手stepへ置き、既存#413を再作成せずCodex保有証拠を保全する。


<a id="guarantees"></a>
## 明示的に変える保証

| 基準実装の契約 | 新契約・失うもの | 理由 |
|---|---|---|
| 全登録worktreeのengine digest/epoch/ready | 起動はinstalled package、writerは自workspace互換性。全体readyなし | 外部CLIと必要時観測へ |
| 全writer共通lockとlifetime lease | Startの競合開始だけ直列化。通常編集等の同時変更は完全transactionではない | 利用者が広いロックを不採用 |
| active setで任意対象を取得、部分clear/Finishで親へ昇格 | 新規取得はStartのみ。show/clearと動的参照は残す。親は文脈/集計 | lock外の取得経路と暗黙の重複開始をなくす |
| 永久canonical branch対応 | デフォルト候補または明示branch。現在選択のbranch記録は履歴の一件だけ | 共有binding台帳なし |
| local発行・予約・高水位・永久tombstone | 新規GitHub発行/取込のみ。現在treeの二重登録は拒否。削除済みScopeの再importは可能 | ID保全と永久台帳は別 |
| operation IDで続行/巻戻し | 現物を再観測して新しい明示操作。失った送信意図は復元できない | journal、自動復旧を持たない |
| generationとGitHub cacheの同期 | Syncはその場の表示。保存済み観測からfresh/完了を作らない | 初期cache・中央選択コピーなし |
| installationがcommon-dirの全作業場を更新 | 自分が指定したworktreeのstatic資産だけ | mainや全worktreeを制御単位にしない |
| Linux/macOS/Windowsの最小adapterと三OS受入 | Linux/macOSだけを対応OSとし、Windows専用source/test/CIと未完了義務を撤去する。utilityはcontext-freeのまま | 2026-10-02 JSTの最新利用者決定 |

通常metadataへの楽観的な再検査は維持できますが、ロックを除いても従来の全writer直列化保証が残るとは説明しません。依存の同時編集は、読み取ったsnapshot内の検査と公開前再確認、後続validateで検出します。任意の並行非協調変更まで循環を絶対防止する保証はありません。

<a id="start-conditions"></a>
## 実装開始条件・残余リスク

利用者のQ1〜Q8は解決済みです。本版は保存方式、activeの最小制限、CLI引数差分を設計判断として固定しており、実装者が一般的な製品再検討を始める必要はありません。対応OS判断も解決済みで、Windowsを完成させる再検討は行いません。検証済みSHAとの対応表を再確認し、差分があれば該当stepだけ止めてD節を修正します。

Linux/macOSのOS/FS原語、fresh wheel、既存240 metadataの全件schema適合、ブラウザ実描画は公開条件であり、今回の資料生成だけでは充足しません。Windows専用実装と未完了testはP-18の撤去対象で、完成・port・native受入の残作業ではありません。P-18は更新済み正本のpushと独立Implementation Brief Strictより前にコードへ着手しません。

同一cloneを異なるOSユーザーや複数ホストで共有する新保証は追加しません。それが実際の導入先の必須条件であると判明した場合は、勝手な権限変更や別lock方式へfallbackせず、該当環境への適用を停止するmaterialな適用判断です。core実装の無関係な機能を増やす理由にはしません。

実適用には旧writer停止、実体backupと復元確認、unknown remoteの照合、対象への許可が必要です。直接状態はignoredなので強制clean/手削除で失えます。電源断、媒体故障、非協調Git、記録をコピーした後のidentity再利用まで、永続台帳なしに完全検知できるとはしません。これらの限界を運用へ渡します。

### 2026-10-03 current disposition

- RQ/ACの製品実装と既存検証証拠は、検証済みSHA `8606e132327066d56567556e336e4bc1ae6a0b17` に結び付けます。今回の文書置換fileはその後の候補であり、新しいGate合格を主張しません。
- 実行runtimeは利用者の外部tool環境にあるpackageです。program更新はその環境に共有されます。docs/system/templates/skills/shim/workspace宣言は明示したworktree単位の静的資産で、直接作業記録はさらに別のignored runtime stateです。
- P-16は0805 worktreeへの適用だけ完了観測があります。mainとほか3 linked worktreeの移行、clone全体のcompleteなSync、P-17の正式#413 import/Start、P-15の人間merge、package publicationは完了扱いにしません。
- 既存Gateの情報提供P2のうち、plan集約状態の不整合は本差し替えで文書上修正します。効果前mkdirのpartial分類と非UTF-8 pathname診断のJSON境界は製品コードの既知事項として残り、本作業では変更しません。
