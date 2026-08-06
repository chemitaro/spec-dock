# iss-00354 S09 Blue Repair v4 — Red v3／Blue v3／Red v4 report同期ブリーフ

## 0. 固定identityと実行境界

| 項目                           | 固定値                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| Repository                   | `chemitaro/spec-dock`                                                                      |
| Named branch                 | `codex/iss-00354-chatgpt-context-contract`                                                 |
| Source HEAD                  | `aa019e5d53af171b31845124e15482f78cd0fcb9`                                                 |
| Branch parity                | named branch tipとsource HEADは`identical`、ahead `0`、behind `0`                              |
| Default branch fallback      | 禁止・未使用                                                                                     |
| Candidate version            | `s09-blue-repair-v2`                                                                       |
| Candidate ID                 | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                                            |
| Implementation commit        | `470cacf5051272edfa71e9780f263d1f402a33a0`                                                 |
| Red v3 reviewed HEAD         | `26d40034507b60f76d06536fb7c5e552bdb49850`                                                 |
| Red v3 review SHA-256        | `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2`                         |
| Red v4 reviewed/current HEAD | `aa019e5d53af171b31845124e15482f78cd0fcb9`                                                 |
| Red v4 review SHA-256        | `7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911`                         |
| Red v4 verdict               | `FAIL`、P0=`0`、P1=`1`、P2=`0`、P3=`0`                                                         |
| Active finding               | `RT-354-S09-V4-001`                                                                        |
| Blue v3 brief SHA-256        | `cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93`                         |
| Semantic mutation allowlist  | `report.md`のみ                                                                              |
| Expected resulting state     | Red v3、Blue v3、Red v4をappend-only EALへ採用し、S09 current-stateをBlue v4修正中／fresh Red v5待ちへ同期する |
| `closure_claim`              | `none`                                                                                     |

GitHub connectorで、指定named branchのtipとsource HEADが完全一致することを確認済みである。default branchまたは別branchは参照していない。

Current reportでは`EAL-073`〜`EAL-076`が存在し、`EAL-074`も所定位置へ復元済みである。一方、Implementation Delegation Gate、Delegated Worker Evidence、Parent Implementation Exception、Reviewer Gate Status、Milestone Gateは、実行済みRed v3を依然としてpendingまたは未実施として扱っている。

---

## 1. Red v4 findingとBlue v4の最小目的

Red v4で唯一残ったP1は、runtime、tests、profile、reader、canonical三文書の欠陥ではない。

```text
RT-354-S09-V4-001
```

対象は、同じcurrent HEADに次の証跡が存在するにもかかわらず、`report.md`のcurrent-stateが一世代古いままであることに限定される。

```text
Red v3 formal review
  reviewed HEAD = 26d40034507b60f76d06536fb7c5e552bdb49850
  verdict = FAIL
  P0/P1/P2/P3 = 0/1/0/0
  finding = RT-354-S09-V3-001
  SHA-256 = aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2

Blue v3 brief
  semantic scope = report.md only
  operation = EAL-074 restoration
  SHA-256 = cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93
  closure_claim = none

Red v4 formal review
  reviewed HEAD = aa019e5d53af171b31845124e15482f78cd0fcb9
  verdict = FAIL
  P0/P1/P2/P3 = 0/1/0/0
  finding = RT-354-S09-V4-001
  SHA-256 = 7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911
```

Red v3 canonical reviewはCandidate version、Candidate ID、implementation commit、reviewed HEAD、FAIL P0=`0`／P1=`1`を明示している。 Blue v3 briefも、`report.md`だけを変更し、Candidate identityとimplementation commitを維持する境界を固定している。

Blue v4の目的は次の二点だけである。

1. Red v3、Blue v3、Red v4を`EAL-077`〜`EAL-079`としてappend-only採用する。
2. S09の六つのcurrent-state surfaceを、Red v4 FAILとBlue v4 report-only修正中、fresh Red v5待ちへ同期する。

---

## 2. Allowlistとimmutable paths

