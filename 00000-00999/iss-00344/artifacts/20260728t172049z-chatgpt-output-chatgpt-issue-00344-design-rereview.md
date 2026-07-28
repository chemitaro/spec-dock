# Issue 344 Design Review

## Verdict FAIL

**FAIL**。

GitHub Connector で `chemitaro/spec-dock` の branch `iss-00344-workbench-shell-scaffolding` を開き、指定 commit `fc20546b1fd419badab636c8cefd97e8a9f3c9a7` と branch HEAD が identical であることを確認した。指定 commit は B-001〜B-003 および NB-001 の訂正を目的とする commit である。

pathname-based Git contract、generic exact-copy seam、package inventory root、copy compatibility、rollback、sibling ownership の主要な訂正方向は妥当である。一方、承認済み要件に対して **新たに確認された blocking contradiction が2件**残る。以前の B-001〜B-003 と NB-001 は再掲しない。

## Findings

### BLOCKING B-004 — 固定された canonical README 本文が、必須の `artifacts/` destination guidance を満たしていない

承認済み `I344-RQ-003` は、保存する一 file を「対象 scope の **`artifacts/`** へ明示 import する」と README に明示することを要求している。これは9つの必須 guidance element の一つである。

しかし、design が canonical bytes として固定した本文は、次のように「対象の root、Initiative、Epic、Issue の **Artifact へ**」とだけ記述している。

> 残す価値がある一つのファイルは、repository root から repo-local runtime を使い、対象の root、Initiative、Epic、Issue の Artifact へ明示的に import します。

直後の command spelling は正しいが、destination directory である `artifacts/` は本文に現れない。

「Artifact」という概念名だけでは、「対象 scope の `artifacts/` directory へ保存する」という requirement の具体的 guidance を一意に満たさない。しかも design はこの block を4 asset共通の canonical bytes としているため、この欠落は4 READMEすべてへ複製される。

**必須訂正:**

canonical block の該当文を、少なくとも次の意味が明示される形へ修正する。

> 対象の root、Initiative、Epic、Issue scope の `artifacts/` へ Artifact として明示的に import します。

修正後の完全本文を引き続き UTF-8、LF、末尾 newline 1つ、placeholder token 不在の canonical bytes とし、4 asset parity と guidance assertion の対象にする必要がある。

---

### BLOCKING B-005 — canonical wording の変更管理契約が design 内で自己矛盾している

`DES-344-003` は、fenced block を4 asset共通の canonical Markdown bytes とし、**wording 変更は design amendment と fresh review を要する**と規定している。

ところが `Open questions` では、次の自由変更を許している。

> exact README wording の可読性調整は9 guidance elementsとbyte parityを維持する限り許可する。

承認済み requirement も、README の exact wording は design で固定すると明記している。

この二つの design 規則は同時には成立しない。後者を採用すると、実装者は4 assetを byte-identical に保ちさえすれば、canonical blockを fresh reviewなしで一括変更できる。その場合、B-002訂正で導入した「レビュー可能な完全本文の固定」が再び無効になる。

**必須訂正:**

`Open questions` の可読性調整許可を削除するか、次のように限定する。

> README wording の可読性調整を含むすべての本文変更は、design amendment、4 asset canonical bytes の更新、および fresh design review を要する。

B-004 の本文修正も、この変更管理契約に従わせる必要がある。

---

### NON-BLOCKING NB-002 — exact five-file inventory が normalized root 相対の exact path 表記になっていない

design は探索 root を `spec_dock/assets/spec_dock/templates/` subtree に固定したが、allowlist は次のように記載されている。

* `templates/README.md`
* root `.workbench/README.md`
* Initiative `.workbench/README.md`
* Epic `.workbench/README.md`
* Issue `.workbench/README.md`

探索 root が `.../templates/` なら、最初の項目は `README.md` であるべきであり、残り4項目も node-kind label ではなく exact relative pathname にすべきである。親 Epic design には4 asset の具体的 path が記載されているため、意図自体は推定できる。

Standard-grade の machine-verifiable allowlist としては、次の5件へ正規化することが望ましい。

```text
README.md
root/.workbench/README.md
initiative/.workbench/README.md
epic/.workbench/README.md
issue/.workbench/README.md
```

これは局所的な表記訂正であり、単独では blocking としない。

## Scope and consistency checked

### Pathname-based Git contract

訂正後の design は次の3 ruleを固定している。

```gitignore
**/.workbench/*
!**/.workbench/README.md
**/.workbench/README.md/**
```

さらに tracking eligibility を entry type ではなく exact pathname identity と定義し、exact path の symlink は再包含され得ること、exact path が directory の場合は descendants を第三規則で ignore することを明示している。regular file、symlink、directory、directory descendant、nested/case variant/near-name を real Git matrix に含める設計もある。

これは、top-level `.workbench/README.md` のみを tracking 可能とし、nested README、case variant、その他 payload、near-name directory を対象外とする approved requirement と整合する。

以前の entry-type claim と pathname rule の矛盾は、design 上は解消されている。

### Canonical README bytes and text

design は4 provider assetについて、UTF-8、LF、末尾 newline 1つ、template placeholder token 不在、byte identity、完全な fenced canonical blockを定義した。repo-local exact command、node-scoped helper、root exclusion、evidence-only authorityも本文に含まれている。

ただし、B-004 の `artifacts/` destination欠落と、B-005 の変更管理自己矛盾により、canonical text contract はまだ promotion可能な状態ではない。

