# iss-00354 S09 Blue Repair v3 — `EAL-074` report-only復元ブリーフ

## 0. 固定identityと期待結果

| 項目                          | 固定値                                                                                            |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| Repository                  | `chemitaro/spec-dock`                                                                          |
| Named branch                | `codex/iss-00354-chatgpt-context-contract`                                                     |
| Source HEAD                 | `26d40034507b60f76d06536fb7c5e552bdb49850`                                                     |
| Branch parity               | named branch tipとsource HEADは`identical`、ahead `0`、behind `0`                                  |
| Default branch fallback     | 使用禁止・未使用                                                                                       |
| Candidate version           | `s09-blue-repair-v2`                                                                           |
| Candidate ID                | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                                                |
| Candidate実装commit           | `470cacf5051272edfa71e9780f263d1f402a33a0`                                                     |
| Red v3 reviewed HEAD        | `26d40034507b60f76d06536fb7c5e552bdb49850`                                                     |
| Red v3 review SHA-256       | `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2`                             |
| Red v3 verdict              | `FAIL`、P0=`0`、P1=`1`、P2=`0`、P3=`0`                                                             |
| 唯一のfinding                  | `RT-354-S09-V3-001`                                                                            |
| Semantic mutation allowlist | `report.md`のみ                                                                                  |
| Expected resulting state    | `EAL-073`、`EAL-074`、`EAL-075`、`EAL-076`が連続し、それ以外のbytesは不変。新しいpushed exact HEADをfresh Red v4へ渡す |
| `closure_claim`             | `none`                                                                                         |

GitHub connectorでnamed branchとsource HEADの完全一致を確認した。Fresh Red v3は、Blue repair v2のruntime修正を解消済みと判定し、唯一のP1を「Red v2正式レビューの採用行`EAL-074`がEvidence Adoption Ledgerから欠落していること」に限定している。 

GPT-5.6 Luna / Reasoning Effort Maxは本ブリーフの実行先設定であり、観測済みmodel evidenceとしてreportへ追記しない。

---

## 1. 修正目的

Current `report.md`のEvidence Adoption Ledgerは次の順序になっている。

```text
EAL-073
EAL-075
EAL-076
```

一方、同じreportのReviewer Gate Statusは`EAL-074 Red v2`を参照しており、Blue repair v2 briefも`EAL-074`を既存Red v2正式review evidenceとして保持する前提で`EAL-075`と`EAL-076`を採番している。Current GitHub blobでも`EAL-073`直後が`EAL-075`であることを確認した。

本修正では、`EAL-073`直後かつ`EAL-075`直前へ、Red v2正式レビューを採用する`EAL-074`を一行だけ復元する。

変更しないもの:

* `EAL-073`、`EAL-075`、`EAL-076`の全bytesと意味。
* S09のDelegated Worker Evidence、Reviewer Gate Status、Milestone / Commit Candidate Gate。
* Candidate version、Candidate ID、実装commit。
* Fresh Red v3の本文、判定、SHA、reviewed HEAD。
* Red v1/v2 canonical/raw review bytes。
* runtime、tests、characterization receipts、既存briefs。
* requirement、design、plan、ADR。
* S09 closure state。

---

## 2. Allowlist

### 2.1 内容変更を許可する唯一のファイル

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/
report.md
```

以下、このパスを`${ISSUE_DIR}/report.md`とする。

### 2.2 本ブリーフの扱い

この本文はCodexへのread-only実装指示である。オーケストレーターが別途brief artifactとして保存する場合でも、今回のsemantic repairは`${ISSUE_DIR}/report.md`の一行追加だけである。新しいEAL ID、Candidate artifact、review artifact、ZIPを生成しない。

---

## 3. 禁止事項

次は一切変更または実施しない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
```

加えて、次を禁止する。

* `EAL-073`、`EAL-075`、`EAL-076`の書換え。
* S09 current rowsの時制、state、next actionの変更。
* Red v3 formal reviewのrepository追加、修正版生成、要約による置換。
* Red v1/v2 canonical/raw bytesの変更。
* 既存S09 characterization receipt、implementation briefの変更。
* Candidate versionまたはCandidate IDの更新。
* runtime、tests、wrapper、Oracle API、generic recoveryの変更。
* S10以降のstage taxonomy、fallback、retry、captureの先取り。
* default branchまたは別branchの参照・利用。
* 新規ZIP、patch artifact、reviewer-generated correctionの作成。
* PR、merge、Issue close、Issue finish。
* S09 PASSまたはclosureの宣言。

---

## 4. 事前確認

### 4.1 Repository identity