`ISSUE_DIR`:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract
```

### 2.1 Semantic mutation allowlist

内容変更を許可する唯一の正本は次である。

```text
${ISSUE_DIR}/report.md
```

### 2.2 別証跡操作として許可されるimmutable import

オーケストレーターは、repositoryに未収録の場合に限り、次の外部成果物をexact bytesのままimportできる。

```text
${ISSUE_DIR}/reviews/red-team-review-s09-v4.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4-raw.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md
```

このimportはsemantic repairとは別の証跡操作である。

* Red v4 canonical/rawを編集、再生成、要約置換しない。
* 本brief artifactを保存する場合は、この回答本文をbyte-identicalに保存する。
* Import後のlogical filename、SHA-256、canonical/raw equalityを検証する。
* Red v4の修正版reviewまたは新しいZIPを生成しない。

### 2.3 Immutable paths

次は変更しない。

```text
${ISSUE_DIR}/requirement.md
${ISSUE_DIR}/design.md
${ISSUE_DIR}/plan.md
${ISSUE_DIR}/decisions/
${ISSUE_DIR}/artifacts/characterization/
${ISSUE_DIR}/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v3.md
${ISSUE_DIR}/reviews/red-team-review-s09-v3-raw.md
src/spec_dock/
tests/
```

### 2.4 変更禁止のidentity

次は更新しない。

```text
Candidate version:
  s09-blue-repair-v2

Candidate ID:
  iss-00354-s09-blue-repair-v2-20260805T225843Z

Implementation commit:
  470cacf5051272edfa71e9780f263d1f402a33a0
