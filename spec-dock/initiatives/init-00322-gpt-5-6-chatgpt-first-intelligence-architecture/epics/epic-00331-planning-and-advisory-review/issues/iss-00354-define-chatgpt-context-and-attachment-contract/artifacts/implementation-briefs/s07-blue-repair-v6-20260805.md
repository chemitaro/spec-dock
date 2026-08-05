# S07 Blue Team Repair Brief v6

* repository: `chemitaro/spec-dock`
* branch: `codex/iss-00354-chatgpt-context-contract`
* source_head: `d96ce0807340631bbf214ed24cdfe9bd91165780`（GitHub named branch tip と `identical`、ahead `0`、behind `0`）
* red_review: `S07 Fresh Red Team Review v6` — `FAIL` / P0=`0` / P1=`1` / P2=`0` / P3=`0` / finding=`RT-354-S07-V6-001`
* scope: `report.md` の2セルのみ
* model_requested: `GPT-5.6 Pro`
* model_resolved: `GPT-5.6 Pro`
* model_verified: `no`

Fresh Red v6は、`EAL-053`の`next_action`と`Closure Coverage`のS07行だけが、完了済みのv5 mutationおよびv5 reviewを未来の作業として再要求していると判定した。その他のS07 narrative、S90、Final Code Review、Final Spec Review、Final Commit、Skill、Epic、cleanup receipt、runtime、tests、Issue三文書は整合済みであり、変更対象外である。

## Exact edits

### EAL-053 next_action

対象ファイル:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  report.md
```

GitHub exact HEAD上の`EAL-053`末尾の`next_action`は次の文である。

**置換前**

```text
v5 evidence importとdisposition修正をcommit/pushし、次のfresh Red v6でP0/P1=0を確認するまでS07 closure/S08/PR/merge/closeを保留
```

**置換後**

```text
v5 evidence、Blue repair v5 brief、v5 disposition correctionはexact HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780`へcommit/push済みであり、Red v5 reviewもFAIL（P0=0/P1=1、formal artifact SHA-256 `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`）として完了済みである。Fresh Red v6は同exact HEADに対してFAIL（P0=0/P1=1、`RT-354-S07-V6-001`）を返したため、現在のBlue修正は`report.md`のEAL-053 next_actionとClosure CoverageのS07行だけに限定する。修正をcommit/pushした後のexact HEADをfresh Red v7へ渡し、Red v7でP0/P1=0を確認するまで`cl-s07-projection` / `tc-s07-001`、S07、S08〜S13、PR、merge、Issue close、Issue finishを保留する。
```

この置換では`EAL-053`の他の列を変更しない。特に、source、source role、claim、evidence path、既存Blue briefのSHA、model evidenceは履歴として保持する。

### cl-s07-projection / tc-s07-001

GitHub exact HEAD上の現行`Closure Coverage`行は次のとおりである。

**置換前**

```md
| `cl-s07-projection` / `tc-s07-001` | S07 | S07 brief、Fresh Red v1〜v4 FAIL、Blue repair briefs、provider/installed/dogfood recursive parity、validate、diff-check、historical scope audit | four parity comparisons and historical scope audit pass; v4 exact HEAD `7538f749...` has P1×1 for repeated future commit/push wording; report-only correction is now the bounded Blue action and fresh Red v5 is pending | pending | close only on fresh Red v5 PASS |
```

**置換後**

```md
| `cl-s07-projection` / `tc-s07-001` | S07 | S07 brief、Fresh Red v1〜v6 FAIL、Blue repair briefs、provider/installed/dogfood recursive parity、validate、diff-check、historical scope audit | four parity comparisons and historical scope audit pass; v5 evidence、Blue repair v5 brief、v5 disposition correctionはexact HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780`へcommit/push済みであり、Red v5 reviewはFAIL（P0=0/P1=1、formal artifact SHA-256 `698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488`）として完了済み。Fresh Red v6は同exact HEADに対してFAIL（P0=0/P1=1、`RT-354-S07-V6-001`）を返し、残るbounded Blue actionはEAL-053 next_actionと本Closure Coverage行の同期だけである | pending / blocked | 修正後のexact pushed HEADに対するfresh Red v7がPASS（P0=0/P1=0）した場合だけcloseする。Red v7 PASSまでS08〜S13、PR、merge、Issue close、Issue finishを保留する |
```

この行では、既存のrecursive parity、validate、diff-check、historical scope auditの成功証跡を再判定しない。Red v6も、それらを再実行せず、今回のP1を上記2セルに限定している。

## Out of scope

変更してよいファイルは次の一件だけである。

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  report.md
```

その中でも編集対象は次の2セルだけである。

```text
Evidence Adoption Ledger:
  EAL-053 / next_action

Closure Coverage:
  cl-s07-projection / tc-s07-001 row
```

次はすべてread-onlyとし、内容・空白・改行・identityを変更しない。

```text
provider/root Issue Planning Skill
parent Epic requirement.md / design.md / plan.md
Issue requirement.md / design.md / plan.md
cleanup receipt
Blue repair briefs v1〜v5
Red reviews v1〜v6 canonical/raw
MANIFEST.json / CHECKSUMS.sha256 / Candidate identity
runtime / CLI / application / domain / infra
tests / fixtures
unrelated docs / reports / artifacts
```

