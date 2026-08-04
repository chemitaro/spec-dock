# BLOCKED — iss-00354 S05 実装前ブリーフ

## Orchestration / CLI cutover

## 1. 対象 identity と実装開始ゲート

| 項目                      | 確認結果                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                                                                      |
| Branch                  | `codex/iss-00354-chatgpt-context-contract`                                                 |
| Source HEAD             | `ee012140410f3a3d73b147d8e57515feb017803c`                                                 |
| Branch tip との比較         | `identical` / ahead `0` / behind `0`                                                       |
| Default branch fallback | 使用していない                                                                                    |
| 添付との照合                  | 添付 bundle の canonical 文書、対象 runtime、read-only runtime、指定テストは Source HEAD の GitHub blob と一致 |
| S03/S04 前提              | `report.md` 上で same-HEAD closure 済み。S05 へ進む記録あり                                            |

Repository、named branch、Source HEAD のいずれかが変わった場合は、このブリーフを流用せず停止する。default branch、添付だけの内容、ローカル記憶を代替 identity にしてはならない。

### 実装開始を止める既知の P1 相当不整合

Source HEAD の `tests/cli_runtime/test_chatgpt_cli.py` にある `test_leaf_help_freezes_required_and_conditional_options` は、`planning create --help` に `--context-manifest` が存在することを明示的に要求している。

S05 の canonical 契約は、同 option を help/parser から削除する hard cutover である。このテストを変更せず契約どおりに実装すると、既存 suite に確実な失敗が残る。一方、同ファイルは今回指定されたテスト変更許可リストに含まれていない。

したがって、**現在の変更境界のまま実装を開始してはならない**。owning workflow は実装前に、次の一件だけを計画・許可境界へ戻して補正し、新しい exact HEAD にブリーフを再結合すること。

* `tests/cli_runtime/test_chatgpt_cli.py` を S05 の test-only allowlist に追加し、旧 help expectation を新しい repeatable path option と旧 option 不在の expectation へ更新可能にする。

これは production scope、設計、CLI architecture の拡張ではなく、S05 が直接変更する既存 help contract の同期に必要な最小 test-boundary repair である。別の production ファイルを追加して回避してはならない。

## 2. モデル要求と証跡境界

実装担当として想定される設定は `GPT-5.6 Luna` / `Reasoning Effort Max` である。

このブラウザおよび GitHub connector 経路では、実際に解決されたモデル表示名と Reasoning Effort を測定できない。そのため、本ブリーフは Luna / Max を実測済み、verified、または実行成功済みとは主張しない。モデル設定は実装担当への要求値であり、product runtime の成功条件や S05 closure evidence の代替ではない。

## 3. S05 の目的

S05 は、S03/S04 で成立した path-only / direct transport を create、review、semantic revision の command/application 境界まで一貫させる orchestration / CLI cutover である。

実装目的は次に限定する。

1. create の旧 `--context-manifest` と manifest-based request field、loader を完全に削除する。
2. create、review、revise に共通する optional・repeatable・directory-oriented path option を導入する。
3. operator-supplied path を `Path` のまま request から prompt synthesis へ渡し、provider static attachment directory と required dynamic original paths の後ろへ追加する。
4. exact GitHub preflight/postflight、Candidate/Review identity、typed ZIP/closed JSON、publication transaction、mechanical revision を変更しない。
5. review は continuation locator や reusable binding を受け取らない fresh Red request のまま維持する。
6. semantic revision は prior Candidate、exact Review、revision request の original paths、および選択された P0/P1・保持前提を現在の minimal identity として維持する。

S06 の Blue continuity/private binding、S07 の projection/docs、S08 の全体 regression closure、S09 以降の Oracle `0.17.0` capability/profile/recovery は実装しない。

## 4. Source HEAD で確認した現状

### 4.1 CLI / request

`commands/issue_planning.py` の create は現在、次の旧契約を持つ。

