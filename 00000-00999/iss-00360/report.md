---
種別: 実装報告書（Issue）
ID: "iss-00360"
タイトル: "Cut Over Distribution and Retire Legacy Workflow Surfaces"
関連GitHub: ["#360"]
最終更新: "2026-08-16"
親: ["epic-00356", "init-local-00003"]
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

## Outcome

Issue 360の配布切替、旧workflow面の物理退役、既存consumerの保守的更新、uninstallのno-follow安全化、retry / root identity、provider・dogfood・archive parity、docs migrationを実装し、対象スイートを通過させた。S00〜S95の実装証跡と決定台帳を更新し、最終品質ゲートで検出したP0/P1を段階的に修正した。`7cb830ad8ccf1700c408abbd17f5261a53aa0214` では、uninstall marker最終化後にfallibleなworkspace root rmdirを行わないよう処理を単純化し、成功時はmarkerを除去した空の`spec-dock`境界を残すことで、terminal cleanup failureとmarker再発行 failureの複合状態でもdurable retry admissionを失わないようにした。`a30afda01b8a2307c8a55bfa4ccb758021b41620` では、partial uninstallのJSON / text診断からcredential・host absolute path・raw exceptionを除外し、relative failed path、phase、last completed phase、retry commandを安定した契約として出力するようにした。`cc1b42a4742e5d5c9efca042f29c506258013822` では、成功した`uninstall --remove-specs`後に残る空の`spec-dock`境界をFresh admissionとして安全に再初期化できるようにし、明示targetのpartial retry診断で元のtarget文脈を保持するようにした。`34e77724b5af9b1eb742185c3eb131f4c9944606` では、配布 marker のheld-parent identity再検証、distribution/uninstall retryの元target伝搬、特殊パスを含むargv-safeなretry commandと実行回帰を追加した。`6d06578511e8b1d54c997e25d5f19994ed50f1bd` では、managed scaffoldの全managed rootを再帰的に安全検査し、providerがregular fileを期待するexact pathのdirectory・symlink・special type・hard linkを、marker公開およびrecursive refresh前にzero-writeで停止する統合回帰を追加した。`3bb7a77c` では、managed scaffold・generated active・initiative・Workbench境界を配布manifestのmutation前重複検査で保護し、`5488dc75882ce9f0fd2d1a20f3c4e23ecb1a8a48` では、uninstall後に管理対象が完全に消えた空境界だけを安全な再実行として認め、管理対象が残る空workspaceのupdate/uninstallは引き続きzero-writeで拒否するようにした。Fresh / update / uninstallの既存no-follow境界、partial diagnostics、同一package retry収束も維持している。

### Latest P1 repair candidate (2026-08-14)

* `src/spec_dock/managed_distribution.py`のrecognized regular upgradeを同一親directoryのstaging fileへ書き込み、no-follow identity再検証後にatomic swapで公開する方式へ変更した。staging write失敗時は既存targetを保持する。
* Current bytesが一致してもprovider modeと不一致の場合、`update` / `init --force`で`upgrade`へ分類し、expected modeを修復する。Freshの既存pathは従来どおり無変更である。
* Fresh initは`spec-dock/.distribution-retry.json`をapply前に作成し、通常の同じ`spec-dock init .`をforward retryとして再開できるようにした。marker parent作成後はroot ctimeを再取得してapply snapshotを再構築する。
* partial failureの診断にrelative target、`last_completed_phase`、operation別retry commandを追加し、credentialやhost absolute pathを再出力しない。
* 修正テスト: atomic staging failure、mode repair、Fresh same-package retry、partial failure diagnostic。

### Latest P1 repair candidate 2 (2026-08-14)

* apply時にplan取得後のprovider bytes / modeを再観測し、計画時modeと不一致なら公開せず停止する。regular upgradeのold staging cleanupはstrict化し、既知のregular / symlink stage identityだけをdescriptor-relativeに再検出・cleanupして同一package retryを収束させる。
* markerを公開した後のtemporary cleanup失敗でも、marker実体を再確認してpartial failure診断へ遷移させる。recognized updateの`spec-dock/.gitignore`はprovider bytesとのidentityをpreflightとwrite直前にno-follow再検証し、未知内容を上書きしない。
* 修正テスト: provider mode rebind、known stale stage retry cleanup、unknown scaffold `.gitignore` preserve-and-block、retry identity recheck、marker publish partial diagnostic。

### Latest P1 repair candidate 3 (2026-08-14)

* Fresh scaffold pruningからrepository外側の`.github/workflows/spec-dock-close.yml`無条件unlinkを除去し、ownership proofのない同名file / symlinkを保持する回帰を追加した。obsolete pathのpruneはmanaged distributionのproven identity分類へ限定する。
* 既知staging cleanup後にactionと後続actionのtarget snapshotを再観測し、親directory ctime更新を反映して同一package retryが収束するようにした。regular / symlink両方のprivate stage prefixをretry cleanup対象に含めた。
* 修正テスト: Fresh legacy-named workflow file/symlink preservation、same-parent later-action snapshot refresh、known stale symlink stage retry cleanup。

### Latest P1 repair candidate 4 (2026-08-14)

* `init --force` のadmissionがFreshを返す空targetでは、recognized workspace installerへ進まずFresh distributionへ分岐させ、marker parent未作成によるmaterialization前失敗を防止した。
* 修正テスト: 空targetへの公開 `init --force` がFresh scaffoldとversion markerを作成する回帰。

### Latest P1 repair candidate 5 (2026-08-14)

* stale-stage cleanupを`apply_distribution_plan`のretry opt-inへ限定し、通常Fresh / updateでprefixとbytesだけが一致する未知siblingを削除しないようにした。生成stage名はtarget pathと計画identityから安定導出し、retry時はその計画由来の名前だけを回収する。
* obsolete/historical ownershipのdigest照合ではmodeを無視し、modeはCurrent assetのpostconditionおよびmode修復判定だけに利用する。production manifestのmode付きidentityとchmod driftの回帰を追加した。
* 修正テスト: unknown stage-like sibling preservation、same-parent retry snapshot refresh、symlink stage cleanup、historical mode-only drift prune。

### Latest P1 repair candidate 6 (2026-08-14)

* retry markerにexclusive create直後のstage target、filename、device / inode / `ctime_ns`、file typeを記録し、retry cleanupはその作成時identityと計画由来のstage名が一致するentryだけを削除するようにした。記録のない同名stage-like siblingは保持し、collisionとして停止する。
* 修正テスト: 未記録の正確なstage名collisionを二回のapplyで保持する回帰、regular / symlink stale stageの記録済みidentity cleanup、marker schemaのstage ownership受理。

### Latest P1 repair candidate 7 (2026-08-14)

* Fresh createのstaging write / fchmod / verify / publish例外を一つのcleanup境界で処理し、例外発生後に取得したno-follow identityと一致するstageだけを回収する。既存targetを変更するupgrade経路は従来どおり保持する。
* Fresh retryではroot Workbench親をseed判定の前後で検証し、既存READMEが外部symlink先にあってもcopyを成功扱いにせずpreserve-and-blockする。provider assetの欠損診断は論理relative pathだけを返す。
* 修正テスト: Fresh create staging write failure cleanup、外部READMEを持つWorkbench symlink retryのzero-external-write / marker保持 / 修復後収束。

### Latest P1 repair candidate 8 (2026-08-14)

* atomic swap後の旧target stage ownershipをmarkerへ再束縛する際、marker更新が失敗しても旧target stageを即時にstrict cleanupし、staleなpre-swap markerがmanaged payloadを隠したまま成功扱いにならないようにした。retry時にmarker ownership identityが現物と一致しない場合は、別の一致recordがない限りfail-closedで停止する。
* retry cleanupのhistorical identity集合をdirect historical、recognized workspace anchor、obsolete identityへ広げ、trusted consumer manifest claimは現行classifierと同じmanifest identity検証で許可する。recognized anchorの収集とtrusted claim由来stage cleanupの回帰を追加した。
* 修正テスト: marker更新失敗後のrebound stage cleanup、trusted manifest claim由来stageのsame-package retry、recognized anchor identity収集。

### Latest contract-test alignment (2026-08-14)

* `tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_keeps_initiatives_by_default` の期待値を、Issue 360のpreserve契約どおり所有権証明のないlegacy-named workflowを保持する内容へ更新した。実装コードは変更していない。
* 修正テスト: `uv run pytest --run-full-regression -q tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_keeps_initiatives_by_default` → `1 passed`。

### Latest P1 repair candidate 9 (2026-08-14)

* regular upgradeのstage writeが部分的に進んでから失敗した場合、close前にstage fdのno-follow identityを再取得してからownership-checked cleanupするようにした。作成時ctimeが更新されたstageを古いsnapshotで誤って残さず、同一packageのforward retryを停止させない。
* 回帰テストを「write前に即時raise」から「partial bytesを書いてからraise」へ強化し、既存targetの保持とstage残骸cleanupを確認した。
* S95では`0f56c0063e07e281200961c7f1dd274874569d0b`の全回帰、固定点の全回帰、現行failure node id 27件の固定点subset再実行を行い、27件すべてが固定点でも再現する`approved-no-op`であることを [`s95-full-regression-ledger.json`](artifacts/s95-full-regression-ledger.json) にpath・owner・follow-up付きで記録した。旧authoring-pack / wrapper専用テストはS40Aの物理退役として本差分から削除し、current-only failureは残していない。

### Latest P1 repair candidate 10 (2026-08-14)

* regular upgradeの部分書き込み後、close前に取得したstageのno-follow device / inode / `ctime_ns` / typeをretry markerへ再記録し、cleanup失敗をstrictに通知するようにした。markerの正確な所有identityが一致するstageはpayloadがpartialでも同一package retryで回収でき、unknown siblingは従来どおり触らない。
* S40Aで退役したauthoring-pack / ChatGPT wrapperの専用テストとmanual validatorテストを物理削除し、S95でcurrent-only failureが0件になるよう回帰選択を現行cutover suiteへ揃えた。
* 修正テスト: partial bytes + stage unlink failure後のmarker identity再記録とretry収束、旧wrapper / manual validator testの退役。

### Latest P1 repair candidate 11 (2026-08-14)

* Fresh createの部分書き込み後、close前に取得したstageのno-follow device / inode / `ctime_ns` / typeをretry markerへ再記録し、cleanupをstrictに実行するようにした。markerの更新が失敗してもcleanupを継続し、cleanup失敗時は正確な所有identityを次回のsame-package retryへ引き渡す。
* Fresh createのpartial bytes + stage unlink failureを同時に再現する回帰テストを追加し、更新済みmarkerでstale stageを回収してFresh scaffoldへ収束することを確認した。
* S95 v13では`a6c420985bb7cd9d2e04984e3825ba62383229fe`の全回帰、固定点subset再実行を行い、27件すべてが固定点でも再現する`approved-no-op`、expected-retirement 0件、比較未完了0件となった。

### Latest P1 repair candidate 12 (2026-08-14)

* `_assert_pending_snapshot_stable`が、全action preflight後に外部processで作成された未登録parentを`created_parent_bindings`へ新規登録しないよう変更した。SpecDock自身が`_bind_created_parent_identities`で作成・束縛したparentだけを後続actionへ引き渡し、未所有parentの事後出現はidentity errorで停止する。
* 先行actionの実行後、後続actionの当初欠落parentを外部作成する競合を再現する回帰テストを追加し、先行actionの結果を保持したまま後続managed fileを作成しないことを確認した。
* S95 v14では`48779d16935546d818e003cf33a7b2e97d0832c8`の全回帰、固定点subset再実行を行い、27件すべてが固定点でも再現する`approved-no-op`、expected-retirement 0件、比較未完了0件となった。

### Latest P1 repair candidate 13 (2026-08-15)

* `_observe_target`が最初の欠落componentで停止せず、残りの欠落parentもsnapshotへ記録するよう変更した。先行actionが作成した上位parentの下に外部processが下位parentを作成した場合も、未登録identityとして後続mutation前に停止する。
* Current / historical / obsoleteのsymlink prune・upgradeでlink countを確認し、hard-linked symlinkは`hard-link-mutation-unsafe`として分類してzero-writeでblockする。regularの既存hard-link保護は維持した。
* recognized update / `init --force`でdistribution planやretry markerを作成する前に、Freshと同じ全scaffold source catalog（managed directories、`.gitignore`、root Workbench seed）をpreflightする。
* 回帰テスト: 多段parent競合、current / historical hard-linked shortcut、recognized updateの欠落scaffold sourceによるzero-write停止。S95 v14現行HEADでは`27 failed, 1941 passed, 516 skipped`、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。

