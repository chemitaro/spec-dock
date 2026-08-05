# iss-00354 S08 実装ブリーフ — Regression / quality / closure evidence

## 結論

S08 は **evidence / ledger-only** とする。現行の production source および plan-listed focused tests には、S08 のために事前追加すべきコード／テスト欠落は確認されていない。変更対象は原則として次の `report.md` と、必要なら既存規約に従う step-local quality evidence だけである。

`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md`

ただし、closure ledger には次の **report-only gap** があるため、完全な no-op ではない。

1. plan の正規 S02 closure ID は `cl-s02-resources` だが、report の current-state rows は `cl-s02-profile` を使用している。
2. HEAD `20286bea6b5c37ceffffdbcf0100f51e3c721a00` は S07 v8 PASS と closure 更新を既に commit 済みである一方、report の一部 current-state rows は「EAL-058 と v8 evidence を今後 commit/push する」と記録したままである。
3. `Final Commit` 表は四列の header に対して S07 row が五セルあり、かつ `pending commit/push` の時制が残っている。
4. S08 は現在 `S08〜S13` の pending 集約行に埋まっているため、`cl-s08-regression` と `tc-s08-001` の専用 closure rows が必要である。

この S08 では production behavior、canonical requirement/design/plan、projection、S07 review artifact を変更しない。

---

## 確認済み identity

| 項目                      | 確認値                                                                |
| ----------------------- | ------------------------------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                                              |
| Branch                  | `codex/iss-00354-chatgpt-context-contract`                         |
| Verified source HEAD    | `20286bea6b5c37ceffffdbcf0100f51e3c721a00`                         |
| Branch comparison       | `identical` / ahead `0` / behind `0`                               |
| Default branch fallback | 使用していない                                                            |
| Commit purpose          | `docs(iss-00354): S07 v8 PASSを反映しクローズ条件を更新`                        |
| `plan.md` Git blob      | `c553db3d222f5c346c1d15c21f0242cebdee0de4`                         |
| `report.md` Git blob    | `959fca623bcdefc088d0fd77e348743fd054224a`                         |
| S07 v8 reviewed source  | `a534d14c19e7fc720f64f292c8d47d105238851f`                         |
| S07 v8 review SHA-256   | `0aa7ea8b085a6cdf85e1b0a82e428e788e21f4367284006e7234fb066b8f1ead` |

GitHub named branch と指定 HEAD の一致を確認済みである。HEAD `20286bea…` は S07 v8 PASS、canonical/raw review identity、および S07 closure 更新を取り込んだ commit である。

添付 bundle の plan、report、六つの focused test、四つの production source は、同じ exact HEAD の Git blob と照合済みである。

---

## S08 の目的

S01–S07 で保持・実装された次の契約を、一つの exact verification HEAD で回帰確認し、`cl-s08-regression` と `tc-s08-001` を閉じる。

* minimal body と opaque original paths。
* generated input pack、input tree inspection、copy、ZIP、hash materialization の不在。
* PATH Oracle、managed Chrome、typed output safety。
* old `--context-manifest` の hard cutover。
* Blue continuity、fresh Red、private handle/transcript 非公開。
* exact GitHub repository / named branch / HEAD gate。
* Candidate provenance、output manifest、publication safety。
* provider / installed / dogfood projection の S07 証跡不変性。
* focused pytest、Ruff、Mypy、SpecDock validate、`git diff --check` の全 exit `0`。
* closure ledger の current-state 整合。

S08 の delegation contract は `dev-coder`、許可パスは `tests/`、上記 `report.md`、step-local quality evidence であり、production behavior と unrelated docs の変更は禁止されている。

