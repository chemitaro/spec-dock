# iss-00354 S09 Blue Repair v5 — Red v5 current-state report同期ブリーフ

## 0. 固定identityとGitHub確認結果

| 項目                                                 | 固定値                                                                          |
| -------------------------------------------------- | ---------------------------------------------------------------------------- |
| Repository                                         | `chemitaro/spec-dock`                                                        |
| Named branch                                       | `codex/iss-00354-chatgpt-context-contract`                                   |
| Semantic source HEAD before Red v5 evidence import | `d52f8ab1df0d34be36880d1be64f6b2605a63065`                                   |
| Default branch fallback                            | 禁止・未使用                                                                       |
| Candidate version                                  | `s09-blue-repair-v2`                                                         |
| Candidate ID                                       | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                              |
| Implementation commit                              | `470cacf5051272edfa71e9780f263d1f402a33a0`                                   |
| Red v5 reviewed HEAD                               | `d52f8ab1df0d34be36880d1be64f6b2605a63065`                                   |
| Red v5 review SHA-256                              | `7bda038fdb085493d8d847ac1ac778c9968516b3a5d7e4c680e1b831585d882b`           |
| Red v5 verdict                                     | `FAIL`、P0=`0`、P1=`1`、P2=`0`、P3=`0`                                           |
| Active finding                                     | `RT-354-S09-V5-001`                                                          |
| Semantic mutation allowlist                        | `report.md`のみ                                                                |
| `closure_claim`                                    | `none`                                                                       |
| Expected handoff                                   | Blue v5 report-only repairをcommit/pushし、resulting exact HEADをfresh Red v6へ渡す |

GitHub connectorでnamed branchを確認した。Named branchはsemantic source HEAD `d52f8ab1...`よりahead `1`、behind `0`であり、差分はRed v5 canonical/raw reviewの二ファイル追加だけである。これはユーザーが指定した「source HEAD before evidence import」と整合する。`report.md`のGit blobはsource HEADとnamed branchの双方で同じ`3cb21bc59865ef419d4806d40459f5cde28f6a49`であり、Red v5 evidence importによるreport mutationはない。

Red v5は、Blue v4のreport同期が既に`d52f8ab1...`へcommit/pushされている一方、五つのS09 current-state行がBlue v4を未完了・commit/push前として扱う一世代遅れだけをP1とした。Runtime、Oracle `0.17.0` profile、reader、decoder、builders、0.16.1回帰、tests、requirement／design／planには新しいP0/P1を認めていない。

---

## 1. Blue v5の最小修正目的

本修正は次の二点だけを行う。

1. Red v5 formal reviewを`EAL-080`としてappend-only採用する。
2. 次の五つのS09 current-state surfaceを、事実に合わせて置換する。

```text
Red v5 FAIL
  ↓
Blue v5 report-only repair active
  ↓
fresh Red v6 pending
```

対象surface:

1. Implementation Delegation Gate
2. Delegated Worker Evidence
3. Parent Implementation Exception
4. Reviewer Gate Status
5. Milestone / Commit Candidate Gate

`blue-v5-report-repair-active`は、**未commit・未pushを意味しない**。Blue v5のreport-only repair Candidateがcurrent review targetであり、fresh Red v6による確認待ちであることを表すgate stateとする。Blue v5のresulting commit SHAは、自己参照を避けるため事前の`report.md`へ記録せず、push後のRed v6 handoffで外部指定する。

Current reportでは`EAL-073`〜`EAL-079`が連番で存在し、`OAL-001`／`OAL-002`も存在する。一方、五つのcurrent-state行にはBlue v4を「repair active」「実施中」「commit/push後」とする旧状態が残っている。

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

### 2.2 別のimmutable evidence importとして扱うファイル

Red v5 canonical/rawは、semantic repairとは別のexact-byte evidence importである。

```text
${ISSUE_DIR}/reviews/red-team-review-s09-v5.md
${ISSUE_DIR}/reviews/red-team-review-s09-v5-raw.md
```

本回答を後でartifactとして保存する場合:

```text
${ISSUE_DIR}/artifacts/implementation-briefs/
s09-red-v5-blue-repair-v5-20260806.md
```

これらは内容を編集、短縮、再format、要約置換しない。

### 2.3 Expected semantic diff

```text
${ISSUE_DIR}/report.md
```

だけである。

