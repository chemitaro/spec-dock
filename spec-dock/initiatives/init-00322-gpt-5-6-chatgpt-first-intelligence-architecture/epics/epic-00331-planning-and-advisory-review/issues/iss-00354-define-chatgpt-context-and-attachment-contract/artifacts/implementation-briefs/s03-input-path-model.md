# iss-00354 / Milestone S03 実装前ブリーフ

## Input model を bytes から path へ

| 項目                         | 固定値・観測結果                                                                        |
| -------------------------- | ------------------------------------------------------------------------------- |
| Repository                 | `chemitaro/spec-dock`                                                           |
| Branch                     | `codex/iss-00354-chatgpt-context-contract`                                      |
| Exact source HEAD          | `9a3ce89ee80f54221cfe8da40e0264d560efb2c6`                                      |
| Branch 比較                  | `identical` / ahead `0` / behind `0`                                            |
| Default branch fallback    | 使用していない                                                                         |
| Upstream                   | `origin`                                                                        |
| Issue / parents            | `iss-00354` / `epic-00331` / `init-00322`                                       |
| Milestone                  | S03 — Input model を bytes から path へ                                             |
| Canonical closure ID       | `cl-s03-path-input`                                                             |
| Canonical test ID          | `tc-s03-001`                                                                    |
| 文書の効力                      | read-only advisory。コード変更、patch、Candidate ZIP、review artifact、repository 更新を行わない |
| 要求モデル                      | `GPT-5.6 Luna` / Reasoning Effort `Max`                                         |
| この実行で露出している model identity | `GPT-5.6 Pro`                                                                   |
| Browser picker の実測 label   | 未確認                                                                             |
| Luna / Max の実測成功           | 未確認。主張しない                                                                       |

GitHub Connector で指定 branch が存在し、branch tip と指定 source HEAD が一致することを確認した。source HEAD `9a3ce89e...` は S02 コード commit の後に `report.md` の証跡だけを更新した commit であり、S03 対象コードは S02 完了時の実装と同一である。

S02 の fresh Red Team 結果は P0/P1/P2/P3=`0` の PASS として記録されている。そこに記録された browser model evidence は historical S02 実行の `GPT-5.6 Sol` であり、この S03 ブリーフ実行の Luna/Max 証跡ではない。

## 結論と実装開始ゲート

S03 の target contract は明確である。

* synthesized operation が保持する attachment 情報を `tuple[Path, ...]` に限定する。
* attachment bytes、抽出 text、classification、logical attachment name、source label、per-input SHA を保持しない。
* path は incoming `Path` object のまま保持し、存在確認、実体種別判定、正規化、内容読取りを行わない。
* source preflight の repository / branch / HEAD / manifest evidence と、ChatGPT に渡す attachment path transport state を別オブジェクトとして扱う。
* generated prompt-pack、copy、ZIP、manifest、Oracle argv の実装は S03 に入れない。

ただし、**exact HEAD の現行実装と S03 の四ファイル allowlist の間には blocking な不整合がある**。

1. bytes を生成している主要 caller は allowlist 外の `application/issue_planning.py` にある。
2. bytes を検査して source manifest と再照合している処理も同ファイルにある。
3. infra は `synthesized.attachments` と `synthesized.exact_attachments` を必須入力として generated prompt-pack を作り、`attachment_paths` を Oracle argv に使用していない。
4. したがって、四ファイルだけで bytes field を削除すると application caller または infra regression が壊れる。
5. 旧 bytes field を compatibility 用に残す、path から bytes を再構成する、一時ファイルを作る、空の compatibility property を置く、という回避はいずれも S03 の受入条件または S04 の責務を侵害する。

このため、**現行 plan のまま許可できるのは Red と scope-gate の確定までである。`cl-s03-path-input` を Green / closed として記録してはならない**。完全な Green には、少なくとも次のどちらかの plan-level 解決が必要になる。

* S03 を additive な path contract 導入に再定義し、旧 production contract の除去と closure を S04 の direct transport cutover と同時に行う。
* S03 と S04 の contract/consumer cutover を一つの atomic execution boundary として再承認する。

この brief はどちらも勝手に採択しない。plan amendment または active-step scope 更新がないまま compatibility bridge を発明した場合は停止する。S03 の正本 execution card 自体も、path materialization や新しい inspection rule が必要なら閉じずに plan amendment へ戻すよう指定している。

---

## 1. 現在のコードの関係箇所と exact HEAD で確認した事実

### 1.1 Application prompt contract

`issue_planning_prompt.py` の現状は次のとおり。

