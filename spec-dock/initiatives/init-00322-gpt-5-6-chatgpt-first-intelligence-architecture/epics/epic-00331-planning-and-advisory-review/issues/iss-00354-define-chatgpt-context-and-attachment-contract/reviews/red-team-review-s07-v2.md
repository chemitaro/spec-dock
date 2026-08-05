# S07 Fresh Red Team Review v2

## 結論

**FAIL**

| 項目                      | 結果                                         |
| ----------------------- | ------------------------------------------ |
| Reviewed repository     | `chemitaro/spec-dock`                      |
| Named branch            | `codex/iss-00354-chatgpt-context-contract` |
| Reviewed exact HEAD     | `51ec44361934991c0ba347eed7e5047c719ec122` |
| Branch-tip verification | `identical`、ahead `0`、behind `0`           |
| Repair source           | `21a2c4c2bfb6e30a925e64f8bb9508687b128417` |
| Repair relation         | ahead `1`、behind `0`、1 commit              |
| P0 / P1 / P2 / P3       | **0 / 3 / 0 / 0**                          |

GitHub connectorで指定repository、named branch、exact HEADを直接確認した。default branch、別branch、ローカル文脈、添付だけへの代替は行っていない。添付bundleはGitHub blobとの補助照合にのみ使用した。 

## P0 findings

なし。

## P1 findings

### `RT-354-S07-V2-001` — recursive parity receipt が「exact command」証跡になっていない

**Severity: P1**

**対象**

* `artifacts/20260805t-projection-cleanup-analysis.md`
* `report.md`
* `artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md`

**Evidence**

Blue repair briefは、fresh-installed／dogfood parityについて、実行したexact command、exit code、各root、file count、tree digest、`parity_exclusions: []`をcontent-free receiptへ記録するよう要求している。さらに、同brief自身はprojection update、fresh init、parity script等を実行していないと明記しており、brief中のスクリプトは計画であって実行証跡ではない。

しかし、現行cleanup artifactには次の欠落がある。

* provider-source preflight commandが `<<'PY' ...` で省略され、exact commandではない。
* fresh-init commandのoperandが単なる `<fresh-installed>` で、実行可能なexact commandまたは変数表現ではない。
* recursive parityについて、実行command自体とそのcommandのexit codeが記録されていない。
* fresh-installed側のskill rootとdocs rootがどちらも同じ `<fresh-installed>` に潰され、exact subtreeをreceipt単体から特定できない。

file count `7`／`37`、tree digest、`parity_exclusions: []`、各comparisonの`status: pass`は記録されているが、それらをどのexact invocationが生成したかへbindできない。

**Impact**

先行finding `RT-354-S07-004`が要求した再現可能なfresh-installed receiptは、完全には閉じていない。特にrepositoryに残らないtemporary installed treeについて、digestを独立再現・照合するための実行identityが不足しているため、`tc-s07-001`と`cl-s07-projection`を信頼できない。

---

### `RT-354-S07-V2-002` — changed-file scope audit の `unexpected_changed_files: []` が exact repair commit と矛盾する

**Severity: P1**

**対象**

* `artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md`
* `artifacts/20260805t-projection-cleanup-analysis.md`
* commit `51ec44361934991c0ba347eed7e5047c719ec122`

**Evidence**

Repair briefのminimal changed-file allowlistは、直接編集4ファイルと生成projection 1ファイルに閉じている。

1. provider `SKILL.md`
2. root `.agents` projection `SKILL.md`
3. parent Epic `design.md`
4. Issue `report.md`
5. cleanup artifact

また、`iss-00354 reviews/**`はread-onlyとされ、brief内のscope-audit scriptも上記5パスだけを許可している。

一方、GitHub上の `21a2c4c2...` → `51ec443...` の実差分は8ファイルであり、上記allowlist外の次の3ファイルを含む。

* `artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md`
* `reviews/red-team-review-s07-v1.md`
* `reviews/red-team-review-s07-v1-raw.md`

それにもかかわらず、cleanup receiptは `scope_audit: unexpected_changed_files: []` と記録している。

**Impact**

scope auditがrepair source `21a2c4c2...`に対して実行されたなら失敗するはずであり、実行後に3ファイルが追加されたならreceiptはfinal commitを監査していない。どちらの場合も、現行HEADに対する「bounded repair」「scope violationなし」という証跡が成立しない。

これはreview／briefを保存すること自体の是非ではなく、**宣言allowlist、実際のcommit contents、`unexpected_changed_files: []`という観測結果が同時には成立しない**ことがfindingである。

---

### `RT-354-S07-V2-003` — report が pushed repair HEAD を未commit／未push状態として記録している

**Severity: P1**

**対象**

* `report.md`
* Final Commit Gate
* S07 TDD／delegation／review state rows

**Evidence**

本レビューではnamed branch tipが `51ec44361934991c0ba347eed7e5047c719ec122`であることを確認済みであり、これは `21a2c4c2...`より1 commit aheadのpushed repair HEADである。

