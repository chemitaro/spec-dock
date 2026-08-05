# iss-00354 S05 実装前 advisory brief

## 1. 実装指示

S05 は、S03/S04 で確立した path-only / direct attachment transport を、Issue Planning の command、request、application orchestration、prompt synthesis まで一貫させる hard cutover である。

実装は次に限定する。

1. `planning create` から旧 `--context-manifest` を完全に削除する。
2. `planning create`、`review planning`、`planning revise` に optional・repeatable な `--provided-context-path PATH` を追加する。
3. 指定された値を、入力順・重複・相対／絶対の lexical form を維持した `Path` として prompt synthesis へ渡す。
4. provider static operation attachments、既存 required original paths、optional provided paths の順で direct Oracle の repeated `--file` operand へ到達させる。
5. create、review、semantic revision、mechanical revision の既存 identity、preflight/postflight、typed output、publication、stale/rejection semantics を変更しない。

このブリーフは advisory implementation input である。計画補正の採用、実装完了、test PASS、commit、push、fresh code review、Human adoption、PR、merge、Issue close、assurance promotionを意味しない。

---

## 2. Exact repository identity と開始条件

| 項目                      | 確認値                                                                 |
| ----------------------- | ------------------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                               |
| Branch                  | `codex/iss-00354-chatgpt-context-contract`                          |
| Source HEAD             | `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332`                          |
| Named branch comparison | `identical` / ahead `0` / behind `0`                                |
| Default branch fallback | 使用していない                                                             |
| 添付 bundle               | 17ファイルすべて、Source HEAD の対応 Git blob SHA と一致                          |
| S05 plan correction     | `plan.md` の S05 execution cardへ production 3ファイル、test 6ファイルの補正を反映済み |
| Plan-review evidence    | `EAL-032` および `reviews/red-team-review-s05-plan-v1.md` に記録済み        |
| S03/S04 prerequisite    | `report.md` 上で同一 reviewed HEADのclosure済み                            |

Source HEAD の直前の plan-review target `bdad37d7eb6a26204ffde7ae5a60c91e9eedb541` から現在の `a4e38bd...` までの差分は、`report.md` の証跡追記と S05 plan-review artifact の追加だけである。production runtime と対象 tests に追加差分はない。

実装開始直前に、named branch tip が `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` と一致することを再確認する。次のいずれかに該当した場合は、このブリーフを流用せず停止する。

* named branch が存在しない。
* named branch tip が Source HEAD と一致しない。
* repository が `chemitaro/spec-dock` でない。
* default branch を参照しなければ対象を取得できない。
* 添付 bundle と Source HEAD の対象 blob が一致しない。
* Source HEAD 後に対象 runtime/test の先行変更がある。
* S03/S04 path-only/direct-transport closureを構成する実装が変更されている。

default branch、添付だけの内容、ローカル記憶、別ブランチ、推測上のworktreeを exact identity の代替にしてはならない。

canonical requirement/design/plan に残る historical Candidate source identity は、その文書の履歴証跡である。S05 の実装 baseline は本節の `a4e38bd...` であり、historical identity をS05で書き換えない。

---

## 3. モデル要求と実測証跡の境界

実装担当に対する要求値は次である。

```text
GPT-5.6 Luna
Reasoning Effort Max
```

Source HEAD の plan-review evidence に記録されたモデル情報は次に限定される。

```text
requested: gpt-5.6
target: GPT-5.6 Sol
resolved label: GPT-5.6 Pro
verification: independently verified ではない
reasoning effort: 証跡なし
```

したがって、現時点では次を主張しない。

* `GPT-5.6 Luna` が実測された。
* `Reasoning Effort Max` が実測された。
* Luna / Max が verified である。
* model label の自己申告が browser picker evidence より強い。

実装後の証跡にも、browser経路で実測できた値だけを記録する。Reasoning Effort の観測証拠がなければ `Max verified` と記録しない。

---

## 4. S05 の目的

S05 は transport backend、domain lifecycle、output schemaを再設計するステップではない。目的は、旧 manifest-based CLI inputを廃止し、S03/S04のoriginal-path transportをcreate/review/reviseの公開入力まで接続することである。

### 4.1 実装対象

* CLI option surface。
* command args から application request への forwarding。
* application request の新しい path tuple。
* createのmanifest loader除去。
* create/review/semantic revisionからprompt synthesisへのoptional path forwarding。
* prompt synthesisでのpath ordering。
* hard-cutover help/parser tests。
* focused command/application/prompt/transport/lifecycle tests。

### 4.2 非対象

* S06 Blue continuity / private thread binding。
* cross-operation continuation。
* reusable Blue/Red handle。
* provider projection・docs同期。
* Issue全体のregression closure。
* Oracle `0.17.0` compatibility profile。
* recovery taxonomy、retry、inline mode。
* versioned artifact reader。
* public status/reasonの追加。
* Candidate/Review schema変更。
* wrapper、API、alternate backend。
* canonical requirement/design/plan/reportの更新。

---

## 5. Source HEAD で確認した現状事実

### 5.1 CLI / command

`commands/issue_planning.py` は現在、createだけに次の旧契約を持つ。

```text
PlanningCreateArgs.context_manifest_path
--context-manifest
_create_args() で Path へ変換
_run_create() で PlanningCreateRequest.context_manifest_path へ転送
```

review と revise には operator-supplied context path field がない。

`cli/chatgpt_parser.py` は、各 `CommandSpec.add_arguments` を leaf parser にbindするだけである。S05ではこのファイルを変更せず、`commands/issue_planning.py` のargument definitionを変更することでhelp/parser surfaceを切り替える。

### 5.2 Application

`PlanningCreateRequest` は現在 `context_manifest_path` を保持する。

create は `_load_planning_context_manifest()` によって外部 JSON を読み、次へ変換している。

