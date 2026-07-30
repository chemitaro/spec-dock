# Issue 344 S02 実装・テスト具体化 brief

## 結論

GitHub connector で `chemitaro/spec-dock` の `iss-00344-workbench-shell-scaffolding` を直接参照し、ブランチ HEAD が指定どおり **`59d3d11c903a010a4fa98d0386f077a28862e70f`** であることを確認した。

S02 の最小変更は、次の **test-only 差分**で足りる見込みである。

1. `test_runtime_fs_repo_workbench_opacity.py` の既存 opacity test を、README・ADR-like Markdown・binary・invalid UTF-8 まで含む mixed fixture に拡張する。
2. `test_workbench.py` の既存 runtime opacity test を、README・binary・invalid UTF-8・active context の観測まで拡張する。
3. `test_workbench.py` に linked-worktree の identical README/no-diff test を1件追加する。
4. 同じファイルに divergent README/source-wins test を1件追加する。
5. `_prepare_linked_worktrees()` は同ファイル内で、ignored payload を worktree 作成前に投入できる小さな keyword-only option を追加する。既存呼び出しの既定挙動は変えない。

現行 production source は、exact `.workbench` prune と opaque whole-tree source-wins を既に実装しており、README 専用分岐もない。したがって、最初から production 変更を予定せず、**characterization-first** とする。正しい新規 assertion が production contract failure を示した場合だけ **STOP** とし、read-only production file は変更しない。添付 brief の allowed/read-only/forbidden 境界をそのまま維持する。

---

## 1. Current behavior and gaps

### 1.1 既存 evidence として再利用するもの

| 契約                                   | 現在のコード／テストが既に示すこと                                                                                                                                             | S02 での扱い                                                               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| exact `.workbench` metadata prune    | `fs_repo._find_metadata_paths()` は `os.walk(..., topdown=True)` を使い、child directory 名が exact `.workbench` の場合だけ traversal から除外する。`.workbench-copy` 等へは拡張しない。  | production は変更せず、mixed payload fixture で characterization を強化する        |
| metadata opacity                     | 現在の unit test は `.workbench` 内の fake `.meta.json` と legacy `meta.json` を無視し、canonical node だけを返す。near-name と Workbench 外 malformed metadata は従来どおり strict。    | 既存 test を README、ADR、binary、invalid UTF-8 へ拡張する                        |
| prune-before-access                  | guarded `os.walk` test が、`.workbench` descendant へ入る前に directory list から除外されることを証明している。                                                                       | 変更・複製しない                                                               |
| CLI surface                          | `--from`、`--root`、`--date`、`--path` は parameterized test で拒否され、local ID も既存の `invalid_scope` で拒否される。                                                          | 既存 test をそのまま TC-344-007C evidence とする                                 |
| node-scoped source/target resolution | public copy test は source と target で別々に full ID を解決し、target 側 directory 名が異なっても target scope に copy する。                                                       | linked checkout test では rename を無効化し、Git diff noise を避ける               |
| current runtime opacity              | 現在の CLI test は fake metadata、ADR-like Markdown、dependency-like YAML を copy した後、`validate`、`sync`、`deps check` が成功することを確認している。                                 | README、binary、invalid UTF-8、active context と baseline comparison を追加する |
| whole-tree source-wins               | low-level test は source-wins、destination-only preservation、再実行時の同一結果を既に検証している。                                                                                | 一般 copy test は増やさず、README の divergent case だけ public CLI seam で追加する    |
| content classification なし            | low-level test は binary、ZIP-like bytes、`.env`、Python、YAML、`.git/config` を content classification なしで byte copy することを確認している。                                   | S02 では invalid UTF-8 を public copy/semantic observation に接続するだけにする     |
| failure / partial mutation           | low-level tests は pre-mutation failure と、先行 entry copy 後の failure における `mutation_started` を区別する。 application test も `copy_failed` への stable mapping を両値で検証する。 | 新しい failure injection は作らず、selected regression と full CLI suite を再実行する |
| authoring source manifest            | dedicated tests が explicit `.workbench` source を filesystem access 前に拒否し、parent walk では exact `.workbench` を prune しつつ `.workbench-notes` を保持する。              | allowed test fileへ重複移植せず、selected node を再利用する                          |