```

今回のreport-only commitを新しいimplementation commitまたは新Candidateへ昇格しない。

---

## 3. Evidence Adoption Ledger追加

Current EALは`EAL-076`まで存在する。`EAL-073`〜`EAL-076`のbytes、意味、順序、historical next actionは一切変更しない。Current GitHub reportでもこれらの行と復元済み`EAL-074`を確認できる。

`EAL-076`の直後、Objective Alignment Ledger見出しの直前へ、次の三行をこの順序で追加する。

```text
EAL-077 — Red v3 formal review
EAL-078 — Blue v3 report-only brief
EAL-079 — Red v4 formal review
```

### 3.1 Exact `EAL-077` row — Red v3

```markdown
| EAL-077 | adopted | `reviews/red-team-review-s09-v3.md` | chatgpt-use-red-team | Candidate `iss-00354-s09-blue-repair-v2-20260805T225843Z`、exact reviewed HEAD `26d40034507b60f76d06536fb7c5e552bdb49850` に対するfresh defect-only Red Team v3はFAIL（P0=0/P1=1/P2=0/P3=0）。Blue v2のruntime修正は解消済みであり、唯一のfindingはRed v2正式review採用行`EAL-074`欠落の`RT-354-S09-V3-001`である | `reviews/red-team-review-s09-v3.md`, `reviews/red-team-review-s09-v3-raw.md`, `report.md` | S09 fresh Red v3 gate and Blue repair v3 input | Red v3はnamed branchのexact HEADをread-onlyで確認し、runtime、tests、canonical三文書、既存review bytesを変更していない。findingはreport/evidence-onlyであり、S10以降へ拡張しない | fresh_fail | canonical/raw byte-identical、SHA-256 `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2`; reviewed branch/HEAD `codex/iss-00354-chatgpt-context-contract` / `26d40034507b60f76d06536fb7c5e552bdb49850` | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S09 closure | Blue v3で`EAL-074`をreport-only復元し、新しいpushed exact HEADをfresh Red v4へ渡す。P0/P1=0までS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |
```

### 3.2 Exact `EAL-078` row — Blue v3 brief

```markdown
| EAL-078 | adopted | `artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md` | chatgpt-use-blue-repair-brief | Red v3唯一のP1 `RT-354-S09-V3-001`を、`report.md`の`EAL-073`直後かつ`EAL-075`直前へexact `EAL-074`一行を復元するreport-only修正へ限定し、fresh Red v4 handoffを定義した | `artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md`, `report.md` | S09 Blue repair v3 implementation gate | Candidate version、Candidate ID、implementation commitを維持し、runtime、tests、requirement、design、plan、characterization、Red v1〜v3 bytesを変更しないadvisory briefである | advisory_adopted | brief SHA-256 `cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93`; source HEAD `26d40034507b60f76d06536fb7c5e552bdb49850`; closure claim `none` | issue orchestrator | ChatGPT-Use | no | Exact `EAL-074`復元をreport-onlyでcommit/pushし、resulting exact HEADをfresh Red v4へ渡す。S09 closure claimは行わない |
```

### 3.3 Exact `EAL-079` row — Red v4

```markdown
| EAL-079 | adopted | `reviews/red-team-review-s09-v4.md` | chatgpt-use-red-team | Candidate `iss-00354-s09-blue-repair-v2-20260805T225843Z`、exact reviewed/current HEAD `aa019e5d53af171b31845124e15482f78cd0fcb9` に対するfresh defect-only Red Team v4はFAIL（P0=0/P1=1/P2=0/P3=0）。Red v3 findingは解消済みであり、唯一のfindingは実行済みRed v3とBlue v3がcurrent-stateおよびEALへ反映されずRed v3がpendingのまま残る`RT-354-S09-V4-001`である | `reviews/red-team-review-s09-v4.md`, `reviews/red-team-review-s09-v4-raw.md`, `report.md` | S09 fresh Red v4 gate and Blue repair v4 input | Red v4はcurrent HEADのreport/evidence-only scopeを確認し、runtime、tests、profile、canonical三文書に新規P0/P1を認めていない。修正はreport current-stateとappend-only evidence同期だけに限定する | fresh_fail | canonical/raw byte-identical、SHA-256 `7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911`; reviewed branch/HEAD `codex/iss-00354-chatgpt-context-contract` / `aa019e5d53af171b31845124e15482f78cd0fcb9`; model、strategy、verified telemetryは未観測 | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S09 closure | Blue v4でEAL-077〜EAL-079とS09 current-stateをreport-only同期し、commit/push後のresulting exact HEADをfresh Red v5へ渡す。P0/P1=0までS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |
```

### 3.4 EAL row invariants

各追加行は次を満たす。

* 既存EAL schemaの14 fields。
* `adoption_status=adopted`。
* Red reviewは`evidence_strength=fresh_fail`。
* Blue briefは`evidence_strength=advisory_adopted`。
* Red v3とRed v4のFAILをPASSへ変更しない。
* Historical next actionは当時の時点を保持する。
* `EAL-077`はBlue v3とRed v4より前。
* `EAL-078`はRed v3を入力としたBlue v3。
* `EAL-079`はBlue v3修正後HEADを対象としたRed v4。
* Blue v4の将来commit SHAを記載しない。

---

## 4. Objective Alignment Ledger同期

Current OALには`OAL-001`のみが存在する。 `OAL-001`は変更せず、その直後へ次の一行を追加する。

```markdown
| OAL-002 | S09の主要目的はimplementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`で成立したexact Oracle 0.16.1／0.17.0 profile、reader、decoder、builderおよびfail-closed契約の維持であり、Blue v4ではこれらを変更しない | Red v3／Red v4 formal review、Blue v3／Blue v4 report-only brief、EAL/current-state同期は主要実装を追跡可能にする副次証跡である | report-only allowlist、Candidate identity不変、`closure_claim=none`を維持する限りlow。runtime／spec変更またはRed v4 FAILをS09 PASSへ昇格するとhigh | Red v4 FAIL（P0=0/P1=1）。Blue v4 report-only repairを実施し、fresh Red v5でP0/P1=0を確認するまでS09 closureとS10以降を保留する |
```

---

## 5. Current-state rowのexact同期

Historical narrative、EAL-001〜EAL-079のhistorical next action、Red v1〜v4 review本文は書き換えない。

次の六surfaceにある**現在のS09行だけ**を置換または追記する。

### 5.1 Implementation Delegation Gate

既存S09行を次へ置換する。