### Latest P1 repair candidate 14 (2026-08-15)

* Fresh開始時の`spec-dock/`境界作成をheld root FD配下の相対no-replace `mkdir`へ移し、preflight後に出現したworkspaceをreplacement rootへ書かずfail-closedで停止するようにした。
* root Workbench seedを`exists()`のbool判定からno-follow identity / provider bytes / modeの分類へ変更した。Freshはmissingならseed、provider-identicalなsingle-link regularならadopt、その他はpreserve-and-blockとし、recognized update / `init --force`ではsymlinkを含むWorkbenchを検査・変更しない。
* 回帰テスト: provider-identical Fresh retryのadopt、recognized updateのsymlinked root Workbench preserve、Fresh root rebind中のreplacement zero-write。S95 v15では`27 failed, 1944 passed, 516 skipped`、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。

### Latest P1 repair candidate 15 (2026-08-15)

* `_preflight_fresh_spec_dock_assets`で必須nested runtime `spec_dock/scripts/spec-dock`をno-follow regular、single-link、executable modeとして検証し、Fresh / recognized updateのmarker・distribution mutation前に欠落・不正sourceを拒否するようにした。
* 回帰テスト: recognized updateでnested runtimeが欠落するケースと、実行bitが失われたsource packageのzero-write停止。S95 v16では`27 failed, 1946 passed, 516 skipped`、v15とのfailure node集合差分0件、固定点subset比較は同一failure behavior 27件。

### Latest P1 repair candidate 16 (2026-08-15)

* 初回`spec-dock/.distribution-retry.json`の公開前にwrite / sync / linkまたはowned temp cleanupが失敗した場合、tempのdevice / inode / regular・single-link identityを再検証して一度だけpayloadを再発行するようにした。valid markerを公開できた場合は、元の失敗をpartialとして返しつつ、次回の通常`spec-dock init .`が同一package・同一rootのforward retryとしてadmitできる状態を残す。
* 回帰テスト: Fresh markerの初回write失敗とtemp cleanup失敗を同時注入し、marker公開、temp residueなし、通常init retryの成功を確認した。S95 v17では`27 failed, 1947 passed, 516 skipped`、v16とのfailure node集合差分0件、固定点subset比較は同一failure behavior 27件。

### Latest P1 repair candidate 17 (2026-08-15)

* 初回distribution markerの新規公開をhard-link + unlinkからdescriptor-relativeなno-replace renameへ変更し、公開後の一時ファイル削除失敗で`st_nlink=2`のmarkerが残る経路を除去した。markerは公開時点でsingle-link regular fileとなり、同じpackageのadmissionを阻害しない。
* 回帰テスト: publish競合時のrace winnerを保持し、初回publish fault injection後もmarkerのsingle-link・temp residueなし・通常init retryを確認した。

### Latest P1 repair candidate 18 (2026-08-15)

* regular upgradeのatomic swap後にstage ownership再記録が失敗した場合、current stage identityのmarker再記録を一度再試行し、cleanup失敗も限定的に再試行してからpartial errorを返すようにした。recorder / cleanupを同時注入しても、再記録またはownership-checked removalの一方が成立し、次回same-package retryがstage identity mismatchで停止しない。
* 回帰テスト: post-swap recorder failureとstage cleanup二回失敗を同時注入し、current stage identityを保持したretry markerで次回cleanupが収束することを確認した。

### Latest S95 v22 evidence (2026-08-15)

* no-replace publish seamへfault-injection hookを追従させ、v18で一時unlink / `os.link` hookが無効化していた2テストを修正した。
* S95 v22は `27 failed, 1949 passed, 516 skipped`。v19とのfailure node集合差分は0件（new 0 / missing 0）、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。

### Latest P0/P1 repair evidence (2026-08-15)

* managed scaffoldの再帰uninstallで、保持したdirectory FDだけを信頼して外部へ移動されたtreeを削除しないよう、各再帰mutation直前に可視パスのno-follow root binding（device / inode）とentry identityを再検証する実装を `91f8b824e1a6839ee8e81030b6ae20f76b143fa1` に追加した。rename fault injectionで外部treeを削除しないことを確認した。
* atomic regular-file retryで一時ファイルをO_TRUNC付きで開く前にidentityを検証できるよう、O_TRUNCを外してfstat後にftruncateする実装とhard-link差し替え回帰テストを `9b9e53e968f48c5883a04ef4fbd71aaac096aca8` に追加した。差し替え先外部inodeが不変であることを確認した。
* uninstall retry markerのwrite/fsync失敗時に作成inodeをidentity確認して除去し、通常rerunでmarkerを再作成できるようにした実装を `b0763b5fa743a6f11b14718eb5cd65b17926134b` に追加した。write failure注入後のmarker残留なし・同一package retry成功を確認した。
* uninstall retry markerの既存競合時にdescriptorからcanonical payload・stable identityを検証し、不完全markerを再利用しない実装を `194b793acb015a9c564bde0aa1dc480b8e188b84` に追加した。partial markerのreuse拒否回帰を確認した。
* S95 v29は実装tree `194b793acb015a9c564bde0aa1dc480b8e188b84`に対して `27 failed, 1956 passed, 516 skipped`（12分34秒）。v28とのfailure node集合差分は0件（new 0 / missing 0）、S95 ledgerの27件と完全一致、current-only failure 0件、比較未完了0件である。
* S95 v30は配布面の運用指針と回帰テストを含むbranch tip `68ee1c67d7d770e7684751f7f07289a80e27f80a`に対して `27 failed, 1957 passed, 516 skipped`（12分34秒）。v29とのfailure node集合差分は0件（new 0 / missing 0）、S95 ledgerの27件と完全一致、current-only failure 0件、比較未完了0件である。
* S95 v32はFresh mode mismatch保護と既存hard-link read-only adoption契約を含む実装tree `774e126124bd5a297c4ff193b40e0c6e11061888`に対して `27 failed, 1958 passed, 516 skipped`（12分39秒）。v30とのfailure node集合差分は0件（new 0 / missing 0）、S95 ledgerの27件と完全一致、current-only failure 0件、比較未完了0件である。
* marker削除失敗時のdiagnostic phaseを`marker-finalization`へ分離し、targetを`spec-dock/.distribution-retry.json`へ固定する実装とFresh / update / init-forceの回帰テストを `5fe6ddb6543fc896e54bc110e67da1bfb53c7663` に追加した。
* S95 v33はmarker-finalization修正を含むbranch tip `fa5b354c8a70f63d87d0e4e44240d920a36c0e9b`に対して `27 failed, 1961 passed, 516 skipped`（12分39秒）。v32とのfailure node集合差分は0件（new 0 / missing 0）、S95 ledgerの27件と完全一致、current-only failure 0件、比較未完了0件である。

### Latest S95 v34 evidence (2026-08-15)

* Fresh uninstall完了時に、生成された`spec-dock/active`と`spec-dock/.agent`をboundedな空directory cleanup対象へ明示的に含め、retry markerのfinalization後にcleanup / postcondition verifyを再実行する実装を`415b0564a`に追加した。Fresh `uninstall --apply --remove-specs`でmanaged rootを残さない回帰テストと、既に除去済みworkspaceの再実行期待値を`f99340169`で整合させた。
* S95 v34はbranch tip `f99340169b9d2e0352b9422b3376a4e2f9fd3f1a`に対して `27 failed, 1966 passed, 516 skipped`（12分38秒）。v33とのfailure node集合差分は0件（new 0 / missing 0）、S95 ledgerの27件と完全一致、current-only failure 0件、比較未完了0件である。

### Latest P1 repair candidate 19 (2026-08-15)

* Uninstallのsymlink identityにdevice / inode / ctime / link count / targetを含め、同じtargetへ差し替えたsymlinkをmutation直前にfail-closedで停止するようにした。
* Generated state・managed assetのhard linkをmarker作成前に`preserved`としてblockし、uninstall applyは最初の安全性失敗後のremovalを`pending`として停止するようにした。
* Generated root配下をno-followでbottom-up走査し、入れ子の空directoryをbounded cleanupし、残存・検査失敗をpartial failureとして扱うようにした。Partial resultへphase、last completed phase、pending paths、relative retry commandを追加した。
* 回帰テスト: 同一target symlink差し替え、generated hard link事前停止、失敗後pending、入れ子generated directory cleanup、phase/retry JSONを追加した。

### Latest S95 v35 evidence (2026-08-15)

* S95 v35はuninstall安全性修正を含むbranch tip `e6dfe3aa2733f906786bb8a409c0acf22c6c2038`に対して `27 failed, 1969 passed, 516 skipped`（12分45秒）。v34とのfailure node集合差分は0件（new 0 / missing 0）、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件である。

### Latest P1 repair candidate 20 (2026-08-15)

* Uninstall対象のsymlinkをno-followで取得する際、link countが1でないsymlinkを`unsafe` identityとして分類し、hard-linked symlinkをmarker作成前にblockするようにした。
* `spec-dock/.agent/**` のsymlinkをgenerated stateの事前block対象へ追加し、apply後のsymlink拒否によるpartial stateを防止した。repo-root shortcutもunsafe identityを事前分類する。
* `--remove-specs` の `spec-dock/initiatives` をmanaged treeと同じno-follow再帰安全走査へ接続し、descendant symlink・hard link・special entry・検査失敗をmarker前にpreserve-and-blockするようにした。
* 回帰テスト: hard-linked generated symlink、`.agent` symlink、unsafe `initiatives` descendantのzero-write blockerを追加した。

### Latest S95 v36 evidence (2026-08-15)

* S95 v36はuninstall preflight修正を含むbranch tip `e9759ba245643e2572a9917d48d7db43e5d26b4f`に対して `27 failed, 1972 passed, 516 skipped`（12分49秒）。v35とのfailure node集合差分は0件（new 0 / missing 0）、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件である。

### Latest P1 repair candidate 21 (2026-08-16)

* uninstallの空directory cleanupと2回目のpostcondition verifyをretry marker最終化より前に完了させ、markerが存在する状態で全managed payloadの除去結果を確認するようにした。marker最終化後のterminal workspace root `rmdir`だけを最後の操作に分離し、その操作が失敗した場合はmarkerを再発行して次回の同一package retryへ引き渡す。
* 既に除去済みのspec history rootは「期待どおり欠落」として再試行可能に分類し、terminal cleanup failure後のmarker保持・phase診断・通常uninstall retry収束を回帰テストで固定した。

### Latest S95 v37 evidence (2026-08-16)

* S95 v37はterminal workspace cleanup後のmarker復旧修正を含むbranch tip `6315c9d4fc0267ca3b4434cfc0783e245c6563eb`に対して `27 failed, 1973 passed, 516 skipped`（12分36秒）。既存S95 ledgerのfailure node 27件と一致し、current-only failure 0件、expected-retirement 0件、比較未完了0件である。

### Latest P1 repair candidate 22 (2026-08-16)

* uninstall marker最終化後のworkspace root rmdirを廃止し、全remove actionとpostcondition verifyが完了した後はmarker除去だけでcompleteとするようにした。これによりmarker削除後にfallibleなfilesystem mutationが残らず、terminal cleanup failureとmarker publish failureの複合状態でretry admissionを失う経路を閉じた。
* 成功時はmanaged payloadと生成stateをbounded cleanupした空の`spec-dock`境界を保持し、markerは除去する。この空境界はownership markerではなく、次回Fresh admissionを誤認させないための無害なboundary residueとして扱う。回帰テストでmarker除去後にroot rmdirが呼ばれないことを確認した。

### Latest S95 v38 evidence (2026-08-16)

* S95 v38はmarker最終化後のfallible root cleanupを除去したbranch tip `7cb830ad8ccf1700c408abbd17f5261a53aa0214`に対して `27 failed, 1973 passed, 516 skipped`（12分37秒）。v37とのfailure node集合差分は0件（new 0 / missing 0）、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件である。

### Latest S95 v39 evidence (2026-08-16)

* S95 v39はpartial uninstall診断のsanitization / recovery contract修正を含むbranch tip `a30afda01b8a2307c8a55bfa4ccb758021b41620`に対して `27 failed, 1975 passed, 516 skipped`（12分36秒）。v38とのfailure node集合差分は0件（new 0 / missing 0）、現行の27件を`--lf`で再実行してledgerのfailure node集合と一致し、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件である。今回追加したuninstall診断テストを含む変更対象スイートはpassした。

