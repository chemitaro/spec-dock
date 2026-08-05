# S07 Blue Team Repair Brief v7

* repository: `chemitaro/spec-dock`
* branch: `codex/iss-00354-chatgpt-context-contract`
* source_head: `3d20925280f7992d8bbc8341c94829584e5c3630`
* red_review: `S07 Fresh Red Team Review v7` — `FAIL` / P0=`0` / P1=`2` / P2=`0` / P3=`0`; findings=`RT-354-S07-V7-001`, `RT-354-S07-V7-002`
* scope: `report.md` + append-only S07 evidence rows/sections
* model_requested: `GPT-5.6 Pro`
* model_resolved: `GPT-5.6 Pro`
* model_verified: `no`

GitHub Connectorでnamed branchを直接確認し、branch tipはsource HEAD `3d20925280f7992d8bbc8341c94829584e5c3630`と`identical`、ahead `0`、behind `0`だった。Default branch fallbackは使用していない。Red v7は同HEADをread-only／defect-onlyで確認し、current-state同期不足とv5/v6 evidence SHAの誤結合だけをP1としている。

`d96ce0807340631bbf214ed24cdfe9bd91165780`からsource HEADまでの差分は、`report.md`の2行変更と、Red v6 canonical/rawおよびBlue v6 briefの3 evidence importだけである。Provider Skill、親Epic、Issue三文書、cleanup receipt、runtime、testsには差分がない。Red v7は、これらのv6 evidenceが既にcommit/push済みであることも確認している。

現行`report.md`はGitHub exact HEADのblobと一致するものを修正元とする。

## Exact edits

### EAL additions and SHA correction

#### 1. 既存行の扱い

`EAL-052`と`EAL-053`は履歴行として**変更しない**。

* `EAL-052`はRed v5の正しいidentityを持つ。

  * reviewed HEAD: `03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a`
  * Red v5 output SHA-256: `1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc`
* `EAL-053`は、当時生成されたBlue v5 briefと、その後の修正指示をimmutable historyとして残す。
* `EAL-053`内でRed v5 SHAとして記載された`698ff25d...`は誤結合だが、履歴行を上書きせず、後続のappend-only EALで明示的に訂正する。

現行GitHub `report.md`では、`EAL-052`が正しいRed v5 SHAを保持する一方、`EAL-053`のnext actionがRed v6 SHAをRed v5へ誤って結び付けている。

#### 2. `EAL-054` — Red v6 review evidence

`EAL-053`直後へ、次の行をappendする。

```md
| EAL-054 | adopted | `reviews/red-team-review-s07-v6.md` | chatgpt-use-red-team-docs | exact HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780` に対するv1〜v5とは別のfresh defect-only S07 review v6はFAIL（P0=0/P1=1/P2=0/P3=0）。`RT-354-S07-V6-001`をBlue修正入力として採用する。Red v5の正式SHAはEAL-052の`1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc`であり、`698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`はRed v6 canonical/rawのSHAである。EAL-053の誤ったversion結合は本append-only行で訂正し、EAL-053自体は履歴として変更しない | `reviews/red-team-review-s07-v6.md`, `reviews/red-team-review-s07-v6-raw.md`, `report.md` | S07 v6 review identity、versioned SHA correction、review gate history | Red v6はGitHub named branchとexact HEADをread-onlyで確認し、repository、Candidate、canonical docs、runtime、testsを変更していない。P1はEAL-053 next_actionとClosure Coverageの2セルに残る完了済みv5 mutation/reviewの再要求だけに限定された | fresh_fail | `reviews/red-team-review-s07-v6.md`, `reviews/red-team-review-s07-v6-raw.md`（SHA-256 `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`、canonical/raw Git blob `3a428ff82d94fa41beb090ac1e547b0aa6aa8ba9`）；requested/resolved `GPT-5.6 Pro`、verified `no` | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S07 closure/S08 start | v6 findingの2セル修正とv6 evidence importはsource HEAD `3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済みである。v6を再実行せず、Red v7結果をEAL-056へ採用し、bounded report/evidence repair後のexact pushed HEADをfresh Red v8へ渡す |
```

Red v6の正式artifactは、source HEAD `d96ce080...`、model requested/resolved `GPT-5.6 Pro`、verified `no`、`FAIL / P1=1`を記録している。

#### 3. `EAL-055` — Blue v6 brief evidence

続けて次の行をappendする。

