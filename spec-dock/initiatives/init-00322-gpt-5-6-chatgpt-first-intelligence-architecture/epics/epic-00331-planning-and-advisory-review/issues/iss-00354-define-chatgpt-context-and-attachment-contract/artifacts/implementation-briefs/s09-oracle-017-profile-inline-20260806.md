# iss-00354 S09 実装ブリーフ追補 — Oracle 0.17.0 inline text capability binding

## 1. Identity and implementation gate

| 項目                      | 確認値                                                          |
| ----------------------- | ------------------------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                                        |
| Named branch            | `codex/iss-00354-chatgpt-context-contract`                   |
| Current pushed HEAD     | `647df1861298ad929d8ee4cbddb324a00cd11b9e`                   |
| Branch equality         | named branch と exact HEAD は `identical`、ahead `0`、behind `0` |
| Default branch fallback | 使用していない                                                      |
| S09判断                   | **実装開始可**。ただしclosureは未成立                                     |

Current HEADでは、private exact-version profile、0.16.1 browser/session builders、profile-owned reader、exact help-token検査、unknown-version fail-closedまでは実装済みである。一方、registryとartifact readerはまだexact `0.16.1`だけを登録しており、`0.17.0` profile/readerは未実装である。

GitHub current HEADにはnative rerun receiptが存在するが、今回のinline receiptは添付された追加証跡である。実装入力には使用できるが、S09 closure前にreceipt本体とreportのEAL-068相当をrepositoryへ束縛すること。

---

## 2. Inline capability decision

### 結論

Exact `0.17.0` profileの

```text
inline_mode_characterized = true
```

は、**inline-compatible text file 1件に限定したcapability declarationとして採用可能**である。

根拠は、`--browser-attachments never`と一つのtext attachmentで、`promptSubmitted=true`、`response-complete=true`、top-level `status=completed`、validated ZIPまで同一runで観測されたことである。成果物はlogical filename `oracle-017-attachment-characterization.zip`、internal root `oracle-017-attachment-characterization`、size `483`、SHA-256 `9566748c79c49e5369d36fff3c76d2cb65250dc281fdaca563c5c0be3bd827a2`である。

### 制約

`true`の意味を次に限定する。

```text
Oracle 0.17.0には、観測済みのinline-compatible text fileを
--browser-attachments neverで送信できるcharacterized pathが存在する
```

次の意味へ拡張してはならない。

* 任意のfile type、directory、ZIP、binary fileがinline-compatibleである。
* attachment pathの拡張子、内容、MIME typeをSpecDockが検査・分類してよい。
* `inline_mode_characterized=true`だけで自動fallbackを実行してよい。
* `--browser-attachments never`を全attachmentに対するprimary policyとして使用してよい。
* `--browser-attachments always`が成功済みである。

Current profile codeはこのbooleanをcompleteness確認にだけ使用し、inline executionをまだ選択しないため、S09でscopeを限定した`true`を記録してもruntime behaviorは一般化されない。

Inline runのmodel strategyは`current`、selector evidenceは`verified=false`である。このrunをmodel compatibility証跡へ昇格しない。0.17 profileのmodel policyは、別のnative rerunで観測済みの`gpt-5.6`、`select`、observed `GPT-5.6 Sol`、verified `true`の証跡と分離して維持する。

---

## 3. Stage decoder decision

Exact `0.17.0` stage decoderは、artifact/session metadataのtop-level `status`だけを入力にする。

```text
status == "completed"  -> terminal
missing                -> invalid/missing reader result
non-string             -> invalid
empty string           -> invalid
other string           -> invalid
```

`running`、`pending`等をcharacterized nonterminal statusとして推測登録しない。

`promptSubmitted`、model selection strategy、model verified flag、observed model labelはbrowser runtime receiptであり、artifact metadataの`status`へ混ぜない。したがってinline runが`verified=false`でも、validated artifactの`status=completed`はterminal artifact stateとして扱える。逆に、`status=completed`だけからmodel verifiedまたはprompt submissionを推測してはならない。

Current readerはtop-level `status`を文字列として取得し、profileのdecoderへ渡す構造を既に持つため、0.17専用decoderを追加するだけでよい。

---

## 4. Harvest / capture builder decision

### 結論

Exact `0.17.0` profileでは、観測済みの次のcommandを一つのbuilderとして実装し、harvestとcaptureの両semantic fieldへ**同じbuilder object**をbindしてよい。

```text
<oracle executable>
session
<session id>
--harvest
--no-recover
```

Required binding:

```python
profile.harvest_argv_builder is profile.capture_argv_builder
```

Native rerunでは、このcommandにより同じresponseと同じZIP artifact identityが再取得されている。canonical planも、harvestとcaptureが同じcommandである場合は、同じcharacterized builderを両fieldへ明示bindすることを許容している。

### 境界

独立したcapture optionは追加しない。

独立したartifact-pending stateは未観測であるため、S09で次を主張しない。

* pending artifactをこのcommandがdownloadedへ遷移させる。
* response-complete後のcapture invocation条件が確定した。
* capture recoveryのruntime call countが検証済みである。

S09で閉じるのは**exact command identityとprofile ownership**だけである。Artifact-pendingの検出およびbuilder呼出し判断は、未検証事項として後続のstage-specific gateへ残す。添付reportも、same-builder bindingは実装対象としつつ、artifact-pending stateと個別capture optionを成功扱いしない境界を記録している。