* `PlanningCreateArgs.context_manifest_path`
* `--context-manifest`
* `_create_args()` による manifest path 化
* `_run_create()` から `PlanningCreateRequest.context_manifest_path` への受け渡し

review と revise には operator-supplied context path field がない。

`cli/chatgpt_parser.py` は command spec の `add_arguments` を leaf parser へ結び付けるだけである。したがって、S05 では同ファイルを変更せず、`commands/issue_planning.py` から旧 option を削除すれば help/parser surface からも削除される。

### 4.2 Application

`PlanningCreateRequest` は `context_manifest_path` を保持している。create は `_load_planning_context_manifest()` で外部 JSON を読み、`relevant_source_paths` と `operator_context` へ展開している。

この manifest loader は次の旧契約を持つ。

* 外部 file の bounded read
* JSON parse と duplicate-key rejection
* `relevant_source_paths` / `operator_context` schema
* count/byte limits
* merge/sort/dedup

これは directory-oriented opaque path transport ではないため、S05 で production path から削除する。

一方、次の現行挙動は既に target contract と整合しており、変更しない。

* `run_issue_planning_transport()` は `allow_default_branch_fallback=False` で exact branch/source preflight を行う。
* local/remote HEAD と upstream identity が一致しない場合は backend を開始しない。
* `PlanningContext` は canonical/relevant repository source identity を保持する。
* create は response 後に source evidence を再検証し、publication guard でも再確認する。
* review は Candidate を original path から読み、review 後にも同じ path から identity/bytes を再確認する。
* semantic revision は Candidate、Review、revision request の original paths を prompt attachment に渡す。
* mechanical revision は ChatGPT transport を呼ばない。
* publication は typed Candidate/Review output と既存 collision/stale/error mappingを使う。

### 4.3 Prompt synthesis / direct transport

`SynthesizedPlanningPrompt` は既に次の path-only contract である。

```text
role
prompt
attachment_paths: tuple[Path, ...]
output_expectation
```

現行 prompt synthesis は provider operation の opaque `attachments/` directory を先頭へ置き、各 original path を後続要素として保持する。

read-only の `infra/issue_planning_chatgpt.py` は `attachment_paths` を順番どおり repeated `--file` operand に変換し、`cwd=repo_root` で direct Oracle を呼ぶ。入力用 pack、copy、rename、ZIP、manifest は生成しない。

review invocation は role ごとに新しい session slug を生成し、review request/prompt に continuation locator を持たない。S05 ではこの既存境界を利用し、infra や新しい thread abstractionを変更しない。

## 5. S03/S04 から引き継ぐ不変条件

* provider static attachment directory を第一 operand とする。
* required dynamic evidence の original paths を第二群とする。
* optional operator-supplied directory paths を最後の群とする。
* path の順序、重複、相対・絶対という lexical representation、`Path` object identity を保持する。
* optional path を `resolve`、absolute 化、sort、deduplicate、stat、open、walk、glob、hash、copy、rename、archive、materialize しない。
* repository-relative source path は repository root を prefix せず lexical path のまま渡す。
* external absolute Candidate、Review、revision request、operator path は別場所へ複製しない。
* prompt body に private absolute path、attachment inventory、content hash を描画しない。
* generated `context-NNN.md`、input manifest、prompt pack、provenance packを復活させない。
* S03/S04 の既承認 allowlist、no-inspection tests、direct repeated `--file` contractを緩めない。

## 6. Public CLI / request 契約

### 6.1 Option 名

同一 repository で既に使用されている naming convention に合わせ、次を使用する。

```text
--provided-context-path PATH
```

* create、review planning、planning revise の三 command に追加する。
* `action="append"` の repeatable option とする。
  -省略時は空 tuple とする。
* apply には追加しない。
* help は「Oracle へ original top-level path として直接渡す optional opaque context directory path。repeatable」であることだけを示す。
* directory であることを runtime が filesystem inspection により検証してはならない。

### 6.2 Request field

三 request/args に次の field を追加する。

```text
provided_context_paths: tuple[Path, ...] = ()
```

