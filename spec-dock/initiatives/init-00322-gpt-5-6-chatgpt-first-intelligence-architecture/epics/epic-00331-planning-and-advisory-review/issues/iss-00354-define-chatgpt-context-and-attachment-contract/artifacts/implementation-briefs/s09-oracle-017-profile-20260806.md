# iss-00354 S09 実装ブリーフ — Oracle 0.17.0 exact compatibility profile

## 1. Identity and repository evidence

### 1.1 実装基準 identity

| 項目                      | 確認値                                                          |
| ----------------------- | ------------------------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                                        |
| Named branch            | `codex/iss-00354-chatgpt-context-contract`                   |
| Exact source HEAD       | `061829c33fea751f430948da954aae6dcebda2b0`                   |
| Branch comparison       | exact HEAD と named branch は `identical`、ahead `0`、behind `0` |
| Default branch fallback | 使用していない。`main` の内容を代替入力として開いていない                             |
| 作業種別                    | S09 実装準備。read-only advisory brief                            |
| 実装・レビュー状態               | S09 は未実装・未検証。S08 までの履歴とは分離する                                 |

GitHub connector で exact commit を解決し、named branch tip と一致することを確認した。 文書中に記録された過去の Candidate HEAD、verification HEAD、reviewed HEAD は履歴証跡であり、S09 worker の入力基準は上記 `061829...` である。

### 1.2 読み込んだ添付と exact-HEAD blob