* `relevant_source_paths`
* `operator_context`

manifest loader は次を行う。

* external file read。
* UTF-8 decode。
* JSON parse。
* duplicate key rejection。
* closed schema validation。
* entry count/byte limit。
* sort/dedup/merge。

この処理はopaque path transportではないため、S05でproduction pathから削除する。

一方、以下は既存の正しい境界として維持する。

* exact GitHub preflightは `allow_default_branch_fallback=False`。
* branch/upstream/local HEAD/remote HEAD/source manifest identity不一致ではbackendを開始しない。
* create response後にsource evidenceを再検証する。
* create publication guardでもsource identityを再検証する。
* reviewはoriginal Candidate pathからCandidateを読み、backend後にも同じpathから再検証する。
* reviewはreviewed identityとdigestをprompt/outputへbindする。
* semantic revisionはCandidate、Review、revision requestのoriginal pathsを使用する。
* semantic revisionはReview SHA、Candidate identity、selected findingsをbackend前に検証する。
* mechanical revisionはChatGPT backendを呼ばない。
* typed Candidate ZIP、closed Review JSON、collision/stale/rejected mappingを維持する。

### 5.3 Prompt synthesis

`SynthesizedPlanningPrompt` は既にpath-onlyである。

```python
@dataclass(frozen=True)
class SynthesizedPlanningPrompt:
    role: Literal["planner", "semantic_revision", "reviewer"]
    prompt: str
    attachment_paths: tuple[Path, ...]
    output_expectation: PlanningOutputExpectation | None = None
```

現行prompt synthesisは次の順でpathsを構成する。

```text
provider operation attachments directory
required source/dynamic paths
```

optional operator pathsはまだ存在しない。

### 5.4 Direct transport

read-only対象の `infra/issue_planning_chatgpt.py` は次を既に行う。

```python
for attachment_path in synthesized.attachment_paths:
    argv.extend(("--file", str(attachment_path)))
```

Oracle subprocessは `cwd=repo_root`、`shell=False` で実行される。input prompt-pack、context file、manifest、copy、rename、ZIPを生成しない。

S05ではこのinfraを変更しない。

### 5.5 Tests

Source HEAD のtestsには次の旧契約が残っている。

* command testが `--context-manifest` forwardingを要求する。
* application testsがmanifest loader、schema、deep JSON rejectionを検証する。
* CLI runtime help testがcreate helpに `--context-manifest` を要求する。
* prompt testsにはS03/S04 path-only、opaque directory、no-inspectionの既存テストがある。
* integration testsにはdirect repeated `--file` とlifecycle fake Oracleがある。

旧manifest testsは新しいtransport-only契約のtestsへ置換する。既知failureをS08まで持ち越さない。

---

## 6. S03/S04 から引き継ぐ不変条件

以下を緩めてはならない。

1. provider static operation attachment directoryを最初のattachment operandとする。
2. required dynamic/source pathsをその後に置く。
3. optional operator pathsはrequired pathsの後ろに置く。
4. pathをbytes、text、manifest entry、hash recordへ変換しない。
5. repository-relative pathを `repo_root / path` に変換しない。
6. relative operandはrelativeのままOracleへ渡す。
7. external absolute pathはabsoluteのままOracleへ渡す。
8. duplicate pathをdeduplicateしない。
9. supplied orderをsortしない。
10. pathを`resolve()`、`absolute()`、`stat()`、`exists()`で正規化・検証しない。
11. directoryをwalk、glob、rglob、iterdir、scandirしない。
12. pathまたはそのchildrenをopen、read、decode、hashしない。
13. inputをcopy、rename、replace、archive、ZIP化しない。
14. generated `context-NNN.md`、prompt-pack、input manifest、provenance packを復活させない。
15. Candidate、Review、revision requestのoriginal pathを別名・別directoryへmaterializeしない。
16. private absolute pathをprompt body、Candidate provenance、public resultへ描画しない。
17. default branch fallbackを追加しない。
18. unsupported inputを除外して続行しない。
19. alternate backend、wrapper、API、inline/bytes fallbackを追加しない。
20. direct Oracle invocationのone-prompt、repeated `--file` contractを維持する。

provider-owned resource rootの健全性検証とprovider `prompt.md` のreadは既存管理対象処理であり、operator-supplied pathのinspectionとは区別する。no-inspection spyはoperator-supplied pathとそのdescendantsだけを保護し、provider resource validationを誤って禁止しない。

---

## 7. 許可変更境界

### 7.1 Production write allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

### 7.2 Test write allowlist

```text
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

### 7.3 Read-only inputs

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
```

### 7.4 変更禁止

* canonical requirement/design/plan/report。
  -既存S05 briefやreview artifact。
* Candidate/Review validator。
* closed JSON schema。
* domain public contract。
* infra invocation signature。
* Oracle argv policy。
* CLI parser architecture。
* wrapper/API。
* alternate backend。
* retry loop。
* fallback。
* tree scanner。
* ZIP/input materialization。
* projection。
* S06以降の実装。

read-only fileの変更が必要になった場合、実装範囲を拡張せず停止する。

---

## 8. Public CLI contract

### 8.1 Option

次のoptionを使用する。

```text
--provided-context-path PATH
```

追加対象は次の三commandだけである。

```text
planning create
review planning
planning revise
```

追加しないcommand:

```text
planning apply
```

argument contract:

```python
parser.add_argument(
    "--provided-context-path",
    action="append",
    metavar="PATH",
    help="Optional opaque context path passed directly to Oracle; repeatable.",
)
```

help wordingは同等の意味でよいが、次を示す。

* optional。
* repeatable。
* opaque top-level path。
* direct attachment transport用。

helpは、directory existence、file type、contents、validation、source identityへの採用を示唆してはならない。

