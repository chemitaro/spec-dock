# iss-00354 S03/S04 Fresh Red Team Code Review

## 判定

**FAIL**

| Severity | 件数 |
| -------- | -: |
| P0       |  0 |
| P1       |  4 |
| P2       |  0 |
| P3       |  0 |

P1 が4件あるため、判定は **FAIL** とする。

## 1. 対象 identity

| 項目                      | 確認値                                           |
| ----------------------- | --------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                         |
| Named branch            | `codex/iss-00354-chatgpt-context-contract`    |
| 要求 exact HEAD           | `458fa4a130be05c3a6ed0ad675639148b604f91a`    |
| GitHub branch tip       | `458fa4a130be05c3a6ed0ad675639148b604f91a`    |
| Branch comparison       | `identical` / ahead `0` / behind `0`          |
| Commit message          | `feat(iss-00354): S03/S04実装のtransport契約を実装反映` |
| Default branch fallback | 使用していない                                       |
| 実装 baseline             | `f2238d12313b36a002185d3e101154c20f19993c`    |
| Baseline からの差分          | ahead `1`、1 commit、15 changed paths           |

指定 SHA の commit object と当該 commit の実装差分を GitHub connector で取得した。

## 2. GitHub・添付確認結果

GitHub exact HEAD 上の `requirement.md`、`design.md`、`plan.md`、`report.md`、S03/S04 atomic implementation brief、provider runtime、Review resource、指定5テスト、checked-in projection を開いた。Canonical documents はいずれも `approved` 状態である。

添付 `attachments-bundle.txt` では、canonical requirement/design/plan/report、atomic implementation brief、identity rebind addendum、provider runtime 3ファイル、Review resource、指定5テストを確認し、GitHub exact HEAD 上の対応ファイルと内容を照合した。添付は行番号付き bundle であるため、bundle framing 自体の byte identity は根拠にせず、契約内容と実装本文を照合した。

別添の `設計判断と提案.txt` は例外・failure taxonomy に関する別テーマであり、iss-00354 S03/S04 の要件、設計、実装 brief または Candidate 差分ではないため、本レビューの finding 根拠から除外した。

## 3. 検証方法と静的根拠

実施した GitHub connector 検証は次のとおり。

* Named branch の存在確認。
* Named branch と要求 SHA の exact comparison。
* `f2238d12313b36a002185d3e101154c20f19993c...458fa4a130be05c3a6ed0ad675639148b604f91a` の commit/file comparison。
* Exact commit metadata と diff の取得。
* Canonical docs、implementation brief、runtime、resource、tests、projection の exact-ref blob取得。
* Provider/projection 四組の blob SHA comparison。
* Exact HEAD の combined status と PR-triggered workflow run の確認。

本レビューでは repository checkout 上の `pytest`、`ruff`、`mypy`、`spec-dock validate`、`cmp` は実行していない。GitHub connector は exact HEAD に対する status context と PR-triggered workflow run を返さず、`report.md` にも当該 HEAD のテスト実行結果は記録されていなかった。したがって、テスト成功は未検証であり、以下の判定は exact GitHub blobs、diff、添付、静的契約照合に基づく。

---

# 4. Findings

## RT-354-S03S04-CODE-001

**Severity:** `p1`

**Exact location:**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py:467-471`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py:132-139`
* 同ファイル `1172-1180`
* 同ファイル `1544-1549`
* `tests/unit/application/test_issue_planning_prompt.py:18-32`

**Finding:**

Repository-relative source path の lexical identity が保持されず、`repo_root / relative` に変換されている。

`_source_attachment_paths()` は canonical/relevant source path を `root / relative` に変換し、`_context_source_operands()` も同様に `repo_root / relative` を構築する。Git-bound Review の caller も canonical/relevant path を明示的に `repo_root` へ結合している。

**Violated requirement or contradiction:**

Atomic implementation brief §5.2 は、repository-relative source path を `cwd=repo_root` の Oracle operand として **lexical representation のまま保持**するよう要求している。外部 Candidate、Review、revision request についても original `Path` を保持する契約である。

現行テストは逆に `tmp_path / relative` を期待値とし、承認済み契約ではなく実装上の root-prefix 変換を固定している。

**Concrete impact:**

* Oracle の `--file` operand が承認済みの repository-relative path ではなく、呼出環境の `repo_root` を含む別の文字列表現になる。
* `repo_root` が absolute path の通常実行では private host path が child process argv に入る。
* 同じ repository content でも checkout root によって argv identity が変わり、deterministic lexical path、portability、content-free privacy boundaryを満たさない。
* テストが誤った表現を正として固定しているため、契約違反を回帰として検出できない。

**必要な最小修正:**