Production copy path は `.workbench` directory 全体を filesystem gateway に渡しており、README を個別選択していない。 `fs_cli` も source directory の全 entry を列挙し、regular file は destination の同名 entry を source bytes で置換するため、README を含む opaque source-wins である。

### 1.2 最小の未観測点

現時点で追加が必要なのは次の四点だけである。

| Gap                           | 必要な追加観測                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| README を含む mixed opacity      | README、fake metadata、ADR-like Markdown、binary、invalid UTF-8 を同じ `.workbench` に入れても、canonical node observation が baseline と一致する |
| active context opacity        | ignored payload copy 前後で `active set` の canonical ID/path observation が変わらない                                                   |
| checkout と manual copy の分離    | linked worktree 作成直後に tracked README だけがあり、ignored payload は存在しない                                                              |
| README-specific compatibility | identical README は copy 後も tracked content diff なし、divergent README は source-wins                                              |

S02 plan も、tracked README の checkout、ignored payload の manual copy、identical/divergent README の既存 semantics 維持を要求している。

---

## 2. Exact test plan

### 2.1 Test helper の最小変更

`tests/cli_runtime/test_workbench.py::_prepare_linked_worktrees()` にだけ、以下の keyword-only parameters を追加する。

```python
source_workbench_payloads: dict[str, bytes] | None = None
rename_target_scope: bool = True
```

実装順序は次のとおり。

1. hierarchy 作成後、commit 前に source issue scope と `scope_id` を解決する。
2. `source_workbench_payloads` がある場合、その relative path を source node の `.workbench/` 以下へ `write_bytes()` する。
3. `git add -A` と commit を実行する。payload は ignore contract により commit されない。
4. `git worktree add` を実行する。
5. target scope を解決する。
6. `rename_target_scope=True` の場合だけ現在と同じ rename を行う。

既存 test は default arguments により今までどおり target scope rename を使う。新しい Git diff test だけ `rename_target_scope=False` とし、tracked node path rename による無関係な dirty state を除く。現行 helper が commit 後に linked worktree を作り、同じ ID の target scope を解決している構造は維持する。

### 2.2 Test cases

