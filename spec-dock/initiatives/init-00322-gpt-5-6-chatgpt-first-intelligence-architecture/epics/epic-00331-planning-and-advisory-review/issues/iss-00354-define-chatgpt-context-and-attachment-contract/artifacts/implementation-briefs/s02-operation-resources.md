# iss-00354 / Milestone S02 実装ブリーフ

## Operation resources と deterministic minimal body

| 項目                      | 固定値                                                                         |
| ----------------------- | --------------------------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                                       |
| Branch                  | `codex/iss-00354-chatgpt-context-contract`                                  |
| Exact source HEAD       | `ba9e64944702c85e64c127c2eee10b1100712daa`                                  |
| Branch 比較               | `identical` / ahead `0` / behind `0`                                        |
| Default branch fallback | 使用しない                                                                       |
| Issue                   | `iss-00354-define-chatgpt-context-and-attachment-contract`                  |
| Milestone               | S02 — Operation resources と minimal body                                    |
| Closure ID              | `cl-s02-resources`                                                          |
| 必須テスト ID                | `tc-s02-001`                                                                |
| 実装ブリーフ配置先               | `artifacts/implementation-briefs/s02-operation-resources.md`                |
| 文書の効力                   | Codex 実装用 advisory。実装完了、review PASS、commit、push、PR、merge、Issue close を意味しない |

GitHub Connector で指定 commit の存在を確認し、指定 branch tip と exact HEAD が一致することを確認した。対象 commit は S01 の停止ゲートを閉じ、S02 を開始可能にした report 更新である。

添付 bundle は approved requirement / design / plan、現行 renderer、tests、resources を照合する補助資料として使用した。 別添の exception taxonomy に関する設計判断は本 Issue・S02 の resource / prompt 契約と無関係であり、実装根拠には採用しない。

---

## 1. 結論

S02 では、現在の flat resource 群を次の operation-scoped tree に移行し、application code が知る resource 名を各 operation の `prompt.md` と top-level `attachments/` directory だけに限定する。

* `planning`
* `review`
* `revision`

application に置く registry は、既存 runtime role と上記 operation key の対応だけとする。attachment 内の file 名、個数、SHA、並び順を registry に持たせてはならない。

renderer は、operation resource の `prompt.md` を目的文として読み、固定順序の minimal body を生成する。詳細な authoring rule、Review schema、revision rule、固定 13 見出し、4 図要件は operation の `attachments/` 側へ移す。

未知 operation は planner、reviewer、revision のいずれにもフォールバックせず、resource 読取り前に明示的に拒否する。

S01 は exact HEAD 時点で directory、multiple paths、continuation を supported として閉じており、remote post-upload failure の分類だけが S10 に持ち越されている。したがって S02 は開始可能だが、Oracle transport や recovery を変更してはならない。

---

## 2. 目的、非目的、前提

### 2.1 目的

S02 で閉じる責務は次のとおり。

1. `planning`、`review`、`revision` が、それぞれ独立した `prompt.md` と `attachments/` を持つ。
2. operation attachment の file 増減が、application registry の変更なしで反映される。
3. body に operation、目的、exact identity、GitHub gate、hard failure、Human authority、expected output を残す。
4. body から input attachment SHA、input inventory、classification、固定 13 見出し、4 図要件、長い operation 手順を除く。
5. Reviewer の body に `fresh`、`read-only`、`defect-only` を保持する。
6. 同一入力から UTF-8 byte 単位で同一の body を生成する。
7. unknown operation、欠落 `prompt.md`、欠落 `attachments/` を fail-closed にする。
8. provider resource と生成済み projection の recursive byte parity を検証する。

Approved requirement は、minimal body に目的、identity、authority、expected output、attached instructions への参照、exact access hard failure を保持し、各 operation が provider-owned `prompt.md` と opaque `attachments/` を持つことを要求している。

### 2.2 非目的

S02 では以下を実装しない。

