# Issue 344 Plan Re-review

レビュー対象は GitHub connector で取得した `chemitaro/spec-dock`、branch `iss-00344-workbench-shell-scaffolding`、commit `1c98baabbde0cf9a7535cd91d6760012439e5e24` である。branch と指定 commit の比較結果は `identical` であり、commit は先行 plan-review の B-001/B-002 を反映したものとして取得できた。

## Verdict PASS

**blocking contradiction、material execution gap ともに残っていない。**

修正版 `plan.md` は、承認済み `requirement.md` / `design.md` の契約を変更せず、先行指摘で不足していた以下を実行可能な粒度まで具体化している。

* generic unchanged-byte exact-copy の実装変更面、Closure、Red/Green、exact test node、placeholder-render・path-agnostic guardrail
* custom `build_py` の seed → pre-prune snapshot → post-prune 結果を含む distribution test
* repository 外 temporary build、wheel / sdist / installed-resource の正規化 inventory と byte parity
* scoped Ruff、Ruff format、Mypy、`git diff --check` の exact command と report destination

したがって、先行 B-001/B-002 は解消済みと判断する。

## Findings

**Blocking findings: なし。**

**Material execution gaps: なし。**

**新規 non-blocking finding: なし。**

## Scope and consistency checked

### Generic unchanged-byte exact-copy

承認済み `DES-344-002` は、UTF-8 template について replacement 後の bytes が source bytes と同一なら text rewrite を行わず exact-copy し、bytes が変化する placeholder template は従来の rendering を維持することを normative contract としている。また、この分岐は README、Workbench、path を意味解釈しない generic primitive でなければならない。

修正版 plan では、この契約を実装する `template_scaffolder.py` が明示的な許可変更面へ移され、copy/discovery の read-only 3ファイルとは区別された。承認済み exact-copy branch は design amendment を要する変更ではなく、本Issueの実装対象であることも明記されている。

検証閉包も十分に具体化されている。

* `TC-344-002B` が real provider scaffolder による unchanged-byte exact-copy と placeholder rendering を専有する。
* `B-003` が generic recursion、exact-copy、placeholder render を一つの behavior として結ぶ。
* 3つの exact pytest node が、unchanged UTF-8、changed placeholder、path-agnostic behavior を個別に固定する。
* CRLF を含む path-neutral fixture により、`read_text` → `write_text` による newline normalization を検出する。
* 結果は `EVD-002/003` に Red/Green、fixture bytes、render result、path-agnostic assertion として記録する。

これは現行 source seam とも整合する。現在の `copy_scaffolded_tree()` は、UTF-8 decode 可能な file を常に `write_text(render_text(...))` し、`shutil.copy2` は decode failure 時だけ使用しているため、実装変更が実際に必要である。

また、既存 node test の stub scaffolder も UTF-8 text を常に render/write しており、node path parity test だけでは exact-copy を証明できない。修正版 plan が stub に依存せず real provider 用の独立 test file/node を置いたことは、この偽陽性経路を正しく閉じている。

**確認結果:** generic unchanged-byte exact-copy は許可された実装変更であり、専用 Closure、TDD、exact test node、placeholder-render、CRLF、path-agnostic の各 guardrail が揃っている。

### Distribution、custom `build_py`、inventory、installed resources

承認済み要件は、template subtree の README inventory を次の正規化5 pathだけに限定し、source、wheel、sdist、installed package resources の全 surface で inventory と4 Workbench README bytesを一致させることを要求している。

承認済み設計も、`pyproject.toml` の broad exclusion、`setup.py` の custom `build_py` post-build cleanup、allowlist 外 stale nested README の除去、全 surface の normalized five-path inventory を同じ契約として固定している。

現行 source には、この検証に必要な seam が実在する。

* broad nested README prune pattern

* stale `issue/legacy/README.md` fixture

* `SPEC_DOCK_BUILD_PY_SEED_STALE_FIXTURES`

* `SPEC_DOCK_BUILD_PY_PRE_PRUNE_SNAPSHOT`

* `super().run()` → seed → snapshot → prune の順序