| 要素                                    | exact HEAD の責務                                                                                    | S03 とのギャップ                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `PlanningPromptAttachment`            | `name`、`classification`、`source_label`、`content: bytes` を保持し、`sha256` を計算する                       | S03 では型ごと production contract から除外する必要がある                          |
| `SynthesizedPlanningPrompt`           | `attachments: tuple[(path, text)]`、`exact_attachments`、`attachment_paths` を同時に保持する                | source bytes/text と path transport state が混在している                   |
| `synthesize_issue_planning_prompt`    | canonical/relevant source を resolve・safe-read・UTF-8 decode・sensitive scan し、text attachment を生成する | path synthesis が source inspection/materialization を兼ねている          |
| `synthesize_planning_evidence_prompt` | `exact_attachments` を必須とし、bytes attachment を synthesized result に移す                               | original path を受け取らず、bytes identity を保持する                          |
| `_resolve_operation_resources`        | managed `prompt.md` と opaque `attachments/` top-level path を解決する                                  | managed resource preflight と operator path assembly をテスト上分離する必要がある |

`PlanningPromptAttachment` と `SynthesizedPlanningPrompt` の現行 field、および source file の読取りは exact HEAD の provider source で確認できる。 `synthesize_planning_evidence_prompt` も bytes attachment をそのまま result に保持している。

### 1.2 Application orchestration caller

`application/issue_planning.py` は、prompt contract の単なる利用者ではなく、現在の bytes attachment の主要 producer である。

#### `run_issue_planning_transport`

* GitHub preflight から `PlanningSourceEvidence` を構築する。
* prompt synthesizer の返却後、`_exact_attachments_have_sensitive_content` で attachment bytes を再走査する。
* `_attachments_match_source_manifest` で materialized text/bytes を SHA-256 化し、preflight source hashes と再照合する。
* その後に backend invoker へ渡す。

これは source preflight state と attachment transport state を結合している。

#### `run_issue_planning_review`

Review 用 closure は現在、次を bytes 化している。

* Candidate ZIP bytes。
* git-bound canonical target file bytes。
* Candidate 内 onboarding companion bytes。
* `reviewed-identity.json` の生成 bytes。
* reviewed identity SHA text の生成 bytes。
* canonical/relevant source の supplemental text attachments。

したがって `PlanningPromptAttachment` を四ファイルだけで削除すると、この caller は import または runtime call で破綻する。

#### `run_issue_planning_revise`

Semantic Revision 用 closure は現在、次を bytes attachment にする。

* prior Candidate ZIP。
* exact Review JSON。
* Candidate 内の canonical documents。
* selected findings と preserved assumptions は prompt instructions に入る。

S03 の target は Candidate、Review、revision request の original path を渡すことだが、現行 caller は Candidate view から抽出した bytes を渡している。

### 1.3 Infra consumer と argv

`infra/issue_planning_chatgpt.py` は現在、次を行う。

1. private temporary directory に `prompt-pack` を作る。
2. `synthesized.attachments` から `context-NNN.md` を生成する。
3. `synthesized.exact_attachments` の bytes を file として書く。
4. input manifest、provenance、source-manifest、stale-if を生成する。
5. Oracle argv には一つの `--file <prompt-pack>` だけを置く。

`attachment_paths` は argv assembly に使われていない。

したがって、path-only synthesized contract と現行 infra consumer は直接互換ではない。S03 で infra を変更しないという拘束を維持したまま bytes field を除去する Green は存在しない。

### 1.4 現行テスト

`test_issue_planning_prompt.py` は現在、次を明示的に assertion している。

* `PlanningPromptAttachment.content` が保持される。
* `synthesized.exact_attachments` から injected bytes を取得できる。
* operation attachment directory は opaque で、`iterdir` / `glob` / `rglob` / `os.walk` を呼ばない。
* S02 の `attachment_paths` は static operation directory 一件である。

`test_issue_planning.py` も Review identity bytes や classification を `synthesized.exact_attachments` から読む test double を持つため、full production cutover には同テストの更新が必要である。

`test_issue_planning_contracts.py` は provider source を直接 import し、`PlanningContext` の immutability と identity/path validation を固定している。

### 1.5 正本 target

Approved requirement は、static directory と dynamic evidence の original path を Oracle へ渡し、attachment entry を read、classify、scan、size/count precheck、hash、copy、rename、archive、manifest 化しないことを要求する。

Approved design の conceptual target は、synthesized operation が `prompt`、`attachment_paths`、`output_expectation` 等だけを持ち、現行 `PlanningPromptAttachment.content`、classification、per-file SHA、input manifest を廃止する形である。

### 1.6 採用外入力