| 対象外                                                                        | 後続境界    |
| -------------------------------------------------------------------------- | ------- |
| dynamic Candidate / Review / revision request を bytes から original path に置換 | S03     |
| generated prompt-pack、`context-NNN.md`、manifest 群の削除                       | S04     |
| Oracle argv に operation attachment path を直接渡す transport wiring             | S04     |
| CLI の `--context-manifest` 廃止や directory option 追加                         | S05     |
| Blue continuity、fresh Red binding、conversation persistence                 | S06     |
| Oracle `0.17.0` profile、stage decoder、inline recovery                      | S09–S10 |
| artifact reader、download / ZIP capture                                     | S12     |
| output ZIP / closed Review JSON validator の緩和または変更                         | 対象外     |
| `SKILL.md`、workflow docs、parent Epic wordingの更新                            | S07     |
| personal wrapper、API、default branch、alternate backend の追加                  | 禁止      |

現行 infra は引き続き generated prompt-pack を作成し、`context-NNN.md`、manifest、provenance、source manifest、stale-if を materialize する。これは S04 の置換対象であり、S02 から触れてはならない。

### 2.3 実装開始前の前提

Codex は変更前に次を確認する。

* current branch が指定 branch である。
* current HEAD が exact source HEAD である。
* worktree に S02 と無関係な変更がない。
* S02 の write scope を超える変更が必要でない。
* provider resource を正本とし、projection を先に編集しない。

HEAD が変化している場合、rebase、adoption、fresh review の判断なしに S02 を開始しない。

---

## 3. 現状と S02 target の差分分析

Approved plan は、S02 の Red として minimal body、operation-scoped resources、registry-free resource mutation、fresh/read-only/defect-only Reviewer を固定し、Green として self-contained operation tree、deterministic renderer、unknown operation rejection を要求している。

### 3.1 Resource 配置

| Concern              | Exact HEAD の現状                                                                                                       | S02 target                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Layout               | `planner-prompt.md`、`reviewer-prompt.md`、`revision-prompt.md`、`transport-output-contract.md` が一つの flat directory にある | `operations/{planning,review,revision}/{prompt.md,attachments/}`                       |
| Planning resource    | `planner-prompt.md` 自体に固定 13 見出しと 4 PlantUML 要件を埋め込む                                                                 | `prompt.md` は短い目的文。13 見出しと 4 図は `attachments/` 内                                       |
| Review resource      | role、closed JSON schema、digest rule、finding criteria、onboarding review criteria が一ファイルに混在                            | `prompt.md` は fresh/read-only/defect-only の目的文。詳細 schema / criteria は `attachments/` 内 |
| Revision resource    | revision purpose と固定 13 見出し・4 図が同一ファイル                                                                               | `prompt.md` は revision purpose。詳細 rule は `attachments/` 内                              |
| Shared resource      | 全 operation が root の `transport-output-contract.md` に依存                                                              | 各 operation directory が sibling/root shared instruction file に依存しない                    |
| Attachment discovery | operation attachment directory は未導入                                                                                  | application は directory path のみ解決し、children を認識しない                                     |

現行 planning resource は body に出すには詳細すぎ、固定 13 見出しと 4 図契約を直接含む。 現行 revision resource も同じ問題を持つ。

Reviewer resource は fresh/read-only/defect-only という body に残すべき役割と、digest・closed JSON・finding criteria という attachment 側へ移すべき詳細を混在させている。

### 3.2 Renderer

| Concern                    | Exact HEAD の現状                                                    | S02 target                                                                                           |
| -------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Required resource registry | `_REQUIRED_RESOURCE_NAMES` が flat 4 file を列挙                      | operation 名だけを registry 化。attachment file inventory は持たない                                            |
| Role resolution            | `semantic_revision` だけ条件分岐し、他は `f"{role}-prompt.md"`              | closed role→operation mapping                                                                        |
| Identity                   | `context.to_dict()` 全体を body に JSON 化                             | exact identity と bounded operation context を分離                                                       |
| Attachment metadata        | evidence prompt が name、classification、source label、SHA を body に列挙 | input attachment index 全体を body から除去                                                                 |
| Instructions               | revision instructions を `## Operation instructions` として展開         | selected findings / preserved assumptions だけを typed revision scope として残し、静的手順は resource attachment へ |
| Output/authority           | root shared transport resource を body 末尾へ連結                       | renderer が固定 minimal authority/output boundary を生成                                                   |
| Determinism                | JSON は canonical だが、long resource 内容と index に依存                   | fixed headings、fixed order、canonical JSON、exactly one terminal LF                                    |