```md
| EAL-055 | adopted | `artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md` | chatgpt-use-implementation-brief-repair | Red v6 P1一件を`report.md`のEAL-053 next_actionとClosure CoverageのS07行だけへ限定するBlue repair v6を採用した。Briefのsource HEADは`d96ce0807340631bbf214ed24cdfe9bd91165780`であり、Red v6 `FAIL / P1=1`、report-only 2セル修正、fresh Red v7停止条件を定義する | `artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md`, `report.md` | S07 Blue repair v6 input and immutable evidence identity | Brief、Red v6 canonical/raw、2セル修正はsource HEAD `3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済みである。Provider Skill、parent docs、cleanup receipt、Issue三文書、runtime、tests、既存Red/Blue evidenceは変更していない | advisory_adopted | `artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md`（SHA-256 `21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5`）；requested/resolved `GPT-5.6 Pro`、verified `no` | issue orchestrator | ChatGPT-Use | no | Blue v6 repairは`3d20925280f7992d8bbc8341c94829584e5c3630`で完了済みとして保持する。Red v7が報告したcurrent-row同期とevidence identityのP1×2だけを次の修正対象とする |
```

Blue v6 briefは、source HEAD `d96ce080...`、Red v6 `FAIL / P1=1`、`report.md`の2セル限定scope、model requested/resolved `GPT-5.6 Pro`、verified `no`を持つ。

#### 4. `EAL-056` — Red v7 review evidence

続けて次の行をappendする。

```md
| EAL-056 | adopted | `reviews/red-team-review-s07-v7.md` | chatgpt-use-red-team-docs | exact HEAD `3d20925280f7992d8bbc8341c94829584e5c3630` に対するv1〜v6とは別のfresh defect-only S07 review v7はFAIL（P0=0/P1=2/P2=0/P3=0）。`RT-354-S07-V7-001`と`RT-354-S07-V7-002`をBlue修正入力として採用する | `reviews/red-team-review-s07-v7.md`, `reviews/red-team-review-s07-v7-raw.md`, `report.md` | S07 v7 review gate、current-state synchronization、v5/v6/v7 evidence identity binding | Red v7はGitHub named branch、exact HEAD、current report、Red v6 evidence、Blue v6 briefをread-onlyで確認した。P1は、current S07 rowsに残るv6未実施表現と、Red v5/v6 SHAの誤結合およびv6 formal evidence未採用だけに限定される。Provider Skill、Epic §6.3、Issue三文書、cleanup receipt、runtime、testsには新規P1がない | fresh_fail | `reviews/red-team-review-s07-v7.md`, `reviews/red-team-review-s07-v7-raw.md`（SHA-256 `471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a`）；requested/resolved `GPT-5.6 Pro`、verified `no` | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S07 closure/S08 start | append-only v6/v7 evidence adoption、正しいversion別SHA binding、全current S07 rowのv7完了/v8 next-gate同期だけを行う。修正後のexact pushed HEADをfresh Red v8へ渡し、P0/P1=0までS07、S08〜S13、PR、merge、Issue close、Issue finishを保留する |
```

Red v7は、source HEAD `3d209252...`、model requested/resolved `GPT-5.6 Pro`、verified `no`、`FAIL / P1=2`を記録し、対象をcurrent S07 rowsとv6 evidence bindingに限定している。 

#### 5. `EAL-057` — このBlue v7 brief

この回答を次へbyte-exactで保存する。

```text
artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md
```

保存後に実測SHA-256を計算する。

```bash
BLUE_V7_BRIEF='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md'
BLUE_V7_SHA="$(sha256sum "$BLUE_V7_BRIEF" | awk '{print $1}')"
printf '%s\n' "$BLUE_V7_SHA"
```

`<OBSERVED_BLUE_V7_BRIEF_SHA256>`を実測値へ置換してから、次の行をappendする。Placeholderを残したままcommitしてはならない。

```md
| EAL-057 | adopted | `artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md` | chatgpt-use-implementation-brief-repair | Red v7 P1×2だけを、append-only v6/v7 EAL、version別SHA correction、v6/v7 review history、列挙されたcurrent S07 gate rowsの同期へ限定するBlue repair v7を採用した | `artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md`, `report.md` | S07 Blue repair v7 input and evidence | 修正境界は`report.md`と新規v7 canonical/raw review evidenceおよび本briefのimportだけである。Provider Skill、parent Epic、Issue三文書、cleanup receipt、runtime、CLI、application、domain、infra、tests、既存v1〜v6 evidenceは変更しない | advisory_adopted | `artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md`（SHA-256 `<OBSERVED_BLUE_V7_BRIEF_SHA256>`）；requested/resolved `GPT-5.6 Pro`、verified `no` | issue orchestrator | ChatGPT-Use | no | report/evidence-only修正をvalidate・diff-check・scope audit後にcommit/pushし、外部で確定したexact HEADをfresh Red v8へ渡す。Red v8 PASS前はS07 closureと後続工程を開始しない |
```

### S07 current-state synchronization

次のcurrent-state rowsだけを置換する。既存のv1〜v5 historical narrative、EAL-044〜EAL-053、過去review artifactsは書き換えない。

#### 1. TDD evidence — S07 row

`#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）`のS07行を全文置換する。