```bash
test "$(git branch --show-current)" = \
  "codex/iss-00354-chatgpt-context-contract"

test "$(git rev-parse HEAD)" = \
  "26d40034507b60f76d06536fb7c5e552bdb49850"

test "$(git rev-parse '@{upstream}')" = \
  "26d40034507b60f76d06536fb7c5e552bdb49850"

test -z "$(git status --short)"
```

一つでも不一致なら停止する。default branchへfallbackしない。

### 4.2 Red v3 input identity

権威あるRed v3 review bytesについて、次を確認する。

```text
logical filename = red-team-review-s09-v3.md
Candidate version = s09-blue-repair-v2
Candidate ID = iss-00354-s09-blue-repair-v2-20260805T225843Z
reviewed HEAD = 26d40034507b60f76d06536fb7c5e552bdb49850
SHA-256 = aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2
verdict = FAIL
P0/P1/P2/P3 = 0/1/0/0
finding = RT-354-S09-V3-001
```

添付Red v3 reviewはこのCandidate identity、commit chain、唯一のP1を明示している。

### 4.3 Current report shape

修正前に次を確認する。

```bash
python - <<'PY'
from pathlib import Path

path = Path(
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
    "report.md"
)
lines = path.read_text(encoding="utf-8").splitlines()
positions = {
    eal: [i for i, line in enumerate(lines) if line.startswith(f"| {eal} |")]
    for eal in ("EAL-073", "EAL-074", "EAL-075", "EAL-076")
}
assert len(positions["EAL-073"]) == 1
assert positions["EAL-074"] == []
assert len(positions["EAL-075"]) == 1
assert len(positions["EAL-076"]) == 1
assert positions["EAL-075"][0] == positions["EAL-073"][0] + 1
assert positions["EAL-076"][0] == positions["EAL-075"][0] + 1
print(positions)
PY
```

`EAL-074`が既に存在する、重複IDがある、または順序が異なる場合は自動挿入せず停止する。

---

## 5. 最小patch

### 5.1 操作

`${ISSUE_DIR}/report.md`の`EAL-073`行直後、`EAL-075`行直前へ、次の一行を挿入する。

削除、置換、改行正規化、table再formatは行わない。

### 5.2 Exact `EAL-074` row

この行は、Red v2 canonical/raw identity、reviewed HEAD、FAIL判定、P1二件、Blue repair v2 handoffを既存EAL schemaの14 fieldsへ束縛する。以前のreport evidenceにも同一内容の`EAL-074`が存在していた。

```markdown
| EAL-074 | adopted | `reviews/red-team-review-s09-v2.md` | chatgpt-use-red-team | exact pushed HEAD `ec179c301c045f94d54abea308c47e79d16c5979` に対するRed v1とは別のfresh defect-only Red Team review v2はFAIL（P0=0/P1=2）。`RT-354-S09-V2-001`は0.17 valid ZIPと未characterize artifactのmixed inventoryをauthoring ZIP direct readerが受理する問題、`RT-354-S09-V2-002`は既にpush済みのrepair HEADをreportがpending commit/pushとして記録する時制不整合を指摘した | `reviews/red-team-review-s09-v2.md`, `reviews/red-team-review-s09-v2-raw.md`, `report.md` | S09 fresh Red v2 gate and Blue repair v2 input | Red v2はGitHub named branchとexact HEAD、canonical三文書、S09 evidence、4 source/testをread-onlyで確認し、repository、Candidate、review evidenceを変更していない。Red v1 RT-354-S09-002は解消済み、RT-354-S09-001はmixed inventoryで部分解消。P2/P3や設計提案は採用せずP1二件だけをBlue修正入力とする。wrapper実行はrequested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、strategy `select`、verified `yes`を観測し、Luna/Maxは主張しない | fresh_fail | canonical/raw byte-identical、SHA-256 `90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b`; reviewed branch/HEAD `codex/iss-00354-chatgpt-context-contract` / `ec179c301c045f94d54abea308c47e79d16c5979`、session `iss354-s09-red-review-20260806-2` | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S09 closure | Blue側でRT-354-S09-V2-001の0.17 mixed inventory direct-reader fail-closedとRT-354-S09-V2-002のreport-only current-state同期を最小修正し、新しいpushed exact HEADを別fresh Red v3へ渡す。P0/P1=0になるまでS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |
```

Red v2 canonical reviewはreview source HEAD `ec179c301c045f94d54abea308c47e79d16c5979`、FAIL P0=`0`/P1=`2`、findings `RT-354-S09-V2-001`と`RT-354-S09-V2-002`を記録している。

### 5.3 Historical next actionを変更しない

`EAL-074`の`next_action`はRed v2時点の履歴として、Blue repair v2とfresh Red v3を指す。現在はRed v3実施後であっても、これをfresh Red v4へ書換えない。