### Latest P1 repair candidate 23 (2026-08-16)

* 成功した`uninstall --remove-specs`後に残る完全に空の`spec-dock`境界を、通常の`init` / `init --force` / `update`がFreshとして安全に再初期化できるようにした。version markerやmanaged payloadを含む非空の未認識workspaceは従来どおりfail-closedで保持する。明示targetのpartial uninstall診断は、host absolute pathやraw exceptionを露出せず、caller CWDからの相対targetと同じtargetを使うretry commandを返す。回帰テストでremove-specs後の再初期化と明示target retryを固定した。

### Latest S95 v40 evidence (2026-08-16)

* S95 v40は空のpost-uninstall boundary再初期化修正と旧テスト期待値更新を含むbranch tip `ec36ef5ca0b56755f90be6ba2b7be6b3b87d0fc8`に対して `27 failed, 1976 passed, 516 skipped`（12分43秒）。v39とのfailure node集合差分は0件（new 0 / missing 0）、現行の27件を確認し、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件である。追加のIssue 360 focused regressionとarchive distribution integrationはpassした。

### Latest P1 repair candidate 24 (2026-08-16)

* distribution markerの削除をheld parent directory descriptor経由に限定し、unlink直前にregular-file identity（device / inode / mode / link count / ctime）を再検証して、差し替えられたmarkerを削除しないようにした。distribution partial failureのretry commandへ開始時targetを伝搬し、uninstallを含むretry commandはshell/argv-safe quotingと先頭hyphen用`--` terminatorを使う。特殊targetで表示commandをargvへ戻して同一targetへ再実行する回帰を追加した。

### Latest S95 v41 evidence (2026-08-16)

* S95 v41はmarker identity再検証、distribution/uninstall retry serialization、特殊target回帰を含むbranch tip `34e77724b5af9b1eb742185c3eb131f4c9944606`に対して `27 failed, 1979 passed, 516 skipped`（12分40秒）。v40とのfailure node集合差分は0件（new 0 / missing 0）、固定点subset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件である。Issue 360 focused suiteは`302 passed, 468 skipped`、archive distribution integrationは`13 passed`、通常テストは`1013 passed, 1509 skipped`である。

### Latest P0 repair candidate 25 (2026-08-16)

* Managed scaffoldのprovider asset pathを全件preflightし、regular fileを期待するexact pathがdirectory・symlink・special type・hard linkへ変化している場合は、retry marker作成およびrecursive refresh前に停止するよう修正した。managed root内の未知entryもsymlink・special type・hard linkを拒否し、各rootのrecursive replacement直前にtarget identityを再検証する。`spec-dock/docs/README.md`を利用者データ入りdirectoryへ置き換えたupdate回帰では、sentinelとconsumer snapshotが不変のまま終了する。

### Latest S95 v42 evidence (2026-08-16)

* S95 v42はmanaged scaffold exact-path structural blockerのzero-write修正を含むbranch tip `6d06578511e8b1d54c997e25d5f19994ed50f1bd`に対して `27 failed, 1983 passed, 516 skipped`（13分53秒）。現行failure node 27件はS95 ledgerおよび固定点subsetと完全一致し、current-only failure 0件、expected-retirement 0件、比較未完了0件である。Issue 360 focused suiteは`187 passed`、通常テストは`1013 passed, 1513 skipped`。証跡更新後のclean treeでarchive distribution integrationも`13 passed`となった。

### Latest P1 repair candidate 26 (2026-08-17)

* Current Artifactを6種へ限定し、旧discussion / draft作成契約、profile template routing、専用CLIテストを物理退役した。Historical Artifactは既存文書のparse / validate / preserve用途だけを残し、provider assets、dogfood projection、rules docs、testsを同一hard-cutover契約へ同期した。実装コミットは`c6beb7663665eb98a7488c6a938fc0bb02a773c3`である。

### Latest S95 v47 evidence (2026-08-17)

* cleanな実装コミット`c6beb7663665eb98a7488c6a938fc0bb02a773c3`に対するfull regressionは`26 failed, 1942 passed, 498 skipped`（15分20.09秒）。解消した旧scaffold docs failureを除く26件は、固定点`a6ded0d9a838b40cdcd741fa473cd264b801f245`でも同一failure behaviorの`approved-no-op`である。ledgerだけを更新したevidence-only HEAD `8456ecd16a0c7a10f4e8b3478754ce44bd3dc4f2`に対してcampaign controllerが再実行した結果も、同一の`26 failed, 1942 passed, 498 skipped`（15分18.54秒）としてexact-set verifierを通過した。

### Latest P1 repair candidate 27 (2026-08-17)

* managed scaffold rootのpath-based `shutil.rmtree`を廃止し、repository root、parent chain、対象directoryを`O_NOFOLLOW` descriptorで保持したfd-relative recursive removalへ移行した。descriptor open後にvisible directoryを差し替えるfault injectionでは、置換先sentinelを削除せずidentity driftで停止する。生成active directory fallbackも同じ安全経路へ統合し、retired scaffoldはコピー前除外とfd-relative exact-entrypoint削除へ移した。実装コミットは`62bd4855ea9a385d9764f426fe895bc04edddd51`である。

### Latest S95 v48 evidence (2026-08-17)

* cleanな実装コミット`62bd4855ea9a385d9764f426fe895bc04edddd51`に対するfull regressionは`26 failed, 1943 passed, 498 skipped`（15分06.07秒）。failure node集合はS95 v47および固定点subsetの`approved-no-op` 26件と完全一致し、current-only failure 0件、expected-retirement 0件、比較未完了0件である。ledger commitは`5e99e82d1bc6297a976adc2ae55598a258d923eb`。本reportを含むsuccessor review headはself-referential SHAを本文へ埋め込まず、campaign controllerと最終certificateをexact identity authorityとする。

### Latest P1 repair candidate 28 (2026-08-17)

* 所有権を証明できない`spec-dock/current-{initiative,epic,issue}`と`.path` 6件を独立削除処理から共通distribution plannerへ移し、regular file、symlink、directoryの全衝突をmutation前にpreserve-and-blockするよう修正した（`3b3b3c5e898f830c8b37676040eac95ab184dc29`）。さらにprovider assetをplan時のdevice / inode / ctime / mtime / size / modeとSHA-256へapply直前に再照合し、retry marker admissionをempty / preserved workspaceのFresh fast-pathより先に評価するよう修正した（`5edadf743b9ee99416cf7f9c0d93cda9deb39329`）。変更済みversion anchorの既存テスト期待もfail-closed契約へ同期し、最終実装コミットは`c7fa5b46506e6a9ceac75166d8c6f0b9b0d98d17`である。

### Latest S95 v49 evidence (2026-08-17)

* cleanな実装コミット`c7fa5b46506e6a9ceac75166d8c6f0b9b0d98d17`に対するfull regressionは`26 failed, 1964 passed, 498 skipped`（15分24.92秒）。failure node集合はS95 v48および固定点subsetの`approved-no-op` 26件と完全一致し、current-only failure 0件、expected-retirement 0件、比較未完了0件である。通常テストは`1022 passed, 1466 skipped`、managed distributionは`96 passed`、distribution cut-over full laneは`133 passed`、静的解析・format・mypyもすべて成功した。本reportとledgerだけの後続commitはevidence-only deltaとし、campaign controllerと最終certificateをreview headのexact identity authorityとする。

### Latest P1 repair candidate 29 (2026-08-17)

* bounded reviewで検出したempty-directory cleanupの2件を`ddd32f97b994a294cce0133e86a607cec356eb90`で修正した。uninstall cleanupは観測したdirectoryのdevice / inode / ctimeを保持し、no-followで開いたparent / target descriptor、空判定、削除直前identity、削除後visible chainを再検証する。Fresh pre-marker rollbackも、このoperationが作成したworkspace identityと一致する空directoryだけを削除し、同名のuser-owned replacementは保持する。競合回帰を追加したcut-over full laneは`135 passed`、通常テストは`1022 passed, 1468 skipped`、静的解析・format・mypyはpassした。
* S95 ledgerの固定点subset commandを、immutableな`d81a12ef51dcbdf2e162d7480da0d3ba46de9b07`から26 node IDを読み、固定点`a6ded0d9a838b40cdcd741fa473cd264b801f245`でpytest終了コード1とfailure node集合の完全一致を機械判定する実行可能commandへ置換した。一時worktreeでの再実測はshared Git metadataの`Operation not permitted`により未実施であり、既存の固定点26件比較結果を置換していない。現行candidateのfull regressionはcampaign controllerのslow laneでexact SHAに対して再実行する。

### Latest P1 repair candidate 30 (2026-08-17)

* generation 3 bounded reviewの新規P1 3件を`89e801d7614e1edb3d4b7cd3b51d640d3697f258`で一括修正した。managed scaffoldの再帰preflightは`os.walk(..., onerror=...)`の走査失敗を即時blockし、未検査subtreeを含むtree replacementへ進まない。operation lockで保持したroot device / inodeはFresh、recognized update / force、apply uninstallの初回identityへ伝播し、lock後admission前のpathname replacementをmutation前に拒否する。固定点subset verifierは`git worktree add --detach a6ded0...`で実際の固定点treeをmaterializeし、そのworktree内でのみ26 node IDのpytestとexact-set比較を実行するcommandへ更新した。
* 新規root rebind / incomplete walk回帰を含むfocused 5件はpass、distribution cut-over full laneは`137 passed`、通常テストは`1022 passed, 1470 skipped`、静的解析・format・mypyはpassした。ローカル環境ではshared Git metadataへのworktree登録が`Operation not permitted`となるため固定点commandの再実測は行わず、既存の固定点26件比較結果を維持する。successor campaignのslow laneは現行exact SHAのfull regressionを再実行する。

### Latest P1 repair candidate 31 (2026-08-17)

* successor bounded reviewで指摘されたpreserved workspace互換性は、実体が`pathlib.Path`ではなくPython 3.10–3.12でも`follow_symlinks`を受け取る`os.DirEntry`であることを確認した。そのうえで型の誤読を排除しno-follow分類を明示するため、`af90cbd8906cf6ffe3c5eaade6da5dc3f5407b14`で`DirEntry.stat(follow_symlinks=False)`と`stat.S_ISDIR/S_ISREG/S_ISLNK`へ統一した。keep-specs後のreinitとupdate block回帰2件はpassした。
* 同じcommitで、`tests/unit/infra/test_init_update.py`に`_ISSUE_360_RETIRED_LEGACY_SURFACE`でskipされたまま残っていた旧host-adapter / native-shim / planning distribution専用テスト17関数（603行）とskip markerを物理削除した。現行cut-over testは維持され、distribution cut-over full laneは`137 passed`、通常テストは`1022 passed, 1453 skipped`、静的解析・format・mypyはpassした。

### Latest P1 repair candidate 32 (2026-08-17)

* successor generation 2 bounded reviewで検出した二つのfilesystem競合を`0c5532f42a3f5bb702d8ed02dcdb8473b263042a`で修正した。`active/*.path`と`context-pack.md`はpathname `write_text`を廃止し、全parent componentをno-followで開いたFD chainへstaging / publish / retry / cleanupを固定する。Dangling pathfile symlinkをfollowせず、親directoryがopen後にsymlinkへ差し替えられた場合は外部へ一切writeせずidentity mismatchで停止する。従来のmarker publication再試行とforward recoveryもFD-relativeに維持した。
* 新規競合回帰を含むfocused 7件はpass、distribution cut-over full laneは`139 passed`、通常テストは`1022 passed, 1455 skipped`、静的解析・format・mypyはpassした。clean exact-upstream実装SHAに対するfull regressionは`26 failed, 1970 passed, 481 skipped`（15分23.80秒）で、ledger 26 node IDだけのcache無効再実行も`pytest_exit=1 expected=26 failed=26 exact=True`、added / missingはいずれも0件である。後続report commitはevidence-only deltaとする。

## Verification