```md
| S07 | implementation-repair | provider-first docs, installed/dogfood projection parity, parent wording consistency | v1〜v5の履歴を保持した上で、Fresh Red v6はexact HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780`をreviewしFAIL（P0=0/P1=1）。Red v6 canonical/raw、Blue repair v6 brief、v6の2セルreport correctionは`3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済み。Fresh Red v7は同HEADをreviewしFAIL（P0=0/P1=2、`RT-354-S07-V7-001`、`RT-354-S07-V7-002`） | Red v5 SHA `1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc`、Red v6 SHA `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`、Blue v6 brief SHA `21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5`、Red v7 SHA `471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a`。次のreview identityは本修正commit/push後に外部で確定する | blocked; fresh Red v8 required | S07はpending/blocked。S08〜S13、PR、merge、Issue close、Issue finishはfresh Red v8 PASSまで開始しない |
```

#### 2. Discovered Tests — S07 row

`#### 発見されたテスト / リスク（Discovered Tests）`のS07行を全文置換する。

```md
| S07 | parity/scope/current-state/evidence identity drift after v1 repair | Fresh Red `RT-354-S07-V2-001`〜`003`、`RT-354-S07-V3-001`、`RT-354-S07-V4-001`、`RT-354-S07-V5-001`、`RT-354-S07-V6-001`、`RT-354-S07-V7-001`、`RT-354-S07-V7-002` | parity command、distinct fresh-installed roots、historical five-direct/three-evidence scope、v2〜v5 push-stateは既存証跡として保持する。v6 review/briefをappend-only EALへ採用し、Red v5=`1e67e8d...`、Red v6=`698ff25d...`、Blue v6=`21aa6dbc...`、Red v7=`471e45d7...`へversion別identityを訂正する。全current S07 rowsをv6完了・v7 FAIL P1×2・fresh Red v8 next gateへ同期する | `cl-s07-projection` / `tc-s07-001` | no | EAL-054〜EAL-057、`reviews/red-team-review-s07-v6.md`/raw、`artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md`、`reviews/red-team-review-s07-v7.md`/raw、`artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md`; fresh Red v8 PASSまでpending/blocked |
```

#### 3. Step Contract Closure — S07 row

```md
| S07 | `cl-s07-projection`, `tc-s07-001` | provider/installed/dogfood parity and parent wording consistency | recursive parity、historical scope audit、provider/installed identityは既存PASS証跡として保持する。Fresh Red v6は`d96ce0807340631bbf214ed24cdfe9bd91165780`をreviewしてFAIL（P0=0/P1=1）。v6 evidence/briefと2セル修正は`3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済み。Fresh Red v7は同HEADをreviewしてFAIL（P0=0/P1=2）。現在のbounded actionはreport current rowsとappend-only v6/v7 evidence identityの同期だけである | pending / blocked | 本修正後のexact pushed HEADに対するfresh Red v8がPASS（P0=0/P1=0）した場合だけcloseする。S08〜S13、PR、merge、Issue close、Issue finishはそれまで保留する |
```

#### 4. Test Contract Closure — `cl-s07-projection`

```md
| `cl-s07-projection` | S07 | yes | implementation-repair | S07 brief、Fresh Red v1〜v7、Blue repair briefs、provider/installed/dogfood recursive parity、validate、diff-check、historical scope audit | committed parity/scope receipt、append-only v6/v7 EAL/history、current-state row synchronization、version別SHA/path assertion | Red v5 review SHA=`1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc`。Red v6 review SHA=`698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`、Blue v6 brief SHA=`21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5`で、v6 evidence/briefと2セル修正は`3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済み。Red v7 review SHA=`471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a`、FAIL P1×2 | pending / blocked | close only after fresh Red v8 PASS; S08〜S13、PR、merge、Issue close、Issue finishを開始しない |
```

#### 5. Test Contract Closure — `tc-s07-001`

```md
| `tc-s07-001` | S07 | yes | implementation-repair | provider-source preflight、fresh init、四組recursive parity、`parity_exclusions=[]`、historical eight-file scope audit、v6/v7 evidence identity | existing counts 7/7/37/37 and tree SHAs、Red v5/v6/v7 SHA separation、v6 canonical/raw and Blue brief path binding、all current S07 gate rows synchronized to fresh Red v8 | parity/scopeは既存PASS証跡を保持する。Red v6は`d96ce080...`でFAIL P1×1、v6 repair/evidence boundaryは`3d209252...`。Red v7は`3d209252...`でFAIL P1×2。現在の修正はreport/evidence-onlyでありruntime/test mutationはない | pending / blocked | fresh Red v8 P0/P1=0までS07をcloseせず、S08〜S13を開始しない |
```

#### 6. Closure Coverage — `cl-s07-projection / tc-s07-001`