| Test name / change                                                                                                                                                     | Fixtures・preconditions                                                                                                                                                                                                                                                          | Operation                                                                                                                                  | Expected result                                                                                                                                                                                                          | Failure detected                                                                                                                    | Closure                |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **amend/rename** `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py::test_workbench_readme_and_payloads_remain_semantically_opaque`                           | canonical Initiative `.meta.json` を作成し、Workbench なしの `load_node_records()` result を baseline とする。その後 `.workbench/README.md`、`fake-node/.meta.json`、`legacy/meta.json`、`decisions/adr-999.md`、`binary.bin`、`invalid-utf8.bin` を配置する。binary と invalid UTF-8 は `write_bytes()` を使う | 同じ `fs_repo.load_node_records(specdock_dir)` を再実行                                                                                          | full normalized record observation が baseline と一致。fake ID の追加なし。parse/decode error なし                                                                                                                                    | README や Markdown の semantic source 化、binary/invalid UTF-8 decode、exact prune の退行                                                   | TC-344-006             |
| **amend/rename** `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands`                  | 現在の fake metadata、ADR-like、dependency fixture に binary と invalid UTF-8 を追加。generated README の存在を assertion。copy 前の target で `validate`、`sync`、`deps check`、`active set <scope_id> --force` を実行し、stable semantic fields を baseline 化                                             | node-scoped `workbench copy` を実行し、payload bytes を確認。その後同じ4 command を再実行                                                                    | 全 command が同じ成功分類。active `.agent/active.json` の Initiative/Epic/Issue ID と repo-relative path が baseline と一致。fake dependency・fake metadata・ADR-like file は canonical observation に現れない。decode error なし                   | copy 後だけ Workbench が semantic input になる回帰、active resolver 汚染、binary decode、public copy regression                                   | TC-344-006、TC-344-009  |
| **add** `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_linked_worktree_checkout_and_manual_copy_preserve_identical_readme_and_move_only_ignored_payload` | `_prepare_linked_worktrees(..., source_workbench_payloads={"notes/opaque.bin": ...}, rename_target_scope=False)`。payload は worktree 作成前に source だけへ置く                                                                                                                           | linked worktree 作成直後の source/target inventory、SHA-256、Git tracking/ignore/diff を記録。その後 `workbench copy --scope <id> --to <target>` を実行し再記録 | checkout 直後: source は README+payload、target は README のみ。README hashes は同一。copy 後: target に payload が現れ、payload hash が source と一致。README hash は不変。README の unstaged/staged content diff はともに0。payload は target でも ignored | README が checkout されない、ignored payload が自動 materialize される、manual copy が payload を移さない、identical README に tracked content diff が生じる | TC-344-007A、TC-344-009 |
| **add** `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_workbench_copy_preserves_opaque_source_wins_for_divergent_readme`                                 | linked worktree を `rename_target_scope=False` で作成。source と target の node README に異なる bytes を書き、copy 前 hashes が異なることを確認                                                                                                                                                          | node-scoped `workbench copy`                                                                                                               | target README bytes/hash が source README と一致し、target-before bytes/hash と異なる。README を除外した形跡なし                                                                                                                             | README-aware filter の導入、destination-wins、README だけ special-case される互換破壊                                                             | TC-344-007B、TC-344-009 |
| **unchanged evidence** `TestCliWorkbench::test_workbench_copy_rejects_unpublished_source_and_scope_routes`                                                             | 現行 parameterized options                                                                                                                                                                                                                                                        | existing test のまま                                                                                                                          | `--root`、`--from`、`--date`、`--path` を拒否                                                                                                                                                                                  | root route または未公開 selector の追加                                                                                                      | TC-344-007C、TC-344-009 |
| **unchanged evidence** `TestCliWorkbench::test_workbench_copy_invalid_scope_uses_stable_content_free_shape` と full CLI suite                                           | local ID、failure、malformed root、unsafe path 等                                                                                                                                                                                                                                   | existing test のまま                                                                                                                          | error code、side、`mutation_started`、content-free shape が変わらない                                                                                                                                                             | public failure semantics、preflight、atomicity contract の退行                                                                           | TC-344-007C、TC-344-009 |

### 2.3 Semantic observation の比較範囲

CLI opacity test で raw repository snapshot 全体を比較しない。`sync` が生成する derived filesや incidental metadataに過剰依存しないよう、以下だけを比較する。

```text
validate.returncode
sync.returncode
deps check.returncode
active set.returncode
active.json:
  initiative.id / path
  epic.id / path
  issue.id / path
canonical node ID inventory
```

`stdout` を比較する場合は、既存 command が保証する stable content のみに限定する。timestamp、絶対 temporary path、生成順序などは contract に含めない。

Authoring source manifest は既存の専用 tests が Workbench の explicit source rejection、parent-walk prune、near-name preservation を直接検証しているため、CLI opacity test に authoring command を追加しない。

---

## 3. Characterization / Red / Green sequence

### 3.1 Baseline

変更前に次を実行し、既存 regression の有無を分離する。

```bash
uv run pytest tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
uv run pytest tests/cli_runtime/test_workbench.py
```

baseline failure がある場合は S02 test 追加を開始せず、既存 failure として STOP する。

### 3.2 Characterization-first