Named branch全体をsemantic source HEAD `d52f8ab1...`と比較した場合は、別操作でimportされたRed v5 canonical/raw、および後からbyte-identicalに保存される本brief artifactが追加差分として存在してよい。

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
${ISSUE_DIR}/reviews/red-team-review-s09-v1.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v3.md
${ISSUE_DIR}/reviews/red-team-review-s09-v3-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4-raw.md
src/spec_dock/
tests/
```

次のidentityを更新しない。

```text
Candidate version:
  s09-blue-repair-v2

Candidate ID:
  iss-00354-s09-blue-repair-v2-20260805T225843Z

Implementation commit:
  470cacf5051272edfa71e9780f263d1f402a33a0
```

また、次の既存ledger行を一文字も変更しない。

```text
EAL-073
EAL-074
EAL-075
EAL-076
EAL-077
EAL-078
EAL-079
OAL-001
OAL-002
```

OALは今回のcurrent-state修正対象外である。Blue v4文脈を含む`OAL-002`もhistorical alignment evidenceとしてbyte-identicalに維持する。

---

## 4. Evidence Adoption Ledger — exact `EAL-080`

`EAL-079`の直後、Objective Alignment Ledger見出しの前へ次の一行を追加する。

```markdown
| EAL-080 | adopted | `reviews/red-team-review-s09-v5.md` | chatgpt-use-red-team | Candidate `iss-00354-s09-blue-repair-v2-20260805T225843Z`、exact reviewed HEAD `d52f8ab1df0d34be36880d1be64f6b2605a63065` に対するfresh defect-only Red Team v5はFAIL（P0=0/P1=1/P2=0/P3=0）。Red v3 pendingの旧不整合は解消済みであり、唯一のfindingはBlue v4 report/evidence同期がcommit/push済みであるにもかかわらず五つのS09 current-state surfaceがBlue v4を未完了・commit/push前として扱う`RT-354-S09-V5-001`である | `reviews/red-team-review-s09-v5.md`, `reviews/red-team-review-s09-v5-raw.md`, `report.md` | S09 fresh Red v5 gate and Blue repair v5 input | Red v5はnamed branchのexact reviewed HEADと34論理ファイルをread-onlyで照合し、runtime、tests、Oracle 0.17.0 profile/reader/decoder/builders、0.16.1回帰、requirement、design、planに新しいP0/P1を認めていない。修正はreport current-stateとformal evidenceの同期だけに限定する | fresh_fail | canonical/raw byte-identical、SHA-256 `7bda038fdb085493d8d847ac1ac778c9968516b3a5d7e4c680e1b831585d882b`; reviewed branch/HEAD `codex/iss-00354-chatgpt-context-contract` / `d52f8ab1df0d34be36880d1be64f6b2605a63065`; Candidate version `s09-blue-repair-v2`; Candidate ID `iss-00354-s09-blue-repair-v2-20260805T225843Z`; implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0` | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S09 closure | Blue v5で五つのS09 current-state surfaceをreport-only同期し、resulting exact HEADをfresh Red v6へ渡す。P0/P1=0になるまでS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |
```

### 4.1 `EAL-080` invariants

* 既存EAL schemaと同じ14 fields。
* `adoption_status=adopted`。
* `evidence_strength=fresh_fail`。
* Red v5のFAIL、P0=`0`、P1=`1`を維持する。
* Findingは`RT-354-S09-V5-001`だけ。
* Reviewed HEADは`d52f8ab1...`。
* Canonical/raw SHAは`7bda038f...d882b`。
* Blue v5の将来commit SHAは記載しない。
* Historical next actionを現在時制へ書き換えない。
* `EAL-073`〜`EAL-079`は不変。

Red v5 canonical/rawはbyte-identicalであり、同じSHA-256を持つ。 

---

## 5. Current-state surfaceのexact replacement rows

Historical EAL、past review narrative、OAL、Candidate identityは変更しない。以下の五つのS09行だけを置換する。

## 5.1 Implementation Delegation Gate

