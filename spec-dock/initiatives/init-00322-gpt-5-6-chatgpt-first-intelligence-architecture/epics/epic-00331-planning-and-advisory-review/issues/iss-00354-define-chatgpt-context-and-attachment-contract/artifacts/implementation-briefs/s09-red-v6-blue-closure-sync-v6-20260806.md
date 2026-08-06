# iss-00354 S09 Blue Closure-Sync v6 — Fresh Red v6 PASS採用・S09閉鎖ブリーフ

## 0. 固定identityと前提

| 項目                          | 固定値                                                                   |
| --------------------------- | --------------------------------------------------------------------- |
| Repository                  | `chemitaro/spec-dock`                                                 |
| Named branch                | `codex/iss-00354-chatgpt-context-contract`                            |
| Current exact HEAD          | `8dde4f448d5d12534f6fe3984fb261354ce9ab71`                            |
| Branch parity               | named branch tipとcurrent exact HEADは`identical`、ahead `0`、behind `0`  |
| Default branch fallback     | 禁止・未使用                                                                |
| Candidate version           | `s09-blue-repair-v2`                                                  |
| Candidate ID                | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                       |
| Implementation commit       | `470cacf5051272edfa71e9780f263d1f402a33a0`                            |
| Red v6 reviewed HEAD        | `b3e281af2c4380c9937bfcf862bd295d3d6be960`                            |
| Red v6 review identity      | `iss-00354-s09-fresh-red-v6@b3e281af2c4380c9937bfcf862bd295d3d6be960` |
| Red v6 review SHA-256       | `b64d0c5597cab46c019a54a5ff0272cf515d52eb6ef49155de7d43e8559df7bb`    |
| Red v6 verdict              | `PASS`、P0=`0`、P1=`0`、P2=`0`、P3=`0`                                    |
| Blue v5 brief SHA-256       | `b356e0884419b301e84413c418e993d901775809ad0ddee4a84d79745f63348f`    |
| Semantic mutation allowlist | `report.md`のみ                                                         |
| S09 step closure            | 本同期をcommit/push後、`committed-and-closed`                               |
| Issue-level closure claim   | `none`                                                                |
| Next gated step             | S10。S10専用のper-step brief、実装、検証、fresh reviewを別途行う                      |

GitHub connectorで、指定named branchと`8dde4f448d5d12534f6fe3984fb261354ce9ab71`の完全一致を確認した。Current HEADはRed v6 reviewed HEADより1 commit先であり、その差分はRed v6 canonical/rawのimmutable evidence import二ファイルだけである。`report.md`はRed v6 reviewed HEADから変更されていない。Current exact HEADの`report.md` Git blobは`dcb1c5d5b17aa9b00b8a4f981aba87a264f7abe3`である。

Fresh Red v6は、exact reviewed HEAD `b3e281af...`についてP0/P1を認めず、Red v5の唯一のP1が解消されたこと、`EAL-073`〜`EAL-080`、OAL、五つのcurrent-state、runtime／testsのbounded scopeが整合していることを正式PASSとした。

---

## 1. 目的

本作業は、Fresh Red v6 PASSを正式採用し、S09のcurrent-stateを閉じるための**report-only closure synchronization**である。

実施する変更は次の二点だけとする。

1. Red v6 formal reviewを`EAL-081`としてappend-only採用する。
2. 次の五つのS09 current-state surfaceを、Red v6 PASS、S09 committed/closed、S10 handoffへ置換する。

   * Implementation Delegation Gate
   * Delegated Worker Evidence
   * Parent Implementation Exception
   * Reviewer Gate Status
   * Milestone / Commit Candidate Gate

Current reportは、Red v6 review前の状態である`blue-v5-report-repair-active / red-v6-pending`を記録しているため、PASS採用後の閉鎖状態へ同期する必要がある。

本作業では、Oracle `0.17.0`実装、0.16.1回帰、reader、decoder、builders、tests、canonical三文書の設計判断を変更しない。

---

## 2. Allowlist