次を禁止する。

* `context_manifest_path` compatibility property
* `--context-manifest` alias
* JSON-to-path translation
* old/new dual-write
* warning付き legacy acceptance
* single string への結合
* path sorting/deduplication
* existence/type/symlink check
* source-context fieldへの変換

旧 option を指定した場合は argparse の unknown-option error、exit code `2` で command/use-case invocation 前に拒否する。

## 7. ファイルごとの変更契約

## 7.1 `commands/issue_planning.py`

### 変更するもの

* `PlanningCreateArgs.context_manifest_path` を削除し、`provided_context_paths` へ置換する。
* `PlanningReviewArgs` と `PlanningReviseArgs` に同 field を追加する。
* create/review/revise の argument builder に `--provided-context-path` を追加する。
* `_create_args()`、`_review_args()`、`_revise_args()` で、入力順のまま次へ変換する。

```text
tuple(Path(value) for value in ns.provided_context_path or ())
```

* `_run_create()`、`_run_review()`、`_run_revise()` は生成した tuple を対応 request へ同一 object/order で渡す。

### 変更しないもの

* apply の args、parser、request。
* output format と renderer。
* mode validation。
* Candidate、review、apply の既存 conditional options。
* `cli/chatgpt_parser.py`。

## 7.2 `application/issue_planning.py`

### Request dataclass

* `PlanningCreateRequest.context_manifest_path` を削除する。
* create/review/revise request に `provided_context_paths: tuple[Path, ...] = ()` を追加する。
* `PlanningContext`、domain contract、source evidence へ同 field を追加しない。

### create

* `_load_planning_context_manifest()` 呼び出しと manifest-derived merge block を削除する。
* manifest 専用の次を削除する。

  * `_load_planning_context_manifest`
  * `_manifest_string_values`
  * `_merge_context_values`
  * manifest parse のためだけの `json` import
    -既存の injected `relevant_source_paths` / `operator_context` 引数は削除しない。これらは repository source identity と operation context の既存内部契約であり、operator attachment directoryとは別である。
* create 用 prompt synthesizer に `request.provided_context_paths` を明示的に渡す。
* optional paths は GitHub preflight `source_paths`、`PlanningContext.relevant_source_paths`、source manifest hash、Candidate source baseline、publication guardへ混入させない。

### review

* `request.provided_context_paths` を review prompt synthesis へ渡す。
* required dynamic path の既存順序を変更しない。

  * original Candidate ZIP
  * git-bound の canonical/relevant repository source paths、または archive review の source operands
  * optional provided context paths
* role は常に `reviewer` とする。
* continuation/session/thread locator を request や promptへ追加しない。
* `ReviewedPlanningIdentity`、identity SHA、Candidate reload、source postflight、publication guardを変更しない。

### semantic revision

* semantic laneだけで optional paths を prompt synthesisへ渡す。
* required dynamic pathsの先頭順を維持する。

  1. prior Candidate original path
  2. exact Review original path
  3. revision request original path
  4. canonical/relevant source paths
  5. optional provided context paths
* exact Review digest、Candidate identity、`revision.validate_against()` を通過する前に backendを呼ばない。
* revision body の scope は現在の最小表現を維持する。

  * `selected finding <id>: <p0|p1>`
  * `preserve assumption: <value>`
* finding本文、attachment path、private path、Review全文を bodyへ追加しない。

### mechanical revision

* `provided_context_paths` が指定されても transport/prompt synthesisへ渡さない。
* existing `apply_mechanical_revision()`、diff budget、output identity、publication behaviorを変更しない。
  -新しい rejection、fallback、ChatGPT invocationを追加しない。

### 推奨する最小 wiring

`run_issue_planning_transport()` の source preflight contractへ operator pathを追加せず、create/review/revise の step-local prompt synthesizer closureから `provided_context_paths` を prompt synthesis APIへ渡す。operator attachmentを generic GitHub source stateへ昇格させない。

