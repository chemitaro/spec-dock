# S07 Fresh Red Team Review

## 結論

**FAIL**

* Reviewed repository: `chemitaro/spec-dock`
* Named branch: `codex/iss-00354-chatgpt-context-contract`
* Reviewed exact HEAD: `21a2c4c2bfb6e30a925e64f8bb9508687b128417`
* S07 base: `68afc5bb009256231976877475d4038f3e95b728`
* Difference: `ahead 1 / behind 0`、1 commit、15 changed files
* P0: **0**
* P1: **4**
* P2: **0**
* P3: **0**

指定 named branch を GitHub connector で直接確認した。S07 base からの差分は、provider／dogfood の skill・docs、親 Epic の限定文言、Issue report、および S07 evidence artifacts に限定され、runtime や tests の変更は含まれていない。default branch fallback は使用していない。

---

## Findings

### `RT-354-S07-001` — Parent Epic Design §6.3 が廃止済み input snapshot／manifest 契約を残している

**Severity: P1**

**Location**

`epic-00331-planning-and-advisory-review/design.md`
`§6.3 Prompt and reference attachments`

**Evidence**

S07 brief は、親 Design の §4、§6.3、§6.5、§9、§10、§11 に残る旧 body／attachment／session 境界を限定修正対象として明示している。また、directory input の walk、read、hash、copy、archive、filter、manifest 化を推奨する文言を禁止している。

現行 Design §4 は、Issue Planning の追加 reference を repeatable な `--provided-context-path` で渡す opaque path とし、Runtime が内容を scan、再構成、hash、archive しない契約へ更新されている。

しかし §6.3 は依然として、入力添付を「source／evidence の byte snapshot」とし、`name`、`source label`、`SHA`、`reference purpose` を持つ attachment manifest を生成する契約を記載している。

**Impact**

一つの approved Parent Design 内に、次の二つの相互排他的な input contract が残る。

1. original top-level path を opaque に Oracle へ渡し、内容を inspect／hash／manifest 化しない。
2. 添付を byte snapshot 化し、SHA 付き manifest を構築する。

実装者や後続 reviewer が §6.3 を authority として読むと、S03／S04／S05 で廃止した generated input pack、input hashing、attachment manifest を再導入できてしまう。S07 の parent-wording acceptance criteria も「Parent design の対応節が同じ意味になること」を要求しているため、現状では `cl-s07-projection` を close できない。

**Required repair**

§6.3 だけを限定修正し、次を明記する。

* authoritative minimal body と provider-owned operation resources の分離
* `--provided-context-path` は original opaque reference path
* input file／directory の内容を scan、snapshot、hash、archive、manifest 化しない
* output artifact の safe snapshot／SHA validation は別の output-side contract として維持する

---

### `RT-354-S07-002` — Official Skill が formal Issue Planning の `local-context` bypass を残している

**Severity: P1**

**Location**