`ISSUE_DIR`:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract
```

### 2.1 Semantic mutationを許可する唯一の正本

```text
${ISSUE_DIR}/report.md
```

### 2.2 Immutable evidence import

Red v6 canonical/rawはcurrent exact HEADへ既にimport済みであり、内容を変更しない。

```text
${ISSUE_DIR}/reviews/red-team-review-s09-v6.md
${ISSUE_DIR}/reviews/red-team-review-s09-v6-raw.md
```

本回答をartifactとして保存する場合は、オーケストレーターが回答本文をbyte-identicalに保存する。推奨logical filename:

```text
${ISSUE_DIR}/artifacts/implementation-briefs/
s09-red-v6-blue-closure-sync-v6-20260806.md
```

このbrief artifactはsemantic mutationではなく、read-only実装指示のimmutable evidence importとして扱う。

---

## 3. Immutable pathsとidentity

次を変更しない。

```text
${ISSUE_DIR}/requirement.md
${ISSUE_DIR}/design.md
${ISSUE_DIR}/plan.md
${ISSUE_DIR}/decisions/
${ISSUE_DIR}/MANIFEST.json
${ISSUE_DIR}/CHECKSUMS.sha256
${ISSUE_DIR}/candidate-note.md
${ISSUE_DIR}/artifacts/context-and-attachment-contract.md
${ISSUE_DIR}/artifacts/decision-and-migration-ledger.md
${ISSUE_DIR}/artifacts/implementation-and-test-matrix.md
${ISSUE_DIR}/artifacts/oracle-017-failure-classification.md
${ISSUE_DIR}/artifacts/characterization/
${ISSUE_DIR}/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v5-blue-repair-v5-20260806.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v3.md
${ISSUE_DIR}/reviews/red-team-review-s09-v3-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v5.md
${ISSUE_DIR}/reviews/red-team-review-s09-v5-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v6.md
${ISSUE_DIR}/reviews/red-team-review-s09-v6-raw.md
src/spec_dock/
tests/
```

次のidentityは更新しない。

```text
Candidate version:
  s09-blue-repair-v2

Candidate ID:
  iss-00354-s09-blue-repair-v2-20260805T225843Z

Implementation commit:
  470cacf5051272edfa71e9780f263d1f402a33a0
```

次のledger行はbyte-identicalに維持する。

```text
EAL-073
EAL-074
EAL-075
EAL-076
EAL-077
EAL-078
EAL-079
EAL-080
OAL-001
OAL-002
```

Red v1〜v5のFAILは履歴として保持する。Red v6 PASSによって、過去FAIL行をPASSへ書き換えない。

---

## 4. Evidence Adoption Ledger — exact `EAL-081`

`EAL-080`の直後、Objective Alignment Ledger見出しの直前へ、次の14-field rowを一行追加する。

```markdown
| EAL-081 | adopted | `reviews/red-team-review-s09-v6.md` | chatgpt-use-red-team | Candidate `iss-00354-s09-blue-repair-v2-20260805T225843Z`、exact reviewed HEAD `b3e281af2c4380c9937bfcf862bd295d3d6be960` に対するfresh defect-only Red Team v6はPASS（P0=0/P1=0/P2=0/P3=0）。Red v5の唯一のfinding `RT-354-S09-V5-001`は解消済みであり、EAL-073〜EAL-080、OAL、五つのS09 current-state、runtime／reader／builders／testsのbounded scopeに新しいP0/P1を認めなかった | `reviews/red-team-review-s09-v6.md`, `reviews/red-team-review-s09-v6-raw.md`, `report.md` | S09 fresh Red v6 final gate and closure evidence | Red v6はnamed branchのexact reviewed HEADと37論理ファイルをread-onlyで照合し、37/37のGit blob identity、report-only semantic scope、Candidate identity不変、runtime／tests／canonical三文書／ADR／characterization非変更を確認した。Oracle browser smoke、pytest、Ruff、Mypy、SpecDock validateは再実行しておらず、既存committed evidenceとしてのみ確認した | fresh_pass | canonical/raw byte-identical、SHA-256 `b64d0c5597cab46c019a54a5ff0272cf515d52eb6ef49155de7d43e8559df7bb`; reviewed branch/HEAD `codex/iss-00354-chatgpt-context-contract` / `b3e281af2c4380c9937bfcf862bd295d3d6be960`; review identity `iss-00354-s09-fresh-red-v6@b3e281af2c4380c9937bfcf862bd295d3d6be960`; Candidate version `s09-blue-repair-v2`; Candidate ID `iss-00354-s09-blue-repair-v2-20260805T225843Z`; implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`; Blue v5 brief SHA-256 `b356e0884419b301e84413c418e993d901775809ad0ddee4a84d79745f63348f` | issue orchestrator | ChatGPT-Use Red Team | no | Red v6 PASSをS09 final gateとして採用し、S09をcommitted-and-closedへ同期する。S10は自身のper-step brief、実装、検証、fresh reviewを経て開始する。PR、merge、Issue close、Issue finishはIssue-level gateまで保留する |
```

