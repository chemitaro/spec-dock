---
種別: disc
ID: "20260831t005132z-disc"
タイトル: "Disposable Root Replacement And Skill Lifecycle Design"
状態: "complete"
作成者: "iwasawayuuta"
最終更新: "2026-08-31"
親: ["epic-00384"]
template: "disc"
authority: "evidence"
derived_from: ["20260830t234548z-research", "20260830t235429z-disc", "20260818t031610z-adr"]
reflected_to: ["20260831t005139z-adr", "../requirement.md", "../design.md", "../plan.md", "../report.md"]
---

# 20260831t005132z-disc Disposable Root Replacement And Skill Lifecycle Design

## 0. 結論

SpecDock の配布更新は、ファイル単位の所有権照合・差分調停・操作ジャーナルから、**固定された provider-owned root の全量置換**へ変更するのが最も単純で安全である。本 Artifact では、この方式を既存 Option C の具体形として **Option C2 — Disposable Root Replacement** と呼ぶ。

採用する境界は次のとおりである。

- 利用者データである `spec-dock/initiatives/**` と、その配下の Artifact は永久に update / uninstall の対象外とする。
- `spec-dock/active/**`、`spec-dock/.agent/**`、dashboard、tree / deps 図、ADR mirror などの生成物は再生成可能な projection とし、配布差分の所有管理をしない。
- provider が所有する `spec-dock/scripts`、`spec-dock/docs`、`spec-dock/templates`、`spec-dock/system` は disposable root とし、update では各 root の中身を残さず全量置換する。
- disposable root 内の利用者編集は保存対象にしない。この非保証を public contract として明示する。
- `.agents/skills` 全体は共有領域なので削除・置換しない。SpecDock が所有する固定 skill slot だけを root 単位で置換する。
- 通常 uninstall は provider tooling と ownership を証明できる固定 skill slot だけを削除し、spec history を削除しない。
- 全操作の自動 rollback、per-file checkpoint resume、cross-intent recovery は通常 product contract から外す。失敗後は外部 installer の同一 command を再実行して収束させる。

これは「安全性を捨ててテストを減らす」案ではない。安全性の対象を **利用者データと共有領域の境界**に限定し、provider 内部の過去状態を自動保存・復旧する責務を廃止する案である。

## 1. Inputs

