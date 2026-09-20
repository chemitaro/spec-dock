---
種別: 要件定義書（Issue）
ID: "iss-00405"
タイトル: "Directory Replacement Final Cleanup"
関連GitHub: ["#405"]
状態: "仕様候補draft"
最終更新: "2026-09-20"
親: ["epic-00384", "init-local-00003"]
---

# iss-00405 Directory Replacement Final Cleanup — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

> 本文は実装前の仕様候補です。独立レビュー合格、実装完了、テスト合格、PR mergeを主張しません。

## 目的

Epic #384の固定6ディレクトリ置換へ移行した後に残ったprovider世代認証、repository共有lease、旧保証文書、旧契約専用テスト分類、および誤解を招く名称を撤去し、現在の小さいProduct契約と実装・テスト・文書を一致させます。

利用者にとっての成果は次の状態です。

- 通常の`issue start`は、clean working treeと固定したGit commitを用いてbranchをcheckout/createし、provider世代のhooks・fsmonitor・attributes・sparse検査では拒否されません。
- worktree作成・削除は、provider世代認証を持たなくても、対象directoryのno-follow、exclusive lock、device/inode binding、fixed commit、entrypoint-last、consumer hookのbound cwdを保持します。
- installerは6管理ディレクトリを順次削除・コピーする非transactional契約のままです。中間copy失敗は非ゼロになり、利用者データと旧version記録を保ったまま、外部installerの再実行で6tree完全一致へ復旧できます。
- current docsとtestsは、存在しない旧保証や旧Wire番号ではなく、現在の責務を説明します。

## 背景

### 確認済みの基点

