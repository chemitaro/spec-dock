# iss-00354 S05 Fresh Red Team Code Review v2

## Verdict

| 項目          |       判定 |
| ----------- | -------: |
| **Verdict** | **PASS** |
| P0          |        0 |
| P1          |        0 |
| P2          |        0 |
| P3          |        0 |

`RT-354-S05-001`で指摘されたfalse-green経路は、今回のtest-only差分で解消されている。別`Path` object、lexical descendant、`Path` / `builtins` / `os` / `shutil` / archive / ZIP / hash系の監視とactive canaryが追加され、canary履歴をclearした後の実synthesisについてzero-callを確認する構造になった。

変更は指定されたテストファイル一件だけであり、production runtime、S03/S04 direct transport、CLI hard cutover、create/review/semantic revision/mechanical lane、identity/stale/publication契約への新規差分はない。現行HEADの関連sourceを独立に照合した範囲でも、P0/P1相当の残存欠陥を確認しなかった。

## Identity / Preflight

| 項目                       | 確認結果                                                                  |
| ------------------------ | --------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                 |
| Named branch             | `codex/iss-00354-chatgpt-context-contract`                            |
| Reviewed source HEAD     | `ae58ef254e40ebb2fad4e64d8c22627fa312dae0`                            |
| Named branch tip parity  | `identical`                                                           |
| Ahead / behind           | `0 / 0`                                                               |
| Previous reviewed HEAD   | `4bb3b4072f4624ca862a0c8fcc58e5b0be581eec`                            |
| Previous → reviewed HEAD | 1 commit / ahead 1 / behind 0                                         |
| GitHub connector         | 使用済み。named branch、exact SHA、diff、current blobsを確認                     |
| Default branch fallback  | **0 / 使用していない**                                                       |
| Fresh thread             | **yes**。v1 verdictを継承せず、添付v1 reviewをhistorical defect artifactとしてのみ参照 |
| Review mode              | read-only / defect-only                                               |
| Repository mutation      | 0                                                                     |

Reviewed commitは`test(s05): provided-context-pathの監査テストを強化`であり、GitHub上のcommit identityと変更ファイルは指定値に一致する。

### Changed-file allowlist

`4bb3b4072f4624ca862a0c8fcc58e5b0be581eec`から`ae58ef254e40ebb2fad4e64d8c22627fa312dae0`までの差分は、次の一件だけだった。

```text
tests/unit/application/test_issue_planning_prompt.py
```

差分統計は`+190 / -13`である。production source、canonical requirement/design/plan、`report.md`、review artifact、infra、CLI、domainには今回のcommit差分がない。

添付されたcurrent testのGit blob SHAは`5feefecc7f22b1df8820a640b87bad8fce78e4d7`で、GitHub reviewed HEADの同ファイルblobと一致した。

添付`plan.md`のGit blob SHAも`c553db3d222f5c346c1d15c21f0242cebdee0de4`で、reviewed HEADのcanonical planと一致した。

## Findings

該当なし。

| ID | Severity | Evidence              | Path | Minimal correction |
| -- | -------- | --------------------- | ---- | ------------------ |
| —  | —        | P0/P1/P2/P3に該当する実欠陥なし | —    | なし                 |

## `RT-354-S05-001` 解消確認

v1は、旧spyが一部の`Path` methodと同一objectだけを監視していたため、同じlexical pathから再構築した別object、descendant、`os` / `shutil` / ZIP / archive / hash経路を見逃すと指摘していた。

### 1. 別`Path` objectとlexical descendant

修正版は、対象判定をobject identityから次のlexical判定へ変更している。

```python
candidate == root or candidate.is_relative_to(root)
```

入力は`str`または`os.PathLike`から`Path`へ再構築されるため、元objectと別objectであっても同じlexical operandを検出する。

active canaryには少なくとも次が含まれる。

```python
Path(str(provided_relative)).stat()
descendant.read_bytes()
builtins.open(str(descendant), "rb")
os.listdir(descendant)
os.scandir(descendant)
os.walk(descendant)
```

これにより、同値だが別objectのpathと、protected root配下のlexical descendantの双方を明示的に通している。

### 2. API監視とactive canary

修正版は次のsurfaceをfailure spy対象にしている。