`ISSUE_DIR`:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/
```

| 添付                                       | GitHub exact path                                                                                  | Blob SHA                                   |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `requirement.md`                         | `${ISSUE_DIR}/requirement.md`                                                                      | `76ebf016b12abb06f2b5daa544ea7a1421c7471e` |
| `design.md`                              | `${ISSUE_DIR}/design.md`                                                                           | `118e46f905b86883aac9df0f34ebca9e7be2fe91` |
| `plan.md`                                | `${ISSUE_DIR}/plan.md`                                                                             | `c553db3d222f5c346c1d15c21f0242cebdee0de4` |
| `report.md`                              | `${ISSUE_DIR}/report.md`                                                                           | `e5233795c6e5f3aa127d55df190d494e6e427b98` |
| `issue_planning_chatgpt.py`              | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`         | `4a9ce078a7f255e431de742ff47c7c8f0cc03350` |
| `issue_planning_oracle_artifact.py`      | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py` | `ea7184e9cacee6b9ae9a16d177763cf4b16ee531` |
| `test_issue_planning_chatgpt.py`         | `tests/unit/infra/test_issue_planning_chatgpt.py`                                                  | `7934037ec33ad59aa7710d045dac6fe25abeb83e` |
| `test_issue_planning_oracle_artifact.py` | `tests/unit/infra/test_issue_planning_oracle_artifact.py`                                          | `67658a97508d64098da8e1053b9ceceef36036e4` |

添付コピーと GitHub exact-HEAD blob の内容を照合済みである。S09 の計画境界は、現行 stage-blind recovery を先に固定し、0.16.1 の旧 command を profile へ抽出したうえで、実測済み 0.17.0 profile だけを追加することである。

---

## 2. S09 objective and non-goals

### 2.1 Objective

S09 の最小目的は次の四点である。

1. `oracle --version` の正規化済み完全一致値から、private な exact-version compatibility profile を選択する。
2. 現行 Oracle `0.16.1` の browser argv、session recovery argv、artifact reader behavior を一切置換せず profile 所有へ移す。
3. direct PATH Oracle `0.17.0` の sanitized characterization receipt に根拠がある場合だけ、capability、browser policy、stage decoder、artifact reader、harvest builder、capture builderを一つの profile として登録する。
4. generic adapter から version-specific recovery command assembly を除去し、選択済み profile の builder 以外から same-session commandを生成できないようにする。

### 2.2 Non-goals

S09 では次を実装しない。

* S10 の `promptSubmitted` ベースの回復判断、failure taxonomy、retry budget、public status/reason mapping。
* S10 の model retry、direct-to-inline retry、successful submission count制御。
* S11 の live browser smoke、representative prompt verification、observed model mappingの正式採用。
* S12 の response/download state machine、capture invocation policy、ZIP download recovery。
* S12 の artifact validation緩和、pending/download-failed mapping、publication policy変更。
* application、domain、commands、CLI、thread lifecycle、Blue/Red bindingの変更。
* public option、generic backend abstraction、generic safety layer、新しい外部依存の追加。
* personal `chatgpt-use` wrapper、Oracle wrapper/API、alternate backend、alternate model、default branchへの fallback。
* `SUPPORTED_ORACLE_VERSION = "0.17.0"` という単純定数置換。
* `>=0.17.0`、`0.17.x`、unknown patchの受理。
* `GPT-5.6 Sol`、`GPT-5.6 Luna`、Reasoning Effort Maxを product runtime success、logical-model mapping、profile constantとして扱うこと。
* 実装完了、review PASS、S09 closure、PR、merge、Issue closeの自己宣言。

---

## 3. Current-code findings with exact file/symbol locations

### 3.1 `issue_planning_chatgpt.py`

| Location                                                  | 現状                                                                                                     | S09で必要な変更                                                                                           |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| lines 28–35                                               | artifact moduleから単一の `SUPPORTED_ORACLE_VERSION` と汎用関数をimportしている                                       | exact profileに artifact reader/decoderをbindし、単一version constant依存を除く                                |
| lines 51–62 `_ROOT_CAPABILITIES`, `_SESSION_CAPABILITIES` | capabilityがmodule-globalで、version profileに属していない                                                       | profile-owned exact token tupleへ移す                                                                  |
| lines 51–62                                               | 実行argvでは使う `--browser-no-cookie-sync` がrequired root capabilityに含まれていない                                | 0.16.1 profileのrequired root tokenに追加し、全 emitted version-sensitive flagをhelp evidenceへ結び付ける         |
| lines 78–88 `_OraclePreflightReceipt`                     | version/help exit、missing flags、boolだけを持ち、選択profile、profile completeness、decoder/builder bindingを保持しない | content-free receiptへ exact profile identity とprofile contract validation結果を追加する                    |
| lines 95–223 `invoke_issue_planning_chatgpt`              | preflight結果をboolとして捨て、selected profileを後続へ渡さない                                                         | preflightが selected profileを返し、browser argv、session state、recovery、artifact collectionへ同じprofileを渡す |
| lines 145–165 browser argv assembly                       | `Pro`、`select`、attachment policy等がgeneric adapterにhardcodeされている                                        | 0.16.1の完全な旧argv順序を維持しつつ、version-specific policy値はprofileから取得する                                      |
| lines 169–200 recovery trigger                            | nonzero、timeout、session nonterminalだけで `_recover_same_session` を呼ぶstage-blind baseline                 | S09ではこの発火条件を変更しない。builder ownershipだけ移す。false/unknown guardはS10                                     |
| lines 322–419 `_read_oracle_preflight_receipt`            | `version != SUPPORTED_ORACLE_VERSION`で単一versionのみ受理する                                                  | exact registry lookupへ置換する                                                                          |
| lines 378–405 help checks                                 | `flag in stdout` のsubstring判定で、`--harvester`等のnear-matchがflag存在と誤認され得る                                 | help出力からexact option tokenを抽出し、token set membershipで判定する                                            |
| lines 446–490 `_recover_same_session`                     | generic helperが `"session"`, `"--harvest"`, `"--no-recover"` を直接構築する                                   | selected profileの `harvest_argv_builder` を一度だけ呼ぶ。generic helperからversion-specific tokenを除去する        |
| lines 509–518 `_session_state`                            | artifact readerへ単一version constantを渡す                                                                  | selected profileのstage decoder/artifact readerを使う                                                   |
| lines 521–565 `_collect_typed_result`                     | repository sentinel、ZIP、Review JSONの全読取りに単一version constantを渡す                                         | selected profileのreader bindingを使う。validation semanticsは変更しない                                       |

### 3.2 `issue_planning_oracle_artifact.py`

| Location                           | 現状                                                                                   | S09で必要な変更                                                        |
| ---------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| line 1                             | moduleがOracle 0.16.1専用と明記される                                                         | exact-version reader registryまたはprivate reader objectsへ移行する      |
| line 20 `SUPPORTED_ORACLE_VERSION` | `"0.16.1"` の単一定数                                                                     | exact `"0.16.1"` / exact `"0.17.0"` の個別bindingへ置換する              |
| lines 47–174                       | status、ZIP、Review JSON、repository sentinelが共通 `_read_metadata` へ依存                   | selected exact-version readerを入口にする                              |
| lines 177–201 `_read_metadata`     | versionが単一constant以外ならrejectし、`meta.json`、`id`、`mode=browser`を0.16.1 schemaとして読む     | 0.16.1 decoderをそのまま保持し、0.17.0はcharacterized schemaだけを別decoderで読む |
| lines 204以降                        | descriptor-rooted open、size/SHA、symlink/path containment、ZIP bounds等のsafe primitives | 変更・緩和しない。意味が同一と確認できた内部primitiveのみ共有する                            |

現行artifact readerが単一 `0.16.1` gateを持つこと、および安全なZIP/JSON読取りが既に存在することは確認済みである。

### 3.3 Focused tests

| File / location                                 | 現状                                                                                                         |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `test_issue_planning_chatgpt.py:529–569`        | `0.16.2` と `0.17.0` をunsupportedとしてprompt/recovery 0にする                                                    |
| `test_issue_planning_chatgpt.py:636–707`        | preflight receiptを0.16.1専用として固定し、0.17.0ではhelpを呼ばない                                                         |
| `test_issue_planning_chatgpt.py:800–1103`       | timeout/nonzero/nonterminalでprompt 1、harvest 1となるstage-blind baselineを保持する                                 |
| `test_issue_planning_chatgpt.py:1851–1863`      | 旧exact recovery argvを直接assertする                                                                            |
| `test_issue_planning_chatgpt.py:1910–1911`      | session help fixtureは `--harvest --no-recover`                                                             |
| `test_issue_planning_oracle_artifact.py:16–147` | 0.16.1 successと0.16.2 rejectionのみをfixture化している                                                             |
| 両test module                                    | profile registry、builder spy、capture builder、exact 0.17 reader binding、cross-version decoder isolationが未実装 |

### 3.4 Written contractとのreconciliation

* `report.md` のS01 probeは、direct PATH Oracle `0.17.0` のversion/help surface、directory、multiple paths、native follow-up、missing-path pre-submit failureを確認している。
* ただし、添付情報には次のexact値が存在しない。

  * 0.17.0のharvest argv。
  * 0.17.0のcapture argv。
  * harvest/captureが同一commandか否か。
  * `promptSubmitted`、response completion、model verified、observed labelのexact metadata field。
  * 0.17.0 artifact metadataの完全schema。
  * inline attachment modeのpositive/negative characterization。
* したがって、これらを0.16.1から流用または推測して0.17.0 profileへ記述してはならない。

---

## 4. Minimal implementation steps in execution order

### Step 1 — Characterization receiptをhard precondition化する

実装前に、direct PATH Oracle `0.17.0` から取得したsanitized receiptを確認する。receiptには最低限、次が必要である。

* normalized versionがexact `0.17.0`。
* root helpのexact option token set。
* `session --help` のexact option token set。
* formal browser invocationで使用可能なexact model/strategy/attachment argv policy。
* `inline_mode_characterized` の明示的な `true` または `false` と根拠。
* sanitized session metadata shape。
* stage decoderが参照するexact field path、型、enum/boolean値。
* exact harvest command token sequence。
* exact capture command token sequence。
* harvest/captureが同一commandなら、その同一性。
* exact artifact reader schema binding。
* raw prompt、private path、target URL、session handle、config、transcriptを含まないこと。

receiptが不足している場合、0.16.1 profile抽出とtestsまでは実施可能だが、`0.17.0` registry entryを作成せず、S09を`blocked`として返す。placeholder、TODO value、0.16.1流用でprofileを有効化しない。

### Step 2 — Red testsを先に固定する

既存0.16.1 testsを削除せず、次を追加する。

1. 0.16.1 profileが旧browser argvと旧recovery argvを完全一致で返す。
2. generic recovery helperがselected profile builderを使う。
3. 0.17.0 profileはcharacterization fixtureとの完全一致だけで成立する。
4. unknown patch、missing capability、incomplete profileはprompt前に停止する。
5. help flag near-matchを拒否する。
6. selected profile以外のreader/builderを呼ばない。
7. capture builderはprofileに存在するが、S09 runtime invocationでは呼ばれない。

### Step 3 — Private exact-version profile contractを導入する

`issue_planning_chatgpt.py` 内に、公開APIを増やさないprivate frozen profile contractとexact registryを置く。

Profileが所有する最小field:

| Field                           | Contract                                                                                           |
| ------------------------------- | -------------------------------------------------------------------------------------------------- |
| `version`                       | exact normalized version string                                                                    |
| `required_root_capabilities`    | exact help option token tuple/set                                                                  |
| `required_session_capabilities` | exact session-help option token tuple/set                                                          |
| `browser_argv_policy`           | engine、logical model、strategy、managed Chrome、cookie、wait、attachment syntaxのversion-specific policy |
| `inline_mode_characterized`     | 明示的bool。未設定を許可しない                                                                                  |
| `stage_evidence_decoder`        | exact-version sanitized metadataを読むcallable                                                        |
| `artifact_reader`               | exact-version reader binding                                                                       |
| `harvest_argv_builder`          | executable/session IDからexact immutable argv tupleを返すcallable                                       |
| `capture_argv_builder`          | executable/session IDからexact immutable argv tupleを返すcallable                                       |

Profile completenessをprompt実行前に検証する。required field、decoder、reader、両builder、inline宣言のいずれかが欠落する場合は、prompt、harvest、captureをすべて0回にして `oracle_capability_unsupported` で停止する。

### Step 4 — Exact token help validationへ移行する

* help出力から `--...` のoption lexemeだけを抽出するprivate parserを作る。
* substring検索を廃止する。
* `--harvester` は `--harvest` を満たさない。
* `--browser-model-strategy-extra` は `--browser-model-strategy` を満たさない。
* 0.16.1 required root capabilitiesには、現行argvで使用している `--browser-no-cookie-sync` を含める。
* unknown versionはroot/session helpを実行せず停止する。
* root capability不足ならsession helpへ進まず停止する。

### Step 5 — 0.16.1 behaviorをprofileへ抽出する

* 現行browser argvの値、順序、one prompt、repeated `--file` orderを変更しない。
* 現行harvest commandを0.16.1 builderへ移す。
* generic `_recover_same_session` はbuilderが返したtupleをそのまま `_run_oracle` へ渡す。
* 0.16.1では現行の一つのsame-session commandを、harvest/captureの二つのsemantic fieldへ同じbuilderとして明示bindする。
* S09 runtimeが実際に呼ぶのはharvest builderだけとする。capture invocationはS12まで追加しない。
* current stage-blind trigger、poll deadline、executable identity revalidation、one-prompt behaviorを保持する。
* `inline_mode_characterized=False` を明示する。inline executionは追加しない。

### Step 6 — Artifact readerをexact-version bindingへ移行する

`issue_planning_oracle_artifact.py` では次だけを行う。

* 現行 `_read_metadata` を0.16.1専用decoderとして保持する。
* exact versionからreaderを取得するprivate registry/bindingを追加する。
* 0.17.0 sanitized fixtureのschemaが完全にcharacterizeされている場合だけ0.17.0 decoderを追加する。
* selected profileがreader object/callableを所有する。
* existing status、repository sentinel、ZIP、Review JSON entry pointsはselected readerを経由する。
* path containment、descriptor identity、size、SHA、ZIP bounds、strict JSON、missing/ambiguous semanticsを変更しない。
* S12のdownload pending、capture result、response-complete separationを追加しない。

### Step 7 — 0.17.0 profileをreceiptからのみ構築する

* exact keyは `"0.17.0"` のみ。
* root/session capability tuple、browser policy、inline declaration、decoder field、artifact reader、harvest/capture argvをreceiptからliteral fixture化する。
* builderが置換してよい動的operandは、characterizationで確認された executable path と session IDだけとする。
* 0.17.0 commandへ0.16.1の `"session"`, `"--harvest"`, `"--no-recover"` を自動付加しない。
* harvest/captureが同じcommandなら、同じbuilder objectを両fieldへbindし、identity assertionを置く。
* logical requestは`Pro`、strategyはexplicit `select`を維持する。characterizationがこれを受理しない場合、`current`や別modelへ変更せず停止する。
* `GPT-5.6 Sol` をprofile constantやaccepted mappingにしない。

### Step 8 — Selected profileを全S09 infra pathへ伝播する

Selected profileを次へ明示的に渡す。

* browser argv policy。
* session state decoder。
* `_recover_same_session`。
* artifact collection。
* repository access sentinel。
* authoring ZIP / Review JSON reader。

Generic helperがversion文字列から再選択したり、single global constantを参照したりしない。preflightで選択した同一profile objectを一つのinvocation全体で使う。

---

## 5. Explicit allowlist and forbidden paths/behaviors

### 5.1 Production write allowlist

1. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
2. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`