### Generic no-token exact-copy materialization

現行 provider sourceでは、root側 `_copy_file` は `shutil.copy2` により source fileをそのまま複製する一方、node scaffolder はUTF-8 templateを読み、replacementを行って text writeする。

訂正後の design は、replacement後のUTF-8 bytesがsource bytesと同一なら text rewriteを行わず exact byte copyし、replacementにより内容が変わる通常templateでは既存renderingを維持する generic primitiveを定義した。また、path、README、Workbenchを意味解釈する専用branchを禁止している。

この設計は、root/node間の異なるmaterialization seamを、README-specific special caseなしでbyte-stableにするものとして一貫している。B-003の設計上の矛盾は解消されている。

### Package subtree inventory and pruning

現行 `_prune_legacy_scaffold` は `templates/README.md` を除くnested `README.md`をすべて削除する。

現行 `pyproject.toml` も、hidden Workbench READMEを明示includeしておらず、`assets/spec_dock/templates/*/**/README.md` を広くexcludeしている。

design は pruneをexact allowlistへ変更し、4 hidden READMEをpackage dataへ明示追加し、source、wheel、normalized sdist、installed resourcesの探索をtemplate subtreeへ限定する責任を定義している。

設計方向は親 Epicと整合する。残る問題はNB-002のpath表記精度であり、package backendの実挙動は後続のbuild evidence対象である。

### Semantic opacity and copy compatibility

design は exact `.workbench` subtree のtop-down prune、READMEやmetadata-like file、binary、invalid UTF-8の非parse、validate/sync/dependency/active/source-manifestへの非参加を維持している。

現行 opacity tests は、exact `.workbench` 配下のfake metadataを発見せず、near-nameを通常どおり扱い、metadata walkerがWorkbench descendantへ入らないことを検証する構造である。

`workbench copy` についても、design は以下を維持している。

* Initiative / Epic / Issue のfull IDによるnode scope。
* root routeと `--root`、`--from`、`--date`、`--path` の拒否。
* opaque whole-tree source-wins。
* destination-only entry preservation。
* file/symlink object behaviorとentry-type collision。
* README-specific filterなし。
* automatic sync、watch、copy-backなし。

現行 application sourceはnode scopeを解決して `.workbench` 同士だけをcopyし、full non-local IDを要求する。  現行filesystem mergeもsource側entryだけを再帰処理し、regular fileまたはsymlinkをsource-winsで置換し、destination-only entryを保持する。

current testsも未公開routeの拒否と、copied metadata、ADR-like file、dependency-like fileのsemantic opacityを保持する構造である。

この領域に新たな blocking contradiction は確認しなかった。

### Rollback

design は、ignored payloadがGit statusへ露出する期間を避けるためignore contractを先に戻し、その後provider assets、installer branch、package config、tests、docsをrevertする順序を定義している。生成済みREADMEやuser Workbench contentは自動削除しない。

親 Epicも、旧ignore ruleを先に復元し、生成済みREADMEとuser evidenceを削除しない方針である。

rollback contract に blocking contradiction は確認しなかった。

### Sibling Issue boundaries

approved Issue requirement は、generic single-file importをIssue 345、candidate-wheel consumer E2E、dogfood、full regression、Epic-wide final reviewと送達をIssue 346へ割り当てている。

Issue designも、Issue 345をimport capability、Issue 346をcandidate wheel、dogfood、full regression、final deliveryのownerとし、Issue 344ではfocused package evidenceのみを扱う。 親 Epic planのCandidate 1 ownership、rollback、forbidden boundaryとも整合している。

sibling ownershipのscope creepやpremature completion claimは確認しなかった。

### Report alignment

`report.md` はB-001〜B-003およびNB-001の採用を記録している一方、design gateをfailed / blockingのまま保持し、fresh re-review後に次のreviewへ進む状態としている。

したがって、report上のgate状態は今回のFAIL判定と矛盾しない。

## Residual risks

* canonical READMEのB-004修正後、4 provider assets、fresh root output、3 node output、source/wheel/sdist/installed resourcesのすべてでbyte identityを確認する必要がある。
* generic exact-copy primitiveは、no-token UTF-8 templateではsource bytesをそのまま出し、replacement対象templateでは既存renderingを維持することを直接確認する必要がある。出力が偶然一致するだけのtext rewriteでは、cross-platform newline差を防げない。
* pathname contractのregular file、symlink、directory、directory descendant matrixは、実際のGit repositoryでの後続検証対象である。
* hidden `.workbench/README.md` のwheel、sdist、installed-resource収録はbuild artifactによる後続検証対象であり、現時点では未確認である。approved requirementもこの点を未検証事項としている。
* 本レビューは指定commit上の文書、provider source、test sourceの静的確認であり、pytest、real-Git matrix、wheel/sdist buildは実行していない。

## Promotion decision

**design phase から plan phase への昇格不可。**

昇格前に、少なくとも次を canonical `design.md` へ反映する必要がある。

1. canonical README本文へ対象 scope の **`artifacts/`** destinationを明示する。
2. wordingの自由な可読性調整を許す記述を削除し、すべての本文変更をdesign amendmentとfresh reviewの対象に統一する。
3. NB-002のfive-file inventoryをnormalized subtree root相対のexact pathへ正規化する。

その後、fresh design re-reviewおよびfresh `spec-reviewer` reviewを行う。

本判定は **advisory / evidence-only** であり、実装、テスト合格、PR、merge、Issue finishを示さない。
