# iss-00354 S05 Fresh Red Team Code Review

## Verdict

| 項目          |       判定 |
| ----------- | -------: |
| **Verdict** | **FAIL** |
| P0          |        0 |
| P1          |        1 |
| P2          |        0 |
| P3          |        0 |

S05のproduction実装自体には、旧optionの残存、path wiringの欠落、入力materialization、lifecycle/publication契約の破壊を確認しなかった。一方、S05 completion candidateで必須とされたno-inspection/no-materialization spyが受け入れ契約を実際には固定しておらず、禁止動作が混入してもGreenになり得るため、blockingなtest defectをP1と判定する。

## Reviewed identity and GitHub preflight

| 項目                               | 確認結果                                                                   |
| -------------------------------- | ---------------------------------------------------------------------- |
| Repository                       | `chemitaro/spec-dock`                                                  |
| Named branch                     | `codex/iss-00354-chatgpt-context-contract`                             |
| Reviewed source HEAD             | `4bb3b4072f4624ca862a0c8fcc58e5b0be581eec`                             |
| Named branch tip parity          | `identical`                                                            |
| Ahead / behind                   | `0 / 0`                                                                |
| Previous implementation baseline | `9a8602a771860bf7959e249926800dabcf3d823b`                             |
| Baseline → reviewed HEAD         | 1 commit                                                               |
| Default branch fallback          | **0 / 使用していない**                                                        |
| Fresh thread                     | **yes**。S05 planning brief、S05 plan review、S03/S04 v8のverdictを再利用していない |
| Review mode                      | read-only / defect-only                                                |
| Connector                        | GitHub connectorでnamed branchとexact SHAを直接確認                           |

Reviewed HEADのcommitはS05の`--provided-context-path`切替を表し、baselineからの差分は後述の8ファイルである。

添付されたcurrent-baseline implementation briefも補助入力として参照した。

### Changed-file allowlist

