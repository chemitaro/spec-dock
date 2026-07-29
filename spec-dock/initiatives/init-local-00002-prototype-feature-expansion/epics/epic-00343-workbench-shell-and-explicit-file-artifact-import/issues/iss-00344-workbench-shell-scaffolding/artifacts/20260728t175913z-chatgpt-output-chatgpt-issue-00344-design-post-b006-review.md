# Issue 344 Design Review

## Verdict PASS

**PASS**。

GitHub Connector で `chemitaro/spec-dock`、branch `iss-00344-workbench-shell-scaffolding`、指定 commit `dae3c3485cd29e63e72a3258178f186160e9ceb3` を確認した。指定 commit と branch HEAD は一致している。

訂正後の `design.md` は、現行の active な custom `build_py` post-build prune を Issue 344 の設計責任へ取り込み、正規化した5つの README pathだけを保存しつつ、allowlist外の stale nested READMEを除去する契約まで定義している。承認済み要件、親 Epic、provider source、packaging source、関連test sourceとの間に、新たな blocking contradictionは確認しなかった。

## Findings

新規 finding はない。

* **Blocking:** 0
* **Non-blocking:** 0

解消済みの過去 finding は再掲しない。

## Scope and consistency checked

### Active custom `build_py` boundary

現行 build backend は `setuptools.build_meta` であり、`setup.py` は独自の `build_py` と `sdist` を `cmdclass` へ登録している。`build_py.run()` は通常の `super().run()` 後に `_prune_stale_build_outputs()` を必ず呼ぶため、この処理は dead codeではなく、wheel build treeへ実際に作用する packaging boundaryである。

現行 prune patternには `spec_dock/assets/spec_dock/templates/*/**/README.md` が含まれ、追加予定の4つの hidden Workbench READMEを包含する。一方、既存の stale-output fixtureには `issue/legacy/README.md` が含まれており、修正後もこの非allowlist READMEを削除し続ける必要がある。

### B-006 correction coverage

訂正後の設計は `setup.py` を source mapへ追加し、現状分析でも custom `build_py` が4つの Workbench READMEを削除することを明示している。

`DES-344-008` は、単に broad patternを削除するのではなく、`_prune_stale_build_outputs()` を normalized template-root-relative exact allowlist-aware cleanupへ変更し、次の5 pathだけを保存するよう規定している。

```text
README.md
root/.workbench/README.md
initiative/.workbench/README.md
epic/.workbench/README.md
issue/.workbench/README.md
```

同時に、allowlist外の stale nested READMEは引き続き除去すること、source・wheel・normalized sdist・installed resourcesのinventoryをこの5 pathに限定すること、4つの Workbench READMEのbytesを全surfaceで比較することも明記されている。

この責任はファイル責任表の `setup.py` 行、`TC-344-008` の actual post-build prune検証、rollback対象にも反映されている。`TC-344-008` は、custom `build_py` を実際に通したうえで、4つの hidden READMEが残ること、非allowlist stale nested READMEが消えること、全distribution surfaceのexact inventoryとbytesが一致することを `tests/unit/infra/test_init_update.py` で検証する設計である。

### Approved Issue requirementとの整合

承認済み `requirement.md` の `I344-RQ-008` は、4つのWorkBench READMEをsource tree、wheel、sdist、installed package resourcesへ収録し、template README inventoryを既存 `templates/README.md` と4つの Workbench READMEだけに限定し、allowlist外のnested READMEを配布しないことを要求している。`AC-344-008` も同じexact inventoryと4 READMEのbyte parityをclosure条件にしている。

訂正後の `DES-344-008` と `TC-344-008` は、この要件を build後の削除経路まで含めて具体化しており、要件の縮小、過剰拡張、surface漏れは確認しなかった。

### Parent Epicとの整合

親 Epicは、existing `workbench copy` のsource-wins境界を維持することと、provider implementation・packaged assets・consumer間のparityを要求している。

