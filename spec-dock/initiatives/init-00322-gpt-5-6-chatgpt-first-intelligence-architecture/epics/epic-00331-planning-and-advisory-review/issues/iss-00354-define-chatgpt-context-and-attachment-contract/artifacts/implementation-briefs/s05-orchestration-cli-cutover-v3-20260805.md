# iss-00354 S05 implementation brief v3 — current exact baseline

> **対象:** `iss-00354` / S05 Orchestration・CLI cutover
> **目的:** S03/S04 で確定した path-only / direct Oracle transport 契約を、旧 manifest-based CLI input から repeatable `provided-context` path input へ切り替える。
> **性質:** 実装担当者向けの current-baseline brief。canonical requirement/design/plan の改訂、設計変更、実装完了、test PASS、review verdict、assurance promotion、PR、merge、Issue closeを意味しない。
> **現行 source identity:** `9a8602a771860bf7959e249926800dabcf3d823b`

---

## 1. Exact repository identity

| 項目                          | 確認値                                        |
| --------------------------- | ------------------------------------------ |
| Repository                  | `chemitaro/spec-dock`                      |
| Named branch                | `codex/iss-00354-chatgpt-context-contract` |
| Current source HEAD         | `9a8602a771860bf7959e249926800dabcf3d823b` |
| Named branch tip comparison | `identical`                                |
| Ahead / behind              | `0 / 0`                                    |
| Default branch fallback     | 使用していない / 使用禁止                             |
| GitHub Connector確認日         | `2026-08-05`                               |
| Implementation diff base    | `9a8602a771860bf7959e249926800dabcf3d823b` |

GitHub Connectorで指定されたnamed branchを確認し、branch tipとcurrent source HEADを比較した結果は次のとおりである。

```text
base:   9a8602a771860bf7959e249926800dabcf3d823b
head:   codex/iss-00354-chatgpt-context-contract
status: identical
ahead:  0
behind: 0
files:  0
```

default branchは参照していない。実装担当者は、このbriefに記載されたrepository、named branch、full SHAを一つの不可分なsource identityとして扱う。

---

## 2. Historical identityとの分離

以下は、既存artifactを生成または再結合した時点のhistorical identityである。

| Artifact / binding          | Historical source identity                 |
| --------------------------- | ------------------------------------------ |
| Original S05 v2 brief       | `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` |
| Identity rebind addendum v1 | `dd780169f65bb923229e7f43c72c6ea744475d49` |
| Identity rebind addendum v2 | `ce7f933ff25e2edfc521d5e05cae995c8f967d69` |
| 本v3 implementation brief    | `9a8602a771860bf7959e249926800dabcf3d823b` |

historical SHAはartifact provenanceとして保持し、current implementation baselineの代替にしてはならない。

元v2 briefまたはrebind addendum中の次の意味だけを、本briefではcurrent source HEADへ置き換える。

* worker開始時のbranch tip一致条件。
* implementation diffの起点。
* concurrent runtime/test/spec driftの検出基準。
* resulting HEADに対するallowlist監査のbase。

元artifactが過去の生成、レビュー、採用、SHA記録を表す箇所は書き換えない。

canonical requirement/design/plan、reportのS03/S04 closure、元v2 brief、rebind addendum v1/v2が本briefの契約入力である。      

---

## 3. Current HEADへのrebind proof

### 3.1 Previous bound baselineからの差分

`ce7f933ff25e2edfc521d5e05cae995c8f967d69` からcurrent source HEADへのGitHub比較結果は次のとおりである。

```text
base:           ce7f933ff25e2edfc521d5e05cae995c8f967d69
head:           9a8602a771860bf7959e249926800dabcf3d823b
status:         ahead
ahead / behind: 1 / 0
commits:        1
files changed:  2
```

変更は次の二件だけである。

```text
report.md
artifacts/implementation-briefs/
  s05-orchestration-cli-cutover-v2-rebind-2-20260805.md
```

current tip commitは、rebind-v2 artifactの保存と`report.md`へのEAL-035追加だけを行うdocs/evidence commitである。

### 3.2 Original v2 sourceからの累積差分

`a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` からcurrent source HEADまでのGitHub比較では、変更ファイルは次の五件だけである。

```text
.assurance.json
report.md
artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-20260805.md
artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-rebind-20260805.md
artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-rebind-2-20260805.md
```

したがって、original v2 brief生成後に次の範囲は変更されていない。

### S05 production runtime

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

### S05 tests

```text
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

### Canonical specifications

```text
requirement.md
design.md
plan.md
```

### Read-only dependencies

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
```

docs/evidence-only additionsはcurrent source identityを更新するが、S05のruntime/test/spec implementation contractを変更していない。`.assurance.json`もprovisional evidence metadataのままであり、このbriefによるassurance promotionはない。

---

## 4. Model要求と実測証跡の境界

実装担当に対する要求設定は次である。

```text
Model: GPT-5.6 Luna
Reasoning Effort: Max
```

本brief作成時には、LunaまたはReasoning Effort Maxを独立に実測・検証できる証跡を取得していない。

したがって、実装記録、test evidence、fresh review inputにおいて次を主張してはならない。

* `GPT-5.6 Luna verified`。
* `Reasoning Effort Max verified`。
* Luna / Maxの組合せが実測されたこと。
* modelの自己申告だけを根拠とするresolved model label。
* model要求値をproduct runtime compatibilityの成功条件として扱うこと。

