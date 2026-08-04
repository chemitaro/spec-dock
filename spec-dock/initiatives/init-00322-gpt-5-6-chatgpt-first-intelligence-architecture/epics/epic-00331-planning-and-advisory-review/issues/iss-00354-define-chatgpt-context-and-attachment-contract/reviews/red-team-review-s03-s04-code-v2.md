# iss-00354 S03/S04 Fresh Red Team Code Review v2

## 1. 対象 identity

| 項目                            | 確認結果                                                               |
| ----------------------------- | ------------------------------------------------------------------ |
| Repository                    | `chemitaro/spec-dock`                                              |
| Branch                        | `codex/iss-00354-chatgpt-context-contract`                         |
| Source HEAD / review identity | `5813ad0d97510110c498102cbe18c7b4556d104c`                         |
| Blue実装修正コミット                  | `836a9c7372879747a24b7785e9484a9e9dfc2f3b`                         |
| GitHub branch tip             | `5813ad0d97510110c498102cbe18c7b4556d104c`                         |
| Branch comparison             | `identical` / ahead `0` / behind `0`                               |
| Default branch fallback       | 使用していない                                                            |
| `836a9c...` → `5813ad0...`    | ahead `1`。変更は `report.md` のみ                                       |
| GitHub確認時点                    | 2026-08-05 JST                                                     |
| Review freshness              | v1とは別の新規・独立したFresh review thread。v1 verdictは継承せず、findingの解消確認にだけ使用 |
| Mutation                      | なし。repository、canonical docs、tests、report、review artifactsを変更していない |

GitHub connectorでnamed branchと要求SHAを確認した。`5813ad0...` は、コミットメッセージと差分上もS03/S04 v1修正後のreport-only evidence updateであり、runtime、resource、testsの実体は`836a9c...`から変化していない。

添付`attachments-bundle.txt`は補助照合に使用し、判定のrepository authorityはGitHub exact HEADとした。
別添`設計判断と提案.txt`は例外・failure taxonomyの別テーマであり、iss-00354 S03/S04のfinding根拠から除外した。

---

## 2. 判定

# **FAIL**

| Severity | 件数 |
| -------- | -: |
| P0       |  0 |
| P1       |  2 |
| P2       |  0 |
| P3       |  0 |

P1が2件残っているため、S03/S04 atomic closureは成立しない。

---

## 3. Finding table

| ID                     | Severity | File / symbol                                                                                                                                               | 事実                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | 最小修正方向                                                                                                                                                                                                                                                                                                        |
| ---------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S03S04-V2-001` | P1       | `tests/unit/infra/test_issue_planning_chatgpt.py::test_direct_file_operands_preserve_order_and_do_not_materialize_pack`                                     | `tc-s04-001`は、input-sideのtree、copy、archive、ZIP、hash、write APIをfailure spyで`0`と証明することを要求している。現行testがfailure-spyしているのは`Path.mkdir`、`write_bytes`、`write_text`、`unlink`、`rename`、`replace`、`iterdir`、`glob`、`rglob`、`resolve`、`stat`であり、入力の`read_bytes`／`open`、`shutil.copy*`、archive／`ZipFile`、hash APIを直接禁止していない。そのため、`shutil.copyfile(input, temp)`、`ZipFile.write(input)`、`open(input)`＋hashによる再materializationを導入しても、このtestは通過し得る。承認済みのno-materialization test contractを満たしていない。                                                                                                                                                                                                                                                                     | 許可済みtest file内で、attachment入力を対象とするread/open、copy、archive/ZIP、hashのfailure spiesを追加し、全call countが`0`であることをassertする。output-only private stagingは対象外として明示的に分離する。production codeを変更する必要は、追加testが実際の違反を検出した場合に限る。                                                                                                  |
| `RT-354-S03S04-V2-002` | P1       | `<issue-root>/report.md` — `EAL-018`、`Test Contract Closure`、`Closure Coverage`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`、`S03/S04 Blue修正` | reportのcurrent-state ledgerがexact HEADの事実と整合していない。①`Test Contract Closure`はcanonical ID `cl-s04-direct-transport`ではなく`cl-s04-profile`を使用する一方、直後の説明は「aliasを使う場合はClosure Deltaへ記録」とし、Closure Delta自身は`no alias`としている。②`Closure Coverage`はS03を「no implementation evidence yet」、S04以降を「not observed before implementation」と記録し、同じreport内の「`836a9c...`で実装・検証済み、pending review」と矛盾する。③Reviewer Gate、Milestone Gate、EAL-018、Blue修正節はFresh v2 targetを`836a9c...`へ固定しているが、GitHubのcurrent exact review sourceはreport-only commitを含む`5813ad0...`である。④実装ブリーフがreport記録を必須とするlegacy searchのexact result、provider syncのexact invocation／exit code／生成対象、`spec-dock validate`、scope audit、no-inspection call countsもS03/S04 evidenceとして記録されていない。v1 `CODE-004`は部分修正に留まる。 | `836a9c...`をimplementation resulting HEADとして保持しつつ、review source identityを「修正後にpushされたnamed branchのexact tip」として別fieldへ結合する。全current-state rowを実装済み／review pendingへ統一し、`cl-s04-direct-transport`へ訂正する。必須コマンド、exit code、spy counts、provider-sync生成対象、validate／scope auditを記録する。P1解消まではclosure、PASS、S05開始を記録しない。 |

### Finding 001の具体的な失敗検出不足

現行のdirect transport本体は、`attachment_paths`を順番どおり`("--file", str(path))`へ追加し、child processを`cwd=repo_root`で起動している。現時点のproduction codeそのものにinput pack生成は確認されなかった。

問題は、この実装境界を固定するtestが次の回帰を検出できないことである。