現行 renderer は flat resource 名をコードに固定し、role prompt、identity、GitHub gate、hard failure、attachment authority、output expectation、shared transport を連結している。 Evidence renderer はさらに attachment classification、source label、SHA と operation instructions を body に埋め込む。

### 3.3 Tests

Exact HEAD の tests は、S02 target と逆向きの assertion を含む。

| 現行 assertion                                 | S02 での変更                                                     |
| -------------------------------------------- | ------------------------------------------------------------ |
| Planner body に固定 13 見出しが全てある                 | body では不在、planning attachment resource では存在                  |
| Planner body に 4 図契約がある                      | body では不在、planning attachment resource では存在                  |
| Review body に classification と SHA がある       | body では不在。`exact_attachments` の bytes 自体は保持                  |
| Revision body に固定 13 見出しと 4 図契約がある           | body では不在、revision attachment resource では存在                  |
| flat 4 resources を installed fixture に作る     | nested 3-operation tree を作る                                  |
| role fragments と shared transport file の責務分離 | operation `prompt.md` と operation-local `attachments/` の責務分離 |

現行 Planner test は 13 見出しと 4 図契約が body にあることを積極的に要求している。 Revision test、attachment SHA test、flat installed resource fixture も S02 に合わせた更新が必要である。

---

## 4. 変更対象ファイルと責務

| Path                                                                                            | Authority / responsibility      | S02 で行う変更                                                                                |
| ----------------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------- |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/`          | **provider resource authority** | flat resources を operation tree に移行。詳細手順を attachments 側へ分離                               |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py` | provider application authority  | role→operation mapping、resource resolver、minimal body renderer、static attachment path 投影 |
| `tests/unit/application/test_issue_planning_prompt.py`                                          | S02 behavioral contract         | Red/Green tests、negative assertions、byte determinism、opaque directory、projection fixture |
| `.agents/skills/spec-dock-issue-planning/resources/`                                            | dogfood / installed projection  | provider から生成。直接 source of truth にしない                                                    |
| `spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`                      | installed runtime projection    | provider application から生成し、byte parity を確認                                               |
| `artifacts/implementation-briefs/s02-operation-resources.md`                                    | Issue-local advisory artifact   | 本ブリーフを Codex が配置する対象。runtime authority ではない                                              |

Provider resource と root `.agents` projection は exact HEAD で同一 blob になっているため、S02 後もこの関係を維持する。 Provider application と installed runtime application も exact HEAD では同一 blob である。

Projection は既存の provider projection mechanism で生成する。生成方法が現行 workflow から一意に解決できない場合、手作業で projection だけを合わせず停止する。

---

## 5. Operation resource 契約

### 5.1 Target tree

```text
resources/
└── operations/
    ├── planning/
    │   ├── prompt.md
    │   └── attachments/
    │       └── instructions.md
    ├── review/
    │   ├── prompt.md
    │   └── attachments/
    │       └── instructions.md
    └── revision/
        ├── prompt.md
        └── attachments/
            └── instructions.md
```

`instructions.md` は初期配置の推奨名であり、application contract ではない。将来これを分割、rename、追加、削除しても application code を変更してはならない。

Approved design は、application が読む known template を `prompt.md` に限定し、`attachments/` を opaque directory path として扱い、registry に file inventory を持たせない。

### 5.2 Directory / file invariants

| Entry                   | 必須条件                                        |
| ----------------------- | ------------------------------------------- |
| `resources/operations/` | regular directory、symlink 不可                |
| operation directory     | `planning`、`review`、`revision` の exact name |
| `prompt.md`             | regular file、symlink 不可、UTF-8、空文字不可         |
| `attachments/`          | directory、symlink 不可                        |
| attachment children     | application は存在、種類、個数、名前、順序、size、SHA を検査しない |

Application が許される filesystem operation は、選択した operation directory、`prompt.md`、`attachments/` という top-level contract の型確認までとする。

`attachments/` に対して次を行ってはならない。

* `iterdir`
* `glob` / `rglob`
* `os.walk`
* child `stat`
* child `open` / `read_text` / `read_bytes`
* sort
* hash
* count
* file allowlist
* hidden / symlink / FIFO の分類
* manifest 作成

### 5.3 Resource 内容の移行