workerは実測できたprovider/browser evidenceだけを記録する。Reasoning Effortの観測証拠がなければ、要求値としてのみ記録し、verifiedとは記載しない。

---

## 5. S05の実装目的

S05は、旧`--context-manifest`契約をhard cutoverし、S03/S04のoriginal-path transportをcreate、review、reviseのpublic command boundaryまで接続する。

実装後の入力経路は次とする。

```text
CLI repeatable --provided-context-path
    ↓
command args: tuple[Path, ...]
    ↓
application request: tuple[Path, ...]
    ↓
operation-local prompt synthesizer
    ↓
static operation attachment directory
    + required original paths
    + optional provided paths
    ↓
existing infra repeated --file operands
    ↓
direct Oracle
```

S05は次を再設計しない。

* Issue Planning lifecycle。
* exact GitHub preflight/postflight。
* Candidate publication transaction。
* Review JSON parser。
* revision evidence validation。
* mechanical revision。
* Oracle adapter。
* Oracle recovery。
* output schema。
* Blue/Red thread continuity。
* provider projection。
* Oracle `0.17.0` compatibility profile。

---

## 6. Current exact source facts

Current source HEADでは、command層に`PlanningCreateArgs.context_manifest_path`と`--context-manifest`が残り、review/reviseにはoperator-supplied attachment pathがない。

application層では、`PlanningCreateRequest.context_manifest_path`を受け取り、create開始時に`_load_planning_context_manifest()`を呼び出している。manifestは外部file read、UTF-8 decode、JSON parse、duplicate-key検査、closed schema検査、entry limits、sort/dedup/mergeを行う。

prompt synthesisはすでにpath-onlyであり、現在は次の順で`attachment_paths`を作る。

```text
provider operation attachments directory
required source/dynamic paths
```

optional provided pathsはまだ存在しない。

infraは既存`SynthesizedPlanningPrompt.attachment_paths`を順番に反復し、各pathを一つの`--file` operandとして追加する。Oracle subprocessは`cwd=repo_root`かつ`shell=False`であり、S05では変更しない。

current testsには、create commandが`--context-manifest`をforwardする旧contractと、create helpに同optionを要求するexpectationが残っている。

---

## 7. Scope

### 7.1 実装対象

1. `planning create`から旧`--context-manifest`を削除する。
2. 次の三commandへoptional・repeatableな`--provided-context-path PATH`を追加する。

   * `planning create`
   * `review planning`
   * `planning revise`
3. CLI値を、入力順、重複、relative/absolute lexical shapeを維持した`Path` tupleとしてapplicationへ渡す。
4. create/review/semantic revisionのprompt synthesisへoptional pathsを接続する。
5. attachment順序を次に固定する。

   * provider static attachment directory。
   * required original paths。
   * optional provided context paths。
6. mechanical revisionではprovided pathsを無視し、backend invocationを引き続き行わない。
7. old manifest loaderとmanifest専用helper/importをproduction pathから削除する。
8. command、application、prompt、CLI、transport、lifecycle testsを新契約へ同期する。

### 7.2 非対象

* `planning apply`への新option追加。
* `PlanningContext`へのfield追加。
* `PlanningSourceEvidence`へのfield追加。
* Candidate source baseline/provenanceへのprovided path追加。
* Reviewed identityへのprovided path追加。
* Review JSON schema変更。
* Candidate ZIP schema変更。
* public resultへのprovided path追加。
* source stale判定へのprovided path追加。
* direct Oracle infraの変更。
* `cli/chatgpt_parser.py`の変更。
* domain public reason/status変更。
* thread handle、continuation、Blue/Red binding。
* inline transport。
* retry/fallback。
* input materialization。
* provider projection/docs更新。
* S06以降の先行実装。

---

## 8. S03/S04から継承する不変条件

以下をすべて維持する。

1. provider static operation attachment directoryを常に第一operandとする。
2. required source/dynamic pathsをその後に置く。
3. optional provided pathsを全required pathsの後ろに置く。
4. provided pathsがrequired pathと同じでもdeduplicateしない。
5. provided paths同士の重複を保持する。
6. supplied orderをsortしない。
7. repository-relative pathを`repo_root / path`へ変換しない。
8. relative pathをrelativeのままOracleへ渡す。
9. absolute pathをabsoluteのままOracleへ渡す。
10. `resolve()`、`absolute()`、`exists()`、`stat()`等でprovided pathを正規化・検査しない。
11. directoryをwalk、glob、rglob、iterdir、listdir、scandirしない。
12. provided pathまたはそのchildをopen、read、decode、hashしない。
13. provided inputをcopy、rename、replace、archive、ZIP化しない。
14. `context-NNN.md`、prompt-pack、input manifest、input provenanceを生成しない。
15. Candidate、Review、revision requestのoriginal pathをcopyまたはrenameしない。
16. private absolute pathをprompt body、Candidate、Review、public resultへ描画しない。
17. unsupported entryを除外して処理を続行しない。
18. no-bytes fallbackを維持する。
19. wrapper、API、alternate backendへfallbackしない。
20. one promptとrepeated `--file` contractを維持する。