### 5.2 Test write allowlist

1. `tests/unit/infra/test_issue_planning_chatgpt.py`
2. `tests/unit/infra/test_issue_planning_oracle_artifact.py`

### 5.3 Evidence-only update

実装・検証後に限り、orchestrator指定の次の場所へcontent-free evidenceを追加できる。

* `${ISSUE_DIR}/report.md`
* S09 step-local implementation/evidence artifact

Evidence-only updateはproduction behavior変更と同じcommit scopeとして扱わず、実装差分、characterization receipt、test結果を区別する。

### 5.4 Forbidden paths

次は変更禁止である。

* `application/`
* `domain/`
* `commands/`
* CLI parser/runtime
* generic ports/backend abstractions
* operation resources
* provider/installed/dogfood projection
* requirement/design/plan/ADR
* S06 Blue/Red lifecycle
* S10以降のproduction files/tests
* Oracle本体またはpersonal wrapper
* unrelated profile、Issue、Epic、Initiative

### 5.5 Forbidden behavior

* semver range、wildcard、unknown patch acceptance。
* 0.17.0から0.16.1へのsilent downgrade。
* alternate Oracle path/binary探索。
* wrapper/API/default branch fallback。
* model `current`、default model、別modelへのfallback。
* required attachmentのdrop、copy、archive、ZIP、materialization。
* tree traversal、content inspection、hashingをinput transportへ再導入すること。
* new execution retry、inline retry、post-submit new execution。
* public failure reasonの追加・変更。
* output validatorの緩和。
* shell invocation、command string concatenation。
* raw help、prompt、path、URL、session handle、transcript、configのpublic/report出力。
* generic `_recover_same_session` 内へのversion-specific command literal残存。