### `EAL-081` invariants

* `adoption_status=adopted`
* `evidence_strength=fresh_pass`
* `blocking=no`
* Verdictは`PASS`
* P0/P1/P2/P3はすべて`0`
* Reviewed HEADは`b3e281af...`
* Current evidence-import HEAD `8dde4f...`をRed v6 reviewed HEADとして扱わない
* Candidate version、Candidate ID、implementation commitを変更しない
* Blue v6 closure-syncの将来commit SHAを書かない
* `EAL-073`〜`EAL-080`のhistorical next actionを変更しない
* Issue全体のcloseを主張しない

---

## 5. S09 current-state surfaceのexact replacement rows

以下の五行だけを置換する。

## 5.1 Implementation Delegation Gate

```markdown
| S09 | completed-and-closed | Exact Oracle 0.17.0 compatibility profile、0.16.1回帰、version-bound reader、completed-only decoder、profile-owned harvest／capture builders、unknown-version fail-closed、Blue v1〜v5 repairsをFresh Red v6 PASSで閉じる | dev-coder / issue orchestrator | S09 exact profile／reader implementation、focused infra tests、characterization receipts、Blue repair v1〜v5、Red v1〜v6 review、report closure evidence | plan.md、S09 briefs、EAL-067〜EAL-081、Candidate identity、implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`、Red v6 formal review | 本closure-syncでは`report.md`への`EAL-081`追加と五つのS09 current-state row閉鎖だけを許可する。S10は別per-step brief／reviewで開始する | runtime、tests、provider/projection、wrapper/API、generic recovery、requirement/design/plan、ADR、MANIFEST、CHECKSUMS、characterization、Candidate identity、implementation commit、既存EAL/OAL、Red／Blue evidence bytes、PR、merge、Issue close、Issue finishを変更しない | current branch／HEAD、Red v6 canonical/raw SHA/cmp、Blue v5 brief SHA、EAL-073〜EAL-081 sequence／field count、OAL no-op、五current-state closed assertion、immutable path audit、SpecDock validate、diff-check、post-push clean/parity | identity／SHA不一致、historical EAL/OAL mutation、report外semantic diff、Red v6 PASSの不整合、validation failure、S10実装の混入では閉鎖せず停止する | report-only closure diff、EAL-081、五closed current-state rows、S09 closure evidence、S10 per-step handoff。Blue v6 resulting SHAはpost-push external evidenceへ記録する | Fresh Red v6は`b3e281af2c4380c9937bfcf862bd295d3d6be960`でPASS（P0=0/P1=0/P2=0/P3=0）。Current exact HEAD `8dde4f448d5d12534f6fe3984fb261354ce9ab71`はRed v6 canonical/raw importだけを追加した状態であり、Red v6 PASSを`EAL-081`へ採用してS09をcommitted-and-closedとする。Issue-level closure claimは`none`、次のactive gateはS10 |
```

## 5.2 Delegated Worker Evidence

```markdown
| S09 | dev-coder / issue orchestrator | Exact 0.16.1／0.17.0 profile、reader、decoder、builders、fail-closed testsを実装し、Blue v1〜v5で各Red findingをbounded修正した。Fresh Red v6はBlue v5 report-only Candidateとbounded runtime/test scopeを正式PASSし、Red v5 findingの解消を確認した。本closure-syncではRed v6を`EAL-081`へ採用し、S09 current-stateだけをclosedへ更新する | Historical implementationはS09 provider/test 4ファイルとS09 evidence artifacts。本closure-syncのsemantic mutationは`report.md`のみ。Red v6 canonical/rawと本briefはimmutable evidence import | Existing committed S09 focused／infra／static evidenceを維持する。Red v6は37/37 Git blob identity、EAL/OAL、五current-state、runtime／reader／testsをread-only確認しP0/P1=0。Red v6ではOracle browser smoke、pytest、Ruff、Mypy、SpecDock validateを再実行していない | Fresh Red v1 FAIL（P1=2）、v2 FAIL（P1=2）、v3 FAIL（P1=1）、v4 FAIL（P1=1）、v5 FAIL（P1=1）、v6 PASS（P0=0/P1=0/P2=0/P3=0） | S09内の未解決blockerはない。Submission evidence、artifact-pending、capture-specific action、bounded recovery、stage-specific public mappingはS10の明示scopeであり、S09 closureの未解決欠陥ではない | `EAL-081`を採用してS09をcommitted-and-closedとし、S10専用brief／implementation／verification／fresh reviewへ進む。Issue-level PR、merge、Issue close、Issue finishは行わない |
```

## 5.3 Parent Implementation Exception

```markdown
| S09 | no delegation exception; Fresh Red v6 PASSの正式採用とS09 closure current-state同期をissue orchestratorがreport-onlyで実施する | user request to adopt the formal PASS and continue to S10; risk accepted: no | Semantic mutationは`report.md`のみ。Red v6 canonical/rawと本Blue closure-sync briefのexact-byte importは別証跡操作 | `EAL-081`のappend-only追加、五つのS09 current rowをcommitted-and-closedへ同期、report-only commit/push、S10 per-step handoff | 失敗時はcurrent source HEAD `8dde4f448d5d12534f6fe3984fb261354ce9ab71`のreportへ戻す。Candidate identity、implementation commit、EAL-073〜EAL-080、OAL-001/OAL-002、Red v1〜v6、Blue briefs、receiptsを保持する | named branch／source HEAD、Red v6 SHA/cmp、Blue v5 brief SHA、historical EAL/OAL equality、closed-row assertion、scope audit、SpecDock validate、diff-check、post-push worktree clean／upstream parity | Fresh Red v6 PASS（P0=0/P1=0/P2=0/P3=0）はS09のfinal reviewer gateを満たす。追加のS09 fresh reviewは要求しない。S10は自身のper-step briefとreview gateを持つ | identity mismatch、evidence byte mismatch、report外semantic diff、historical evidence mutation、future commit SHAの自己参照では停止する。S09は閉じるが、PR、merge、Issue close、Issue finishは行わない |
```

## 5.4 Reviewer Gate Status

```markdown
| S09 | implementation review | ChatGPT-Use Red Team | fresh v1〜v6 | pass | no | Red v1とv2は各P1=2、Red v3〜v5は各P1=1のFAIL履歴として保持する。Fresh Red v6はexact reviewed HEAD `b3e281af2c4380c9937bfcf862bd295d3d6be960`でPASS（P0=0/P1=0/P2=0/P3=0）し、Red v5 finding `RT-354-S09-V5-001`の解消、EAL-073〜EAL-080／OAL／五current-state／bounded runtime-test scopeの整合を確認した。Red v6を`EAL-081`へ採用し、S09をclosedとしてS10 per-step gateへpromoteする | EAL-067〜EAL-081、`reviews/red-team-review-s09-v6.md`／raw SHA-256 `b64d0c5597cab46c019a54a5ff0272cf515d52eb6ef49155de7d43e8559df7bb`、review identity `iss-00354-s09-fresh-red-v6@b3e281af2c4380c9937bfcf862bd295d3d6be960`、Candidate version `s09-blue-repair-v2`、Candidate ID `iss-00354-s09-blue-repair-v2-20260805T225843Z`、implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`、Blue v5 brief SHA-256 `b356e0884419b301e84413c418e993d901775809ad0ddee4a84d79745f63348f`、current evidence-import HEAD `8dde4f448d5d12534f6fe3984fb261354ce9ab71` |
```