添付された exception taxonomy に関する設計判断は、iss-00354 の path input / Oracle attachment contract と無関係であり、この brief の設計根拠には採用していない。

---

## 2. 変更対象ファイルと各ファイルの最小変更責務

### 2.1 現行 S03 allowlist

| Path                                                                                            | 最小責務                                                                           | S03 で許可される変更                                                            |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py` | synthesized application contract、minimal prompt synthesis、opaque path assembly | path-only contract、pure path assembler、bytes/materialization helper の除去 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`   | source identity、PlanningContext、immutable domain contracts                     | 既存 source-context bounds の回帰固定。新 transport policy を発明しない                |
| `tests/unit/application/test_issue_planning_prompt.py`                                          | prompt/path contract tests                                                     | `tc-s03-001`、failure spies、path identity、negative field assertions      |
| `tests/unit/domain/test_issue_planning_contracts.py`                                            | domain immutability / limit boundary                                           | 既存 limits が削除・緩和されないことのテスト                                              |

### 2.2 Full closure に必要だが現行 allowlist 外の provider application

次のファイルは exact HEAD の依存関係上、path-only production cutoverには必要になる。しかし、この brief は編集を許可しない。

| Path                                                                                       | 必要となる理由                                                                                                     |
| ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`   | Review/Revision bytes producer、source hash再照合、sensitive bytes scanを path/typed identity boundaryへ切り替える必要がある |
| `tests/unit/application/test_issue_planning.py`                                            | bytes attachment を読む test doubles と assertions を original path assertions へ変更する必要がある                        |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py` | path-only contract の consumer。S04 所有であり S03 では変更禁止                                                          |
| `tests/unit/infra/test_issue_planning_chatgpt.py`                                          | direct `--file` operands と no-pack を証明する S04 test。S03 では変更禁止                                                |

`issue_planning.py` とその unit test を含めずに full S03 closure を試みる場合、caller import/runtime failureを compatibility fieldで隠してはならない。scope amendment がなければ停止する。

### 2.3 Provider source と installed projection

Exact HEAD では、provider と installed projection は byte-identical である。

* `issue_planning_prompt.py`: blob `6be3256269876914b360539212155c6deea7e7d2`。
* `issue_planning_contracts.py`: blob `98ae151819b417773929396657929b70fef10193`。

S03 の扱いは次に固定する。

* **正本:** `src/spec_dock/assets/spec_dock/scripts/...`
* **installed projection:** `spec-dock/scripts/...`
* S03 では installed projection を直接編集しない。
* manual copy で parity を合わせない。
* projection 同期と recursive parity は S07 の責務である。
* S03 test は現在どおり provider source を import する。
* S03 完了証跡に installed runtime parity を含める場合は、plan の S07 境界との Closure Delta が必要である。

S02 brief は provider-first と projection mechanism の原則を既に固定している。

---

## 3. bytes→path のデータ契約

### 3.1 Target synthesized contract

S03 の最小 target は、現行 class 名を維持して unnecessary rename を避ける。

```python
@dataclass(frozen=True)
class SynthesizedPlanningPrompt:
    role: Literal["planner", "semantic_revision", "reviewer"]
    prompt: str
    attachment_paths: tuple[Path, ...]
    output_expectation: PlanningOutputExpectation
```

S03 では `ThreadRequest` や Oracle profile field を追加しない。それらは後続 milestone の責務である。

### 3.2 入力型

`attachment_paths` の production input contract は次に限定する。

* outer container は `tuple`。
  -各要素は caller が既に構築した `Path`。
* `str`、`bytes`、`None`、file-like object、iterable generator を自動 coercion しない。
* dynamic path の順序を保持する。
* dynamic path の重複を黙って deduplicate しない。
* `Path(path)` による再構築、`.absolute()`、`.resolve()`、`.expanduser()`、`.relative_to()` を行わない。
* synthesized result 内では、incoming dynamic `Path` object 自体を保持する。

現在の request API が `Path` を受け取った後では、CLI に入力された raw spelling の repeated separator や `.` segment は既に失われ得る。S03 が保証する identity は「application boundary に到達した incoming `Path` object と `str(path)`」であり、CLI parse 前の raw token identity は未確認である。

### 3.3 保持する値

* role。
* exact prompt string。
* managed operation attachment directory の top-level `Path`。
* explicitly supplied dynamic `Path` objects。
* path order。
* output expectation。
* source repository / branch / HEAD / manifest は別の `PlanningSourceEvidence` に保持する。
* `PlanningContext` の dependency/operator/relevant-path count・text bounds は source-context validation として維持する。

### 3.4 保持しない値