```markdown
| S09 | review-failed / blue-v5-report-repair-active / red-v6-pending | Exact Oracle 0.17.0 implementationとBlue v1〜v4の修正結果は維持し、Red v5唯一のP1 `RT-354-S09-V5-001`であるcurrent-stateの一世代遅れだけをreport-onlyで同期する | issue orchestrator | `report.md`のappend-only `EAL-080`と五つのS09 current-state rows。Red v5 canonical/rawと本briefのimportは別のimmutable evidence操作 | plan.md、S09 briefs、EAL-067〜EAL-080、Red v1〜v5 formal reviews、semantic source HEAD `d52f8ab1df0d34be36880d1be64f6b2605a63065`、current Issue scope | `EAL-080`追加、Implementation Delegation／Worker／Parent Exception／Reviewer Gate／Milestone GateのS09行同期、report-only evidence repair、resulting branch parity確認、fresh Red v6 handoff | runtime、tests、provider/projection、wrapper/API、generic recovery、requirement/design/plan、ADR、MANIFEST、CHECKSUMS、characterization、Candidate identity、implementation commit、既存EAL-073〜EAL-079、OAL-001/OAL-002、Red v1〜v5 bytes、既存Blue briefs、S10以降、PR、merge、closeを変更しない | semantic source／evidence-import分離、Red v5 canonical/raw SHA/cmp、Blue v4 brief SHA、historical EAL/OAL equality、EAL-080 field count、五current-row assertion、SpecDock validate、diff-check、semantic scope audit、resulting branch parity、fresh Red v6 | identityまたはSHA不一致、historical EAL/OAL変更、report以外のsemantic diff、duplicate EAL、current rowのBlue v4未完了表現、future commit SHAの自己参照、validation failureでは停止する | report-only semantic diff、EAL-080 identity、五current-state row、immutable checks、resulting exact HEADの外部handoff、fresh Red v6 review input | Blue v4 report/evidence同期は`d52f8ab1df0d34be36880d1be64f6b2605a63065`としてcommit/push済み。Red v5は同HEADでFAIL（P0=0/P1=1、`RT-354-S09-V5-001`）。Blue v5 report-only repairがcurrent review Candidateとしてactiveであり、closure claimは`none`、次ゲートはfresh Red v6 |
```

## 5.2 Delegated Worker Evidence

```markdown
| S09 | issue orchestrator | Blue v1/v2のOracle 0.17.0実装、Blue v3のEAL-074復元、Blue v4のRed v3／v4 evidence同期は変更せず、commit/push済みBlue v4の状態を前提にRed v5 formal reviewを`EAL-080`へ採用し、`RT-354-S09-V5-001`に従って五つのcurrent-state rowだけをBlue v5 report repair active／fresh Red v6 pendingへ同期する | Semantic mutationは`report.md`のみ。Red v5 canonical/rawと本Blue v5 briefはオーケストレーターが別のimmutable evidence importとして扱う | Red v5 canonical/raw SHA/cmp、Blue v4 brief SHA、EAL-073〜EAL-080連番、OAL-001/OAL-002 byte equality、五current surface、SpecDock validate、diff-check、semantic scope audit、resulting branch parity | Fresh Red v1 at `ac84de312072028ad864d06ae018b3ccf196051d` FAIL（P0=0/P1=2）、v2 at `ec179c301c045f94d54abea308c47e79d16c5979` FAIL（P0=0/P1=2）、v3 at `26d40034507b60f76d06536fb7c5e552bdb49850` FAIL（P0=0/P1=1）、v4 at `aa019e5d53af171b31845124e15482f78cd0fcb9` FAIL（P0=0/P1=1）、v5 at `d52f8ab1df0d34be36880d1be64f6b2605a63065` FAIL（P0=0/P1=1） | Active riskは`RT-354-S09-V5-001`のみ。Runtime、tests、0.16.1回帰、0.17.0 profile/reader/decoder/builders、S10境界にはRed v5による新しいP0/P1なし | `EAL-080`と五current-state rowをreport-only同期し、resulting exact HEADを外部handoffへbindしてfresh Red v6へ渡す。P0/P1=0までclosure claimは`none`、S10以降とPR／merge／closeを保留する |
```

## 5.3 Parent Implementation Exception