## 5.5 Milestone / Commit Candidate Gate

```markdown
| S09 | committed-and-closed | Candidate version `s09-blue-repair-v2`、Candidate ID `iss-00354-s09-blue-repair-v2-20260805T225843Z`、implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`、S09 characterization／brief／Red v1〜v6／Blue v1〜v5 evidence、`EAL-067`〜`EAL-081`をS09 final ledgerとして保持する。本closure-syncは`report.md`だけを変更する | Implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`、Fresh Red v6 reviewed HEAD `b3e281af2c4380c9937bfcf862bd295d3d6be960`、Red v6 evidence-import HEAD `8dde4f448d5d12534f6fe3984fb261354ce9ab71`、final S09 ledger `EAL-067`〜`EAL-081`。Blue v6 closure-syncのresulting commit SHAはreportへ自己参照せずpost-push handoffへ外部記録する | Closure-sync commit/push後にworktree clean、HEADとupstream exact equality、ahead `0`／behind `0`を確認し、resulting SHAをS10 handoffへ外部指定する | Fresh Red v6 PASSによりS09 runtime／tests／canonical docsへの追加mutationは不要。Current changeはPASS採用とcurrent-state closureのためのreport-only synchronizationである | `src/spec_dock/`、`tests/`、requirement/design/plan、ADR、MANIFEST、CHECKSUMS、Candidate files、characterization receipts、EAL-073〜EAL-080、OAL-001/OAL-002、Red v1〜v6、Blue v1〜v5 bytes | `./spec-dock/scripts/spec-dock validate`; `git diff --check`; EAL sequence／14-field assertion; historical EAL/OAL equality; five-current-row closed assertion; immutable path audit; scoped `git diff --name-only`; post-push parity | S09はFresh Red v6 PASSをもってcommitted-and-closed。次はS10専用のChatGPT-Use brief、実装、検証、fresh reviewを開始する。Issue-level closure claimは`none`であり、PR、merge、Issue close、Issue finishは後続whole-Issue gateまで保留する |
```

