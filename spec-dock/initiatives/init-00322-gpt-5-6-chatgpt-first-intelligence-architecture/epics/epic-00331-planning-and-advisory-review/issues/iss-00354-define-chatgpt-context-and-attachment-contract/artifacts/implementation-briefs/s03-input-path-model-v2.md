# iss-00354 S03/S04 Atomic Cutover 実装ブリーフ

> **対象実装者:** Codex / GPT-5.6 Luna / Reasoning Effort Max 想定
> **実行単位:** S03 と S04 を一つの deployable change-set、一つの rollback unit、一つの resulting HEAD として扱う
> **成果物境界:** application の path-only input contract と infra の direct repeated `--file` transport を同時に切り替える
> **モデル証跡:** GPT-5.6 Luna / Reasoning Effort Max による実測成功証跡は未確認。モデル設定は実装作業上の想定であり、製品 runtime の受け入れ条件ではない

## 1. 結論

現行の bytes/materialization producer と generated-pack consumer を、**互換層なしで同時に削除**する。

* S03 は、`SynthesizedPlanningPrompt` から attachment bytes、classification、per-file SHA、generated identity attachment を除き、static operation attachment directory と dynamic original paths だけを保持する。
* S04 は、`_write_transport_pack` と一つの generated prompt-pack `--file` operand を廃止し、S03 が構成した各 original path を、順序どおりの複数の `--file` operand として Oracle に渡す。
* Review の `reviewed_identity` と `reviewed_identity_sha256` は attachment file ではなく minimal body の deterministic field とする。
* S03/S04 の片側だけを Green、commit candidate、closure、rollback 対象にしてはならない。
* S05 以降は、この atomic change-set の同一 resulting HEAD に必要証跡が揃うまで開始しない。

この境界は、minimal body、opaque attachment directory、dynamic original paths、no generated input pack を定める要件・設計と、S03/S04 atomic amendment の実行境界に従う。

## 2. 固定 identity

| 項目                  | 固定値・扱い                                                  |
| ------------------- | ------------------------------------------------------- |
| Repository          | `chemitaro/spec-dock`                                   |
| Current branch      | `codex/iss-00354-chatgpt-context-contract`              |
| Source HEAD         | `8b44eb6da5d8be4f2178ce3be09d25e968f14747`              |
| GitHub connector 検証 | named branch と指定 SHA は `identical`、ahead `0`、behind `0` |
| Default branch      | 未参照。fallback 禁止                                         |
| Resulting HEAD      | 実装後に一つだけ記録する。S03/S04 の両責務を同じ SHA に bind する              |
| Rollback unit       | resulting HEAD の atomic revert                          |
| 実装ブリーフ前提モデル         | GPT-5.6 Luna / Reasoning Effort Max                     |
| Luna / Max 実測証跡     | **未確認**                                                 |

指定 SHA は current branch の exact commit として取得できている。

実装開始時に named branch の HEAD が一文字でも変わっていた場合、このブリーフを別 HEAD に流用せず停止する。default branch、添付ファイル、ローカル記憶を source identity の代替にしない。

## 3. 変更境界

### 3.1 Delegated implementation write allowlist

#### Provider runtime

1. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
2. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
3. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`

#### Provider resource

4. `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md`

変更できるのは、generated identity attachments を参照する現在の identity wording を、minimal body の `reviewed_identity` と `reviewed_identity_sha256` を参照する wording に置換する部分だけである。

#### Tests

5. `tests/unit/application/test_issue_planning_prompt.py`
6. `tests/unit/application/test_issue_planning.py`
7. `tests/unit/infra/test_issue_planning_chatgpt.py`
8. `tests/integration/test_issue_planning_chatgpt_transport.py`
9. `tests/integration/test_issue_planning_e2e.py`

### 3.2 Provider sync でのみ再生成する projection

次は provider source の生成 projection としてのみ更新する。手編集は禁止する。

* `spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
* `spec-dock/scripts/spec_dock_runtime/application/issue_planning.py`
* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
* `.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md`