### 8.2 Argparse destination

argparseのdestinationは通常どおり単数形となる。

```text
ns.provided_context_path
```

factoryで次へ変換する。

```python
tuple(Path(value) for value in (ns.provided_context_path or ()))
```

変換はCLI stringから`Path`を構築する一回だけである。その後は`resolve()`、`absolute()`、repository-root prefixing等を行わない。

### 8.3 Args/request field

create/review/reviseのcommand argsとapplication requestsに次を持たせる。

```python
provided_context_paths: tuple[Path, ...] = ()
```

対象:

```text
PlanningCreateArgs
PlanningReviewArgs
PlanningReviseArgs

PlanningCreateRequest
PlanningReviewRequest
PlanningReviseRequest
```

apply args/requestには追加しない。

### 8.4 Hard cutover

次はすべて削除する。

```text
--context-manifest
context_manifest_path
_load_planning_context_manifest
_manifest_string_values
_merge_context_values
manifest専用json import
```

次は禁止する。

* `--context-manifest` alias。
* hidden/deprecated optionとしての残置。
* warning付きlegacy acceptance。
* compatibility property。
* JSON-to-path translation。
* old/new dual-write。
* manifestのsilent materialization。
* manifest valuesをprovided pathsとして再解釈すること。

旧optionを指定した場合はargparseのunknown-option errorとしてexit code `2` で拒否し、use-case call、GitHub preflight、backend invocationをすべて `0` にする。

---

## 9. `provided_context_paths` の値契約

### 9.1 順序

指定順をそのまま保持する。

```text
--provided-context-path first
--provided-context-path second
--provided-context-path third
```

は次になる。

```python
(
    Path("first"),
    Path("second"),
    Path("third"),
)
```

### 9.2 重複

重複は保持する。

```text
--provided-context-path same
--provided-context-path same
```

は長さ2のtupleとなる。set化、deduplicationをしない。

### 9.3 Relative / absolute form

CLI boundaryで`Path(value)`を構築した後、その`Path`が表すrelative/absolute formを維持する。

```python
Path("operator/context")       # relative
Path("/external/context")      # absolute
```

relative pathをrepo-root-prefixed absolute pathへ変換しない。absolute pathをrepository-relativeへ変換しない。

### 9.4 Object identity

application requestに直接渡された`Path`は、prompt synthesis後の`attachment_paths`でも同じobject referenceを保持する。

```python
provided = Path("operator/context")
request.provided_context_paths = (provided,)
assert synthesized.attachment_paths[-1] is provided
```

CLI stringからはfactoryが新しい`Path`を構築するが、その後のcommand→request→application→prompt間では同じ`Path` objectを使う。

### 9.5 No inspection

provided pathに対し次を呼ばない。

```text
exists
is_file
is_dir
is_symlink
stat
lstat
resolve
absolute
open
read_text
read_bytes
iterdir
glob
rglob
os.listdir
os.scandir
walk
copy
copy2
copyfile
copytree
rename
replace
ZipFile
archive
hash
```

存在しないpath、symlinkを想定したpath、FIFOを想定したpath、repository外absolute pathもapplicationでは検査しない。

directory-orientedという契約はoperator intentを表し、SpecDockによるfilesystem type checkを意味しない。

### 9.6 Identity boundary

provided pathsはattachment transport専用である。次へ入れない。

* `GitHubSyncPreflightRequest.source_paths`
* `PlanningContext.canonical_issue_paths`
* `PlanningContext.relevant_source_paths`
* `PlanningContext.operator_context`
* `PlanningSourceEvidence`
* source manifest hash
* Candidate source baseline
* Candidate provenance
* reviewed identity
* Review SHA
* publication guard
* public command result

provided pathの内容・存在・mtime・bytesが変化しても、SpecDockはそれをsource stale判定へ使用しない。

---

## 10. ファイルごとの最小変更契約

## 10.1 `commands/issue_planning.py`

### 変更するもの

1. `PlanningCreateArgs.context_manifest_path` を削除する。
2. `PlanningCreateArgs` に `provided_context_paths` を追加する。
3. `PlanningReviewArgs` に `provided_context_paths` を追加する。
4. `PlanningReviseArgs` に `provided_context_paths` を追加する。
5. create/review/reviseの各argument builderに `--provided-context-path` を追加する。
6. `_create_args()`、`_review_args()`、`_revise_args()` でtupleを入力順のまま構築する。
7. `_run_create()`、`_run_review()`、`_run_revise()` で対応requestへtupleをそのまま渡す。

request constructionは次の形にする。

```python
PlanningCreateRequest(
    issue_id=typed.issue_id,
    output_dir=typed.output_dir,
    provided_context_paths=typed.provided_context_paths,
)
```

```python
PlanningReviewRequest(
    issue_id=typed.issue_id,
    mode=typed.mode,
    output_dir=typed.output_dir,
    candidate_path=typed.candidate_path,
    reviewed_head=typed.reviewed_head,
    provided_context_paths=typed.provided_context_paths,
)
```

```python
PlanningReviseRequest(
    candidate_path=typed.candidate_path,
    request_path=typed.request_path,
    output_dir=typed.output_dir,
    provided_context_paths=typed.provided_context_paths,
)
```

### 変更しないもの

* command registry keys。
* output format。
* renderer。
* review/apply mode options。
* Candidate conditional args。
* apply arguments/request。
* `cli/chatgpt_parser.py`。
* error/result serialization。

---

## 10.2 `application/issue_planning.py`

### Request dataclasses

次へ変更する。

```python
@dataclass(frozen=True)
class PlanningCreateRequest:
    issue_id: str
    output_dir: Path
    provided_context_paths: tuple[Path, ...] = ()
```