provider-owned resource treeの健全性検査とprovider `prompt.md`のreadは既存の管理対象処理であり、operator-supplied provided pathのinspectionとは別である。no-inspection testsはprotected optional pathsとそのlexical descendantsだけを対象とし、provider resource validationを無効化してはならない。

---

## 9. Write allowlist

### 9.1 Production

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

### 9.2 Tests

```text
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

### 9.3 Read-only

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
```

### 9.4 Worker変更禁止

```text
requirement.md
design.md
plan.md
report.md
.assurance.json
artifacts/implementation-briefs/*
reviews/*
provider/installed/dogfood projection
Candidate/Review validators
Oracle artifact reader
Oracle profile/recovery code
```

read-only fileまたはallowlist外testの変更が必要になった場合、範囲を自己拡張せず停止する。

---

## 10. Public CLI contract

### 10.1 新option

```text
--provided-context-path PATH
```

追加対象:

```text
planning create
review planning
planning revise
```

追加禁止:

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

help wordingは完全一致でなくてもよいが、次の意味を保持する。

* optional。
* repeatable。
* opaque top-level path。
* direct attachment transport用。

helpにdirectory existence、file type、content validation、source identity採用、automatic conversionを示唆する文言を入れない。

### 10.2 Argparse destination

argparse destinationは次とする。

```text
provided_context_path
```

factory変換は一回だけ行う。

```python
tuple(Path(value) for value in (ns.provided_context_path or ()))
```

`Path(value)`の後にresolve、absolute化、repo-root prefixing、validationを行わない。

### 10.3 Argsとapplication request

次の六型にfieldを追加する。

```text
PlanningCreateArgs
PlanningReviewArgs
PlanningReviseArgs

PlanningCreateRequest
PlanningReviewRequest
PlanningReviseRequest
```

field contract:

```python
provided_context_paths: tuple[Path, ...] = ()
```

`PlanningApplyArgs`と`PlanningApplyRequest`は変更しない。

### 10.4 Hard cutover

productionから次を削除する。

```text
--context-manifest
context_manifest_path
_load_planning_context_manifest
_manifest_string_values
_merge_context_values
manifest専用json import
```

禁止:

* deprecated alias。
* hidden option。
* warning付きlegacy acceptance。
* old/new dual-write。
* JSON-to-path translation。
* compatibility property。
* silent materialization。
* manifest entryをprovided pathとして再解釈する処理。

旧optionを指定した場合はargparse unknown-optionとしてexit code `2`で拒否する。use-case、GitHub preflight、prompt synthesis、backend invocationはすべて`0`とする。

---

## 11. `provided_context_paths` value contract

### 11.1 Order

```text
--provided-context-path first
--provided-context-path second
--provided-context-path third
```

は次のtupleを形成する。

```python
(
    Path("first"),
    Path("second"),
    Path("third"),
)
```

### 11.2 Duplicate retention

```text
--provided-context-path same
--provided-context-path same
```

は長さ2のtupleとする。`set`化、ordered-unique処理、required pathsとのdeduplicationも行わない。

### 11.3 Lexical relative/absolute shape

```python
Path("operator/context")
Path("/external/context")
```

をその形のまま保持する。

* relative pathをrepo-root absolute pathへ変換しない。
* absolute pathをrepository-relativeへ変換しない。
* `..`、hidden name、symlinkを想定する文字列をapplicationで解釈しない。

### 11.4 Object identity

application requestとして受け取った`Path`は、prompt synthesis後の`attachment_paths`でも同じobject referenceを保持する。

```python
provided = Path("operator/context")
request.provided_context_paths = (provided,)
assert synthesized.attachment_paths[-1] is provided
```

CLI boundaryではstringから新しい`Path`を構築するが、その後のcommand args → request → application → prompt間では同じobjectを渡す。

### 11.5 No inspection