`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
`Stop Conditions`

**Evidence**

Parent `E1-REQ-031` は、formal Issue Planning／Review で exact current repository／branch／HEAD または GitHub connector を確認できない場合、fail closed とし、default branch、別 branch、添付、memory を代替 source に使わないことを要求する。

汎用 authoring-pack documentation に追加された S07 scope noteも、`local-context` evidence を formal Issue Planning の fallback として扱わないと明示している。

一方、現行 official Skill の Stop Conditions は次の条件になっている。

> Repository/branch evidence ... is unavailable **and no explicit local-context run was approved**.

これは、明示承認された `local-context` run があれば、formal Issue Planning の exact GitHub branch gate を迂回できるという正の経路を残す。

provider Skill と root dogfood Skill は同一 blob であるため、この矛盾は両 surface に投影されている。

**Impact**

operational entrypoint が、Parent Requirement と generic-lane scope note の双方で禁止された fallback を許可している。GitHub connector unavailable、current branch unavailable、wrong branch only available の各ケースで、formal Candidate／Review を生成してよいという誤った operator 判断につながる。

**Required repair**

Stop Condition を、formal Issue Planning では exact repository／named branch／HEAD evidence が unavailable なら無条件に停止する文言へ変更する。

`local-context` は generic authoring-pack evidence lane にだけ残し、Issue Planning formal run、Candidate、Review、Human Gate、apply の代替経路としては参照しない。

---

### `RT-354-S07-003` — Official Skill の `--provided-context-path` 操作別契約が Runtime と一致していない

**Severity: P1**

**Location**

`spec-dock-issue-planning/SKILL.md`
`Operating Spine`

**Evidence**

S07 brief は、repeatable `--provided-context-path` を次の三操作で使用可能と明記し、`planning apply` には渡さないことを要求している。

* `planning create`
* `review planning`
* semantic `planning revise`
* `planning apply`: option なし

Runtime parser／request wiring もこの形になっている。`PlanningCreateArgs`、`PlanningReviseArgs`、`PlanningReviewArgs` は `provided_context_paths` を持つが、`PlanningApplyArgs` は持たない。argument registration も create／revise／review のみである。

ところが現行 Skill は create の例と説明だけに option を追加している。review と revise の command examplesには option がなく、apply に渡してはならないという exclusion も記載されていない。

後段の一般文は「Reference files and directories are passed through the repeatable option」とだけ記載しており、操作別境界を示さないため、apply にも適用できるように読める。

**Impact**

official Skill だけを参照する operator は、Review や Semantic Revision へ追加 evidence を渡せることを発見できない。一方で、apply に同 option を渡す誤った invocation を組み立てる可能性がある。これは user-facing operational contract と実 Runtime contract の不一致である。

**Required repair**

Operating Spine に最小限の操作別記載を追加する。

* archive／git-bound Review で必要な場合、`--provided-context-path` を repeatable に指定できる。
* Semantic Revision でも prior Candidate／Review evidence 以外の追加 reference を同 option で渡せる。
* Mechanical Revision と `planning apply` にはこの reference optionを渡さない。
* path の順序、字句表現、opaque identity を保持し、内容を inspect／materialize しない。

---

### `RT-354-S07-004` — Fresh-installed recursive parity と pushed-HEAD evidence が report に閉じていない

**Severity: P1**

**Location**

* `iss-00354/report.md`
* `artifacts/20260805t-projection-cleanup-analysis.md`

**Evidence**

S07 brief の acceptance contract は、provider／dogfood／fresh installed の skill tree と docs treeについて、全 relative file set、size、SHA-256 の完全一致を要求している。個別 allowlist、除外、glob skip、content-based exception は禁止されている。

さらに report evidence として、少なくとも次を要求している。

* exact projection command と exit code
* provider↔dogfood／provider↔installed の四つの parity roots
* recursive file counts
* content-free tree SHA-256
* `parity_exclusions: []`
* exact scope audit
* validate／diff-check results

現行 report は S07 の証跡を「provider/projection SHA parity」「cleanup analysis artifact」「validate」「diff-check」と要約するだけで、source identityを `current S07 working tree`、次ゲートを `commit/push` と記録している。

Milestone gate も、既に GitHub 上で exact HEAD `21a2c4c2...` が存在するにもかかわらず、S07 commit candidate を `current working tree` とし、「commit/push後にexact HEADをfresh Red Teamへ送る」と記載したままである。

cleanup artifact が提示する parity evidence は、skill 一件の SHA と「docs 4件が provider／dogfood byte-identical」という要約までである。fresh installed tree の exact root、relative file set、recursive file count、tree digest、exclusions、init command／exit codeは記録されていない。

**Impact**

GitHub 上の changed provider／dogfood file pairsについては blob parity を確認できるが、S07 の必須条件である **fresh installed tree 全体**の再現性を確認できない。したがって、QA reviewer は missing／extra／changed file がないことを独立検証できず、`tc-s07-001` と `cl-s07-projection` の closureは証拠不足となる。

report の「fresh review pending」という状態自体は finding ではない。finding は、その review に先立って必要な pushed-HEAD identity と recursive parity evidence が閉じていないことである。

**Required repair**

1. provider source から既定 update を実行する。
2. fresh temporary targetへ `spec_dock.cli init` を実行する。
3. skill／docs の四比較を、除外なしで recursive に検証する。
4. exact command、exit code、root、file count、tree digest、`parity_exclusions=[]` を report または content-free evidence artifactへ記録する。
5. `21a2c4c2...` を historical failed-review sourceとして保持し、修正後の新しい pushed HEAD を fresh Red Teamへ渡す。

---

## 確認できた正の事項

* S07 baseからの差分は、予定された skill／docs projection、親 Requirement／Design、report、S07 artifacts に限定され、runtime、CLI、application、domain、infra、tests の変更はなかった。
* provider／dogfood の四つの変更 docs pairは、それぞれ GitHub blob SHA が一致している。
* Parent `E1-REQ-032` と `E1-REQ-034` は、minimal body／opaque reference paths、および pre-submit／post-submit recovery分離へ更新されている。
* Parent Design §6.5 と §9 の session recovery wordingは、pre-submit new execution と post-submit same-session recoveryを区別している。
* generic authoring-pack docsの既存用途は保持され、formal Issue Planningとのscope boundaryが追加されている。

## 仮定

* S07 canonical plan、S07 implementation brief、親 Epic Requirement／Design、official Skill、current Runtime parserを本レビューの契約 authority として扱った。
* 添付 bundle は、GitHub exact branchの補助 evidence としてのみ使用した。

## 不確実性

* `/private/tmp/iss-00354-s07-review-prompt-20260805.md` の literal file bytes はこの実行環境には存在しなかった。そのため、提示 path をS07 fresh review依頼として解釈し、GitHub current branchと添付されたS07 source bundleからレビューを実施した。
* repository checkout上で `spec-dock validate`、`git diff --check`、fresh init、recursive parity scriptは再実行していない。本判定はGitHub exact blobs、canonical contracts、committed evidenceのread-only inspectionに基づく。

## 未検証主張

* report／cleanup artifactが主張する fresh-installed parity、`spec-dock validate` success、`git diff --check` successは、exact command outputまたは完全なcontent-free receiptがないため独立検証済みとは扱っていない。
* live Oracle、managed Chrome、model selection、Blue continuation、fresh Red transportはS07 docs/projection reviewの対象外であり、今回再検証していない。
* repository、branch、canonical docs、artifacts、tests、commit、PRへの変更は行っていない。