---

## 6. Profile contract and exact fixture/builder behavior

### 6.1 共通invariants

1. Registry lookupはnormalized exact version equalityのみ。
2. Profile selection後、required capability、decoder、reader、inline declaration、両builderをすべて検証する。
3. Profile completenessが不明ならpromptを開始しない。
4. Help capabilityはexact option tokenで比較する。
5. Generic adapterはprofile commandを補完・修正しない。
6. Builderはimmutable tupleを返し、shell quotingを行わない。
7. Selected profileとartifact reader versionを交差利用しない。
8. Profileのversion-specific literalはprofile definition/fixture内だけに置く。

### 6.2 Exact `0.16.1` profile

| Contract item        | Required behavior                                                                                                                                                                                                                        |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Version              | exact `"0.16.1"`                                                                                                                                                                                                                         |
| Root capabilities    | `--engine`, `--file`, `--slug`, `--wait`, `--prompt`, `--browser-attachments`, `--model`, `--browser-model-strategy`, `--remote-chrome`, `--browser-no-cookie-sync`                                                                      |
| Session capabilities | `--harvest`, `--no-recover`                                                                                                                                                                                                              |
| Browser argv         | 現行順序を完全保持。`--engine browser --model Pro --browser-model-strategy select --remote-chrome <loopback> --browser-no-cookie-sync --wait --browser-attachments always --slug <id> --prompt <exact prompt>` の後に、入力順どおりのrepeated `--file <path>` |
| Prompt               | 一つのargv value。改行、引用符、Unicode、末尾改行を変更しない                                                                                                                                                                                                  |
| Inline declaration   | explicit `False`                                                                                                                                                                                                                         |
| Stage decoder        | 現行0.16.1 metadata/status semanticsを保持。未存在fieldを推測でtrue/falseにしない                                                                                                                                                                         |
| Artifact reader      | 現行0.16.1 readerとstrict validationをそのままbind                                                                                                                                                                                               |
| Harvest builder      | exact `(str(executable), "session", session_id, "--harvest", "--no-recover")`                                                                                                                                                            |
| Capture builder      | 旧commandと同じbuilderを明示bind。S09 runtime invocation countは0                                                                                                                                                                                 |
| Recovery trigger     | S09では現行stage-blind triggerを維持。S10で変更                                                                                                                                                                                                     |
| Model claim          | logical `Pro` requestのみ。observed label/verified successは主張しない                                                                                                                                                                            |