```md
| `cl-s07-projection` / `tc-s07-001` | S07 | S07 brief、Fresh Red v1〜v7、Blue repair briefs、provider/installed/dogfood recursive parity、validate、diff-check、historical scope audit、versioned review/brief identity | four parity comparisons and historical scope audit remain pass。Red v5 reviewed `03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a` and its output SHA is `1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc`。Red v6 reviewed `d96ce0807340631bbf214ed24cdfe9bd91165780`, returned FAIL（P0=0/P1=1）, and its canonical/raw SHA is `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`。Blue v6 brief SHA is `21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5`。v6 evidence/brief and two-cell correction are committed/pushed at `3d20925280f7992d8bbc8341c94829584e5c3630`。Red v7 reviewed that HEAD, returned FAIL（P0=0/P1=2、`RT-354-S07-V7-001`、`RT-354-S07-V7-002`）, and its output SHA is `471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a` | pending / blocked | current bounded action is report current-state synchronization plus append-only v6/v7 evidence and Blue v7 brief adoption。Close only after fresh Red v8 PASS（P0=0/P1=0）。Red v8 PASSまでS08〜S13、PR、merge、Issue close、Issue finishを保留する |
```

#### 7. Implementation Delegation Gate — S07 row

```md
| S07 | implementation-repair | Red v7 P1×2のreport identity/gate repairを既存Blue continuity内で行う | doc-writer | `report.md` current-state rowsとappend-only v6/v7 EAL/history、Red v7 canonical/rawおよびBlue v7 briefのimmutable evidence import | plan.md、S07 briefs、Red v6/v7 reviews、GitHub exact HEAD `3d20925280f7992d8bbc8341c94829584e5c3630` | `report.md`、`reviews/red-team-review-s07-v7.md`、`reviews/red-team-review-s07-v7-raw.md`、`artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md`だけ | provider/root Skill、parent Epic、Issue requirement/design/plan、cleanup receipt、runtime、CLI、application、domain、infra、tests、既存v1〜v6 evidence、Candidate identityを変更しない | version別SHA/path assertion、v6/v7 history/EAL、全current-row v8 gate同期、scope audit、`spec-dock validate`、`git diff --check`、fresh Red v8 | identity mismatch、placeholder SHA残存、上記4パス外の差分、既存evidence bytes変更、P0/P1 finding | append-only evidenceとcurrent reportを同期し、commit/push後のexternal exact HEADをfresh Red v8へ渡す。Red v8 PASS前はno promotion |
```

#### 8. Delegated Worker Evidence — S07 row