この wiringで実装できず、`PlanningContext`、domain contract、infra invocation signatureの変更が必要になった場合は停止する。

## 7.3 `application/issue_planning_prompt.py`

次の二つの synthesis entry point に、default empty tuple の明示 parameter を追加する。

```text
provided_context_paths: tuple[Path, ...] = ()
```

対象:

* `synthesize_issue_planning_prompt()`
* `synthesize_planning_evidence_prompt()`

path assembly は次の exact order とする。

### create

```text
provider operation attachments directory
canonical/relevant source paths
provided context paths
```

### review / semantic revision

```text
provider operation attachments directory
required dynamic attachment_paths
provided context paths
```

`provided_context_paths` に対して、次を一切呼ばない。

```text
exists
is_file
is_dir
is_symlink
stat
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
copy
copytree
rename
replace
ZipFile
hash
```

`_render_minimal_body()`、identity renderer、output expectation、reviewed identity、revision scopeの構造は変更しない。path は prompt body に描画しない。

## 8. create / review / revise の end-to-end 契約

## 8.1 Create

### 入力

```text
static planning attachments dir
canonical/relevant repository source paths
zero or more provided context paths
```

### 維持する処理

1. existing Issue target と current front matter の検証。
2. exact GitHub preflight。
3. planner prompt synthesis。
4. direct path transport。
5. typed authoring ZIP validation。
6. exact source postflight。
7. Candidate material build。
8. publication guard。
9. Candidate identity と git-bound operation binding の出力。

provided context path は attachment transport のみに影響し、Candidate provenance/source identityには影響させない。

## 8.2 Review

### 入力

```text
static review attachments dir
original Candidate ZIP path
required exact source paths
zero or more provided context paths
```

### fresh Red

* request role は `reviewer`。
* prompt は fresh / read-only / defect-only を維持する。
* reusable Blue/Red binding、past Red locator、continuation optionを受け取らない。
* existing infra の per-invocation new sessionを利用する。
* cross-operation thread storeやBlue continuityはS06まで追加しない。

### Identity / output

* original Candidate pathを別名または別directoryへ複製しない。
* `ReviewedPlanningIdentity` と SHAを bodyへ保持する。
* closed `PlanningReviewResult` parserを変更しない。
* duplicate/unknown key、wrong identity、unsafe findingは従来どおり rejectする。
* Candidate reloadとsource postflightに失敗した場合は publicationしない。

## 8.3 Semantic revision

### 入力

```text
static revision attachments dir
prior Candidate original path
exact Review original path
revision request original path
required source paths
zero or more provided context paths
```

### Minimal body identity

* exact repository、branch、HEAD、Issue、parents。
* selected P0/P1 の ID と severity。
* preserve assumptions。
* authoring ZIP expectation。

### 維持する処理

* Candidate identityとReview reviewed identityの一致。
* exact Review SHA binding。
* `revision.validate_against()`。
* source preflight と stale判定。
* typed authoring ZIP validation。
* version increment。
* publication guard。
* Candidate identity/binding出力。

## 9. 変更してはいけない契約

* authoring ZIP の logical filename、internal root、canonical three documents、exactly-one onboarding。
* Candidate ZIP builder、validator、snapshot、publication path。
* closed Review JSON schema/parser。
* reviewed identity と identity SHA。
* Review verdict/finding parsing。
* create/review/revise の exact GitHub source gate。
* stale、rejected、blocked の既存 reason mapping。
* mechanical revision lane。
* PATH Oracle、managed Chrome、model argv、session artifact reader。
* direct repeated `--file` implementation。
* output staging。
* copy、rename、materialization、generated input ZIP。
* default branch fallback。
* inline/bytes fallback。
* retry loop。
* alternate backend、wrapper、API。
* directory tree scanner。
* `domain/issue_planning_contracts.py`。
* `infra/issue_planning_chatgpt.py`。
* `cli/chatgpt_parser.py`。
* S06 以降の thread continuity、projection、regression、Oracle `0.17.0` work。
* canonical requirement/design/plan/report の変更。実測 evidence の report 統合は親 orchestrator が別途行う。