### 3.3 Read/run-only

次は変更しない。

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
* `tests/unit/domain/test_issue_planning_contracts.py`
* CLI / commands
* Oracle compatibility profile、version、help capability、session recovery
* `issue_planning_oracle_artifact.py`
* ZIP / Review JSON output validators
* Candidate / Review / Human / apply contract
* 上記 Review identity contract 以外の operation resource wording または inventory
* requirement、design、plan
* personal wrapper、Oracle 本体

実装証跡は、親 orchestrator が既存の次の report に記録する。これは delegated production/test write allowlist の拡張として扱わない。

`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md`

## 4. 現状のコード事実

### 4.1 Prompt synthesis は path と bytes の二重契約になっている

現在の `PlanningPromptAttachment` は `name`、`classification`、`source_label`、`content: bytes` を保持し、content SHA-256 も計算する。`SynthesizedPlanningPrompt` は、text attachments、exact byte attachments、`attachment_paths` を同時に保持している。

通常 Planning synthesis は canonical/relevant source を descriptor-relative に open し、bytes を UTF-8 decode・sensitive scan して `attachments` に格納する。一方で `attachment_paths` には static operation attachment directory しか入っていない。

### 4.2 Application caller が transport materialization を所有している

`run_issue_planning_transport` は、synthesized attachment bytes の SHA-256 を preflight source manifest と再照合し、exact attachment bytes の sensitive scan も行う。これは source preflight state と attachment transport state がまだ分離されていないことを示す。

Review caller は現在、次を `PlanningPromptAttachment.content` として構築している。

* archive Review の Candidate ZIP bytes
* git-bound Review の canonical document bytes
* Candidate 内 onboarding companion bytes
* `reviewed-identity.json`
* `reviewed-identity-sha256.txt`
* canonical/relevant source の supplemental text

その後、returned closed JSON の typed identity equality は application 側で検証されている。

Semantic Revision caller は、prior Candidate ZIP、Review JSON、Candidate 内の三 canonical documents を byte attachments として作り、current source text と合わせて generated pack に渡している。

### 4.3 Infra は一つの generated prompt-pack を Oracle に渡している

現在の infra は temporary directory に `prompt-pack` を作り、`_write_transport_pack` で次を生成している。

* `.specdock-authoring-pack`
* `context-NNN.md`
* exact attachment copies
* `manifest.json`
* `provenance.json`
* `source-manifest.json`
* `stale-if.json`

Oracle argv には一つの `--prompt` と、一つの `--file <prompt-pack>` が入る。出力用 private staging、Oracle session artifact reader、typed ZIP / JSON snapshot は同じ infra 内にあるが、これらは S03/S04 で削除しない。

### 4.4 Review resource と E2E fixture も generated identity files に依存している

Review instructions は `reviewed-identity.json` と `reviewed-identity-sha256.txt` を参照している。

E2E fake Oracle は最初の `--file` operand を directory pack とみなし、`rglob` で pack inventory を作り、Review 時には pack 内の二つの identity files を読む。submission assertion も一つの `--file` と `prompt-pack` を前提にしている。

### 4.5 Exact HEAD 時点で infra projection に既存 drift がある

同じ source HEAD で、provider infra と checked-in dogfood projection の blob SHA は一致していない。

| Path                                                               | Blob SHA                                   |
| ------------------------------------------------------------------ | ------------------------------------------ |
| Provider `src/.../infra/issue_planning_chatgpt.py`                 | `d0266d283160def00c42063a4c0d12dab3f65ff5` |
| Projection `spec-dock/scripts/.../infra/issue_planning_chatgpt.py` | `2c962d6458c7969bc988f7104c706cdfaabe5ca5` |

したがって provider sync は、S03/S04 の差分だけでなく、この既存 projection drift も provider source に収束させる可能性がある。生成差分を確認し、provider source の byte projection 以外の変更が含まれた場合は停止する。