* attachment content bytes。
* decoded attachment text。
* `name`。
* `classification`。
* `source_label`。
* per-attachment SHA-256。
* generated input manifest / provenance。
* path target の inode、device、realpath。
* symlink target。
* file type。
* directory inventory。
* size、entry count、compression metadata。
* copied/transformed path。
* extracted Candidate members。

### 3.5 `limits` の解釈

正本は `original paths and limits survive` と記載する一方、S03 Green は `input scanner / limits / materialization-only fields` を production path から除くとしており、新しい `PlanningAttachmentLimits` schema や数値は定義していない。

したがって本 brief では次のように解釈する。

* 維持する limits は既存の **source-context bounds**:

  * dependency 件数。
  * relevant source path 件数。
  * operator context 件数。
  * operator context entry/total UTF-8 bytes。
* 除去する limits は materialized attachment content に対する bytes/total-size scan。
* attachment transport に新しい count/size/path-length limit を発明しない。
* `PlanningInputLimits` 等の新しい public typeを、正本根拠なしに追加しない。
* `tc-s03-001` の limits assertion は、既存 source-context boundaries が削除・緩和されていないことを別 assertion で証明する。

実装者が `limits` を synthesized field として追加する必要があると判断した場合、その field schema と数値が正本未定義なので、実装せず plan clarificationへ戻す。

### 3.6 Identity boundary

* Source identity: `PlanningSourceEvidence`。
* Candidate identity:既存 typed Candidate contract。
* Review identity:既存 `ReviewedPlanningIdentity`。
* Attachment transport identity: incoming `Path` object / lexical path text。
* S03 は path の content digest を identity として再計算しない。
* `reviewed-identity.json` や SHA text を generated input file として materialize しない。
* Reviewer に typed reviewed identity を伝えるため generated file が不可避なら、inline fallbackを発明せず停止する。identity を minimal body の deterministic JSON sectionへ移す判断は caller/prompt scopeを伴うため、現行四ファイル allowlistでは確定できない。

### 3.7 Error boundary

S03 で許される error は contract-shape error のみとする。

| 条件                               | 結果                                                     |
| -------------------------------- | ------------------------------------------------------ |
| outer value が tuple でない          | content-free `ValueError`                              |
| tuple element が `Path` でない       | content-free `ValueError`                              |
| role が closed set 外              | 既存 unknown-operation rejection                         |
| output expectation が role と不一致   | 既存 contract rejection                                  |
| path が存在しない                      | S03 では判定しない                                            |
| symlink / FIFO / hidden / nested | S03 では判定しない                                            |
| private absolute path            | S03 では内容・場所を理由に拒否しない。ただし prompt/public resultへ文字列を出さない |
| path materialization が必要         | stop condition                                         |
| direct transport capability が未対応 | existing capability gate に接続して stop                    |

Error message に path text、private root、filename、token-like segmentを含めない。

---

## 4. symlink / FIFO / hidden / nested path に対する inspection 0 方針

### 4.1 Pure assembly boundary

Path-only assembly は、managed resource resolution や source preflight と別の pure helper にする。

概念形:

```python
def _assemble_synthesized_planning_prompt(
    *,
    role: PlanningRole,
    prompt: str,
    managed_attachment_path: Path,
    dynamic_attachment_paths: tuple[Path, ...],
    output_expectation: PlanningOutputExpectation,
) -> SynthesizedPlanningPrompt:
    _validate_path_tuple(dynamic_attachment_paths)
    return SynthesizedPlanningPrompt(
        role=role,
        prompt=prompt,
        attachment_paths=(
            managed_attachment_path,
            *dynamic_attachment_paths,
        ),
        output_expectation=output_expectation,
    )
```

この helper が行ってよい操作は次だけである。

* tuple/type validation。
* tuple concatenation。
* dataclass construction。

次はすべて禁止する。

```text
Path.read_bytes
Path.read_text
Path.iterdir
Path.glob
Path.rglob
Path.stat
Path.lstat
Path.resolve
Path.absolute
Path.exists
Path.is_file
Path.is_dir
Path.is_symlink
os.walk
os.scandir
open
shutil.copy*
zipfile.*
hashlib.sha256(input-content)
```

### 4.2 Managed resources との分離

S02 の `_resolve_operation_resources` は provider-managed `prompt.md` と top-level `attachments/` の完全性を検証する。これは operator-supplied attachment entry の inspection ではない。

`tc-s03-001` では `_resolve_operation_resources` と repository preflight を先に完了した state として扱い、pure assembly helper だけを failure spy 下で呼ぶ。global spy を張ったまま resource resolverを呼ぶと、S02 の top-level fail-closed validationまで誤って禁止するため、テスト境界を混同しない。