provided pathsに対する次の呼出しを禁止する。

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
os.walk
copy
copy2
copyfile
copytree
rename
replace
ZipFile
make_archive
hash
```

存在しないpath、repository外absolute path、symlink/FIFOを想定するpathもapplicationで検査しない。

### 11.6 Identity boundary

provided pathsはattachment transport専用である。次へ含めない。

```text
GitHubSyncPreflightRequest.source_paths
PlanningContext.canonical_issue_paths
PlanningContext.relevant_source_paths
PlanningContext.operator_context
PlanningSourceEvidence
source manifest hash
Candidate source baseline
Candidate provenance
ReviewedPlanningIdentity
reviewed identity SHA
Review result SHA
publication guard
stale-source comparison
public command result
```

provided pathのexistence、mtime、content、target、bytesが変化しても、SpecDockはそれをsource freshness判定へ使用しない。

---

## 12. File/function-level changes

## 12.1 `commands/issue_planning.py`

### Dataclasses

* `PlanningCreateArgs.context_manifest_path`を削除する。
* `PlanningCreateArgs.provided_context_paths`を追加する。
* `PlanningReviewArgs.provided_context_paths`を追加する。
* `PlanningReviseArgs.provided_context_paths`を追加する。
* `PlanningApplyArgs`は変更しない。

### `_add_create_arguments()`

* `--context-manifest` definitionを削除する。
* repeatable `--provided-context-path`を追加する。
* `--issue`、`--output`、`--format`は変更しない。

### `_add_review_arguments()`

* repeatable `--provided-context-path`を追加する。
* mode、candidate、reviewed-head、output、format契約は変更しない。

### `_add_revise_arguments()`

* repeatable `--provided-context-path`を追加する。
* Candidate、request、output、format契約は変更しない。
* sibling `planning-review-result.json` help wordingは維持する。

### `_create_args()`

次を削除する。

```text
context_manifest_path=...
```

次を構成する。

```text
provided_context_paths=tuple(Path(value) for value in (ns.provided_context_path or ()))
```

### `_review_args()` / `_revise_args()`

同じ変換でtupleを作る。入力順と重複を保持する。

### `_run_create()` / `_run_review()` / `_run_revise()`

typed argsのtupleを対応application requestへそのまま渡す。

### 変更しないもの

* `command_specs()` keys。
* renderer。
* output format。
* cross-mode conditional validation。
* apply command。
* result serialization。
* `cli/chatgpt_parser.py`。

---

## 12.2 `application/issue_planning.py`

### Request dataclasses

契約shapeを次へ変更する。

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

既存のpositional constructorが末尾default fieldの追加により不要に壊れないことを確認する。

### Manifest loader削除

`run_issue_planning_create()`から次を削除する。

```text
_load_planning_context_manifest() call
manifest_relevant_paths
manifest_operator_context
_merge_context_values() calls
manifest parse error block
```

moduleから次を削除する。

```text
_load_planning_context_manifest
_manifest_string_values
_merge_context_values
```

`json` importが他用途に残らない場合だけ削除する。未使用importを残さない。

既存function引数の次は維持する。

```text
relevant_source_paths
operator_context
```

これらはapplication内部のsource/context inputであり、provided attachment pathsとは統合しない。

### `run_issue_planning_create()`

provided pathsを`run_issue_planning_transport()`のsource inputへ追加しない。

既存injectable `prompt_synthesizer`を、create-local wrapperで包む。

概念契約:

```text
create_prompt_synthesizer(**kwargs)
    → prompt_synthesizer(
          **kwargs,
          provided_context_paths=request.provided_context_paths,
      )
```

`transport_runner()`にはこのwrapperを渡す。

これにより、provided pathsはprompt synthesisだけへ到達し、次へ混入しない。

* preflight source paths。
* `PlanningContext`。
* source evidence。
* Candidate baseline。
* publication guard。

`run_issue_planning_transport()`のsignatureを変更しない。

### `run_issue_planning_review()`

既存`review_prompt_synthesizer()`のrequired dynamic paths構成を維持する。

archive-candidate required paths:

```text
original Candidate path
canonical/relevant source operands
```

git-bound required paths:

```text
original Candidate path
canonical target paths
non-duplicate relevant source paths
```

`synthesize_planning_evidence_prompt()`呼出しへ、required tupleとは別parameterとして次を渡す。

```text
provided_context_paths=request.provided_context_paths
```

`dynamic_paths`自体へmerge、sort、dedupしない。

次を維持する。

* `role="reviewer"`。
* fresh/read-only/defect-only provider resource。
* original Candidate path。
* reviewed identity。
* reviewed identity digest。
* closed Review JSON parser。
* Candidate/source postflight。
* publication guard。

thread handle、continuation locator、past Red bindingは追加しない。

### `run_issue_planning_revise()` — semantic lane

既存required attachment tupleを変更しない。

```text
request.candidate_path
review_evidence.review_result_path
request.request_path
context source operands
```

`synthesize_planning_evidence_prompt()`へ次を追加する。

```text
provided_context_paths=request.provided_context_paths
```

optional pathsはprompt synthesizer内でrequired tupleの後ろへ追加する。

次を変更しない。

* Candidate validation。
* Review SHA equality。
* reviewed Candidate identity equality。
* selected blocking finding validation。
* preserve assumptions。
* exact source preflight。
* Candidate version increment。
* typed ZIP output。
* source/Candidate postflight。
* publication guard。

### `run_issue_planning_revise()` — mechanical lane

non-empty `request.provided_context_paths`を受け取っても無視する。

維持するcall count:

```text
prompt synthesizer: 0
transport runner:   0
backend invoker:    0
Oracle invocation:  0
provided-path I/O:  0
```

provided pathがmissing、outside repository、symlink、FIFO等であることを理由にmechanical revisionを拒否しない。

---

## 12.3 `application/issue_planning_prompt.py`

### `synthesize_issue_planning_prompt()`

default empty tuple parameterを追加する。

```text
provided_context_paths: tuple[Path, ...] = ()
```

最終attachment order:

```text
resources.attachments_dir
source_paths
provided_context_paths
```

コードshape:

```text
(
    resources.attachments_dir,
    *source_paths,
    *provided_context_paths,
)
```

既存source path validation、ordered canonical/relevant source contractは変更しない。provided pathsへsource validationやordered-unique処理を適用しない。

### `synthesize_planning_evidence_prompt()`

default empty tuple parameterを追加する。

```text
provided_context_paths: tuple[Path, ...] = ()
```

最終attachment order:

```text
resources.attachments_dir
attachment_paths
provided_context_paths
```

コードshape:

```text
(
    resources.attachments_dir,
    *attachment_paths,
    *provided_context_paths,
)
```

### Prompt body

次を変更しない。

* `_render_minimal_body()`。
* exact source identity。
* operation context。
* GitHub connector gate。
* repository access hard failure。
* Human authority boundary。
* reviewed identity。
* reviewed identity SHA。
* revision scope。
* expected output。
* attached-instructions wording。

provided pathの次の情報をbodyへ描画しない。

```text
path string
inventory
count
hash
type
existence
private absolute location
```

### No inspection

provided tupleはunpack以外の処理をしない。validation helper、scanner、limit、normalizerを追加しない。

---

## 12.4 Read-only files

### `domain/issue_planning_contracts.py`

変更しない。

特に次を追加・変更しない。

* `PlanningContext` field。
* public reason。
* Candidate identity。
* Review schema。
* Review finding schema。
* source evidence。
* serialization。

### `infra/issue_planning_chatgpt.py`

変更しない。

既存処理がtransportを担当する。

```text
for attachment_path in synthesized.attachment_paths:
    argv.extend(("--file", str(attachment_path)))