- `20260830t234548z-research-provider-test-suite-root-cause-analysis-and-redesign.md`
- `20260830t235429z-disc-provider-test-strategy-simplification-decision-analysis.md`
- accepted ADR `20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md`
- current implementation:
  - `src/spec_dock/managed_distribution.py`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/managed_distribution.json`
  - `src/spec_dock/assets/spec_dock/{scripts,docs,templates,system}`
  - `src/spec_dock/assets/install_root/.agents/skills/{spec-dock,spec-dock-grill-with-docs}`
- Product owner の受理内容:
  - Initiativesとその配下のArtifactsは利用者データとして残す。
  - 再生成できるprojectionをinstall / updateの差分管理対象にする必要はない。
  - provider-ownedなscripts / docs / templates / systemは古い内容を削除して全量交換できる。
  - skillは共有領域のため、他skillを壊さずに追加・更新・削除する最小状態が必要である。

## 2. なぜ現行方式が重いのか

前段調査では、2,708 tests の Full Regression が約99分の wall time と約5.51 shard-process-hoursを使い、通常 gate だけでも `1567 passed, 1141 skipped in 650.55s` だった。`managed_distribution.py` は22,332行で provider Python source の約44%を占め、主要distribution testsは約35,000行に達していた。

この規模は、配布物の中身そのものが複雑だからではない。現行 engine が次の問いにファイル単位で回答しようとしているためである。

1. このpathはproviderが今所有しているか。
2. 過去のどのversion / SHAと一致するか。
3. 利用者が変更したか、同じbytesだがinodeが変わったか。
4. symlink、hardlink、FIFO、parent rebindがあるか。
5. update / deprovision / purgeのどのintentで、どのcheckpointまで進んだか。
6. crash後にどのactionから安全に再開できるか。
7. 古いskillを削除してよいか、未知のfileとして残すべきか。

`managed_distribution.json` には、現在配布していない多数のskill pathとhistorical identityが残っている。skill一つの更新でもexact old digestをcatalogへ追加し、provider / projection parityとcollision behaviorを証明する必要がある。これは現行契約に対しては整合的だが、軽量なローカルツールが恒久的に負うべきproduct valueではない。

根本原因は「pytestが遅い」ことではなく、**provider内部の全履歴状態を自動調停するproduct contractが大きいこと**である。したがって、shardを増やす前にcontractを減らす必要がある。

## 3. 所有権モデル

### 3.1 固定分類

| class | path / example | update | uninstall | 利用者編集 |
|---|---|---|---|---|
| durable user data | `spec-dock/initiatives/**`、配下Artifact | 触れない | 触れない | 保持 |
| opaque user / local data | `spec-dock/.workbench/**`、未知path | 触れない | 触れない | 保持 |
| generated projection | `spec-dock/active/**`、`spec-dock/.agent/**`、dashboard、tree / deps、ADR mirror | 配布差分を管理しない | 原則触れない | 再生成可能 |
| disposable provider root | `spec-dock/scripts` | root全量置換 | root削除 | 非保証 |
| disposable provider root | `spec-dock/docs` | root全量置換 | root削除 | 非保証 |
| disposable provider root | `spec-dock/templates` | root全量置換 | root削除 | 非保証 |
| disposable provider root | `spec-dock/system` | root全量置換 | root削除 | 非保証 |
| fixed shared slot | `.agents/skills/spec-dock` | slot root全量置換 | ownership markerが有効な場合だけ削除 | 非保証 |
| fixed shared slot | `.agents/skills/spec-dock-grill-with-docs` | slot root全量置換 | ownership markerが有効な場合だけ削除 | 非保証 |
| shared consumer surface | `.agents/skills` のその他 | 触れない | 触れない | 保持 |
| unresolved shared surface | `.github/workflows/ci.yml` | 別判断まで通常update対象外 | 別判断まで削除しない | 未確定 |

`spec-dock/.gitignore` はinit時のseedとし、その後はconsumer-ownedとする案を第一推奨とする。version表示はper-file catalogではなく、小さなinstallation recordから生成または更新する。

### 3.2 境界の意味

disposable rootは「providerが提供したbytesと一致するときだけ上書きできるroot」ではない。**そのpathの内側はprovider implementationであり、次回updateで全消去され得るroot**である。利用者がprovider実装を改造したい場合はfork / package sourceを変更するべきで、consumer repository内の配布copyをcustomization pointにしない。

一方、共有親である `spec-dock/` や `.agents/skills/` はdisposableではない。親全体を置換するとuser dataやunrelated skillを消すため、削除authorityは固定leaf rootより上へ拡張しない。

## 4. Provider root update protocol

### 4.1 前提

- updaterは置換対象 `spec-dock/scripts` の外側で実行する。installed packageまたは外部 `uvx` processがoperationを所有し、更新中のrepo-local scriptに実行継続を依存しない。
- root allowlistはcodeに固定し、manifestやworkspace fileから任意pathを追加できない。
- target repositoryとroot parentのbindingをoperation開始時と各destructive step直前に `lstat` で確認する。
- root自体がsymlink、non-directory、root外へrebindされた状態なら、子要素を辿らず書込み前に停止する。
- rootの中のindividual file driftは分類しない。root ownershipが成立していれば全量置換する。

### 4.2 手順

1. candidate packageから4 rootの完全なstaging treeを、targetと同一filesystem上に作る。
2. 必須entrypoint、file count、mode、package digestなどcandidate自身の整合性をstaging側だけで検証する。
3. durable / opaque / generated / shared pathがaction listに含まれていないことを確認する。
4. installation recordとroot bindingを照合する。legacy markerのないworkspaceは、有限のone-shot migration preflightを通った場合だけcurrent layoutへ移す。
5. `docs`、`templates`、`system`、`scripts` の順に、各旧rootを削除し、対応staging rootを最終pathへrenameする。
6. `scripts` は最後に置換し、更新操作の途中まで旧repo-local entrypointを残す。
7. fixed skill slotsを後述のcontractで置換する。
8. 最後に単一のinstallation record / ready markerをatomic file replaceし、installed version、schema、candidate digest、固定slot versionを記録する。
9. staging cleanupはbest effortとする。cleanup failureをrollback理由にしない。

directory tree全体のcross-platform atomic swapは約束しない。各rootは削除とrenameの間に短い欠落状態を持ち得て、複数root全体は一つのtransactionではない。その代わり、全stagingを先に完成させ、ready markerを最後に書き、同じupdaterを再実行すればexpected candidateへ収束する。

### 4.3 failure model

| failure point | observable state | recovery |
|---|---|---|
| staging / validation前 | 旧installationがready | stagingを捨てて再実行 |
| root削除前 | 旧installationがready | 再実行 |
| root削除後・rename前 | 一つのrootが欠落 | 外部updaterを再実行 |
| root間 | old / new rootが混在、ready markerは旧 | 外部updaterが4 rootをdesiredへ再置換 |
| scripts置換後・ready前 | repo-local scriptは新、markerは旧 | installed package / `uvx` から再実行 |
| ready後のcleanup | 新installationがready、staging残存 | 成功扱い。後で限定cleanup |
| root type / binding異常 | mutation前にblock | 利用者へ対象と修復手順を表示 |

自動rollbackを設けない理由は、rollback path自体が別のfailure matrix、journal schema、old package compatibilityを生むためである。provider rootが一時的に利用不能になることは許容し、user dataが破損しないことを優先する。

## 5. Skill lifecycle

### 5.1 なぜskillだけ別扱いか

skillは `.agents/skills` というconsumerと他providerが共有する親の下に置かれる。`spec-dock/` 内部rootと違い、親を全量置換できない。しかしcurrent provider sourceは次の2 slotだけである。

- `.agents/skills/spec-dock`
- `.agents/skills/spec-dock-grill-with-docs`

したがって、per-file catalogではなく **固定slot root + 小さなowner marker** で十分である。

### 5.2 marker contract

各managed skill rootには、たとえば `.spec-dock-owner.json` を同梱し、最低限次を持たせる。

```json
{
  "schema_version": 1,
  "owner": "spec-dock",
  "slot": "spec-dock-grill-with-docs",
  "distribution_version": "<version>"
}
```

- marker pathとschemaはprovider sourceに固定する。
- `slot` は実際のdirectory basenameと一致させる。
- markerは削除authorityの証拠であり、任意pathの指定機能を持たない。
- inner file hash、過去の全digest、checkpoint、consumer manifestは持たない。
- markerが欠落・不正・別ownerなら、そのslotを上書きも削除もせずblockする。

### 5.3 install / update / removal

- install: fixed slotがabsentなら、markerを含む完全なrootを配置する。未知の既存rootがあれば上書きしない。
- update: valid markerがあるexact slotのroot全体を置換する。内側のuser editは保存しない。
- current slot removal: uninstallはvalid markerがあるexact slotだけを削除する。
- retired slot: codeに固定された有限のretired-slot allowlistにexact nameを追加し、valid old owner markerがある場合だけ一度削除する。migration window終了後はallowlistとtestを削除する。
- unrelated skill: prefixやname patternで探索せず、一切変更しない。

旧版にmarkerがない現在の2 skill rootについては、一度だけexact current tree identityを確認してmarker付きslotへ移行する。これは恒久的historical identity catalogではなく、期限付きmigration adapterとする。

## 6. Uninstall と purge

通常uninstallのpostconditionは次で固定する。

- 4 disposable provider rootsがない。
- ownership markerを検証できたcurrent / retired SpecDock skill slotがない。
- installation recordがない、またはdeprovisionedを示す。
- `spec-dock/initiatives/**` とnested Artifactsはbyte-identicalである。
- `.workbench/**`、generated projections、unknown paths、unrelated skillsは変更されない。

`--remove-specs` は通常uninstall authorityから外す。利用者データを本当に削除する機能が必要なら、別名のpurge command、独立した明示確認、別Issueとして設計する。update / retry / uninstallからpurgeへ権限昇格しない。

## 7. テスト設計への効果

### 7.1 廃止できる契約

- provider root内のper-file modified / unknown / same-bytes-new-inode判定
- historical file digestの無期限catalog
- actionごとのpre / post SHAとcheckpoint resume
- cross-intent journal recovery
- provider file preservation witness
- provider root内のobsolete fileを一件ずつ判定・削除するmatrix
- automatic whole-operation rollback / quarantine restoration
- 通常uninstallからのspec-history purge

### 7.2 残すsecurity invariant

- fixed root allowlistから外へ書かない・削除しない。
- symlink root / parent rebind / unexpected typeで書込み前に停止する。
- durable user dataとunrelated skillを変更しない。
- candidate stagingが不完全ならtarget mutationを開始しない。
- ownership markerのないskill slotを上書き・削除しない。
- failure後の再実行でdesired candidateへ収束する。

### 7.3 最小portfolio

| owner | representative proof | 目安 |
|---|---|---:|
| pure contract | path classification、fixed allowlist、marker validation、action order | 数十test |
| filesystem service | fresh install、whole-root update、obsolete inner file消滅、user data不変、mid-root fault再実行、symlink block | 10〜20 scenarios |
| skill service | absent install、owned update、unknown collision、unrelated preserve、retired slot removal | 5〜10 scenarios |
| CLI adapter | representative text / JSON / exit mapping | 各public command 1 happy + 1 blocked |
| package smoke | built wheelでinit → update → uninstall | Linux 1系列、macOS差分のみ |

test countを先にquota化しないが、全historical checkpoint × file kind × intentの直積は作らない。rootごとのfault injectionとownership boundaryのrepresentative caseへ変える。新testが旧contractを証明した時点で、旧testを「念のため」残さず同じchangeで削除する。

## 8. 既存accepted ADRとの関係

`20260818t031610z-adr` は、現行product contractを前提として、per-file identity、operation journal、journaled forward recovery、deprovision / purgeの共通engineを採択した。この判断は当時の安全要件には整合するが、Epic #384の根本原因分析とProduct ownerの方針により、配布更新・tooling deprovision・skill projectionについては前提が変わった。

新ADRは次をsupersedeする。

- unified per-file action grammarをすべてのdistribution lifecycleへ使う判断
- operation journalとarbitrary checkpoint forward recoveryを通常updateに要求する判断
- managed deprovisionとspec-history purgeを同じengineで扱う判断
- skillのhistorical file identityを無期限に持つ判断

一方、次は維持する。

- destructive targetを固定境界へ限定する。
- root binding / symlink / unknown shared contentでfail closedする。
- user data削除には通常tooling operationとは別の明示authorityが必要である。
- whole-operation rollbackを約束しない。

## 9. 実装Issue候補

Issueはまだ作成しない。受理済みADRを基準に、次の4 outcomeへ分けるのが最小である。

1. **Disposable provider root cutover**: ownership classifier、staging、4 root replacement、installation record、legacy one-shot migrationを実装し、旧per-file engineの該当routeとtestsを削除する。
2. **Fixed skill slot lifecycle**: owner marker、2 current slots、有限retired slots、uninstall behaviorを実装し、historical skill file catalogとtestsを削除する。
3. **Tooling-only uninstall and public compatibility**: `--remove-specs`の廃止 / 独立purge、CLI / JSON移行、`.github/workflows/ci.yml`の所有方針を確定・実装する。
4. **Test portfolio and CI cutover**: contract inventoryを新boundaryへ移し、旧journal / parity / ledger / shard machineryを削除し、単一process10分budgetをmerge gateにする。

Issue 1と2は独立して受け入れ可能だが、同じproduction writerが順序立てて行う。Issue 4は1〜3のproduction contract cutover後に実行する。

## 10. 未決事項

次は今回の受理範囲から推測で確定しない。

- `.github/workflows/ci.yml` をinit-once consumer-ownedとするか、reusable workflow参照へ変えるか。
- legacy direct updateを何version / 何日支援するか。
- `--remove-specs` を完全削除するか、独立purge commandとして残すかのCLI移行方法。
- `.gitignore` の既存consumer customizationと初回seedの衝突規則。
- package / sdist / macOS smokeのrelease triggerとpublic deprecation window。

これらは4 root置換の採否を再度未決にするものではない。各実装Issueの開始前に、影響する項目だけProduct判断を得る。

## 11. Reflection

- 本分析のdurableな判断を `20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md` に採択ADRとして記録した。
- Epic Requirementのownership、update、uninstall、skill要件をOption C2へ更新した。
- Epic Designのstate modelとfailure modelを、per-file journalからroot replacement + rerun convergenceへ更新した。
- Epic Planを4 outcome候補へ再構成し、旧immutable-payload前提を外した。
- 人間向けの補助説明は `disposable-root-replacement-and-skill-lifecycle.html` にまとめる。