Fresh Red v4は今回のreport-only修正commitに対する**新しい外部handoff**であり、歴史的な`EAL-074`の内容ではない。

---

## 6. Immutable checks

### 6.1 Report内の既存EAL行

`EAL-073`、`EAL-075`、`EAL-076`がsource HEADからbyte-identicalであることを確認する。

次のscriptは、working copyがsource HEADのreportへexact `EAL-074`一行だけを挿入した状態であることを検証する。

```bash
python - <<'PY'
from pathlib import Path
import subprocess

SOURCE = "26d40034507b60f76d06536fb7c5e552bdb49850"
PATH = (
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
    "report.md"
)

EXPECTED = """| EAL-074 | adopted | `reviews/red-team-review-s09-v2.md` | chatgpt-use-red-team | exact pushed HEAD `ec179c301c045f94d54abea308c47e79d16c5979` に対するRed v1とは別のfresh defect-only Red Team review v2はFAIL（P0=0/P1=2）。`RT-354-S09-V2-001`は0.17 valid ZIPと未characterize artifactのmixed inventoryをauthoring ZIP direct readerが受理する問題、`RT-354-S09-V2-002`は既にpush済みのrepair HEADをreportがpending commit/pushとして記録する時制不整合を指摘した | `reviews/red-team-review-s09-v2.md`, `reviews/red-team-review-s09-v2-raw.md`, `report.md` | S09 fresh Red v2 gate and Blue repair v2 input | Red v2はGitHub named branchとexact HEAD、canonical三文書、S09 evidence、4 source/testをread-onlyで確認し、repository、Candidate、review evidenceを変更していない。Red v1 RT-354-S09-002は解消済み、RT-354-S09-001はmixed inventoryで部分解消。P2/P3や設計提案は採用せずP1二件だけをBlue修正入力とする。wrapper実行はrequested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、strategy `select`、verified `yes`を観測し、Luna/Maxは主張しない | fresh_fail | canonical/raw byte-identical、SHA-256 `90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b`; reviewed branch/HEAD `codex/iss-00354-chatgpt-context-contract` / `ec179c301c045f94d54abea308c47e79d16c5979`、session `iss354-s09-red-review-20260806-2` | issue orchestrator | ChatGPT-Use Red Team | no for Issue history; yes for S09 closure | Blue側でRT-354-S09-V2-001の0.17 mixed inventory direct-reader fail-closedとRT-354-S09-V2-002のreport-only current-state同期を最小修正し、新しいpushed exact HEADを別fresh Red v3へ渡す。P0/P1=0になるまでS09 closure、S10以降、PR、merge、Issue close、Issue finishを保留する |"""

base = subprocess.check_output(
    ["git", "show", f"{SOURCE}:{PATH}"],
    text=True,
).splitlines()

current = Path(PATH).read_text(encoding="utf-8").splitlines()

eal_073 = [i for i, line in enumerate(base) if line.startswith("| EAL-073 |")]
eal_075 = [i for i, line in enumerate(base) if line.startswith("| EAL-075 |")]

assert len(eal_073) == 1
assert len(eal_075) == 1
insert_at = eal_073[0] + 1
assert eal_075[0] == insert_at
assert not any(line.startswith("| EAL-074 |") for line in base)

expected_current = base[:insert_at] + [EXPECTED] + base[insert_at:]
assert current == expected_current, "report.md has changes other than exact EAL-074 insertion"

assert current[insert_at - 1].startswith("| EAL-073 |")
assert current[insert_at] == EXPECTED
assert current[insert_at + 1].startswith("| EAL-075 |")
assert current[insert_at + 2].startswith("| EAL-076 |")

fields = [part.strip() for part in EXPECTED.strip("|").split("|")]
assert len(fields) == 14, len(fields)

print("exact EAL-074-only insertion verified")
PY
```

### 6.2 Red v2 canonical/raw bytes

```bash
sha256sum \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md"
```

両方の期待値:

```text
90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b
```

さらに:

```bash
cmp \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md"
```

exit codeは`0`でなければならない。

### 6.3 Existing repository artifacts

```bash
git diff --exit-code \
  26d40034507b60f76d06536fb7c5e552bdb49850 \
  -- \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md" \
  "$ISSUE_DIR/artifacts/characterization" \
  "$ISSUE_DIR/artifacts/implementation-briefs" \
  "$ISSUE_DIR/requirement.md" \
  "$ISSUE_DIR/design.md" \
  "$ISSUE_DIR/plan.md"
```

### 6.4 Runtimeとtests

```bash
git diff --exit-code \
  26d40034507b60f76d06536fb7c5e552bdb49850 \
  -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  tests
```