### 非目的

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` の変更。
* `requirement.md`、`design.md`、`plan.md`、ADR の改訂。
* provider、installed、dogfood projection の再生成または手編集。
* S07 v8 canonical/raw review、EAL-058、既存 Blue/Red evidence の変更。
* Oracle `0.17.0` profile、failure taxonomy、browser smoke、artifact reader に関する S09–S13 の実装。
* PR、merge、Issue close、Issue finish。
* whole-Issue QA、Oracle 0.17 formal compatibility、production rollout の完了 claim。

---

## 変更要否の判定

### テスト変更

**事前のテスト変更は不要。**

既存の plan-listed suite は次を既に直接検証している。

| Test path                                              | S08 で保持する主な契約                                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `tests/unit/application/test_issue_planning_prompt.py` | path-only input、opaque path、no inspection/materialization、minimal body、operation resources |
| `tests/unit/application/test_issue_planning.py`        | exact GitHub gate、publication/stale safety、Blue continuity、fresh Red、private evidence 非漏えい |
| `tests/unit/infra/test_issue_planning_chatgpt.py`      | PATH Oracle、direct repeated `--file`、one prompt、no generated pack、no personal wrapper      |
| `tests/unit/commands/test_issue_planning.py`           | repeatable path forwarding、old option rejection、typed request dispatch                     |
| `tests/cli_runtime/test_chatgpt_cli.py`                | CLI help/parser hard cutover、operation-specific option boundary                            |
| `tests/integration/test_issue_planning_e2e.py`         | create→review→revision→fresh review、exact access failure、no repository mutation            |

`tc-s08-001` は新しい pytest function 名を要求する契約ではなく、上記 suite と static gates を同一 HEAD で実行し、結果を ledger に束ねる **execution/evidence contract** である。

### 必須変更

`report.md` のみを修正する。

* S08 専用 closure rows を追加する。
* S02 の current closure ID を `cl-s02-resources` に正規化する。
* historical `cl-s02-profile` 記録は消さず、`Closure Delta` で `cl-s02-profile` → `cl-s02-resources` の alias を明示する。
* S07 の current-state rows を「evidence commit/push 完了済み、current source HEAD=`20286bea…`、S08 active」へ同期する。
* `Final Commit` 表を正しい四セル構造に戻す。
* S09–S13 および whole-Issue final gates は `pending` のまま保持する。

plan の Spec-Locked Closure Index は S02 を `cl-s02-resources` と定義している一方、現行 report は current closure rows で `cl-s02-profile` を使用している。

S07 の worker／milestone rows は、既に HEAD `20286bea…` に取り込まれた EAL-058 と v8 evidence を future action として残している。  `Final Commit` row も `pending commit/push` のままで、四列 header に対して五セルになっている。

### gate failure 時だけ許可する最小 test-only 修正

実行で実在する test gap が判明した場合だけ、原因に対応する既存 test file 一つへ限定する。

| Failure boundary                      | 許可する最小 test path                                       |
| ------------------------------------- | ------------------------------------------------------ |
| prompt/path/no-inspection             | `tests/unit/application/test_issue_planning_prompt.py` |
| application/thread/source/publication | `tests/unit/application/test_issue_planning.py`        |
| Oracle argv/direct transport          | `tests/unit/infra/test_issue_planning_chatgpt.py`      |
| command forwarding                    | `tests/unit/commands/test_issue_planning.py`           |
| CLI parser/help                       | `tests/cli_runtime/test_chatgpt_cli.py`                |
| whole lifecycle                       | `tests/integration/test_issue_planning_e2e.py`         |

production code の修正が必要なら S08 内で修正せず、対応する S01–S07 milestone を再オープンして停止する。

---

## exact command sequence

plan に記載された必須 command は次のとおりであり、置換、分割、省略、追加オプションを行わない。

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_e2e.py -q

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate
git diff --check
```

---

## same-HEAD evidence capture 手順

### 1. source preflight

最初に exact source を固定する。ここで不一致なら編集・テストを開始しない。

```bash
set -euo pipefail

REPOSITORY='chemitaro/spec-dock'
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='20286bea6b5c37ceffffdbcf0100f51e3c721a00'
UPSTREAM="origin/${BRANCH}"

test "$(git branch --show-current)" = "${BRANCH}"
test "$(git rev-parse HEAD)" = "${SOURCE_HEAD}"
test -z "$(git status --porcelain=v1)"
test "$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "${UPSTREAM}"
test "$(git rev-parse '@{upstream}')" = "${SOURCE_HEAD}"
test "$(git rev-list --left-right --count HEAD...'@{upstream}')" = $'0\t0'
```

記録する値:

```text
repository
branch
source_head
upstream
upstream_head
ahead
behind
pre_execution_status
```

### 2. rehearsal と report-only correction