### 4.3 Fixture 別の期待動作

| Fixture                    | S03 の扱い                                                          |
| -------------------------- | ---------------------------------------------------------------- |
| `nested/path/input`        | path object をそのまま保持                                              |
| `.hidden/context`          | hidden name を列挙・拒否せず保持                                           |
| directory symlink path     | targetを読まず、path objectを保持                                        |
| file symlink path          | targetを読まず、path objectを保持                                        |
| FIFO path                  | open/statせず、path objectを保持                                       |
| dangling symlink           | resolve/existsせず、path objectを保持                                  |
| missing path               | S03 assembly 成功。Oracle pre-submit failureは既存 capability boundary |
| sensitive-looking filename | content scanせず保持。prompt/public resultへ反映しない                      |

### 4.4 既存 fail-closed 契約との関係

衝突する fail-closed contract と衝突しない contract を分ける。

#### 維持する

* exact GitHub repository / branch / HEAD preflight。
* source manifest evidence。
* managed operation resource top-level validation。
* closed role / output expectation。
* typed Candidate / Review / Human output validation。
* unsupported capability で backend invocationしない境界。

#### 除去するか transport state から外す

* synthesized attachment textを SHA 化して source manifest と再照合する処理。
* exact attachment bytes の sensitive scan。
* review supplemental source bytes の再読取り。
* Candidate member extractionを input transportのために行う処理。

Source preflight は source path を対象に実施済みであり、attachment path assembler が同じ contentを再読取りして証明し直してはならない。

S01 receipt は directory、multiple paths、continuation の positive evidenceと、missing path が送信前に fail-closed したことを記録している。remote post-upload attachment failure stageだけは S10 へ保留されている。S03 がその gapを inline conversionやcopyで補ってはならない。

---

## 5. `argv` と transport boundary に渡す値の具体例

S03 は production Oracle argv builderを実装しない。次は **S04 に渡す path contract と、S03 unit test内の期待値** である。

### 5.1 Planning

```python
managed = Path("resources/operations/planning/attachments")
canonical = (
    Path("spec-dock/issues/iss-00354/design.md"),
    Path("spec-dock/issues/iss-00354/plan.md"),
    Path("spec-dock/issues/iss-00354/requirement.md"),
)
operator_supplied = (
    Path("inputs/nested/.hidden/context"),
)

synthesized.attachment_paths == (
    managed,
    *canonical,
    *operator_supplied,
)
```

### 5.2 Archive Review

```python
managed = Path("resources/operations/review/attachments")
candidate = Path("inputs/iss-00354-candidate-v3.zip")

synthesized.attachment_paths == (
    managed,
    candidate,
)
```

Candidate ZIP を別名でcopyしたり、その memberを抽出したりしない。

### 5.3 Semantic Revision

```python
managed = Path("resources/operations/revision/attachments")
candidate = Path("inputs/iss-00354-candidate-v3.zip")
review = Path("inputs/planning-review-result.json")
revision_request = Path("inputs/revision-request.json")

synthesized.attachment_paths == (
    managed,
    candidate,
    review,
    revision_request,
)
```

### 5.4 S03 test-local argv assertion

S03 test は production helper を追加せず、test内で次の expected operandを組み立ててよい。

```python
argv_tail = tuple(
    operand
    for path in synthesized.attachment_paths
    for operand in ("--file", str(path))
)

assert argv_tail == (
    "--file",
    str(managed),
    "--file",
    str(candidate),
    "--file",
    str(review),
    "--file",
    str(revision_request),
)
```

この assertion の目的は次に限定する。

* `str(path)` 以外の filesystem operationが不要である。
* path order が保持される。
* original incoming `Path` が別 pathに置き換わらない。
  -一つの generated pack path に collapse されない。

`--engine`、model、managed Chrome、session、recoveryを含む actual Oracle argv は S04/S09以降の責務であり、S03 production codeへ持ち込まない。

---

## 6. Red→Green→Refactor の実装手順

### 6.1 Step 0 — source / scope gate

変更前に次を確認する。

```bash
git branch --show-current
git rev-parse HEAD
git status --short
```

必須値:

```text
branch = codex/iss-00354-chatgpt-context-contract
HEAD   = 9a3ce89ee80f54221cfe8da40e0264d560efb2c6
```

HEAD または branch が変化している場合は、この brief の source identityを流用しない。

### 6.2 Red — 現行 allowlist 内で必ず先に追加する tests

編集対象:

```text
tests/unit/application/test_issue_planning_prompt.py
tests/unit/domain/test_issue_planning_contracts.py
```

