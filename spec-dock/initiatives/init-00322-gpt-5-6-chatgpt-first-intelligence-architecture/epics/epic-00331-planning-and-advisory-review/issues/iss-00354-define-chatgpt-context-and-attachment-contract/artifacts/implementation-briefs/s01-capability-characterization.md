# iss-00354 / Milestone S01 実装ブリーフ

## Oracle 0.17.0 Capability Characterization and Regression Boundary

| 項目                      | 値                                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------- |
| 対象リポジトリ                 | `chemitaro/spec-dock`                                                              |
| 対象ブランチ                  | `codex/iss-00354-chatgpt-context-contract`                                         |
| GitHub preflight commit | `6561f0b16cb5ba12d54ba262c3baf86340236c00`                                         |
| GitHub比較結果              | 指定ブランチと上記 commit は `identical`、ahead `0`、behind `0`                                |
| default branch fallback | 使用禁止、今回も未使用                                                                        |
| Issue / Milestone       | `iss-00354` / S01                                                                  |
| closure ID              | `cl-s01-capability`                                                                |
| 保存予定先                   | `artifacts/implementation-briefs/s01-capability-characterization.md`               |
| 想定利用モデル                 | `GPT-5.6 Luna`                                                                     |
| 想定推論設定                  | `Reasoning Effort Max`                                                             |
| 実測モデル証跡                 | **未検証**。上記はブリーフ利用時の要求設定であり、本ブリーフの生成経路または product runtime で実際に選択されたとの主張ではない         |
| 文書の権威                   | Codex 実装用の advisory guidance。実装完了、assurance promotion、PR、merge、Issue finish を意味しない |

GitHub connector では指定 branch の存在、commit `6561f0b1...` の存在、および branch tip との完全一致を確認した。commit は v5 fresh review の結果を `candidate-note.md` と `report.md` に反映した文書変更である。
正規要件・設計・計画・報告・ADR・runtime・tests の統合資料も参照した。

---

## 1. S01 の目的と非目的

### 1.1 目的

S01 の目的は、**現在の PATH-resolved Oracle における capability 境界を実測し、後続の direct-path 実装を開始できるかを fail-closed に判断すること**である。

S01 で閉じる対象は次の四点である。

1. original directory path を Oracle へ直接渡せるか。
2. static directory と dynamic file など、複数の original top-level paths を一回の operation に渡せるか。
3. successful submission 後の conversation を、Oracle の正式な continuation interface で継続できるか。
4. direct attachment failure を、prompt submission 前の attachment failure として安全に観測できるか。

併せて、現行 Oracle `0.16.1` adapter の次の回帰境界を固定する。

* exact version / root help / session help preflight。
* PATH Oracle、managed Chrome、`shell=False`、sanitized child environment。
* logical selector `Pro`、strategy `select`。
* one `--prompt`、one generated prompt-pack `--file`。
* personal wrapper / API invocation 0。
* unsupported version / capability では prompt invocation 0。
* timeout / nonzero / nonterminal 時の現行 stage-blind same-session harvest。

計画上、S01 は capability receipt を作り、`_ROOT_CAPABILITIES` / `_SESSION_CAPABILITIES` を実測した interface に整合させる段階である。directory、multiple path、continuation のいずれかが未対応なら S02 以降へ進まない。

### 1.2 非目的

S01 では以下を行わない。

* `invoke_issue_planning_chatgpt` を original attachment paths transport へ移行しない。これは S03–S04。
* `_write_transport_pack`、`context-NNN.md`、manifest 群を削除しない。これも S03–S04。
* Blue continuation binding、fresh Red state、thread persistence を実装しない。これは S06。
* Oracle `0.17.0` を production-supported version として登録しない。これは S09。
* `OracleCompatibilityProfile`、stage decoder、inline fallback、harvest/capture builder を実装しない。これは S09–S10。
* stage-specific public reasons を追加しない。これは S10。
* 0.17 session metadata / artifact reader を実装しない。これは S09 / S12。
* model `current`、alternate model、`GPT-5.6 Sol`、または `GPT-5.6 Luna` を product constant にしない。
* undocumented Oracle flag、subcommand、environment variable、target URL を推測して追加しない。
* personal `chatgpt-use` wrapper、OpenAI API、別 backend、absolute executable path、default branch fallback を使わない。
* prompt、transcript、credentials、private URL、session handle、private absolute path を repository evidence に保存しない。
* canonical requirement / design / plan / ADR を変更しない。
* assurance status、review status、implementation status を昇格させない。

---

## 2. 検証済み source facts、仮定、未検証事項

### 2.1 Repository / document facts