```markdown
| S09 | no delegation exception; Red v5 P1に対するBlue v5 report-only current-state repairをissue orchestratorが実施する | user request to implement and review; risk accepted: no | Semantic mutationは`report.md`のみ。Red v5 canonical/rawとBlue v5 briefのexact-byte importは別証跡操作 | `EAL-080`のappend-only追加、五つのS09 current row同期、report-only evidence repair、resulting exact HEADの外部handoff、fresh Red v6 review | 失敗時はsemantic source HEAD `d52f8ab1df0d34be36880d1be64f6b2605a63065`のreportへ戻す。Red v5 evidence import、Candidate identity、implementation commit、EAL-073〜EAL-079、OAL-001/OAL-002、Red v1〜v5、既存briefs、receiptsは保持する | named branch／semantic source／evidence-import境界、SHA/cmp、historical EAL/OAL equality、current-row zero-stale assertion、scope audit、SpecDock validate、diff-check、post-push clean/parity | Latest formal gateはRed v5 FAIL（P0=0/P1=1、`RT-354-S09-V5-001`）。Blue v5 report-only repair Candidateをresulting exact HEADへcommit/pushし、fresh Red v6で確認する | identity mismatch、evidence byte mismatch、report外semantic diff、historical row変更、future self-reference、P0/P1 findingでは停止する。S09 closure、S10、PR、merge、Issue close、Issue finishはP0/P1=0まで行わない |
```

## 5.4 Reviewer Gate Status

```markdown
| S09 | implementation review | ChatGPT-Use Red Team | fresh v1〜v5 / Blue v5 report repair active / Red v6 pending | fail | no | Red v1とv2は各P1=2、Red v3は`26d40034507b60f76d06536fb7c5e552bdb49850`でFAIL（P0=0/P1=1、`RT-354-S09-V3-001`）、Red v4は`aa019e5d53af171b31845124e15482f78cd0fcb9`でFAIL（P0=0/P1=1、`RT-354-S09-V4-001`）、Blue v4 report/evidence同期は`d52f8ab1df0d34be36880d1be64f6b2605a63065`へcommit/push済み、Red v5は同HEADでFAIL（P0=0/P1=1、`RT-354-S09-V5-001`）。Blue v5 report-only repair Candidateをfresh Red v6で確認しP0/P1=0となるまでS09をpromoteまたはcloseしない | EAL-067〜EAL-080、`reviews/red-team-review-s09-v3.md` SHA-256 `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2`、`reviews/red-team-review-s09-v4.md` SHA-256 `7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911`、Blue v4 brief SHA-256 `6d5708e2009b72868b5b95bb41dde3bfb3c0e58a81d0aa1bfc534e5cebffa4`、`reviews/red-team-review-s09-v5.md` SHA-256 `7bda038fdb085493d8d847ac1ac778c9968516b3a5d7e4c680e1b831585d882b`、Red v5 reviewed HEAD `d52f8ab1df0d34be36880d1be64f6b2605a63065`、Blue v5 resulting HEADはpost-push handoffで外部指定 |
```

## 5.5 Milestone / Commit Candidate Gate

```markdown
| S09 | review-failed / blue-v5-report-repair-active / red-v6-pending | Candidate version `s09-blue-repair-v2`、Candidate ID `iss-00354-s09-blue-repair-v2-20260805T225843Z`、implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`を維持する。Semantic source HEAD `d52f8ab1df0d34be36880d1be64f6b2605a63065`の`report.md`へRed v5 adoptionと五current-state同期だけを加える。Red v5 canonical/rawとBlue v5 briefは別のimmutable evidence importである | Source ledgerは`d52f8ab1df0d34be36880d1be64f6b2605a63065`、EAL-067〜EAL-080、Red v1〜v5 formal reviewである。Blue v5 resulting commit SHAはreportへ自己参照せず、push後のfresh Red v6 handoffで外部記録する | Blue v4 report/evidence同期は`d52f8ab1df0d34be36880d1be64f6b2605a63065`としてcommit/push済み。Blue v5ではresulting worktree clean、HEADとupstream exact、ahead `0`／behind `0`を外部handoff evidenceで確認する | Runtime、tests、profile、reader、canonical三文書、ADR、MANIFEST、CHECKSUMS、receipts、OAL、既存briefs／reviewsはno-op。変更理由はRed v5が特定した五current-state surfaceの一世代遅れとformal review adoptionだけである | `src/spec_dock/`、`tests/`、requirement/design/plan、ADR、MANIFEST、CHECKSUMS、characterization、EAL-073〜EAL-079、OAL-001/OAL-002、Candidate identity、implementation commit、Red v1〜v5、Blue v1〜v4 bytes | `./spec-dock/scripts/spec-dock validate`; `git diff --check`; EAL field-count／sequence assertion; historical EAL/OAL equality; five-current-row assertion; SHA/cmp; scoped `git diff --name-only`; post-push parity | Red v5 FAIL P0=0/P1=1を保持し、Blue v5 report-only repair Candidateのresulting exact HEADをfresh Red v6へ渡す。P0/P1=0までS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |
```

---

## 6. 禁止事項

次を実施しない。

* Runtime、tests、provider、installed／dogfood projectionの変更。
* Wrapper、Oracle API、alternate backendの変更。
* Generic recovery、profile registry、reader、decoder、builderの変更。
* `requirement.md`、`design.md`、`plan.md`、ADRの変更。
* `MANIFEST.json`、`CHECKSUMS.sha256`の再生成または修正。
* Candidate ZIPの生成、修正、再封印。
* Candidate version、Candidate ID、implementation commitの更新。
* `EAL-073`〜`EAL-079`の書換え。
* `OAL-001`／`OAL-002`の書換え。
* Red v1〜v5 canonical/rawの編集または要約置換。
* 既存Blue briefの編集。
* Red v5のFAILをPASSへ変更すること。
* Blue v5の将来commit SHAを事前reportへ書くこと。
* S10以降のartifact-pending、capture、fallback、retry、stage taxonomyの先取り。
* Default branchまたは別branchの使用。
* PR、merge、Issue close、Issue finish。
* `closure_claim`を`none`以外にすること。

---

## 7. 実行前assertion

### 7.1 Branchとsemantic source

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE='d52f8ab1df0d34be36880d1be64f6b2605a63065'

test "$(git branch --show-current)" = "$BRANCH"
git cat-file -e "${SOURCE}^{commit}"
```