`pyproject.toml` 側にも、現時点では4 Workbench READMEを落とす broad exclusion が残っており、package-data/exclude-package-data の変更対象が plan と一致する。Ruff、Mypy の configured surfaceも、planに列挙された static commandと整合している。

修正版 M3 は、正式な2つの pytest nodeへ次の責任を集約している。

1. `build_py` の stale seed と pre-prune snapshotを有効化する。
2. prune前に allowlist / stale fixture が存在することを確認する。
3. post-prune wheelで5 pathを保存し、allowlist外 stale READMEだけを除去する。
4. repository外 `TemporaryDirectory` に build context、wheel、sdist、venvを作る。
5. `python -m build --wheel --sdist --no-isolation --outdir <temporary-dist>` を実行する。
6. wheel ZIP、sdist TAR、installed resourcesを同じ template-root-relative pathへ正規化する。
7. temporary wheel install後に `importlib.resources` から4 assetを読み、source bytesと照合する。

Gate は曖昧な `-k` selector や単独の `uv build` ではなく、2つの正式 node名を列挙している。さらに、変更対象に対する Ruff check、Ruff format check、Mypy、diff checkを exact commandとして固定し、distribution結果を `EVD-007`、static結果を `EVD-011` へ送る。

repository-managed wheelhouse と hermetic build/install helper は既存 package-parity workで導入済みであり、`build`、`setuptools`、`wheel`、`packaging`、`pyproject_hooks` を temp venvへ供給する既存 seamを再利用するという plan の前提にも根拠がある。

**確認結果:** custom build seed/pre-prune/post-prune、repository外 build、wheel/sdist/installed inventory、temporary resources、byte parity、scoped static commands、report destinationsが、設計判断を実行者に委ねない exact node/command 契約として閉じている。

### Parent Epic、Issue report、sibling boundary

親Epicでは Issue 344 が shell、package-data、source/wheel/sdist/installed resource の focused evidenceを所有し、Issue 346が candidate wheel consumer E2E、dogfood projection、full regression、Epic-wide review、PR deliveryを所有する。修正版 plan はこの分担を維持し、本Issueで final distribution closureやPR/mergeを主張していない。

`report.md` は B-001/B-002 の採用と plan 修正を `EAL-015` に記録し、次のゲートを fresh ChatGPT re-review、その後の fresh `spec-reviewer` reviewとしている。plan phaseがまだ failed/blocking 表示なのは、本レビュー結果を採用する前の正しい workflow stateである。

添付の「設計判断と提案」は Issue 344 の repository正本とは異なる内容であるため、本判定の根拠には使用していない。

## Residual risks

* 本判定は plan の静的レビューであり、記載された pytest、build、temporary install、Ruff、Mypy、diff commandは実行していない。テスト成功や配布物の実測結果は未検証である。
* 対象 commitの provider実装は依然として UTF-8 fileを常に text rewriteする状態である。したがって、このPASSは変更計画の完全性に対するものであり、exact-copy実装済みという意味ではない。
* 現行 pre-prune snapshot payloadは主に seeded stale fixtureの存在を記録する。実装時には、planが要求する allowlisted READMEのpre-prune presenceも同じ exact nodeから観測可能にする必要がある。`setup.py` は許可変更面に含まれ、期待結果と停止条件も既に固定されているため、これは未解決のplan gapではなく実装時の検証義務である。
* hidden directoryのbackend-specific収録挙動は、引き続き implementation evidenceで閉じる対象である。inventory欠落、余剰README、byte mismatchのいずれかが出た場合はM3を失敗させ、設計を推測で緩和してはならない。

## Promotion decision

**Advisory plan re-review: PASS**

`plan.md` は fresh `spec-reviewer` reviewへ昇格してよい。requirement または design amendmentへ戻す必要はない。

次の正規ゲートは以下である。

1. 本PASSを `report.md` の Evidence Adoption Ledger / Spec Authoring Gateへ反映する。
2. fresh `spec-reviewer` が requirement、design、plan、reportの整合を独立確認する。
3. その reviewでも blocking findingが0の場合に限り、planの implementation-start gateを満たしたものとして扱う。

本レビューは、実装完了、テスト成功、PR準備、PR作成、merge、Issue完了のいずれも認定しない。