| Operation | `prompt.md` に残すもの                                                                  | `attachments/` に移すもの                                                                                  |
| --------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| planning  | existing Issue の advisory package を作成するという短い目的                                     | canonical precedence、固定 13 見出し、4 図、authoring guidance、詳細 output/privacy rule                          |
| review    | fresh、read-only、defect-only、concrete defects only                                  | reviewed identity digest rule、closed JSON schema、verdict rule、finding keys、onboarding review criteria |
| revision  | prior Candidate と exact Review に基づく complete replacement、Issue/source identity を維持 | selected P0/P1 の処理ルール、preserved assumption rule、固定 13 見出し、4 図、authoring output details                |

Root の旧 `planner-prompt.md`、`reviewer-prompt.md`、`revision-prompt.md`、`transport-output-contract.md` は、全参照を nested tree へ移した同一変更内で削除する。旧 flat resource と新 tree を同時 fallback として残してはならない。

---

## 6. Operation registry と resolver の最小アルゴリズム

### 6.1 Registry contract

Registry は次の三つの対応だけを持つ。

| Existing runtime role | Operation key |
| --------------------- | ------------- |
| `planner`             | `planning`    |
| `reviewer`            | `review`      |
| `semantic_revision`   | `revision`    |

Registry が持ってはならない情報:

* `prompt.md` 以外の file 名
* attachment file 名
* attachment count
* SHA
* file order
* operation fallback
* output schemaの複製
* Oracle transport option

### 6.2 Resolver 手順

| 順序 | 処理                                                                          | 失敗時                                              |
| -: | --------------------------------------------------------------------------- | ------------------------------------------------ |
|  1 | role が closed registry に存在することを確認                                           | `ValueError("unknown issue planning operation")` |
|  2 | provider または installed resource root を解決                                    | managed resource incomplete                      |
|  3 | `operations/<operation>` を構築                                                | fallback しない                                     |
|  4 | operation directory が regular directory かつ non-symlink と確認                  | fail-closed                                      |
|  5 | `prompt.md` が regular file かつ non-symlink と確認                               | fail-closed                                      |
|  6 | `attachments/` が directory かつ non-symlink と確認                               | fail-closed                                      |
|  7 | `prompt.md` だけを UTF-8 で読む                                                   | decode/read error を伝播                            |
|  8 | operation、prompt text、attachments directory path を immutable descriptor にする | —                                                |
|  9 | renderer に descriptor を渡す                                                   | —                                                |

次のような分岐は禁止する。

* unknown role なら planning
* reviewer 以外なら revision
* nested tree がなければ flat resource
* operation attachment が欠落したら shared resource
* resource error なら empty attachments

### 6.3 S02 時点の synthesized contract

既存 `SynthesizedPlanningPrompt` の末尾へ、approved path model に接続する `attachment_paths: tuple[Path, ...] = ()` を追加する。

S02 ではこの field に、選択した operation の static `attachments/` directory 一つだけを設定する。

* planning: `(planning/attachments,)`
* review: `(review/attachments,)`
* revision: `(revision/attachments,)`

既存の `attachments`、`exact_attachments`、`PlanningPromptAttachment.content` は S02 では削除しない。S03 が dynamic original paths を `attachment_paths` へ統合し、legacy bytes/classification/SHA fields の廃止を完了する。

S02 では infra がこの新 field を Oracle argv に使用しなくてよい。infra 変更を必要とする場合は S02 を停止し、S03/S04 境界へ引き渡す。

---

## 7. Deterministic minimal body 契約

### 7.1 Section 順序

Renderer は次の順序を固定する。

| 順序 | Exact section                         | 内容                                                          |
| -: | ------------------------------------- | ----------------------------------------------------------- |
|  1 | `# SpecDock Issue Planning Operation` | 固定 title                                                    |
|  2 | `## Operation`                        | `planning` / `review` / `revision`                          |
|  3 | `## Purpose`                          | operation `prompt.md` の本文                                   |
|  4 | `## Exact source identity`            | canonical compact JSON                                      |
|  5 | `## Operation context`                | bounded dependency / operator context。空なら `none`            |
|  6 | `## GitHub connector gate`            | exact repository、branch、HEAD の確認義務                          |
|  7 | `## Hard failure`                     | exact access 不可なら `repository access failed` のみ             |
|  8 | `## Human authority`                  | mutation、adoption、approval、implementation authorization の否定 |
|  9 | `## Revision scope`                   | revision の場合だけ、selected finding と preserved assumption      |
| 10 | `## Expected output`                  | existing typed expectation の canonical JSON                 |
| 11 | `## Attached instructions`            | operation attachment に詳細手順があることだけを宣言                        |