Runtime/test変更は0件でなければならない。

---

## 7. Report validation

### 7.1 EAL連番

```bash
python - <<'PY'
from pathlib import Path

path = Path(
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
    "report.md"
)
lines = path.read_text(encoding="utf-8").splitlines()

selected = [
    line.split("|")[1].strip()
    for line in lines
    if line.startswith(("| EAL-073 |", "| EAL-074 |", "| EAL-075 |", "| EAL-076 |"))
]
assert selected == ["EAL-073", "EAL-074", "EAL-075", "EAL-076"], selected
assert sum(line.startswith("| EAL-074 |") for line in lines) == 1
print(selected)
PY
```

### 7.2 Required identity strings

```bash
rg -n \
  'EAL-074|90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b|ec179c301c045f94d54abea308c47e79d16c5979|RT-354-S09-V2-001|RT-354-S09-V2-002' \
  "$ISSUE_DIR/report.md"
```

`EAL-074`は一行だけであり、Red v2 SHA、reviewed HEAD、finding IDsがその行に含まれること。

### 7.3 Repository validation

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

コードまたはtestの変更はないため、pytest、Ruff、Mypyを今回の修正証跡として再実行・再主張しない。既存のEAL-076 test evidenceを変更しない。

### 7.4 Scope

Commit前:

```bash
git diff --name-only
```

期待値:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md
```

それ以外のpathが存在する場合は停止する。

---

## 8. Commitとpush

推奨commit message:

```text
docs(iss-00354): restore S09 Red v2 EAL-074 evidence row
```

Commit後:

```bash
git status --short
git rev-parse HEAD
git push origin HEAD:codex/iss-00354-chatgpt-context-contract
git rev-parse HEAD
git rev-parse '@{upstream}'
git rev-list --left-right --count HEAD...'@{upstream}'
```

期待結果:

```text
worktree clean
HEAD == upstream
ahead 0 / behind 0
```

Source HEAD `26d40034507b60f76d06536fb7c5e552bdb49850`は履歴として保持し、resulting HEADを新しいfresh Red v4 review targetとして記録する。

Candidate identityは変更しない。

```text
Candidate version = s09-blue-repair-v2
Candidate ID = iss-00354-s09-blue-repair-v2-20260805T225843Z
```

---

## 9. Fresh Red v4 handoff条件

次をすべて満たした場合だけ、fresh Red v4へ渡す。

```text
repository = chemitaro/spec-dock
branch = codex/iss-00354-chatgpt-context-contract
source_head = 26d40034507b60f76d06536fb7c5e552bdb49850
resulting_head = <new pushed exact SHA>
candidate_version = s09-blue-repair-v2
candidate_id = iss-00354-s09-blue-repair-v2-20260805T225843Z
red_v3_review_sha256 = aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2
finding_repaired = RT-354-S09-V3-001
changed_files = report.md only
EAL sequence = 073, 074, 075, 076
Red v2 canonical/raw SHA = 90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b
runtime_changed = false
tests_changed = false
existing_briefs_changed = false
existing_reviews_changed = false
requirement_design_plan_changed = false
spec_dock_validate = pass
git_diff_check = pass
branch_parity = identical / ahead 0 / behind 0
closure_claim = none
handoff_status = ready_for_fresh_review
next_action = fresh Red v4
```

Fresh Red v4はv3とは別のfresh、read-only、defect-only reviewとして、resulting pushed exact HEADを確認する。

---

## 10. 停止条件

次のいずれかではcommit/pushせず停止する。

1. Named branchまたはsource HEADが固定identityと一致しない。
2. Source reportに`EAL-074`が既に存在する。
3. `EAL-073`直後が`EAL-075`ではない。
4. Exact rowを挿入するために`EAL-073`、`EAL-075`、`EAL-076`の編集が必要になる。
5. Red v2 canonical/raw SHAが`90354...c43c4b`と一致しない。
6. Red v3 review SHAが`aaf20c...15b6f2`と一致しない。
7. Runtime、tests、briefs、reviews、receipts、requirement、design、planへ差分が生じる。
8. Markdown tableの14-field schemaを維持できない。
9. SpecDock validateまたは`git diff --check`が失敗する。
10. Default branch、別branch、wrapper、API、fallbackが必要になる。
11. Fresh Red v3の判定、Candidate identity、S09 current rowsを変更する必要が生じる。
12. S09 closureまたはS10開始を同じ修正で宣言する必要が生じる。

本作業の完了状態は、`EAL-074`復元済みの新しいpushed exact HEADをfresh Red v4へ渡せる状態までである。

```text
closure_claim = none
handoff_status = ready_for_fresh_review
```