| 事実                                                             | 根拠と実装上の意味                                                                                                                                                 |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 指定 branch tip は `6561f0b1...`                                  | GitHub connector で exact commit と branch の一致を確認済み。S01 の baseline identity とする                                                                             |
| `candidate-note.md` が記録する last reviewed HEAD は `079685b2...`   | current preflight commit `6561f0b1...` とは異なる。`6561f0b1...` が review 済みであるとは本ブリーフから主張しない。Codex は product-code変更前に workflow 上の current-HEAD gate を独立確認すること。 |
| `.assurance.json` は `stage=requirement`、`status=provisional`   | S01 brief の作成や test execution は assurance promotion を意味しない。                                                                                               |
| `report.md` は implementation 未開始を記録                            | S01 の結果は既存 closure / test / EAL slot に追記し、既存の未実施記録を実測結果で置き換える                                                                                             |
| historical wrapper evidence は direct PATH Oracle evidence ではない | wrapper の model / browser observation を capability supported の根拠として採用しない                                                                                  |
| Luna / Max は要求設定                                               | 過去の wrapper 記録でも Luna / Max の実測成功は確認されていない。要求値と observed model evidence を分離する。                                                                            |

### 2.2 現行 runtime facts

対象ファイル:

`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`

確認済み symbol と現状:

| Symbol                          | 現行挙動                                                                                                                                        | S01 での扱い                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `_ROOT_CAPABILITIES`            | `--engine`, `--file`, `--slug`, `--wait`, `--prompt`, `--browser-attachments`, `--model`, `--browser-model-strategy`, `--remote-chrome` を要求 | actual help surface と照合する。推測で追加しない                               |
| `_SESSION_CAPABILITIES`         | `--harvest`, `--no-recover` を要求                                                                                                             | actual session help と照合する。continuation capability と同一視しない        |
| `_preflight_supported_oracle`   | `oracle --version` が `SUPPORTED_ORACLE_VERSION` と完全一致した後、root/session help を検査                                                              | content-free receipt を得られる最小 seam を追加してよい。public contract は変更しない |
| `SUPPORTED_ORACLE_VERSION`      | artifact reader 由来の `"0.16.1"`                                                                                                              | S01 では変更しない                                                      |
| `invoke_issue_planning_chatgpt` | generated prompt-pack を作り、one `--file` と one `--prompt` で起動                                                                                 | S01 では変更しない                                                      |
| `_write_transport_pack`         | attachment contents を `context-NNN.md` 等へ materialize                                                                                       | S01 では削除・変更しない                                                   |
| `_recover_same_session`         | generic adapter が `oracle session <id> --harvest --no-recover` を直接構築                                                                        | S01 では挙動を変更しない。characterization regression として固定する               |
| `_run_oracle`                   | `shell=False`, `stdin=DEVNULL`, `capture_output=True`, `check=False`                                                                        | direct capability probe でも同じ subprocess boundary を使用できる          |
| `_sanitized_child_environment`  | allowlist environment を子 process に渡す                                                                                                        | 保持する                                                             |

現行 preflight は exact `0.16.1` と help tokens を確認するだけであり、directory operand、multiple path semantics、cross-operation continuation を証明していない。

現行 production invocation は original paths ではなく generated prompt-pack directory を一つの `--file` として渡す。S01 の positive capability probe を product invocation の direct-path対応と混同してはならない。

Oracle artifact reader は exact `0.16.1` 専用である。S01 の 0.17 characterization でこの reader を 0.17 session に適用してはならない。

### 2.3 現行 tests facts

主対象:

`tests/unit/infra/test_issue_planning_chatgpt.py`

既存 test seam は次を既に提供している。

* fake executable と `subprocess.run` spy。
* exact `--version` / root help / session help fixtures。
* managed Chrome preflight stub。
* Oracle home 内の fake session / `meta.json` / artifact fixture。
* prompt call、harvest call、environment、typed result の assertion。
* wrapper / personal-profile argument が出ないことの assertion。
* unsupported version / missing help flag で prompt 0。
* timeout / nonzero 時に prompt 1、harvest 1。
* strict output / privacy regression。

既存 test は `--model Pro`、`select`、managed Chrome、one prompt、one file、sanitized environment を固定している。
timeout fixture は prompt 1 と hardcoded harvest 1 を固定している。
test helper の `_root_help()`, `_session_help()`, `_patch_runtime()`, `_invoke()` を再利用できる。

### 2.4 実装上の仮定

1. S01 の behavior characterization は、production `invoke_issue_planning_chatgpt` とは別の direct Oracle probe として実施する。
2. direct probe は `_resolve_oracle_executable`、`_executable_identity`、`_sanitized_child_environment`、`_run_oracle` と同等の boundary を使う。
3. positive behavior probe 用の exact argv は、同じ Oracle binary の `--help` / `session --help` または Oracle 自身の明示的な usage evidence から確定する。
4. help に記載されない syntax は使用しない。試行錯誤による flag guessing は characterization ではない。
5. 0.16.1 の regression evidence は repository fixture で保持できる。0.17 capability support は direct PATH Oracle の実測を必要とする。
6. live browser probe に使用する prompt は短い無害な control prompt とし、Issue 本文や private data を送信しない。

### 2.5 未検証事項