追加する Red:

1. `SynthesizedPlanningPrompt` の public dataclass fields が `role`、`prompt`、`attachment_paths`、`output_expectation` のみである。
2. `PlanningPromptAttachment` が production contractとして存在しない。
3. `tc-s03-001`:

   * nested、hidden、symlink、FIFO path fixtureを作る。
   * `read_bytes`、`iterdir`、`rglob`、`stat`、`resolve` を failure spy化する。
   * pure path assemblyを実行する。
   * spy count がすべて `0`。
   * test-local argv operands が exact。
4. dynamic path elementの object identityと順序が保持される。
5. `str`、`bytes`、`None` elementを拒否する。
6. duplicate pathを deduplicateしない。
7. path textが prompt bodyに含まれない。
   8.既存 `PlanningContext` count/text limits が変わらない。
8. attachment content sizeやtree member数による validationが存在しない。

Red command:

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  -q
```

期待結果は failure である。現行 classには bytes fieldsが存在し、pure path-only assemblyもない。

### 6.3 Mandatory scope gate

Red failureを確認した時点で、次を判定する。

```bash
rg -n \
  "PlanningPromptAttachment|exact_attachments|synthesized\\.attachments|_write_transport_pack" \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  tests/unit
```

Exact HEAD では、allowlist 外の application callerと infra consumerに一致する。したがって現行 active-step scopeのまま Greenへ進んではならない。

ここで必要な evidence:

-四ファイルだけでは caller/consumerを移行できないこと。

* compatibility fieldを残すと S03 acceptanceを満たさないこと。
* S04 consumer変更なしでは full regressionが Greenにならないこと。
* plan amendment または atomic cutover briefが必要であること。

### 6.4 Green — 現行 briefでは実行禁止

次の変更は target Green の内容だが、scope/sequenceが再承認されるまで実行しない。

#### Contract Green

* `PlanningPromptAttachment` を production contractから除去する。
* `SynthesizedPlanningPrompt.attachments` と `.exact_attachments` を除去する。
* `attachment_paths` を required immutable tupleにする。
* source bytes read/decode/hash helpersを prompt synthesis pathから除去する。
* pure path assemblerを導入する。
* materialized attachment content limitsを削除する。
* existing source-context limitsを維持する。

#### Caller Green

* Planning は preflight済み canonical/relevant sourceの lexical pathを渡す。
* Review は original Candidate pathを渡す。
* Revision は original Candidate、Review、revision request pathを渡す。
* bytes sensitive scanと content hash再照合を transport stateから除去する。
* typed reviewed identityを generated fileなしで伝える契約を確定する。

#### Consumer Green

* path-only contractを直接使用する consumerが必要である。
* generated prompt-packを使う現行 consumerは互換でない。
  -この変更は S04 所有であり、本 S03 briefでは実行しない。

### 6.5 Refactor — full Green 後のみ

Full consumer cutover後に限り、次を行う。

* unused `hashlib`、`stat`、descriptor-read imports/helperを削除する。
* `MAX_RELEVANT_FILE_BYTES` / `MAX_RELEVANT_TOTAL_BYTES` 等、materialization専用 constantsを削除する。
* `_exact_attachments_have_sensitive_content` を削除する。
* `_attachments_match_source_manifest` の attachment-content branchを削除する。
* `_read_review_supplemental_attachments` を削除する。
* compatibility alias、deprecated bytes property、temporary file bridgeを残さない。
* prompt/resource resolverの S02 behaviorを変更しない。

Refactor後の command:

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain \
  tests/unit/application \
  tests/unit/domain

uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime

git diff --check
```

---

## 7. 必須テストケースと期待結果