### 6.3 Exact `0.17.0` profile

| Contract item             | Required behavior                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------- |
| Version                   | exact `"0.17.0"`                                                                      |
| Root/session capabilities | sanitized direct-PATH characterization receiptのexact token tupleと完全一致                 |
| Browser policy            | receiptでacceptedと確認されたexact argv policyのみ                                             |
| Logical model             | `Pro`を要求し、strategyを明示する。`current` fallback禁止                                          |
| Inline declaration        | receiptの明示的bool。証跡なしはprofile未登録                                                       |
| Stage decoder             | receiptに記録されたexact field path、型、enum/booleanだけを読む。missing、wrong type、ambiguous値を推測しない |
| Model evidence            | decoder sourceがcharacterizedされていること。UI labelをgeneric constantへ昇格しない                   |
| Artifact reader           | sanitized 0.17.0 schema fixtureと完全にbindしたreaderだけ                                     |
| Harvest builder           | receiptのexact token sequenceを返す。executable/session operand以外を発明しない                    |
| Capture builder           | receiptのexact token sequenceを返す。harvestとの同一性または差異をfixtureで固定                          |
| Same builder case         | receiptが同一commandを示す場合、両fieldへ同じbuilder objectをbindする                                 |
| Formal claim              | S09 unit fixtureの成立はS11 live browser/model compatibility PASSを意味しない                   |

このbrief時点で、0.17.0のexact harvest/capture token sequence、stage field names、artifact schema、inline boolは提示情報から確定できない。workerはcharacterization receiptなしに値を作らない。

### 6.4 Unknown-version block

次はすべてprofile lookup failureとする。

* `0.16.0`
* `0.16.2`
* `0.17.1`
* `0.17.2`
* `0.18.0`
* `1.0.0`
* malformed output
* 複数行version output
* prefix/suffix付きversion output

Expected behavior:

* version invocation `1`
* root help `0`
* session help `0`
* prompt invocation `0`
* harvest builder calls `0`
* capture builder calls `0`
* recovery subprocess `0`
* public resultはexisting `blocked / oracle_capability_unsupported`
* 0.16.1へのdowngrade `0`

---

## 7. Focused tests and exact commands

### 7.1 Required test changes

#### `tests/unit/infra/test_issue_planning_chatgpt.py`

追加・更新するtests:

1. `test_exact_profile_registry_accepts_only_0161_and_characterized_0170`
2. `test_unknown_patch_stops_before_help_prompt_or_builder`
3. `test_help_capability_matching_rejects_near_match_tokens`
4. `test_0161_profile_preserves_exact_browser_argv`
5. `test_0161_profile_harvest_and_capture_bind_legacy_builder`
6. `test_0170_profile_matches_characterization_fixture_exactly`
7. `test_incomplete_profile_blocks_before_prompt_or_builder`
8. `test_generic_recovery_invokes_selected_profile_harvest_builder_once`
9. `test_generic_recovery_does_not_assemble_version_specific_tokens`
10. `test_selected_profile_reader_is_used_for_session_and_output`
11. `test_cross_profile_builder_is_never_called`
12. `test_user_config_environment_boundary_is_unchanged`