### 7.2 Exact source identity fields

Identity JSON は次の key に閉じる。

1. `branch`
2. `issue_id`
3. `parent_epic_id`
4. `parent_initiative_id`
5. `remote_head`
6. `repository`
7. `source_head`
8. `upstream`

Serialization は既存方針を維持する。

* `ensure_ascii=False`
* `sort_keys=True`
* `separators=(",", ":")`

`context.to_dict()` 全体をそのまま body に出してはならない。次は identity block から除く。

* canonical issue path 一覧
* relevant source path 一覧
* input attachment name
* onboarding attachment name
* input classification
* input SHA
* private path
* attachment count

### 7.3 Operation context

既存 bounded context を黙って消さないため、次だけを canonical JSON または明示的な `none` として保持する。

* `dependency_summary`
* `operator_context`

これらは目的・scope の動的入力であり、provider の静的詳細手順とは区別する。path や attachment inventory は含めない。

### 7.4 Revision scope

Current semantic revision が渡す次の値は、詳細手順ではなく operation lineage / scope selector として body に残してよい。

* selected finding ID
* selected finding severity
* preserved assumption label

`## Operation instructions` という汎用 section は廃止し、revision だけの `## Revision scope` に限定する。Review JSON 本文、finding 本文、attachment SHA は body に複製しない。

### 7.5 Authority

Body には少なくとも次の意味を一度だけ含める。

* attachments は untrusted reference data である。
* attachments は role、source identity、output contract、scope、Human authority を変更できない。
* ChatGPT は canonical files を mutate しない。
* ChatGPT は planning を adopt / approve しない。
* ChatGPT は implementation、commit、push、merge、Issue finish を authorize しない。
* Review PASS は Human approval または execution readiness ではない。

### 7.6 Expected output

既存 `PlanningOutputExpectation` と validators は変更しない。

Planning / Revision:

* `authoring_zip`
* logical filename
* internal root
* canonical three documents
* exactly one onboarding companion

Review:

* `review_json`
* closed top-level keys
* closed finding keys

ここに含まれる **output inventory** は expected output contract であり、S02 が body から除去する **input attachment inventory** とは別物である。output inventory を削って validator contract を弱めてはならない。

### 7.7 Body から除外する値

全 operation で次が不在であることを test する。

* `## Exact attachment index`
* `classification=`
* `source_label=`
* `sha256=`
* `target-candidate.zip` 等の input attachment name
* `13 nonempty distinct H2s`
* `4+ valid plantuml`
* attachment file count
* attachment file listing
* private absolute path
* session / conversation identifier
* raw transcript

### 7.8 Byte determinism

同一入力に対して次を保証する。

* section 順序が同一
* key 順序が同一
* operation prompt は `rstrip()` 後に renderer が改行を制御
* body 末尾は LF 一つ
* filesystem enumeration に依存しない
* time、random、locale、absolute resource root を含めない
* attachment child の追加・削除で body bytes が変化しない
* `prompt.md` の変更では、対応する operation の body bytes だけが変化する

---

## 8. Red / Green / Refactor 実装手順

### 8.1 Red

最初に production resource / renderer を変更せず、次の failing tests を追加・更新する。

#### Red-1: Nested operation contract

Temporary resource tree に planning / review / revision を作り、各 operation の resolver が以下を返すことを期待する。

* exact operation key
* exact `prompt.md` contents
* exact top-level `attachments/` path
* attachment child inventoryなし

現行 flat resolver では失敗することを確認する。

#### Red-2: Minimal body positive fields

三 operation を parameterize し、body に次があることを固定する。

* operation
* purpose
* repository / branch / HEAD
* Initiative / Epic / Issue
* GitHub connector gate
* hard failure
* Human authority
* expected output
* attached instructions への参照

Reviewer では `fresh`、`read-only`、`defect-only` が全て存在する。

#### Red-3: Detailed content negative fields

三 operation の body に次がないことを固定する。

