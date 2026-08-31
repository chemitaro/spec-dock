---
種別: ADR（Architecture Decision Record）
ID: "20260831t005139z-adr"
タイトル: "Disposable Provider Roots And Fixed Skill Slots"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-08-31"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-08-31"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from: ["20260830t234548z-research", "20260830t235429z-disc", "20260831t005132z-disc", "20260818t031610z-adr"]
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
---

# 20260831t005139z-adr Disposable Provider Roots And Fixed Skill Slots

本ADRは、Epic #384 におけるdistribution product contractのaccepted authorityである。個別behaviorの受け入れ条件はEpic / Issue Requirement、構造はDesign、実装順はPlanへ反映する。

## Context

SpecDockは軽量なrepo-local toolを目指す一方、現行distribution engineはprovider fileごとのidentity、historical digest、preservation、journal、retry checkpoint、cross-intent recovery、deprovision、spec-history purgeを統合している。その結果、`managed_distribution.py` は22,332行、主要distribution testsは約35,000行になり、2,708-test Full Regressionは4 shardでも約99分wall・約5.51 shard-process-hoursを消費した。

Product ownerは、次を明示した。

- Initiativesとその配下のArtifactsは利用者データとして残す。
- 再生成できるprojectionをinstall / updateの差分管理対象にする必要はない。
- SpecDockが所有する `scripts`、`docs`、`templates`、`system` は、更新時に古い内容を捨てて全量交換できる。
- skillは共有 `.agents/skills` の下にあるため、他skillを壊さずに追加・更新・削除する最小状態が必要である。

accepted ADR `20260818t031610z-adr` は、当時の広い自動復旧contractを前提に、unified per-file operation modelとjournaled forward recoveryを採択した。Epic #384のroot-cause analysisにより、この契約自体がtest state spaceの主要因であり、simple toolの目標と一致しないことが判明した。

## Decision

### 1. 利用者データをdistribution authorityから除外する

`spec-dock/initiatives/**` と、その配下のすべてのArtifactをdurable user dataとする。init、update、tooling uninstall、retry、cleanupは、これらを作成・変更・移動・削除するauthorityを持たない。

`spec-dock/.workbench/**` と未知のpathもopaque user/local dataとして保持する。通常tooling lifecycleはspec-history purge authorityを暗黙取得しない。

### 2. 生成物を配布差分として管理しない

`spec-dock/active/**`、`spec-dock/.agent/**`、dashboard、tree / deps diagrams、ADR mirrorなど、source dataから再生成できるprojectionは、provider file inventory、historical identity、uninstall delete listへ含めない。必要な整合性は各projectionのsync / rebuild commandが所有する。

### 3. 4つのprovider rootをdisposableにする

通常updateが所有するrepo-local provider contentは、次の固定rootだけとする。

1. `spec-dock/docs`
2. `spec-dock/templates`
3. `spec-dock/system`
4. `spec-dock/scripts`

updateはcandidateの4 rootをすべてstage・validateした後、各target rootを全削除してcandidate rootへ置換する。`scripts` は最後に置換する。root allowlistは実装に固定し、workspace manifestやCLI引数から任意pathを追加できない。

各rootの内部はprovider implementationである。inner fileのuser edit、unknown file、obsolete file、同一bytes / inode差を保存・調停しない。root ownershipが成立したupdateでは、内部を無条件にcandidateと同じtreeへする。この破壊的性質をpublic documentationへ明記する。

### 4. 安全性をroot boundaryで証明する

target root、親binding、repository rootをdestructive step直前に検証する。root自体がsymlink、unexpected type、別parentへrebindされた状態では、子を辿らずwrite前にblockする。

update processは置換されるrepo-local `scripts` の外側にあるinstalled package / external processが所有する。candidate stagingはtarget mutation前に完成させる。

small atomic installation record / ready markerを一つだけ持ち、schema、installed version、candidate digest、fixed skill slot versionsを記録する。per-file identity、action checkpoint、rollback image、arbitrary manifest pathは記録しない。