既存の0.17.0 unsupported testsは、complete profile fixtureがある場合に限り0.17.0 success/profile testsへ分割する。unknown-version fixtureは`0.17.1`等へ変更する。

#### `tests/unit/infra/test_issue_planning_oracle_artifact.py`

追加・更新するtests:

1. exact 0.16.1 fixtureの全既存success/rejection保持。
2. sanitized exact 0.17.0 metadata fixture。
3. 0.16.1 fixtureを0.17.0 readerへ渡すとreject。
4. 0.17.0 fixtureを0.16.1 readerへ渡すとreject。
5. exact version以外のreader lookup拒否。
6. 0.17.0 required stage/model fieldのmissing、wrong type、unknown enum拒否。
7. 0.17.0 artifact inventory/schema mismatch拒否。
8. existing descriptor/path/SHA/ZIP/JSON testsの非回帰。

### 7.2 Builder invocation spies and exact call counts

Invocation-level spyはbuilder callable自体をmonkeypatchし、呼出し引数と回数を記録する。builderが返すsentinel argvをそのままsubprocess spyが受け取ることまで確認する。

| Scenario                                    | Version | Version probe | Root help | Session help | Prompt | Harvest builder | Capture builder | Recovery subprocess |
| ------------------------------------------- | ------: | ------------: | --------: | -----------: | -----: | --------------: | --------------: | ------------------: |
| malformed/unknown version                   | unknown |             1 |         0 |            0 |      0 |               0 |               0 |                   0 |
| known version、root capability欠落             |   exact |             1 |         1 |            0 |      0 |               0 |               0 |                   0 |
| known version、session capability欠落          |   exact |             1 |         1 |            1 |      0 |               0 |               0 |                   0 |
| known version、inline declaration欠落          |   exact |             1 |         1 |            1 |      0 |               0 |               0 |                   0 |
| known version、stage decoder欠落               |   exact |             1 |         1 |            1 |      0 |               0 |               0 |                   0 |
| known version、harvest builder欠落             |   exact |             1 |         1 |            1 |      0 |               0 |               0 |                   0 |
| known version、capture builder欠落             |   exact |             1 |         1 |            1 |      0 |               0 |               0 |                   0 |
| normal terminal 0.16.1 success              |  0.16.1 |             1 |         1 |            1 |      1 |               0 |               0 |                   0 |
| 0.16.1 nonzero/timeout/nonterminal baseline |  0.16.1 |             1 |         1 |            1 |      1 |               1 |               0 |                   1 |
| normal terminal characterized 0.17.0        |  0.17.0 |             1 |         1 |            1 |      1 |               0 |               0 |                   0 |
| 0.17.0 nonterminal S09 structural fixture   |  0.17.0 |             1 |         1 |            1 |      1 |               1 |               0 |                   1 |
| invalid metadata before recovery            |   exact |             1 |         1 |            1 |      1 |               0 |               0 |                   0 |
| direct capture-builder contract unit test   |   exact |             — |         — |            — |      — |               0 |               1 |                   0 |

最後の行はruntime invocation testではなくbuilder単体contract testである。S09 runtime pathでcapture builderを呼ぶtestを追加しない。

### 7.3 Exact assertions

* 0.16.1 harvest builderの戻り値は旧exact argvとbyte-for-byte相当。
* 0.16.1 harvest/capture fieldは同じbuilderを明示的に指す。
* 0.17.0 builderはcharacterization fixtureとtuple全体が一致する。
* 0.17.0でharvest/captureが同一ならbuilder object identityも一致する。
* promptは一回だけ。
* post-submit/new-execution behaviorは追加しない。
* selected profile以外のbuilder/reader call countは0。
* generic `_recover_same_session` がsentinel builder argvを変更せず実行する。
* generic recovery body内でversion-specific tokenを再構築しない。
* raw help、prompt、path、session metadataがreceipt/resultのreprやserializationへ出ない。
* `--browser-no-cookie-sync` missing help fixtureはprompt前にblockする。
* `--harvester`だけのsession help fixtureは`--harvest` missingとしてblockする。

### 7.4 Exact verification commands

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py -q

uv run pytest \
  tests/unit/infra \
  -k 'oracle and (artifact or session or profile)' -q

uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py

uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py

git diff --check

git diff --name-only -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py
```

Generic-command locality audit:

```bash
rg -n '"session"|--harvest|--no-recover' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

Expected audit result:

* version-specific command tokenの出現はprofile-owned 0.16.1 builder、およびcharacterized 0.17.0 builderだけ。
* generic `_recover_same_session` body、generic preflight、generic artifact collection内の出現は0。