```markdown
| S09 | review-failed / blue-v4-report-repair-active | exact 0.17.0 profile/reader実装とBlue v1/v2修正は維持し、Red v4唯一のP1 `RT-354-S09-V4-001`であるreport current-state／EAL不整合だけを修正する | issue orchestrator | `report.md`のEAL-077〜EAL-079、OAL-002、S09 current-state rows。Red v4 canonical/rawと本briefのimportは別のimmutable evidence操作 | plan.md、S09 briefs、EAL-067〜EAL-079、Red v1〜v4 formal reviews、current Issue scope | append-only EAL追加、OAL current alignment追加、Implementation Delegation／Worker／Parent Exception／Reviewer Gate／Milestone GateのS09行同期、report-only commit/push、fresh Red v5 handoff | runtime、tests、provider/projection、wrapper/API、generic recovery、requirement/design/plan、characterization、Candidate identity、既存EAL-073〜EAL-076、Red v1〜v4 bytes、S10以降、PR、merge、closeを変更しない | exact branch/HEAD、Red v3/v4 canonical/raw SHA/cmp、Blue v3 brief SHA、historical EAL row equality、current-row assertion、SpecDock validate、diff-check、post-push branch parity、fresh Red v5 | identityまたはSHA不一致、historical row変更、report以外のsemantic diff、duplicate EAL/OAL、validation failure、future commit SHAの自己参照 | report-only diff、EAL/OAL identity、current-state assertion、immutable checks、resulting HEADの外部handoff、fresh Red v5 review input | Red v3は`26d40034507b60f76d06536fb7c5e552bdb49850`でFAIL（P0=0/P1=1）、Blue v3は`EAL-074`を復元済み、Red v4は`aa019e5d53af171b31845124e15482f78cd0fcb9`でFAIL（P0=0/P1=1）。Blue v4 report-only repairを実施中であり、closure claimは`none`、次ゲートはfresh Red v5 |
```

### 5.2 Delegated Worker Evidence

既存S09行を次へ置換する。

```markdown
| S09 | issue orchestrator | Blue v1/v2のexact 0.17.0実装とmixed-inventory修正は変更せず、Red v3 formal review、Blue v3 report-only brief、Red v4 formal reviewを採用し、Red v4の`RT-354-S09-V4-001`に従ってS09 current-stateだけをBlue v4 report repair中へ同期する | Semantic repairは`report.md`のみ。Red v4 canonical/rawとBlue v4 briefはオーケストレーターが別のimmutable evidence importとして扱う | Red v3 canonical/raw SHA/cmp、Blue v3 brief SHA、Red v4 canonical/raw SHA/cmp、EAL-073〜EAL-079順序、OAL-002、六current surface、SpecDock validate、diff-check、post-push parity | Fresh Red v1 at `ac84de312072028ad864d06ae018b3ccf196051d` FAIL（P0=0/P1=2）、v2 at `ec179c301c045f94d54abea308c47e79d16c5979` FAIL（P0=0/P1=2）、v3 at `26d40034507b60f76d06536fb7c5e552bdb49850` FAIL（P0=0/P1=1）、v4 at `aa019e5d53af171b31845124e15482f78cd0fcb9` FAIL（P0=0/P1=1） | Active riskは`RT-354-S09-V4-001`のみ。runtime、tests、0.16.1回帰、0.17 profile/reader、S10境界には新規P0/P1なし | EAL-077〜EAL-079とcurrent-stateをreport-only同期し、commit/push後のresulting exact HEADをfresh Red v5へ渡す。P0/P1=0までclosure claimは`none`、S10以降とPR／merge／closeを保留 |
```

### 5.3 Parent Implementation Exception

既存S09行を次へ置換する。

```markdown
| S09 | no delegation exception; Red v4 P1に対するBlue v4 report-only current-state repairをissue orchestratorが実施する | user request to implement and review; risk accepted: no | Semantic mutationは`report.md`のみ。Red v4 canonical/rawとBlue v4 briefのexact-byte importは別証跡操作 | EAL-077〜EAL-079のappend-only追加、OAL-002追加、五つのS09 current row同期、report-only commit/push、fresh Red v5 handoff | 失敗時はsource HEAD `aa019e5d53af171b31845124e15482f78cd0fcb9`のreportへ戻す。Candidate、implementation commit、EAL-073〜EAL-076、Red v1〜v4、briefs、receiptsは保持する | branch/HEAD、SHA/cmp、historical row equality、current-row zero-stale assertion、scope audit、SpecDock validate、diff-check、post-push parity | Latest formal gateはRed v4 FAIL（P0=0/P1=1、`RT-354-S09-V4-001`）。Blue v4修正後の新しいexact pushed HEADをfresh Red v5で確認する | identity mismatch、evidence byte mismatch、report外semantic diff、future self-reference、P0/P1 findingでは停止する。S09 closure、S10、PR、merge、Issue close、Issue finishはP0/P1=0まで行わない |
```