### 5. update全体のatomicityとautomatic rollbackを約束しない

4 root全体は一つのfilesystem transactionではない。root削除とrenameの間、またはroot間でprocessが停止すると、toolingが一時的に欠落・混在し得る。user dataが影響を受けないことを不変条件とし、外部installerから同じdesired versionのupdateを再実行して収束させる。

operation journal、per-action checkpoint resume、cross-intent forward recovery、automatic whole-operation rollback、quarantine restoreは通常update contractから廃止する。ready markerは全rootとskill slotの配置完了後にだけ更新する。staging cleanup failureはupdate成功をrollbackしない。

### 6. skillは固定slot rootで管理する

`.agents/skills` 親全体をprovider-ownedとしない。現行managed skillは次の2つのfixed slotに限定する。

- `.agents/skills/spec-dock`
- `.agents/skills/spec-dock-grill-with-docs`

各slot rootへowner、slot、schema versionを持つ小さなmarkerを同梱する。installはabsent slotへrootを追加し、updateはvalid owner markerのあるexact slot root全体を置換し、uninstallはvalid markerのあるexact slotだけを削除する。markerが欠落・不正・別ownerなら上書きも削除もせずblockする。

retired skillは、codeに固定された有限のexact-slot allowlistとvalid old owner markerの組合せでだけ削除する。prefix match、任意manifest path、`.agents/skills`全体scan、per-file historical digestを削除authorityに使わない。unrelated skillsは常に保持する。

marker導入前のcurrent 2 skill rootsは、期限付きone-shot migrationでexact current treeを認識してmarker付きrootへ移す。migration完了後は旧identityとtestsを削除する。

### 7. uninstallをtooling-onlyにする

通常uninstallは4 disposable root、valid owner markerを持つfixed skill slots、small installation recordだけを対象にする。`spec-dock/initiatives/**`、nested Artifacts、`.workbench/**`、generated projections、unknown paths、unrelated skillsを変更しない。

spec historyの削除は通常uninstallから分離する。`--remove-specs`を維持する場合でも、独立したpurge authority / commandとして別途設計し、update、retry、tooling uninstallから権限昇格できないようにする。

### 8. testを新しいdeep interfaceへ置換する

testsはper-file reconciler内部ではなく、`install_tooling`、`update_tooling`、`uninstall_tooling`に相当するservice interfaceを主対象にする。最低限、次を証明する。

- 4 rootがcandidateと完全一致し、obsolete inner fileが残らない。
- durable user dataとunrelated skillがbyte-identicalである。
- staging failureではtarget mutationを開始しない。
- root間failure後の再実行でdesired stateへ収束する。
- symlink root / parent rebind / unexpected typeでfail closedする。
- skill markerのowned / unknown / retired境界が正しい。

新contractのproofが成立したchangeで、旧journal、checkpoint、historical per-file identity、cross-intent、purge integration testsを削除する。旧testをslow laneへ残さない。

### 9. 既存ADRを部分的にsupersedeする

本ADRは `20260818t031610z-adr` のうち、provider distribution update、tooling deprovision、skill projectionに関する次の判断をsupersedeする。

- unified per-file action grammar
- Operation Journalによるarbitrary checkpoint forward recovery
- managed deprovisionとspec-history purgeの同一engine化
- provider / skill fileごとの無期限historical identity管理

同ADRのpre-write fail-closed、fixed root binding、unknown shared content preservation、deprovisionとpurgeのauthority separation、whole-operation rollbackを約束しない原則は維持する。

## Options

### 採択: Option C2 — Disposable Root Replacement

repo-local self-contained toolを維持しつつ、provider内部を全量置換可能にする。user dataとshared skill parentだけを強いownership boundaryで守る。product state spaceとtest state spaceを同時に最も大きく縮小できる。

### 棄却: 現行per-file reconcilerを維持してtestだけ整理する

