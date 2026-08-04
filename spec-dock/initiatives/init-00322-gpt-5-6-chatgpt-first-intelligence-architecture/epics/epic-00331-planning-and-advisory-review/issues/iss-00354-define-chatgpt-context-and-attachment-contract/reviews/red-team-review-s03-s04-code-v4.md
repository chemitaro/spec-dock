# 1. レビュー対象 identity

| 項目                                | 確認結果                                                                          |
| --------------------------------- | ----------------------------------------------------------------------------- |
| Repository                        | `chemitaro/spec-dock`                                                         |
| Branch                            | `codex/iss-00354-chatgpt-context-contract`                                    |
| Source HEAD                       | `150d81a3e1a98e1f3e9776743e8376c28a7c7184`                                    |
| GitHub branch tip                 | `150d81a3e1a98e1f3e9776743e8376c28a7c7184`                                    |
| GitHub exact comparison           | `identical` / ahead `0` / behind `0`                                          |
| Default branch fallback           | 使用していない                                                                       |
| Runtime implementation baseline   | `836a9c7372879747a24b7785e9484a9e9dfc2f3b`                                    |
| Input-side spy repair             | `0586f151407ff95aeb4ef8b72d18a019b5d7a1a8`                                    |
| v3 review source                  | `91781cf507f979b02ba3ceb0a0610f2815114ec8`                                    |
| v3 repair / current review source | `150d81a3e1a98e1f3e9776743e8376c28a7c7184`                                    |
| Freshness                         | v1/v2/v3とは別のFresh v4。過去の判定は継承せず、findingの解消確認にのみ使用                             |
| Mutation                          | なし。repository、canonical docs、runtime、tests、report、review artifacts、添付を変更していない |

GitHub connectorでnamed branchの存在と要求SHAとの完全一致を確認した。current commitは、mixed path / explicit cwdのtest修正、v3 review、repair brief、report更新を含み、production runtimeは変更しない旨を明記している。

判定のrepository authorityはGitHub exact HEADとし、添付bundleは補助照合にのみ使用した。 別添の例外・failure taxonomy資料はS03/S04とは別テーマであり、finding根拠から除外した。

# 2. 判定

# **FAIL**

| Severity | 件数 |
| -------- | -: |
| P0       |  0 |
| P1       |  2 |
| P2       |  0 |
| P3       |  0 |

P1が2件残るため、`cl-s03-path-input` / `cl-s04-direct-transport` のatomic closureは成立しない。

# 3. Finding table