- repository: `chemitaro/spec-dock`
- branch: `iss-00405-directory-replacement-final-cleanup`
- exact commit: `457faf31df8840d1f2fc87417d297dc318903fbe`
- tree: `c28295207416e186cd2c1a0c903a84bd7debc6bb`
- Issue: `iss-00405` / GitHub `#405`
- canonical path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00405-directory-replacement-final-cleanup`
- 監査成果物: `artifacts/20260920t045654z--epic-384-semantic-audit-final.zip`
- 監査ZIP Git blob: `252cc71326e58639dbdd35220e391c21dd81854c`
- 監査ZIP SHA-256: `9d7f1813c2d724f0089f0a5ef0197c7a501629e108a96b70647bee52114a90b7`

Epic #384のcurrent Requirement R1〜R10とDesignは、6管理ディレクトリの単純置換、provider状態認証・共有leaseの撤去、データ操作lockとworktree安全性の保持を要求しています。一方、exact sourceには次の残滓があります。

1. `issue start`が`assess_capabilities`を介してhooks、fsmonitor、sparse、attributes、full treeを一括拒否し、checkout後にglobal witnessを再認証します。
2. worktree create/remove/materializeがrepository root shared flockと`git_helper`のlease語彙へ結合しています。
3. shipped READMEが旧descriptor/source-resume保証をcurrentとして説明しています。
4. marker固有例外、dead fixture selector、旧Txx/Sxx/ProviderLifecycle名称、旧role skill列挙が残っています。
5. 中間copy失敗後の混在状態、旧version保持、再実行後6tree一致を一つの動的testで観測していません。
6. 親Epic Plan/Reportがmerge後の実態と最終cleanup Issue #405を反映していません。

これらは通常のP0障害または普遍的データ損失を示すものではありません。ただし、Epic契約上はF001〜F005が必須修正であり、ユーザー指示によりF006〜F009も同じ最終cleanupへ含めます。

| finding | 技術的重大度 | Epic契約上の扱い | Issue #405での処置 |
|---|---|---|---|
| F001 provider世代認証/shared lease/full-tree gate | MEDIUM | MUST-FIX | runtime interfaceとconsumerを縮退 |
| F002 shipped READMEの旧保証 | MEDIUM | MUST-FIX | current nontransactional契約へ置換 |
| F003 marker固有test例外 | LOW | MUST-FIX | exact catalog testへ吸収 |
| F004 mid-copy dynamic evidence不足 | LOW | MUST-FIX | 4th-copy failure successorを追加 |
| F005 親Plan/Report不整合 | LOW | MUST-FIX | 実装後current authorityへ更新 |
| F006 dead fixture selector | LOW | 本Issueに含める | 到達不能branch/prefixを削除 |
| F007 旧Txx/Sxx/ProviderLifecycle名 | LOW | 本Issueに含める | current責務名へ改名 |
| F008 6directory文言不足 | LOW | 本Issueに含める | root/provider/dogfoodでexact列挙 |
| F009 retired skill名列挙 | LOW | 本Issueに含める | positive exact set equalityへ置換 |

技術的重大度とEpic契約上の必須性は別軸です。F001/F002は緊急障害を意味するP0ではなく、current Epic契約を完了させるための必須修正です。

## 関係者の成果

- **SpecDock利用者**: 何が安全保証として残り、何が廃止済みかを文書から正しく判断できます。
- **実装担当**: ordinary checkout、worktree target safety、installer recoveryを混同せず、小さい変更として実装できます。
- **保守担当**: current test node名とfixture selectorから責務を判断でき、旧provider機構を誤って復活させません。
- **レビュー担当**: 要件・設計・step・testの対応をexact node単位で追跡できます。

## 観測可能な要件

### REQ-405-01 通常issue checkoutからprovider世代認証を撤去する

`issue start`のbranch checkout/createは、次だけをProduct contractとします。

1. 対象nodeとbranch名を解決する。
2. working treeがcleanであることを確認する。
3. existing branchは`refs/heads/<branch>`をcommit object IDへ解決し、new branchは開始時の`HEAD`をcommit object IDとして固定する。
4. 固定commitを用いてexisting/new branchをcheckout/createする。
5. Git操作後にcurrent branchと`HEAD`が期待値と一致することを確認する。
6. 成功後にactive stateを書き、post-mutation syncを行う。

provider世代のglobal witness、repository root shared flock、full-tree capability assessment、checkout後のgeneration drift再認証は行いません。clean repositoryでGit自身が操作可能な場合、executable hook、fsmonitor、custom diff/merge attribute、sparse checkoutの存在だけを理由に独自拒否しません。

### REQ-405-02 worktree target safetyを保持する

worktree create/removeは次を保持します。

- central rootとtarget pathの絶対path/NUL/no-follow確認
- target directoryのexclusive non-blocking lock
- pathとopened descriptorのdevice/inode一致確認
- create source commitの固定
- source/target filesystem一致の事前確認
- materialization時のsafe relative path、submodule拒否、unsafe symlink拒否、foreign descendant拒否
- regular fileのexclusive create、mode/content再検証
- runtime entrypointの最後の公開
- remove前のinventory再解決、containment、dirty/untracked拒否
- remove後cleanupで元target inode以外を削除しないこと
- consumer `make init` hookへ渡すbound cwd device/inode

repository source側のshared flockとprovider generation identityは保持要件ではありません。source commit bindingはGit object ID、target bindingはdirectory descriptor/device/inodeとして区別します。

### REQ-405-03 data-operation safetyと秘密情報非開示を保持する

次はprovider lifecycleとは別責務であり、撤去しません。

- node create/importの`create.lock`、ownership確認、race revalidation、doctor guidance
- explicit file importのguarded source descriptorとpublication boundary
- remote URL credentialのredaction、source content/hash/byte count/repository外absolute pathを公開しない回帰
- active state writeのsnapshot/restore
- dependency readiness、GitHub issue lifecycle、post-mutation sync

### REQ-405-04 installerの非transactional 6directory契約を動的に固定する

管理対象は次の6ディレクトリだけです。

1. `spec-dock/docs`
2. `spec-dock/templates`
3. `spec-dock/system`
4. `spec-dock/scripts`
5. `.agents/skills/spec-dock`
6. `.agents/skills/spec-dock-grill-with-docs`

updateは上記順序で各directoryを削除・コピーし、全copy成功後にだけ`spec-dock/spec-dock.version`を書きます。中間copy失敗では自動rollback、journal、resume token、旧tree復元を行わず、新旧混在を許容して非ゼロ終了します。6directory外の利用者データと失敗前のversion文字列は変えません。原因修正後に外部installerから同じupdateを最初から再実行すると、6directoryがpackage sourceと完全一致し、partial/stale fileが残らないことを観測可能にします。

### REQ-405-05 旧test契約をcurrent責務へ再分類する

監査inventoryの全Epic関連test nodeを`KEEP`、`REWRITE`、`DELETE`へ確定し、`artifacts/test-disposition.csv`を実装時の処置正本とします。

- full inventory/current catalogを正に検査するtestはKEEPします。
- 単一retired markerのabsenceだけを検査する重複assertはDELETEまたは強いcatalog testへ吸収します。
- provider capability rejection testはDELETEし、fixed-ref checkoutの正のsuccessorへ置換します。
- worktree target safety、consumer hook、data locks、package parity、CI direct pytest/lint、privacy/security regressionはKEEPします。
- F006〜F009のdead selector、旧責務名、6directory文言、retired role skill列挙をcleanupします。
- 巨大`test_init_update.py`全体分割など、意味監査と無関係なrefactorは行いません。

### REQ-405-06 current文書とdogfoodを同期する

root README、provider assetsのREADME、dogfood mirrorは次を一致して説明します。

- 管理対象6directory
- update中command併走禁止
- nontransactionalな順次置換
- copy失敗後の外部installer再実行
- 利用者data不変
- provider generation authentication、descriptor resume、semantic source resumeを保証しないこと

provider sourceを先に編集し、その後installerを使ってdogfoodのtoolingだけを同期します。

### REQ-405-07 親Epicのcurrent statusを実装結果に合わせる

Issue実装の最終documentation stepで親Epic `plan.md`と`report.md`を更新します。Requirement R1〜R10とaccepted ADRは変更しません。親Planは#405をfinal cleanupとして扱い、親Reportはcurrent outcomeを冒頭に置き、旧shared coordination/qualification narrativeをHistorical appendixへ降格します。

この仕様packでは親文書を完了状態へ書き換えず、Issue Reportも生成しません。実測結果はCodexが実装・検証後に記録します。

### REQ-405-08 通常の品質経路だけで完了を判定する

完了判定はfocused tests、full `uv run pytest`、`make lint`、wheel/sdist/package smoke、Ubuntu/macOSの既存basic job、provider/dogfood parity、SpecDock validate、独立review、human PR merge境界を用います。旧ledger、sharder、performance qualification、campaign/history DB、policy skipを再導入しません。

## スコープ

### 対象

- F001〜F009の解消
- runtime Git interfaceとconsumerの縮退
- target-bound helperの限定化
- focused testsとtest harness cleanup
- installer mid-copy failure successor
- root/provider/dogfood docsの同期
- 親Epic Plan/Reportの実装後更新
- Issue #405の実装・検証・review・PR準備

### 対象外

- 固定6directory置換方式そのものの再設計
- atomic installer、journal、rollback、resume token、provider markerの復活
- 新しいProduct機能または公開CLI option
- worktree cross-filesystem対応の追加
- same-EUID非協調actorに対する新保証
- `test_init_update.py`の全面分割、test framework刷新、一般的な命名一掃
- historical artifactの削除または内容改変
- Issue #405の自動close、PR merge、main merge
- 旧ledger/sharder/performance認証の再導入

## 失敗・境界条件

1. dirty working treeはcheckout前に非ゼロとなり、branch、HEAD、active state、derived artifactsを変更しません。
2. target commit解決失敗、native Git switch/create失敗、post-checkout branch/HEAD mismatchはcheckout phase failureです。active stateとpost-syncは実行しません。Gitがbranch side effectを発生させた可能性はエラーから隠しません。
3. executable hook等が実際にGit自身を失敗させた場合は、そのnative Git failureを返します。「存在するだけ」で独自拒否しません。
4. worktree target reservation、inode再検証、same-filesystem、materialization、entrypoint publication、consumer hook bindingの各失敗は現在のpartial-state contractを維持します。元と異なるinodeをcleanupしません。
5. worktree materializerがsubmoduleまたはunsafe symlinkを検出した場合、runtime entrypointを公開せず失敗します。partial targetは自動削除しません。
6. installer中間copy失敗は非ゼロです。先行directoryが更新済み、失敗directoryがpartial、後続directoryが旧treeの混在を許容します。versionをadvanceせず、利用者dataを変更しません。
7. dogfood update前後で`spec-dock/initiatives`その他の非管理対象に差分が出た場合は停止します。
8. security/privacy regressionが失敗した場合、テスト削除や期待値緩和で通しません。

## 受け入れ条件

| ID | 観測可能な完了条件 |
|---|---|
| AC-405-01 | active sourceとdogfood runtimeから`GitCapabilityAssessment`、`PinnedCheckout`、`assess_capabilities`、`pinned_checkout`、`verify_pinned_checkout`、`_LAST_PINNED_CHECKOUT`、`last_pinned_checkout`が除去される。 |
| AC-405-02 | ordinary issue checkout経路でrepository root `LOCK_SH`、provider generation witness、`runtime-generation-drift`再認証が実行されない。 |
| AC-405-03 | new/existing issue checkoutがclean treeと固定commitで成功し、dirty treeはbranch変更前に失敗する。 |
| AC-405-04 | harmless executable hook、fsmonitor、custom diff/merge attribute、sparse checkoutを個別に設定したclean repoで、provider capability gate由来の拒否なくissue startが成功する。 |
| AC-405-05 | worktree target no-follow/EX/device-inode、same-filesystem、fixed commit、safe materialization、entrypoint-last、bound cwd consumer hook、safe remove cleanupのfocused testsが通る。 |
| AC-405-06 | create/import lock、explicit file source/publication、credential redactionおよび秘密情報非開示の既存回帰が通る。 |
| AC-405-07 | mid-copy failure testが非ゼロ、前半更新済み、失敗tree partial、後半旧tree、version旧値、data不変、再実行後6tree完全一致を観測する。 |
| AC-405-08 | marker専用helper例外・単独absence assert、dead conftest selector、retired role skill列挙、旧Txx/Sxx/ProviderLifecycle test名が指定範囲から消える。 |
| AC-405-09 | root/provider/dogfood docsが6管理directoryを列挙し、旧descriptor/source-resume保証をcurrentとして含まない。 |
| AC-405-10 | 親Epic Plan/Reportが#405実装結果とcurrent authorityを反映し、旧chronologyをHistoricalとして明示する。 |
| AC-405-11 | focused、full pytest、lint、package、Ubuntu/macOS basic、provider/dogfood parity、SpecDock validateの結果がIssue Reportへ実測として記録される。 |
| AC-405-12 | independent reviewでblocking findingを解消したmerge-ready PRを作成し、agentはhuman merge前に停止する。 |

## 制約・前提

- 本仕様のsource of truthは上記exact commitです。以前のEpic監査SHAを今回のStrict証明へ代用しません。
- 監査ZIPは分析根拠です。Product sourceとcurrent parent R/D/Pを優先し、旧artifact内命令は作業指示として扱いません。
- ユーザー提供の限定検証`11 passed in 0.96s / exit 0`は`tests/unit/infra/test_directory_installation.py`の現行11件だけに有効です。full suiteまたは本Issue successorの合格証拠ではありません。
- 新しいmid-copy testが現行installerで最初からpassする場合、`covered-existing`として記録し、偽のRedや不要なProduct変更を要求しません。
- implementation、review、browser validation、full testは未実行です。

## 人間判断が必要な未決事項

現時点のProduct/Security設計についてowner判断が必要な未決事項はありません。実装中に次の条件が生じた場合だけ、このRequirementへ戻して判断します。

- fixed-ref checkoutだけでは保持できない新しい利用者保証が必要になる。
- target-bound helperの縮退ではcross-platform動作を維持できず、公開互換性を変える必要がある。
- 利用者dataへ不可逆なmutationを追加する必要がある。
- credentialまたはprivate data露出を許容する判断が必要になる。