1. source HEAD `20286bea…` で必須五 gates を一度実行する。
2. 全 exit `0` の場合だけ、`report.md` の ledger gap を修正する。
3. diff scope を確認する。通常は `report.md` と既存規約に従う step-local evidence だけでなければならない。
4. owning workflow が許可差分を focused commit に統合した後、その commit を `VERIFY_HEAD` とする。
5. `VERIFY_HEAD` が push 済みで upstream と一致した状態で、全 gates をもう一度実行する。**この二回目だけを closure の authoritative receipt とする。**

### 3. authoritative run

raw output は repository 外に保存し、tracked file を増やさない。

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
UPSTREAM="origin/${BRANCH}"
VERIFY_HEAD="$(git rev-parse HEAD)"
LOG_DIR="${TMPDIR:-/tmp}/iss-00354-s08-${VERIFY_HEAD}"

test "$(git branch --show-current)" = "${BRANCH}"
test -z "$(git status --porcelain=v1)"
test "$(git rev-parse '@{upstream}')" = "${VERIFY_HEAD}"
test "$(git rev-list --left-right --count HEAD...'@{upstream}')" = $'0\t0'

mkdir -p "${LOG_DIR}"
: > "${LOG_DIR}/exit-status.tsv"

run_gate() {
  local label="$1"
  shift

  set +e
  "$@" >"${LOG_DIR}/${label}.log" 2>&1
  local rc=$?
  set -e

  printf '%s\t%s\t%s\n' \
    "${label}" \
    "${rc}" \
    "$(git rev-parse HEAD)" \
    | tee -a "${LOG_DIR}/exit-status.tsv"

  test "$(git rev-parse HEAD)" = "${VERIFY_HEAD}"
  test "${rc}" -eq 0
}

run_gate focused-pytest \
  uv run pytest \
    tests/unit/application/test_issue_planning_prompt.py \
    tests/unit/application/test_issue_planning.py \
    tests/unit/infra/test_issue_planning_chatgpt.py \
    tests/unit/commands/test_issue_planning.py \
    tests/cli_runtime/test_chatgpt_cli.py \
    tests/integration/test_issue_planning_e2e.py -q

run_gate ruff \
  uv run ruff check \
    src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
    tests

run_gate mypy \
  uv run mypy \
    src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime

run_gate spec-dock-validate \
  ./spec-dock/scripts/spec-dock validate

run_gate diff-check \
  git diff --check

test "$(git rev-parse HEAD)" = "${VERIFY_HEAD}"
test "$(git branch --show-current)" = "${BRANCH}"
test -z "$(git status --porcelain=v1)"
test "$(git rev-parse '@{upstream}')" = "${VERIFY_HEAD}"
test "$(git rev-list --left-right --count HEAD...'@{upstream}')" = $'0\t0'

printf 'repository=%s\n' 'chemitaro/spec-dock'
printf 'branch=%s\n' "${BRANCH}"
printf 'verification_head=%s\n' "${VERIFY_HEAD}"
printf 'upstream=%s\n' "${UPSTREAM}"
printf 'worktree=clean\n'
```

### 4. same-HEAD 不変条件

* 五 gates の各実行前後で `git rev-parse HEAD == VERIFY_HEAD`。
* authoritative run 後に tracked diff を追加しない。
* authoritative run 後に report を変更した場合、その新しい HEAD で五 gates をすべて再実行する。
* `tee` の exit code ではなく、実コマンドの exit code を記録する。
* report の `verification_head` と、raw receipt の HEAD が一致する。
* report/evidence commit の SHA と `verification_head` を混同しない。report 自身の commit SHA を先取りして自己参照しない。
* test-only correction が発生した場合、旧 HEAD の PASS を流用せず、新しい exact HEAD で全 gates を再実行する。

---

## `report.md` の最小 ledger 更新

### 1. Evidence Adoption Ledger

source HEAD 時点の次の空き ID は `EAL-059`。次を一行で記録する。

```text
ID: EAL-059
adoption_status: adopted
source:
  - artifacts/implementation-briefs/s08-regression-quality-closure.md
  - cl-s08-regression same-HEAD command receipt
source_role: chatgpt-use-implementation-brief / s08-quality-execution
claim:
  - S08 is evidence/ledger-only
  - all required gates exited 0 on VERIFY_HEAD
  - no production source changed