* Oracle `0.17.0` が directory path を一つの attachment operand として受理するか。
* attachment operand が反復可能か、別の multiple-value syntax を持つか。
* Oracle が cross-operation continuation を提供するか。
* continuation が同一 ChatGPT conversation であることを content-free evidence で検証できるか。
* direct attachment failure と prompt reconstruction / model selection failure を区別できるか。
* attachment failure 時の `promptSubmitted` 相当 evidence が存在するか。
* 0.17 help surface、session metadata、artifact schema。
* GPT-5.6 Luna / Max が browser runtime で選択されたか。

---

## 3. 最小の Red → Characterization → Green 実行順序

### 3.0 開始前 gate

product-code変更前に次を確認する。

```bash
git branch --show-current
git rev-parse HEAD
git status --short
```

開始時の期待値:

```text
branch: codex/iss-00354-chatgpt-context-contract
HEAD:   6561f0b16cb5ba12d54ba262c3baf86340236c00
status: clean
```

GitHub connector でも branch tip と上記 commit の一致を再確認する。local only の SHA 確認で代替しない。

`candidate-note.md` が記録する reviewed HEAD と current HEAD が異なる点について、workflow が fresh current-HEAD review を要求する場合は、**brief は保持してよいが product-code変更を開始しない**。

### 3.1 Red — regression boundary と fail-closed contract を先に固定

#### Red-1: 0.16.1 baseline を明示的に固定

既存 tests を削除・緩和せず、次を exact assertion にする。

* version call: `[oracle, "--version"]` → `0.16.1\n`
* root help call: `[oracle, "--help"]`
* session help call: `[oracle, "session", "--help"]`
* submit call count: `1`
* `--prompt` count: `1`
* `--file` count: `1`
* file operand: generated `prompt-pack` directory
* model: `Pro`
* strategy: `select`
* `--remote-chrome`: loopback endpoint
* `--browser-no-cookie-sync`: exactly once
* `shell=False`
* wrapper/API arguments: `0`

#### Red-2: current stage-blind recovery を characterization test にする

現行挙動を変更する前に、次を test 名と assertion で明示する。

推奨 test:

```text
test_0161_nonterminal_or_nonzero_uses_current_stage_blind_harvest_once
```

期待:

* prompt calls: `1`
* hardcoded recovery calls: `1`
* exact recovery argv shape:

```text
[resolved_oracle, "session", session_id, "--harvest", "--no-recover"]
```

* second prompt / new execution: `0`
* session が terminal になれば `pass / transport_received`
* terminal にならなければ `blocked / oracle_session_recovery_required`

この test は現行挙動を承認するものではなく、S09/S10 で置換すべき migration baseline である。

#### Red-3: unsupported capability は invocation 0

既存 `test_unsupported_version_or_capability_submits_no_prompt` を次まで強化する。

* fake version `0.16.2`
* fake version `0.17.0`
* missing root capability
* missing session capability
* version command timeout / nonzero
* root/session help timeout / nonzero

全 fixture の期待:

```text
PlanningInvocationResult.status == "blocked"
PlanningInvocationResult.reason == "oracle_capability_unsupported"
prompt calls == 0
harvest calls == 0
session directory creation == 0
wrapper/API calls == 0
```

`0.17.0` の live capability receipt が positive でも、S09 前の production invocation は引き続き block する。

#### Red-4: capability receipt の安全 schema

production/public contract に新しい type を追加せず、infra-private seam として次の最小 shapeを test-first で導入してよい。

```python
@dataclass(frozen=True)
class _OraclePreflightReceipt:
    version: str | None
    version_exit_code: int | None
    root_help_exit_code: int | None
    session_help_exit_code: int | None
    missing_root_capabilities: tuple[str, ...]
    missing_session_capabilities: tuple[str, ...]
    supported_by_current_runtime: bool
```

推奨 helper:

```python
def _read_oracle_preflight_receipt(...) -> _OraclePreflightReceipt
```

`_preflight_supported_oracle(...)` はこの receipt の `supported_by_current_runtime` を返す薄い wrapper とし、既存呼出側を変えない。

receipt に以下を持たせない。

* raw help stdout / stderr
* prompt
* path
* URL
* endpoint
* executable absolute path
* session ID
* transcript
* credentials
* environment dump

directory / multiple path / continuation / attachment failure の behavior receipt は **test/report-only** とし、domain/public resultへ追加しない。

### 3.2 Characterization — direct PATH Oracle の実測

#### Characterization-1: executable identity と command surface

正確に実行できる固定コマンドは次のみである。

```bash
command -v oracle
oracle --version
oracle --help
oracle session --help
```

期待 evidence:

* PATH から一つの regular executable が解決される。
* exact version string。
* root help exit `0`。
* session help exit `0`。
* directory attachment、multiple path、continuation に関係する明示 syntax。
* current `_ROOT_CAPABILITIES` / `_SESSION_CAPABILITIES` との差分。

`command -v` の absolute path、raw help全文、stderr は `report.md` に貼らない。ローカル観測用にのみ使用する。

#### Characterization-2: directory attachment

