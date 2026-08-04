# 1. レビュー対象 identity

| 項目                                    | 確認結果                                                                  |
| ------------------------------------- | --------------------------------------------------------------------- |
| Repository                            | `chemitaro/spec-dock`                                                 |
| Branch                                | `codex/iss-00354-chatgpt-context-contract`                            |
| 要求 source HEAD                        | `91781cf507f979b02ba3ceb0a0610f2815114ec8`                            |
| GitHub branch tip                     | `91781cf507f979b02ba3ceb0a0610f2815114ec8`                            |
| GitHub exact comparison               | `identical` / ahead `0` / behind `0`                                  |
| Default branch fallback               | 使用していない                                                               |
| Runtime implementation                | `836a9c7372879747a24b7785e9484a9e9dfc2f3b`                            |
| Input-spy repair / v2 artifact        | `0586f151407ff95aeb4ef8b72d18a019b5d7a1a8`                            |
| Current report update / review source | `91781cf507f979b02ba3ceb0a0610f2815114ec8`                            |
| Freshness                             | v1/v2とは別の新規・独立したFresh review。過去 verdict は継承せず、解消確認にのみ使用               |
| Mutation                              | なし。repository、canonical docs、tests、report、review artifacts、添付を変更していない |
| 確認時点                                  | 2026-08-05 JST                                                        |

GitHub connectorで指定branchを再確認した結果、レビュー終了時点でも要求SHAとbranch tipは一致していた。current commitは、v2 FAIL、closure ID、実装HEADとreview HEADの区別、必須コマンド証跡をreportへ反映するreport-only更新である。

判定のrepository authorityはGitHub exact HEADとした。添付bundleは補助照合にのみ使用した。
別添の例外・failure taxonomy資料はS03/S04契約とは別テーマであり、finding根拠には使用していない。

# 2. 判定

# **FAIL**

| Severity | 件数 |
| -------- | -: |
| P0       |  0 |
| P1       |  1 |
| P2       |  0 |
| P3       |  0 |

現行production実装にinput materializationは確認されなかった。しかし、repository-relative operandと`cwd=repo_root`の結合を必須spy付きで実行するtestがなく、承認済みtransport contractの将来回帰を検出できないため、`cl-s04-direct-transport`のclosure evidenceとしては不足している。

# 3. Finding table

| ID                     | Severity | File / line または symbol                                                                                                                                                                                                                                                                      | 事実                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 最小修正方向                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S03S04-V3-001` | P1       | `tests/unit/infra/test_issue_planning_chatgpt.py:1288-1551` — `test_direct_file_operands_preserve_order_and_do_not_materialize_pack`, `test_s04_direct_transport_accepts_path_only_synthesized_input`; `tests/integration/test_issue_planning_e2e.py::_assert_oracle_submission`, `_invoke` | v2で追加されたread/open/tree/copy/ZIP/hash guardは、実際にinfraを呼ぶtestでは`tmp_path / ...`の**absolute pathだけ**を入力としている。隣接するrepository-relative path testは`SynthesizedPlanningPrompt`を構築するだけでinfraを呼ばない。さらにfull-chain e2eは外側のCLIを`cwd=target`で起動する一方、fake Oracleが記録した`cwd`をassertしていない。このため、例えば`if not path.is_absolute(): (repo_root / path).read_bytes()`というrepository-relative inputだけの再materialization、またはOracle subprocessから明示的な`cwd=repo_root`を削除する回帰が、現行S03/S04 test setを通過し得る。production本体は現在、repository-relative `Path`を保持し、各pathを直接`--file`へ追加し、Oracleを`cwd=repo_root`で起動しており正しい。欠陥はその結合を固定する必須回帰証跡の不足である。 | 既存のdirect-transport spy testをtest-onlyで補正し、少なくとも①absolute static attachment directory、②original external absolute Candidate path、③lexical repository-relative source pathを同一invocationへ渡す。guardはrelative operand自体と`repo_root / relative`の双方を入力aliasとして拒否し、submit argvにはrelative文字列がそのまま残ること、prompt subprocessの`cwd`がexact `repo_root`であることをassertする。既存のoutput-only artifact hash/copy許可は維持する。追加testが実違反を検出しない限りproduction変更は不要。 |

## Findingの再現可能性

現在のspy testは、実際にinfraを呼ぶ際の入力を次の形に固定している。

```python
paths = (
    tmp_path / "attachments",
    tmp_path / "candidate.zip",
    tmp_path / "source.md",
)
```

すべてabsolute pathである。一方、実際のPlanning/Git-bound Reviewではcanonical sourceが`Path("spec-dock/...")`のようなrepository-relative operandになる。current productionはこれを正しく扱うが、次のような回帰はabsolute-only testでは分岐に入らない。

```python
if not attachment_path.is_absolute():
    (repo_root / attachment_path).read_bytes()