```python
@dataclass(frozen=True)
class PlanningReviewRequest:
    issue_id: str
    mode: Literal["archive-candidate", "git-bound"]
    output_dir: Path
    candidate_path: Path | None = None
    reviewed_head: str | None = None
    provided_context_paths: tuple[Path, ...] = ()
```

```python
@dataclass(frozen=True)
class PlanningReviseRequest:
    candidate_path: Path
    request_path: Path
    output_dir: Path
    provided_context_paths: tuple[Path, ...] = ()
```

`PlanningContext`、domain contracts、source evidenceにはfieldを追加しない。

### Manifest loader

createから次のblockを削除する。

```text
_load_planning_context_manifest() call
manifest_relevant_paths
manifest_operator_context
_merge_context_values()
manifest parse error mapping
```

manifest専用helperを削除する。

```text
_load_planning_context_manifest
_manifest_string_values
_merge_context_values
```

`json` importが他用途に残らないことを確認し、manifest専用なら削除する。

既存function parametersの次は残す。

```text
relevant_source_paths
operator_context
```

これらは内部application inputであり、旧CLI manifestやprovided attachmentsと同義ではない。

### Create wiring

`run_issue_planning_transport()` のsource preflight contractへprovided pathsを追加しない。

create内で、既存のinjected `prompt_synthesizer` をstep-local wrapperから呼ぶ。

概念形:

```python
def create_prompt_synthesizer(**kwargs: Any) -> Any:
    return prompt_synthesizer(
        **kwargs,
        provided_context_paths=request.provided_context_paths,
    )
```

transport runnerへはこのwrapperを渡す。

```text
prompt_synthesizer=create_prompt_synthesizer
```

これによりprovided pathsを次へ混入させず、prompt synthesisだけへ渡す。

* GitHub source paths。
* preflight。
* `PlanningContext`。
* source manifest。
* Candidate provenance。
* publication guard。

`run_issue_planning_transport()` の公開signatureやgeneric source orchestrationを拡張しない。

### Review wiring

既存 `review_prompt_synthesizer()` のrequired dynamic path組立てを維持し、`synthesize_planning_evidence_prompt()` に次を追加する。

```python
provided_context_paths=request.provided_context_paths
```

required dynamic pathsへ直接mergeせず、prompt synthesizerの専用parameterとして渡す。

review roleは常に次を維持する。

```text
role="reviewer"
```

次を追加しない。

* session locator。
* continuation locator。
* Blue binding。
* reusable Red binding。
* past Review handle。
* private thread store。

### Semantic revision wiring

既存 `revision_prompt_synthesizer()` から次を渡す。

```python
provided_context_paths=request.provided_context_paths
```

既存required attachment tupleは変更しない。

```python
(
    request.candidate_path,
    review_evidence.review_result_path,
    request.request_path,
    *_context_source_operands(repo_root, runtime_context),
)
```

optional pathsはprompt synthesizer内でこのtupleの後ろへ追加する。

### Mechanical revision

`provided_context_paths` を無視する。

mechanical laneでは次を維持する。

```text
prompt synthesizer call = 0
backend invocation = 0
provided path filesystem access = 0
```

provided pathsが空でなくても、新しいrejection、warning、precheck、transport callを追加しない。

### 変更しないもの

* `run_issue_planning_transport()` のexact GitHub gate。
* `PlanningContext` construction。
* source evidence。
* Candidate loader。
* Review parser。
* publication transaction。
* stale reason。
* Candidate versioning。
* `apply_mechanical_revision()`。
* diff budget。
* source/candidate revalidation。

---

## 10.3 `application/issue_planning_prompt.py`

### Signature変更

次の二entry pointへdefault empty tupleを追加する。

```python
def synthesize_issue_planning_prompt(
    *,
    ...
    provided_context_paths: tuple[Path, ...] = (),
    ...
) -> SynthesizedPlanningPrompt:
```

```python
def synthesize_planning_evidence_prompt(
    *,
    ...
    attachment_paths: tuple[Path, ...] = (),
    provided_context_paths: tuple[Path, ...] = (),
    ...
) -> SynthesizedPlanningPrompt:
```

### Create path order

create/planner promptの最終pathsは次の順にする。

```python
(
    resources.attachments_dir,
    *source_paths,
    *provided_context_paths,
)
```

意味上の順序:

```text
1. provider planning attachments directory
2. canonical repository source paths
3. relevant repository source paths
4. optional provided context paths
```

既存source pathのvalidation、ordered-unique semanticsは変更しない。provided pathsに `_ordered_unique()` や `_validate_source_path()` を適用しない。

### Review / semantic revision path order

evidence promptの最終pathsは次の順にする。

```python
(
    resources.attachments_dir,
    *attachment_paths,
    *provided_context_paths,
)
```

意味上の順序:

```text
1. provider review/revision attachments directory
2. applicationが構成したrequired original paths
3. optional provided context paths
```

### Prompt body

次を変更しない。

* `_render_minimal_body()`。
* exact source identity。
* operation context。
* reviewed identity。
* reviewed identity SHA。
* revision scope。
* output expectation。
* attached instructions wording。
* authority boundary。

provided pathの文字列、inventory、count、hashをbodyに描画しない。

### No-inspection

provided pathsにvalidation helperを追加しない。tuple unpack以外の処理を行わない。

---

## 10.4 Read-only files

### `domain/issue_planning_contracts.py`

変更しない。

特に `PlanningContext` へprovided path fieldを追加しない。Review JSON schema、Candidate identity、public reasonを変更しない。

### `infra/issue_planning_chatgpt.py`

変更しない。

既存の次の処理がfinal transportを担当する。

```python
for attachment_path in synthesized.attachment_paths:
    argv.extend(("--file", str(attachment_path)))
```

S05はinfra signature、Oracle argv、session behavior、recovery、output collectionを変更しない。