親 Epic planは Issue 344をWorkbench shellのprimary ownerとし、hidden README package-data、broad nested README exclusionの限定、source・wheel・sdist・installed resourcesのexact inventory、allowlist外nested READMEの不存在をfocused verificationへ割り当てている。Issue 346はcandidate wheelを含む最終distribution integrationを所有するが、Issue 344自身のpackage correctnessを肩代わりする境界ではない。

したがって `setup.py` のpost-build prune修正を Issue 344へ追加したことは、sibling scopeの侵食ではなく、親から割り当てられたfocused shell packaging responsibilityのsource-level具体化である。

### `pyproject.toml` との整合

`pyproject.toml` 側にも、現行の broad nested README exclusionである `assets/spec_dock/templates/*/**/README.md` が存在する。したがってpackage parityには、宣言的なexclude-package-dataと、`setup.py` のpost-build pruneの両方を修正対象にする必要がある。訂正後の設計はその二重境界を明示的に扱っている。

### Provider sourceと既存compatibility

現行installerの `_prune_legacy_scaffold` は `templates/README.md` 以外のnested READMEを一律削除するため、installer側にも同じexact allowlist化が必要である。訂正後の設計は、installer pruneとbuild-output pruneを別々の責任として扱っており、一方だけを直して完了とする構造にはなっていない。

node scaffolderはtemplate tree内のfileをgenericに再帰列挙してmaterializeするため、`.workbench/README.md` をprovider templateへ追加する設計と整合する。設計がREADME専用のnode-kind branchを追加せず、generic byte-stable primitiveとして扱う方針にも矛盾はない。

既存 `workbench copy` はfull Initiative／Epic／Issue IDだけを受け付け、root scopeを公開していない。またfilesystem copyはsource entryだけを再帰処理するopaque source-wins mergeであり、README専用filterを持たない。訂正後の設計はこれらをread／verify-only boundaryとして維持している。

関連test sourceも、exact `.workbench` subtreeのtop-down opacity、near-name directoryの非除外、root routeの拒否、copied metadata／ADR-like file／dependency-like fileのsemantic opacityを検証する構造である。設計変更がこの既存境界を緩める記述はない。

### Report alignment

`report.md` の Evidence Adoption LedgerはB-006を採用し、`setup.py` をsource map、`DES-344-008`、責任表、`TC-344-008`、rollbackへ反映したことを記録している。

Spec Authoring GateがまだB-006を理由に `failed`／`blocking=yes` としているのは、このfresh review結果をまだ採用していない現在のworkflow stateであり、訂正後designとの実質的な矛盾ではない。

## Residual risks

**未検証:** 本レビューは指定commit上の文書、packaging source、provider source、test sourceの静的レビューである。pytest、wheel／sdist build、custom `build_py` の実行、installed-resource inspectionは実行していない。

**後続証跡:** 実装段階では `TC-344-008` に従い、少なくとも次を実測で閉じる必要がある。

* custom `build_py` のpost-build prune後も4つのallowlisted hidden READMEが残る。
* `issue/legacy/README.md` 相当の非allowlist stale nested READMEは除去される。
* normalized template root下のREADME inventoryは全surfaceでexact five pathsとなる。
* 4つのWorkbench READMEはsource、wheel、normalized sdist、installed resourcesでbyte-identicalとなる。

**台帳更新:** このadvisory verdictをcanonical workflowで採用する場合、`report.md` のdesign gateとEvidence Adoption Ledgerをfresh review結果へ更新する必要がある。これはpromotion手続上の残作業であり、design内容のblocking contradictionではない。

## Promotion decision

**design phaseから次のplanning phaseへの昇格を支持する。**

指定されたB-006の既知の削除経路は、訂正後designで次のすべてに反映されている。

* active `setup.py` build boundary
* normalized exact five-path allowlist
* 非allowlist stale nested READMEの継続除去
* actual post-build pruneを通るfocused verification
* file responsibility
* rollback
* Issue 344／346間のownership境界

本判定はadvisory／evidence-onlyである。実装完了、test成功、PR作成、merge、Issue完了、または実際のphase promotionを主張するものではない。