Named branchはRed v5 evidence importにより`SOURCE`より先へ進んでいてよい。ただし、semantic sourceとの差分は次に限定する。

```text
reviews/red-team-review-s09-v5.md
reviews/red-team-review-s09-v5-raw.md
```

本brief artifactが先にimport済みなら、追加で次だけを許容する。

```text
artifacts/implementation-briefs/s09-red-v5-blue-repair-v5-20260806.md
```

### 7.2 Report blob identity

```bash
REPORT="$ISSUE_DIR/report.md"
EXPECTED_REPORT_BLOB='3cb21bc59865ef419d4806d40459f5cde28f6a49'

test "$(git rev-parse "$SOURCE:$REPORT")" = "$EXPECTED_REPORT_BLOB"
test "$(git rev-parse "$BRANCH:$REPORT")" = "$EXPECTED_REPORT_BLOB"
```

Named branch側のreportがsource baselineから既に変更されている場合は停止する。

### 7.3 Red v5 canonical/raw identity

```bash
sha256sum \
  "$ISSUE_DIR/reviews/red-team-review-s09-v5.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v5-raw.md"
```

双方の期待値:

```text
7bda038fdb085493d8d847ac1ac778c9968516b3a5d7e4c680e1b831585d882b
```

```bash
cmp \
  "$ISSUE_DIR/reviews/red-team-review-s09-v5.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v5-raw.md"
```

### 7.4 Blue v4 brief identity

```bash
test "$(sha256sum \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md" \
  | awk '{print $1}')" = \
  '6d5708e2009b72868b5b95bb41dde3bfb3c0e58a81d0aa1bfc534e5cebffa4'
```

### 7.5 Existing EAL／OAL shape

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()

for number in range(73, 80):
    identifier = f"EAL-{number:03d}"
    matches = [line for line in lines if line.startswith(f"| {identifier} |")]
    assert len(matches) == 1, (identifier, len(matches))

assert not any(line.startswith("| EAL-080 |") for line in lines)

positions = [
    next(i for i, line in enumerate(lines) if line.startswith(f"| EAL-{number:03d} |"))
    for number in range(73, 80)
]
assert positions == list(range(positions[0], positions[0] + 7)), positions

for identifier in ("OAL-001", "OAL-002"):
    matches = [line for line in lines if line.startswith(f"| {identifier} |")]
    assert len(matches) == 1, (identifier, len(matches))