fixture:

```text
<temporary-root>/
└── static-attachments/
    └── control.txt
```

条件:

* `control.txt` は秘密を含まない短い固定文字列。
* Oracle help が directory operand を明示している場合だけ実行する。
* exact argv は help から得た syntax を使用する。
* product `_write_transport_pack` は呼ばない。
* raw direct Oracle probe として実行する。
* prompt は short control prompt。
* automatic retry、harvest、capture は行わない。

supported と判定する条件:

* original directory path が一つの top-level operand として渡された。
* Oracle evidence が attachment preparation / acceptance を示す。
* prompt submission が成功するか、少なくとも attachment stage 成功を一意に示す。
* SpecDock probe が directory contents を walk / copy / ZIP / materialize していない。
* wrapper/API calls が 0。

help syntax が曖昧、または attachment acceptance を検証できない場合は `unknown`。単に process exit `0` だけでは supported としない。

#### Characterization-3: multiple path attachment

fixture:

```text
<temporary-root>/
├── static-attachments/
│   └── control.txt
└── dynamic-evidence.txt
```

条件:

* exact multiple-value syntax は Oracle help から取得する。
* repeated `--file` を、help evidence なしに仮定しない。
* original directory と original file がそれぞれ一度だけ exact argv に現れる。
* combined temporary directory、manifest、copy、ZIP を作らない。
* one Oracle execution、one control prompt。
* recovery call 0。

supported と判定する条件:

* Oracle evidence で両方の path が attachment input として受理されたことを確認できる。
* 一方だけの silent drop がない。
* argument order が deterministic。
* prompt submission は最大1回。

#### Characterization-4: direct continuation

ここでいう continuation は、**successful operation 後の ChatGPT conversation continuation** であり、現行 `_recover_same_session` の harvest ではない。

fixture:

1. short control prompt A を fresh conversation に送信。
2. Oracle が明示する continuation interface を用いて short control prompt B を同じ conversation に送信。

期待:

* initial submission: `1`
* continuation submission: `1`
* automatic retry: `0`
* harvest/capture: `0`
* wrapper/API: `0`
* logical model / target strategyを途中で変更しない。
* Oracle evidence から same conversation continuation と判断できる。
* report には conversation/session handle を保存しない。

以下では supported としない。

* `oracle session <id> --harvest` で既存回答を回収できただけ。
* URL、browser tab、private handleを人が目視して同一と推測しただけ。
* second prompt が新しい conversation へ送信された可能性を排除できない。
* continuation interface が help / stable evidence に存在しない。

#### Characterization-5: direct attachment failure

fixture:

* temporary root 内の、意図的に存在しない attachment path。
* short control prompt。
* exact direct attachment syntax。

期待:

* execution count: `1`
* automatic retry: `0`
* inline fallback: `0`
* harvest/capture: `0`
* response artifact: `0`
* promptSubmitted相当: `false` が明示されることが望ましい。
* failure stage: attachment submission と一意に分類できること。

次の場合は `attachment_failure_observable=unknown` とする。

* submission state が不明。
* reconstruction / model / attachment のどれで失敗したか区別できない。
* prompt が既に送信された可能性がある。
* session metadata を読むために 0.16.1 reader を 0.17へ流用する必要がある。

この live failure probe に current product adapter を使用しない。現行 adapter は stage-blind recovery により harvest を呼び得るため、Oracle 自体の attachment failure behavior を汚染する。

### 3.3 Green — 実測結果だけを最小反映

#### 全 capability が安全に観測できた場合

1. `_ROOT_CAPABILITIES` / `_SESSION_CAPABILITIES` を exact observed help surface に合わせる。
2. `_read_oracle_preflight_receipt` を追加し、raw stdoutを保持しない。
3. `_preflight_supported_oracle` の public behaviorを維持する。
4. unit fixtures を sanitized observed surface に更新する。
5. behavior receipt を `report.md` に記録する。
6. `SUPPORTED_ORACLE_VERSION` は `"0.16.1"` のままにする。
7. `invoke_issue_planning_chatgpt` の prompt-pack / one-file transport を維持する。
8. `_recover_same_session` の現行 argv と gate を維持する。
9. 0.17 production invocation は `blocked / oracle_capability_unsupported` のままにする。

#### capability が unsupported または unknown の場合

* flag や subcommand を推測しない。
* wrapper/API fallback を追加しない。
* directory を ZIP 化しない。
* required attachmentを落とさない。
* continuationを browser tab操作や private URLで補わない。
* production supportをenableしない。
* test は fail-closed behavior を固定する。
* `report.md` に gap と stop condition を記録する。
* `cl-s01-capability` を closed にしない。

---

## 4. 許可パスと変更禁止パス

### 4.1 許可された implementation / test paths