---

## 6. 禁止事項

次を行わない。

* Runtime、tests、provider、installed／dogfood projectionの変更
* Wrapper、Oracle API、alternate backend、generic recoveryの変更
* `requirement.md`、`design.md`、`plan.md`、ADRの変更
* `MANIFEST.json`、`CHECKSUMS.sha256`の変更または再生成
* Candidate ZIP、Candidate version、Candidate ID、implementation commitの変更
* Characterization receiptの変更
* `EAL-073`〜`EAL-080`または`OAL-001`／`OAL-002`の変更
* Red v1〜v6 canonical/rawの編集、再生成、要約置換
* 既存Blue briefの変更
* Red v1〜v5のFAIL履歴の上書き
* Red v6 PASSをFAILへ戻す変更
* S10のimplementation、artifact-pending、capture、fallback、retry、stage taxonomyの先取り
* Blue v6の将来commit SHAを事前の`report.md`へ記載すること
* PR作成、merge、Issue close、Issue finish
* default branchまたは別branchの利用

---

## 7. 実行前assertion

### 7.1 Branch／HEAD／worktree

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE='8dde4f448d5d12534f6fe3984fb261354ce9ab71'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE"
test "$(git rev-parse '@{upstream}')" = "$SOURCE"
test -z "$(git status --short)"
```

### 7.2 Red v6 reviewed HEADからcurrent HEADまでの差分

```bash
git diff --name-only \
  b3e281af2c4380c9937bfcf862bd295d3d6be960...\
8dde4f448d5d12534f6fe3984fb261354ce9ab71
```

期待値は次の二ファイルだけ。

```text
${ISSUE_DIR}/reviews/red-team-review-s09-v6.md
${ISSUE_DIR}/reviews/red-team-review-s09-v6-raw.md
```

### 7.3 Current report blob

```bash
REPORT="$ISSUE_DIR/report.md"

test "$(git rev-parse \
  "8dde4f448d5d12534f6fe3984fb261354ce9ab71:$REPORT")" = \
  "dcb1c5d5b17aa9b00b8a4f981aba87a264f7abe3"
```

### 7.4 Red v6 canonical/raw identity

```bash
sha256sum \
  "$ISSUE_DIR/reviews/red-team-review-s09-v6.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v6-raw.md"