### `cli/chatgpt_parser.py`

変更しない。

commands側のargument builder変更がleaf help/parserへ反映されることをtestで証明する。

---

## 11. Operation別 end-to-end contract

## 11.1 Create

### Attachment order

```text
1. provider planning attachments directory
2. canonical/relevant repository source operands
3. provided context paths in supplied order
```

### 維持する処理順

1. existing Issue target解決。
2. canonical three documentsのcurrent front matter検証。
3. output directory validation。
4. operation time/onboarding companion決定。
5. exact GitHub preflight。
6. deterministic prompt synthesis。
7. direct repeated `--file` transport。
8. typed authoring ZIP validation。
9. exact source postflight。
10. Candidate material build。
11. publication guard。
12. atomic Candidate publication。
13. Candidate identity / binding output。

### Identity boundary

provided pathsは次に影響させない。

* repository。
* branch。
* HEAD。
* canonical/relevant source list。
* source manifest hash。
* dependency snapshot。
* Candidate source baseline。
* Candidate identity。
* output key set。

### Success

成功時は既存のまま次を返す。

```text
status = ok
reason = candidate_created
```

public output shape:

```text
candidate_path
candidate_identity
git_bound_operation_binding_sha256
zip_byte_count
```

provided pathをpublic outputへ追加しない。

### Rejection / stale

* exact GitHub preflight不成立ではbackend `0`。既存reason mappingを維持する。
* invalid typed ZIPではCandidate publication `0`。
* response後のsource HEAD/hash driftでは次を維持する。

```text
status = stale
reason = planning_source_stale
publisher call = 0
```

* publication guardでsourceが変化した場合も `planning_source_stale`。
* provided pathがmissing、changed、symlink、FIFO、repository外であること自体をapplication rejection/stale理由にしない。

---

## 11.2 Review

### Attachment order

archive-candidate:

```text
1. provider review attachments directory
2. original Candidate ZIP path
3. canonical/relevant source operands
4. provided context paths
```

git-bound:

```text
1. provider review attachments directory
2. original Candidate ZIP path
3. canonical target paths
4. non-duplicate relevant source paths
5. provided context paths
```

### Fresh Red request

次を維持する。

* roleは `reviewer`。
* provider promptはfresh/read-only/defect-only。
* requestにcontinuation/thread locatorがない。
* past Red bindingを受け取らない。
* per-invocation session slugを既存infraに委ねる。
* S06のthread lifecycleを先行実装しない。

### Candidate path

original Candidate `Path`をrequired pathsの先頭に置く。

次を行わない。

* copy。
* rename。
* staging input copy。
* logical filenameへのrename。
* ZIP再作成。
* temporary manifest。

### Identity / parser

次を維持する。

* `ReviewedPlanningIdentity`。
* reviewed identity SHA-256。
* Candidate identity/binding。
* closed `PlanningReviewResult` parser。
* unknown key rejection。
* duplicate key rejection。
* wrong identity rejection。
* unsafe finding rejection。

### Success

成功時は既存のまま次を返す。

```text
status = ok
reason = review_completed
```

### Rejection / stale

* invalid mode/Candidate/requestは `review_request_rejected`。
* wrong reviewed identity、wrong digest、unknown/duplicate JSON keyは `review_result_rejected`。
* backend後にCandidate bytes/identityが変化した場合:

```text
status = stale
reason = review_target_changed
publication = 0
```

* source postflight driftまたはpublication guard driftも `review_target_changed`。
* provided pathsはreviewed identity、digest、stale判定へ入れない。

---

## 11.3 Semantic revision

### Attachment order

```text
1. provider revision attachments directory
2. prior Candidate original path
3. exact Review original path
4. revision request original path
5. canonical/relevant source operands
6. provided context paths in supplied order
```

Candidate、Review、requestの三つはcallerから受け取った同じ`Path` objectを使用する。

### Backend前のgate

次をすべて通過する前にbackendを呼ばない。

* Candidate typed validation。
* revision request parse。
* Candidate identity equality。
* exact Review file availability。
* Review SHA equality。
* Review closed JSON validation。
* reviewed Candidate identity equality。
* blocking P0/P1の存在。
* selected finding validation。
* `revision.validate_against()`。
* exact source preflight。

provided pathsをこれらのidentity gateへ入れない。

### Minimal body

revision scopeは既存の最小表現を維持する。

```text
selected finding <id>: <p0|p1>
preserve assumption: <value>
```

bodyへ次を追加しない。

* finding full text。
* full Review JSON。
* Candidate content。
* attachment path。
* private absolute path。
* provided path inventory。
* selectedでないfinding。

### Success

成功時は既存のまま次を返す。

```text
status = ok
reason = candidate_revised
```

Candidate version increment、identity、binding、typed ZIP contractを変更しない。

### Rejection / stale

* Review unavailableは既存 `revision_review_unavailable`。
* Review digest/Candidate identity/selection mismatchは既存 `revision_evidence_mismatch`。
* invalid requestは既存 `revision_request_rejected`。
* backend transport nonpassは既存transport resultを維持する。
* backend後にCandidateまたはsourceが変化した場合:

```text
status = stale
reason = revision_source_stale
publication = 0
```

provided pathsはrevision identity、Review SHA、source stale判定へ入れない。

---

## 11.4 Mechanical revision

provided pathsが指定されていても、mechanical laneの処理は変えない。

```text
prompt synthesis = 0
backend invocation = 0
Oracle invocation = 0
provided path inspection = 0
```

次を維持する。

* exact Reviewとblocking finding gate。
* `apply_mechanical_revision()`。
* target file validation。
* exact replacement。
* meaning invariant。
* diff budget。
* Candidate version increment。
* source/Candidate revalidation。
* publication guard。
* typed Candidate output。