| 種別                             | Exact path                                                                                                                                                                                                                                                          | 許可内容                                                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| infra implementation           | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`                                                                                                                                                                          | `_ROOT_CAPABILITIES`, `_SESSION_CAPABILITIES` の実測整合、private preflight receipt、既存 preflight の最小 refactor |
| existing unit tests            | `tests/unit/infra/test_issue_planning_chatgpt.py`                                                                                                                                                                                                                   | 0.16.1 regression、unsupported invocation 0、preflight receipt tests                                      |
| optional dedicated test module | `tests/unit/infra/test_issue_planning_oracle_capability_characterization.py`                                                                                                                                                                                        | test-only behavior receipt schema、sanitized capability fixtures。live testを置く場合は opt-in / default skip   |
| brief artifact                 | `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s01-capability-characterization.md` | 本ブリーフの保存のみ                                                                                              |
| evidence destination           | 同 Issue の `report.md`                                                                                                                                                                                                                                               | orchestrator が実測後に content-free evidence を追記する。dev-coder の runtime変更範囲とは分離する                            |

専用 test moduleを追加しない場合は、全テストを既存 `test_issue_planning_chatgpt.py` に置く。上記二つ以外の test fileへ分散させない。

### 4.2 変更してはならない paths

#### Application / domain / CLI

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py`
* その他 application / domain / command modules

#### Artifact reader / profile work

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
* `tests/unit/infra/test_issue_planning_oracle_artifact.py`

0.16.1 artifact readerに0.17 fixtureを通す、version constantを書き換える、0.17 schemaを追加する作業は S01 の範囲外。

#### Resources / projection / shipped docs

* `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/`
* `spec-dock/scripts/spec_dock_runtime/`
* installed / dogfood projection
* operation resources
* workflow docs
* parent Epic文書
* README / templates

projection同期は S07。

#### Canonical Issue records

* `requirement.md`
* `design.md`
* `plan.md`
* `candidate-note.md`
* `.assurance.json`
* `decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md`
* historical reviews / Candidate files

`report.md` は実測 evidence の追記先に限る。仕様判断を変更する必要が生じた場合は、S01を停止し plan amendment / reviewへ戻す。

#### External boundary

* Oracle binary / wrapper source
* personal browser profile
* private configuration
* credentials
* target URL
* GitHub default branch
* OpenAI API integration
* CI configurationやdependency追加

S01 の delegation contractも、許可パスを `issue_planning_chatgpt.py`、`tests/unit/infra/`、brief artifactに限定し、application orchestration、generic recovery policy、Oracle wrapper、unrelated docsを禁止している。

---

## 5. 具体テストケース、fixture、spy、期待 call / status

### TC-S01-001 — Unsupported version / capability は invocation 0

**対象:** unit / fake Oracle

**Fixture:**

| Case                  | `--version` | root help                                              | session help        |
| --------------------- | ----------- | ------------------------------------------------------ | ------------------- |
| unknown patch         | `0.16.2`    | 未到達でも可                                                 | 未到達でも可              |
| pre-profile 0.17      | `0.17.0`    | characterization helperでは取得可、production preflightでは未対応 | 同左                  |
| missing root token    | `0.16.1`    | required tokenを一つ欠く                                    | valid               |
| missing session token | `0.16.1`    | valid                                                  | required tokenを一つ欠く |
| timeout / nonzero     | caseごとに発生   | —                                                      | —                   |

**Spies:**

* `subprocess.run` / `_run_oracle` call list
* `_recover_same_session`
* session directory existence
* wrapper/API sentinel

**期待:**

```text
status == "blocked"
reason == "oracle_capability_unsupported"
prompt calls == 0
harvest calls == 0
capture calls == 0
session directory == absent
personal wrapper/API calls == 0
```

version mismatch caseでは、production `_preflight_supported_oracle` が version call後に停止してよい。characterization用のhelp取得は別の明示操作とする。

---

### TC-S01-002 — Directory attachment capability

**対象:** direct PATH Oracle characterization + sanitized fixture test

**Fixture:**

* one benign temporary directory。
* one benign marker file。
* exact observed help surface。
* short control prompt case ID。raw promptはfixture/reportに保存しない。

**Spies / assertions:**

* resolved executableは PATH Oracleのみ。
* behavior execution `1`。
* original directory operand `1`。
* `_write_transport_pack` call `0`。
* tree traversal / copy / archive / generated manifest `0`。
* automatic retry / harvest / capture `0`。
* wrapper/API `0`。

**期待 receipt:**

```text
directory_attachment = supported
attachment_mode = direct
behavior_execution_count = 1
prompt_submission_count <= 1
```

attachment acceptance evidenceが曖昧なら:

```text
directory_attachment = unknown
```

process exit `0` だけで supported にしない。

---

### TC-S01-003 — Multiple original paths

**対象:** direct PATH Oracle characterization + sanitized fixture test

**Fixture:**

* `static-attachments/`
* `dynamic-evidence.txt`
* same short control prompt digest。
* exact Oracle-documented multiple path syntax。

**Spies / assertions:**

* directory path occurrence `1`。
* file path occurrence `1`。
* operand order deterministic。
* generated combined directory `0`。
* copy / ZIP / path filtering `0`。
* behavior execution `1`。
* prompt submission最大 `1`。
* recovery `0`。