## 10. 最小 test cases

### TC-S05-000 — allowlist blocker

対象: `tests/cli_runtime/test_chatgpt_cli.py`。
現状は create help に `--context-manifest` を要求するため、S05 hard cutover と矛盾する。

解除後は次を固定する。

* create/review/revise help に `--provided-context-path` がある。
* create help に `--context-manifest` がない。
* apply help に `--provided-context-path` がない。
  -旧 option の実行は exit `2`。
* help contract以外の command family は不変。

この test file の変更許可が得られるまで、後続 test-driven implementationを開始しない。

### TC-S05-001 — parser hard cutover と repeatable request

`tests/unit/commands/test_issue_planning.py` で create/review/revise を table-driven に検証する。

* `--provided-context-path first --provided-context-path second` が二つの `Path` として同じ順番で requestへ渡る。
  -同じ値を二回指定した場合も勝手にdeduplicateしない。
* option省略時は `()`。
* `--context-manifest` は parser errorでuse-case call `0`。
* args/request に `context_manifest_path` が残らない。
* apply request は不変。

### TC-S05-002 — prompt path order / original identity / no inspection

`tests/unit/application/test_issue_planning_prompt.py` で、存在しない path、repository-relative lexical path、repository外 absolute pathを指定する。

期待値:

```text
static dir
required paths
optional paths in supplied order
```

* optional `Path` object は tuple 内で同一 object。
* bodyに path stringがない。
* optional pathまたはその子に対する filesystem/tree/content API callは `0`。
* provider resource validationやoutput expectationの既存処理を誤って禁止しないよう、spyはoperator-supplied pathだけを保護する。

### TC-S05-003 — create success と exact stale gate

`tests/unit/application/test_issue_planning.py` で次を確認する。

* create request の optional paths が planner synthesisへ同じ順序で渡る。
* preflight source pathsには追加されない。
* `PlanningContext.relevant_source_paths` / `operator_context` は変わらない。
* Candidate source baseline/public outputに private pathが入らない。
  -成功時の `candidate_created` output shape は不変。
* response後の HEAD/source hash driftでは `planning_source_stale`、publisher call `0`。
  -旧 manifest loader testsは削除し、新契約の transport-only assertionsへ置換する。

### TC-S05-004 — review fresh request / original Candidate / identity rejection

`tests/unit/application/test_issue_planning.py` と prompt testで次を確認する。

* role は `reviewer`。
* prompt は fresh/read-only/defect-only。
* session locator、continuation locator、reusable binding inputがない。
* Candidate original `Path` が required dynamic pathの先頭。
* optional pathsは required pathsの後ろ。
* Candidate を copy/rename/materializeしない。
* wrong reviewed identity、wrong identity SHA、unknown/duplicate JSON keyは従来どおり `review_result_rejected`。
* review中にCandidate bytes/identityが変化した場合は `review_target_changed`、publication `0`。

### TC-S05-005 — semantic revision original path / minimal scope

`tests/unit/application/test_issue_planning.py` で次を確認する。

* Candidate、Review、revision request の三つは、呼び出し元と同じ `Path` object。
  -三つの順序は不変。
* required source pathsの後ろに optional pathsが並ぶ。
* bodyには選択済み P0/P1 ID/severityとpreserved assumptionsだけが追加される。
* selectedでない finding や full Review contentはbodyに入らない。
* Review digest mismatch、Candidate identity mismatch、未選択/無効 findingでは backend call `0`。
  -成功時の revised Candidate ZIP/version/binding contractは不変。

### TC-S05-006 — mechanical revision lane

non-empty `provided_context_paths` を持つ revise requestでも、laneがmechanicalなら次を確認する。

* prompt synthesizer call `0`。
* backend invocation `0`。
* provided pathsへのfilesystem access `0`。
* existing exact replacement/diff budget/output contractが不変。

### TC-S05-007 — integration direct transport