## 5. Target contract

### 5.1 `SynthesizedPlanningPrompt` の責務

target contract は次の情報だけを保持する。

| Field                | 責務                                                            |
| -------------------- | ------------------------------------------------------------- |
| `role`               | planner / reviewer / semantic revision                        |
| `prompt`             | deterministic minimal body                                    |
| `attachment_paths`   | static directory と dynamic original paths の immutable tuple   |
| `output_expectation` | existing typed authoring ZIP / closed Review JSON expectation |

削除対象:

* `PlanningPromptAttachment`
* `attachments`
* `exact_attachments`
* `content`
* attachment classification
* attachment source label
* attachment SHA
* generated attachment filename
* input manifest/provenance fields
* compatibility property または旧 field alias

`attachment_paths` は path を指すだけであり、application/infra は attachment directory または dynamic path の内容を理解しない。

### 5.2 Path order

infra は application が渡した順序を変更、sort、resolve、deduplicate しない。各 operation の application order は次とする。

| Operation           | `attachment_paths` の順序                                                                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Planning            | static planning attachment directory → canonical source paths → relevant source paths                                                                                |
| Archive Review      | static review attachment directory → original Candidate ZIP path → canonical/relevant source paths                                                                   |
| Git-bound Review    | static review attachment directory → original Candidate ZIP path → exact canonical target paths → relevant source paths                                              |
| Semantic Revision   | static revision attachment directory → original prior Candidate ZIP path → exact Review JSON path → original revision request path → canonical/relevant source paths |
| Mechanical Revision | Oracle transport を使用しない既存 lane のまま                                                                                                                                   |

重複する canonical path は application が operation contract 上で一度だけ構成する。infra 側で filesystem identity を調べて重複除去してはならない。

Repository-relative source path は `cwd=repo_root` の Oracle operand として lexical representation を保持する。外部 Candidate、Review、revision request は request で受けた original `Path` を、copy、rename、temporary file、archive を介さず保持する。

### 5.3 Static attachment directory

* operation resource resolver が top-level managed resource の存在を確認する既存 S02 contract は保持する。
* `attachments/` の子 entry は列挙しない。
* nested、hidden、symlink、FIFO、unsupported entry を application が walk、glob、stat、open、hash、classify、filter しない。
* entry 単位の exclusion、conversion、automatic ZIP、fallback を作らない。
* static directory の内容に起因する Oracle failure は通常の transport failure とする。

### 5.4 Review identity

Review operation の minimal body に、次を deterministic に一度だけ描画する。

1. `ReviewedPlanningIdentity.to_dict()` の canonical JSON
2. `identity.sha256`

body 上の値は、たとえば専用の `Reviewed identity` と `Reviewed identity SHA-256` セクションとして、他の operation context と混同しない closed field にする。

Review instructions は次の意味へ限定して更新する。

* minimal body の exact `reviewed_identity` を output の `reviewed_identity` として使う。
* minimal body の exact digest を `reviewed_identity_sha256` として使う。
* attachment file の SHA や改行 framing に関する現在の説明を削除する。

保持するもの:

* `PlanningReviewResult.from_json_bytes` の closed parser
* unknown / duplicate key rejection
* typed identity equality
* verdict/finding consistency
* sensitive finding rejection
* Candidate / source postflight
* Human authority boundary

生成しないもの:

* `reviewed-identity.json`
* `reviewed-identity-sha256.txt`
* 同等の別名 identity attachment
* identity-only directory
* body から file への再 materialization

### 5.5 Source preflight と transport の分離

既存 exact GitHub preflight/postflight は保持する。一方、synthesized attachment bytes を source manifest と再 hash する transport check は廃止する。

境界は次のとおり。