* input attachment SHA/index/classification
* fixed 13 headings
* 4 diagram contract
* static detailed Review / revision procedure

現行 Planner / Revision tests はこの Red で失敗する。

#### Red-4: Unknown operation

`planner`、`reviewer`、`semantic_revision` 以外の値を渡し、以下を確認する。

* `ValueError`
* resource read count `0`
* fallback `0`
* planning prompt 使用 `0`
* reviewer prompt 使用 `0`
* revision prompt 使用 `0`

#### Red-5: Missing resource

各 case を分離する。

* operation directory missing
* `prompt.md` missing
* `prompt.md` symlink
* `attachments/` missing
* `attachments/` symlink
* invalid UTF-8 prompt

いずれも別 operation への fallback なしで失敗する。

#### Red-6: Opaque attachment directory

`Path.iterdir`、`Path.glob`、`Path.rglob`、`os.walk` を呼ぶと失敗する spy を設定し、それでも resolver と body rendering が成功することを確認する。

### 8.2 `tc-s02-001`

`tc-s02-001` は、approved opaque-directory contract と矛盾しないよう、二つの subcase に分ける。

| Subcase | Fixture 変更                      | Expected body                           | Expected attachment path | Registry |
| ------- | ------------------------------- | --------------------------------------- | ------------------------ | -------- |
| A       | operation の `prompt.md` を置換     | 対応 operation だけ deterministic byte diff | 不変                       | 不変       |
| B       | `attachments/` child を一つ追加または削除 | **byte-identical**                      | 同じ top-level directory   | 不変       |

Subcase B で attachment child の名前、個数、SHA を body に反映してはならない。反映すると REQ-003 と opaque directory contract に反する。

Plan の「resource fixture 差替えによる body identity change」は Subcase A で検証し、「resource file 増減で registry edit 不要」は Subcase B で検証する。S02 execution card は unit test と byte diff を必須証跡としている。

### 8.3 Green

1. Provider resource を nested operation tree に移行する。
2. 各 `prompt.md` を短い operation purpose に縮小する。
3. 固定 13 見出し、4 図、Review schema、revision rule を operation-local `attachments/` へ移す。
4. root shared `transport-output-contract.md` の minimal authority/output 部分を renderer の固定 body へ移す。
5. detailed output/privacy wordingを各 operation attachment に含め、directory を self-contained にする。
6. role→operation の closed mapping を追加する。
7. immutable operation resource descriptor を追加する。
8. `_provider_resource_root()` を nested tree contract に更新する。
9. 両 synthesis function を同じ resolver / body renderer に通す。
10. Evidence prompt から attachment index、classification、source label、SHA を除去する。
11. Existing exact attachment bytes と output expectation は変更しない。
12. `SynthesizedPlanningPrompt.attachment_paths` に static operation attachment directory を設定する。
13. Provider から installed / dogfood projection を生成する。
14. Focused tests と byte parity check を実行する。

### 8.4 Refactor

Green 後、次の重複だけを整理する。

* `synthesize_issue_planning_prompt` と `synthesize_planning_evidence_prompt` の body assembly
* identity JSON renderer
* authority / hard-failure renderer
* expected-output renderer
* operation resolver

Refactor 後も以下は分離したままにする。

* repository source file safe-read
* exact attachment bytes validation
* output expectation constructors
* sensitive-content scan
* Oracle transport
* source preflight
* dynamic revision scope assembly

新しい generic prompt framework、plugin registry、backend abstractionは作らない。

---

## 9. Unit test 更新一覧