* `shutil.copyfile(candidate_path, temporary_path)`
* `zipfile.ZipFile(...).write(candidate_path)`
* `open(candidate_path, "rb")`と`hashlib.sha256`
* attachment directory childを`os.scandir`やraw `open`で読む処理
* inputから別temporary pathへ書き出すmaterialization

これは任意のcoverage改善ではなく、planが`required verification=no-tree/copy/archive/hash spy`、`tc-s04-001=tree/copy/ZIP/hash/write API 0`として明示したclosure条件である。

### Finding 002の具体的なreport不整合

`Step Contract Closure`はS03/S04を正しく「`836a9c...`で実装済み、Fresh review pending」と記録している。一方、その直後の`Closure Coverage`は実装前状態を残している。また、同じ一連の表で`cl-s04-direct-transport`と`cl-s04-profile`が混在している。

さらに、current HEADのコミット自身は「TDD/closure/worker/reviewer台帳をS03/S04実装後状態で整合」と主張しているため、これは単なるhistorical noteではなく、更新対象から漏れたcurrent-state contradictionである。

---

## 4. v1 findingごとの解消確認

| v1 ID                    | v2確認結果       | 根拠                                                                                                                                                                                                                                                                                                                      |
| ------------------------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S03S04-CODE-001` | **解消済み**     | Provider promptの`_source_attachment_paths`はrepository-relative sourceを`Path(relative)`として返し、`repo_root / relative`へ変換しない。application側の`_context_source_operands`も同じlexical contractである。  Archive ReviewではCandidate `Path`のobject identityを`is`で検証し、Semantic RevisionでもCandidate、Review、revision requestの3つを`is`で検証している。 |
| `RT-354-S03S04-CODE-002` | **解消済み**     | Exact HEADでprovider/projection blob SHAが一致する。Prompt=`6e009946...`、application=`e81f4ebe...`、infra=`4a9ce078...`、Review resource=`bf77b4cb...`。                                                                                                                                                                          |
| `RT-354-S03S04-CODE-003` | **未解消／部分修正** | nested、hidden、symlink、FIFOを使ったopaque-directory test、dynamic pathの`read_bytes`／`resolve`／`stat`／tree API guards、external `Path` identity、argv orderは追加された。  ただし、direct transport入力側のcopy／ZIP／hash／raw readをfailure-spyする必須matrixが不足している。`RT-354-S03S04-V2-001`へ継続。                                                       |
| `RT-354-S03S04-CODE-004` | **未解消／部分修正** | resulting implementation HEAD、主要test件数、v1 FAIL、修正境界、closure pendingは追記された。reportはS03/S04をPASS／closedとせず、S05も開始していない点は正しい。 しかし、current exact review target、Closure Coverage、closure ID、必須report evidenceが未整合である。`RT-354-S03S04-V2-002`へ継続。                                                                               |

---

## 5. Scope逸脱、未検証、残るリスク

### Scope逸脱

**S03/S04 union allowlistを越えるproduction変更は確認されなかった。**

`f2238d...`からimplementation commit `836a9c...`までの変更は、次に限定されている。

* provider runtime 3ファイル
* provider Review resource
* 対応するprovider projection
* 指定されたunit/integration test 5ファイル
* implementation identity addendum、v1 review、report evidence

次の変更は確認されなかった。

* `domain/issue_planning_contracts.py`
* CLI／commands
* Oracle profile／stage／recovery policy
* Oracle artifact reader
* ZIP／Review JSON validators
* requirement／design／plan
* S05以降
* bridge、inline fallback、generated pack、alternate backend

Review resourceはgenerated identity attachmentではなくminimal bodyの`Reviewed identity`とdigestを参照し、provider/projection SHAも一致する。

### 未検証

* Exact source HEAD `5813ad0...`にはGitHub combined status contextがなく、PR-triggered workflow runも取得できなかった。
* 本Fresh reviewではrepository checkout上の`pytest`、`ruff`、`mypy`、`spec-dock validate`、provider sync、`cmp`を再実行していない。
* Report記載の`1472 passed / 2252 skipped`、focused `237 passed / 11 skipped`、full-regression `11 passed`はBlue Teamの記録であり、本reviewによる独立実行結果ではない。
* `5813ad0...`はreport-only commitであるためruntime/test blobは`836a9c...`と同じだが、report evidenceそのものは`5813ad0...`を対象に判定した。
* PATH Oracleの実browser behavior、attachment upload結果、0.17 profileは今回のS03/S04 review範囲外であり、PASSを主張しない。

### 残るリスク

* Production sourceの静的実体はpath-only／direct repeated `--file`契約に整合しているが、Finding V2-001のtest gapにより、将来のinput copy／ZIP／hash回帰をclosure suiteが検出できない。
* 0.16.1のstage-blind recoveryはS03/S04理由では変更されておらず、S09/S10の後続責務である。今回のfindingではない。
* Reportはclosureをpending、S05を未開始としているため、早すぎるPASS／完了／S05開始claimは確認されなかった。ただし、current-state表とexact review identityの修正が必要である。

---

## 6. Blue Teamが次に取るべき最小アクション

Blue Teamは次の2点だけを修正する。

1. `tests/unit/infra/test_issue_planning_chatgpt.py`のdirect transport testへ、input-side read/open、copy、archive/ZIP、hashのfailure spiesを追加し、output-only stagingと分離したうえでcall count `0`を証明する。
2. `report.md`のcurrent-state rows、canonical closure ID、implementation HEADとreview source HEADの区別、legacy search／provider sync／validate／scope audit等の必須証跡を整合させる。

修正後は、同一の新しいpushed branch tipにtestとreportを結合し、そのexact HEADを別のFresh Red Team reviewへ渡す。**それまではS03/S04をcloseせず、S05、PR、merge、Issue closeへ進まない。**