1. unit opacity mixed fixture を追加する。
2. exact node を実行する。
3. CLI opacity mixed fixture と normalized baseline comparison を追加する。
4. exact node を実行する。
5. identical README linked-worktree test を追加する。
6. divergent README source-wins test を追加する。
7. 新規4 nodeをまとめて実行する。
8. full two suites と reusable selected nodes を実行する。

現行 source は exact `.workbench` prune と opaque directory copy を既に持つため、これらの assertion は production change 前から Green になる可能性が高い。Green なら **「Red を得られなかった」ではなく、現行契約を固定した characterization** として記録する。設計上も copy/discovery production files は read/verify-only であり、README filter や新 selector が必要なら planning へ戻す契約である。

### 3.3 Genuine Red として扱う条件

次のいずれかが、正しい fixture と assertion で再現した場合だけ genuine contract failure とする。

* linked worktree 作成直後に README がない。
* ignored payload が manual copy 前から target にある。
* identical README copy 後に path-scoped tracked content diff がある。
* divergent README copy 後に target が source bytes にならない。
* README、binary、invalid UTF-8 により validate/sync/deps/active/node discovery が変わる。
* existing root selector rejection、failure code、`mutation_started` が変わる。

### 3.4 Test defect として修正する条件

以下は production Red に分類しない。

* source payload を `git worktree add` 後に作ったため、checkout/manual-copy境界を観測できていない。
* target scope rename 自体を whole-repo Git diff として拾った。
* temporary absolute path、timestamp、derived-file ordering を raw equality した。
* ignored payload の不在確認に `Path.exists()` ではなく、誤った source-relative path を使った。
* identical copyで inode や mtime の不変まで要求した。

特に、現行 low-level copy は regular file を source bytes・mode・mtimeで書き直し得る。S02 が求めるのは **tracked content diff がないこと**であり、inode、ctime、write の不発生ではない。これらを追加 assertion にしてはならない。

---

## 4. Exact inventory / hash / Git-diff observations

### 4.1 Identical README case

Workbench root を基準に、regular file の relative path と SHA-256 を記録する。

| Stage                    | Source inventory                | Target inventory                | Required hash relation                                                                             |
| ------------------------ | ------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------- |
| linked checkout 後、copy 前 | `README.md`, `notes/opaque.bin` | `README.md`                     | `source README == target README`                                                                   |
| manual copy 後            | 同上                              | `README.md`, `notes/opaque.bin` | `target README after == target README before == source README`; `target payload == source payload` |

SHA-256 は Python `hashlib.sha256(path.read_bytes()).hexdigest()` で計算する。Git object hash は repository hash algorithm に依存するため、byte equality evidence の正本にしない。

### 4.2 Required Git observations

`readme_rel` と `payload_rel` は target repository root からの repo-relative pathとする。

```bash
git ls-files --error-unmatch -- "$readme_rel"
```

期待: exit `0`。README が tracked index entry である。

```bash
git check-ignore -q -- "$payload_rel"
```

期待: source の ignored payload、および copy 後の target payloadで exit `0`。

```bash
git diff --quiet -- "$readme_rel"
git diff --cached --quiet -- "$readme_rel"
```

期待: identical README case の copy 前後とも exit `0`。

必要なら ignored state の可視化として以下を記録できるが、primary assertionにはしない。

```bash
git status --short --ignored --untracked-files=all -- "$payload_rel"
```

期待される表示は `!! <path>`。Git version による cosmetic output差を避けるため、pass/fail の正本は `git check-ignore -q` とする。

### 4.3 Divergent README case

記録値は次の三つで足りる。

```text
source_readme_before_sha256
target_readme_before_sha256
target_readme_after_sha256
```

期待関係:

```text
source_readme_before_sha256 != target_readme_before_sha256
target_readme_after_sha256 == source_readme_before_sha256
```

この case では target README が HEAD と異なること自体が意図的であるため、「Git diff がない」とは assertion しない。source-wins の bytes/hash equality だけを検証する。

### 4.4 Inventory の禁止事項