---

## 8. Verification and report/EAL evidence to record after implementation

### 8.1 Repository evidence

`report.md` に次を記録する。

* source repository。
* named branch。
* source HEAD `061829...`。
* resulting implementation HEAD。
* local/remote exact equality。
* default branch fallback 0。
* changed production/test files。
* allowlist外diff 0。
* workerが実装完了またはreview PASSを自己宣言していないこと。

### 8.2 Characterization evidence

Direct PATH Oracleのreceiptについて、次のcontent-free値だけを記録する。

* `oracle_version`
* `profile_id`
* root capability token tuple
* session capability token tuple
* `inline_mode_characterized`
* stage decoder field namesと型
* model evidence field namesと型
* artifact schema IDまたはsanitized shape
* harvest/capture builderがsame/differentか
* builder argvのsanitized token shape
* receipt path
* receipt SHA-256
* receipt取得条件の分類
* 未確認field

記録禁止:

* raw prompt
* raw attachment path
* private absolute path
* target URL
* session handle
* Oracle home
* user/project config
* transcript
* browser endpoint
* credential
* UI full dump

### 8.3 Evidence Adoption Ledger

少なくとも次を分ける。

| Evidence class                        | 扱い                                            |
| ------------------------------------- | --------------------------------------------- |
| `direct_path_oracle_characterization` | 0.17.0 profile fixture/builder/readerの一次根拠    |
| `external_wrapper_observation`        | 補助証跡。profile command/model mappingの根拠にしない     |
| unit fixture                          | characterization receiptをsanitizedに投影したtest証跡 |
| code/static verification              | pytest、ruff、mypy、diff-check結果                 |
| fresh review                          | implementation後の別ゲート。workerはPASSを記録しない        |

Wrapperがmodel evidenceを出した場合は、wrapper-observed値としてのみ次を記録できる。

* requested model
* target label
* resolved label
* strategy
* verified flag

`GPT-5.6 Luna / Max` の実測証跡がない場合、requested authoring setting以上の主張をしない。`GPT-5.6 Sol` が観測されても、direct PATH Oracle profile mappingとして採用しない。

### 8.4 S09 closure evidence

S09をfresh reviewへ渡せる最低条件:

* exact 0.16.1 profile builder regression pass。
* complete exact 0.17.0 characterization receipt。
* complete 0.17.0 profile fixture。
* generic recovery hardcode除去。
* unknown-version block pass。
* profile completeness fail-closed pass。
* exact help token tests pass。
* cross-version reader isolation pass。
* builder spy call-count matrix pass。
* focused pytest、ruff、mypy、diff-check pass。
* allowlist外diff 0。

これらの一つでも欠ける場合、reportはS09を`blocked`または`pending`のまま保持する。

---

## 9. Stop conditions, risks, and unresolved questions

### 9.1 Immediate stop conditions

次のいずれかでは0.17.0 profileを登録せず停止する。

1. direct PATH Oracle `0.17.0` characterization receiptを取得できない。
2. root/session helpのexact option tokenを確定できない。
3. `--model Pro` / explicit `select` を0.17.0で受理できない。
4. model evidence sourceをprofileへbindできない。
5. prompt submission evidence sourceをprofileへbindできない。
6. stage metadataのmissing/unknownを安全に識別できない。
7. `inline_mode_characterized` を明示的boolにできない。
8. exact harvest commandを確定できない。
9. exact capture commandを確定できない。
10. harvest/captureの同一性を確定できない。
11. artifact metadata/schemaをexact readerへbindできない。
12. 0.17.0対応に0.16.1 commandの推測流用が必要になる。
13. generic adapterへversion-specific条件またはcommand literalを残す必要がある。
14. application/domain/CLI/public reason変更が必要になる。
15. wrapper、API、alternate model、default branch fallbackが必要になる。
16. existing path/SHA/ZIP/JSON safety validationを緩める必要がある。
17. allowlist外ファイル変更が必要になる。

### 9.2 Risks to preserve in the handoff

* 現行0.16.1 recoveryはstage-blindである。S09でprofileへ移しても安全化されたとは扱わない。
* Builder ownershipの移行と`promptSubmitted` guardを混同すると、S10 scopeを先取りする。
* Capture builderの存在とcapture recoveryの実装を混同すると、S12 scopeを先取りする。
* Unit fixtureによる0.17.0 profile成立とlive browser compatibilityを混同すると、S11 gateを迂回する。
* Help substring matchingを残すとnear-match capabilityを誤受理する。
* `--browser-no-cookie-sync`をrequired capabilityに含めないと、explicit argvとhelp evidenceが不一致のまま残る。
* Reader共通化を急ぐと0.16.1/0.17.0 schema差分を隠す。
* Wrapper-observed model labelをprofileへ固定すると一時的UI表示へ過適合する。

### 9.3 Unresolved questions — guessed answerを作らない

