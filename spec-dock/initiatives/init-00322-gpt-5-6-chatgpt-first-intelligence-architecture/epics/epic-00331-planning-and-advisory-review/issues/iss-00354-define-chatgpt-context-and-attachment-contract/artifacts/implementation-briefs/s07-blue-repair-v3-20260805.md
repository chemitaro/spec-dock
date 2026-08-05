## 結論

S07 Blue repair v3として、**`report.md`一件だけを変更した完全な修正候補**を作成しました。

GitHub Connectorでnamed branch `codex/iss-00354-chatgpt-context-contract` のtipが、指定されたsource HEAD `18ac1c79529feadd0925fa20d3ddb55b0f2e9a38`とidenticalであることを確認しました。添付された`report.md`のGit blob SHAは`267f588f20f2734f84017880ec930f84616356ab`で、同HEAD上のGitHub版と一致しています。

Red v3の正式finding `RT-354-S07-V3-001`に限定して修正しています。Red v3 canonical/rawはどちらもGit blob `7cebba8c74edd45c8ff94be2614c18292ff9af96`で一致し、変更していません。

* [修正後の完全な report.md](sandbox:/mnt/data/s07-blue-repair-v3/report.md)
* [元ファイルからの unified diff](sandbox:/mnt/data/s07-blue-repair-v3/report.diff)
* [検証レシート](sandbox:/mnt/data/s07-blue-repair-v3/verification.txt)

## 修正内容

`report.md`へ`EAL-048`を追加し、Red v3の次のidentityをimmutable historyとして記録しました。

```text
reviewed HEAD: 7634899dcbf31fafcba9380906e6918f87f82948
verdict: FAIL
P0 / P1 / P2 / P3: 0 / 1 / 0 / 0
finding: RT-354-S07-V3-001
evidence import source: 18ac1c79529feadd0925fa20d3ddb55b0f2e9a38
```

さらに、以下のS07 current-state行を同じ状態へ統一しました。

* TDD／Discovered Tests
* Step Contract Closure
* Test Contract Closure
* Closure Coverage
* Implementation Delegation Gate
* Delegated Worker Evidence
* Parent Implementation Exception
* Reviewer Gate Status
* Milestone / Commit Candidate Gate
* S90 Docs Impact
* Final Code Review Gate
* Final Spec Review Gate
* Final Commit

統一後の状態は次のとおりです。

```text
Red v2 historical source:
  51ec44361934991c0ba347eed7e5047c719ec122
  FAIL / P0=0 / P1=3

v2後のrepository state:
  three Blue correction paths: committed and pushed
  three immutable v2 evidence-import paths: committed and pushed

Red v3:
  reviewed HEAD: 7634899dcbf31fafcba9380906e6918f87f82948
  FAIL / P0=0 / P1=1
  finding: RT-354-S07-V3-001

current source:
  18ac1c79529feadd0925fa20d3ddb55b0f2e9a38
  Red v3 canonical/raw evidence import only

current Blue repair:
  report.md only
  PASS/closure claim: none
  next gate: commit/push後のexact HEADに対するfresh Red v4
```

旧v1／v2のhistorical narrative、EAL、review identity、findingは削除・改変していません。新たにv3の履歴節を追加し、過去の「当時のnext action」と現在の実行状態を分離しました。

## 変更範囲

変更候補は次の一件だけです。

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  report.md
```

次は変更していません。

```text
provider/root Skill
Epic/Issue requirement.md
Epic/Issue design.md
Epic/Issue plan.md
cleanup receipt
Blue repair briefs
Red v1/v2/v3 canonical/raw outputs
runtime / CLI / application / domain / infra
tests
unrelated docs
```

## 検証結果

| 検証                                   | 結果                                                                 |
| ------------------------------------ | ------------------------------------------------------------------ |
| Source report Git blob               | `267f588f20f2734f84017880ec930f84616356ab`                         |
| Candidate report Git blob            | `3a61f2e7a599b0c325839113379a9f9614f95e17`                         |
| Candidate SHA-256                    | `772b0bb7126558e785e01665692dd2f554230b3747b1e487ba02b849a84c3033` |
| Changed-file scope                   | `report.md`のみ                                                      |
| `git diff --check`                   | PASS                                                               |
| Modified table-row shape checks      | PASS                                                               |
| S07 state-consistency assertions     | PASS                                                               |
| Red v3が拒否したstale wording             | zero-match                                                         |
| `EAL-048`                            | exactly once                                                       |
| Red v3履歴節                            | exactly once                                                       |
| v1/v2/v3 review identity保持           | PASS                                                               |
| S07 PASS／closureの先取り                 | なし                                                                 |
| S08／Delivery PR／merge／close／finish禁止 | 維持                                                                 |

`git diff --check`は、GitHub版と一致する元`report.md`をbase commitとした隔離Git repositoryに修正候補を配置して実行しています。

## 次のゲート

このturnではcommit、push、Fresh Red v4、S07 closure、S08開始を行っていません。

Fresh Red v4の対象HEADは、修正候補をnamed branchへ**一ファイルだけcommit/pushした後のexact branch tip**として確定してください。そのSHAはこの`report.md`内で先取りせず、review promptとGitHub Connectorによって外部から束縛します。

```text
S07: open / blocked
Fresh Red v4: required
S08: prohibited
Delivery PR: prohibited
merge: prohibited
Issue close / finish: prohibited
```