| ID                     | Severity | File / line または symbol                                                                                                               | 事実                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 最小修正方向                                                                                                                                                                                                                                                                                                         |
| ---------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S03S04-V4-001` | P1       | `tests/unit/infra/test_issue_planning_chatgpt.py:1288-1544` — `test_direct_file_operands_preserve_order_and_do_not_materialize_pack` | v3 repair contractは、①absolute static directory、②**repository外のoriginal external absolute Candidate**、③lexical repository-relative source pathを同じinfra invocationへ渡すことを要求していた。しかしcurrent testは、`repo_root=tmp_path`に対してCandidateも`tmp_path / "candidate.zip"`としている。したがってCandidateはabsoluteではあるがrepository root内であり、external pathではない。  repair briefは明示的に`repo_root = tmp_path / "repo"`とし、Candidateをその外に置く構成を指定している。 relative operand、`repo_root / relative` alias、input-side read/open/tree/copy/ZIP/hash guard、argv lexical preservation、submit cwd assertionは追加済みだが、external absolute path固有の分岐は実行されない。このため、repository外のCandidateだけをresolve、root-prefix、copy、rejectまたはmaterializeする将来回帰がclosure testを通過し得る。 | Test-onlyで`repo_root = tmp_path / "repo"`を作り、static directoryをrepo側、Candidateを`tmp_path / "candidate.zip"`のようなrepo外absolute path、sourceをlexical relative pathにする。その3つを同じ実invocationへ渡し、external Candidateもprotected input setに含める。現在のoutput-only staging/hash例外とe2e cwd assertionは維持する。                        |
| `RT-354-S03S04-V4-002` | P1       | `<issue-root>/report.md` — TDD S03-S04 row、Reviewer Gate、Milestone / Commit Candidate Gate、`S03/S04 Blue修正`、Final Commit             | GitHub exact HEAD `150d81a3...`はrepair brief、report、v3 review、unit/e2e test修正を既にcommitしたcurrent branch tipである。 しかし同じHEADのreportは、修正を「未コミット」、`working-tree v3 test repair`、`must be pushed`、`staged for a new commit/push`と記録している。   またreportは、commit/push後に全体pytest、full-regression integration、validate、provider update/parity、legacy search、scope auditを再実行するとしているが、current exact HEADに対するその実行結果を記録していない。したがって、repair commit、current review source、必須verification evidenceが同一exact HEADへ閉じていない。なお、closureとS05をpendingに保っている点は正しい。                                                                                                                                                                           | `150d81a3...`をv3 test-repair commitとして履歴固定し、report修正後の新しいbranch tipを次のreview sourceとして区別する。current-state rowsから`未コミット`、`working tree`、`staged for push`を除き、exact repair commitと実際に再実行した必須コマンド、exit code、件数、parity、legacy search、scope auditを記録する。P1解消後の新しいexact HEADでも、Fresh review前にclosure、PASS、S05開始を記録しない。 |

# 4. v1/v2/v3 finding解消確認

| 既存finding                                                                      | v4確認結果                               | 根拠                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `RT-354-S03S04-CODE-001` — repository-relative pathのroot-prefix化               | **解消済み**                             | `_source_attachment_paths`と`_context_source_operands`はrepository-relative sourceを`Path(relative)`として保持する。infraは各pathを文字列化してrepeated `--file`へ追加し、Oracleを`cwd=repo_root`で実行する。                                                              |
| `RT-354-S03S04-CODE-002` — provider/projection byte parity                     | **解消済み**                             | Exact HEADでpromptは双方`6e009946...`、applicationは双方`e81f4ebe...`、infraは双方`4a9ce078...`、Review resourceは双方`bf77b4cb...`で一致する。                                                                                                                  |
| `RT-354-S03S04-CODE-003` — mandatory no-inspection/no-materialization matrix   | **部分解消／V4-001へ継続**                   | nested/hidden/symlink/FIFO、application側dynamic-path guards、external `Path` object identity、infraのread/open/tree/copy/ZIP/hash guardsは追加済み。ただし実infra invocationのabsolute Candidateがrepo外ではなく、承認されたmixed external-path matrixを完遂していない。       |
| `RT-354-S03S04-CODE-004` — report implementation/closure evidence              | **旧欠陥は解消後、current HEADで再不整合／V4-002** | Runtime HEAD、spy repair、prior review identity、closure ID、旧verification evidenceは記録された。一方、current repair commitをなおworking tree / stagedとして扱い、post-commit verificationを記録していない。                                                              |
| `RT-354-S03S04-V2-001` — input-side read/open/copy/ZIP/hash spy不足              | **部分解消／V4-001へ継続**                   | 指摘されたAPI guardとoutput-only stagingの分離は実装済み。ただしrepo外absolute Candidateを実際にguard付きinfra invocationへ通していないため、path-location固有のmaterialization回帰検出が未完了。                                                                                         |
| `RT-354-S03S04-V2-002` — report current-state、closure ID、HEAD distinction、必須証跡 | **旧状態は解消後、current HEADで再不整合／V4-002** | Canonical closure ID、runtime/test/report/review identityの区分、旧legacy/parity/validate/scope evidenceは存在する。しかし`150d81a3...`のcommit済み状態とreportの未commit記述が矛盾し、同HEADのpost-repair full verificationがない。                                           |
| `RT-354-S03S04-V3-001` — mixed pathsとexplicit cwdの実invocation assertion        | **部分解消／V4-001へ継続**                   | Lexical relative operandとそのabsolute aliasのguard、argv lexical preservation、unit submit cwd、repository外の呼出元からのe2e explicit cwd assertionは追加された。e2eはfake Oracleが記録したcwdをexact repo rootと比較しており、この部分は解消済み。 ただしmixed tupleのCandidateがrepo外ではない。 |

# 5. Scope逸脱、未検証、残るリスク

## Scope逸脱

S03/S04 union allowlistを越えるproduction変更は確認されなかった。

* `91781cf...`から`150d81a3...`の変更は、repair brief、report、v3 review artifact、infra unit test、e2e testに限定される。
* Runtime implementation baseline `836a9c...`以後、provider production runtime、Review resource、projectionの動作変更はない。
* `domain/issue_planning_contracts.py`、CLI / commands、Oracle profile / stage / recovery、Oracle artifact reader、ZIP / Review JSON validators、requirement / design / plan、S05以降への変更は確認されなかった。
* Current infraはpathを順序どおりrepeated `--file`へ追加し、generated input packを作らず、output-only private stagingだけを保持している。
* Review resourceはgenerated identity fileではなく、minimal bodyの`Reviewed identity`とdigestを参照し、provider/projectionも同一bytesである。
* Reportはv4をpending、S03/S04を`repair_required`、S05–S13を未開始としており、PASS、closure、S05を先取りしていない。

## 未検証

* 本Fresh reviewではrepository checkout上の`pytest`、Ruff、mypy、`spec-dock validate`、provider update、`cmp`、legacy `rg`、scope-audit commandを独立実行していない。
* GitHub exact HEADにはcombined status contextおよびPR-triggered workflow runが確認できなかった。
* Report記載のfocused unit `1 passed`、infra `93 passed`、e2e `4 passed`等はBlue Teamの実行記録であり、本reviewの独立実行結果ではない。
* PATH Oracleの実browser attachment動作、Oracle `0.17.0` profile、submission evidence、stage-aware recoveryはS03/S04の範囲外であり、PASSを主張しない。
* GPT-5.6 Luna / Reasoning Effort Maxの実測証跡は確認しておらず、主張しない。

## 残るリスク

* Repo外absolute Candidateだけに適用されるresolve、copy、hash、archive、rejection処理が将来追加されても、current mixed-path unit testは検出できない。
* Reportのcurrent-state identityがstaleなままでは、runtime implementation、test repair、review source、次のclosure targetを一意に結合できない。
* 現行`0.16.1`のstage-blind same-session recoveryは残るが、S09/S10の明示責務であり、本レビューのfindingではない。
* Output-only staging、typed ZIP/JSON validation、exact GitHub gate、Human authorityには今回の差分による回帰は確認されなかった。

# 6. Blue Teamの最小アクション

1. `test_direct_file_operands_preserve_order_and_do_not_materialize_pack`をtest-onlyで補正し、`repo_root=tmp_path/"repo"`、repo外absolute Candidate、lexical relative sourceを同じinfra invocationへ渡す。
2. `report.md`をcommit済みの`150d81a3...`に対する事実へ更新し、post-repairのfull required verification結果を記録する。`150d81a3...`はrepair commit、新しいreport tipは次のreview sourceとして区別する。
3. 修正と必須verification evidenceを同じ新しいpushed exact HEADへ束ね、別のFresh Red Teamで再判定する。それまではS03/S04をcloseせず、S05、PR、merge、Issue closeへ進まない。