| Test                                                         | Fixture / operation                   | 必須 assertion                                                                          |
| ------------------------------------------------------------ | ------------------------------------- | ------------------------------------------------------------------------------------- |
| `tc_s03_001_path_input_has_zero_inspection`                  | nested + hidden + symlink + FIFO      | `read_bytes/rglob/iterdir/stat/resolve` call countが全て0、assembly成功、argv operands exact |
| `test_path_tuple_preserves_order_and_identity`               | 3つの distinct `Path`                   | equalityに加え各 dynamic itemが incoming objectと `is` 一致                                   |
| `test_duplicate_paths_are_not_silently_removed`              | 同一 `Path` を二回                         | 出力にも二回残る                                                                              |
| `test_path_input_rejects_non_path_elements`                  | `str` / `bytes` / `None`              | content-free `ValueError`、filesystem call 0                                           |
| `test_path_input_does_not_normalize`                         | lexical relative paths                | `.resolve/.absolute/expanduser` 0、`str(path)` unchanged                               |
| `test_hidden_and_sensitive_looking_path_is_not_scanned`      | hidden / token-like filename          | assembly成功、prompt本文に path textなし、content scan 0                                       |
| `test_missing_path_is_not_preinspected`                      | 存在しない path object                     | S03 assembly成功。存在判定は transport/pre-submit boundary                                    |
| `test_fifo_is_never_opened`                                  | `os.mkfifo` fixture                   | open/read/stat 0。platform非対応時のみ明示 skip                                                |
| `test_symlink_target_is_not_resolved`                        | symlink / dangling symlink            | resolve/stat/read 0                                                                   |
| `test_synthesized_contract_has_no_attachment_payload_fields` | dataclass introspection               | `attachments`、`exact_attachments`、`content`、`classification`、`sha256` がない             |
| `test_existing_source_context_limits_remain`                 | dependency/relevant/operator limit境界  | 既存境界値は pass、境界超過は従来どおり reject                                                         |
| `test_source_preflight_evidence_is_not_attachment_state`     | fake `PlanningSourceEvidence` + paths | source manifest hashが synthesized path contractに複製されない                                |
| `test_reviewer_uses_original_candidate_path`                 | archive Review request                | Candidate path objectが1回保持され、Candidate bytes/extracted membersなし                      |
| `test_revision_uses_original_evidence_paths`                 | Candidate + Review + request          | 3 pathが同一順序・identityで保持される                                                            |
| `test_no_generated_input_pack_contract`                      | synthesized result inspection         | `context-NNN`、manifest、provenance、source-manifest、stale-if metadataなし                 |
| `test_unknown_operation_still_fails_before_fallback`         | unknown role                          | S02 fail-closed regression                                                            |
| `test_operation_resource_directory_remains_opaque`           | managed attachments dir               | existing S02 tree-enumeration spiesが pass                                             |

### 7.1 Sensitive/private path の期待結果

Sensitive/private path test は pathを public-safe placeholderへ置換して assertionを弱めてはならない。一方で、実際の absolute path textを test failure、prompt、reportへ出してはならない。

検証する内容:

* path objectは contractに保持される。
* path名を credential scannerへ渡さない。
* path contentを開かない。
* promptに path inventoryを出さない。
* exception messageに path textを出さない。
* public `PlanningInvocationResult` に pathを追加しない。

### 7.2 S01 / S02 regression

S03対象外ファイルを変更しない場合も、最低限次を実行する。

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  -q

uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  -q
```

Full application caller cutoverが再承認された場合:

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  -q
```

最終 repository gate:

```bash
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate .
git diff --check
```

この brief 作成時点では、上記実装後 tests は未実行である。

---

## 8. 影響範囲、停止条件、未解決リスク、証跡要求

### 8.1 影響範囲

| Area                           | S03 target impact                                               |
| ------------------------------ | --------------------------------------------------------------- |
| Prompt contract                | bytes/text/classification/SHA fieldを path tupleへ置換              |
| Source preflight               | 既存 exact GitHub/source evidenceを維持し、synthesized content再hashを廃止 |
| Planning                       | canonical/relevant sourceを contentではなく pathとして引き渡す              |
| Review                         | Candidate ZIP original pathを保持。identity伝達方式は要scope解決            |
| Semantic Revision              | Candidate / Review / revision request original pathを保持          |
| Oracle transport               | S03では変更しない。S04 consumer cutoverが必要                              |
| CLI                            | 変更しない。S05所有                                                     |
| Projection                     | 変更しない。S07所有                                                     |
| Output validation              | 変更しない                                                           |
| Recovery / Oracle 0.17 profile | 変更しない                                                           |

### 8.2 Mandatory stop conditions

次のいずれかが発生したら `cl-s03-path-input` を閉じない。

1. attachment pathの target確認に `stat` / `resolve` / `exists` が必要になる。
2. Candidate、Review、identityを送るため copy、temp file、ZIP、manifest が必要になる。
3. path内容を sensitive scan / UTF-8 decode / SHA計算する必要がある。
   4.旧 bytes contractを compatibility fieldとして production resultに残す必要がある。
   5.四ファイル allowlist外の caller/consumer変更が、active-step scope更新なしに必要になる。
4. Reviewer identityを generated attachmentなしで伝える契約が解決できない。
5. S01 receiptと異なり、directory/multiple path capabilityが利用不能と判明する。
6. missing pathやremote attachment failureを inline fallbackで補う提案が出る。
7. installed projectionを手作業で編集する必要がある。
8. `limits` の新しい field/schema/数値を正本なしに定義する必要がある。
9. S04の Oracle argv builderを S03 application/domainへ先行実装する必要がある。
10. existing S01/S02 regressionを Greenに保てない。

