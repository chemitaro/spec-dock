# Issue 344 Design Review

## Verdict FAIL

**FAIL**。

GitHub Connector で `chemitaro/spec-dock` の branch `iss-00344-workbench-shell-scaffolding` を確認し、branch HEAD が指定 commit `17bbc14e27c4fb759da0de373028920af36eccb3` と一致することを確認した。

指定されていた訂正は canonical `design.md` と `report.md` に反映されている。しかし、現行 packaging source との再照合により、**新たな blocking contradiction が1件**確認された。解消済みの finding は再掲しない。

## Findings

### BLOCKING B-006 — `setup.py` の post-build README prune が設計責任から漏れており、wheel / installed-resource parity を成立させられない

承認済み要件は、4つの Workbench README asset を source、wheel、sdist、installed package resources の全 surface に収録し、template README inventory を既存 `templates/README.md` と4つの Workbench READMEだけに限定することを要求している。`AC-344-008` も同じ exact inventory と4 READMEの byte parity を closure 条件にしている。

現在の設計は、distribution 対応として次を規定している。

* installer 側 `_prune_legacy_scaffold` の exact allowlist 化
* `pyproject.toml` の broad nested README exclusion の修正
* package data への4 assetの明示追加
* source / wheel / sdist / installed resources の5-path inventory検証

しかし、設計の source map とファイル責任表は packaging source を `pyproject.toml` に限定しており、`setup.py` を変更対象または検証対象に含めていない。

現行 `setup.py` には、次の独立した build-output prune が存在する。

```python
"spec_dock/assets/spec_dock/templates/*/**/README.md",
```

この pattern は、追加予定の次の4 pathをすべて包含する。

```text
spec_dock/assets/spec_dock/templates/root/.workbench/README.md
spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md
spec_dock/assets/spec_dock/templates/epic/.workbench/README.md
spec_dock/assets/spec_dock/templates/issue/.workbench/README.md
```

さらに、custom `build_py` は通常の build copy 後に `_prune_stale_build_outputs()` を実行するため、`pyproject.toml` 側で4 assetを package dataへ含めても、build treeから改めて削除する構造になっている。

本 repository は `setuptools.build_meta` を build backend とし、`setup.py` はこの custom `build_py` / `sdist` を `cmdclass` として登録している。したがって、この seam は dead code ではなく package build boundary の一部である。

そのため、現在の設計をそのまま実装した場合、少なくとも wheel とそこから得られる installed resources について、設計自身の `TC-344-008` および承認済み `AC-344-008` を満たせない。これは「build artifactで後から確認すればよい未知の挙動」ではなく、現行 source に存在する既知の削除経路である。

**必須訂正:**

1. `setup.py` を設計の source map、`DES-344-008`、ファイル責任表、rollback 対象へ追加する。

2. `_STALE_BUILD_OUTPUT_PATTERNS` の broad nested README patternを単純削除するだけでなく、build treeに残留した legacy READMEを引き続き削除しつつ、正規化した template root相対の次の5 pathだけを保存する exact allowlist-aware pruneへ変更する設計を定義する。

   ```text
   README.md
   root/.workbench/README.md
   initiative/.workbench/README.md
   epic/.workbench/README.md
   issue/.workbench/README.md
   ```

3. `TC-344-008` を、`pyproject.toml` の package-data設定だけでなく、custom `build_py` の post-build pruneを実際に通る検証として明示する。

4. 親 Epic が focused verification seamとして指定している `tests/unit/infra/test_init_update.py` で、少なくとも次を区別して検証する。

   * 4つの allowlisted hidden README は build prune後も残る。
   * allowlist外の stale nested README は引き続き除去される。
   * wheel / normalized sdist / installed resources の inventoryとbytesが設計上の契約と一致する。

## Scope and consistency checked

### Approved Issue requirement

`requirement.md` は `approved` であり、fresh root、future node、byte-identicalな4 README、README-only tracking、no-backfill、semantic opacity、node-scoped manual copy、provider/distribution parity、documentationを Issue 344 の責務としている。generic import実装とEpic-wide最終統合は sibling Issueへ分離されている。

指定された3件の訂正については、canonical README、変更管理契約、normalized template-root相対の5-path inventoryへ反映されていることを確認した。