`tests/integration/test_issue_planning_chatgpt_transport.py` で少なくとも一つの create/review/semantic-revise pathを fake Oracleまで通す。

* provider static directory、required original paths、optional pathsが repeated `--file` に同じ順番で現れる。
* relative pathはrelativeのまま。
* external absolute pathは同じ absolute string。
* `--prompt` は一つ。
* input pack、manifest、context file、copy、rename、ZIP化がない。
* typed output処理は既存結果と同じ。

### TC-S05-008 — full-chain identity regression

`tests/integration/test_issue_planning_e2e.py` の既存 lifecycle fixtureを最小拡張する。

```text
create
fresh review
semantic revise
```

各経路で optional pathが original operandとして渡ることを確認し、次を維持する。

* create Candidate identity。
* reviewed identity。
* closed Review JSON。
* exact source stale protection。
* revised Candidate version。
* Candidate/Review original path。
* no default fallback。
* no materialization。

## 11. 実装順序

1. **停止ゲートを解消する。** `tests/cli_runtime/test_chatgpt_cli.py` の test-only allowlist補正、新しい exact branch HEAD、再結合済み briefを確認する。
2. Source HEAD から実装対象外の差分がないことを確認する。
3. command testsを先に Red にし、旧 option rejectionとnew repeatable optionを固定する。
4. command args/request dataclassを hard cutoverする。
5. prompt synthesis APIへ `provided_context_paths` を追加し、path order/no-inspection testをGreenにする。
6. create manifest loaderを削除し、transport-only wiringへ置換する。
7. review の required/original path order、fresh request、identity checksを維持したまま optional pathsを追加する。
8. semantic revisionへ optional pathsを追加し、mechanical lane regressionを固定する。
9. focused unit testsを実行する。
10. CLI runtime help testを実行する。
11. transport integration、full-chain e2eを実行する。
12. lint/type/diff/scope auditを行う。
13. 親 orchestratorへ changed files、test results、source/resulting HEAD、未検証事項を返す。worker自身は `report.md` を変更しない。

## 12. Verification commands

### 12.1 Focused unit tests

```bash
uv run pytest \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  -q
```

### 12.2 CLI help/parser contract

allowlist補正後に必須とする。

```bash
uv run pytest tests/cli_runtime/test_chatgpt_cli.py -q
```

### 12.3 Integration

```bash
uv run pytest \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  -q
```

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py \
  -q
```

### 12.4 Static checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

### 12.5 Legacy contract absence

次の production filesに対する検索が zero-matchであること。

```bash
rg -n -- \
  '--context-manifest|context_manifest_path|_load_planning_context_manifest|_manifest_string_values' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

`tests/` では旧 option拒否 assertionの文字列だけを許容する。

### 12.6 Diff / scope

```bash
git diff --check
git diff --name-only ee012140410f3a3d73b147d8e57515feb017803c...HEAD
```

diff は、再承認された S05 production/test allowlist以外を含んではならない。

`spec-dock validate`、provider/installed/dogfood projection、docs parity、全 repository regression はS07/S08のclosureであり、S05 production scopeを広げる理由にしない。

## 13. 停止条件と canonical 文書へ戻す条件

次のいずれかを検出した場合は実装を止める。

1. 現在の `tests/cli_runtime/test_chatgpt_cli.py` allowlist不整合が未解消。
2. named branch tipが Source HEADから変化し、再結合判断がない。
3. old `--context-manifest`をalias、hidden option、translationとして残す必要がある。
4. `--provided-context-path` の処理に directory stat、existence check、tree scan、copy、ZIP、hashが必要になる。
5. optional pathを GitHub source manifest、Candidate provenance、`PlanningContext`へ入れる必要がある。
6. `domain/issue_planning_contracts.py`、`infra/issue_planning_chatgpt.py`、`cli/chatgpt_parser.py` の変更が必要になる。
7. fresh Redのためにcross-operation thread binding、private handle store、continuation portが必要になる。これはS06へ戻す。
8. Candidate publication、ZIP inventory、closed Review JSON、reviewed identityを変更する必要がある。
9. mechanical revisionの入出力またはbackend call countが変わる。
10. S03/S04のpath-only/direct transport/no-inspection testが退行する。
11. default branch、alternate backend、inline fallback、retry、wrapper、APIが必要になる。
12. authorized files外のproduction変更が必要になる。