```md
| S07 | doc-writer | Red v6 review/briefと2セル修正は`3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済み。Red v7は同HEADをreviewしFAIL P1×2。現workerはversion別SHA訂正、append-only v6/v7 evidence adoption、v6/v7 history追加、列挙されたcurrent rowsのfresh Red v8 gate同期だけを行う | `report.md`、新規`reviews/red-team-review-s07-v7.md`、新規`reviews/red-team-review-s07-v7-raw.md`、新規`artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md`。既存v1〜v6 evidenceはread-only | Red v5=`1e67e8d...`、Red v6=`698ff25d...`、Blue v6=`21aa6dbc...`、Red v7=`471e45d7...`のSHA/path binding、current-state assertion、scope audit、validate、diff-check | Fresh Red v6 FAIL（P1×1）；Fresh Red v7 FAIL（P1×2） | current unresolved findingsは`RT-354-S07-V7-001`と`RT-354-S07-V7-002`だけ。S07はpending/blocked | 修正commit/push後のexact HEADをfresh Red v8へ渡す。Red v8 PASS前はS08〜S13、PR、merge、Issue close、Issue finishを開始しない |
```

#### 9. Parent Implementation Exception — S07 row

```md
| S07 | no delegation exception; bounded report/evidence repair remains within approved S07 artifact boundary | user request to implement and review; risk accepted: no | `report.md`、新規Red v7 canonical/raw、新規Blue v7 briefだけ。v6 evidence/briefは既存immutable input | append-only EAL/history、current-state synchronization、versioned SHA correction、scope/identity verification、fresh Red v8 handoff | no rollback needed; preserve provider source、Candidate identity、v1〜v7 Red bytes、v1〜v6 Blue evidence。失敗時はcurrent source HEADへreport/evidence差分を戻す | exact branch/HEAD、SHA/cmp、current-row assertion、four-path scope audit、validate、diff-check | out-of-scope path、evidence byte mismatch、placeholder SHA、fresh Red v8 P0/P1 finding | stop before S07 closure、S08〜S13、PR、merge、Issue close、Issue finish |
```

#### 10. Reviewer Gate Status — S07 row

```md
| S07 | docs/projection repair review | ChatGPT-Use Red Team | fresh v1〜v7 | fail / repair pending | no | no promotion; `cl-s07-projection` / `tc-s07-001`、S07 closure、S08〜S13を保留 | v1 `21a2c4c2...` FAIL P1×4；v2 `51ec4436...` FAIL P1×3；v3 `7634899d...` FAIL P1×1；v4 `7538f749...` FAIL P1×1；v5 `03ce7f0c...` FAIL P1×1（SHA `1e67e8d...`）；v6 `d96ce080...` FAIL P1×1（SHA `698ff25d...`）；v6 evidence/briefと2セル修正は`3d209252...`へcommit/push済み；v7 `3d209252...` FAIL P1×2（SHA `471e45d7...`）。次の唯一のgateは本修正後exact HEADのfresh Red v8 |
```

#### 11. Milestone / Commit Candidate Gate — S07 row

```md
| S07 | repair-pending-review | reviewed source `3d20925280f7992d8bbc8341c94829584e5c3630`。次commitのbounded scopeは`report.md` current-state/EAL/historyと新規Red v7 canonical/raw、Blue v7 brief evidenceだけ | v6 evidence/briefと2セルcorrectionは`3d209252...`へcommit/push済み。Red v7は同HEADをreviewしてFAIL P1×2。今回のresulting SHAはreportへ自己参照せず、push後に外部で確定する | commit後にclean worktree、local HEADと`origin/codex/iss-00354-chatgpt-context-contract`のexact equalityを確認する | provider Skill、parent Epic、Issue三文書、cleanup、runtime、tests、既存evidenceはno-op/read-only | `report.md`、Red v7 canonical/raw、Blue v7 briefの4パスだけを確認する | `./spec-dock/scripts/spec-dock validate`; `git diff --check`; SHA/cmp/current-state/scope assertions | fresh Red v8 PASSまでS07 closure、S08〜S13、PR、merge、Issue close、Issue finishを保留する |
```

#### 12. S90 Docs Impact Resolution row

```md
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer | S07 v1〜v7 FAIL historyを保持する。v6 review paths/SHA `698ff25d...`、Blue v6 brief path/SHA `21aa6dbc...`、v6 evidence boundary `3d209252...`、Red v7 paths/SHA `471e45d7...`をappend-only EAL/historyへ採用し、全current rowsをv7完了/fresh Red v8 next gateへ同期する。Provider/installed parity、parent wording、cleanup receiptは既存PASS証跡のまま変更しない | pending S07 fresh Red v8 |
```

#### 13. Final Code Review Gate — S07 row

```md
| ChatGPT-Use Red Team | S07 provider Skill, parent Epic §6.3, operation-specific path option docs, projection parity and report/evidence identity | v1 `21a2c4c2...` FAIL P1×4；v2 `51ec4436...` FAIL P1×3；v3 `7634899d...` FAIL P1×1；v4 `7538f749...` FAIL P1×1；v5 `03ce7f0c...` FAIL P1×1（output SHA `1e67e8d...`）；v6 `d96ce080...` FAIL P1×1（output SHA `698ff25d...`）；Blue v6 brief SHA `21aa6dbc...`；v6 evidence/briefと2セル修正は`3d209252...`へcommit/push済み；v7 `3d209252...` FAIL P1×2（output SHA `471e45d7...`、findings `RT-354-S07-V7-001`/`002`） | 7 fresh reviews; v7 is the current FAIL gate; a new fresh Red v8 is required after the bounded report/evidence repair | FAIL / repair pending |
```

#### 14. Final Spec Review Gate — S07 row

```md
| spec-reviewer / ChatGPT-Use Red Team | requirement / design / plan / report / candidate identity alignment plus S03/S04 atomic plan amendment | historical Candidate/spec baseline and S03/S04 PASS remain unchanged。S07 docs reviews v1 at `21a2c4c2...`、v2 at `51ec4436...`、v3 at `7634899d...`、v4 at `7538f749...`、v5 at `03ce7f0c...`、v6 at `d96ce080...`、v7 at `3d209252...` are FAIL with P1×4、P1×3、P1×1、P1×1、P1×1、P1×1、P1×2。Red v5/v6/v7 output SHAはそれぞれ`1e67e8d...`、`698ff25d...`、`471e45d7...` | S03/S04 gate remains passed; S07 v7 P1×2 is under bounded report/evidence repair; fresh Red v8 is pending | S07 docs gate remains blocked until fresh Red v8 PASS; no S08〜S13、PR、merge、Issue close、Issue finish |
```

#### 15. Final Commit row

既存のtable形状を変更せず、S07行だけを次へ置換する。

```md
| current branch HEAD | S07 bounded evidence repair: existing parity/scope evidence、v2〜v5 history、v6 canonical/raw evidence、Blue v6 brief、`3d209252...`の2セルcorrectionを保持し、今回のscopeをreport current-state/EAL/history同期と新規Red v7 canonical/raw、Blue v7 brief importに限定する | source HEAD `3d20925280f7992d8bbc8341c94829584e5c3630`はRed v7 reviewed sourceであり、Red v7はFAIL P1×2。今回のresulting commit SHAはreportへ先取りせず、commit/push後にlocal/origin exact tipとして外部確定する | exact pushed HEADを新規fresh Red v8 threadへ渡す。Red v8でP0=0/P1=0を確認するまで追加のS07 promotionを行わない | pending / blocked; S07 closure、S08〜S13、PR、merge、Issue close、Issue finishを保留 |
```

### S07 review history sections

既存の`## S07 Fresh Red Team review v5 と Blue repair v5`節の後、`## 最終品質ゲート`の前へ、次の2節をappendする。

#### 1. Red v6 / Blue v6 history