* **Source preflight:** canonical/relevant source の存在、source manifest、branch、HEAD、freshness を既存 GitHub sync preflight が検証する。
* **Application lifecycle validation:** Candidate ZIP、Review JSON、revision request を既存 typed parser が必要な範囲で読む。
* **Attachment transport:** preflightまたはtyped validationで使用した bytes を attachment payload として再構成せず、original path だけを渡す。
* **Source postflight:** Oracle invocation 後の source/candidate drift は既存 postflight/publication guard で検出する。
* **Output validation:** Oracle session artifact、authoring ZIP、Review JSON の既存 strict validationを保持する。

したがって「no read / no hash」は input transport materialization に対する禁止であり、existing exact-source preflight、typed Candidate validation、output artifact validationを緩める理由にはしない。

### 5.6 Direct Oracle argv

Oracle invocation は既存の固定 prefix と一つの exact prompt を保持し、その後に各 path を独立した operand として追加する。

期待形:

* `--prompt` は exactly one
* `--file` count は `len(attachment_paths)` と一致
* 各 `--file` の次の値は対応する path の lexical string
* path order は `attachment_paths` と完全一致
* input pack path は存在しない
* input temporary directory、context file、manifest、identity file は作成しない

private `TemporaryDirectory` を残す場合、その用途は output staging のみに限定する。

## 6. 保持する不変条件

| 境界                | 保持条件                                                                                |
| ----------------- | ----------------------------------------------------------------------------------- |
| GitHub            | named current branch、exact local/remote HEAD、default fallback なし                    |
| Oracle executable | `PATH` resolution、executable identity recheck                                       |
| Browser           | managed Chrome loopback preflight                                                   |
| Process           | `shell=False`、stdin disabled、sanitized child environment                            |
| Prompt            | exactly one `--prompt`、text normalizationなし                                         |
| Model             | current explicit `Pro` / `select` contractを変更しない                                    |
| Session           | slug、session root collision guardを保持                                                |
| Recovery          | current 0.16.1 stage-blind recoveryを変更しない。S09/S10責務へ踏み込まない                          |
| Artifact reader   | version、session metadata、path、size、SHA、ZIP/JSON validationを変更しない                    |
| Output            | authoring ZIP / Review JSON typed result、private staging、publication transactionを保持 |
| Lifecycle         | Candidate / Review / Human / apply authorityを維持                                     |
| Privacy           | raw prompt、private path、session handle、transcriptをpublic result/reportへ出さない         |
| CLI               | parser、options、public reason、serializationを変更しない                                    |
| Domain            | `PlanningContext`、Candidate/Review identity、closed result contractを変更しない            |
| Backend           | personal wrapper、API、alternate backendを追加しない                                        |
| Retry             | inline fallback、attachment drop、dual executionを追加しない                                |

## 7. Red → Green → Refactor

### 7.1 Baseline guard

変更前に次を確認し、結果を source HEAD に bind する。

1. current branch が `8b44eb6da5d8be4f2178ce3be09d25e968f14747` のままである。
2. task scope 外の worktree change がない。
3. focused five-file suite と domain contract test の baseline resultを記録する。
4. provider / projection 四組の SHA または `cmp` resultを記録する。
5. 既存 infra projection driftを pre-existing evidence として区別する。

baseline failure、HEAD drift、scope外変更を検出した場合、Red test追加へ進まない。

### 7.2 Red

#### `tests/unit/application/test_issue_planning_prompt.py`

先に次を固定する。

* synthesized contract が bytes、classification、SHA、exact attachmentを持たない。
* static attachment directory が tuple の先頭にある。
* canonical/relevant paths の lexical orderが保持される。
* nested/hidden/symlink/FIFO を含む attachment directoryについて、child traversalが0。
* dynamic path に対する `read_bytes`、`resolve`、`stat`、`rglob`、`iterdir` が0。
* managed `prompt.md` の既存 read と top-level resource completeness checkは許容する。
* minimal body、output expectation、unknown operation rejectionは回帰させない。

#### `tests/unit/application/test_issue_planning.py`

Planning / Review / Semantic Revision の caller matrixを固定する。