しかしreportのFinal Commit rowは、repair working treeについて次のcurrent-state claimを残している。

> `has not yet been committed/pushed`

さらに、commit／push後に新HEADをRed v2へ渡すことを未来の処置として記録している。

同じstale時制は、S07 observationの「new repair HEAD will be supplied after commit/push」、Final Code Review Gateの「repair commit/push and v2 are pending」にも残る。

Repair briefが禁止しているのは、同一commitのreportへresulting SHAを自己参照で書くこと、およびFresh Red PASSを先取りすることである。現在のpushed SHAをreport本文に自己記載しないことは妥当だが、既にcommit／push済みの状態を「未commit／未push」と記録することまでは正当化しない。brief自身も、stale S07 identity wordingを除去し、repair HEADはexternal handoff evidenceとしてFresh Redへ渡す契約としている。

**Impact**

`report.md`はObserved Evidence Ledgerであるため、current commit stateの誤記はrepair identityとreview gateの追跡を不正確にする。reportはrepair HEADをreview済みPASSと自己主張してはいないが、その代わりに実際のpushed状態を過去のworking-tree状態として記録しており、current ledgerとして信頼できない。

## P2 findings

なし。

## P3 findings

なし。

## 明示的に確認した正の条件

1. **Provider Skillとroot `.agents` projectionはbyte-identical。**
   両方のGit blob SHAは `69b0a87c5fa23e78bbe776f75d61f154b222bf87` で一致する。

2. **Parent Epic Design §6.3はinput-side opaque path契約へ修正済み。**
   `--provided-context-path`をoriginal top-level pathのまま扱い、walk、open、snapshot、hash、archive、filter、rename、copy、input attachment manifest化を禁止している。output-side ZIP／JSON snapshot・SHA validationは§6.4／§6.5へ分離して維持されている。退役済みinput snapshot／manifest契約は§6.3から除去されている。

3. **Formal Issue Planningはexact GitHub evidence unavailable時にfail closed。**
   Provider Skillはrepository／named branch／HEADをGitHubで確認できなければ無条件停止し、`local-context`、default branch、別branch、添付、prompt context、memoryを代替にしない。Parent Requirement `E1-REQ-031`とも整合する。

4. **操作別の`--provided-context-path`境界は明示済み。**
   `planning create`、archive Review、git-bound Review、Semantic Revisionの使用が示され、`planning apply`とclosed Mechanical Revisionから明示的に除外されている。operandの順序・字句identityを保持し、内容をinspect／materializeしない契約も記載されている。

5. **Prior v1 review identityは正しく保持されている。**
   v1 FAILはexact HEAD `21a2c4c2bfb6e30a925e64f8bb9508687b128417`、P0=0／P1=4として記録され、finding IDsも維持されている。canonical／raw review filesは同じGit blob SHA `58ebacdd03c522a385dda9589718366d91602306`である。

6. **Repair HEADをreviewed PASSとする自己主張はない。**
   reportはS07 review gateをFAIL／repair pendingとし、`cl-s07-projection`と`tc-s07-001`をpendingに維持している。S08開始、PR、merge、Issue closeもFresh Red v2 PASS前は禁止されている。

7. **Runtime／CLI／application／domain／infra／testsへのrepair差分はない。**
   GitHub上のrepair commitはdocs、Skill projection、report、brief／review evidenceに限定されている。

## 仮定・不確実性・未検証主張

* Fresh-installed treeはtemporary targetでありGitHub repositoryには残らないため、その実bytesを本Red Teamが直接取得して比較することはできない。今回確認したのは、committed receiptがformal evidence contractを満たすかどうかである。
* `validate`、`git diff --check`、fresh init、recursive parity scriptは本レビューでは再実行していない。Red Teamはread-onlyである。
* Receiptに記載されたfile countとtree digestが実際のtemporary treeから生成されたという主張は、`RT-354-S07-V2-001`のため独立検証済みとは扱わない。
* S08以降、live Oracle、browser、Blue continuity、fresh Red transportは今回のS07 review範囲外である。

## Blue Teamへのdisposition

S07は**未closeのまま維持**する。Blue TeamはS07のarchitectureやruntimeを変更せず、次の三点だけを修正対象とする。

1. parity receiptを、実際に実行したexact command、command exit code、区別可能なfresh-installed subroots、file count、tree digest、`parity_exclusions: []`へ閉じる。
2. `21a2c4c2...`からのactual changed-file setとdeclared allowlistを一致させ、final repair HEADに対するscope auditを再実行・記録する。
3. reportから未commit／未pushというstale current-state wordingを除去し、repair HEADはexternal review identityとして扱いながら、Fresh Red PASS・S07 closure・S08 readinessを先取りしない。

修正を新しいpushed exact HEADへ束ね、別のfresh Red Team reviewでP0=0／P1=0を確認するまで、`cl-s07-projection`、`tc-s07-001`、S08、PR、merge、Issue closeを進めない。