### 5.4 Reviewer Gate Status

既存S09行を次へ置換する。

```markdown
| S09 | implementation review | ChatGPT-Use Red Team | fresh v1〜v4 / Blue v4 report repair active / Red v5 pending | fail | no | Red v1とv2は各P1=2、Red v3は`26d40034507b60f76d06536fb7c5e552bdb49850`でFAIL（P0=0/P1=1、`RT-354-S09-V3-001`）、Blue v3は`EAL-074`を復元、Red v4は`aa019e5d53af171b31845124e15482f78cd0fcb9`でFAIL（P0=0/P1=1、`RT-354-S09-V4-001`）。Blue v4 report-only同期をcommit/push後、fresh Red v5でP0/P1=0を確認するまでS09をpromoteまたはcloseしない | EAL-067〜EAL-079、`reviews/red-team-review-s09-v3.md` SHA-256 `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2`、Blue v3 brief SHA-256 `cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93`、`reviews/red-team-review-s09-v4.md` SHA-256 `7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911`、resulting HEADはpost-commit handoffで外部指定 |
```

### 5.5 Milestone / Commit Candidate Gate

既存S09行を次へ置換する。

```markdown
| S09 | review-failed / blue-v4-report-repair-active | Candidate version `s09-blue-repair-v2`、Candidate ID `iss-00354-s09-blue-repair-v2-20260805T225843Z`、implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0`を維持し、source HEAD `aa019e5d53af171b31845124e15482f78cd0fcb9`から`report.md` current-state／EALだけを修正する | Source ledgerは`aa019e5d53af171b31845124e15482f78cd0fcb9`とEAL-067〜EAL-079。Blue v4のresulting commit SHAはreportへ自己参照せず、commit/push後の外部handoffで記録する | Commit前はsource HEAD／upstream／cleanを確認し、push後はworktree clean、HEADとupstream exact、ahead `0`／behind `0`を外部証跡へ記録する | Runtime、tests、profile、reader、canonical三文書、receipts、既存briefs／reviewsはno-op。変更理由はRed v4が特定したreport current-state／mandatory EAL不整合のみ | `src/spec_dock/`、`tests/`、requirement/design/plan、characterization、EAL-073〜EAL-076、Candidate identity、Red v1〜v4／Blue v1〜v3 bytes | `./spec-dock/scripts/spec-dock validate`; `git diff --check`; historical EAL/current-row assertions; SHA/cmp; scoped `git diff --name-only` | Red v4 FAIL P0=0/P1=1を保持し、Blue v4 report-only修正後のresulting exact HEADをfresh Red v5へ渡す。P0/P1=0までS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |
```

---

## 6. 実行前assertion

### 6.1 Git identity

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE='aa019e5d53af171b31845124e15482f78cd0fcb9'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE"
test "$(git rev-parse '@{upstream}')" = "$SOURCE"
test -z "$(git status --short)"
```

### 6.2 Current report blob

Current source HEADにおける`report.md` Git blobは次である。

```text
c93086e20ac6e4721a172ced0a5498a99695e774
```

```bash
REPORT="$ISSUE_DIR/report.md"

test "$(git hash-object "$REPORT")" = \
  "c93086e20ac6e4721a172ced0a5498a99695e774"
```

不一致なら本ブリーフをそのまま適用せず停止する。

### 6.3 Existing EAL shape

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()

def positions(identifier: str) -> list[int]:
    return [
        index
        for index, line in enumerate(lines)
        if line.startswith(f"| {identifier} |")
    ]

for identifier in ("EAL-073", "EAL-074", "EAL-075", "EAL-076"):
    assert len(positions(identifier)) == 1, (identifier, positions(identifier))