provided pathsがinvalid/missingであることを理由にmechanical laneを拒否しない。

---

## 12. 最小 test contract

## 12.1 TC-S05-001 — CLI help hard cutover

対象:

```text
tests/cli_runtime/test_chatgpt_cli.py
```

検証:

* `planning create --help` に `--provided-context-path` がある。
* `review planning --help` に `--provided-context-path` がある。
* `planning revise --help` に `--provided-context-path` がある。
* `planning apply --help` に `--provided-context-path` がない。
* create helpに `--context-manifest` がない。
  -既存required/conditional optionsは維持される。
* core CLI helpにはIssue Planning leaf commandsを追加しない。

旧help expectationを新契約へ更新し、known failing expectationを残さない。

---

## 12.2 TC-S05-002 — Old option rejection

対象:

```text
tests/unit/commands/test_issue_planning.py
tests/cli_runtime/test_chatgpt_cli.py
```

入力例:

```text
planning create
--issue iss-00003
--output /tmp/out
--context-manifest /tmp/context.json
```

期待:

```text
argparse exit = 2
use-case call = 0
GitHub preflight = 0
backend invocation = 0
```

旧optionを別名・hidden optionとして受理しない。

---

## 12.3 TC-S05-003 — Repeatable command/request forwarding

対象:

```text
tests/unit/commands/test_issue_planning.py
```

create/review/reviseをtable-drivenに検証する。

入力:

```text
--provided-context-path relative/context
--provided-context-path /external/context
--provided-context-path relative/context
```

期待request:

```python
(
    Path("relative/context"),
    Path("/external/context"),
    Path("relative/context"),
)
```

検証:

* supplied orderを維持。
* duplicateを維持。
* option省略時は `()`。
* create/review/reviseのtyped requestへ渡る。
* apply requestは不変。
* `context_manifest_path` fieldがない。

---

## 12.4 TC-S05-004 — Prompt ordering / identity / no inspection

対象:

```text
tests/unit/application/test_issue_planning_prompt.py
```

provided pathsとして次を使用する。

* 存在しないrepository-relative path。
* repository外absolute path。
  -同じPath objectの重複。
* nested/hidden/symlink/FIFOを想定するopaque path。

create expectation:

```text
provider static dir
canonical/relevant source paths
provided paths
```

evidence expectation:

```text
provider static dir
required dynamic paths
provided paths
```

検証:

* final tuple orderがexact。
* duplicatesが残る。
* provided `Path` objectが同一object。
* relativeはrelativeのまま。
* absoluteはabsoluteのまま。
* bodyにpath文字列がない。
* provided pathまたはdescendantへのfilesystem/tree/content callが `0`。
* provider resource validationは従来どおり動く。
* output expectationは不変。

---

## 12.5 TC-S05-005 — Create success / identity / stale

対象:

```text
tests/unit/application/test_issue_planning.py
```

成功ケース:

* requestのprovided pathsがplanner synthesisへ同じ順序で渡る。
* preflight source pathsへ追加されない。
* `PlanningContext.relevant_source_paths` に追加されない。
* `PlanningContext.operator_context` に追加されない。
* Candidate source baselineへ追加されない。
* public resultへprivate pathが出ない。
  -成功resultは `ok / candidate_created`。
* Candidate identity/output keysは不変。

identity/preflight mismatch:

* branch/upstream/local/remote HEAD不一致でbackend `0`。
* existing reason mappingを変更しない。
* provided pathsがidentity mismatchを回避しない。

stale:

* response後のsource driftで `stale / planning_source_stale`。
* publisher `0`。
* publication guard driftも同じ。
* provided path自体はstale sourceとして扱わない。

旧manifest loader testsは削除または本transport-only contractへ置換する。

---

## 12.6 TC-S05-006 — Review fresh request / original Candidate / identity

対象:

```text
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
```

検証:

* roleは `reviewer`。
* bodyはfresh/read-only/defect-only。
* continuation/session/reusable binding inputがない。
* original Candidate `Path` がrequired dynamic pathの先頭。
* optional pathsは全required pathsの後ろ。
* Candidateをcopy/rename/materializeしない。
* provided pathsをreviewed identityへ入れない。
* closed JSON parserを維持。
* wrong reviewed identity/digest/unknown key/duplicate keyは `review_result_rejected`。
* Candidate mutationまたはsource driftは `review_target_changed`。
* stale時publication `0`。

---

## 12.7 TC-S05-007 — Semantic revision input / minimal scope

対象:

```text
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
```

検証:

* Candidate、Review、revision requestのoriginal `Path` objectを保持。
* exact orderを維持。
* source operandsの後ろにprovided pathsを追加。
* duplicate optional pathsを維持。
* bodyにはselected P0/P1 ID/severityとpreserved assumptionsだけを含める。
* selectedでないfinding、full Review、path inventoryをbodyに入れない。
* Review digest mismatchでbackend `0`。
* Candidate identity mismatchでbackend `0`。
* invalid/unselected findingでbackend `0`。
  -成功時はCandidate version、typed ZIP、binding contractが不変。
* source/Candidate driftでは `revision_source_stale`、publication `0`。

---

## 12.8 TC-S05-008 — Mechanical lane

対象:

```text
tests/unit/application/test_issue_planning.py
```

non-empty `provided_context_paths` を指定したmechanical requestで次を検証する。

```text
prompt synthesizer call = 0
backend invocation = 0
provided path filesystem access = 0
```

さらに既存の次を維持する。

* exact replacement。
* diff budget。
* output version。
* Candidate identity。
* publication behavior。
* `mechanical_revision_rejected`等の既存mapping。

---

## 12.9 TC-S05-009 — Direct transport integration

対象:

```text
tests/integration/test_issue_planning_chatgpt_transport.py
```