```md
## S07 Fresh Red Team review v6 と Blue repair v6（2026-08-05 / reviewed HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@d96ce0807340631bbf214ed24cdfe9bd91165780`。GitHub connectorでnamed branch tipとexact SHAの一致を確認し、default branch fallbackは使用していない。v1〜v5とは別のfresh read-only／defect-only Red Team threadである。
- review evidence: `reviews/red-team-review-s07-v6.md` と `reviews/red-team-review-s07-v6-raw.md`。Canonical/rawはbyte-identical、SHA-256 `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`、Git blob `3a428ff82d94fa41beb090ac1e547b0aa6aa8ba9`。
- verdict: **FAIL**（P0=0 / P1=1 / P2=0 / P3=0）。Findingは`RT-354-S07-V6-001`。対象はEAL-053 next_actionとClosure CoverageのS07行に残る完了済みv5 mutation/reviewの再要求だけであり、Provider Skill、Epic §6.3、Issue三文書、cleanup receipt、runtime、testsには新規P1がない。
- model evidence: requested `GPT-5.6 Pro`、resolved `GPT-5.6 Pro`、verified `no`。Luna／Reasoning Effort Maxの実測成功は主張しない。
- Blue repair v6 brief: `artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md`、SHA-256 `21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5`。Source HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780`、Red v6 FAIL P1×1、`report.md`の2セル限定scope、fresh Red v7停止条件を記録する。
- repository boundary: `d96ce0807340631bbf214ed24cdfe9bd91165780`から`3d20925280f7992d8bbc8341c94829584e5c3630`までに、Red v6 canonical/raw、Blue repair v6 briefがimmutable evidenceとして追加され、`report.md`は対象2行だけが変更された。Provider、Epic、Issue三文書、cleanup、runtime、testsには差分がない。
- disposition: v6 repairとevidence importは`3d20925280f7992d8bbc8341c94829584e5c3630`へcommit/push済みである。Red v7は同HEADをreviewしてFAIL P1×2を返したため、v6を再実行せず、EAL-056と次節のv7 historyをcurrent authorityとする。
```

#### 2. Red v7 / Blue v7 history

```md
## S07 Fresh Red Team review v7 と Blue repair v7（2026-08-05 / reviewed HEAD `3d20925280f7992d8bbc8341c94829584e5c3630`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@3d20925280f7992d8bbc8341c94829584e5c3630`。GitHub connectorでnamed branch tipとexact SHAの一致を確認し、default branch fallbackは使用していない。v1〜v6とは別のfresh read-only／defect-only Red Team threadである。
- review evidence: `reviews/red-team-review-s07-v7.md` と `reviews/red-team-review-s07-v7-raw.md`へ正式outputをbyte-identicalにimportする。Canonical/rawのSHA-256は`471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a`。
- verdict: **FAIL**（P0=0 / P1=2 / P2=0 / P3=0）。
  - `RT-354-S07-V7-001`: EAL-053とClosure Coverage以外のcurrent S07 gate rowsがv6未実施／fresh Red v6 pendingの状態を残している。
  - `RT-354-S07-V7-002`: Red v5 SHAにRed v6 SHAを誤結合し、Red v6 canonical/rawおよびBlue v6 briefの正式path/SHAがappend-only EALへ採用されていない。
- model evidence: requested `GPT-5.6 Pro`、resolved `GPT-5.6 Pro`、verified `no`。Luna／Reasoning Effort Maxの実測成功は主張しない。
- 正しいidentity:
  - Red v5 output SHA-256: `1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc`
  - Red v6 output SHA-256: `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`
  - Blue v6 brief SHA-256: `21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5`
  - Red v7 output SHA-256: `471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a`
- Blue repair v7 boundary: canonical `report.md`のappend-only EAL/historyと列挙されたcurrent S07 rowsを同期し、Red v7 canonical/rawと`artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md`をimmutable evidenceとして追加する。Provider/root Skill、parent Epic、Issue requirement/design/plan、cleanup receipt、runtime、CLI、application、domain、infra、tests、既存v1〜v6 evidence、Candidate identityは変更しない。
- disposition: 修正をcommit/pushした後のexact branch tipを外部で確定し、新規fresh Red v8 threadへ渡す。Red v8がP0=0/P1=0を返すまで`cl-s07-projection` / `tc-s07-001`、S07、S08〜S13、PR、merge、Issue close、Issue finishを保留する。
```

## Out of scope

今回変更可能なpathは次の4件だけ。

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  report.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  reviews/red-team-review-s07-v7.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  reviews/red-team-review-s07-v7-raw.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md
```