for identifier in ("EAL-077", "EAL-078", "EAL-079"):
    assert positions(identifier) == [], (identifier, positions(identifier))

sequence = [
    next(index for index, line in enumerate(lines) if line.startswith(f"| EAL-{number:03d} |"))
    for number in range(73, 77)
]
assert sequence == list(range(sequence[0], sequence[0] + 4)), sequence

assert sum(line.startswith("| OAL-001 |") for line in lines) == 1
assert not any(line.startswith("| OAL-002 |") for line in lines)
PY
```

### 6.4 Red v3 identity

```bash
sha256sum \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md"
```

両方の期待値:

```text
aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2
```

```bash
cmp \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md"
```

### 6.5 Blue v3 brief identity

```bash
test "$(sha256sum \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md" \
  | awk '{print $1}')" = \
  "cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93"
```

### 6.6 Red v4 identity

Red v4 canonical/rawがまだrepositoryへimportされていない場合、オーケストレーターが添付bytesを無変更で保存してから次を実行する。

```bash
sha256sum \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4-raw.md"
```

両方の期待値:

```text
7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911
```

```bash
cmp \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4-raw.md"
```

一つでも不一致なら`EAL-079`を追加せず停止する。

---

## 7. Patch手順

1. Named branch、source HEAD、upstream、clean状態を確認する。
2. Red v3 canonical/rawとBlue v3 briefのSHAを確認する。
3. Red v4 canonical/rawを外部証跡としてexact-byte importし、SHAと`cmp`を確認する。
4. 本briefをartifact化する場合は、回答本文をbyte-identicalに保存する。
5. `report.md`の`EAL-076`直後へ`EAL-077`、`EAL-078`、`EAL-079`を順に追加する。
6. `OAL-001`直後へ`OAL-002`を追加する。
7. Implementation Delegation GateのS09行を置換する。
8. Delegated Worker EvidenceのS09行を置換する。
9. Parent Implementation ExceptionのS09行を置換する。
10. Reviewer Gate StatusのS09行を置換する。
11. Milestone / Commit Candidate GateのS09行を置換する。
12. Historical EAL、historical review narrative、Candidate identity、runtime/test evidenceは変更しない。
13. Report validation、immutable checks、SpecDock validate、diff-checkを実行する。
14. Report-only semantic repairをcommitする。
15. Named branchへpushし、local/upstream exact parityとclean状態を確認する。
16. Resulting SHAはreportへ追記せず、fresh Red v5 handoff promptと外部post-commit evidenceへ記録する。

---

## 8. Immutable checks

### 8.1 `EAL-073`〜`EAL-076`

```bash
python - <<'PY'
from pathlib import Path
import subprocess

SOURCE = "aa019e5d53af171b31845124e15482f78cd0fcb9"
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
        line
        for line in text.splitlines()
        if line.startswith(f"| {identifier} |")
    ]
    assert len(matches) == 1, (identifier, len(matches))
    return matches[0]

for identifier in ("EAL-073", "EAL-074", "EAL-075", "EAL-076"):
    assert row(before, identifier) == row(after, identifier), identifier

for identifier in ("EAL-077", "EAL-078", "EAL-079"):
    row(after, identifier)

print("historical EAL rows unchanged; EAL-077..079 present")
PY
```

### 8.2 Runtime、tests、三文書、characterization

```bash
git diff --exit-code \
  aa019e5d53af171b31845124e15482f78cd0fcb9 \
  -- \
  src/spec_dock \
  tests \
  "$ISSUE_DIR/requirement.md" \
  "$ISSUE_DIR/design.md" \
  "$ISSUE_DIR/plan.md" \
  "$ISSUE_DIR/decisions" \
  "$ISSUE_DIR/artifacts/characterization"
```

### 8.3 Existing S09 briefsとRed v1〜v3

```bash
git diff --exit-code \
  aa019e5d53af171b31845124e15482f78cd0fcb9 \
  -- \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md"
```

### 8.4 Candidate identity

```bash
rg -n \
  's09-blue-repair-v2|iss-00354-s09-blue-repair-v2-20260805T225843Z|470cacf5051272edfa71e9780f263d1f402a33a0' \
  "$ISSUE_DIR/report.md"