Repository 内の canonical/relevant source operand は、`cwd=repo_root` を前提とした repository-relative `Path` の lexical value のまま構成する。Candidate ZIP、Review JSON、revision request は現在どおり request から受けた `Path` object を変更せず渡す。対応テストは relative lexical value と外部 path の object identity を検証する。

---

## RT-354-S03S04-CODE-002

**Severity:** `p1`

**Exact location:**

* Provider:
  `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
* Checked-in projection:
  `spec-dock/scripts/spec_dock_runtime/application/issue_planning.py`

**Finding:**

Provider source と checked-in projection の byte parity が成立していない。

| 対象                                | Exact HEAD blob SHA                        |
| --------------------------------- | ------------------------------------------ |
| Provider application              | `3ebf15fac4139b9aa7bbc487aa5cb9b575da3458` |
| Checked-in application projection | `9dbb16fecd467ecbfdccacd5fef08d1bdc3c5c90` |

Provider blob の SHA は exact HEAD 上で `3ebf15...`、projection blob は `9dbb16...` であり、不一致である。

同じ確認では、以下の三組は一致していた。

* `issue_planning_prompt.py`: `00a01bd12dd3b8d68d6387755f4548f71f85bcdc`
* `issue_planning_chatgpt.py`: `4a9ce078a7f255e431de742ff47c7c8f0cc03350`
* Review `instructions.md`: provider と `.agents` projection が同一

Prompt projection と infra projection の exact blob は、それぞれ provider と一致している。

**Violated requirement or contradiction:**

* `ISS354-REQ-018 Provider / projection parity`
* `AC-011 provider/installed/dogfood recursive byte parity`
* Atomic implementation brief §9.4–9.5

Brief は provider-owned sync 後、変更対象四組すべての `cmp -s` が exit `0` になることを必須としている。

また、対象 commit 自身が「dogfooding の照合用 projection を同期した」と記述しているため、commit claim と exact blobs も矛盾する。

**Concrete impact:**

* Provider runtime と checked-in dogfood/runtime projection が異なる application orchestration を実行する。
* Provider 側だけで成功するテストは、checked-in projection の同等動作を証明しない。
* Atomic cutover の rollback unit、dogfood parity、同一 resulting HEAD closure が成立しない。
* Brief §9.5 の四つの必須 `cmp` のうち少なくとも一つは必ず失敗する。

**必要な最小修正:**

Repository-owned provider sync mechanism だけを使って `issue_planning.py` projection を provider bytes と一致させ、四組すべての byte parity と blob/SHA evidence を同じ resulting HEAD に記録する。Projection の手編集による補正は行わない。

---

## RT-354-S03S04-CODE-003

**Severity:** `p1`

**Exact location:**

* `tests/unit/application/test_issue_planning_prompt.py:18-32`
* 同ファイル `742-763`
* `tests/unit/application/test_issue_planning.py` の Planning/Review/Revision path assertions
* `tests/unit/infra/test_issue_planning_chatgpt.py:1281-1318`

**Finding:**

許可されたテストは新しい path-only/no-inspection/no-materialization 契約の必須 failure-spy matrix を実証していない。

具体的には次が欠落している。

1. `test_operation_attachment_directory_is_opaque` は `iterdir`、`glob`、`rglob` だけを禁止している。nested、hidden、symlink、FIFO entry を実際に配置せず、dynamic path に対する `read_bytes`、`resolve`、`stat`、`iterdir` の zero-call を検証していない。
2. `test_direct_file_operands_preserve_order_and_do_not_materialize_pack` は `--file` の値と個数、および top-level name に `prompt-pack` がないことだけを確認している。Input-side `mkdir`、write、copy、ZIP、hash、tree traversal の failure spy がない。
3. Planning/Review/Revision の external path assertion は主として `Path.__eq__` による値比較で、request から受けた Candidate、Review、revision request の object identity を実証していない。
4. Planning path test は Finding 001 の root-prefixed source path を期待しており、承認済み lexical contractを証明していない。

**Violated requirement or contradiction:**

Atomic brief §7.2 は明示的に以下を要求する。

* nested/hidden/symlink/FIFO attachment directory。
* child traversal `0`。
* dynamic path の `read_bytes`、`resolve`、`stat`、`rglob`、`iterdir` が `0`。
* external Candidate/Review/revision request の lexical path/object identity。
* input-side `mkdir`、write、copy、ZIP、hash、tree traversal が `0`。

これは `tc-s03-001` と `tc-s04-001` の必須受入契約であり、任意の追加カバレッジではない。

**Concrete impact:**

現行テストを通過したまま、次の回帰が再導入され得る。

* Dynamic path の `resolve`、`stat`、`read_bytes`。
* Static directory child の inspection。
* Input pack、copy、ZIP、hash、write による再 materialization。
* External path の再構築による object identity 消失。
* Repository-relative path の absolute/root-prefixed 化。

そのため、テストが pass しても `cl-s03-path-input`、`tc-s03-001`、`cl-s04-direct-transport`、`tc-s04-001` の closure evidenceにはならない。

**必要な最小修正:**

指定された allowed test files内で、brief が列挙した API に failure spy を置き、nested/hidden/symlink/FIFO を含む static directory、Planning/Archive Review/Git-bound Review/Semantic Revision の path matrix、external `Path` object identity、input-side write/copy/ZIP/hash `0` を検証する。既存の source preflight、typed external input validation、output stagingに必要な read/write は対象外として明示的に分離する。

---

## RT-354-S03S04-CODE-004

**Severity:** `p1`

**Exact location:**

* `<issue-root>/report.md:143-211`
* 同ファイル `241-288`
* 同ファイルの S03/S04 implementation、Test Contract Closure、Worker Evidence、Milestone/Commit Candidate Gate

**Finding:**

Exact implementation HEAD に含まれる `report.md` が、同じ HEAD の実装差分と正面から矛盾し、必須実行証跡を記録していない。

Report は exact HEAD においても次を記述している。

* 「S03〜S13 の実装は未実施」
* S03 は `blocked` / `no implementation evidence yet`
* S04 以降は `pending`
* `tc-s03-001` は `pending implementation`
* S04以降の tests は `not executed`
* S03/S04 worker は「コード実装は未実施」
* S03-S13 commit candidate は `not started`

これらは、runtime、Review resource、tests、projectionを変更した exact commit `458fa4...` と一致しない。

**Violated requirement or contradiction:**

Atomic brief §9 は、同じ resulting HEAD に対して次の証跡を必須としている。

* Focused five-file suite。
* Domain contract regression。
* Legacy symbol search。
* Exact provider sync command。
* 四組の projection parity。
* `spec-dock validate`。
* `git diff --check`。
* Scope audit。
* Resulting HEAD と S03/S04 atomic binding。

Report は実装 commit に9行を追加しただけで、identity rebind の履歴を追加した一方、resulting implementation HEAD、実行コマンド、テスト件数、provider sync、parity、no-inspection evidence、closure結果を記録していない。Commit metadata では production/test implementation を明示している。

**Concrete impact:**

* S03/S04 の両 closure を同じ resulting HEAD に bindできない。
* 実装差分、実行結果、projection generation、scope audit の provenance が欠落する。
* Review は「実装済みのコード」と「未実装と記録された正式台帳」のどちらを closure authority とすべきか決定できない。
* 現に Finding 002 の parity failureがあるにもかかわらず、report からその失敗を追跡できない。
* Candidate/Review/Human lifecycle上、S05開始条件や atomic rollback identity を安全に判断できない。

**必要な最小修正:**

Report を exact resulting HEAD の事実に合わせ、少なくとも resulting SHA、変更ファイル、S03/S04共通 binding、実行した exact commandsと結果、no-inspection call counts、legacy search、provider sync command、四組の parity、validate/diff/scope audit、remaining failuresを記録する。Finding 001–003が未解決の間は S03/S04 closure を `closed` または `pass` にせず、正確な failed/pending 状態を記録する。

---

# 5. 確認済みの非 finding

以下は exact HEAD の静的実装上、承認済みS03/S04契約と整合している。

1. `SynthesizedPlanningPrompt` から attachment bytes、classification、per-file SHA、`attachments`、`exact_attachments` は除去され、`attachment_paths: tuple[Path, ...]` を保持する形になっている。
2. Review identity と digest は minimal body の独立 section に一度描画され、Human authority と exact GitHub gateも本文に保持されている。
3. Returned Review JSON は既存 `PlanningReviewResult.from_json_bytes` でparseされ、typed identity equality と `identity.sha256` equalityが検証される。
4. Infra は一つの `--prompt` の後、`attachment_paths` の順序で各 pathを独立した repeated `--file` operandとして追加している。
5. Production path では `_write_transport_pack`、`context-NNN.md`、generated identity attachment、input manifest/provenance writerは除去されている。
6. Output-only private staging、PATH Oracle resolution、managed Chrome、sanitized environment、existing stage-blind 0.16.1 recovery、typed ZIP/Review JSON artifact validationはS03/S04理由では変更されていない。
7. Review resource は generated identity filename ではなく、minimal body の `Reviewed identity` と `Reviewed identity SHA-256` を参照する文面へ更新されている。

## 6. 最終結論

Exact GitHub identity gate は成功したが、次の blocking conditions が残る。

* Repository-relative original path contract違反。
* Provider/projection byte parity不一致。
* 必須 no-inspection/no-materialization test contractの未実証。
* Exact resulting HEAD の report/evidence closure欠落。

したがって、`chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@458fa4a130be05c3a6ed0ad675639148b604f91a` の S03/S04 atomic cutover review verdict は **FAIL** である。

本レビューは read-only であり、repository、canonical docs、report、artifact、testsを変更していない。