理由は、Fresh Red v6が新規P1を上記2セルだけに限定し、他のS07 current-state行、Skill、Epic、projection、cleanup receipt、runtime、testsに新規のidentity・contract・projection不整合を認めていないためである。

既存のv1〜v5 review identity、finding、当時のdispositionはimmutable historyとして保持する。Candidate identity、architecture、runtime behavior、S07 scopeを変更しない。

## Verification

### 1. Exact identity preflight

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='d96ce0807340631bbf214ed24cdfe9bd91165780'

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"
```

いずれかが不一致なら編集を開始しない。default branch、別branch、添付だけの状態を代替sourceにしない。

### 2. Two-cell current-state assertions

```bash
REPORT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md'

uv run python - "$REPORT" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines()

eal_rows = [line for line in lines if line.startswith("| EAL-053 |")]
if len(eal_rows) != 1:
    raise SystemExit(f"EAL-053 row count must be 1, got {len(eal_rows)}")
eal = eal_rows[0]

coverage_header = "#### クロージャ網羅（Closure Coverage）"
delta_header = "#### クロージャ差分（Closure Delta）"
if text.count(coverage_header) != 1 or text.count(delta_header) != 1:
    raise SystemExit("Closure Coverage section is missing or ambiguous")

coverage = text.split(coverage_header, 1)[1].split(delta_header, 1)[0]
coverage_rows = [
    line
    for line in coverage.splitlines()
    if line.startswith("| `cl-s07-projection` / `tc-s07-001` |")
]
if len(coverage_rows) != 1:
    raise SystemExit(
        "cl-s07-projection / tc-s07-001 coverage row "
        f"count must be 1, got {len(coverage_rows)}"
    )
closure = coverage_rows[0]

required_eal = (
    "d96ce0807340631bbf214ed24cdfe9bd91165780",
    "698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488",
    "RT-354-S07-V6-001",
    "fresh Red v7",
    "S08〜S13",
    "Issue finish",
)
required_closure = (
    "Fresh Red v1〜v6 FAIL",
    "d96ce0807340631bbf214ed24cdfe9bd91165780",
    "698ff25d2f3b91b545f64a837bfad1f423fc0e56b7a93f48c2469f7f631d1488",
    "RT-354-S07-V6-001",
    "pending / blocked",
    "fresh Red v7",
    "S08〜S13",
    "Issue finish",
)

for token in required_eal:
    if token not in eal:
        raise SystemExit(f"EAL-053 next_action missing token: {token}")

for token in required_closure:
    if token not in closure:
        raise SystemExit(f"Closure Coverage row missing token: {token}")

stale_eal = (
    "v5 evidence importとdisposition修正をcommit/pushし",
    "次のfresh Red v6でP0/P1=0",
)
stale_closure = (
    "fresh Red v5 is pending",
    "close only on fresh Red v5 PASS",
    "report-only correction is now the bounded Blue action",
)

for token in stale_eal:
    if token in eal:
        raise SystemExit(f"stale EAL-053 state remains: {token}")

for token in stale_closure:
    if token in closure:
        raise SystemExit(f"stale Closure Coverage state remains: {token}")

print("S07 Red v6 two-cell current-state assertions: pass")
PY
```

### 3. One-file scope

適用後、commit前に次を確認する。

```bash
test "$(
  git diff --name-only "$SOURCE_HEAD"
)" = "$REPORT"

test -z "$(
  git ls-files --others --exclude-standard
)"
```

期待値:

```text
changed tracked files: 1
changed path: report.md
untracked files: 0
```

`report.md`内でも、差分は`EAL-053`の`next_action`と`Closure Coverage`のS07行だけでなければならない。

```bash
git diff -- "$REPORT"
```

第三の行・セルに差分があれば停止する。

### 4. Repository gates

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

期待値:

```text
validate: exit 0
git diff --check: exit 0
```

今回の修正はreport-onlyであり、runtime testやparityの再実行を新たな受入条件へ追加しない。既存のcommitted receiptを保持する。

### 5. Commit, push, and Fresh Red v7 handoff

通常のreviewed commit/push後に、resulting HEADを外部で確定する。

```bash
PUSHED_HEAD="$(git rev-parse HEAD)"

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$PUSHED_HEAD"
```

`PUSHED_HEAD`はこの修正前の`report.md`へ先取りして書かない。commit/push後に確定したfull SHAを、次の新規Fresh Red v7 threadへreview identityとして渡す。

Fresh Red v7の条件:

```text
repository:
  chemitaro/spec-dock

branch:
  codex/iss-00354-chatgpt-context-contract

reviewed HEAD:
  commit/push後に確定したexact full SHA

review mode:
  new thread
  read-only
  defect-only
  default branch fallbackなし

required result:
  P0=0
  P1=0
```

Red v7 PASS前は次を禁止する。

```text
cl-s07-projection closure
tc-s07-001 closure
S07 PASS claim
S08〜S13 start
PR / Delivery PR
merge
Issue close
Issue finish
```

モデル証跡はFresh Red v6 artifactの実測値だけを記録し、`GPT-5.6 Luna`または`Reasoning Effort Max`を主張しない。