```

S05ではOracle argv policy、session slug、recovery、environment、managed Chrome、artifact captureを変更しない。

### `cli/chatgpt_parser.py`

変更しない。

command-side argument builderの変更だけでleaf parser/help surfaceを切り替え、testsで証明する。

---

## 13. Operation contracts

## 13.1 Create

### Final attachment order

```text
1. provider planning attachments directory
2. canonical repository source paths
3. relevant repository source paths
4. provided context paths in supplied order
```

provided pathがcanonical/relevant pathと同じでも末尾にもう一度残す。

### 維持する処理順

1. existing Issue target resolution。
2. current canonical document front matter validation。
3. candidate output directory validation。
4. operation time/onboarding companion決定。
5. exact GitHub preflight。
6. deterministic prompt synthesis。
7. direct repeated `--file` transport。
8. typed authoring ZIP validation。
9. exact source postflight。
10. Candidate material build。
11. publication guard。
12. atomic Candidate publication。
13. Candidate identity/binding result。

### Success contract

```text
status = ok
reason = candidate_created
```

public output keysは既存のまま維持する。

```text
candidate_path
candidate_identity
git_bound_operation_binding_sha256
zip_byte_count
```

provided path、count、inventoryを追加しない。

### Stale/rejection contract

* exact GitHub preflight failureではbackend `0`。
* invalid typed ZIPではpublication `0`。
* response後またはpublication guard時のsource drift:

```text
status = stale
reason = planning_source_stale
```

* provided path自体の変化はsource stale判定に使わない。

---

## 13.2 Review

### Archive-candidate order

```text
1. provider review attachments directory
2. original Candidate ZIP path
3. canonical/relevant source operands
4. provided context paths
```

### Git-bound order

```text
1. provider review attachments directory
2. original Candidate ZIP path
3. canonical target paths
4. non-duplicate relevant source paths
5. provided context paths
```

### Fresh Red boundary

S05では次だけを維持する。

* roleは`reviewer`。
* provider promptはfresh/read-only/defect-only。
* requestにcontinuation/thread locatorがない。
* past Red bindingを入力しない。
* existing infraがper-invocation session slugを作る。

S06のthread continuityやprivate binding storeを先行実装しない。

### Identity/parser

維持する。

* `ReviewedPlanningIdentity`。
* reviewed identity SHA-256。
* Candidate identity/binding。
* strict closed `PlanningReviewResult`。
* unknown key rejection。
* duplicate key rejection。
* wrong identity/digest rejection。
* unsafe finding rejection。

### Result contract

success:

```text
status = ok
reason = review_completed
```

stale:

```text
status = stale
reason = review_target_changed
publication = 0
```

provided pathsをreviewed identityまたはstale判定に含めない。

---

## 13.3 Semantic revision

### Final order

```text
1. provider revision attachments directory
2. prior Candidate original path
3. exact Review original path
4. revision request original path
5. canonical/relevant source operands
6. provided context paths
```

Candidate、Review、revision requestはcallerから受け取ったoriginal `Path` objectを保持する。

### Backend-before gates

次がすべて成立する前にbackendを呼ばない。

* Candidate typed validation。
* revision request parse。
* Candidate identity equality。
* exact Review availability。
* Review SHA equality。
* closed Review JSON validation。
* reviewed Candidate identity equality。
* blocking P0/P1 existence。
* selected finding validation。
* `revision.validate_against()`。
* exact source preflight。

provided pathsをこれらのgateへ入れない。

### Minimal body

revision scopeは既存の次だけとする。

```text
selected finding <id>: <p0|p1>
preserve assumption: <value>
```

full finding、full Review、Candidate content、attachment path inventory、unselected findingをbodyへ追加しない。

### Result contract

success:

```text
status = ok
reason = candidate_revised
```

source/Candidate drift:

```text
status = stale
reason = revision_source_stale
publication = 0
```

---

## 13.4 Mechanical revision

provided pathsの有無にかかわらず、existing mechanical behaviorを維持する。

```text
prompt synthesis = 0
backend invocation = 0
Oracle invocation = 0
provided path inspection = 0
```

次を変更しない。

* exact Review gate。
* selected blocking finding gate。
* `apply_mechanical_revision()`。
* target file validation。
* exact replacement。
* meaning invariant。
* diff budget。
* Candidate version increment。
* source/Candidate revalidation。
* publication guard。
* typed Candidate output。
* existing reason mapping。

---

## 14. Test contract

## TC-S05-001 — CLI help hard cutover

対象:

```text
tests/cli_runtime/test_chatgpt_cli.py
```

assertions:

* `planning create --help`に`--provided-context-path`がある。
* `review planning --help`に`--provided-context-path`がある。
* `planning revise --help`に`--provided-context-path`がある。
* `planning apply --help`に同optionがない。
* create helpに`--context-manifest`がない。
* existing required/conditional optionsは維持される。
* core CLI helpにIssue Planning leaf commandを追加しない。
* revise helpのReview sibling契約を維持する。

---

## TC-S05-002 — Old option rejection

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
prompt synthesis = 0
backend invocation = 0
```