PY
```

---

## 8. Patch手順

1. Named branchとsemantic source HEADの存在を確認する。
2. Named branchのsemantic sourceからの差分がRed v5 evidence importだけであることを確認する。
3. Source HEADとnamed branchで`report.md` blobが一致することを確認する。
4. Red v5 canonical/rawのSHA-256とbyte identityを確認する。
5. Blue v4 briefのSHA-256を確認する。
6. `EAL-079`直後へexact `EAL-080`を一行追加する。
7. Implementation Delegation GateのS09行をexact replacement rowへ置換する。
8. Delegated Worker EvidenceのS09行を置換する。
9. Parent Implementation ExceptionのS09行を置換する。
10. Reviewer Gate StatusのS09行を置換する。
11. Milestone / Commit Candidate GateのS09行を置換する。
12. `OAL-001`／`OAL-002`を変更しない。
13. Historical EAL、reviews、briefs、runtime、tests、canonical docsを変更しない。
14. Report validationとimmutable checksを実行する。
15. Semantic diffが`report.md`だけであることを確認する。
16. Report-only repairをcommitし、named branchへpushする。
17. Push後にworktree clean、HEAD／upstream parity、ahead `0`／behind `0`を確認する。
18. Resulting exact HEADをreportへ追記せず、fresh Red v6 handoffへ外部指定する。

---

## 9. Immutable checks

### 9.1 Existing EAL／OAL byte equality

```bash
python - <<'PY'
from pathlib import Path
import subprocess

SOURCE = "d52f8ab1df0d34be36880d1be64f6b2605a63065"
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

for number in range(73, 80):
    identifier = f"EAL-{number:03d}"
    assert row(before, identifier) == row(after, identifier), identifier

for identifier in ("OAL-001", "OAL-002"):
    assert row(before, identifier) == row(after, identifier), identifier

row(after, "EAL-080")
print("historical EAL/OAL unchanged; EAL-080 present")
PY
```

### 9.2 Canonical files、runtime、tests

```bash
git diff --exit-code \
  d52f8ab1df0d34be36880d1be64f6b2605a63065 \
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
  d52f8ab1df0d34be36880d1be64f6b2605a63065 \
  -- \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4-raw.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md"
```

Red v5 canonical/rawはsource HEAD後のimmutable evidence importなので、このsource-relative zero-diff checkには含めず、SHA／`cmp`で検証する。

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
    if line.startswith(tuple(f"| EAL-{n:03d} |" for n in range(73, 81)))
]
assert selected == [f"EAL-{n:03d}" for n in range(73, 81)], selected

matches = [line for line in lines if line.startswith("| EAL-080 |")]
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

SOURCE = "d52f8ab1df0d34be36880d1be64f6b2605a63065"
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

### 10.3 Current-state zero-stale assertion

Historical EALやpast review本文は検索対象に含めず、五つのcurrent-state sectionだけを検査する。

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
    "d52f8ab1df0d34be36880d1be64f6b2605a63065",
    "RT-354-S09-V5-001",
    "Blue v4 report/evidence同期",
    "Blue v5",
    "fresh Red v6",
    "closure claim",
)

for token in required:
    assert token in current_text, token

forbidden = (
    "review-failed / blue-v4-report-repair-active",
    "Blue v4 report-only repairを実施中",
    "Blue v4 report repair中",
    "Blue v4 report-only同期をcommit/push後",
    "fresh v1〜v4 / Blue v4 report repair active / Red v5 pending",
    "Commit前はsource HEAD",
    "Blue v4修正後の新しいexact pushed HEADをfresh Red v5",
)

for token in forbidden:
    assert token not in current_text, token

print("S09 current-state synchronized for Red v5 / Blue v5 / Red v6")
PY
```

### 10.4 Repository validation

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

今回のsemantic repairはreport-onlyであるため、pytest、Ruff、Mypy、Oracle browser smokeを新たな実装証跡として再主張しない。既存EALに記録された結果を変更しない。

### 10.5 Scope audit

Working-tree semantic diff:

```bash
git diff --name-only
```

期待されるsemantic path:

```text
${ISSUE_DIR}/report.md
```

Source HEAD以降の全差分として許容するpath:

```text
${ISSUE_DIR}/report.md
${ISSUE_DIR}/reviews/red-team-review-s09-v5.md
${ISSUE_DIR}/reviews/red-team-review-s09-v5-raw.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v5-blue-repair-v5-20260806.md
```

最後のbrief pathは、オーケストレーターが本回答をbyte-identicalに保存した場合だけ許容する。

---

## 11. Commit／push

推奨commit message:

```text
docs(iss-00354): sync S09 Red v5 current state
```

Semantic patch:

```bash
git add -- "$ISSUE_DIR/report.md"

git commit -m \
  "docs(iss-00354): sync S09 Red v5 current state"
```

Red v5 reviewsまたはBlue v5 briefのimportが未commitの場合は、オーケストレーターがexact-byte evidenceとして同一commitまたは明示的な別evidence commitへ含めてよい。どちらの場合もsemantic mutationは`report.md`だけである。