### Freshness and no-backfill

設計は installer mutation 前に `os.path.lexists` 相当で freshness を固定し、root READMEを fresh rootにだけ配置する。future nodeは既存 generic recursive template copyに載せ、ancestor / siblingを変更しない。これは承認済み no-backfill contractと整合する。

現行 installer は `spec-dock` directoryの生成後にmanaged assetsを同期し、nested READMEを一律pruneしているため、設計で freshness判定とexact preserve ruleを明示する必要性もsource上確認できる。

この領域に、B-006以外の新たな blocking contradiction は確認しなかった。

### Git-ignore contract

設計は providerとfallbackの双方に次の pathname-based contractを固定している。

```gitignore
**/.workbench/*
!**/.workbench/README.md
**/.workbench/README.md/**
```

regular file以外のexact path、nested / case variant、directory descendant、near-name pathを含むreal-Git matrixも設計されている。

承認済み要件の「exact top-level pathnameだけをtracking可能にし、その他を深さ・形式によらずignoreする」という境界と整合する。

### Semantic opacity

設計は exact `.workbench` subtreeのtop-down pruneを維持し、README、metadata-like file、ADR-like Markdown、binary、invalid UTF-8をsemantic inputにしない。

現行 test sourceも、exact `.workbench` 配下のfake metadataを発見対象から外し、near-name directoryは通常どおり扱い、walkerがWorkbench descendantへ入らないことを検証する構造である。

### Node-scoped copy compatibility

現行 application sourceはInitiative / Epic / Issueのfull non-local IDだけを受け付け、source / target nodeそれぞれの `.workbench` を解決してfilesystem gatewayへ渡す。root scopeは公開していない。

現行filesystem test sourceでは、source-wins、destination-only preservation、idempotence、opaque ordinary bytes、symlink object behaviorが直接固定されている。

CLI test sourceも未公開のroot / source-selection routesを拒否し、copied metadata・ADR-like file・dependency-like fileがvalidate / sync / depsへ影響しない構造を持つ。

設計がこれらのsourceとtestsをread / verify onlyとし、README-specific filterを禁止している点に、新たな矛盾は確認しなかった。

### Parent Epic and sibling ownership

親 Epic planは、hidden README package-data、broad nested README exclusionの修正、source / wheel / sdist / installed inventoryを明確にIssue 344へ割り当てている。したがって `setup.py` のbuild prune修正はIssue 346のfinal E2Eではなく、Issue 344のpackage correctnessに属する。

generic file importをIssue 345へ残す境界には問題を確認しなかった。

### Report alignment

`report.md` は指定訂正の採用を記録している一方、design authoring gateをまだ `failed` / `blocking=yes` のまま維持し、fresh review後の判断待ちとしている。

したがって、report上にprematureなdesign promotion evidenceはない。B-006は新しいledger entryとして記録する必要がある。

## Residual risks

* 本判定は指定commit上の文書、provider source、package configuration、test sourceの静的レビューである。pytest、real-Git matrix、wheel / sdist build、installed-resource検査はこのレビューでは実行していない。
* B-006修正後も、4 provider assets、fresh root output、3 node outputs、wheel、normalized sdist、installed resources間のbyte identityは実測証跡で閉じる必要がある。設計自身もこれを `TC-344-003` / `TC-344-008` に割り当てている。
* generic exact-copy branchは、no-token READMEではsource bytesをそのまま保持し、replacement対象templateでは既存renderingを維持することを区別して確認する必要がある。
* real-Git ignore matrixは、regular file、symlink、directory、directory descendant、nested / case variant / near-nameを実repositoryで確認する後続証跡を要する。
* `report.md` のdesign gate状態と採用台帳は、B-006の設計訂正およびfresh review結果に合わせて更新する必要がある。

## Promotion decision

**design phaseから次のphaseへの昇格は支持しない。**

`setup.py` のactive post-build pruneを設計責任へ取り込み、exact allowlist-aware cleanup、focused build test、rollback対象をcanonical `design.md` に追加したうえで、fresh design reviewを行う必要がある。

本判定はadvisory / evidence-onlyであり、phase promotionそのものを確定するものではない。