**期待 receipt:**

```text
multiple_path_attachment = supported
required_path_count = 2
accepted_path_count = 2
attachment_drop_count = 0
```

片方しか受理されたことを証明できなければ `unknown` または `unsupported`。

---

### TC-S01-004 — Direct continuation

**対象:** direct PATH Oracle characterization

**Fixture:**

* explicit operation A: short control prompt A。
* explicit operation B: short control prompt B。
* Oracleが明示する exact continuation syntax。
* fresh disposable browser state。

**Spies / assertions:**

```text
initial explicit execution = 1
continuation explicit execution = 1
initial prompt submission = 1
continuation prompt submission = 1
automatic retry = 0
harvest = 0
capture = 0
wrapper/API = 0
```

**期待 receipt:**

```text
continuation = supported
same_conversation_verified = true
```

以下は禁止:

* `_recover_same_session` を continuation とみなす。
* `--harvest` の成功を conversation continuation の証拠にする。
* session / conversation handleをreportへ保存する。
* browser tabやprivate URLの目視だけで same conversationを主張する。

same-conversation evidenceを得られない場合:

```text
continuation = unknown
```

この場合は S02を開始しない。

---

### TC-S01-005 — Attachment failure behavior

**対象:** direct PATH Oracle characterization

**Fixture:**

* temporary root 内の nonexistent path。
* direct attachment syntax。
* short control prompt。

**Spies / assertions:**

```text
execution = 1
new execution retry = 0
inline retry = 0
harvest = 0
capture = 0
response artifact = 0
wrapper/API = 0
```

**安全に characterizable な期待:**

```text
failure_stage = attachment_submission
prompt_submitted = false
```

`prompt_submitted=None`、または stage が曖昧なら:

```text
attachment_failure_observable = unknown
```

S01では `oracle_attachment_submission_failed` を public reason に追加しない。production capability不足の public pairは既存どおり:

```text
blocked / oracle_capability_unsupported
```

---

### TC-S01-006 — Existing 0.16.1 successful path

**対象:** unit / existing fake Oracle

既存 `test_path_oracle_direct_argv_environment_and_planner_snapshot` を保持・強化する。

**期待 exact argv properties:**

```text
--engine browser
--model Pro
--browser-model-strategy select
--remote-chrome 127.0.0.1:<port>
--browser-no-cookie-sync
--wait
--browser-attachments always
--slug <generated-id>
--prompt <exact-string>
--file <generated-prompt-pack>
```

**期待:**

```text
status == "pass"
reason == "transport_received"
prompt calls == 1
file operands == 1
shell == false
stdin == DEVNULL
wrapper/API == 0
```

この test が original path direct transport を期待するよう変更してはならない。

---

### TC-S01-007 — Existing 0.16.1 stage-blind recovery

**対象:** unit / fake Oracle

**Fixture A:**

* prompt process timeout。
* session status `running`。
* harvest後に completed ZIPが出現。

**期待:**

```text
prompt calls == 1
harvest calls == 1
exact harvest argv == [oracle, "session", session_id, "--harvest", "--no-recover"]
status == "pass"
reason == "transport_received"
```

**Fixture B:**

* prompt process nonzeroまたはtimeout。
* same-session stateがterminalにならない。

**期待:**

```text
prompt calls == 1
harvest calls == 1
status == "blocked"
reason == "oracle_session_recovery_required"
```

この挙動の修正、`promptSubmitted` guard、profile-owned builderへの移動は S09–S10。

---

### TC-S01-008 — 0.17 characterization と production enablement の分離

**対象:** unit / fake Oracle

**Fixture:**

* version `0.17.0`
* positiveな sanitized behavior receipt

**期待:**

* characterization receipt自体は `supported` statesを保持できる。
* production `invoke_issue_planning_chatgpt` は S09前なので:

```text
status == "blocked"
reason == "oracle_capability_unsupported"
prompt calls == 0
recovery calls == 0
```

この testにより「capability観測済み」と「profile登録済み」を分離する。

---

### TC-S01-009 — Content-free receipt schema

**対象:** unit

receipt serializerまたはreport projection helperを置く場合、許可 key を closed にする。

**許可 key:**

```text
receipt_schema
source_kind
baseline_head
oracle_version
current_runtime_supported
root_help_exit
session_help_exit
missing_root_capabilities
missing_session_capabilities
directory_attachment
multiple_path_attachment
continuation
same_conversation_verified
attachment_failure_observable
prompt_submission_count
behavior_execution_count
harvest_count
capture_count
wrapper_count
api_count
test_case_ids
command_surface_sha256
result
```

**禁止 key / value:**

```text
prompt
prompt_text
transcript
stdout
stderr
credential
cookie
token
url
target_url
browser_endpoint
session_id
session_handle
conversation_handle
absolute_path
oracle_home
environment
```

