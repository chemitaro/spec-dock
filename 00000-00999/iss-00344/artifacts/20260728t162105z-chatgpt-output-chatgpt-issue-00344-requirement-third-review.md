# Issue 344 Requirement Review

## Verdict

FAIL

## Findings

### F-007 [blocking] root Workbench と scoped `workbench copy` の適用範囲が閉じていない

* Location:

  * `§1.2 完了後に観測できること` item 6
  * `SC-344-004 Linked worktree`
  * `I344-RQ-003 README guidance` elements 5 / 8
  * `I344-RQ-007 Git checkout and manual copy positioning`
  * `AC-344-007A` / `AC-344-007B`
  * `I344-RQ-010 Documentation`
  * `report.md` Decision Ledger `D-002`
* Problem:

  * 要件は fresh root と3種類のnodeにbyte-identicalなREADMEを配置した上で、ignoredな作業fileは必要時に`workbench copy`で移すと一般化している。この記述をroot READMEで読むと、root `.workbench/`も同commandの対象であるように解釈できる。
  * しかし現行`workbench copy`はfull Initiative / Epic / Issue IDだけを受け付けるscoped commandであり、root scopeを受け付けない。application guardも`init` / `epic` / `iss`だけを許可し、既存CLI testは`--root`を明示的に拒否している。
  * 採用済みの既存command契約でも、root Workbenchはbulk copy対象外、`workbench copy`はInitiative / Epic / Issueのscope-local Workbenchだけを扱う。現在のtarget-state整理も「current worktreeのscope Workbenchをtarget linked worktreeの同scopeへcopy」と限定している。
  * Issue 344はexisting command surfaceとsource-wins behaviorを維持するsliceであり、root selector追加を所有していない。現状のままでは、design実装者が「root copy routeを追加する」「root READMEに実行不能な案内を載せる」「暗黙にnodeだけをtestする」のいずれを選ぶべきか一意に判断できない。
* Required correction:

  * `workbench copy`の適用対象を、existing commandと同じ**Initiative / Epic / Issueのscope-local Workbenchだけ**とrequirementで明記する。
  * root `.workbench/`は同commandの対象外であり、root selector、root bulk copy、root path-selection routeをIssue 344では追加しないことを明記する。
  * 4つのbyte-identical READMEには共通して、次の区別が分かる文言を要求する。

    * tracked READMEはroot/nodeとも通常のGit checkoutで移る。
    * `workbench copy`は対応するnode scopeのignored payloadを明示的に移すoptional helperである。
    * rootのignored payloadはこのhelperでは移らず、durableに残す一fileはgeneric Artifact importを使う。
  * `SC-344-004`とacceptance criteriaをroot/node別に閉じる。少なくとも、root READMEがroot copy対応を示唆しないこと、CLIがroot routeを引き続き拒否すること、node-scoped copyが既存source-wins behaviorを維持することを検証可能にする。
  * root copyを新たに提供する意図である場合は、Issue-localな解釈で追加せず、親Epicのrequirement・design・Issue ownershipを先に改訂する。
  * `report.md`の`D-002`、Evidence Adoption Ledger、requirement authoring gateにも本findingの採否と再レビュー状態を反映する。
* Evidence:

  * canonical requirementはrootとnodeのREADMEを同一契約に置きつつ、manual copyのscopeを限定していない。
  * 親計画はCandidate 1にexisting `workbench copy` compatibilityだけを割り当て、root copy capabilityの追加を割り当てていない。
  * 現行approved contractではroot/date/path routeは対象外である。

## Scope and consistency checked

* GitHub Connectorで`chemitaro/spec-dock`の指定branchを開き、HEADが指定commit `d7bdb6b3207fcde616da63550c6ff7038c1cd03f`と一致するrevisionを対象に確認した。指定済み修正領域は再確認し、解消済みfindingとして再掲していない。
* 添付review taskの責務、PASS条件、advisory / evidence-only境界に従った。
* 親Epicのfresh root / future node shell、README-only tracking、optional presence、no-backfill、semantic opacity、manual-only helper、provider-first境界と照合した。
* Issue 344がshellとfocused package/copy evidence、Issue 345がgeneric import、Issue 346がcandidate-wheel E2E、dogfood、full regression、最終レビュー、PR deliveryを所有する分割を確認した。
* READMEの9 guidance elements、Git ignore非security boundary、explicit importのevidence-only authority、exact repo-local invocationを確認した。root/scoped copyの適用範囲以外にblockingな欠落は確認しなかった。
* provider source、installer fallback、nested README prune、package include/exclude、node scaffoldのplanned/result/filesystem seam、Workbench opacity testsを照合した。
* `report.md`は現在もrequirement再レビュー待ち、design / planは未合成placeholderであり、先行したdesign promotionやimplementation readinessの主張は確認しなかった。

## Residual risks

* 現行installerの`_prune_legacy_scaffold`は`templates/README.md`以外のnested READMEを削除し、`pyproject.toml`もnested template READMEを広域除外している。designでは4つのWorkbench READMEをexact allowlistとして、pruneとpackage exclusionの双方を同時に修正する必要がある。
* 現行provider `.gitignore`とinstaller fallbackは`.workbench/`全体をignoreしているため、README-only trackingは未実装である。これは予定された実装deltaであり、本findingとは別のrequirement blockerではない。
* build、wheel、sdist、installed-resource inventory、real Git ignore matrix、focused pytestは本レビューでは実行していない。実装、test、build、PR、merge、Issue finishの完了は未検証である。
* 本判定はread-only advisory evidenceであり、canonical authorityまたはreview gate更新そのものではない。

## Promotion decision

* requirement phase を design phase へ昇格不可
* F-007をcanonical `requirement.md`と`report.md`へ反映し、同一revisionに対するfresh requirement reviewでblocking findingがなくなるまでdesign authoring gateを開けない。