* whole repository の `git status` を exact equality しない。
* directory mtime、inode、ctime を記録しない。
* destination-only entry が削除されることを期待しない。既存 contract は preserve である。
* README を inventory から除く test helper を作らない。
* file extension、encoding、content に基づく inventory filter を作らない。

README-only tracking の provider ignore contractは exact pathnameを再包含し、その他の Workbench entry を ignore する三規則である。

---

## 5. README、fake metadata、ADR-like、binary、invalid UTF-8、near-name の最小被覆

| Input class             | 配置先                                                        | 主 observation                                                                                | 重複を避ける方針                                             |
| ----------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| README                  | unit mixed opacity、CLI mixed opacity、linked checkout tests | semantic record不変、runtime observation不変、Git checkout、identical no-diff、divergent source-wins | README専用 parser/filter testは作らない                     |
| fake current metadata   | `.workbench/fake-node/.meta.json`                          | canonical node inventoryへ追加されない                                                              | 既存 fixture を再利用                                      |
| fake legacy metadata    | `.workbench/legacy/meta.json`                              | malformedでも legacy scannerが読まない                                                              | 既存 fixture を再利用                                      |
| ADR-like Markdown       | `.workbench/decisions/adr-999.md`                          | ADR/canonical observationに影響せず、copy bytes一致                                                  | 1ファイルだけで十分                                           |
| dependency-like content | `.workbench/dependency.yml`                                | `deps check` の canonical resultを変えない                                                         | 既存 fixtureを保持                                        |
| binary                  | `.workbench/binary.bin`                                    | parse/decodeなし、byte copy                                                                     | low-level arbitrary-byte testを reusable evidence とする |
| invalid UTF-8           | `.workbench/invalid-utf8.bin`                              | `b"\xff\xfe\x80..."` 等を `write_bytes()`、decode errorなし                                       | encoding別 parameterizationは作らない                      |
| near-name               | `.workbench-copy/...` と既存 source-manifest near-name test   | exact name以外を pruneしない                                                                       | 新しい near-name matrixは追加しない                           |

一つの mixed fixture へ全 payload を置き、payload ごとに validate/sync/deps/active test を複製しない。要求されているのは content-independent opacity であり、各 extension用の runtime command matrixではない。

Canonical README 自体も、人間・model・tool が metadata、ADR、dependency、authoring source として扱ってはならず、tracked README は Git checkout、ignored payload は node-scoped manual copyの責務と記述している。

---

## 6. Minimal verification commands

### 6.1 Characterization / new exact nodes

```bash
uv run pytest \
  tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py::test_workbench_readme_and_payloads_remain_semantically_opaque \
  tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands \
  tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_linked_worktree_checkout_and_manual_copy_preserve_identical_readme_and_move_only_ignored_payload \
  tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_workbench_copy_preserves_opaque_source_wins_for_divergent_readme
```

### 6.2 Required two exact suites

```bash
uv run pytest tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
uv run pytest tests/cli_runtime/test_workbench.py
```

これは approved S02 gate の exact suite boundary と一致する。

### 6.3 Relevant reusable selected nodes

```bash
uv run pytest \
  tests/unit/infra/test_runtime_fs_cli_workbench.py::test_copy_workbench_recursively_merges_source_wins_and_is_idempotent \
  tests/unit/infra/test_runtime_fs_cli_workbench.py::test_copy_workbench_copies_opaque_ordinary_file_bytes_without_classification \
  tests/unit/application/test_workbench.py::test_copy_failure_is_mapped_without_raw_error_or_success \
  tests/unit/domain/test_authoring_source_manifest_workbench.py::test_build_source_manifest_prunes_workbench_from_parent_walk_before_descendant_access \
  tests/unit/domain/test_authoring_source_manifest_workbench.py::test_source_manifest_preserves_near_workbench_names
```

### 6.4 Root rejection focused node