unit parser testでは`SystemExit.code == 2`を確認し、CLI subprocessではreturn code `2`を確認する。旧optionをhidden aliasとして受理しない。

---

## TC-S05-003 — Repeatable forwarding

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

expected request:

```python
(
    Path("relative/context"),
    Path("/external/context"),
    Path("relative/context"),
)
```

assertions:

* supplied orderを保持。
* duplicateを保持。
* option省略時は`()`.
* typed requestへ同じtupleを渡す。
* applyにfield/optionを追加しない。
* `context_manifest_path` fieldがない。

---

## TC-S05-004 — Prompt ordering、object identity、no inspection

対象:

```text
tests/unit/application/test_issue_planning_prompt.py
```

provided fixtures:

* nonexistent repository-relative path。
* repository外absolute path。
  -同じ`Path` objectの重複。
* required pathと同一のoptional path。
* nested/hidden/symlink/FIFOを想定するopaque path。

planner expectation:

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

assertions:

* exact tuple order。
* duplicate retention。
* `Path` object identity。
* relative shape保持。
* absolute shape保持。
* bodyにprovided path文字列がない。
* protected provided path/descendantへのfilesystem、tree、content、copy、ZIP、hash callが`0`。
* provider resource validationは既存どおり動作。
* output expectationは不変。

spyはprotected optional operandsだけをfailさせる。provider resource directoryやcanonical managed source validationを一律に禁止しない。

---

## TC-S05-005 — Create identity、success、stale

対象:

```text
tests/unit/application/test_issue_planning.py
```

success assertions:

* requestのprovided tupleがplanner synthesisへ同じ順序・objectで渡る。
* preflight source pathsへ追加されない。
* `PlanningContext.relevant_source_paths`へ追加されない。
* `PlanningContext.operator_context`へ追加されない。
* Candidate source baselineへ追加されない。
* public resultへprovided/private pathが出ない。
* resultは`ok / candidate_created`。
* Candidate identity/output key setは不変。

preflight/identity assertions:

* branch/upstream/local/remote HEAD mismatchではbackend `0`。
* existing reason mappingを維持。
* provided pathがidentity mismatchを回避しない。

stale assertions:

* response後source driftで`stale / planning_source_stale`。
* publisher `0`。
* publication guard driftも同じ。
* provided path変化だけではstaleにしない。

既存manifest loader/schema/deep-JSON testsは削除し、transport-only contract testsへ置換する。

---

## TC-S05-006 — Review fresh request、original Candidate、identity

対象:

```text
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
```

assertions:

* roleは`reviewer`。
* bodyはfresh/read-only/defect-only。
* continuation/session/reusable binding inputがない。
* original Candidate pathがrequired pathsの先頭。
* optional pathsが全required pathsの後ろ。
* Candidateをcopy、rename、materializeしない。
* provided pathsをreviewed identityへ含めない。
* closed JSON parserを維持。
* wrong reviewed identity/digest、unknown key、duplicate keyは`review_result_rejected`。
* Candidate mutationまたはsource driftは`review_target_changed`。
* stale時publication `0`。

---

## TC-S05-007 — Semantic revision original pathsとminimal scope

対象:

```text
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
```

assertions:

* Candidate、Review、revision requestのoriginal `Path` objectを保持。
* required orderを維持。
* source operandsの後ろにprovided pathsを追加。
* duplicate optional pathsを保持。
* bodyにはselected P0/P1 ID/severityとpreserved assumptionsだけを含める。
* full Review、unselected finding、path inventoryをbodyに入れない。
* Review digest mismatchでbackend `0`。
* Candidate identity mismatchでbackend `0`。
* invalid/unselected findingでbackend `0`。
* success時のCandidate version、typed ZIP、binding contractは不変。
* source/Candidate driftで`revision_source_stale`、publication `0`。

---

## TC-S05-008 — Mechanical lane

対象:

```text
tests/unit/application/test_issue_planning.py
```

non-empty `provided_context_paths`を指定して次をassertする。

```text
prompt synthesizer call = 0
transport runner call = 0
backend invocation = 0
provided path filesystem access = 0
```

既存のexact replacement、diff budget、Candidate version、identity、publication、reason mappingを維持する。

---

## TC-S05-009 — Direct transport integration

対象:

```text
tests/integration/test_issue_planning_chatgpt_transport.py
```

少なくともcreateをfake Oracle/backendまで通し、可能な既存fixture範囲でreview/semantic reviseもtable-drivenに確認する。

expected argv order:

```text
--file <provider static dir>
--file <required path 1>
--file <required path 2>
...
--file <provided path 1>
--file <provided path 2>
```

assertions:

* supplied order。
* duplicate retention。
* relative operandはsame relative string。
* external absolute operandはsame absolute string。
* `--prompt`は一つ。
* pathごとに一つの`--file`。
* generated manifest/context/prompt-packがない。
* input copy/rename/ZIP/hash/materializationがない。
* typed output処理は既存結果と同じ。
* infra production codeの変更なし。

---

## TC-S05-010 — Lifecycle integration

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

各operationへprovided pathsを渡し、fake Oracle/backend recordで確認する。

* static→required→optional order。
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
* S06 Blue continuityを追加していない。

---

## 15. Implementation order

1. repository、branch、exact current source HEADを再確認する。
2. local worktreeのclean状態またはscope外差分の安全な分離を確認する。
3. current source HEAD後にS05 runtime/test/spec driftがないことを確認する。
4. command/CLI testsをRedにする。
5. help surface、新option forwarding、old option exit `2`を固定する。
6. `commands/issue_planning.py`をhard cutoverする。
7. application request dataclassesを`provided_context_paths`へ変更する。
8. createのmanifest loader call、helpers、unused importを削除する。
9. prompt entry pointsへoptional tupleを追加する。
10. prompt order、duplicate、lexical shape、object identity、no-inspection testsをGreenにする。
11. create-local prompt wrapperでprovided pathsをprompt synthesisだけへ接続する。
12. review prompt closureへprovided pathsを接続する。
13. semantic revision prompt closureへprovided pathsを接続する。
14. mechanical laneのzero-invocation/zero-inspectionを固定する。
15. create/review/revision identity・stale regressionを実行する。
16. CLI help/parser testsを実行する。
17. transport integrationを実行する。
18. lifecycle full-regression integrationを実行する。
19. legacy contract zero-matchを確認する。
20. Ruff、Mypy、diff check、allowlist scope監査を実行する。
21. source/resulting HEAD、changed files、command results、未検証事項を親orchestratorへ返す。

workerは`report.md`、review artifact、canonical docsを更新しない。reportへの証跡統合は親orchestratorの責務である。

---

## 16. Required verification commands

### 16.1 Focused unit

```bash
uv run pytest \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  -q
```

### 16.2 CLI help/parser hard cutover

```bash
uv run pytest \
  tests/cli_runtime/test_chatgpt_cli.py \
  -q
```

### 16.3 Transport integration

```bash
uv run pytest \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  -q
```

### 16.4 Lifecycle integration

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py \
  -q
```

### 16.5 Ruff

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

### 16.6 Mypy

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

### 16.7 Legacy production contract absence

```bash
rg -n -- \
  '--context-manifest|context_manifest_path|_load_planning_context_manifest|_manifest_string_values|_merge_context_values' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

expected:

```text
zero matches
rg exit code 1
```

testsではold-option rejectionを検証するliteral `--context-manifest`だけを許容する。legacy help expectation、acceptance、translationとして残してはならない。

### 16.8 New contract presence

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

### 16.9 Diff integrity

```bash
git diff --check
```

```bash
git diff --name-only \
  9a8602a771860bf7959e249926800dabcf3d823b...HEAD
```

```bash
git status --short --branch
```

diffはSection 9のproduction/test allowlist内だけでなければならない。

`spec-dock validate`、provider/installed/dogfood projection、Issue全体のfull regressionはS07/S08以降のclosureであり、S05 production scopeを拡張する理由にしない。

---

## 17. Worker preconditions

実装またはRed test作成前に、次をすべて確認する。

1. repositoryが`chemitaro/spec-dock`である。
2. current branchが`codex/iss-00354-chatgpt-context-contract`である。
3. named branch tipが`9a8602a771860bf7959e249926800dabcf3d823b`と完全一致する。
4. default branch fallbackを使用していない。
5. local HEADとremote named branch tipが一致する。
6. local worktreeがclean、またはscope外変更を安全に分離できる。
7. current source HEAD後にproduction 3ファイルまたはtest 6ファイルの先行変更がない。
8. canonical requirement/design/planに先行変更がない。
9. S03/S04 path-only/direct-transport baselineに先行変更がない。
10. read-only domain/infra/parserに先行変更がない。
11. 本v3 briefをcurrent implementation inputとして使用し、旧v2/rebindのSHAをdiff baseに使わない。
12. implementation diffを`9a8602a...`起点で監査する。

推奨local確認:

```bash
git fetch origin codex/iss-00354-chatgpt-context-contract

test "$(git branch --show-current)" = \
  "codex/iss-00354-chatgpt-context-contract"

test "$(git rev-parse HEAD)" = \
  "9a8602a771860bf7959e249926800dabcf3d823b"

test "$(git rev-parse refs/remotes/origin/codex/iss-00354-chatgpt-context-contract)" = \
  "9a8602a771860bf7959e249926800dabcf3d823b"

git status --short --branch
```

いずれかを満たさない場合、このbriefはstaleである。実装を開始せず`BLOCKED`とし、新しいnamed branch tipへのidentity rebindを必要とする。

GitHub Connectorはworkerのlocal worktree clean状態を検証していない。これはworker開始時の未検証preconditionである。

---

## 18. P0/P1相当の停止条件

### 18.1 Identity/source boundary

次の場合は停止する。

* named branch tipがcurrent source HEADと異なる。
* repositoryまたはbranchが異なる。
* default branchが必要。
* current source HEAD後にruntime/test/spec driftがある。
* scope外worktree changeを安全に分離できない。