次はすべて変更禁止。

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/**
.agents/skills/spec-dock-issue-planning/**

parent Epic requirement.md / design.md / plan.md
Issue requirement.md / design.md / plan.md

artifacts/20260805t-projection-cleanup-analysis.md
artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md
artifacts/implementation-briefs/s07-blue-repair-v2-20260805.md
artifacts/implementation-briefs/s07-blue-repair-v3-20260805.md
artifacts/implementation-briefs/s07-blue-repair-v4-20260805.md
artifacts/implementation-briefs/s07-blue-repair-v5-20260805.md
artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md

reviews/red-team-review-s07-v1*
reviews/red-team-review-s07-v2*
reviews/red-team-review-s07-v3*
reviews/red-team-review-s07-v4*
reviews/red-team-review-s07-v5*
reviews/red-team-review-s07-v6*

src/spec_dock/assets/spec_dock/scripts/**
spec-dock/scripts/spec_dock_runtime/**
tests/**
MANIFEST.json
CHECKSUMS.sha256
Candidate ZIP / Candidate identity
unrelated docs / reports / artifacts
```

理由:

* Red v7は新規P1をcurrent report gateとv6/v7 evidence identityへ限定している。
* Provider Skill、親Epic §6.3、Issue三文書、cleanup receipt、runtime、tests、既存parity evidenceは正の条件として維持される。
* 既存Red／Blue evidenceはimmutable historyであり、SHA訂正はappend-only EALで行う。

## Verification

### 1. Exact HEAD preflight

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='3d20925280f7992d8bbc8341c94829584e5c3630'
ISSUE_ROOT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract'
REPORT="$ISSUE_ROOT/report.md"

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"
```

不一致時は停止し、default branchや添付をrepository authorityへ代用しない。

### 2. Immutable SHA/path binding

```bash
RED_V5="$ISSUE_ROOT/reviews/red-team-review-s07-v5.md"
RED_V6="$ISSUE_ROOT/reviews/red-team-review-s07-v6.md"
RED_V6_RAW="$ISSUE_ROOT/reviews/red-team-review-s07-v6-raw.md"
BLUE_V6="$ISSUE_ROOT/artifacts/implementation-briefs/s07-blue-repair-v6-20260805.md"
RED_V7="$ISSUE_ROOT/reviews/red-team-review-s07-v7.md"
RED_V7_RAW="$ISSUE_ROOT/reviews/red-team-review-s07-v7-raw.md"
BLUE_V7="$ISSUE_ROOT/artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md"

test "$(sha256sum "$RED_V5" | awk '{print $1}')" = \
  '1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc'

test "$(sha256sum "$RED_V6" | awk '{print $1}')" = \
  '698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488'
test "$(sha256sum "$RED_V6_RAW" | awk '{print $1}')" = \
  '698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488'
cmp "$RED_V6" "$RED_V6_RAW"

test "$(sha256sum "$BLUE_V6" | awk '{print $1}')" = \
  '21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5'

test "$(sha256sum "$RED_V7" | awk '{print $1}')" = \
  '471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a'
test "$(sha256sum "$RED_V7_RAW" | awk '{print $1}')" = \
  '471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a'
cmp "$RED_V7" "$RED_V7_RAW"

BLUE_V7_SHA="$(sha256sum "$BLUE_V7" | awk '{print $1}')"
test -n "$BLUE_V7_SHA"

if rg -n '<OBSERVED_BLUE_V7_BRIEF_SHA256>' "$REPORT"; then
  echo 'unresolved Blue v7 brief SHA placeholder' >&2
  exit 1
fi
```

### 3. Preserve EAL-052 / EAL-053 history

`EAL-052`と`EAL-053`はsource HEADからbyte-for-byte変更されていないことを確認する。

```bash
uv run python - "$SOURCE_HEAD" "$REPORT" <<'PY'
from pathlib import Path
import subprocess
import sys

source_head, report_path = sys.argv[1:3]
path = Path(report_path)

before = subprocess.check_output(
    ["git", "show", f"{source_head}:{path.as_posix()}"],
    text=True,
    encoding="utf-8",
)
after = path.read_text(encoding="utf-8")

def row(text: str, identifier: str) -> str:
    matches = [
        line for line in text.splitlines()
        if line.startswith(f"| {identifier} |")
    ]
    if len(matches) != 1:
        raise SystemExit(f"{identifier} row count != 1")
    return matches[0]

for identifier in ("EAL-052", "EAL-053"):
    if row(before, identifier) != row(after, identifier):
        raise SystemExit(f"{identifier} historical row was modified")

for identifier in ("EAL-054", "EAL-055", "EAL-056", "EAL-057"):
    if len([
        line for line in after.splitlines()
        if line.startswith(f"| {identifier} |")
    ]) != 1:
        raise SystemExit(f"{identifier} append-only row missing or duplicated")

print("EAL history preservation and append-only additions: pass")
PY
```

### 4. Current-state assertions

検査対象をcurrent-state sectionsへ限定し、historical narrative内の「当時のfresh Red v6」は削除対象にしない。

```bash
uv run python - "$REPORT" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")

section_pairs = (
    (
        "#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）",
        "#### 発見されたテスト / リスク（Discovered Tests）",
    ),
    (
        "#### 発見されたテスト / リスク（Discovered Tests）",
        "#### ステップ契約の完了証跡（Step Contract Closure）",
    ),
    (
        "#### ステップ契約の完了証跡（Step Contract Closure）",
        "#### テスト契約の完了証跡（Test Contract Closure）",
    ),
    (
        "#### テスト契約の完了証跡（Test Contract Closure）",
        "#### クロージャ網羅（Closure Coverage）",
    ),
    (
        "#### クロージャ網羅（Closure Coverage）",
        "#### クロージャ差分（Closure Delta）",
    ),
    (
        "#### 実装委任ゲート（Implementation Delegation Gate）",
        "#### 委任 worker 証跡（Delegated Worker Evidence）",
    ),
    (
        "#### 委任 worker 証跡（Delegated Worker Evidence）",
        "#### 親実装例外（Parent Implementation Exception）",
    ),
    (
        "#### 親実装例外（Parent Implementation Exception）",
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）",
    ),
    (
        "#### レビューゲート状態（Reviewer Gate Status）",
        "#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）",
    ),
    (
        "#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）",
        "#### 変更したファイル",
    ),
    (
        "### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）",
        "### 最終 QA ゲート（Final QA Gate）",
    ),
    (
        "### 最終コードレビューゲート（Final Code Review Gate）",
        "### 最終 spec review ゲート（Final Spec Review Gate）",
    ),
    (
        "### 最終 spec review ゲート（Final Spec Review Gate）",
        "### 最終 commit（Final Commit）",
    ),
    (
        "### 最終 commit（Final Commit）",
        "## 遭遇した問題と解決",
    ),
)

current_parts = []
for start, end in section_pairs:
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"section boundary missing or ambiguous: {start}")
    current_parts.append(text.split(start, 1)[1].split(end, 1)[0])

current = "\n".join(current_parts)

required = (
    "d96ce0807340631bbf214ed24cdfe9bd91165780",
    "3d20925280f7992d8bbc8341c94829584e5c3630",
    "1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc",
    "698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488",
    "21aa6dbc8e9f80596794feb28ea06f9d116cfb000a20fda78f148071d3ad88e5",
    "471e45d7a734d1490a29303fda6174754ef9a0eddf75e622c167226de93c199a",
    "RT-354-S07-V7-001",
    "RT-354-S07-V7-002",
    "fresh Red v8",
    "pending / blocked",
)

for token in required:
    if token not in current:
        raise SystemExit(f"required current-state token missing: {token}")

stale = (
    "fresh Red v6 required",
    "fresh Red v6 is pending",
    "v6 not yet run",
    "close after fresh Red v6 PASS",
    "fresh Red v6 PASSまで",
    "next gate is fresh Red v6",
    "ready for fresh Red v6",
    "fresh Red v6 handoff",
    "pending S07 fresh Red v6",
    "blocked until fresh v6 PASS",
    "send this exact candidate HEAD to a fresh Red v6 thread",
)

for token in stale:
    if token in current:
        raise SystemExit(f"stale current-state token remains: {token}")

print("S07 current-state v7/v8 synchronization: pass")
PY
```

### 5. Four-path scope audit

```bash
uv run python - "$SOURCE_HEAD" <<'PY'
from __future__ import annotations

import subprocess
import sys

base = sys.argv[1]

allowed = {
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v7.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v7-raw.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s07-blue-repair-v7-20260805.md",
}

tracked = set(
    subprocess.check_output(
        ["git", "diff", "--name-only", base],
        text=True,
        encoding="utf-8",
    ).splitlines()
)
untracked = set(
    subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        text=True,
        encoding="utf-8",
    ).splitlines()
)

observed = tracked | untracked
unexpected = sorted(observed - allowed)
missing = sorted(allowed - observed)

if unexpected or missing:
    raise SystemExit(
        f"scope mismatch: missing={missing}, unexpected={unexpected}"
    )

print("S07 Blue v7 four-path scope: pass")
PY
```

### 6. Repository gates

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

期待値:

```text
validate: exit 0
git diff --check: exit 0
runtime/test/parity rerun: not newly required
```

既存recursive parityとcleanup receiptは変更・再生成しない。

### 7. Commit, push, and fresh Red v8

Commit/push後にresulting HEADを外部で確定する。

```bash
PUSHED_HEAD="$(git rev-parse HEAD)"

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$PUSHED_HEAD"
test "$PUSHED_HEAD" != "$SOURCE_HEAD"
```

`PUSHED_HEAD`を同じcommit内の`report.md`へ自己参照で書かない。

Fresh Red v8 handoff:

```text
repository:
  chemitaro/spec-dock

branch:
  codex/iss-00354-chatgpt-context-contract

reviewed_head:
  commit/push後に外部で確定したexact full SHA

review_mode:
  new thread
  read-only
  defect-only
  default branch fallbackなし

required_result:
  P0=0
  P1=0
```

Fresh Red v8 PASS前は次を禁止する。

```text
cl-s07-projection closure
tc-s07-001 closure
S07 PASS / closure claim
S08〜S13 start
PR / Delivery PR
merge
Issue close
Issue finish
Candidate identity変更
```

`GPT-5.6 Luna`または`Reasoning Effort Max`のwrapper実測証跡はないため、本briefでは使用・成功を主張しない。