| 推奨 test                                                            | 主 assertion                                   |
| ------------------------------------------------------------------ | --------------------------------------------- |
| `test_operation_resources_resolve_all_closed_operations`           | three operations → exact nested paths         |
| `test_unknown_operation_is_rejected_without_fallback`              | unknown → read 0 / fallback 0                 |
| `test_missing_operation_resource_fails_closed`                     | missing prompt/attachments → explicit failure |
| `test_operation_attachment_directory_is_opaque`                    | child traversal APIs 0                        |
| `test_minimal_body_is_deterministic_for_each_operation`            | render twice → exact UTF-8 bytes equal        |
| `test_minimal_body_has_fixed_field_order`                          | heading offsets strictly increasing           |
| `test_minimal_body_excludes_input_attachment_inventory`            | name/classification/source/SHA absent         |
| `test_planning_body_moves_heading_and_diagram_rules_to_attachment` | body absent / resource attachment present     |
| `test_revision_body_moves_heading_and_diagram_rules_to_attachment` | body absent / resource attachment present     |
| `test_review_body_is_fresh_read_only_defect_only`                  | three terms present                           |
| `test_review_details_live_in_operation_attachment`                 | closed JSON criteria attachment side          |
| `test_tc_s02_001_prompt_change_changes_only_body_bytes`            | prompt replacement deterministic diff         |
| `test_tc_s02_001_attachment_child_change_needs_no_registry_change` | body same / path same / tree bytes differ     |
| `test_expected_output_contract_is_preserved`                       | authoring ZIP / Review JSON exact expectation |
| `test_installed_runtime_resolves_nested_operation_resources`       | installed-layout fixture                      |
| `test_provider_and_projection_resources_are_byte_identical`        | recursive relative paths + bytes              |
| `test_provider_and_installed_renderer_are_byte_identical`          | provider Python bytes == projection bytes     |

### 9.1 既存 test の扱い

* 13 見出し・4 図を body に要求する assertion は削除せず、**body にないこと**と **attachment resource にあること**の二つへ反転する。
* Review attachment SHA が body にあることを要求する assertion は削除する。
* `exact_attachments[0].content` が元 bytes と同一である assertion は維持する。
* Semantic revision の selected finding / preserved assumption assertion は、`## Revision scope` の typed values として維持する。
* Character budget test は、旧 long body の exact budget に依存させず、byte determinism と「旧 body より増えていない」上限へ更新する。
* Installed resource fixture は flat 4 file から nested operation tree へ更新する。

---

## 10. Byte diff と projection check

### 10.1 Renderer byte check

各 operation で次を記録する。

* `first.prompt.encode("utf-8")`
* `second.prompt.encode("utf-8")`
* exact equality
* terminal LF count
* SHA は test diagnostic に使ってよいが、body や public outputには埋め込まない

### 10.2 Resource mutation check

Temporary resource tree で、実装 code を変えずに次を実施する。

1. baseline render
2. attachment child 追加
3. rerender
4. body bytes identical
5. attachment directory path identical
6. resource tree bytes differ
7. child 削除
8. baseline tree と再一致

### 10.3 Projection parity

Provider を正本として、少なくとも次を recursive に比較する。

* provider resources と root `.agents` resources
* provider renderer と installed runtime renderer

Comparison は relative path set、file type、file bytes を確認する。resource file 名の allowlist を parity test に書かず、recursive tree 全体を比較する。

---

## 11. 実行コマンド

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py -q

uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  tests/unit/application/test_issue_planning_prompt.py

uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py

diff -qr \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources \
  .agents/skills/spec-dock-issue-planning/resources

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py