戻し先: owning execution orchestration。新しいexact HEADへのbrief rebindを行う。

### 18.2 Allowlist gap

次の場合は停止する。

* allowlist外production/test fileを変更しないとhard cutoverできない。
* read-only domain/infra/parserの変更が必要。
* generic `run_issue_planning_transport()` signature変更が必要。
* S05 execution cardと実装可能範囲に重大な不一致がある。

戻し先: canonical `plan.md` S05 execution card。workerがscopeを自己拡張しない。

### 18.3 Requirement/design gap

次の場合は停止する。

* provided pathsをsource identityへ入れる必要がある。
* Candidate provenanceまたはreviewed identityへ入れる必要がある。
* directory existence/type/content validationが必要。
* provided path count/size precheckが必要。
* input materialization、copy、ZIP、hashが必要。
* Candidate/Review schema変更が必要。
* public status/reason変更が必要。
* output validator緩和が必要。

戻し先: requirement/designの明示変更とfresh review。

### 18.4 S06 boundary violation

次の場合は停止する。

* fresh Redのためにcross-operation thread bindingが必要。
* Blue continuation storeが必要。
* session/thread locatorが必要。
* reusable Red binding preventionのためdomain/thread architecture変更が必要。

戻し先: S06。S05では実装しない。

### 18.5 S03/S04 regression

次の場合は停止する。

* optional pathsがsort/dedupされる。
* required pathとの重複が消える。
* relative pathがabsolute化される。
* external absolute pathが書き換わる。
* no-inspection/no-materialization spyが失敗する。
* generated prompt-pack/manifest/context fileが復活する。
* direct repeated `--file` orderが崩れる。
* infra production変更が必要。
* bytes/inline fallbackが必要。

戻し先: S03/S04 contract再確認と計画補正。compatibility bridgeを追加しない。

### 18.6 Lifecycle/output regression

次の場合は停止する。

* exact create preflight/postflightが緩む。
* Candidate source baselineまたはidentityが変わる。
* Candidate publication transactionが変わる。
* Review closed JSON parserが緩む。
* reviewed identity/digestが変わる。
* semantic revisionのReview/Candidate gateが弱くなる。
* mechanical laneがprompt/backendを呼ぶ。
* stale時にpublicationが発生する。
* public outputへprovided/private pathが漏れる。
* default fallback、wrapper、API、alternate backend、retryが必要になる。

戻し先: requirement/design。S05内で回避実装しない。

P2/P3相当の一般化、cleanup、追加refactor、将来拡張、別option、追加backend設計は本briefの対象外である。

---

## 19. Implementation handoff output

workerは親orchestratorへ次を返す。

```text
repository
branch
source HEAD
resulting HEAD
changed files
production diff summary
test diff summary
executed verification commands
exact pass/fail counts
legacy zero-match result
new-contract presence result
diff --check result
allowlist scope result
worktree/upstream parity
remaining risks
unverified claims
```

さらに次を明記する。

* canonical docsを変更していない。
* report/review/brief artifactを変更していない。
* domain/infra/parserを変更していない。
* S06以降を実装していない。
* Luna / Maxをverifiedと主張していない。
* implementation resultはfresh Red Team PASS、Human adoption、PR、merge、Issue closeを意味しない。

resulting HEADをcommit/pushした後、別のfresh Red Team threadがnamed branch exact resulting HEADをread-only、defect-only、P0/P1 scopeで確認する。worker自身はreview verdictを作成しない。

---

## 20. S05 implementation completion candidate

次が同一resulting HEADに結び付いた場合だけ、親orchestratorは`cl-s05-cli-cutover`のclosure候補として扱える。

* old option hard rejection。
* repeatable provided path forwarding。
* static→required→optional order。
* duplicate retention。
* lexical path preservation。
* `Path` object identity。
* no-inspection/no-materialization。
* create identity/stale/publication regression。
* fresh review request contract。
* semantic revision evidence contract。
* mechanical zero-backend contract。
* CLI help contract。
* direct transport integration。
* lifecycle integration。
* Ruff。
* Mypy。
* legacy zero-match。
* allowlist-only diff。
* pushed exact resulting HEAD。
* subsequent fresh code reviewによるP0/P1=0確認。

この条件は実装担当者によるself-claimを許可するものではない。closure、report統合、review evidence採用は親orchestratorが別ゲートで行う。

---

## 21. Not verified

本brief時点では次をverifiedと扱わない。

* S05 production implementation。
* `--provided-context-path`の実装。
* old `--context-manifest`の削除。
* manifest loader/helperの削除。
* TC-S05-001〜TC-S05-010の実行結果。
* CLI hard-cutover test result。
* transport/lifecycle integration result。
* Ruff/Mypy result。
* legacy zero-match result。
* resulting implementation HEAD。
* worker local worktree clean状態。
* implementation commit/push。
* fresh Red Team code review。
* S05 closure。
* S06 Blue continuity。
* S07 projection/docs consistency。
* S08 issue-level regression closure。
* S09以降のOracle `0.17.0` profile/recovery。
* GPT-5.6 Lunaの実測。
* Reasoning Effort Maxの実測。
* assurance promotion。
* Human adoption。
* PR、merge、Issue close。