戻し先は次のとおりとする。

* CLI/test allowlistの不足: `plan.md` S05 execution cardへ戻す。
* operator pathがsource identityを変更する必要: `requirement.md` / `design.md`へ戻す。
* fresh Redにthread lifecycle実装が必要: S06計画へ戻す。
* output schema/validator変更が必要: requirement/designの別明示変更へ戻す。
* P2/P3相当の改善、一般化、refactorのみ: S05では採用せず記録もしない。

## 14. 実装後の Red Team read-only review scope

実装後は、実装担当と別の fresh Red Team threadで次だけを確認する。

* Repository: `chemitaro/spec-dock`
* Branch: `codex/iss-00354-chatgpt-context-contract`
* Review target: push済み exact resulting HEAD
* Default branch fallback: `0`
* Review mode: read-only / defect-only
* 判定対象: P0/P1のみ
* Canonical requirement/design/plan と S05 brief はread-only
* repository、Candidate、canonical docs、testsをレビュー中に変更しない

確認項目:

1. old option が help/parser/request/applicationから消えている。
2. new repeatable path optionがcreate/review/reviseだけに存在する。
3. path order、object identity、relative/absolute lexical identityが保持される。
4. optional pathのtree/content inspection、copy、rename、materializationがない。
5. create preflight/postflight、Candidate publicationが不変。
6. reviewがfresh reviewer requestで、Candidate original path、reviewed identity、closed JSONを維持する。
7. semantic revisionがCandidate/Review/request original paths、selected P0/P1、preserved assumptionsを維持する。
8. mechanical laneが不変。
9. S03/S04 closureを壊していない。
10. known CLI runtime help testを含む focused verificationが同一 resulting HEADで成功している。

Review PASSをHuman adoption、implementation completion、PR、merge、Issue closeとは扱わない。Red Teamが使用した実モデルまたはReasoning Effortを証拠から確認できない場合、Luna/Max verifiedとは記録しない。

## 15. Assumptions

* Public option名は、同一 repository の既存 repeatable path namingに合わせた `--provided-context-path` とする。
* option値は operator がdirectory-oriented top-level pathとして指定するが、SpecDockはdirectory性を検査しない。
* supplied orderとduplicatesはoperator input identityの一部として保持する。
* provided context pathsはattachment transport専用であり、GitHub source identity、Candidate provenance、operation contextではない。
* provider operation attachment directoryは常に第一 operandである。
* S03/S04 closureとpath-only/direct transportは Source HEAD 時点で有効である。
* S05中にS06のBlue binding/thread continuityを先行実装しない。

## 16. Open questions

### Blocking

* `tests/cli_runtime/test_chatgpt_cli.py` をS05のtest-only allowlistへ追加する plan-boundary correctionを、owning workflowが承認するか。

この一点が解消されるまで、実装は開始不可である。旧 testを無視する、非実行にする、S08まで既知 failureを持ち越す、helpに旧文字列だけを残す、という回避は採用しない。

### Non-blocking

* なし。option naming、path order、identity/output boundaryは上記契約で固定する。

## 17. Not verified

* S05 production codeはまだ変更していない。
* 記載した tests、lint、mypy、integration、full regressionはまだ実行していない。
* resulting HEAD、clean worktree、push、CI statusは存在しない。
* GPT-5.6 Luna / Reasoning Effort Maxの実測成功は確認していない。
* S06 Blue continuity、S07 projection、S08 regression closure、S09以降の Oracle `0.17.0` capabilityは検証していない。
* PR、merge、Issue close、assurance promotion、Human adoptionは行っていない。