| Family         | 監視対象                                                                                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Path`         | `exists`, `is_file`, `is_dir`, `is_symlink`, `stat`, `lstat`, `resolve`, `absolute`, `open`, `read_text`, `read_bytes`, `iterdir`, `glob`, `rglob`, `rename`, `replace` |
| Built-in       | `builtins.open`                                                                                                                                                         |
| `os`           | `stat`, `lstat`, `open`, `listdir`, `scandir`, `walk`, `rename`, `replace`                                                                                              |
| `shutil`       | `copy`, `copy2`, `copyfile`, `copytree`, `make_archive`                                                                                                                 |
| ZIP            | `zipfile.ZipFile`                                                                                                                                                       |
| Hash           | `sha256`, `new`, `file_digest`および利用可能なguaranteed constructors                                                                                                           |
| Module aliases | prompt moduleに既にbindされたcopy/archive/ZIP/hash alias                                                                                                                      |

`Path`各method、built-in open、列挙された`os` API、各copy API、`make_archive`、`ZipFile`、`hashlib.sha256`、`hashlib.new`には実際のactive probeがあり、それぞれが`AssertionError`を発生させ、記録されたAPI labelも一致することをassertしている。

hash familyでは`sha256`と`new`をactive probeとし、`file_digest`およびguaranteed constructorsも同じfailure lambdaへpatchされる。archive/ZIP/hash spyはprompt synthesis中の呼出し自体を禁止するため、provided pathを別表現へ変換してからmaterializeする経路も通さない。

### 3. Canaryと実synthesisの分離

active canary完了後に次を実行している。

```python
forbidden_calls.clear()
```

その後にplannerとreviewerの実synthesisを呼び、末尾で次をassertしている。

```python
assert forbidden_calls == []
```

spyが即時例外を発生させるだけでなく、対象コードが例外を捕捉して処理を継続する場合も、記録が残るためzero-call assertionで検出される。v1で不足していた「spy自体が機能すること」と「実synthesisがそのAPIを呼ばないこと」の二段階検証になっている。

### 4. Provider-owned resource validation

protected setは次のoperator-supplied pathだけである。

```text
operator/context/../opaque
/outside/context
```

productionの`_resolve_operation_resources()`はprovider-owned resource root、operation directory、`prompt.md`、`attachments/`について、symlink/type確認と`prompt.md`読取りを従来どおり行う。修正版spyはこれらprovider pathをprotected operandとして扱わないため、現在のprovider validationを拒否しない。

同じtest内で実際のprovider resource rootを使ってplanner/reviewer synthesisを構築しているため、provider validationを全面禁止したfalse-positive testにはなっていない。

### 5. 順序・重複・lexical form・object identity・privacy

修正版は末尾三件だけでなく、attachment tuple全体をassertしている。

Planner:

```text
planning static directory
→ canonical paths
→ relevant source paths
→ optional relative path
→ optional absolute path
→ duplicate optional relative path
```

Reviewer:

```text
review static directory
→ candidate.zip
→ required_same_lexical
→ optional relative path
→ optional absolute path
→ duplicate optional relative path
```

`required_same_lexical`はoptional pathと値が等しいが別objectであり、required/optional境界を跨ぐ重複が保持される。optional内部の重複も同じobject identityのまま保持される。

さらに、次を個別に固定している。

```text
relative lexical form = operator/context/../opaque
absolute lexical form = /outside/context
```

planner/reviewer promptにはoptional path文字列が現れず、reviewer promptには`candidate.zip`も現れない。したがって、static→required→optionalの完全順序、cross-boundary duplicate、optional duplicate、relative/absolute form、`Path` identity、prompt privacyのassertionは弱められていない。

## Current source contract checks

### CLI hard cutover

現行CLI sourceでは、create、review、reviseにだけ`--provided-context-path`が`action="append"`で定義され、入力順のまま`tuple(Path(...))`へ変換される。applyには追加されておらず、旧`--context-manifest`のdefinitionもない。

### Create

`PlanningCreateRequest`は`provided_context_paths`をdefault-empty tupleとして保持する。create orchestrationはこのtupleをstep-local prompt synthesizerへだけ渡し、source preflight、`PlanningContext`、Candidate provenanceへ昇格させていない。

response後のsource-current確認、typed authoring validation、publication guard、stale/collision/build/publication error mappingも現行sourceに残っている。

### Review

Reviewはrole=`reviewer`を維持し、original Candidate pathをrequired pathの先頭に置き、required source operandsの後ろへoptional tupleを渡す。

reviewed identityとSHAの照合、strict JSON parsing、Candidate再読込、source postflight、publication guard、stale時のpublication停止も維持されている。

### Semantic revision / mechanical lane

Semantic revisionのrequired orderは次のままである。

```text
Candidate
→ exact Review
→ revision request
→ current source operands
→ optional provided paths
```

bodyへ追加するscopeはselected finding ID/severityとpreserved assumptionsに限定される。

mechanical laneはこのprompt synthesizer分岐へ入らず、既存のmechanical replacement処理を実行するため、non-empty optional pathsによってbackend invocationへ移行しない。

### S03/S04 direct transport

infraは一つの`--prompt` operandを構築し、`synthesized.attachment_paths`を順序どおり反復して、一pathにつき一つの`--file` operandへ変換する。subprocessの`cwd`は`repo_root`である。

入力用pack、copy、rename、ZIP、hash、tree traversalはこのargv assemblyにない。`TemporaryDirectory`はtyped output staging用であり、provided inputのmaterializationではない。

今回のcommitがtest file一件だけであるため、これらproduction/CLI/infra/lifecycle sourceはprevious reviewed HEADから変更されていない。

## Canonical and review-source checks

確認した入力は次のとおり。

| Source                     | 扱い                                                                                            |
| -------------------------- | --------------------------------------------------------------------------------------------- |
| Canonical `requirement.md` | direct path、no inspection、original path、no generated pack、fresh Red、typed output契約を確認         |
| Canonical `design.md`      | Option A/C、opaque attachments、output/lifecycle/security boundaryを確認                           |
| Canonical `plan.md`        | S03/S04 inherited contractとS05 execution contractを確認。添付とGitHub blobは一致                        |
| S05 implementation brief   | no-inspection API list、TC-S05-002〜008、provider validation exception、order/identity/privacyを確認 |
| v1 review                  | `RT-354-S05-001`のhistorical defect statementとしてのみ使用                                           |
| Blue repair boundary       | 本依頼本文に明示されたtest-only repair contractとして使用                                                     |
| Current changed test       | GitHub exact blobと添付blobを照合して確認                                                               |
| Canonical `report.md`      | current ledgerをread-onlyで確認。今回のtest-only diffには含まれない                                          |

## Checks / Unverified areas

### 実施済み

* GitHub named branch存在確認。
* named branch tipとreviewed source HEADの完全一致確認。
* previous HEADからreviewed HEADのcommit/file allowlist確認。
* canonical requirement/design/plan、S05 brief、current reportのread-only inspection。
* current production prompt/CLI/application/infra sourceのread-only inspection。
* v1 findingとcurrent test diffの独立照合。
* 添付testとGitHub current blobのbyte identity確認。
* 添付planとGitHub canonical planのbyte identity確認。
* 添付testに対するPython syntax compilation。結果はpass。

### 未検証

* reviewed HEAD上での`pytest`実行。
* focused S05 suite、CLI subprocess suite、integration suite、full regression、Ruff、Mypy、`spec-dock validate`、`git diff --check`の実行結果。
* GitHub Actions / required status checks。reviewed HEADにはconnectorから確認できるstatusまたはworkflow runがなかった。
* live PATH Oracle、managed Chrome、browser attachment transport。
* reviewer環境のoriginal worktree clean状態。
* provider/installed/dogfood projection parity。今回の一ファイルdiffの対象外である。
* current `report.md`へのS05 implementation、v1 FAIL、Blue repair、v2 PASSの採用・closure記録。
* Blue repair briefの独立artifact本文、artifact path、SHA。今回の添付三件と一ファイルGitHub差分には含まれず、本依頼本文に示されたrepair contractだけを確認した。
* PR、merge、Issue close、assurance promotion。

これらは実行・運用証跡の未確認領域であり、current source/diffから確認されたP0/P1 defectではない。したがって、今回のdefect-only verdictをFAILへ変更するfindingとはしていない。

## Assumptions and uncertainty

* Branch identity、HEAD parity、changed-file allowlistについて推測は使用していない。GitHub connectorの比較結果を使用した。
* Test behaviorはcurrent sourceのcontrol flowとactive canary構造から判定した。exact-HEAD pytest成功そのものは主張しない。
* v1 reviewは過去判定の権威として再利用せず、修正対象`RT-354-S05-001`の定義としてだけ利用した。
* Current reportへのevidence adoptionやS05 closureは、このPASSだけでは成立しない。

## No-modification statement

本レビューでは、次の変更を行っていない。

* repository、branch、commit、tagの変更。
* Candidate、canonical requirement/design/plan、`report.md`の変更。
* production source、tests、provider projection、review artifactの変更。
* パッチ、修正版、ZIP、設計提案の生成。
* GitHub comment、PR、Issue、label、status、assurance、publicationのmutation。
* default branchへの切替えまたはfallback。

ローカルでは添付testのsyntax checkだけを行い、一時生成物は削除した。repository sourceまたは添付source本文は変更していない。

## Model evidence boundary

GitHub connector、commit metadata、current source、添付資料のいずれにも、次を独立に実測した証跡はない。

```text
GPT-5.6 Luna verified
Reasoning Effort Max verified
GPT-5.6 Luna / Reasoning Effort Max combination verified
```

したがって、これらはすべて**unverified**である。モデル自己申告やreview本文の要求値を、wrapper/browserによるresolved-model・picker-verification・reasoning-effort実測証跡の代替として扱っていない。