以下はcharacterization receiptが回答するまで未解決のまま残す。

1. 0.17.0のexact root capability tokensは何か。
2. 0.17.0のexact session capability tokensは何か。
3. direct/inline attachmentのexact argv syntaxは何か。
4. inline modeは安全にcharacterized済みか。
5. `promptSubmitted`のexact field path、型、値は何か。
6. response completionのexact field path、型、値は何か。
7. model verifiedのexact field path、型、値は何か。
8. observed model labelのexact field pathは何か。
9. logical `Pro` と observed labelのaccepted mappingは存在するか。
10. 0.17.0のexact harvest commandは何か。
11. 0.17.0のexact capture commandは何か。
12. harvestとcaptureは同一commandか。
13. 0.17.0 session metadata/artifact inventoryは0.16.1と同一schemaか。
14. 0.17.0のsession slug normalizationに差異があるか。
15. artifact readerのどのsafe primitiveだけを共有可能か。

未解決項目を仮fixture、コメント、fallback、broad acceptanceで埋めない。

---

## 10. Worker handoff checklist and required output fields

### 10.1 Handoff checklist

* [ ] Repositoryが`chemitaro/spec-dock`である。
* [ ] Branchが`codex/iss-00354-chatgpt-context-contract`である。
* [ ] 開始時HEADが`061829c33fea751f430948da954aae6dcebda2b0`と一致する。
* [ ] Default branchへfallbackしていない。
* [ ] 8添付とexact GitHub blobsを読んだ。
* [ ] Complete sanitized direct-PATH 0.17.0 characterization receiptを確認した。
* [ ] Receipt不足なら0.17.0 registry entryを追加していない。
* [ ] Production変更は指定2ファイルだけである。
* [ ] Test変更は指定2ファイルだけである。
* [ ] 0.16.1 browser argvが完全一致で維持される。
* [ ] 0.16.1 recovery argvが完全一致で維持される。
* [ ] 0.16.1 harvest/capture semantic fieldsへ旧builderを明示bindした。
* [ ] Generic recovery helperからversion-specific command assemblyを除去した。
* [ ] 0.17.0 builderはreceiptのexact token sequenceだけを返す。
* [ ] Unknown patch/rangeを受理しない。
* [ ] Help optionをexact tokenで検証する。
* [ ] `--browser-no-cookie-sync`を0.16.1 required capabilityへ含めた。
* [ ] Profile incomplete時のprompt/builders call countがすべて0である。
* [ ] S09 runtimeのcapture builder call countが0である。
* [ ] S10 recovery decision/public mappingを実装していない。
* [ ] S11 live browser/model PASSを主張していない。
* [ ] S12 capture/download policyを実装していない。
* [ ] `GPT-5.6 Sol`、Luna、Maxをruntime accepted mappingとしてhardcodeしていない。
* [ ] Raw private evidenceをcode fixture/reportへ持ち込んでいない。
* [ ] Focused pytest、ruff、mypy、diff-checkが完了した。
* [ ] Allowlist外diffが0である。
* [ ] Worker自身がreview PASS、S09 closure、merge readinessを宣言していない。

### 10.2 Required worker output fields

Workerのhandoffには次を必ず含める。

| Field                      | Required content                                         |
| -------------------------- | -------------------------------------------------------- |
| `source_identity`          | repository、branch、source HEAD、default fallback 0         |
| `resulting_identity`       | resulting local HEAD、remote HEADまたは未push、ahead/behind    |
| `changed_files`            | exact path list。production/test/evidenceを区分              |
| `characterization_receipt` | path、SHA-256、exact version、採用可否、未確認field                 |
| `profile_matrix`           | 0.16.1、0.17.0、unknown versionの登録/拒否状態                    |
| `capability_matrix`        | exact root/session tokensとhelp検証結果                       |
| `browser_argv_matrix`      | 0.16.1 exact旧argvと0.17.0 characterized argvの比較           |
| `builder_matrix`           | harvest/captureのexact argv、same/different、profile owner  |
| `builder_call_counts`      | 各required scenarioのprompt/harvest/capture/subprocess回数   |
| `reader_matrix`            | 0.16.1/0.17.0 fixture、cross-version rejection、schema gap |
| `test_results`             | command、exit code、passed/skipped/failed数                 |
| `static_results`           | ruff、mypy、diff-check                                     |
| `scope_audit`              | allowlist外diff、wrapper/API/default branch fallbackの有無    |
| `model_evidence`           | logical selector、wrapper-observed evidenceがある場合の分類、未検証点  |
| `unresolved_risks`         | 推測せず残した質問とblocking/non-blocking分類                        |
| `report_eal_note`          | report/EALへ追加すべきcontent-free要約                           |
| `handoff_status`           | `ready_for_fresh_review` または `blocked`                   |
| `closure_claim`            | 必ず`none`。workerはS09 closureを宣言しない                        |