create、reviewまたはsemantic reviseの少なくとも一つをfake Oracleまで通し、可能なら三operationをtable-drivenまたは既存chainで確認する。

Oracle argv expectation:

```text
--file <provider static dir>
--file <required path 1>
--file <required path 2>
...
--file <provided path 1>
--file <provided path 2>
```

検証:

* supplied order。
* duplicate retention。
* relative operandはrelative string。
* external absolute operandはsame absolute string。
* `--prompt`は一つ。
* `--file`はpathごとに一つ。
* generated manifest/context file/prompt-packがない。
* input copy/rename/ZIP/hash/materializationがない。
* typed output処理は既存結果と同じ。

---

## 12.10 TC-S05-010 — Lifecycle integration

対象:

```text
tests/integration/test_issue_planning_e2e.py
```

既存lifecycle fixtureを最小拡張する。

```text
create
→ fresh review
→ semantic revise
```

各commandへprovided pathを指定し、fake Oracle recordで次を確認する。

* static/required/optional order。
* original Candidate path。
* original Review path。
* original revision request path。
* reviewed identity。
* closed Review JSON。
* Candidate version increment。
* exact source stale protection。
* no default fallback。
* no input materialization。
* public outputにprovided pathがない。
* canonical documents/repository mutationがない。

S06のBlue continuityはこのtestに追加しない。

---

## 13. 実装順序

1. named branch tipとSource HEAD `a4e38bd...` の一致を再確認する。
2. worktreeにS05 scope外の先行変更がないことを確認する。
3. command/CLI testsをRedにし、新option、旧option rejection、help contractを固定する。
4. `commands/issue_planning.py` のargs/parser/request forwardingをhard cutoverする。
5. application request dataclassesを `provided_context_paths` へ変更する。
6. createのmanifest loader callとmanifest-specific helpers/importを削除する。
7. prompt synthesis entry pointsへ `provided_context_paths` を追加する。
8. prompt order/no-inspection unit testsをGreenにする。
9. createでstep-local prompt wrapperを用い、provided pathsをprompt synthesisだけへ渡す。
10. reviewの既存prompt closureへprovided pathsを接続する。
11. semantic revisionの既存prompt closureへprovided pathsを接続する。
12. mechanical laneのzero-invocation/zero-inspection regressionを固定する。
13. create/review/revision identity・stale testsを実行する。
14. CLI help/runtime testを実行する。
15. transport integrationを実行する。
16. lifecycle full-regression integrationを実行する。
17. legacy contract absenceを検索する。
18. ruff、mypy、diff check、diff scopeを実行する。
19. changed files、source/resulting HEAD、test results、未検証事項を親orchestratorへ返す。

workerはcanonical reportやreview artifactを更新しない。実測結果のreport統合は親orchestratorの責務である。

---

## 14. 必須 verification commands

## 14.1 Focused unit

```bash
uv run pytest \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  -q
```

## 14.2 CLI help / parser hard cutover

```bash
uv run pytest \
  tests/cli_runtime/test_chatgpt_cli.py \
  -q
```

## 14.3 Transport integration

```bash
uv run pytest \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  -q
```

## 14.4 Lifecycle integration

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py \
  -q
```

## 14.5 Ruff

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

## 14.6 Mypy

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

## 14.7 Legacy production contract absence

production filesではzero-matchを要求する。

```bash
rg -n -- \
  '--context-manifest|context_manifest_path|_load_planning_context_manifest|_manifest_string_values|_merge_context_values' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

期待:

```text
zero matches
rg exit code 1
```

testsでは、旧option rejectionを検証するliteral `--context-manifest` だけを許容する。legacy acceptanceやhelp expectationとして残してはならない。

新optionの存在確認:

```bash
rg -n -- \
  'provided_context_paths|--provided-context-path' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

## 14.8 Diff and scope

```bash
git diff --check
```

```bash
git diff --name-only \
  a4e38bd00bf11dd7b2c125e6f33aef630c4cf332...HEAD