* callerごとの exact path order。
* requestで渡した Candidate、Review、revision requestの lexical path/object identity。
* Candidate/Review/revision request validation bytes が synthesized inputへ再格納されない。
* Review bodyに exact typed identity と digest が一度だけ存在する。
* generated identity file名が存在しない。
* archive/git-bound Review の closed JSON identity equalityが維持される。
* source preflight state と attachment path state が別 assertionになる。
* source/candidate postflight と publication guardが維持される。
* structured source contentを transport前にscan/materializeする旧 testは、no-content-inspection contractへ置換する。
* mechanical revision laneは非変更。

#### `tests/unit/infra/test_issue_planning_chatgpt.py`

* `--file` の個数、順序、値が `attachment_paths` とexactに一致する。
* `--prompt` は一つ。
* generated pack、context file、manifest、identity fileが作られない。
* input-side `mkdir`、write、copy、ZIP、hash、tree traversalが0。
* private output stagingは残る。
* executable、environment、managed Chrome、typed output、repository-access failure、recovery testsは回帰させない。
* `_write_transport_pack` 専用 testをdirect path argv testへ置換する。
* current recovery call countまたはargvをS03/S04理由で変更しない。

#### `tests/integration/test_issue_planning_chatgpt_transport.py`

* Planning → Candidate、Review → closed JSON、Semantic Revision → revised Candidateの既存 lifecycleを維持する。
* fake transportは `exact_attachments` から identity bytesを取得せず、minimal bodyから exact identity/digestを読む。
* Candidate/Review/revision request original pathが transport requestまで保持される。
* source evidence、Candidate payload binding、fresh Review identityの既存 assertionを維持する。

#### `tests/integration/test_issue_planning_e2e.py`

* fake Oracleは全 `--file` operandsを収集し、`attachment_paths` として記録する。
* 最初の `--file` を directory pack とみなさない。
* attachment pathを `rglob` しない。
* Review identity/digestは minimal bodyから取得する。
* `pack_files`、prompt-pack、generated identity filesへの依存を削除する。
* archive chain、git-bound chain、failed Review → semantic revision → fresh Review chainを維持する。
* public outputにprivate path/sessionが出ない既存 assertionを維持する。

Red は責務別に作成してよいが、片側だけの Green または commit candidateを作らない。

### 7.3 Green

実装順序は次の dependency orderとする。

1. `issue_planning_prompt.py` を path-only contractへ変更する。
2. `issue_planning.py` の Planning/Review/Revision callerを original pathsへ移す。
3. Review identity/digestを minimal bodyへ描画する。
4. Review resourceの identity wordingだけを更新する。
5. `issue_planning_chatgpt.py` を repeated direct `--file` assemblyへ変更し、generated pack writerを除去する。
6. five test filesのfake/backend fixturesを新契約へ合わせる。
7. provider syncで checked-in projectionsを再生成する。
8. focused verificationを同一 worktree / resulting HEAD candidateで実行する。

互換 field、temporary pack、一時的な dual-writeを途中段階にも置かない。producerとconsumerは同じ working change-set内で切り替える。

### 7.4 Refactor

Green後、次の legacy-only要素を参照がなくなった範囲で削除する。

* `PlanningPromptAttachment`
* attachment byte limits
* source-file descriptor materialization helpers
* attachment content SHA logic
* `_attachments_match_source_manifest`
* `_exact_attachments_have_sensitive_content`
* `_read_review_supplemental_attachments`
* generated identity canonical-byte helper
* `_write_transport_pack`
* pack専用 JSON writer
* pack専用 imports
* test helperの `pack_files` / one-file assumptions

残すもの:

* bounded external input readers
* Candidate loader
* Review / revision typed parser
* exact source preflight/postflight
* output staging
* Oracle artifact reader
* recovery helpers
* source/output privacy checks

Refactorで generic backend abstraction、path wrapper class、attachment registryを新設しない。