禁止 key が存在した場合は receipt生成を失敗させる。値の文字列 scanだけに依存せず、schemaをclosedにする。

---

## 6. `report.md` への content-free capability evidence の記録

### 6.1 Evidence source を分離する

少なくとも次の二種類を別 entry として記録する。

| `source_role`                         | 意味                                                          |
| ------------------------------------- | ----------------------------------------------------------- |
| `repository_fixture_characterization` | committed fake Oracle testsによる0.16.1 regression evidence    |
| `direct_path_oracle_characterization` | PATH-resolved Oracle本体のlive observation                     |
| `external_local_observation`          | historical personal wrapper evidence。direct evidenceの代替にしない |

wrapper observation を `direct_path_oracle_characterization` として採用してはならない。

### 6.2 推奨 capability receipt

`report.md` の S01 session logに、次のような content-free tableを追記する。

```md
#### S01 Capability Receipt

| Field | Observed value |
|---|---|
| receipt_schema | `s01-oracle-capability-v1` |
| source_role | `direct_path_oracle_characterization` |
| baseline_head | `6561f0b16cb5ba12d54ba262c3baf86340236c00` |
| observed_worktree_head | `<実行時HEAD>` |
| oracle_version | `<exact observed version>` |
| executable_source | `PATH` |
| executable_identity_rechecked | `true|false` |
| root_help_exit | `<integer>` |
| session_help_exit | `<integer>` |
| command_surface_sha256 | `<sanitized surface digest>` |
| directory_attachment | `supported|unsupported|unknown` |
| multiple_path_attachment | `supported|unsupported|unknown` |
| continuation | `supported|unsupported|unknown` |
| same_conversation_verified | `true|false|unknown` |
| attachment_failure_observable | `supported|unsupported|unknown` |
| prompt_submission_count | `<integer>` |
| behavior_execution_count | `<integer>` |
| harvest_count | `0` |
| capture_count | `0` |
| wrapper_count | `0` |
| api_count | `0` |
| requested_brief_model | `GPT-5.6 Luna / Max` |
| observed_runtime_model | `unverified` |
| result | `pass|blocked` |
```

`command_surface_sha256` は、option names / subcommand namesだけを正規化した content-free surface の digest とする。prompt、paths、endpoint、session handleを含む argv 全体の digestにはしない。

### 6.3 Report sectionへの反映

実測後、orchestrator が次を更新する。

1. **Evidence Adoption Ledger**

   * source
   * source role
   * capability claim
   * adopted / rejected / blocked
   * evidence strength
   * blocking
   * next action

2. **TDD / Red / Green / Refactor Evidence**

   * S01 Red tests
   * direct characterization
   * Green変更または no-op
   * test result

3. **Step Contract Closure**

   * `cl-s01-capability`
   * capability receiptへの参照
   * `pass` または `blocked`

4. **Test Contract Closure**

   * `tc-s01-001`〜`tc-s01-009`
   * command
   * call count
   * result

5. **Reviewer Gate Status**

   * 実装後の actual reviewer evidence が存在する場合だけ更新する。
   * brief自体を reviewer PASS として記録しない。

6. **Decision Ledger**

   * actual Oracle surfaceがapproved designの仮定と materially異なる場合だけentryを追加する。
   * 単なる observed version / help tokenはDecision Ledgerではなく capability receiptへ記録する。

### 6.4 保存禁止情報

`report.md`、test fixture、commit messageに次を含めない。

* prompt本文または再構成されたprompt
* Oracle transcript
* ChatGPT response本文
* credentials、cookies、tokens
* raw target URL
* managed Chrome endpoint
* session slug / handle
* conversation handle
* Oracle home
* executable absolute path
* private attachment path
* raw stdout / stderr
* private config
* browser profile location

prompt correlation が必要なら、`prompt_case_id`、UTF-8 byte length、SHA-256のみを使用する。

---

## 7. 検証コマンドと期待証跡

### 7.1 Focused unit tests

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_capability_characterization.py \
  -q
```

専用test moduleを追加しない場合:

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
```

期待証跡:

* 全test exit `0`。
* unsupported version / capabilityでprompt `0`。
* 0.17 product invocationでprompt `0`。
* 0.16.1 successでprompt `1`。
* 0.16.1 recovery fixtureでharvest `1`。
* wrapper/API `0`。
* receipt privacy tests pass。

### 7.2 Infra regression

```bash
uv run pytest tests/unit/infra -k 'issue_planning and (oracle or session or capability)' -q
```

期待証跡:

* 0.16.1 artifact reader regressionが壊れていない。
* exact repository failure、ZIP / JSON strictnessが維持される。
* S01変更がartifact readerへ波及していない。

### 7.3 Static checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_capability_characterization.py
```

専用test moduleがない場合はその引数を除く。

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

```bash
git diff --check
```

期待証跡:

* lint / type check / diff check exit `0`。
* public/domain type変更なし。
* unused characterization production APIなし。

### 7.4 Allowed-path audit

```bash
git diff --name-only 6561f0b16cb5ba12d54ba262c3baf86340236c00 --
```

許可される出力は次のsubsetのみ。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_capability_characterization.py
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s01-capability-characterization.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md
```