Push:

```bash
git push origin \
  HEAD:codex/iss-00354-chatgpt-context-contract
```

Post-push:

```bash
test -z "$(git status --short)"

RESULTING_HEAD="$(git rev-parse HEAD)"
UPSTREAM_HEAD="$(git rev-parse '@{upstream}')"

test "$RESULTING_HEAD" = "$UPSTREAM_HEAD"
test "$(git rev-list --left-right --count HEAD...'@{upstream}')" = $'0\t0'

printf 'resulting_head=%s\n' "$RESULTING_HEAD"
```

`RESULTING_HEAD`は、事前に`report.md`へ追記しない。

---

## 12. Fresh Red v6 handoff

Fresh Red v6へ次を固定して渡す。

```text
repository
  chemitaro/spec-dock

named_branch
  codex/iss-00354-chatgpt-context-contract

semantic_source_head
  d52f8ab1df0d34be36880d1be64f6b2605a63065

resulting_head
  <post-push exact SHA>

candidate_version
  s09-blue-repair-v2

candidate_id
  iss-00354-s09-blue-repair-v2-20260805T225843Z

implementation_commit
  470cacf5051272edfa71e9780f263d1f402a33a0

red_v5_review
  reviewed_head=d52f8ab1df0d34be36880d1be64f6b2605a63065
  sha256=7bda038fdb085493d8d847ac1ac778c9968516b3a5d7e4c680e1b831585d882b
  canonical_raw=byte-identical
  verdict=FAIL
  P0=0
  P1=1
  P2=0
  P3=0
  finding=RT-354-S09-V5-001

semantic_changed_file
  report.md only

append_only_eal
  EAL-080

current_rows_synchronized
  Implementation Delegation Gate
  Delegated Worker Evidence
  Parent Implementation Exception
  Reviewer Gate Status
  Milestone / Commit Candidate Gate

oal_changed
  false

runtime_changed
  false

tests_changed
  false

requirement_design_plan_changed
  false

manifest_checksums_changed
  false

candidate_identity_changed
  false

implementation_commit_changed
  false

closure_claim
  none

handoff_status
  ready_for_fresh_review

next_action
  fresh Red v6
```

Fresh Red v6はv1〜v5とは別のfresh、read-only、defect-only reviewとして、resulting pushed exact HEADを対象にする。

---

## 13. 停止条件

次のいずれかではcommitまたはpushを行わず停止する。

1. Named branchへアクセスできない。
2. Default branchまたは別branchが必要になる。
3. Semantic source HEAD `d52f8ab1...`がrepositoryに存在しない。
4. Named branchのsemantic sourceからの差分がRed v5 evidence importおよび本brief import以外を含む。
5. Source HEADとnamed branchの`report.md` blobが`3cb21bc59865ef419d4806d40459f5cde28f6a49`で一致しない。
6. Red v5 canonical/raw SHAが`7bda038f...d882b`と一致しない。
7. Red v5 canonical/rawがbyte-identicalでない。
8. Blue v4 brief SHAが`6d5708e2...ffa4`と一致しない。
9. `EAL-073`〜`EAL-079`が欠落、重複、順序違い、または変更されている。
10. `EAL-080`が既に別意味で存在する。
11. `OAL-001`または`OAL-002`の変更が必要になる。
12. 五つのcurrent-state行以外のcurrent/historical row変更が必要になる。
13. Runtime、tests、canonical三文書、ADR、MANIFEST、CHECKSUMS、characterizationの変更が必要になる。
14. Candidate version、Candidate ID、implementation commitの更新が必要になる。
15. Blue v5の将来commit SHAをreportへ自己参照する必要が生じる。
16. Red v5 FAILをPASSへ変更する必要が生じる。
17. SpecDock validate、`git diff --check`、EAL field count、sequence、current-state assertionのいずれかが失敗する。
18. S09 closure、S10開始、PR、merge、Issue close、Issue finishを同一作業で行う必要が生じる。

完了状態は次に限定する。

```text
Blue v5 report-only repair committed and pushed
resulting branch parity = identical / ahead 0 / behind 0
closure_claim = none
handoff_status = ready_for_fresh_review
next_action = fresh Red v6
```

Fresh Red v6でP0/P1=`0`が確認されるまで、S09をcloseせず、S10以降、PR、merge、Issue close、Issue finishへ進まない。