## 8. 各ファイルの責務

| File                                       | 実装責務                                                                                          | 入れてはならないもの                                                 |
| ------------------------------------------ | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `application/issue_planning_prompt.py`     | path-only synthesized contract、static-first path assembly、minimal body Review identity fields | file content read、attachment SHA、compatibility property    |
| `application/issue_planning.py`            | role別 dynamic original paths、identity body binding、source/transport state分離                   | bytes-to-path bridge、generated identity files、domain/CLI変更 |
| `infra/issue_planning_chatgpt.py`          | repeated direct `--file` argv、output-only staging                                             | prompt-pack、copy、ZIP、hash、inline/retry/profile変更           |
| Review `instructions.md`                   | minimal body identity/digest参照                                                                | attachment filename、他のreview wording変更                     |
| `test_issue_planning_prompt.py`            | path-only contract、opaque directory、no-inspection spies                                       | 旧bytes contractの維持                                         |
| `test_issue_planning.py`                   | caller matrix、identity body、pre/postflight regressions                                        | domain/CLI contractの代替 test                                |
| `test_issue_planning_chatgpt.py`           | exact argv、no-pack spies、transport regression                                                 | recovery semantics変更                                       |
| `test_issue_planning_chatgpt_transport.py` | application-to-transport path binding、closed identity                                         | generated identity attachment fixture                      |
| `test_issue_planning_e2e.py`               | repeated operandsを扱うfake Oracle、full lifecycle                                                | pack enumeration、identity file read                        |
| Generated projections                      | provider bytesの再生成結果                                                                          | 手編集、projection固有ロジック                                       |

## 9. 必須検証

すべて同じ resulting HEAD candidate に対して実行する。

### 9.1 Focused five-file suite

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py -q
```

### 9.2 Domain contract read-only regression

```bash
uv run pytest tests/unit/domain/test_issue_planning_contracts.py -q
```

この test fileは実行するだけで変更しない。exact HEAD に存在する read-only contract testである。

### 9.3 Legacy symbol search

```bash
rg -n "_write_transport_pack|reviewed-identity\\.(json|sha256)|exact_attachments|SynthesizedPlanningPrompt\\.attachments" \
  src tests .agents spec-dock
```

期待結果は該当0件。`rg` の zero-match exit code `1` は検索結果0の証拠として記録し、test failureと混同しない。

加えて five-file tests で、検索式が直接捕捉しない `reviewed-identity-sha256.txt`、`prompt-pack`、`context-NNN.md` の非存在を明示 assertionする。

### 9.4 Provider sync

provider source変更後、current branchで検証できる repository-owned provider projection mechanismを実行する。

禁止:

* projectionの手編集
* `cp` / `rsync` を独自の代替 provider sync とすること
* `spec-dock update` をlocal provider syncの代替にすること
* remote/default branchのassetで上書きすること

`spec-dock update` は固定 upstream packageからmanaged filesを更新する経路であり、current working provider sourceのprojection commandであることは確認できない。

current branch内で exact provider sync invocationを特定できなければ、推測コマンドを実行せず停止する。実行した exact command、exit code、生成対象をreportへ記録する。

### 9.5 Projection byte parity

provider sync後、少なくとも変更対象四組をbyte comparisonする。

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py

cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md \
  .agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md
```

四組すべて exit `0` を要求する。SHA-256もreportに記録する場合、path自体ではなくrepository-relative pathとdigestだけを記録する。

### 9.6 Repository validation

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

### 9.7 Scope audit

```bash
git diff --name-only
git status --short
```

差分は次だけに限定する。

* provider runtime 3 files
* provider Review resource 1 file
* tests 5 files
* provider syncで再生成された対応 projection
* 親 orchestratorによるevidence-only report update

domain、CLI、artifact reader、profile/recovery、別resource、canonical docsが出た場合は停止する。

## 10. Report evidence

親 orchestratorは、raw prompt、private absolute path、session handle、transcriptを含めず、次を既存 report に記録する。