```

別Candidate version、別Candidate ID、別implementation commitへ置換されていないことを確認する。

---

## 9. Report validation

### 9.1 EAL連番とfield数

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
lines = text.splitlines()

ids = [
    line.split("|")[1].strip()
    for line in lines
    if line.startswith(tuple(f"| EAL-{number:03d} |" for number in range(73, 80)))
]
assert ids == [f"EAL-{number:03d}" for number in range(73, 80)], ids

for identifier in ("EAL-077", "EAL-078", "EAL-079"):
    matches = [
        line for line in lines
        if line.startswith(f"| {identifier} |")
    ]
    assert len(matches) == 1, (identifier, len(matches))
    fields = [part.strip() for part in matches[0].strip("|").split("|")]
    assert len(fields) == 14, (identifier, len(fields))

assert sum(line.startswith("| OAL-002 |") for line in lines) == 1
PY
```

### 9.2 Current-state assertion

検査対象をcurrent-state sectionsへ限定する。Historical EALや過去review本文に含まれる「当時のfresh Red v3」は削除対象にしない。

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")

section_pairs = (
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

sections = []
for start, end in section_pairs:
    assert text.count(start) == 1, start
    assert text.count(end) == 1, end
    sections.append(text.split(start, 1)[1].split(end, 1)[0])

current = "\n".join(sections)

required = (
    "aa019e5d53af171b31845124e15482f78cd0fcb9",
    "26d40034507b60f76d06536fb7c5e552bdb49850",
    "RT-354-S09-V3-001",
    "RT-354-S09-V4-001",
    "Red v4",
    "Blue v4",
    "fresh Red v5",
    "closure claim",
)

for token in required:
    assert token in current, token

forbidden = (
    "fresh Red v3 is pending",
    "fresh Red v3が未実施",
    "fresh Red v3 is the only remaining S09 gate",
    "Run fresh Red v3",
    "current exact branch tipをfresh Red v3",
)

for token in forbidden:
    assert token not in current, token

print("S09 current-state synchronization: pass")
PY
```

### 9.3 OAL assertion

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
oal_001 = [line for line in lines if line.startswith("| OAL-001 |")]
oal_002 = [line for line in lines if line.startswith("| OAL-002 |")]
assert len(oal_001) == 1
assert len(oal_002) == 1
assert lines.index(oal_002[0]) == lines.index(oal_001[0]) + 1
PY
```

### 9.4 Repository validation

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

今回のsemantic repairはreport-onlyであるため、pytest、Ruff、Mypyの新しい実行結果をS09 runtime evidenceとして再主張しない。EAL-076にある既存実装・test証跡は変更しない。

### 9.5 Scope audit

External evidence importを除いたsemantic diffは`report.md`一件でなければならない。

```bash
git diff --name-only \
  aa019e5d53af171b31845124e15482f78cd0fcb9...HEAD
```

許可される全path:

```text
${ISSUE_DIR}/report.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4.md
${ISSUE_DIR}/reviews/red-team-review-s09-v4-raw.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md
```

後三件はimmutable evidence importであり、semantic contentを編集しない。

---

## 10. Commit／push

推奨commit message:

```text
docs(iss-00354): sync S09 Red v3-v4 evidence state
```

Commit前:

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
git status --short
```

Commit／push:

```bash
git add -- \
  "$ISSUE_DIR/report.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v4-raw.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md"

git commit -m \
  "docs(iss-00354): sync S09 Red v3-v4 evidence state"

git push origin \
  HEAD:codex/iss-00354-chatgpt-context-contract
```

External evidence filesをオーケストレーターが別commitでimportする場合は、report-only semantic commitとimport commitの順序・identityをhandoffへ明記する。どちらの場合もruntime/test差分は0とする。

Push後:

```bash
test -z "$(git status --short)"

RESULTING_HEAD="$(git rev-parse HEAD)"
UPSTREAM_HEAD="$(git rev-parse '@{upstream}')"

test "$RESULTING_HEAD" = "$UPSTREAM_HEAD"
test "$(git rev-list --left-right --count HEAD...'@{upstream}')" = $'0\t0'

printf 'resulting_head=%s\n' "$RESULTING_HEAD"
```

`RESULTING_HEAD`は事前の`report.md`へ書き戻さない。Fresh Red v5 promptとpost-commit handoff evidenceで外部指定する。

---

## 11. Fresh Red v5 handoff

Fresh Red v5には次を固定して渡す。

```text
repository
  chemitaro/spec-dock

named_branch
  codex/iss-00354-chatgpt-context-contract

source_head
  aa019e5d53af171b31845124e15482f78cd0fcb9

resulting_head
  <post-push exact SHA>

candidate_version
  s09-blue-repair-v2

candidate_id
  iss-00354-s09-blue-repair-v2-20260805T225843Z

implementation_commit
  470cacf5051272edfa71e9780f263d1f402a33a0

red_v3_review
  reviewed_head=26d40034507b60f76d06536fb7c5e552bdb49850
  sha256=aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2
  verdict=FAIL
  P0=0
  P1=1
  finding=RT-354-S09-V3-001

red_v4_review
  reviewed_head=aa019e5d53af171b31845124e15482f78cd0fcb9
  sha256=7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911
  verdict=FAIL
  P0=0
  P1=1
  finding=RT-354-S09-V4-001

blue_v3_brief_sha256
  cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93

semantic_changed_file
  report.md only

append_only_eal
  EAL-077
  EAL-078
  EAL-079

current_rows_synchronized
  Implementation Delegation Gate
  Objective Alignment Ledger
  Delegated Worker Evidence
  Parent Implementation Exception
  Reviewer Gate Status
  Milestone / Commit Candidate Gate

runtime_changed
  false

tests_changed
  false

requirement_design_plan_changed
  false

characterization_changed
  false

candidate_identity_changed
  false

closure_claim
  none

handoff_status
  ready_for_fresh_review

next_action
  fresh Red v5
```

Fresh Red v5は、v1〜v4とは別のfresh、read-only、defect-only reviewとして、resulting pushed exact HEADを対象にする。

---

## 12. 停止条件

次のいずれかではcommitまたはpushを行わず停止する。

1. Named branch tipと`aa019e5d53af171b31845124e15482f78cd0fcb9`が一致しない。
2. Default branchまたは別branchの参照が必要になる。
3. Current report Git blobが`c93086e20ac6e4721a172ced0a5498a99695e774`と一致しない。
4. `EAL-073`〜`EAL-076`のいずれかが欠落、重複、変更されている。
5. `EAL-077`〜`EAL-079`が既に存在する、または別意味で予約されている。
6. Red v3 canonical/raw SHAが`aaf20c...15b6f2`と一致しない。
7. Blue v3 brief SHAが`cd95bb...22a93`と一致しない。
8. Red v4 canonical/raw SHAが`7e7fc0...8b911`と一致しない。
9. Red v4 canonical/rawがbyte-identicalでない。
10. `report.md`以外のsemantic変更が必要になる。
11. Runtime、tests、provider/projection、wrapper、Oracle API、generic recovery、canonical三文書を変更する必要が生じる。
12. EAL historical next actionを現在時制へ書き換える必要が生じる。
13. Candidate version、Candidate ID、implementation commitを変更する必要が生じる。
14. Blue v4の将来commit SHAを事前reportへ自己参照する必要が生じる。
15. Red v3またはRed v4のFAILをPASSへ変更する必要が生じる。
16. Model、strategy、verified telemetryが未観測なのに、GPT-5.6 LunaまたはReasoning Effort Maxを観測値として記録する必要が生じる。
17. SpecDock validate、`git diff --check`、EAL field-count、current-state assertionのいずれかが失敗する。
18. S09 closure、S10開始、PR、merge、Issue close、Issue finishを同一作業で行う必要が生じる。

完了状態は次に限定する。

```text
Blue v4 report-only repair committed and pushed
resulting branch parity = identical / ahead 0 / behind 0
closure_claim = none
handoff_status = ready_for_fresh_review
next_action = fresh Red v5
```

Fresh Red v5でP0/P1=`0`が確認されるまで、S09をcloseせず、S10以降、PR、merge、Issue close、Issue finishへ進まない。