`report.md` は orchestrator evidence appendだけを許可する。

### 7.5 Direct PATH Oracle command-surface verification

```bash
command -v oracle
oracle --version
oracle --help
oracle session --help
```

期待証跡:

* executable sourceはPATH。
* exact versionを取得。
* help commands exit `0`。
* relevant option / subcommand surfaceを抽出。
* raw outputはcommitしない。
* personal wrapper / API invocationなし。

directory、multiple path、continuation の behavior commandはここでは事前記載しない。**同一 binary のhelpから確定した exact syntaxだけを使うこと**。placeholderや推測したflagを実行する必要がある場合はcharacterizationを停止する。

---

## 8. リスク、不確実性、S02を止める条件

### 8.1 主要リスク

#### Current HEAD review binding

current branch tip `6561f0b1...` に対し、repository内のlast reviewed HEAD記録は `079685b2...` である。これは brief生成を妨げないが、workflowがcurrent-head reviewを実装開始条件とする場合、product-code変更前の独立gateとなる。

#### Help token と behavior capability の混同

`--file` がhelpに存在しても、directory attachmentまたはmultiple pathを保証しない。help tokenだけでbehavior supportedとしない。

#### Continuation と harvest の混同

現行 `oracle session <id> --harvest --no-recover` はsame-session output recoveryであり、cross-operation conversation continuationではない。これを continuation evidence とすると S06 の前提を誤る。

#### Current adapter による evidence contamination

現行 adapterはnonzero / timeout / nonterminalでstage-blind harvestを呼ぶ。attachment failure characterizationにproduct adapterを使うと、Oracle本体のpre-submit behaviorを正確に観測できない。

#### 0.17 artifact schema の誤読

0.16.1 readerはexact-version fail-closedである。0.17 sessionへ定数差替えで適用してはならない。

#### Browser state dependence

overlay、login state、target kind、UI readinessにより結果が変動する可能性がある。supported判定には、一回の偶然の成功ではなく、少なくとも同じclean-state条件で再現できるreceiptを要求する。

#### Sensitive evidence leakage

raw stdout、session metadata、paths、endpoint、target URLをreportへ貼るとprivacy boundaryを破る。receiptはclosed content-free schemaに限定する。

#### Model evidence confusion

requested brief target `GPT-5.6 Luna / Max`、logical product selector `Pro`、historical observed labelsは別概念である。S01 capability receiptにmodel successを混ぜない。

### 8.2 S02 を開始してはならない条件

次のいずれかが成立する場合、`cl-s01-capability` を閉じず、S02へ進まない。

1. GitHub上の指定branchと実装baseline HEADが一致しない。
2. workflow上必要なcurrent-HEAD review / authorization gateが未解決。
3. directory attachmentが `supported` にならない。
4. multiple original pathsが `supported` にならない。
5. direct continuationが `supported` にならない。
6. continuationがsame conversationであることをcontent-free evidenceで検証できない。
7. capability supportにundocumented flagの推測が必要。
8. capability supportにpersonal wrapper、API、alternate backend、default branchが必要。
9. directory / multiple path supportにSpecDock側のcopy、ZIP、manifest、materializationが必要。
10. required attachmentの一部をdropしなければ成功しない。
11. attachment failure behaviorがOracle本体ではなくcurrent stage-blind recoveryにより汚染されている。
12. 0.16.1 regression testsが失敗する。
13. unsupported capability fixtureでpromptまたはrecovery callが1回以上発生する。
14. receiptにprompt、transcript、URL、handle、credentials、private pathが含まれる。
    15.変更にapplication/domain/CLI/artifact reader/projectionなど許可外pathが必要。
15. direct PATH Oracle evidenceとexternal wrapper evidenceを分離できない。
16. test fixtureのOracle surfaceがlive observed surfaceと一致しない。

attachment failure classificationが `unknown` の場合も、S01 の required characterization evidenceが未閉鎖であるため、現行planの順序ではS02を開始しない。仕様上S02のresource設計自体が技術的に独立していても、approved milestone gateを実装者判断で緩和しない。

### 8.3 S01 完了判定

S01を閉じられるのは、次をすべて満たした場合だけである。

```text
exact source preflight                         = pass
directory attachment                           = supported
multiple original paths                        = supported
direct continuation                            = supported
same conversation continuation evidence        = verified
attachment failure behavior                    = characterized
unsupported capability prompt calls            = 0
unsupported capability recovery calls          = 0
personal wrapper/API calls                     = 0
Oracle 0.16.1 regression                       = pass
Oracle 0.17 production enablement before S09   = 0
content-free report receipt                    = recorded
allowed-path audit                             = pass
```

満たさない場合の成果物は「失敗」ではなく、**再現可能な capability gap と stop decision**である。unsupportedまたはunknownを推測でsupportedへ変換せず、S02を保留する。