| Evidence               | 記録内容                                                                  |
| ---------------------- | --------------------------------------------------------------------- |
| Source identity        | repository、branch、source HEAD `8b44…`、default fallbackなし              |
| Result identity        | S03/S04共通の resulting HEAD                                             |
| Atomic binding         | `cl-s03-path-input` と `cl-s04-direct-transport` が同一 resulting HEADを参照 |
| Changed files          | provider、tests、generated projectionsのrepository-relative一覧            |
| Contract delta         | bytes/exact attachment削除、path-only tuple、repeated `--file`            |
| Path matrix            | roleごとのpath categoryとoperand count。private full pathは記録しない            |
| No-inspection evidence | tree/content/copy/archive/hash spy call count `0`                     |
| Prompt evidence        | prompt count `1`、file operand count、order assertion                   |
| Identity evidence      | body identity/digest、generated identity files `0`、closed parser維持     |
| Focused tests          | exact command、test count、exit code                                    |
| Domain regression      | read-only test command、exit code                                      |
| Legacy search          | exact command、zero-match result                                       |
| Provider sync          | exact command、exit code、生成対象                                          |
| Projection parity      | 四組のbyte parityとdigest                                                 |
| Repository gates       | validate、diff check、scope audit                                       |
| Model evidence         | GPT-5.6 Luna / Reasoning Effort Max は実測未確認。確認できた場合だけ証跡sourceと時点を追記    |
| Remaining gaps         | 未実行browser smoke、未検証Oracle behavior等を推測で埋めない                          |

## 11. 停止条件

次のいずれかで作業を停止し、allowlistを拡張せず計画補正へ戻す。

1. named branch HEAD が固定 source HEAD と一致しない。
2. task scope外の既存 worktree changeを隔離できない。
3. domain contract、CLI、Oracle profile/recovery、artifact readerの変更が必要になる。
4. path-only producerとdirect consumerを同時に成立させられない。
5. compatibility property、dual-write、temporary pack、path-to-bytes reconstructionが必要になる。
6. Candidate、Review、revision requestをcopy/rename/archiveしなければtransportできない。
7. static attachment directoryのentry scanまたはper-entry exclusionが必要になる。
8. direct repeated `--file` capabilityが成立せず、inline、attachment drop、alternate backendを追加する必要が生じる。
9. Review identityをbodyへ移すためにclosed parserまたはtyped identity equalityを緩める必要がある。
10. source preflight/postflightまたはoutput validatorを弱める必要がある。
11. generated input packまたはlegacy identity symbolが検索に残る。
12. focused five-file suite、domain contract test、validate、diff checkのいずれかが成功しない。
13. provider syncの正規機構をcurrent branchから確認できない。
14. generated projectionがprovider bytesと一致しない。
15. provider syncが対応 projection以外のファイルを変更する。
16. S03/S04を一つの resulting HEADとrollback unitにbindできない。
17. personal wrapper、API、default branch、別Oracle executableを必要とする。

## 12. 仮定・未確認点

* GPT-5.6 Luna / Reasoning Effort Max の実測証跡は未確認である。GitHub connectorが確認したのはrepository、branch、commit、file blobであり、Reasoning Effort evidenceではない。
* このブリーフ作成中にpytest、provider sync、validate、browser Oracle invocationは実行していない。
* resulting HEAD はまだ存在せず、source HEAD からの変更内容も未実装である。
* current branchで使うべき exact provider sync invocationは、今回inspectした資料だけでは確定していない。実装時にcurrent branch内のrepository-owned mechanismを確認する必要がある。
* direct Oracle のruntime behaviorは、このブリーフでは再実測していない。S03/S04ではprofile、recovery、browser behaviorを新たに断定しない。
* provider infraとdogfood projectionの既存blob driftは確認済みだが、その発生理由は未確認である。provider sync後のbyte parityだけを受け入れ根拠とする。