```bash
uv run pytest \
  tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_workbench_copy_rejects_unpublished_source_and_scope_routes \
  tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_workbench_copy_invalid_scope_uses_stable_content_free_shape
```

### 6.5 Scope and whitespace checks

```bash
git diff --check
git diff --name-only
```

`git diff --name-only` の期待値は次の2 pathだけである。

```text
tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
tests/cli_runtime/test_workbench.py
```

---

## 7. Stop conditions and scope guards

### STOP

次のいずれかが発生した時点で実装を止める。

1. `application/workbench.py`、`infra/fs_cli.py`、`infra/fs_repo.py` の変更が必要になる。
2. README 専用 copy filter が必要になる。
3. root selector、root copy route、root bulk-copy path が必要になる。
4. exact `.workbench` 以外の新しい semantic exclusion が必要になる。
5. S01 の tracked README が commit/checkoutされていない、または ignore contractが成立していない。
6. correct fixture で semantic opacity、identical no-diff、divergent source-wins のいずれかが成立しない。
7. existing root rejection、failure code、atomicity、destination-only preserve に regression がある。
8. allowed two test files以外に変更が出る。
9. docs、packaging、dogfood projection、generic import、S03/S90/S95/S99 の変更が必要になる。

Production contract変更が必要な failure は test で吸収せず、design amendment対象として報告する。設計は production 三ファイルを原則 read/verify-only とし、契約変更が必要なら design phaseへ戻ることを明示している。

### Scope guards

* public CLI wording、JSON shape、error codeを変更しない。
* current failure/atomicity testsを改名・緩和しない。
* root route rejection testを新実装期待へ反転しない。
* README copy後の inode/mtime不変を要求しない。
* destination-only payloadの削除を要求しない。
* source-manifest testsを allowed filesへ複写しない。
* generic test utility moduleや新 abstractionを作らない。
* `_prepare_linked_worktrees()` の新 parameters は keyword-only、default preserving とする。
* test outputに Workbench payload bodyを表示しない。hash、relative inventory、return codeだけを evidence にする。

---

## 8. Handoff summary for `dev-coder`

**変更対象**

```text
tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
tests/cli_runtime/test_workbench.py
```

**実施内容**

* unit opacity test 1件を mixed payload characterizationへ拡張・改名する。
  -既存 CLI opacity test 1件を README、binary、invalid UTF-8、active context comparisonへ拡張・改名する。
* linked checkout → identical README/no-diff → ignored payload manual copy を一続きに観測する test を1件追加する。
* divergent README が public node-scoped copyで source-winsになる test を1件追加する。
* `_prepare_linked_worktrees()` に、worktree作成前 source payload投入とtarget rename無効化の小さな default-preserving optionを追加する。
* root rejection、failure、atomicity、低レベル source-wins、source-manifest testsは既存 evidenceを再利用する。

**返却する観測値**

```text
changed files
characterization / genuine Red / test-defect classification
source/target Workbench relative inventories
README SHA-256 before/after
ignored payload SHA-256 before/after
git ls-files exit status
git check-ignore exit status
path-scoped unstaged/staged README diff exit status
exact pytest command results
git diff --check result
unresolved risks
```

**禁止**

```text
production changes
README-aware filtering
root copy support
new semantic exclusion
docs/package/import/dogfood changes
S03/S90/S95/S99 work
canonical adoption、review pass、PR、merge、step completion の主張
```

## 仮定・不確実性・未検証主張

* **仮定:** exact source commitにはS01で追加されたtracked node READMEとREADME-only ignore ruleが含まれている。GitHub上のassetとignore sourceは確認済みである。
* **不確実性:** 本回答では pytest や temporary linked-worktree commandを実行していない。上記のGreen見込みはexact GitHub sourceの静的 inspectionに基づく。
* **未検証主張:** 実際のtest count、各commandのexit status、SHA-256、inventory、Git diff結果は `dev-coder` 実行後の観測対象であり、本briefでは成功を主張しない。