./spec-dock/scripts/spec-dock validate
git diff --check
git diff --name-only ba9e64944702c85e64c127c2eee10b1100712daa --
```

`git diff --name-only` の結果は、S02 の許可 resource、renderer、test、生成 projection、S02 brief artifact の subset に限定する。report 更新は orchestrator が実測証跡を採用する段階で行い、renderer worker の必須変更に混ぜない。

---

## 12. 実装担当向け function-level 指針

| Symbol / concern                             | 実装指針                                                                   |
| -------------------------------------------- | ---------------------------------------------------------------------- |
| `_OPERATION_BY_ROLE`                         | closed mapping。default 値なし                                             |
| `_OperationResources`                        | operation、prompt text、attachment directory を保持する frozen internal value |
| `_resolve_operation_resources`               | top-level contract のみ検証。attachment children へ触れない                      |
| `_render_exact_identity`                     | closed fields、canonical JSON                                           |
| `_render_minimal_body`                       | section order、authority、hard failure、outputを一元化                        |
| `synthesize_issue_planning_prompt`           | source safe-read は維持し、body は共通 renderer へ委譲                            |
| `synthesize_planning_evidence_prompt`        | exact bytes は維持し、input attachment index を body に出さない                   |
| `SynthesizedPlanningPrompt.attachment_paths` | S02 では static operation directory 一つ                                   |
| `_provider_resource_root`                    | provider/installed candidate root の nested contract を検証                |
| `_REQUIRED_RESOURCE_NAMES`                   | flat file allowlist としては削除                                             |
| `PlanningOutputExpectation`                  | 変更しない                                                                  |
| `PlanningPromptAttachment`                   | S02 では変更・削除しない                                                         |
| Infra / Oracle adapter                       | 変更しない                                                                  |

---

## 13. 成功条件

S02 は次を全て満たした場合だけ closed とする。

1. exact source identity が実装開始時にも一致している。
2. planning / review / revision の operation directories が存在する。
3. 各 directory に `prompt.md` と `attachments/` がある。
4. 各 operation が root shared instruction resource に依存しない。
5. attachment child の追加・削除で registry code の変更が不要である。
6. attachment child の追加・削除で body bytes が変わらない。
7. `prompt.md` の変更は対応 operation body だけを deterministic に変える。
8. body に operation、purpose、identity、GitHub gate、hard failure、authority、expected output がある。
9. Reviewer body に fresh/read-only/defect-only がある。
10. body に input attachment name、classification、source label、SHA、inventory がない。
11. body に固定 13 見出し、4 図契約がない。
12. 13 見出し、4 図、Review schema、revision rules が operation attachment resource に存在する。
13. unknown operation が明示的に拒否される。
14. missing prompt / attachments が別 operation へ fallback しない。
15. attachment directory children に対する traversal / read / hash が `0`。
16. existing output expectation と validator contract が不変である。
17. provider / installed / dogfood projection が recursive byte-identical である。
18. focused pytest、ruff、mypy、validate、diff check が全て pass する。
19. Oracle transport、CLI、recovery、profile、artifact reader に差分がない。
20. `cl-s02-resources` と `tc-s02-001` の実測証跡を report へ引き渡せる。

---

## 14. 停止条件

次のいずれかが発生した場合、S02 の範囲内で回避実装を作らず停止する。

1. GitHub branch tip と exact implementation baseline が一致しない。
2. operation resource 解決に許可外 code の変更が必要になる。
3. Oracle adapter または CLI を変更しないと S02 tests を成立させられない。
4. attachment file 名や個数を application registry に列挙する必要が生じる。
5. body determinism のために attachment directory children の sort / hash / scan が必要になる。
6. nested tree 欠落時に旧 flat resource fallback が必要になる。
7. unknown operation を planner/reviewer/revision のいずれかへ暗黙変換する必要が生じる。
8. detailed rule を body に残さないと output validator を通せない。
9. output expectation または closed JSON contract の緩和が必要になる。
10. projection mechanism が unrelated files を変更し、その差分を隔離できない。
11. resource directory が symlink、ambiguous root、または provider/projection authority 不明になる。
12. S02 のために dynamic attachment path model を完了させる必要が生じる。
13. test が attachment child inventory を body に要求する。
14. provider resource と projection の byte parity を確立できない。

---

## 15. S03 以降へ持ち越すリスク

| Risk / obligation                                             | 引き渡し先     | S02 で残す境界                                      |
| ------------------------------------------------------------- | --------- | ---------------------------------------------- |
| Static operation attachment path と dynamic original paths の統合 | S03       | `attachment_paths` には static directory だけ      |
| `PlanningPromptAttachment.content`、classification、SHA の廃止     | S03       | legacy fields を維持                              |
| generated prompt-pack / manifest の撤去                          | S04       | infra 無変更                                      |
| Oracle direct `--file` operands への path assembly              | S04       | transport wiring なし                            |
| context manifest / CLI cutover                                | S05       | parser / command 無変更                           |
| revision request original path と selected scope の最終 binding   | S05       | body は selected IDs / assumptions の最小 scope のみ |
| Blue continuity / fresh Red                                   | S06       | Reviewer wordingだけ保持し、thread stateは実装しない       |
| Provider/docs全体の最終 parity                                     | S07 / S13 | S02 相当 projection のみ検証                         |
| Oracle profile / stage recovery                               | S09–S10   | 完全に無変更                                         |
| versioned artifact capture                                    | S12       | output expectationだけ維持                         |

S02 完了は direct Oracle path transport、Blue/Red continuity、Oracle `0.17.0` compatibility、Issue 全体の実装完了を意味しない。