test重複は減らせるが、historical identity、journal、checkpoint、recovery matrixをproduction contractとして残すため、根本的な状態数と保守費用が残る。

### 棄却: immutable versioned payload + activation pointer

全rootを一つのversioned payloadへ集約できればcleanなatomic activationを得られる。しかし現行canonical docsは `spec-dock/docs` へのrelative linkを持ち、repo-local file layout自体が利用される。pointer / symlink projectionを導入すると、portabilityとshared projectionの別管理が必要になる。現在の軽量化後surfaceでは、4 root全量置換の方が小さい。

### 長期候補: package-onlyでrepo-local distributionを廃止する

runtimeをinstalled packageだけから実行すれば最小になるが、repo内docs / templates / scriptsを利用する現行workflowとskill配布を変更する。将来self-contained layoutが不要になった場合の再検討対象とし、今回のcutoverには採用しない。

### 棄却: `.agents/skills` 全体を置換する

他providerとconsumer-owned skillsを削除するため、ownership境界に反する。

### 棄却: skill fileごとのhash catalogを維持する

一つのskill変更ごとにold digest、collision test、projection parity testを加算する現行問題を再生産する。fixed slot markerでroot ownershipを証明すれば不要である。

## Consequences

### Positive

- provider内部のobsolete fileは自動的に消え、削除listやhistorical file catalogが不要になる。
- state modelが `absent / ready(version) / updating-or-incomplete / blocked` 程度へ縮小する。
- user data保護を、数千のfile state組合せではなく固定root境界で説明・検証できる。
- update / uninstall testsを数百のper-file casesから少数のservice contractへ統合できる。
- skill更新はroot replacementになり、内部file追加・削除にmigration stateを追加しない。
- parallelismなしの単一process10分というEpic goalに、production complexity削減から寄与する。

### Cost / Breaking behavior

- 4 provider rootとmanaged skill slot内のlocal editsはupdateで失われる。
- update中のprocess停止でtoolingが一時的に欠落・mixed versionになる可能性がある。
- repo-local scriptだけでは復旧できない場合があり、installed package / `uvx`からの再実行経路を明示する必要がある。
- marker導入前workspaceにはone-shot migrationが必要である。
- `--remove-specs`、`init --force`、既存JSON shapeにはdeprecationまたはbreaking-change判断が必要になり得る。
- old engineとnew engineを長期並置すると一時的にtestが増えるため、Issue単位で旧route削除まで完了する必要がある。

### Unresolved decisions

- `.github/workflows/ci.yml` のownershipと更新方法
- legacy direct updateのsupport window
- purge CLIの廃止または独立化に伴うpublic compatibility
- `.gitignore` init seedの既存file collision policy
- wheel / sdist / macOS validation trigger

これらは本ADRの4 root / fixed skill slot判断を未決へ戻さない。影響するIssueの開始前に個別に確定する。

### Revisit conditions

次のいずれかが実証された場合は新ADRで見直す。

- consumerがprovider root内のlocal customizationをdurable public requirementとして必要とする。
- toolingの一時的欠落を許容できず、cross-root atomic activationが必須である。
- fixed skill slot markerだけではshared ownershipを安全に証明できない実例がある。
- one-shot migration対象を有限にできず、実利用workspaceの大部分が更新不能になる。
- simplified implementation後もsingle-process regressionが10分を大幅に超え、主因がdistribution以外にある。

## References

- `20260830t234548z-research-provider-test-suite-root-cause-analysis-and-redesign.md`
- `20260830t235429z-disc-provider-test-strategy-simplification-decision-analysis.md`
- `20260831t005132z-disc-disposable-root-replacement-and-skill-lifecycle-design.md`
- superseded in part: `../../epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/artifacts/20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md`
- provider source: `src/spec_dock/assets/spec_dock/`
- current managed skill source: `src/spec_dock/assets/install_root/.agents/skills/`