```

双方の期待値:

```text
b64d0c5597cab46c019a54a5ff0272cf515d52eb6ef49155de7d43e8559df7bb
```

```bash
cmp \
  "$ISSUE_DIR/reviews/red-team-review-s09-v6.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v6-raw.md"
```

### 7.5 Blue v5 brief identity

```bash
test "$(sha256sum \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v5-blue-repair-v5-20260806.md" \
  | awk '{print $1}')" = \
  "b356e0884419b301e84413c418e993d901775809ad0ddee4a84d79745f63348f"
```

### 7.6 Existing EAL／OAL shape

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()

for number in range(73, 81):
    identifier = f"EAL-{number:03d}"
    matches = [line for line in lines if line.startswith(f"| {identifier} |")]
    assert len(matches) == 1, (identifier, len(matches))

assert not any(line.startswith("| EAL-081 |") for line in lines)

positions = [
    next(i for i, line in enumerate(lines) if line.startswith(f"| EAL-{number:03d} |"))
    for number in range(73, 81)
]
assert positions == list(range(positions[0], positions[0] + 8)), positions

for identifier in ("OAL-001", "OAL-002"):
    matches = [line for line in lines if line.startswith(f"| {identifier} |")]
    assert len(matches) == 1, (identifier, len(matches))
PY
```

---

## 8. Patch手順

1. Named branch、current exact HEAD、upstream、clean状態を確認する。
2. Red v6 reviewed HEADからcurrent HEADまでの差分がRed v6 canonical/rawだけであることを確認する。
3. Current `report.md` Git blobを確認する。
4. Red v6 canonical/rawのSHA-256とbyte identityを確認する。
5. Blue v5 briefのSHA-256を確認する。
6. `EAL-080`直後へexact `EAL-081`を追加する。
7. Implementation Delegation GateのS09行を`completed-and-closed`へ置換する。
8. Delegated Worker EvidenceのS09行を置換する。
9. Parent Implementation ExceptionのS09行を置換する。
10. Reviewer Gate StatusのS09行を`pass`へ置換する。
11. Milestone / Commit Candidate GateのS09行を`committed-and-closed`へ置換する。
12. `EAL-073`〜`EAL-080`、`OAL-001`／`OAL-002`を変更しない。
13. Historical Red v1〜v5 FAILとRed v6 PASSを保持する。
14. Runtime、tests、canonical docs、Candidate identityを変更しない。
15. Report validation、immutable checks、SpecDock validate、diff-checkを実行する。
16. Report-only closure-syncをcommitし、named branchへpushする。
17. Push後のresulting exact HEAD、upstream parity、clean状態を確認する。
18. Resulting SHAを`report.md`へ書き戻さず、S10 handoffへ外部指定する。

---

## 9. Immutable checks

### 9.1 Historical EAL／OAL equality

```bash
python - <<'PY'
from pathlib import Path
import subprocess

SOURCE = "8dde4f448d5d12534f6fe3984fb261354ce9ab71"
REPORT = (
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
    "report.md"
)

before = subprocess.check_output(
    ["git", "show", f"{SOURCE}:{REPORT}"],
    text=True,
)
after = Path(REPORT).read_text(encoding="utf-8")

def row(text: str, identifier: str) -> str:
    matches = [
        line for line in text.splitlines()
        if line.startswith(f"| {identifier} |")
    ]
    assert len(matches) == 1, (identifier, len(matches))
    return matches[0]

for number in range(73, 81):
    identifier = f"EAL-{number:03d}"
    assert row(before, identifier) == row(after, identifier), identifier

for identifier in ("OAL-001", "OAL-002"):
    assert row(before, identifier) == row(after, identifier), identifier

row(after, "EAL-081")
print("historical EAL/OAL unchanged; EAL-081 present")
PY
```

### 9.2 Runtime、tests、canonical files

```bash
git diff --exit-code \
  8dde4f448d5d12534f6fe3984fb261354ce9ab71 \
  -- \
  "$ISSUE_DIR/requirement.md" \
  "$ISSUE_DIR/design.md" \
  "$ISSUE_DIR/plan.md" \
  "$ISSUE_DIR/decisions" \
  "$ISSUE_DIR/MANIFEST.json" \
  "$ISSUE_DIR/CHECKSUMS.sha256" \
  "$ISSUE_DIR/candidate-note.md" \
  "$ISSUE_DIR/artifacts/characterization" \
  src/spec_dock \
  tests
```