target_artifact: report.md
target_section:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Final QA Gate / S99 input
evidence_strength: exact_head_quality_pass
blocking: no
next_action: begin S09 only through its own brief and gate
```

`EAL-058`、S07 v8 canonical/raw review、および SHA-256 `0aa7ea8…` は変更しない。S07 v8 の model receipt も S07 evidence のまま保持する。

### 2. TDD / Session Log

`S08〜S13` 集約行から S08 を分離し、次を記録する。

* `repository=chemitaro/spec-dock`
* exact branch。
* `source_head=20286bea6b5c37ceffffdbcf0100f51e3c721a00`
* authoritative `verification_head`
* focused pytest の pass/skip summary と exit `0`
* Ruff、Mypy、validate、diff-check の exit `0`
* pre/post worktree state。
* upstream、ahead `0`、behind `0`
* changed paths。
* production diff `0`
* test diff `0`、または実在 gap に対する exact test-only diff。

### 3. Step Contract Closure

専用行を追加する。

```text
S08 | cl-s08-regression | focused suite、static gates、validate、
closure-ledger audit が同一 verification HEAD で全 exit 0 |
exact command receipt、branch/HEAD/upstream/clean facts |
closed
```

S09–S13 は別の pending 行として残す。

### 4. Test Contract Closure

二行に分ける。

```text
cl-s08-regression | S08 | yes | quality evidence |
focused pytest / ruff / mypy / validate / diff-check |
all exit 0 on VERIFY_HEAD | pass
```

```text
tc-s08-001 | S08 | yes | command-level regression |
same exact commands、same verification HEAD、clean current branch |
all exit 0 | pass
```

### 5. Closure Coverage

`cl-s08-regression` / `tc-s08-001` の専用行を `closed` とし、証跡に次を含める。

* exact `VERIFY_HEAD`
* command receipt path
* exit-status matrix
* no-production-drift scope audit
* S02 closure alias correction
* S07 immutable evidence preservation
* S99 input only、whole-Issue final closure は未完了

### 6. Closure Delta

historical textを削除せず、次の alias correction を追加する。

```text
change: alias-normalization
historical alias: cl-s02-profile
canonical closure id: cl-s02-resources
test id: tc-s02-001
reason: plan.md Spec-Locked Closure Index is authoritative
plan amendment required: no
re-review required: report audit only
```

current-state rows では `cl-s02-resources` を使用する。

### 7. S07 current-state repair

次だけを現在形へ直す。

* `Delegated Worker Evidence` の S07 parent integration decision。
* `Milestone / Commit Candidate Gate` の S07 row。
* `Final Commit` row。

意味は次に統一する。

```text
S07 v8 evidence adoption and closure update was committed as
20286bea6b5c37ceffffdbcf0100f51e3c721a00.
The named branch and that exact HEAD were verified identical.
S07 review evidence remains immutable.
S08 is the active next gate.
```

`Final Commit` row は header と同じ四セルへ直す。

### 8. Delegation / worker / milestone rows

S08 を `completed-and-closed` にするのは全 gates が exit `0` の場合だけ。

* delegated role: `dev-coder`
* actual changed files
* no production files
* no projection files
* no S07 review files
* command summary
* exact verification HEAD
* clean branch/upstream facts
* residual risk: S09–S13 pending

### 9. Final QA Gate / S99 input

S08 regression resultを **S99 input** として記録する。ただし次は維持する。

```text
S08 regression gate: pass
whole-Issue QA: pending
S09-S13: pending
PR / merge / Issue close / Issue finish: not performed
```

---

## 停止条件

次のいずれかでは `cl-s08-regression` / `tc-s08-001` を閉じない。

1. branch、HEAD、upstream のいずれかが不一致。
2. preflight worktree が dirty、または既存の scope 外変更がある。
3. focused pytest、Ruff、Mypy、validate、diff-check のいずれかが nonzero。
4. command 間で HEAD が変化する。
5. authoritative run 後に tracked file が変更される。
6. production source、canonical docs、projection、S07 review evidence に差分が出る。
7. `cl-s02-profile` / `cl-s02-resources` の不整合が current ledger に残る。
8. S07 の commit/push 状態または `Final Commit` table が stale／malformed のまま。
9. projection drift が検出される。S08 で projection を再生成せず、S07 scopeへ戻す。
10. failure 修正に production behavior change が必要になる。
11. local passだけで upstream equality、clean worktree、exact verification HEAD を証明できない。
12. qa-reviewer または code-reviewer が stale closure／production drift を検出する。

失敗時は commit candidate を作らず、S08 を `blocked` として command、exit status、HEAD、failure location を report に記録する。

---

## リスクと禁止 claim

* `git diff --check` の exit `0` だけでは clean worktree を証明しない。`git status --porcelain=v1` を別に記録する。
* S07 parity は immutable evidence として保持する。S08 で未指定 parity command を発明したり、projection を更新したりしない。
* focused suite が pass しても Oracle `0.17.0` formal browser compatibility、S09 profile、S10 recovery、S11 browser evidence、S12 artifact reader、S13 whole-Issue closureを証明しない。
* test-only correction があっても production bug 修正完了とは表現しない。
* S08 PASS は PR、merge、Issue close、Issue finish、Human adoption を意味しない。
* model label を product runtime の accepted mapping として使用しない。
* fresh Red S07 evidence を S08 の新しい ChatGPT submission/model evidenceとして再利用しない。

---

## モデル／strategy 証跡

| 区分                              | 証跡                                                                                 |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| 要求された実装ブリーフ target              | `GPT-5.6 Luna` / `Reasoning Effort Max`                                            |
| この応答で確認できるモデル                   | `GPT-5.6 Pro`                                                                      |
| この応答の strategy / effort receipt | 検証可能な `strategy`、`verified`、Reasoning Effort receipt はない                           |
| Luna / Max 成功証跡                 | ない。成功したと主張しない                                                                      |
| immutable S07 v8 receipt        | requested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、strategy `select`、verified `yes` |
| S07 receipt の意味                 | S07 review execution の証跡だけ。S08 brief、本応答、Codex runtime、product runtime のモデル証明ではない  |

---

## 未検証事項

* このブリーフ生成中に pytest、Ruff、Mypy、validate、`git diff --check` は実行していない。
* GitHub branch identity は確認済みだが、Codex 実行環境の local worktree cleanliness、upstream tracking、command exit status は未確認。
* 「テスト変更不要」は exact source/test inspection に基づく暫定判定であり、実行時 failure が実在 gap を示した場合は、上記 test-only 最小 correction ruleを適用する。
* `cl-s08-regression` と `tc-s08-001` は、authoritative same-HEAD receipt が得られるまで未完了である。

---

## 実装チェックリスト

* [ ] repository、branch、source HEAD `20286bea6b5c37ceffffdbcf0100f51e3c721a00`、upstream、clean state を確認する。
* [ ] speculative test を追加せず、まず plan-listed suite を実行する。
* [ ] `report.md` の S02 closure ID、S07 current-state、Final Commit table、S08専用 rowsだけを修正する。
* [ ] EAL-058 と S07 v8 canonical/raw evidence を変更しない。
* [ ] 許可差分を focused candidate HEAD に統合する。
* [ ] candidate HEAD 上で authoritative command sequence を全再実行する。
* [ ] `EAL-059`、`cl-s08-regression`、`tc-s08-001`、S99 inputを実測値だけで記録する。
* [ ] S09–S13、PR、merge、Issue close、Issue finishを pending のまま保持する。

## 検証チェックリスト

* [ ] focused pytest exit `0`
* [ ] Ruff exit `0`
* [ ] Mypy exit `0`
* [ ] `spec-dock validate` exit `0`
* [ ] `git diff --check` exit `0`
* [ ] 全 command が同じ `VERIFY_HEAD`
* [ ] current branch が `codex/iss-00354-chatgpt-context-contract`
* [ ] upstream HEAD が `VERIFY_HEAD`
* [ ] ahead `0` / behind `0`
* [ ] authoritative run 前後の worktree が clean
* [ ] production source diff `0`
* [ ] projection diff `0`
* [ ] S07 review evidence diff `0`
* [ ] current closure ID が `cl-s02-resources`
* [ ] `cl-s08-regression` と `tc-s08-001` が専用 rows で `closed` / `pass`
* [ ] whole-Issue final QA、S09–S13、PR、merge、Issue close、Issue finishは未完了のまま