Capability gap の場合は、S01 receipt の capability結果と remaining unknown stageへ接続し、`oracle_capability_unsupported` 相当の既存 stop boundaryを維持する。wrapper、API、alternate backend、default branch、inline conversionを追加しない。

### 8.3 Closure / test evidence

Canonical evidence key は必ず次を使用する。

```text
closure id = cl-s03-path-input
test id    = tc-s03-001
```

Exact HEAD の `report.md` は S03以降を `cl-s03-profile` という stale aliasで記録している一方、canonical plan の Closure Index は `cl-s03-path-input` を正本としている。

S03 evidence記録時は次のいずれかが必要である。

* `report.md` の S03行を `cl-s03-path-input` に修正する。
* Closure Delta に `cl-s03-profile -> cl-s03-path-input` の alias mapping、理由、plan amendment/re-review要否を明記する。

`cl-s03-profile` を canonical IDとしてそのまま closeしてはならない。

### 8.4 Report に必要な証跡

実装後の Ledger Note は少なくとも次を持つ。

* repository / branch / exact implementation HEAD。
* changed provider source/test files。
* scope amendmentの有無。
* path-only contract diff summary。
* `tc-s03-001` の fixture category。
  -各 spyの call count=`0`。
* path order / object identity assertion結果。
* focused pytest結果。
* S01/S02 regression結果。
* ruff / mypy / validate / diff-check結果。
* generated input pack、copy、ZIP、hash、scanがないこと。
* provider projectionを編集していないこと。
* Reviewer verdict。
* model request、observed model label、picker verification、reasoning-effort evidenceを別 fieldで記録。
* private absolute path、raw prompt、session handle、transcriptを含めない。
* closure ID `cl-s03-path-input` と test ID `tc-s03-001`。

### 8.5 未解決リスク

1. **Step sequencing risk:** S03 contractと現行 S04 consumerは独立に Greenにならない。
2. **Allowlist risk:** bytes producerが現行四ファイル外にある。
3. **Reviewed identity risk:** generated identity attachmentを廃止した後の Reviewer向け exact identity伝達方式が S03 scope内で未確定。
4. **Raw operator spelling risk:** incoming `Path` より前の CLI raw tokenは現行 request typeから復元できない。
5. **Projection risk:** S03で providerを変更すると、S07まで installed projectionが staleになり得る。
6. **Actual argv risk:** path tupleから direct Oracle operandsへの production wiringは S04まで未検証。
7. **Remote failure risk:** post-upload attachment failure stageは S10 characterization対象のまま。
8. **Report alias risk:** `cl-s03-profile` と canonical `cl-s03-path-input` が不一致。
9. **Model evidence risk:** Luna/Maxの browser実測 receiptがこの実行にはない。

---

## 9. 実装者への最終チェックリスト

* [ ] branch と exact HEAD が本 brief の identityに一致している。
* [ ] S03 Red testを production変更より先に追加した。
* [ ] `tc-s03-001` が nested / hidden / symlink / FIFO を含む。
* [ ] `read_bytes` / `iterdir` / `rglob` / `stat` / `resolve` の各 spyが `0`。
* [ ] incoming dynamic `Path` の順序と object identityが保持される。
* [ ] bytes、decoded text、classification、source label、per-input SHAを新 contractに残していない。
* [ ] pathを resolve、absolute化、expand、deduplicate、copy、renameしていない。
* [ ] attachment content limitや新しい path limitを発明していない。
* [ ] source preflight evidenceと attachment transport stateを同じ field/objectに戻していない。
* [ ] private/sensitive-looking pathを prompt、error、public result、reportへ出していない。
* [ ] Reviewer identityのため generated fileが必要なら実装を停止した。
* [ ] `issue_planning.py` または infra変更が必要なら active-step scope更新前に停止した。
* [ ] S04の Oracle argv builder、pack削除、direct transportを S03へ先行実装していない。
* [ ] installed projectionを直接編集していない。
* [ ] S01/S02 regressionを実行した。
* [ ] closure evidenceは `cl-s03-path-input` / `tc-s03-001` に紐付けた。
* [ ] `cl-s03-profile` を使用する場合は Closure Deltaで canonical IDへ解決した。
* [ ] Luna/Maxの実測成功を receiptなしに主張していない。
* [ ] scope/sequence gateが未解決なら、Red evidenceと stop reasonだけを記録し、S03を closed にしていない。