`9a8602a771860bf7959e249926800dabcf3d823b` から `4bb3b4072f4624ca862a0c8fcc58e5b0be581eec` の差分は、指定された次の8ファイルだけだった。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_e2e.py
```

`tests/integration/test_issue_planning_chatgpt_transport.py`、domain contracts、Oracle infra、CLI leaf parser、canonical docs、report、review artifactsにはS05 implementation diffがない。

## Findings

### RT-354-S05-001 — S05のno-inspection/no-materialization spyが必須契約を固定していない

| Field                      | 内容                                                                    |
| -------------------------- | --------------------------------------------------------------------- |
| Severity                   | **P1**                                                                |
| Affected path              | `tests/unit/application/test_issue_planning_prompt.py:37-108`         |
| Defect class               | 必須test contractの誤検証                                                   |
| Production defect observed | なし。現行production sourceはtuple展開だけで、provided pathを検査していない               |
| Blocking impact            | `cl-s05-cli-cutover`のno-inspection/no-materialization証跡をこのHEADで閉じられない |

#### Evidence

Current-baseline briefの`TC-S05-004`は、protected provided pathだけでなく、その**descendant**に対するfilesystem、tree、content、copy、ZIP、hash呼出しを0にするspyを要求している。provider resource validationは維持しつつ、operator-supplied path側だけを保護する契約である。

同briefは具体的な禁止APIとして、`os.listdir`、`os.scandir`、`os.walk`、copy系、`copytree`、`rename`、`replace`、`ZipFile`、`make_archive`、hashなどを列挙している。

しかし実装されたtestは、次の二点でその契約より狭い。

1. 監視対象は一部の`Path` methodだけで、`os.listdir/scandir/walk`、`shutil` copy/archive系、`zipfile.ZipFile`、hash系を監視していない。
2. 呼出しを記録する条件が`self is candidate`であるため、同じlexical pathから再構築された別の`Path` objectや、そのchild/descendantに対するアクセスを検出できない。

既存S03/S04のinfra側spyはcopy、ZIP、hash等を広く監視しているが、それは`SynthesizedPlanningPrompt`がinfraへ到達した後のconsumer境界である。S05で変更されたapplication/prompt producerが、その前段でprovided pathを検査またはmaterializeする回帰を検出する代替にはならない。既存infra spyの対象APIにはcopy、ZIP、hash等が含まれている。

現行prompt production codeはstatic directory、required paths、provided pathsをtuple展開するだけであり、実際のinspection処理は確認されない。したがってfindingはproduction修正ではなく、必須回帰testのfalse-green可能性に限定される。

#### Concrete impact

次のような回帰が将来または修正中に混入しても、現在のS05 testは成功し得る。

```text
Path(str(provided)).stat()        # 同値だが別object
provided / "child"                # descendant
os.scandir(provided)
shutil.copytree(provided, ...)
zipfile.ZipFile(...)
hashlib.sha256(...)
```

これらはOption C、REQ-005/006/007、S03/S04継承契約に反する。禁止動作を検出するための明示的なacceptance testがfalse-greenとなるため、S05 closureをPASSとして扱うには重大である。

#### Required minimal correction

`tests/unit/application/test_issue_planning_prompt.py`の既存testだけを最小修正し、次を固定する必要がある。

* protected optional operandと、そのlexical descendantを、object identityだけに依存せず検出する。
* briefで列挙された`os`、`shutil`、archive/ZIP、hash系の入力側APIをfailure-spy対象にする。
* provider-owned resource directoryとcanonical managed-source validationは従来どおり許可する。
* plannerとevidence promptの双方で、static → required → optionalの順序、重複、lexical form、`Path` object identityを維持する。

production runtime、infra、domain、canonical docsの変更は不要である。

## Checks performed

### CLI hard cutover

* `--context-manifest`のproduction definition、args field、request field、loader/helperが削除されている。
* `--provided-context-path`は`action="append"`でcreate、review、reviseにだけ追加されている。
* applyには追加されていない。
* CLI stringから`Path`を一度構築するだけで、`resolve()`、absolute化、repo-root prefixingを行っていない。
* command argsからapplication requestへ同じtupleを渡している。
* command testはcreate/review/reviseの順序・重複を検証し、旧optionを`SystemExit(2)`で拒否している。
* CLI runtime testはprovider sourceのleaf parser/help surfaceを対象にしている。

### Request and application wiring

* `PlanningCreateRequest`、`PlanningReviewRequest`、`PlanningReviseRequest`にはdefault-emptyの`provided_context_paths`があり、apply requestは変更されていない。
* Createではprovided tupleをprompt synthesizer wrapperにだけ渡し、GitHub preflight source paths、`PlanningContext`、source evidence、Candidate baselineへ混入していない。
* Reviewではoriginal Candidateとmanaged source pathsをrequired tupleとして構成し、provided pathsを別parameterで末尾へ渡している。reviewer role、reviewed identity、stale/publication処理は維持されている。
* Semantic revisionではCandidate、exact Review、revision request、managed source operandsの後ろにprovided pathsを追加している。
* Mechanical revisionはprompt/transport分岐へ入らず、non-empty provided pathsを無視する。

### Attachment ordering and direct transport

Prompt producerの順序は次で一致している。

```text
provider static attachment directory
→ required original paths
→ optional provided paths
```

Provided tupleはsort、dedup、normalizeされず、tuple unpackだけで最終`attachment_paths`へ入る。

未変更infraは、一つのpromptを構成し、`attachment_paths`の各要素を同じ順序で直接一つずつ`--file` operandへ変換する。subprocessは`cwd=repo_root`、`shell=False`である。

### Lifecycle, identity, stale and publication

Source inspectionとtest inspectionでは、次の既存契約の変更を確認しなかった。

* exact named-branch preflight/postflight。
* Candidate ZIP validationとatomic publication。
* original Candidate pathの保持。
* reviewed identityとclosed Review JSON。
* duplicate/unknown Review key rejection。
* semantic revisionのCandidate/Review SHA/finding gate。
* mechanical revisionのno-backend動作。
* create/review/revisionのstale時publication 0。
* Candidate version increment。
* public resultへのprovided/private path追加なし。

E2Eはcreate → failed fresh review → semantic revision → fresh pass reviewを通し、各operationへprovided pathsを渡し、Oracle記録上のprovided tail、Candidate version increment、repository non-mutationを検査する形に更新されている。

### Scope and privacy

* S05差分はallowlist内の8ファイルだけ。
* domain、infra、CLI parser、Candidate/Review validators、canonical docs、report、review artifactに変更なし。
* wrapper、API、alternate backend、inline fallback、generated prompt-pack、generated input manifestの追加なし。
* prompt bodyにprovided path文字列、count、inventory、hashを追加していない。
* S06 Blue continuity、S07 projection/docs、S09以降のOracle profile/recoveryを先行実装していない。

## Unverified areas and evidence limits

次は本レビューでverifiedとは扱わない。

* `4bb3b4072f4624ca862a0c8fcc58e5b0be581eec`上でのfocused pytest実行結果。
* CLI subprocess suite、full-regression E2E、Ruff、Mypy、legacy zero-match、`git diff --check`の実行結果。
* GitHub Actionsまたはrequired status checkの成功。GitHub connectorでは当該HEADに結び付くstatus/workflow resultを確認できなかった。
* reviewer環境のlocal worktree clean状態。
* live PATH Oracle、managed Chrome、browser attachmentの実動作。
* provider/installed/dogfood projection parity。これはS07以降の対象であり、S05差分には含まれない。
* `report.md`へのS05 implementation evidence採用、S05 closure、assurance promotion。
* S06以降、PR、merge、Issue close。

添付bundleからは、S05 briefの要求事項は確認できたが、exact reviewed HEAD `4bb3b407...`に結び付いた実行コマンド結果は確認できなかった。したがって、test sourceを読んだ事実とtestを実行した事実を区別している。

## No-modification statement

本レビューはGitHub connectorと添付資料のread-only inspectionだけで実施した。

* repositoryを変更していない。
* branch、commit、Candidate、canonical docs、`report.md`を変更していない。
* production source、tests、transport integration、review artifactを変更していない。
* パッチ、修正版、ZIP、新規artifactを作成していない。
* GitHub comment、PR、Issue、label、assurance、publicationへのmutationを行っていない。

## Model evidence boundary

Current-baseline briefは実装担当向け要求値として`GPT-5.6 Luna / Reasoning Effort Max`を記載する一方、LunaまたはMaxを独立に実測・検証できる証跡は取得しておらず、verifiedと主張してはならないとしている。

本fresh reviewでもwrapperによるresolved model、picker verification、Reasoning Effortの実測証跡は取得していない。したがって、次はすべて**unverified**である。

```text
GPT-5.6 Luna verified
Reasoning Effort Max verified
Luna / Max combination verified
```

モデル自己申告をwrapper実測証跡の代替にはしていない。