```

同様に、current e2eの親processは最初からrepository rootを`cwd`としているため、infraがOracle subprocessの明示`cwd=repo_root`を誤って削除しても、継承されたcwdによってtestが成功し得る。fake Oracleはcwdを記録しているが、現行assertionはその値を検査していない。

なお、v2 repairが追加したAPI guard自体と、output-only stagingの分離は確認できた。`Path.read_bytes/open`、builtin `open`、`os.scandir/listdir`、copy系、`ZipFile`、`sha256`がguardされ、artifact reader・typed output側の正規hash処理は別経路へ退避されている。したがって、V3-001は「API spyがない」というv2 findingの単純再掲ではなく、**実際のmixed lexical-path contractをspy付きで通していない**という残存範囲である。

# 4. v1/v2 findingごとの解消確認

| 既存finding                                                                      | v3確認結果             | 根拠                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S03S04-CODE-001` — repository-relative pathをroot-prefix化               | **解消済み**           | Provider promptの`_source_attachment_paths`とapplicationの`_context_source_operands`は`Path(relative)`を返す。Candidate、Review、revision requestは元の`Path` objectを保持する。current infraは文字列化だけを行い、`cwd=repo_root`でOracleを実行する。                                                   |
| `RT-354-S03S04-CODE-002` — provider/projection byte parity                     | **解消済み**           | Exact HEADでprovider/projectionのGit blob SHAが四組とも一致する。Prompt=`6e009946...`、application=`e81f4ebe...`、infra=`4a9ce078...`、Review resource=`bf77b4cb...`。Review resourceもminimal bodyのidentity/digestを参照している。                                                          |
| `RT-354-S03S04-CODE-003` — mandatory no-inspection/no-materialization matrix   | **部分解消／V3-001へ継続** | Opaque directoryのnested/hidden/symlink/FIFO、application側relative pathのread/resolve/stat/tree guards、external `Path` identity、infra側read/open/copy/ZIP/hash guardsは追加済み。ただしinfra spy invocationがabsolute-onlyで、repository-relative operandとexplicit cwdの結合を固定できていない。 |
| `RT-354-S03S04-CODE-004` — report implementation/closure evidence              | **解消済み**           | Reportはruntime `836a9c...`、test repair `0586f151...`、review sourceの区別、test件数、legacy zero-match、provider update/parity、validate、scope audit、diff-checkを記録し、closureとS05をpendingのまま維持している。                                                                             |
| `RT-354-S03S04-V2-001` — input-side read/open/copy/ZIP/hash spy不足              | **部分解消／V3-001へ継続** | 指摘されたAPI guardは追加され、output-only stagingからも分離された。ただしrepository-relative operandを実際にinfraへ渡すspy付きcaseがなく、path-shape固有の回帰を検出できない。                                                                                                                                      |
| `RT-354-S03S04-V2-002` — report current-state、closure ID、HEAD distinction、必須証跡 | **解消済み**           | `EAL-019`、canonical `cl-s04-direct-transport`、implementation/test/report/review identityの区分、exact commandsとexit code、provider update/parity、legacy zero-match、scope auditがcurrent reportに存在する。S03/S04はpending review、S05は未開始で、PASSやclosureを先取りしていない。                |

# 5. Scope逸脱、未検証、残るリスク

## Scope逸脱

**S03/S04 union allowlistを越えるproduction変更は確認されなかった。**

GitHub commit comparisonでは、S03/S04 runtime修正はprovider runtime三ファイル、Review resource、対応projection、指定unit/integration testsおよびevidence filesに限定されている。v2 repair以降はinfra unit test、v2 review artifact、reportのみであり、current `91781cf...` はreport-only更新である。

次の変更は確認されなかった。

* `domain/issue_planning_contracts.py`
* CLI / commands
* Oracle profile、stage、recovery policy
* Oracle artifact reader
* ZIP / Review JSON validators
* requirement / design / plan
* S05以降の実装
* compatibility bridge、inline fallback、generated input pack、attachment drop、alternate backend

Review resourceのprovider/projectionは同一bytesで、generated identity attachmentではなくminimal bodyの`Reviewed identity`とdigestを参照している。

## 未検証

* このFresh reviewではrepository checkout上の`pytest`、`ruff`、`mypy`、`spec-dock validate`、provider update、`cmp`を独立再実行していない。
* current exact HEADにはGitHub combined status contextがなく、PR-triggered workflow runも取得できなかった。
* Report記載の`93 passed`、全体`1472 passed / 2252 skipped`、domain `88 passed`、full-regression `11 passed`、validate/update/parity等はBlue Teamの実行証跡であり、本reviewの独立実行結果ではない。
* PATH Oracleの実browser upload、Oracle `0.17.0` profile、submission evidence、recovery behaviorはS03/S04 review範囲外であり、PASSを主張しない。
* GPT-5.6 Luna / Reasoning Effort Maxの実測証跡は確認しておらず、主張しない。

## 残るリスク

* Current production sourceは、path-only producer、lexical repository-relative operand、direct repeated `--file`、`cwd=repo_root`、output-only stagingという承認済み実装に静的には整合している。
* ただしV3-001により、relative-path固有のinput read/hash/copy回帰またはexplicit cwd削除がclosure suiteを通過し得る。
* 現行`0.16.1`のstage-blind same-session recoveryは残っているが、S09/S10の明示責務であり、本レビューのfindingではない。
* Reportは`cl-s03-path-input`と`cl-s04-direct-transport`を同時pendingとし、S05、PR、merge、Issue closeを開始していない。この境界自体は正しい。

# 6. Blue Teamの最小アクション

1. `tests/unit/infra/test_issue_planning_chatgpt.py::test_direct_file_operands_preserve_order_and_do_not_materialize_pack`だけを最小補正し、absolute static directory、absolute external Candidate、lexical repository-relative source pathのmixed tupleを実際にinfraへ渡す。
2. 同testで、relative operand自体と`repo_root / relative`の双方にread/open/tree/copy/ZIP/hash guardを適用し、submit argvのrelative文字列保持とprompt subprocessの`cwd == repo_root`をassertする。現在のoutput-only artifact staging/hash許可は変更しない。
3. Focused suite、full-chain e2e、validate、parity、scope auditを再実行し、test修正とreport evidenceを一つの新しいpushed exact HEADへ束ねる。
4. そのexact HEADを別のFresh Red Team reviewへ渡す。P0/P1が0になるまで、`cl-s03-path-input`、`cl-s04-direct-transport`をcloseせず、S05へ進めない。