* Current branch: `iss-00360-cut-over-distribution-and-retire-legacy-workflow-surfaces`
* Latest implementation commit: `0c5532f42a3f5bb702d8ed02dcdb8473b263042a`（旧root entrypoint ownership、provider source identity、retry marker admission、anchor fail-closed、empty-directory cleanup identity、walk completeness、locked root identity、obsolete test surface物理削除、active fallback / atomic managed-file parent FD bindingを収束させた修正）
* Latest measured evidence: 実装コミット`0c5532f42a3f5bb702d8ed02dcdb8473b263042a`に対するfast / cut-over / full regressionと、ledger 26 node IDのcache無効exact-set再実行。report更新commitはevidence-only deltaとして識別し、successor campaign controllerが全laneを最終candidateへ再固定する。
* Evidence refresh HEAD: `fa5b354c8a70f63d87d0e4e44240d920a36c0e9b`（marker-finalization修正を含む現行branch tip。S95 v33はこのclean exact-upstream treeで実行した）
* Final implementation commit: `5fe6ddb6543fc896e54bc110e67da1bfb53c7663`（marker削除失敗時のphase / target診断とFresh / update / init-force回帰テスト。Fresh mode mismatch保護は`ff7ebb904d6cdcf5f281d6300a5d20de603a4712`、hard-link read-only adoption契約は`774e126124bd5a297c4ff193b40e0c6e11061888`、uninstall retry marker競合時のcanonical payload・stable identity検証は`194b793acb015a9c564bde0aa1dc480b8e188b84`、write/fsync失敗時identity-checked cleanupは`b0763b5fa743a6f11b14718eb5cd65b17926134b`、atomic regular-file retryのidentity検証後ftruncateは`9b9e53e968f48c5883a04ef4fbd71aaac096aca8`、managed scaffold再帰uninstallの各mutation直前root binding / entry identity再検証は`91f8b824e1a6839ee8e81030b6ae20f76b143fa1`）
* Test alignment commit: `b660924deccb0ccf595218815cef83c8483e7298`（no-replace publish seamにfault-injectionテストを追従）
* Final quality-gate evidence commit: `774e126124bd5a297c4ff193b40e0c6e11061888`（Fresh mode mismatch P1修正後の実装treeでS95 v32を実行。ledger / report更新は証跡のみの後続コミット）
* S95 v29 full regression: 実装tree `194b793acb015a9c564bde0aa1dc480b8e188b84`に対して `27 failed, 1956 passed, 516 skipped`。v28とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v30 full regression: branch tip `68ee1c67d7d770e7684751f7f07289a80e27f80a`に対して `27 failed, 1957 passed, 516 skipped`。v29とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v32 full regression: 実装tree `774e126124bd5a297c4ff193b40e0c6e11061888`に対して `27 failed, 1958 passed, 516 skipped`。v30とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v33 full regression: branch tip `fa5b354c8a70f63d87d0e4e44240d920a36c0e9b`に対して `27 failed, 1961 passed, 516 skipped`。v32とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* Latest contract-test alignment commit: `26031b6a`（Issue 360 preserve契約に合わせた既存テスト期待値の更新）
* S95 v34 full regression: branch tip `f99340169b9d2e0352b9422b3376a4e2f9fd3f1a`に対して `27 failed, 1966 passed, 516 skipped`（12分38秒）。v33とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v35 full regression: branch tip `e6dfe3aa2733f906786bb8a409c0acf22c6c2038`に対して `27 failed, 1969 passed, 516 skipped`（12分45秒）。v34とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v36 full regression: branch tip `e9759ba245643e2572a9917d48d7db43e5d26b4f`に対して `27 failed, 1972 passed, 516 skipped`（12分49秒）。v35とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v37 full regression: branch tip `6315c9d4fc0267ca3b4434cfc0783e245c6563eb`に対して `27 failed, 1973 passed, 516 skipped`（12分36秒）。v36とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v38 full regression: branch tip `7cb830ad8ccf1700c408abbd17f5261a53aa0214`に対して `27 failed, 1973 passed, 516 skipped`（12分37秒）。v37とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v39 full regression: branch tip `a30afda01b8a2307c8a55bfa4ccb758021b41620`に対して `27 failed, 1975 passed, 516 skipped`（12分36秒）。v38とのfailure node集合差分は0件、現行failure path 27件の`--lf`再実行とledger照合は一致し、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。
* S95 v40 full regression: branch tip `ec36ef5ca0b56755f90be6ba2b7be6b3b87d0fc8`に対して `27 failed, 1976 passed, 516 skipped`（12分43秒）。v39とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。通常テストは`1013 passed, 1506 skipped`、Issue 360 focused distribution suiteは`180 passed`、archive distribution integrationは`13 passed`。
* S95 v41 full regression: branch tip `34e77724b5af9b1eb742185c3eb131f4c9944606`に対して `27 failed, 1979 passed, 516 skipped`（12分40秒）。v40とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。通常テストは`1013 passed, 1509 skipped`、Issue 360 focused suiteは`302 passed, 468 skipped`、archive distribution integrationは`13 passed`。
* S95 v42 full regression: branch tip `6d06578511e8b1d54c997e25d5f19994ed50f1bd`に対して `27 failed, 1983 passed, 516 skipped`（13分53秒）。v41とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、expected-retirement 0件、比較未完了0件。通常テストは`1013 passed, 1513 skipped`、Issue 360 focused suiteは`187 passed`、clean tree archive distribution integrationは`13 passed`である。
* S95 v43 full regression: implementation candidate `5488dc75882ce9f0fd2d1a20f3c4e23ecb1a8a48`に対して `27 failed, 1991 passed, 516 skipped`（15分04秒）。v42とのfailure node集合差分は0件、固定点failure path 27件とのsubset比較は同一failure behavior 27件、current-only failure 0件、expected-retirement 0件、比較未完了0件。通常テストは`1017 passed, 1517 skipped`、Issue 360 focused suiteは`196 passed`、clean tree archive distribution integrationは`13 passed`である。
* Prior report refresh commit: `a9178856`（remote branch tip verified by `git ls-remote`; linked-worktree tracking ref refresh is unavailable due shared Git metadata lock）
* S95 failure ledger: [`artifacts/s95-full-regression-ledger.json`](artifacts/s95-full-regression-ledger.json)
* Initial planning baseline HEAD: `27b8682cb6e5262c980f3b04c7f01459a87685e9`
* Integrated main baseline: `a6ded0d9a838b40cdcd741fa473cd264b801f245`
* Issue 359 final head: `948d0cf0dedb84ca34e51a4adc0995820aa011f6`
* Initial approved planning commit: `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* Current branch upstream: `origin/iss-00360-cut-over-distribution-and-retire-legacy-workflow-surfaces`

* S35 implementation-admission SHA: `2cd8f5c5fa007d69eb716d79546eeffe3d0d02f8`（local HEAD = upstream、clean）
* S45 implementation SHA: `37d2da3693d4fc26bc815dbeb4b39b9619cda27d`
* S50 implementation SHA: `dd7c86aa446b8fb103caf47d0141d50990bf0f95`
* Plan amendment local review: fresh `spec-reviewer` pass（S40A verificationは既存`test_storage_core_cli.py`のみ）
* Plan amendment Strict review: session `issue-360-admission-current-strict`、GitHub exact SHA `8c01c9fd2e76d7d7bccc754bca902e8010026703`、resolved `GPT-5.5` verified、P0 / P1なしでpass
* S00 revalidation: branch / active Issue / dependency `ready=true` / blockers 0 / `validate nodes=221` / local HEAD = upstream `9916af139e01a322d092e6fc0434b49f6a567e37` / clean

* Push verification at planning commit: local `HEAD` = upstream = `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* `origin/main` merge: fast-forward success、Issue 360文書差分を保持
* `active set iss-00360`: success
* Initial `issue start iss-00360`: dependency `iss-00359`未完了でblocked
* Post-merge dependency check: `ready=true`、blockers=0
* Post-merge `issue start iss-00360`: 未コミットIssue 360文書を保護するcheckout safetyで停止。active selection unchanged
* Approved planning docs / IC evidence commit: success、対象7 pathだけ、commit `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* Issue 360 branch first push / same-name upstream setup: success
* Formal `issue start iss-00360`: success。Issue checkoutはcurrent Issue 360 branch、auto-sync success
* Post-start active context: Initiative `init-local-00003`、Epic `epic-00356`、Issue `iss-00360`
* Post-start dependency: `ready=true`、blockers 0、authority `github`、effective status `open`
* Post-start validation: `spec-dock: ok (validate) nodes=221`
* ChatGPT-Use-Strict: GitHub connectorで`chemitaro/spec-dock` `main` = `a6ded0d9a838b40cdcd741fa473cd264b801f245`を検証し、session `required-strict-github-connector-verificati-65`、resolved model `5.5Pro`でR/D/P authoring案を取得。main orchestratorがrepository factsとIC evidenceへ照合して正本候補へ統合
* Requirement fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし）
* Design fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし、confidence 0.98）
* Plan fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし、confidence 0.99）
* ChatGPT-SpecReview-Strict pre-submit attempt: session `required-strict-github-connector-verificati-66`はrate-limit dialogで停止。`promptSubmitted=false`、conversation IDなし、leaseなしでreview未成立
* ChatGPT-SpecReview-Strict round 1: session `required-strict-github-connector-verificati-67`、GitHub connectorでcurrent branch exact SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証、resolved model `GPT-5.5` verified。Lifecycle current-state矛盾1件をP1として`fail`
* ChatGPT-SpecReview-Strict round 2: session `required-strict-github-connector-verificati-68`、GitHub connectorでcurrent branch exact SHA `4b325885b82dbffa26cdd5cd372d3914e8d604ef`を検証、resolved model `GPT-5.5` verified。P0 / P1なしで`pass`、親Epic Reportの進捗drift 1件だけをP2として検出
* IC-1 fresh verification: Storage Core `4 passed`、S09 Authoring Kit `23 passed`、Fresh node / Artifact `3 passed`
* IC-2 fresh verification: Issue 359 static / collision `11 passed`、finalizer `9 passed`、route / zero-write `7 passed`

## Execution Admission / Blocker

2026-08-13のimplementation-start admissionでは、current exact upstream SHA `a3901a7ec2056bd392762c3d4efa71967f4ec232`に対するStrict reviewがS20順序のP1を検出したため、production / test / provider asset mutationを開始せずPlan amendmentへ戻した。その後、S10 → S40A → S40B → S20の順序、S45の依存、Requirement / Design / Reportのgate記述、S40Aの検証対象を修正し、fresh local `spec-reviewer`とStrictを再実行した。

最小修正として、Planの順序を`S10 → S40A → S40B → S20 → S25 → S30 → S35 → S45`へ変更し、S40Aの検証を既存`tests/cli_runtime/test_storage_core_cli.py`だけへ限定した。S10のread-only exact inventoryを先にlockし、S40A / S40Bでprovider physical cutoverを完了してからS20のCurrent catalog / historical manifest validationを行う契約は維持した。Plan amendment後のfresh local `spec-reviewer`とcurrent exact-upstream Strictがともにpassしたため、implementation-start gateを解消し、S00 / S10へ進む。

### S10 Exact inventory lock

S10はread-onlyで完了した。基準HEADは`9916af139e01a322d092e6fc0434b49f6a567e37`、provider-side historical sourceはIssue 359 final commit `948d0cf0dedb84ca34e51a4adc0995820aa011f6`（reachable branch `iss-00359-replace-managed-workflow-skills-with-specdock-skills`、package version `0.2.3`）とした。`git ls-tree` / `git show`でinstall_root 77 filesと旧scaffoldのexact mode/blob/SHA-256を再現できるため、旧surfaceのhistorical identityはGit provider-source provenanceとして採用できる。wheel / sdistの保存物は存在せず、配布済みpackage identityとは断定しない。

| 分類 | S10でlockした現物 | 実装上の扱い |
|---|---|---|
| Current Target | provider `spec_dock/{docs,templates,scripts,system}/**`、`.gitignore`、install_root二skill、`.github/workflows/ci.yml`、root `spec`、generated `active/.agent` | S40B後にphysical catalogとして導出し、Current全量manifestは作らない |
| Obsolete managed | 旧18 managed skill、host-adapter/native agent/config/prompt/rule、ChatGPT wrapper、authoring-pack、planning runtime、obsolete docs/templates | S40A/S40Bでproviderから除去。consumer pruneはGit-source exact identityまたはtrusted manifest + target identity一致時だけ |
| Preserve / user-owned | `initiatives/**`、node-local evidence、Workbench payload、unknown external skill/config/workflow、unproven same-name path | 自動置換・pruneせず、必要時はpreserve-and-block |
| Read-only evidence | Issue 357〜359 report、Epic IC artifacts、Git history/tree、package metadata、current provider/dogfood parity | source-of-truth照合とreport evidenceだけに使用 |

Provider / dogfoodの現行二skill、CI、`.gitignore`、`scripts/spec-dock`のselected bytes/modeは一致した。dogfood固有のgenerated filesは`spec-dock.version`、active/agent derived views、dashboard/deps/tree projectionに限定される。`meta.json`のowner/path claims、workspace marker、directory名だけでは個別ownershipを証明しない。S10で再現できない「過去wheel/sdistのpackage digest」は未採用候補としてpreserve-and-blockに記録し、S20のmanifestへ推測値を登録しない。

### S40A Legacy planning Runtime physical retirement

S40Aの実装を、S10でlockしたexact targetとPlanの共有symbol境界に従って完了した。実装commitは`abcea9c21669b64bdb2277e6a0cf212ff8ae9727`、旧専用test / fixture整理commitは`091a323225a5b8af854f6f5f16705354fcb761b6`であり、S40A後のclean HEAD / upstreamは`091a323225a5b8af854f6f5f16705354fcb761b6`で一致している。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Old-only Runtime / wrapper removal | pass | provider / dogfoodそれぞれ63 path（60削除 + contracts/ports/bootstrap 3変更）。`spec-dock-chatgpt`、`scripts/authoring-pack/**`、runtimeのplanning / authoring_pack treeを除去 |
| Shared boundary safety | pass | `application/contracts.py` の planning use case 4 fields、`application/ports.py` の planning-only ports、`cli/bootstrap.py` の planning gateway / callback / importだけを除去。Storage Core / Artifact / lifecycle / sync / validate assemblyは保持 |
| Route / import absence | pass | `tests/cli_runtime/test_storage_core_cli.py` の removed module / help-route characterizationを更新 |
| Retained Storage Core characterization | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py -q` → `4 passed` |
| Adjacent retained surfaces | pass | `uv run pytest tests/cli_runtime/test_wrappers.py tests/unit/infra/test_authoring_kit_assets.py -q` → `304 passed, 9 skipped` |
| Formatting / review | pass | `git diff --check`、fresh `code-reviewer` pass（P0/P1なし、provider/dogfood parity確認） |

S40AのREDは、共有契約を先に切断した状態で旧planning modulesをretained listへ残したため、Storage Core testが旧存在期待で失敗したこと。GREENではremoved module / use case fieldへ期待値を移し、物理削除後に4件すべてpassした。旧専用test / fixture 53件も削除し、S40B対象の`test_wrappers.py`、`test_authoring_kit_assets.py`、`test_init_update.py`、`authoring_kit` fixtureは保持した。S40A実装commitとtest整理commitの後にworktree / upstream SHA一致を確認した。S40Bのprovider physical catalog cutoverへ進んだ。

### S40B Shipped Target catalog physical cutover

S40Bのprovider-side physical cutoverを完了した。Current install-rootは次の5ファイルへ縮小した。

* `.agents/skills/spec-dock/SKILL.md`
* `.agents/skills/spec-dock-grill-with-docs/SKILL.md`
* `.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml`
* `.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py`
* `.github/workflows/ci.yml`

旧18 managed skill、legacy 3 skill、host-adapter metadata、`.codex/**`、`.github/agents/**`、旧ChatGPT / planning / authoring-pack配布面はprovider treeから除去した。Current二skillのIssue 359 final bytesをSHA-256で固定し、retained CIはStorage Coreの`sync` / `validate`だけを実行することを確認した。`.gitignore`は`src/spec_dock/assets/spec_dock/.gitignore`を物理provider assetとして必須化し、`_DEFAULT_SPEC_DOCK_GITIGNORE` fallbackを削除した。provider source欠損時はmutation前に停止する境界を残している。

旧phase / workflow / authoring / host-adapter専用docsと、`discussions/**`、`assurance/**`、`issue-profiles/**`、`pr-repair-batch.md`のprovider scaffoldも除去した。S40Bではdogfood projectionを直接編集・更新せず、既存consumerのlegacy external surfaceは保持したままS20/S25 classifierとS55のproven pruneへ引き渡す。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Provider install-root exact catalog | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py -q` → `5 passed` |
| Retained Storage Core / authoring kit | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py -q` → `4 passed`; `uv run pytest tests/cli_runtime/test_wrappers.py tests/unit/infra/test_authoring_kit_assets.py -q` → `304 passed, 9 skipped` |
| S40B focused contract | pass | `uv run pytest --run-full-regression tests/unit/infra/test_authoring_kit_assets.py tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_distribution_cutover.py -q -k "target_catalog or removed_surface or retained or gitignore or s40b or storage_core"` → `11 passed, 302 deselected` |
| Fresh external catalog | pass | temporary repository `init` materialized only the two skill trees and retained `ci.yml`; no `spec-dock-chatgpt` |
| Formatting | pass | `git diff --check` |

S40Bのprovider / test差分はfresh `code-reviewer`確認、commit、push後のclean / upstream一致まで閉じた。S20はこのphysical treeからCurrent catalogを導出し、historical-only manifestを追加した。既存consumerのclassifier、prune、uninstall mutationも後続S25〜S70で接続・検証済みである。

### S20 Current / historical catalog validation

S20では、S40B後のphysical `install_root`からCurrent assetのpath、regular-file SHA-256、modeをread-onlyで導出する`src/spec_dock/managed_distribution.py`と、consumerへコピーしないprovider-private `src/spec_dock/assets/managed_distribution.json`を追加した。ManifestはCurrent catalogを複製せず、historical sectionのpath grammar、kind、lowercase SHA-256、trace source、duplicate / nested identity / ancestor-descendant / Current overlap、schema fieldsをfail-closedで検証する。`build_distribution_plan`は`actions=()`を返し、S20ではconsumer scan、classifier、CLI接続、write / deleteを行わない。

| 観測 | 結果 | 証拠 |
|---|---|---|
| RED seed | pass | module未作成状態で`uv run pytest tests/unit/infra/test_managed_distribution.py -q` → `ModuleNotFoundError` |
| S20 bounded GREEN | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q` → `20 passed` |
| S20 required selection | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "catalog or manifest or overlap"` → `6 passed, 14 deselected` |
| S20 + S40B focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/unit/infra/test_authoring_kit_assets.py tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_distribution_cutover.py -q` → `333 passed` |
| Read-only / formatting | pass | no target write in S20 tests、`git diff --cached --check` |

S20レビューで、recognized version anchors / trusted manifest claimsのnested identityをoverlap検査から漏らしていたP1を検出した。全historical sectionを再帰的に検査し、Current pathとの祖先・子孫衝突を拒否する実装とnegative testsへ修正した。S20のfresh re-review pass、S40B scope re-review pass、step commit / clean / upstream一致後にS25 classifierへ進む。

### S25 Ownership classifier / Current collision

S25では`managed_distribution.py`へ読み取り専用のTarget分類を追加した。provider Current assetに加えてcanonical `spec -> spec-dock/scripts/spec-dock` shortcutを合成し、Fresh / update / `init --force` / uninstallのoperation別にmissing、current-identical、direct historical、trusted manifest + target identity、unknown collision、exact directory、symlink container、hard-link mutationを分類する。Freshではhistorical identityをupgradeせず`preserve-and-block`とし、recognized operationではknown historicalだけをupgrade / prune候補にする。consumer-side `owner`やmarker単独は信頼せず、manifest自身のknown bytesとprovider-private claim、実target identityの一致だけを補助証拠にした。`DistributionAction.diagnostic()`はrepository-relative path、classification、reason、operator actionだけを返し、source bytes・credential風文字列・repository外absolute pathを保持しない。S25ではwrite、delete、CLI接続、version / retry admissionを行わない。

| 観測 | 結果 | 証拠 |
|---|---|---|
| RED seed | pass | target_root / operation引数未実装時の`uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "s25"` → `9 failed` |
| S25 bounded GREEN | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "s25"` → `17 passed, 20 deselected` |
| S20 + S25 + S40B focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py tests/cli_runtime/test_storage_core_cli.py tests/unit/infra/test_authoring_kit_assets.py -q` → `350 passed` |
| Historical Current overlap / obsolete shape | pass | historical Current exact-path overlapを許可し祖先・子孫を拒否、obsolete exact recordのshapeを正規化してduplicate / Current collisionを検証 |
| Read-only / diagnostic sanitation | pass | target tree unchanged、diagnosticにsecret・source bytes・external absolute pathなし、`git diff --check` |

S25 fresh code reviewは、missing uninstallのno-op、canonical shortcutのhistorical evidence、synthetic Current overlap、Freshでのhistorical shortcut非materialization、current hard-link uninstallの5点を検出した。分類器と回帰テストを修正し、Freshでhistorical identityを`preserve-and-block`として明示分類する回帰も追加した。S25 bounded GREEN `17 passed`、S20 + S25 + S40B focused regression `350 passed`を再確認した。修正後のfresh re-review pass、step commit、clean / upstream一致後にS30へ進む。

### S30 No-follow apply / repository root rebind

S30では、S25で確定したblock-free planだけを対象に、provider Current bytesと合成shortcutをdescriptor-relativeなno-follow parent chainからmaterializeし、historical Current / obsolete targetをidentity再検証後にupgradeまたはpruneする`apply_distribution_plan`を追加した。Plan生成時にroot、ancestor、exact targetのdevice、inode、`ctime_ns`、type、link count、content/link identityをsnapshotし、apply開始前と各action直前に再照合する。missing regular fileは`O_CREAT | O_EXCL | O_NOFOLLOW`で作成し、regular upgradeはheld descriptorへ書き込み、pruneはheld parentのexact entryだけをunlinkする。symlink upgradeはplatformのno-replace rename capabilityを先に確認し、private staging symlinkとdescriptor-relative `RENAME_EXCL` / `RENAME_NOREPLACE`でpublishする。hard-link、symlink container、exact directory、root / parent差し替え、destination出現は例外で停止し、外部replacement・旧root・既存user bytesへ書き込まない。CLI、version marker、retry marker、recursive cleanupはS30の対象外である。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S30 bounded GREEN | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "s30"` → `13 passed, 37 deselected` |
| S20 + S25 + S30 + S40B focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py tests/cli_runtime/test_storage_core_cli.py tests/unit/infra/test_authoring_kit_assets.py -q` → `363 passed` |
| Root / parent rebind and destination race | pass | preflight前後、data write直前、既作成祖先の差し替え、destination出現を`DistributionApplyError`で停止し、replacement / 外部root / user bytesが不変 |
| No-follow / hard-link / shortcut | pass | missing Current、historical regular upgrade / prune、canonical shortcutのno-replace upgrade、hard-link uninstallをdescriptor-relativeに検証 |
| Syntax / formatting | pass | `python -m py_compile src/spec_dock/managed_distribution.py`、`git diff --check` |
| S30 fresh code review / re-review | pass | code-reviewerがTOCTOU、hard-link、symlink swap、staging cleanup、capability preflightを再確認し`findings=[]`, `review_status=pass` |

S30のfresh code reviewで検出されたroot / parent再bind、祖先identity binding、hard-link、symlink upgrade、staging cleanupの指摘を修正した。修正後はS30テスト、focused regression、mypy / ruff対象チェックを再実行し、no-follow / no-replace primitiveのcapabilityをmutation開始前に検証した。未対応platformではempty parentを残すmutationも開始せず、再レビュー、commit、clean / upstream一致まで閉じた。

### S35 Version / retry marker admission

S35では、provider-private `managed_distribution.json`に実在する`0.2.3`のrecognized workspace entryと、`spec-dock/scripts/spec-dock` / `spec-dock/.gitignore`のSHA-256 anchorを登録した。`managed_distribution.py`へ読み取り専用の`admit_distribution_operation`を追加し、実行中package version、no-follow・link-count-oneのcanonical `MAJOR.MINOR.PATCH\n` marker、recognized allowlist、version-specific anchor、newer targetのdowngrade拒否を共通判定する。init / update / `init --force`では同一package・同一operation・同一repository rootのdevice / inodeへ束縛した`.distribution-retry.json`だけをforward retryとして許可し、uninstallでは既存`.uninstall-retry.json`のschemaを変更せず使用する。invalid、unknown、dual、operation / package / root mismatchは全mutation前に拒否し、`cli.py`のinit / update / uninstall入口へ接続した。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S35 bounded GREEN | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q -k "s35 or s40b"` → `16 passed, 50 deselected` |
| Version / marker focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "version or marker or force or cross_root"` → `16 passed, 2 skipped, 634 deselected` |
| Zero-write / cross-root | pass | malformed・BOM・CRLF・追加行、hard-link、newer、dual marker、A→B marker replayで`DistributionAdmissionError`を返し、consumer snapshot / marker bytes不変 |
| Legacy uninstall marker | pass | 既存`{"schema_version":1,"managed_by":"spec-dock","purpose":"uninstall-rerun"}`だけをversion欠損のuninstall retryとしてadmitし、新markerへ移行しない |
| Static checks | pass | `uv run ruff check src/spec_dock/managed_distribution.py tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py`、`uv run mypy src/spec_dock/managed_distribution.py src/spec_dock/cli.py`、`python -m py_compile`、`git diff --check` |
| Broad regression | migrated / retired selectors | 旧legacy host-adapter/native-shim前提のテストはIssue 360のphysical cutoverに合わせて明示的にretired selectorへ移し、Current distribution / uninstall / archive consumerのfocused suiteを正本とした |

### S45 Fresh init cutover

S45では、`spec-dock/` が存在しないGenuine Freshだけを対象に、providerのCurrent distribution planを最初のconsumer write前に生成・検証し、Current exact collision、symlink、directory、workspace-invalidをzero-writeで拒否する経路へ切り替えた。Freshでは既存のunknown／obsolete-looking external path、user-owned workflow、native shimを分類根拠だけで削除せず、Current identical assetはadoptし、root Workbench READMEは新規scaffoldへseedする。`init --force` と既存workspaceの更新経路はS45では変更せず、S50へ引き渡した。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S45 bounded GREEN | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py -q -k "s45_fresh"` → `6 passed, 7 deselected` |
| Fresh preservation / collision matrix | pass | unknown／obsolete-looking external、Current unknown collision、existing non-directory workspace、identical Current、symlink/directory collision、force rerunの6ケースを確認 |
| Focused Fresh selection | pass | `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "fresh"` → S45追加ケースはpass。既存S40B削除資産前提テスト3件はbaseline driftで失敗し、step gateには不採用 |
| Static checks | pass | `uv run ruff check src/spec_dock/cli.py tests/cli_runtime/test_distribution_cutover.py`、`git diff --check` |

S45のfresh code review、step commit、clean / upstream一致後にS50 recognized update / `init --force`へ進む。

### S50 Recognized update / `init --force`

S50では、admissionを通過したrecognized workspaceの`update`と既存workspaceへの`init --force`を同じ`managed_distribution` plan/applyへ接続した。Current external assetのcreate／adopt／upgradeはdistribution applyをauthorityとし、その後に`spec-dock/{docs,templates,scripts,system}`だけをrefreshする。`initiatives/**`、既存の`.workbench/**`、unknown siblingはこの経路で削除・置換しない。Fresh `init`はS45の経路を維持し、`--force`なしの既存workspaceは既存のerror契約へ戻した。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S50 focused behavior | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py -q -k "s50 or update or force"` → `7 passed, 11 deselected` |
| S50 + distribution regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q` → `77 passed` |
| Preserve / zero-write matrix | pass | missing Currentのrestore、`init --force` parity、unknown Current collision、directory collisionを検証。initiatives / `.workbench` sentinelは不変 |
| Static checks | pass | `uv run ruff check src/spec_dock/cli.py tests/cli_runtime/test_distribution_cutover.py`、`git diff --check` |
| Existing broad selection | not adopted | legacy provider assetを前提にした既存updateテストと、Current anchorを意図的に壊す旧テストはS35以降の仕様と不一致のため、S50 step gateには採用しない |

S50のfresh code review、step commit、clean / upstream一致後にS55 proven obsolete prune / preserveへ進む。

### S55 Proven obsolete prune / preserve-and-block

S55では、Issue 359 final commit `948d0cf0dedb84ca34e51a4adc0995820aa011f6` のprovider `install_root`からCurrent 5ファイルを除外した旧managed配布物を再走査し、再現可能な72ファイルをGit provider-source SHA-256付きの`obsolete_exact_files`へ登録した。旧legacy 3 skill（`spec-driven-tdd-workflow`、`spec-dock-system-architect`、`spec-dock-implementation-planner`）は過去bytesを現行履歴から再現できないためidentityを推測せず、空identityの`preserve-and-block`として登録した。ManifestはCurrent catalogを複製せず、exact relative path / identity / `on_unknown`だけを保持する。

Provenanceテストは全identityのsource refがこの固定commit SHAであることを常時検証し、履歴オブジェクトが利用できるcheckout（今回のローカル実行）では各blobのSHA-256とmodeまで`git show` / `git ls-tree`で照合する。履歴を取得しないshallow checkoutでは、静的なSHA束縛を実行したうえでblob照合部分だけを明示的にskipし、CIが履歴の有無で誤失敗しないようにする。

既知のobsolete identityに一致するregular fileは`update` / `init --force`でexact entryだけをpruneし、変更済み・ownership不明・symlink・exact directoryは保持またはblockして全mutation前に停止する。既存dogfood checkoutへrecognized `update`を実行し、旧`.agents/**`、`.codex/**`、`.github/agents/**`と旧docs / template surfaceをproviderへ同期して除去した。一方、`spec-dock/initiatives/**`、Issue-local `.workbench/**`、retained CI、Current二skill、unknown siblingは保持した。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S55 catalog / manifest | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py -q` → `65 passed`; manifest obsolete exact entries `75`（known 72 + unproven legacy 3） |
| Proven obsolete prune | pass | unit testでknown digest一致の`.codex/config.toml`を`update`時にprune。CLI testで`update` / `init --force`の実consumer経路を確認 |
| Preserve-and-block | pass | modified / unknown regular、symlink、exact directoryをbefore/after不変で停止。診断はrelative path / reasonのみ |
| Existing consumer cutover | pass | `uv run spec-dock update .` 成功。old managed external surfaceとobsolete scaffold docs/templatesを除去し、initiatives / Issue-local Workbench / retained CIを保持 |
| Focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q` → `87 passed`（unit 65、CLI 22） |
| Static checks | pass | `python3 -m json.tool src/spec_dock/assets/managed_distribution.json`、`uv run ruff check src/spec_dock/managed_distribution.py tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py`、`git diff --check` |

S55ではknown historical assetだけのbounded pruneとpreserve-and-blockを閉じ、再現不能legacy 3 skillは推測削除せずpreserve-and-blockへ分類した。partial failure marker / forward retry、uninstall apply、package parity、docs最終整合はS60〜S90で完了し、旧surfaceのCurrent配布面からの除去と既存consumerの安全な切替を検証済みである。

### S60 Partial failure / same-package forward retry

S60では、recognized `update` / `init --force`のapplyをphase marker付きforward recoveryへ切り替えた。full preflight後に`spec-dock/.distribution-retry.json`を作成し、distribution apply、managed scaffold refresh、post-verify、version writeの各境界で完了phaseをatomicに更新する。`spec-dock.version`はpost-verify後まで旧値を保持し、version writeとmarker除去が完了したときだけsuccessへ到達する。markerはschema version、operation、package version、target rootのdevice / inode、last completed phase、purposeだけを持ち、credential、source bytes、absolute pathを含めない。

root identityはoperation開始時に固定し、marker更新、scaffold refresh、version publish、marker removalの前後で再検証する。実際のmarker / version / scaffold操作はno-followでopenしたroot directory descriptorへbindした相対pathで実行し、visible rootを差し替えられてもreplacement repositoryへredirectしない。root rebind時はpartial failureとして停止し、旧rootへ残ったmarkerやpathname replacementをcleanupしない。markerとversionのregular-file publishはno-follow、link-count-one、destination identity再検証を行い、preflight後に出現したdestinationを上書きしないno-replace pathを採用した。同じroot / package / operationの再実行は既存Currentをadoptしながら収束し、別rootへのmarker replayはadmissionでzero-write blockする。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S60指定契約 | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q -k "retry or fault or rebind or cross_root or post_verify or diagnostic"` → `20 passed, 101 deselected` |
| S55 + S60 + S65 + S70対象回帰 | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q` → `121 passed`（unit 65、CLI 56。S55 baseline 87＝unit 65、CLI 22からS60〜S70の34ケースを追加） |
| Fault / diagnostic sanitation | pass | distribution-apply、scaffold、post-verify / version faultでphase marker保持・旧version保持・same-operation retry収束を確認し、credential風文字列・source bytes・repository外absolute pathをstderrへ出さないことを確認 |
| Root rebind / no-replace | pass | descriptor-bound marker / scaffold / version mutationをroot差し替え中に実行してもreplacement sentinelを変更せず、旧root markerを保持し、retry側replacementへのwriteを0件にした。atomic regular-file publishでrace destinationを上書きしないことも確認 |

### S65 Uninstall admission / dry-run

S65では、uninstall入口がdistribution retry marker、dual marker、invalid / newer / anchor-mismatch versionを既存uninstall planへ渡す前に拒否し、version欠損でも正規のlegacy `.uninstall-retry.json` だけをread-only retryとしてadmitすることを確認した。dry-runの外部配布候補は`managed_distribution.json`と共通classifierから投影し、known historical obsoleteは`would_remove`、modified / unknown collisionは`preserved`として表示する。distribution retry markerの`last_completed_phase`もwriterが出力する5値へallowlistした。実削除とlegacy markerのapply順序はS70で完了した。

| S65指定契約 | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_distribution_cutover.py -q -k "dry_run or admission or marker"` → `12 passed, 33 deselected` |
| S65 zero-write / ownership projection | pass | invalid version、distribution / dual markerのuninstallをfilesystem snapshot不変で拒否し、legacy uninstall markerのみversion欠損のrerun admissionを許可。modified current skillはpreserved、known obsolete identityは`would_remove`としてdry-runへ表示 |
| Static checks | pass | `uv run ruff check src/spec_dock/cli.py tests/cli_runtime/test_distribution_cutover.py`、`uv run mypy src/spec_dock/cli.py src/spec_dock/managed_distribution.py`、`python3 -m json.tool src/spec_dock/assets/managed_distribution.json`、`git diff --check`、`./spec-dock/scripts/spec-dock validate` |

### S70 Uninstall apply / preservation / retry

S70では、S65のdry-run分類をapplyへ引き継ぎ、preservedなownership collision、modified / unknown asset、symlink / hard-link / boundary collisionが1件でもある場合はretry marker作成前に全mutationを停止するようにした。marker作成・file unlink・spec-history recursive removal・empty-boundary cleanup・marker finalizationはdescriptor-relative `O_NOFOLLOW | O_DIRECTORY` chainとroot identity再検証で実行し、pathname差し替え後にreplacementへredirectしない。recognized updateは外部distribution apply前に`spec-dock/{docs,templates,scripts,system}`とgenerated boundaryのno-follow scaffold preflightを通過させ、symlink / non-directory collisionをzero-writeで拒否する。applyableなplanだけが既存`.uninstall-retry.json`を最初のmutationとして作成し、部分失敗時はmarkerを保持して再実行を許可し、post-verify完了後にmarkerを最後のmanaged fileとして除去する。`--keep-specs`では`initiatives/**`を保持し、`--remove-specs`だけが明示的に削除する。

| S70指定契約 | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_distribution_cutover.py -q -k "keep_specs or remove_specs or legacy or repeated or partial or retry or empty"` → focused uninstall / cutover tests pass |
| No-follow race / scaffold collision | pass | scaffold boundary 8件、uninstall root rebind / cleanup rebind 2件を追加し、replacement sentinel保持とmarker未作成を確認 |
| S70 fail-closed / marker ordering | pass | modified current、known obsolete + unknown mixed candidateのapply前block、marker未作成、partial failureでmarker保持、same-package rerunでmarker-last除去を確認 |
| S70 preservation boundary | pass | `--keep-specs`でinitiative bytesを保持し、`--remove-specs`でのみspec historyを削除。空のpreserved / unknown directoryも削除候補へ昇格させず、clean boundaryのcurrent / obsolete action、unknown sibling、root shortcutを分類どおり処理 |
| S70 static checks | pass | `uv run ruff check src/spec_dock/cli.py src/spec_dock/managed_distribution.py tests/cli_runtime/test_distribution_cutover.py tests/unit/infra/test_init_update.py`、`uv run mypy src/spec_dock/cli.py src/spec_dock/managed_distribution.py`、`git diff --check` |

S60〜S70の直接契約はCLI 56件、distribution unit 65件、および旧installer uninstall契約を現行仕様へ移行した28件のfocused regressionで閉じた。uninstallでは計画時のregular-file digest / device / inode / ctime / size、symlink target、directory identityをapply直前に再検証し、差し替えられたreplacementを削除しない。recognized updateではmanaged scaffold各directoryのdevice / inodeをpreflight後のrecursive refresh直前に再検証し、消失した`spec-dock`親をretry marker作成時に再生成しない。旧uninstall群のmarker保持、modified Workbench続行、version marker欠損後の無条件rerunという矛盾した期待は現行fail-closed契約へ更新し、legacy host-adapter/native-shim前提の旧テストはretired selectorとして明示した。

### S80 Dogfood projection / package parity

S80ではprovider-side assetをarchiveの正本としてwheel / sdistを再生成し、archiveだけを参照するisolated consumer、Fresh consumer、既存consumer update、checked-in dogfood projectionの境界を検証した。providerのCurrent install-root、docs / templates / scripts / system、Workbench README、obsolete / cache / generated payloadのallowlistを比較し、working checkoutへのfallbackやmanual consumer repairを使わずに12個のCurrent / archiveシナリオを閉じた。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Package build | pass | `uv build` → `dist/spec_dock-0.2.3.tar.gz` / `dist/spec_dock-0.2.3-py3-none-any.whl`を生成 |
| Archive inventory / prohibited payload | pass | `tests/integration/test_epic_00343_distribution.py` の `s01_001`〜`s01_003`、wheel allowlist、stale / cache / hidden payload拒否 |
| Provider / dogfood projection parity | pass | 同integration suiteの `_assert_s04_provider_projection_parity` と `s04_004` / `s04_005`でprovider bytesとconsumer projectionを比較 |
| S80/S85 integration regression | pass | `uv run pytest --run-full-regression tests/integration/test_epic_00343_distribution.py -q` → `13 passed` |

### S85 Installed consumer smoke

S85ではarchiveからinstallしたCLIだけを使い、retained Storage Core、Authoring Kit、Artifact import、dependency / validate / sync、Workbench preservation、旧workflow不在の組み合わせをisolated consumerで確認した。既存consumerのupdateとfuture node作成も同一archive起点で実行し、GitHub境界はtest harnessのstubに限定した。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Installed Fresh lifecycle | pass | `test_tc_346_s01_004_fresh_consumer_installed_shell_and_generic_import` |
| Existing consumer update / preservation | pass | `test_tc_346_s02_001`〜`s02_004`でcanonical scope、Workbench payload、managed docsを検証 |
| Retained runtime / artifact smoke | pass | `test_tc_346_s03_001`〜`s03_003`でfour-target import、nested cwd、cross-filesystem privacyを検証 |
| Dogfood update / no-backfill | pass | `test_tc_346_s04_004` / `s04_005`でexact checkout update、provider parity、future issue importを検証 |

### S90 Docs impact resolution / docs refresh

S90では、root README、provider docs、dogfood projection、Current rulesの削除済みworkflow linkを実装後のTarget / ownership / recovery contractへ更新した。旧`spec-dock-chatgpt`、旧planning / execution skill、削除済みworkflow / phase docsへのCurrent command・linkは残さず、Historical preservation surfaceの説明は現行Artifact guidanceへ置き換えた。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Docs / Markdown focused tests | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py tests/unit/infra/test_authoring_kit_assets.py -q -k "docs or markdown or vocabulary or migration or link"` → `118 passed, 229 deselected` |
| Actual CLI help alignment | pass | `uv run spec-dock --help`、`uv run spec-dock update --help`、`uv run spec-dock uninstall --help`でCurrent command、dry-run、`--apply`、keep/remove specsを確認 |
| Removed route / link scan | pass | root README、provider / dogfood docs・rules・templates・scriptsをpath-aware `rg`で走査し、旧skill・`spec-dock-chatgpt`・削除済みworkflow / phase link 0件 |
| Provider / dogfood docs parity | pass | provider `docs/README.md`、`reference_github.md`、rules 5ファイルをdogfoodへ反映しbyte parityを確認 |

### S95 / S99 Final quality gate status

Issue 360の対象範囲に対する最終確認を実施した。対象外の既存runtime回帰と外部ブラウザ制限は、passへ置換せず明示的に残す。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Fast lane | pass | 実装コミット`0c5532f42a3f5bb702d8ed02dcdb8473b263042a`で`uv run pytest -q` → `1022 passed, 1455 skipped` |
| Static quality | pass | `make lint`（ruff check / format / mypy）→ pass |
| Issue 360 focused regression | pass (Issue 360 suites) | `uv run pytest --run-full-regression -q tests/cli_runtime/test_distribution_cutover.py` → `139 passed`。Dangling active pathfile symlink、managed-file parent rebind、marker再試行、root binding、no-follow / no-replace、Fresh / update / uninstall cut-overを確認 |
| Archive distribution integration | pass | `uv run pytest --run-full-regression tests/integration/test_epic_00343_distribution.py -q` → `13 passed` |
| Package build | pass | `uv build` → wheel / sdist生成 |
| Consumer validation | pass | `./spec-dock/scripts/spec-dock validate` → `nodes=221`、`deps check iss-00360 --no-github` → `ready=true blockers=0` |
| Full repository regression | pass (accepted nonzero / exact ledger match) | 実装コミット`0c5532f42a3f5bb702d8ed02dcdb8473b263042a`で`uv run pytest --run-full-regression -q` → `26 failed, 1970 passed, 481 skipped`（15分23.80秒）。ledger 26 node IDのcache無効再実行は`exact=True`、added / missing 0件。各path・owner・follow-up・根拠は[`artifacts/s95-full-regression-ledger.json`](artifacts/s95-full-regression-ledger.json)に記録した |
| Final ChatGPT-final-quality-gate-strict | successor remediation cycle 2 | generation 2 bounded reviewのP1二件をFD-relative managed-file publicationで修正し、最新実装SHAでfull regression exact-set証跡を取得した。後続evidence-only candidateへ全laneを再固定する |
| S99 / H10 | pending final certificate | bounded review・slow attestation・fresh full reviewをsuccessor candidateへ再固定し、repository外certificateを発行する。origin session closureは直後candidate限定の診断であり、そのcandidateがbounded P1で停止したため認証要件へ持ち越さない。certificate後にrepositoryを変更しない |

## Residual Risks / Follow-ups

* Issue 359 final headとmain mergeへR/D/Pを再照合した。S10でCurrent branch HEAD、Target二skill、provider / dogfood / packageのexact inventoryをlockした。
* Formal `issue start`はapproved planning commit / push後に成功し、active Issueは`iss-00360`である。
* Epic-local ArtifactとReportにIC-1 / IC-2 pass evidenceを記録し、Requirement / Design review、commit / push、formal start、Plan amendment、fresh local `spec-reviewer`、S00再確認、S10 inventory lock、S40A code review / focused test、S40B focused cutover / S20 catalog tests、S25 focused classifier tests、S30 no-follow apply、S35 admission focused tests、S45 Fresh preservation / collision tests、S50 recognized update / force tests、S55 obsolete prune / preserve tests、S60 forward-retry / root-binding tests、S65/S70 uninstall、S80 package parity、S85 installed smoke、S90 docs refreshを完了した。最終Strict campaignは2件のP1を順に検出し、report identity driftとmanaged scaffold path-swap raceを修正した。S99/H10は最終candidateの全lane passとrepository外certificate発行まで未完了として扱う。
* Historical digestは実際の過去package bytesから再現できるものだけをS10でlockする。再現不能なcandidateは推測登録せずpreserve-and-blockする。

## Notes

### Planning route

初期authoringでは利用者指示によりCodexが直接作成した。その後、利用者がChatGPT-Use-StrictとChatGPT-SpecReview-Strictの利用を明示したため、GitHub exact-mainをauthorityとするStrict routeへ切り替えた。通常の`planning create / apply`、`adoption_published`は使用していない。

ChatGPT-Use-Strictの出力はadvisory evidenceとして扱い、main orchestratorが現行source、test、Issue 357〜359 handoff、IC-1 / IC-2へ照合してcanonical候補へ統合した。最終authorityはrepository内のR/D/Pとfresh reviewer gateであり、Strict outputの自己主張ではない。

### Evidence inputs

* Epic 00356の承認済みRequirement / Design / Plan / Report
* Issue 357の360 handoff keep inventoryとStorage Core実装report
* Issue 358のTarget Authoring Kit、obsolete candidate、21-path preservation fixture、report
* Issue 359の二skill contract、18 managed + 3 legacy skill inventory、branch implementation / PR report
* Issue 360のevidence-only draft Requirement / Design / Plan
* `src/spec_dock/cli.py`の現行init / update / uninstall、exact obsolete path、bootstrap-only、collision-aware additive skill behavior
* provider / dogfood asset treeとinstaller test inventory

### Evidence Adoption Ledger

| ID | adoption_status | Source / role | Claim | Canonical target | Rationale / evidence | Blocking / next action |
|---|---|---|---|---|---|---|
| EAL-360-001 | adopted | ChatGPT-Use-Strict authoring evidence | Current physical authority、historical identity、deep module、operation × provenance、forward recovery、parityをR/D/Pへ具体化できる | Requirement / Design / Plan | GitHub connectorで`chemitaro/spec-dock` main SHA `a6ded0d9…`を確認し、session `required-strict-github-connector-verificati-65`の提案をlocal source / tests / IC evidenceへ照合した | no。canonical authorityはR/D/Pとfresh reviewer |
| EAL-360-002 | adopted | `implementation-planner` read-only draft | Plan round 1の5 P1をstep-local vertical TDD、Closure Index、delegation/review/commit gate、S90/S99/H10へ再構成する | Plan §4〜§9 | Canonical editなしのdraftをmain orchestratorがapproved R/Dとworkflow policyへ照合して統合した。S20順序・S45依存・S40A検証対象をamendし、fresh local reviewとStrict passを確認した | amendment後の現行Planは`approved` / `implementation-start-ready`。S10からstep executionへhandoff |
| EAL-360-003 | adopted | fresh `spec-reviewer` findings | Requirement / Design / PlanのP0/P1をphaseごとに検出し、修正範囲を限定する | R/D/P/report | Requirement round 3、Design round 3、Plan round 3のpassをraw authorityではなくreview evidenceとして採用した | no。Strict round 2 passで独立最終照合済み |

EAL-360-002の旧promotion gateはPlan amendment、fresh local `spec-reviewer`、current exact-upstream Strict passにより解消された。現行Planは`approved` / `implementation-start-ready`であり、S00再確認後にS10 inventory lockへ進む。

### Delegated Draft Evidence

| Draft | created_by_role | Scope / source | Allowed output | Diff guard | Adoption | Reviewer |
|---|---|---|---|---|---|---|
| Issue 360 Plan restructuring draft | `implementation-planner` | Issue 360 approved Requirement / Design、draft Plan / report、`phase_plan_issue.md`、`workflow_issue.md`、Plan round 1 findings | Chat response内のread-only section draft。Canonical、implementation、Artifactへのwrite禁止 | Workerはfile / Artifact変更なし。Main orchestrator統合後の`git diff --check` pass、`spec-dock validate` pass | EAL-360-002でadopted。Authority自己主張、promotion、readiness claimは不採用 | fresh Plan round 3 pass |

### Grade Specialist Evidence Gate

| Grade | Specialist | Availability / route | Output | Integration decision | Gate |
|---|---|---|---|---|---|
| strict | `implementation-planner` | available / used | 5件のP1を閉じるstep構造、Closure Index、concrete RED、delegation / reviewer / commit、S90 / S99 / H10 draft | main orchestratorがapproved R/Dと現行workflowへ照合しcanonical Planへ統合 | closed。fresh `spec-reviewer` round 3 pass |

### Spec Interpretation / Decision Ledger

| ID | Status | Type | Options considered | Disposition | Decision / evidence | Canonical promotion / follow-up |
|---|---|---|---|---|---|---|
| D-360-001 | resolved | authority | Current全量manifest / physical provider tree + historical-only manifest | adopted | Current catalogは物理provider treeから導出し、JSONへ全量複製しない。Provider-private manifestはhistorical identityとobsolete policyだけを持つ | Design §2、§4、Plan S10 / S30 |
| D-360-002 | resolved | safety | path / marker自己申告 / trusted manifest + target identity | adopted | Exact path、workspace marker、consumer manifestの自己申告だけではownershipを認めない。Known target identity、またはknown manifest bytes + provider-private target identityの一致だけを証拠にする | Requirement I360-RQ-009、Design §4.2 / §6、Plan S10 / S30 |
| D-360-003 | resolved | product boundary | CI削除 / cognitive CI維持 / deterministic Storage Core CI維持 | adopted | `.github/workflows/ci.yml`はcognitive workflowではなくdeterministic Storage Core CIとしてTargetへ維持し、Current reusable collision policyを適用する | Requirement I360-RQ-002 / 009、Design §4 / §6、Plan S40B |
| D-360-004 | resolved | migration safety | Freshでもobsolete prune / provenance別prune | adopted | Genuine Freshではobsolete pruneをせず、update / uninstallもunknown / modified assetをpreserve-and-blockする | Requirement I360-RQ-007〜009、Design §6 / §7、Plan S45 / S55 / S70 |
| D-360-005 | resolved | recovery | 全体atomic rollback / phase markerによるforward recovery | adopted | Portable atomic rollbackを主張せず、full preflight、apply-time identity再検証、phase marker、same-package forward retry、post-verifyを採用する | Requirement I360-RQ-012 / 013、Design §6.3 / §8、Plan S30 / S60 / S70 |
| D-360-006 | resolved | compatibility | marker統合 / operation別marker維持 | adopted | Init / updateは新`.distribution-retry.json`、uninstallは既存`.uninstall-retry.json`を維持する。両marker / invalid markerはblockし、暗黙移行しない | Design §8.1、Plan S35 / S60 / S65 / S70 |
| D-360-007 | resolved | package authority | fallback / marker単独 / provider asset + recognized version anchors | adopted | `.gitignore`は必須provider assetだけをsourceとし、version markerはcanonical exact allowlist、version固有anchor、downgrade拒否を一体で検証する | Design §4.1 / §7.3、Plan §3.1 / S10 / S35 / S40B |
| D-360-008 | resolved | recovery | adversarial完全防御 / detected raceのfail-closed境界 | adopted | Operation全体のatomicityではなく、通常process / handled filesystem failureを保証する。Same-UID hostile tampering等は検知時fail-closedとforward recoveryの境界にする | Design §6.3 / §8、Plan S30 / S60 |
| D-360-009 | resolved | lifecycle | gate統合 / 独立gate | adopted | IC-1 / IC-2、dependency readiness、formal `issue start`、R/D/P review、Strict reviewを別gateとして扱う | Requirement I360-RQ-001、Plan §2 / S00 |
| D-360-010 | resolved | downstream | Issue 360内でIC-3を自己承認 / Epic ownerへhandoff | deferred | IC-3 pass、未承認final Issue候補、Epic completionはIssue 360自身で自己承認しない。Planningをblockしない理由は、IC-3が実装・検証後にだけ判定できるEpic-owned downstream gateだからである | Plan H10でEpic ownerへread-only handoffし、Issue 360 closure時に再判定する |

### Spec Authoring Gate / Planning gate ledger

| Phase | Canonical artifact | Reviewer | Status | Evidence / next action |
|---|---|---|---|---|
| Requirement | `requirement.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし。IC-1 / IC-2、Design promotion、formal start、implementation handoffは非承認 |
| Design | `design.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし、confidence 0.98。Plan phaseへ昇格 |
| Plan | `plan.md` | amendment後fresh review | passed | S40A verificationを既存Storage Core CLI testへ限定し、S20本文順・依存graph・gate metadataを確認 | Plan `approved` / `implementation-start-ready`、S10へhandoff |

### Reviewer Gate Status

| Gate | Reviewer | Freshness | State | Risk acceptance | Promotion decision |
|---|---|---|---|---|---|
| Requirement | `spec-reviewer` | fresh round 3 | passed | none | Requirement approved |
| Design | `spec-reviewer` | fresh round 3 | passed | none | Design approved |
| Plan | `spec-reviewer` | amendment後fresh review | passed | S40A verificationを既存Storage Core CLI testへ限定し、S20本文順・依存graph・gate metadataを確認 | Plan `approved` / `implementation-start-ready`、S10へhandoff |
| ChatGPT-SpecReview-Strict | ChatGPT browser-only exact-upstream review | amendment後exact-current review | passed | session `issue-360-admission-current-strict`でGitHub exact SHA `8c01c9fd2e76d7d7bccc754bca902e8010026703`を検証、resolved `GPT-5.5` verified、P0/P1なし | implementation admissionを解消し、S00 / S10を開始 |

### ChatGPT-SpecReview-Strict round 1

Pre-submit session `required-strict-github-connector-verificati-66`はChatGPTのrate-limit dialog再表示で停止した。Recovery診断では`promptSubmitted=false`、conversation IDなし、leaseなしであり、review結果として数えない。共有Pro sessionのterminal完了後、new-submission gateを満たすことを確認してfresh reviewを開始した。

Session `required-strict-github-connector-verificati-67`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。Requirement / Designにformal start前のcheckout-safety停止とreview未完了が現在形で残る一方、Report / Planはformal startとphase reviewの成功を記録しているため、S00の現在地が一意でないというP1を1件検出し、`review_status=fail`となった。

Findingはrepository factsと一致したため採用し、Requirement I360-RQ-001とDesign §1を最新lifecycle evidenceへ同期した。Product scope、migration contract、acceptance criteria、implementation stepは変更していない。修正commitを同名upstreamへpushし、別のfresh Strict conversationでexact-SHA re-reviewするまでimplementation blockを維持する。

### ChatGPT-SpecReview-Strict round 2

Session `required-strict-github-connector-verificati-68`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `4b325885b82dbffa26cdd5cd372d3914e8d604ef`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。P0 / P1はなく、`review_status=pass`、overall confidence 0.91である。Requirement / Design / Planはhard cutover、ownership / provenance、path safety、retry / recovery、Fresh / update / uninstall、parity、docs、IC-3 handoffを相互にtraceでき、実装開始を妨げる矛盾または必須欠落はないと判定された。

唯一のfindingは、親Epic Reportの進捗サマリーがIssue 360のDesign / Plan具体化中、formal start未完了のまま残るというP2であった。これは旧Planに対する履歴であり、S20順序のP1を受けてPlan amendmentとfresh gateを再開した。後続のround 3でamendment後SHAを再検証し、implementation-start-readyへ戻した。

### ChatGPT-SpecReview-Strict round 3（current admission）

Session `issue-360-admission-current-strict`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `8c01c9fd2e76d7d7bccc754bca902e8010026703`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。S20がS40A legacy Runtime retirementとS40B shipped Target physical cutoverの後に配置され、S40Aの検証が既存`tests/cli_runtime/test_storage_core_cli.py`へ限定され、S45がS35を前提とすることを確認した。Requirement / Design / Plan / Reportのgate状態もfresh local `spec-reviewer` passと整合し、P0 / P1なし、`review_status=pass`、overall confidence 0.92となった。この結果によりPlanを`approved` / `implementation-start-ready`へ維持し、S00 / S10を開始する。

### Design review round 1

Fresh reviewerは次のP1を検出し、Design / Plan / Decision Ledgerへ反映した。

* Preflight後も各mutationでrootからno-follow再bindし、device / inode / `ctime_ns` / type / link count / content identityを再検証する。差異時はpathname cleanupを行わない。
* Consumer-side manifestの自己申告を信頼せず、manifest自身のknown historical identityとprovider-private target path + target identityの両方を必須にした。
* Init / update用`.distribution-retry.json`と既存uninstall用`.uninstall-retry.json`を統合せず、dual / invalid markerをblockする一意なmigration契約へ決定した。
* `.gitignore`を必須provider assetとして単一distribution planへ含め、hard-coded fallbackを削除する方針を固定した。
* Provider / dogfood / testのAdd / Modify / Delete / Read-only treeとshared-symbol dependency deltaを追加した。

P2のrecognized / unrecognized `init --force`とmarker matrix、AC別verification trace、Decision Ledgerも同時に追加した。

### Design review round 2

別のfresh reviewerはround 1の5件が解消済みであることを確認したうえで、次の追加findingを検出した。

* `spec-dock.version`を「valid」とする構文、known-version admission、version固有anchor、実行中version、downgrade、retry例外を明文化した。
* Decision Ledgerの`Status`を解決状態、`Disposition`をadopted / rejected / deferredとして分離し、IC-3 deferredの非blocking理由とrevisit条件を記録した。
* Dependency diagramにTitle / Question / Scope / Excluded / Update triggerとedge labelを追加した。

Round 2のP1 / P2を反映済みとした。

### Design review round 3

別のfresh reviewerが最新Design / Reportをapproved RequirementとDesign phase基準へ再照合した。Round 2のversion admission predicate、Decision Ledger分離、dependency diagram metadata / edge意味はいずれも解消済みで、新規P0 / P1なし、confidence 0.98の`pass`と判定した。このpassによりDesignを`approved`へ昇格し、Plan reviewへ進む。

### Plan review round 1

Fresh reviewerはproduct scope / migration設計を概ね反映済みとしつつ、実装開始可能なcommand queueとして次のP1を検出した。

* S20〜S70のhorizontalなRED / layer batchingを、一つのobservable behaviorごとにRED / GREEN / review / commitを閉じるvertical sliceへ分解する。
* 全ACとfilesystem / marker / package / scope riskを追跡する`Spec-Locked Closure Index`を置く。
* 各implementation stepへdepends / unblocks、source、target、allowed / forbidden、delegated role、verification、stop、report、review / re-review、commit / cleanを固定する。
* S90をdocs impact、S99をqa / issue-wide code / specの三者final gateとし、IC-3 input handoffをその後のH10へ分離する。
* Repository root rebindとcross-root retry marker replayをzero-writeで拒否するnegative closureを追加する。

`implementation-planner`のread-only draftを上記findingへ限定して採用し、Plan §4〜§9をS00 / S10 / S20 / S25 / S30 / S35 / S40A / S40B / S45 / S50 / S55 / S60 / S65 / S70 / S80 / S85 / S90 / S95 / S99 / H10へ再構成した。Fresh round 2はpendingである。

### Plan review round 2

別のfresh reviewerはround 1の5件すべてが解消済みであることを確認した。新規P1として、Requirement / Designが要求するdiagnostic sanitationがrequired Closure Indexとstep-local negative testへ固定されていない点を検出した。

`C360-RISK-DIAGNOSTIC-SANITATION`をrequired closureとして追加し、S25 classifier diagnosticとS60 fault / retry diagnosticへcredential風文字列、source bytes、repository外absolute pathの非包含test、owner、verification command、report destinationを固定した。Fresh round 3を待つ。

### Plan review round 3

別のfresh reviewerがapproved Requirement / Designと最新Plan / Reportを再照合した。Diagnostic sanitationはrequired Closure Index、S25 / S60のstep-local negative test、verification command、report destination、S95 / S99まで追跡可能であり、round 1の5件にも回帰なし、新規P0 / P1なし、confidence 0.99の`pass`と判定した。このpassによりPlanを`approved`へ昇格した。

### Requirement review round 1

Fresh reviewerは次のP1を検出し、Requirementへ反映した。

* Planning selection、IC-1 / IC-2 handoff approval、Runtime dependency readinessを分離した。
* Storage Coreの決定論的な`.github/workflows/ci.yml`をTargetへ維持した。
* Obsolete pruneをexact pathではなくoperation × provenanceで判定し、ownership未証明時は全mutation前に停止する契約へ修正した。
* Root `README.md`、installed migration guide、retained scripts / system / template / Workbench MarkdownをCurrent docs auditへ追加した。

### Requirement review round 2

Fresh reviewerは、retained `.github/workflows/ci.yml`が利用者所有の同名workflowと衝突した場合の挙動をP1として検出した。Current target全般をmissing、byte-identical、proven historical、ownership unknownへ分類し、最後のclassは既存bytesを保持して全mutation前に停止する契約とacceptanceを追加した。

### Requirement review round 3

別のfresh reviewerがRequirementを親Epic、Issue 357〜359 handoff、installer / asset現物と再照合し、P0 / P1なしの`pass`と判定した。このpassはRequirement単体の品質gateであり、IC-1 / IC-2の充足、Design promotion、formal `issue start`、実装着手を承認しない。

### Lifecycle state

初回`issue start`はdependency readinessを満たさず実行開始を拒否した。利用者が指定したfallbackに従い、`active set iss-00360`でIssue 360を選択し、ユーザーがIssue 359 branchからIssue 360 branchを作成した。Issue 359 merge後はdependency `ready=true`となったが、再試行はdirty worktree safetyで停止した。IC-1 / IC-2とR/D/P reviewを閉じ、planning commitを同名upstreamへpushした後、formal `issue start iss-00360`を再実行してIssue checkout / auto-syncを含めsuccessした。Post-startもactive Issue、dependency、validation、local / upstream SHAを実測している。
