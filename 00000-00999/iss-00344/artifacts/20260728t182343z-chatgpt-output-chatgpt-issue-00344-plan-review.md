# Issue 344 Plan Review

## Verdict FAIL

GitHub connector で `chemitaro/spec-dock` の branch `iss-00344-workbench-shell-scaffolding` と commit `4c03920ae7ad4fc538a295e895d0e87634d1b390` を確認した。branch と指定 commit の比較結果は `identical` であり、本レビューの対象 HEAD は指定どおりである。

`plan.md` は、3つの vertical micro-batch、Closure Index、Standard/TDD の骨格、exact five-path distribution contract、証跡台帳、停止規則、Issue 346 への deferred delivery、human-only merge 境界を概ね正しく反映している。

ただし、**承認済み設計を実装するために必要な provider 変更を read-only にしている blocking contradiction** と、**distribution/static validation を再現可能にする exact command が不足している material execution gap** が残る。したがって、実装開始へ昇格できない。

## Findings

### B-001 — Generic exact-copy 契約の実装対象が read-only にされている

**分類:** Blocking contradiction

承認済み `DES-344-002` は、generic scaffolder について次を normative contract として固定している。

* placeholder replacement 後の UTF-8 bytes が source bytes と同一なら、text rewrite を行わず exact byte copy する。
* その primitive は README や Workbench を意味解釈しない generic contract とする。
* root の既存 exact-copy seam と node の generic exact-copy branch により、4出力を同一 bytes にする。

しかし、現行 `template_scaffolder.copy_scaffolded_tree()` は UTF-8 として読めるファイルを常に `read_text` → `render_text` → `write_text` している。`shutil.copy2` が使われるのは UTF-8 decode に失敗した場合だけであり、「render 後も bytes 不変なら exact copy」という branch は存在しない。

一方、plan は `template_scaffolder.py` を原則 read/verify-only に置き、runtime contract の変更が必要なら実装を停止して design amendment へ戻るとしている。 しかし、この変更は新しい設計判断ではなく、**すでに承認済み design が要求している実装そのもの**である。

Closure Index と M1 の実行内容も、この sub-contract を閉じていない。

* `TC-344-002` は future 3 node の path parity のみ。
* `TC-344-003` は4 README asset の byte parity と guidance のみ。
* `B-003` は generic recursion による node 生成のみ。
* M1 の test seeds も asset、root freshness、ignore、node path、不変性が中心で、generic unchanged-byte exact-copy の Red/Green がない。

さらに、予定されている node test の現行 stub scaffolder 自体も UTF-8 text を読み、render 後に `write_text` する実装である。そのため、planned/result/filesystem path parity test は、実 provider の exact-copy primitive が未実装でも Green になり得る。

**必要な plan 修正:**

1. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py` を B-003 / M1 の allowed change surface に移す。
2. `DES-344-002` の generic exact-copy contract に専用の Closure または明示的な `TC-344-002` sub-closure を割り当てる。
3. 実 provider scaffolder を通し、replacement による bytes 変更がないファイルが text rewrite ではなく exact-copy seam を通ることを検出する Red/Green test を指定する。
4. placeholder を含む通常 template は従来どおり render されること、README-specific/path-specific branch が追加されないことも同じ cycle の guardrail にする。
5. focused command と Report evidence destination を明記する。

この修正では requirement/design amendment は不要である。逆に generic exact-copy contract を撤回する場合だけ、design amendment と fresh design review が必要になる。

---

### B-002 — Distribution gate と static gate の exact command が不足している

**分類:** Material execution gap / Blocking

M3 は正しい成果を列挙している。

* installer prune と custom `build_py` post-build prune で exact five-path inventory を保存する。
* allowlist 外 stale nested README を除去する。
* source、wheel、normalized sdist、installed resources の inventory と bytes を照合する。
* custom build path を実際に通す。
* temporary install 後に `importlib.resources` で assets を読む。

しかし、Gate に固定されている command は次だけである。

```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'workbench_readme or stale_build'
uv build
uv run pytest tests/unit/infra/test_init_update.py
git diff --check
```

また、「build artifact inspection は repository 外の temporary directory で行う」とだけ記載されている。

この記述からは、以下を一意に実行できない。

* repository 外の build/output directory をどの command で作成・指定するか。
* wheel と sdist のどちらを、どの normalized subtree root から inventory 化するか。
* sdist 展開、wheel 展開、temporary installation、`importlib.resources` 読み出しをどの test node または command が担当するか。
* setup.py の post-`super().run()` prune に stale fixture が実際に入り、prune 前後をどの exact invocation で観測するか。
* `-k '... or stale_build'` が選択する予定 test の正式名称。
* scoped Ruff、Mypy、その他 configured static checks の exact command。

Final Quality Gate も static verification を「configured focused lint/type checks」、distribution を「`uv build` + exact inventory/resource tests」としており、実行 command または test node が未固定である。 Standard plan contract は focused verification、milestone gate、final gate について command/evidence を具体化することを要求している。

現行 `setup.py` には、この検証に利用できる明示的な seam がすでにある。

* broad `templates/*/**/README.md` prune pattern。
* stale fixture seed。
* `SPEC_DOCK_BUILD_PY_SEED_STALE_FIXTURES`。
* `SPEC_DOCK_BUILD_PY_PRE_PRUNE_SNAPSHOT`。
* `super().run()` 後の seed、snapshot、prune 順序。

また、`pyproject.toml` には現在も nested README の broad exclusion が存在する。 承認済み design は、これらを変更して次の normalized template-root-relative five paths だけを全 surface に残すと固定している。

1. `README.md`
2. `root/.workbench/README.md`
3. `initiative/.workbench/README.md`
4. `epic/.workbench/README.md`
5. `issue/.workbench/README.md`

**必要な plan 修正:**

1. custom `build_py` の seed、pre-prune snapshot、post-prune inventory を検証する正式 test node を明記する。
2. `-k` expression がその test node を確実に選択するように名称を固定する。
3. repository 外 temporary output、wheel/sdist 展開、temporary install、installed-resource inspection を一つの exact pytest nodeに封じ込めるか、それぞれの exact commandを列挙する。
4. 5-path inventory の比較 root と normalization ruleを各 command/testへ結び付ける。
5. Ruff、Mypy、format/diff について、この Issue の changed paths を対象にした exact commandを記載する。
6. 各 command の結果を `EVD-007` または static evidence の明示的な Report destination に対応付ける。

現状では executor が build/installation/inventory workflow を補って初めて evidence を作れるため、「設計判断を発明せずに実行可能」という基準を満たさない。

## Scope and consistency checked

以下を指定 commit 上で照合した。

| 対象                                  | 確認結果                                                                                                                         |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Issue requirement/design            | approved contract、AC-344-001〜010、DES-344-001〜009、exact five-path inventory、rollback、sibling ownershipを確認                     |
| Issue plan                          | S01〜S03、M90/M99、Closure Index、Behavior Backlog、Active TDD、EVD、stop/amendment、handoffを確認                                      |
| Issue report                        | EAL/OAL/Spec Authoring Gate、plan phase pending、observed-evidence ledger の役割を確認                                               |
| Parent Epic requirement/design/plan | Candidate 1/2 → Issue 346 integration、no per-Issue PR、final PR delivery と human merge boundaryを確認                            |
| Installer/provider                  | `src/spec_dock/cli.py`、provider `.gitignore`、template scaffolder、node create、Workbench copy、filesystem opacity/copy seamsを確認 |
| Packaging                           | `setup.py` custom `build_py`、stale fixture seam、`pyproject.toml` package-data/exclude-package-dataを確認                        |
| Tests                               | installer、node creation、opacity、linked-worktree/copy の指定 test surfacesを確認                                                    |
| Assurance                           | `.assurance.json` の authorized profile `standard` と Standard plan template obligationsを確認                                    |

特に、次の部分は plan と上位仕様が整合している。

* S01、S02、S03 の順序と reviewable micro-batch 境界。
* AC-344-001〜010 と `TC-344-001〜010` の大枠の対応。
* exact five-path inventory、stale nested README 除去、4 asset byte parity の目標。
* semantic opacity、node-scoped source-wins copy、root selector rejection の維持。
* `EVD-001〜010` の evidence categories と、未実施 command を PASS と扱わない規則。
* requirement/design/scope/assurance gap 発見時の停止・戻り先。
* Issue 345 の generic import と Issue 346 の consumer E2E、dogfood、full regression、PR delivery の分離。
* Issue 346 が Issue 344/345 に依存し、per-Issue PR を作らず、最終 PR 後も human merge 前で停止する親 Epic 境界。
* plan 自身の follow-up と human-only boundary。

`.assurance.json` は authorized profile を `standard` とし、source binding に requirement/design/plan を保持している。 Plan の Standard 構造は概ね充足しているが、B-001 と B-002 により実行契約の閉包が未完成である。

添付の「設計判断と提案」は Issue 344 の GitHub 正本とは異なる内容であり、本判定の仕様根拠には採用していない。

## Residual risks

* 本レビューは repository の静的 inspection であり、pytest、build、lint、type check、temporary install は実行していない。したがって、既存テストの成否や packaging backend の実測結果は未検証である。
* packaging backend の hidden subtree 処理は、承認済み design 自身も implementation evidence で閉じる対象としている。これは設計 open question ではないが、B-002 の exact command/test binding がなければ再現可能な証跡にならない。
* `report.md` の Spec Authoring Gate では plan が `pending`、blocking が `yes` とされているため、現時点で execution-ready を主張する根拠はない。

## Promotion decision

**Plan promotion: BLOCKED**

次の条件を満たすまで `plan.md` を implementation-ready として昇格すべきではない。

1. B-001 を修正し、generic exact-copy primitive の allowed path、Closure、TDD cycle、focused test、evidence destinationを plan に追加する。
2. B-002 を修正し、custom build prune、external temporary build、wheel/sdist/installed inventory、resource bytes、static checksの exact commandまたは exact test nodeを固定する。
3. 修正内容を `report.md` の Evidence Adoption Ledger / Spec Authoring Gate に反映する。
4. 修正版 plan に対する fresh `spec-reviewer` reviewで blocking findingが0になる。

今回の findings は plan-level の不足であり、generic exact-copy contractを維持する限り、approved requirement/design を変更する必要はない。実装、テスト成功、PR、merge、Issue完了については本レビューでは何も認定していない。