---

## 5. Artifact reader update

Exact `0.17.0` readerは、観測済みのcore schemaだけに依存する。

Top-level:

```text
id
status
mode
artifacts
```

File artifact:

```text
kind
path
sizeBytes
sha256
validation.ok
```

`transfer`、`origin`等の追加fieldは存在してもよいが、path、identity、size、SHA、validation authorityとして使用しない。

Current readerは必要なcore fieldだけを取得し、contained path、regular file、size、SHA、`validation.ok`、staging rehash、ZIP safetyを検査している。そのため0.17 readerでも追加fieldを無視して安全に処理できる。追加fieldが不正なcore fieldを救済することは許可しない。

実装は単一定数を`0.17.0`へ置換せず、exact reader registryに次の二つを個別登録する。

```text
0.16.1 -> existing behavior
0.17.0 -> observed common core schema
other  -> reject
```

---

## 6. Minimal implementation allowlist

### Production

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

### Tests

```text
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
```

### Evidence-only after verification

```text
spec-dock/.../iss-00354-define-chatgpt-context-and-attachment-contract/
  artifacts/characterization/s09-oracle-017-native-inline-20260806.md
  report.md
```

### Required production delta

`issue_planning_chatgpt.py`:

1. Exact `0.17.0` profileを追加する。
2. `inline_mode_characterized=True`をtext-only observationとしてbindする。
3. 別native rerunで確定した`select` model policyを維持し、inline runの`current`を採用しない。
4. Exact `status=completed`専用decoderを追加する。
5. Exact 0.17 session builderを追加し、harvest/captureへ同じobjectをbindする。
6. Generic recovery helperへcommand literalを戻さない。

`issue_planning_oracle_artifact.py`:

1. Exact `0.17.0` reader registrationを追加する。
2. 0.16.1 reader behaviorを変更しない。
3. 0.17 core schemaを読み、追加`transfer`/`origin`を無視する。
4. Unknown version、wrong session、wrong mode、invalid status、size/SHA/validation defectをfail-closedにする。

---

## 7. Minimal focused tests

### `test_issue_planning_chatgpt.py`

* Registryがexact `0.16.1`と`0.17.0`だけを受理する。
* `0.17.1`、`0.18.0`、malformed versionはhelp、prompt、harvest、captureを各0回にする。
* Existing 0.16.1 browser argvとsession argvが完全一致で維持される。
* 0.17 profileは`inline_mode_characterized is True`。
* Inline receiptによりprimary model strategyが`current`へ変わらない。
* 0.17 decoderは`completed`だけをterminalとし、missing、non-string、unknown stringをrejectする。
* 0.17 harvest/captureは同じbuilder objectである。
* 0.17 same-session builderはexact observed argvだけを返す。
* `_recover_same_session`はselected profileのbuilderを一回呼び、generic commandを再構築しない。
* S09 runtime pathではcapture builder call countは0。

### `test_issue_planning_oracle_artifact.py`

* Reader registryがexact `0.16.1`と`0.17.0`だけを受理する。
* 0.17 completed ZIP fixtureをsnapshotできる。
* `transfer`と`origin`の存在を許容する。
* `transfer`/`origin`がinvalid path、wrong size、wrong SHA、`validation.ok=false`を上書きできない。
* Missing/non-string/unknown `status`をrejectする。
* Existing 0.16.1 fixturesとZIP safety testsが無変更でpassする。

Current testsは0.17.0をunsupportedとして固定しているため、そのfixtureをexact `0.17.1`等へ移し、0.17.0 success testsを追加する。

---

## 8. Verification commands

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py -q
```

```bash
uv run pytest \
  tests/unit/infra \
  -k 'oracle and (artifact or session or profile)' -q
```

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra \
  tests/unit/infra
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra
```

```bash
git diff --check
git diff --name-only 647df1861298ad929d8ee4cbddb324a00cd11b9e...HEAD
```

---

## 9. Stop and closure conditions

### Stop

次のいずれかでは実装を停止する。

* `inline_mode_characterized=True`を任意file typeの許可として扱う必要がある。
* file suffix、content、MIME、directory entriesの検査が必要になる。
* Inline runの`current / verified=false`をmodel successとして採用する必要がある。
* `--browser-attachments always`の送信前failureをsuccessへ変換する必要がある。
* 独立capture optionまたは未観測statusを発明する必要がある。
* Unknown patchまたはsemver rangeを受理する必要がある。
* 0.16.1 argvまたはreader behaviorを変更する必要がある。
* Allowlist外production/test変更が必要になる。

### S09 closure

次をすべて満たすこと。

* Exact `0.17.0` profileとreaderが登録される。
* `inline_mode_characterized=True`がtext-only evidenceとして記録される。
* Inline runのmodel evidenceは`current / verified=false`のまま非採用である。
* Separate `select` rerunのmodel evidenceとの混同がない。
* `status=completed`だけがterminalである。
* Harvest/captureが同じexact builder objectを所有する。
* Independent artifact-pending recoveryを完了済みと主張しない。
* 0.16.1 exact regressionがpassする。
* Unknown versionがfail-closedになる。
* Focused pytest、Ruff、Mypy、diff-checkがpassする。
* Inline receiptとreport EALのpath、bytes、SHA-256が一致する。
* Attachment-always failure、任意file type inline、未検証model、独立capture optionの成功claimが0件である。