### 9.3 Existing reviews／briefs

```bash
git diff --exit-code \
  8dde4f448d5d12534f6fe3984fb261354ce9ab71 \
  -- \
  "$ISSUE_DIR/reviews" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v5-blue-repair-v5-20260806.md"
```

本brief artifactを今回追加する場合は、その一ファイルだけを上記checkの例外として扱い、byte-identical保存を別途検証する。

---

## 10. Report validation

### 10.1 EAL sequenceと14 fields

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()

selected = [
    line.split("|")[1].strip()
    for line in lines
    if line.startswith(tuple(f"| EAL-{number:03d} |" for number in range(73, 82)))
]
assert selected == [f"EAL-{number:03d}" for number in range(73, 82)], selected

matches = [line for line in lines if line.startswith("| EAL-081 |")]
assert len(matches) == 1
fields = [part.strip() for part in matches[0].strip("|").split("|")]
assert len(fields) == 14, len(fields)
PY
```

### 10.2 OAL no-op

```bash
python - <<'PY'
from pathlib import Path
import subprocess

SOURCE = "8dde4f448d5d12534f6fe3984fb261354ce9ab71"
REPORT = (
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
    "report.md"
)

before = subprocess.check_output(
    ["git", "show", f"{SOURCE}:{REPORT}"],
    text=True,
).splitlines()
after = Path(REPORT).read_text(encoding="utf-8").splitlines()

for identifier in ("OAL-001", "OAL-002"):
    old = [line for line in before if line.startswith(f"| {identifier} |")]
    new = [line for line in after if line.startswith(f"| {identifier} |")]
    assert old == new, identifier
PY
```

### 10.3 Five-current-row closure assertion

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")

sections = (
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
)

current = []
for start, end in sections:
    assert text.count(start) == 1, start
    assert text.count(end) == 1, end
    current.append(text.split(start, 1)[1].split(end, 1)[0])

current_text = "\n".join(current)

required = (
    "completed-and-closed",
    "committed-and-closed",
    "Fresh Red v6",
    "b3e281af2c4380c9937bfcf862bd295d3d6be960",
    "EAL-081",
    "S10",
    "Issue-level closure claim",
)

for token in required:
    assert token in current_text, token

forbidden = (
    "blue-v5-report-repair-active",
    "red-v6-pending",
    "Blue v5 report repair active",
    "fresh Red v6 pending",
    "Blue v5 report-only repair Candidateをfresh Red v6",
    "P0/P1=0となるまでS09をpromoteまたはcloseしない",
)

for token in forbidden:
    assert token not in current_text, token

print("S09 current-state closed; S10 handoff active")
PY
```

### 10.4 Repository validation

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

今回のclosure-syncはreport-onlyであるため、pytest、Ruff、Mypy、Oracle browser smokeの新しい実行結果を再主張しない。既存S09 implementation evidenceとRed v6のread-only確認を保持する。

### 10.5 Scope audit

Working-tree semantic diff:

```bash
git diff --name-only
```

期待値:

```text
${ISSUE_DIR}/report.md
```

本brief artifactを同じworktreeへ保存した場合に限り、追加で次を許容する。

```text
${ISSUE_DIR}/artifacts/implementation-briefs/
s09-red-v6-blue-closure-sync-v6-20260806.md
```

Brief artifactはsemantic mutationではない。

---

## 11. Commit／push

推奨commit message:

```text
docs(iss-00354): close S09 after Red v6 PASS
```

Semantic closure-sync:

```bash
git add -- "$ISSUE_DIR/report.md"

git commit -m \
  "docs(iss-00354): close S09 after Red v6 PASS"

git push origin \
  HEAD:codex/iss-00354-chatgpt-context-contract
```

本brief artifactをrepositoryへ保存する場合、オーケストレーターはbyte-identical evidenceとして同一commitまたは明示的な別evidence commitへ追加できる。どちらの場合もsemantic mutationは`report.md`だけである。