```

```bash
git status --short --branch
```

diffは次のallowlist内だけでなければならない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

`spec-dock validate`、provider/installed/dogfood projection、Issue全体のfull regressionはS07/S08以降のclosureである。S05のproduction scopeを拡張する理由にしない。

---

## 15. P0/P1相当の停止条件

次のいずれかを検出した場合はS05実装を停止する。

### 15.1 Identity / source gate

* named branch tipがSource HEADと異なる。
* attached blobとGitHub blobが異なる。
* default branch fallbackが必要。
* scope外変更を分離できない。

戻し先: owning execution orchestration。新しいexact HEADへのbrief rebindが必要。

### 15.2 Plan / allowlist gap

* 許可test file以外を変更しないとhard-cutover testsを実装できない。
* read-only fileの変更が必要。
* S05 execution cardと実装に重大な不一致がある。

戻し先: `plan.md` S05 execution card。

### 15.3 Requirement/design gap

* provided pathsをsource identity、Candidate provenance、reviewed identityへ入れなければ成立しない。
* directory existence/type/content validationが必要。
* input materialization、copy、ZIP、hashが必要。
* Candidate ZIPまたはReview JSON schema変更が必要。
* public reason/status変更が必要。
* output validator緩和が必要。

戻し先: `requirement.md` / `design.md` の明示変更とfresh review。

### 15.4 S06 boundary violation

* fresh Redを実現するためcross-operation bindingが必要。
* Blue continuation store、thread handle、session locatorが必要。
* Red binding reuse防止のためdomain/thread architecture変更が必要。

戻し先: S06計画。S05では実装しない。

### 15.5 S03/S04 regression

* optional pathsがsort/dedup/resolveされる。
* relative pathがabsolute化される。
* no-inspection/no-materialization spyが失敗する。
* generated pack/manifest/context fileが再導入される。
* direct repeated `--file` orderが崩れる。
* infra変更が必要。

戻し先: S03/S04 contract再確認と計画補正。silent compatibility bridgeは作らない。

### 15.6 Lifecycle / output regression

* create exact pre/postflightが緩む。
* Candidate publication identityが変わる。
* review closed JSON parserが緩む。
* reviewed identityが変わる。
* semantic revisionのReview/Candidate gateが弱くなる。
* mechanical laneがbackendを呼ぶ。
* stale時にpublicationされる。
* default fallback、alternate backend、retry、wrapper、APIが必要になる。

戻し先: requirement/design。S05内で回避実装しない。

P2/P3相当の一般化、cleanup、追加refactor、将来拡張、別option、追加backend設計はこのブリーフの対象にしない。

---

## 16. 実装後の fresh Red Team read-only scope

実装担当とは別のfresh Red Team threadを使用する。

### 16.1 Identity

```text
Repository: chemitaro/spec-dock
Branch: codex/iss-00354-chatgpt-context-contract
Review target: push済み exact resulting HEAD
Default branch fallback: 0
```

named branch tipとreview target SHAがidenticalでなければレビューを開始しない。

### 16.2 Review mode

```text
read-only
defect-only
P0/P1 only
```

Red Teamは次を変更しない。

* repository。
* runtime。
* tests。
* canonical docs。
* Candidate。
* Review artifact。
* implementation brief。
* report。

### 16.3 Read-only確認対象

* exact resulting diff。
* S05 production/test allowlist。
* canonical requirement/design/plan。
  -本S05 brief。
* read-only domain/infra/parser files。
* focused verification evidence。
* source/resulting HEAD evidence。

### 16.4 確認事項

1. `--context-manifest` がhelp/parser/args/request/applicationから消えている。
2. hidden alias、translation、compatibility propertyがない。
3. `--provided-context-path` がcreate/review/reviseだけにある。
4. applyに新optionがない。
5. option省略時はempty tuple。
6. supplied orderとduplicatesを保持する。
7. relative/absolute formを保持する。
8. requestからpromptまで`Path` object identityを保持する。
9. static→required→optionalの順序を維持する。
10. provided pathsへのfilesystem/content/tree inspectionがない。
11. copy/rename/ZIP/hash/materializationがない。
12. create exact pre/postflightとCandidate publicationが不変。
13. reviewがfresh/read-only/defect-only requestを維持する。
14. original Candidate path、reviewed identity、closed JSON parserが不変。
15. semantic revisionのCandidate/Review/request順とminimal bodyが不変。
16. mechanical laneのprompt/backend invocationが `0`。
17. identity mismatchとstale pathがpublicationを行わない。
18. S03/S04 direct transport contractが退行していない。
19. required unit/CLI/transport/lifecycle/ruff/mypy/diff-scope evidenceが同一resulting HEADに結び付いている。
20. production/test diffがallowlist外へ出ていない。

fresh reviewの結果はHuman adoption、PR、merge、Issue closeを意味しない。reviewerが使用したmodelまたはReasoning Effortを実測できない場合、Luna/Max verifiedとは記録しない。

---

## 17. Assumptions

1. Public option名は `--provided-context-path` で固定されている。
2. request field名は `provided_context_paths` で固定されている。
3. operatorはtop-level directory-oriented pathとして値を指定する。
4. SpecDockはdirectory性を検査しない。
5. supplied orderとduplicatesはtransport input identityの一部である。
6. CLIで`Path(value)`を構築した後は追加のlexical normalizationを行わない。
7. provided pathsはattachment transport専用である。
8. provided pathsはGitHub source identityではない。
9. provider static operation attachments directoryは常に第一operandである。
10. required source/dynamic pathsの既存順序は変更しない。
11. S03/S04 path-only/direct transport implementationはSource HEADで有効である。
12. S05中にS06 thread continuityを先行実装しない。
13. read-only domain/infra/parser contractだけでS05を実装できる。
14. current output validators、publication gateway、closed Review parserを再利用する。

---

## 18. Open questions

### Blocking

なし。Source HEADでは、前回ブリーフが検出したtest allowlist不足はS05 execution cardへ反映され、fresh plan-review evidenceが記録されている。

実装中に本ブリーフの停止条件へ該当する事実が見つかった場合、それを新しい設計判断で補わず、該当するrequirement/design/plan境界へ戻す。

### Non-blocking

なし。option naming、request shape、path order、identity boundary、test allowlistはS05入力として固定する。

---

## 19. Not verified

* S05 production codeはまだ変更されていない。
  -旧 `--context-manifest` はSource HEADではまだ存在する。
* `--provided-context-path` はSource HEADではまだ存在しない。
* manifest loaderはSource HEADではまだ存在する。
  -本ブリーフ記載のunit testsはまだ実行していない。
* CLI runtime testsはまだ実行していない。
* transport integrationはまだ実行していない。
* lifecycle full-regression integrationはまだ実行していない。
* ruffはまだ実行していない。
* mypyはまだ実行していない。
* legacy zero-match searchはまだ実行していない。
* resulting HEADはまだ存在しない。
* implementation commit/pushはまだ行っていない。
* resulting HEADのclean worktree/GitHub parityはまだ存在しない。
* implementation後のfresh Red Team reviewはまだ行っていない。
* GPT-5.6 Lunaの実測成功は確認していない。
* Reasoning Effort Maxの実測成功は確認していない。
* S06 Blue continuityは実装・検証していない。
* S07 projection/docs consistencyは実装・検証していない。
* S08全体regression closureは実装・検証していない。
* S09以降のOracle `0.17.0` capability/profile/recoveryは実装・検証していない。
* canonical reportへの実装証跡統合は行っていない。
* assurance promotion、Human adoption、PR、merge、Issue closeは行っていない。