Push後:

```bash
test -z "$(git status --short)"

RESULTING_HEAD="$(git rev-parse HEAD)"
UPSTREAM_HEAD="$(git rev-parse '@{upstream}')"

test "$RESULTING_HEAD" = "$UPSTREAM_HEAD"
test "$(git rev-list --left-right --count HEAD...'@{upstream}')" = $'0\t0'

printf 's09_closure_resulting_head=%s\n' "$RESULTING_HEAD"
```

`RESULTING_HEAD`を事前の`report.md`へ書き戻さない。

---

## 12. S09 closureとS10 handoff

Closure-sync commit/push後の正規状態:

```text
S09 step state
  committed-and-closed

S09 reviewer gate
  Fresh Red v6 PASS
  P0=0
  P1=0
  P2=0
  P3=0

S09 Candidate version
  s09-blue-repair-v2

S09 Candidate ID
  iss-00354-s09-blue-repair-v2-20260805T225843Z

S09 implementation commit
  470cacf5051272edfa71e9780f263d1f402a33a0

S09 closure review identity
  iss-00354-s09-fresh-red-v6@b3e281af2c4380c9937bfcf862bd295d3d6be960

S09 final EAL
  EAL-081

S09 closure-sync resulting HEAD
  <post-push exact SHA>

next active step
  S10

S10 start condition
  S10専用のChatGPT-Use implementation briefを作成する
  S10 plan allowlistとstop gateを再確認する
  S10 implementation／tests／fresh reviewを別ゲートで行う

Issue-level closure claim
  none

PR
  not created by this task

merge
  not performed

Issue close / finish
  not performed
```

S10では、S09で意図的に未実装のsubmission evidence、artifact-pending、capture-specific action、bounded retry、stage-specific public mappingを、S10 planと専用briefに従って扱う。本closure-syncでS10 production behaviorを先取りしない。

---

## 13. 停止条件

次のいずれかではcommit／pushせず停止する。

1. Named branch tipが`8dde4f448d5d12534f6fe3984fb261354ce9ab71`と一致しない。
2. Default branchまたは別branchの利用が必要になる。
3. Red v6 reviewed HEADからcurrent HEADまでの差分がcanonical/raw二ファイル以外を含む。
4. Current `report.md` Git blobが`dcb1c5d5b17aa9b00b8a4f981aba87a264f7abe3`と一致しない。
5. Red v6 canonical/raw SHAが`b64d0c5597cab46c019a54a5ff0272cf515d52eb6ef49155de7d43e8559df7bb`と一致しない。
6. Red v6 canonical/rawがbyte-identicalでない。
7. Blue v5 brief SHAが`b356e0884419b301e84413c418e993d901775809ad0ddee4a84d79745f63348f`と一致しない。
8. `EAL-073`〜`EAL-080`が欠落、重複、順序違い、または変更されている。
9. `EAL-081`が既に別意味で存在する。
10. `OAL-001`または`OAL-002`の変更が必要になる。
11. 五つのS09 current-state row以外のhistorical row変更が必要になる。
12. Runtime、tests、canonical三文書、ADR、MANIFEST、CHECKSUMS、Candidate、characterizationの変更が必要になる。
13. Candidate version、Candidate ID、implementation commitの変更が必要になる。
14. Red v1〜v5のFAIL履歴を変更する必要が生じる。
15. Red v6 PASSを変更する必要が生じる。
16. Blue v6 closure-syncの将来commit SHAを事前reportへ自己参照する必要が生じる。
17. SpecDock validate、`git diff --check`、EAL sequence／field count、historical equality、closed current-state assertionのいずれかが失敗する。
18. S10 production implementationを同じ作業へ含める必要が生じる。
19. PR、merge、Issue close、Issue finishを同じ作業で行う必要が生じる。

完了状態は次に限定する。

```text
Fresh Red v6 PASS adopted as EAL-081
S09 current-state = committed-and-closed
S09 closure-sync committed and pushed
resulting branch parity = identical / ahead 0 / behind 0
S10 = next gated step
Issue-level closure claim = none
PR / merge / Issue close / Issue finish = not performed
```
