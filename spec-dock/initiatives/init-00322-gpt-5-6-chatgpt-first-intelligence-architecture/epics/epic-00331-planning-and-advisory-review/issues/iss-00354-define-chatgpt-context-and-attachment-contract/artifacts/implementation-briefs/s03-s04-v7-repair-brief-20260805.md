# S03/S04 v7 Blue Team report-only repair brief

## 結論

canonical `report.md` の `Delegated Worker Evidence` にある **S03-S04 行の「親統合判断」セルだけ**を変更する。

変更は、既に push 済みの v6 report-only 修正を将来条件としている文言を現在状態へ訂正し、次のゲートを Fresh Red Team v8 に進める **1行・1文字列置換**に限定する。

GitHub connector で named branch `codex/iss-00354-chatgpt-context-contract` の tip が exact HEAD `48b0c86ee7e58ae8b971c15b14a3249db577e6d5` と `identical`、ahead `0`、behind `0` であることを確認済み。default branch fallback は使用していない。

exact HEAD の対象行には、v6 report-only 修正の push を将来条件として扱う文言が残っている。 Fresh Red Team v7 の唯一の P1 もこの時制残差であり、commit ledger 部分は解消済みである。

## 1. 編集対象

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md
```

対象セクション:

```text
#### 委任 worker 証跡（Delegated Worker Evidence）
```

対象行:

```text
| S03-S04 | dev-coder | ... |
```

対象セル:

```text
親統合判断（parent integration decision）
```

S03-S04 行の他のセルを再整形、改行、修正しない。

## 2. 置換前後

### 置換前

```text
v6 report-only修正をpushし、同一 resulting HEADでv7 PASSを確認してから両closureをcloseし、S05へ進む
```

### 置換後

```text
v6 report-only修正はpush済み。Fresh Red Team v8でP0/P1=0を確認してから両closureをcloseし、S05へ進む
```

この置換以外は行わない。

`48b0c86ee7e58ae8b971c15b14a3249db577e6d5` および今回生成される新しい修正 commit SHAを、`report.md` 本文へ自己参照として追加しない。SHA自己参照の欠落は v7 finding ではなく、先行 repair brief でも要求対象外とされている。

## 3. 不変範囲

次を変更しない。

* v1〜v7 の review history、verdict、finding、source identity
* review artifact の本文または SHA-256
* `#### コミット` の commit ledger
* `827e439d20557ef99e05f8ac844310915acce704` と commit message
* Final Code Review Gate、Final Spec Review Gate、Final Commit
* EAL、Objective Alignment Ledger、closure coverage、closure delta
* runtime、application、domain、infra
* unit、integration、e2e tests
* `requirement.md`、`design.md`、`plan.md`、ADR、assurance
* provider／installed／dogfood projection
* Review resource、provider assets、review policy
* S05以降の記録

commit ledger には既に full SHA `827e439d20557ef99e05f8ac844310915acce704` と正しい commit message が存在するため、再編集しない。

## 4. 作業開始 preflight

```bash
export BRANCH='codex/iss-00354-chatgpt-context-contract'
export BASE='48b0c86ee7e58ae8b971c15b14a3249db577e6d5'
export REPORT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md'

git fetch origin \
  "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$BASE"
test "$(git rev-parse "origin/$BRANCH")" = "$BASE"
test -z "$(git status --porcelain=v1)"
```

いずれかが失敗した場合は編集を開始しない。default branch は参照しない。

## 5. exact replacement 検証

編集後、次の検証で **BASE の `report.md` に対する上記1文字列置換だけ**であることを確認する。

```bash
python - <<'PY'
from pathlib import Path
import os
import subprocess

base = os.environ["BASE"]
report = os.environ["REPORT"]

old = (
    "v6 report-only修正をpushし、同一 resulting HEADでv7 PASSを確認してから"
    "両closureをcloseし、S05へ進む"
)
new = (
    "v6 report-only修正はpush済み。Fresh Red Team v8でP0/P1=0を確認してから"
    "両closureをcloseし、S05へ進む"
)

before = subprocess.check_output(
    ["git", "show", f"{base}:{report}"],
    text=True,
)
after = Path(report).read_text(encoding="utf-8")

old_count = before.count(old)
if old_count != 1:
    raise SystemExit(
        f"stop: BASE reportの置換対象件数が1ではない: {old_count}"
    )

if new in before:
    raise SystemExit("stop: BASE reportに置換後文言が既に存在する")

expected = before.replace(old, new, 1)
if after != expected:
    raise SystemExit(
        "stop: report.mdの差分が指定された1文字列置換だけではない"
    )

print("exact one-string replacement: pass")
PY
```

## 6. `git diff --check` と scope audit

```bash
git diff --check

test "$(git diff --name-only)" = "$REPORT"

test "$(
  git diff --numstat -- "$REPORT" |
    awk '{print $1 ":" $2}'
)" = '1:1'

git diff -- "$REPORT"
git status --short --branch
```

期待結果:

* changed file は canonical `report.md` のみ
* numstat は `1:1`
* diff hunk は S03-S04 worker 行の親統合判断だけ
* whitespace error なし
* v1〜v7履歴、commit ledger、Final Gate等に差分なし

pytest、ruff、mypy、provider update、projection regeneration、追加テストは実行対象にしない。この修正は report-only の1行訂正であり、生成系コマンドによる別ファイル差分を発生させない。

## 7. Commit／push

検証合格後、`report.md` だけを stage、commit、pushする。

```bash
git add -- "$REPORT"

git diff --cached --check
test "$(git diff --cached --name-only)" = "$REPORT"

git commit -m 'docs(iss-00354): v7 worker evidenceの時制を修正'

NEW_HEAD="$(git rev-parse HEAD)"

git push origin "HEAD:refs/heads/$BRANCH"

git fetch origin \
  "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

test "$NEW_HEAD" = "$(git rev-parse "origin/$BRANCH")"
test -z "$(git status --porcelain=v1)"

test "$(git diff --name-only "$BASE..$NEW_HEAD")" = "$REPORT"
git diff --check "$BASE..$NEW_HEAD"
```

push後、GitHub connector でも次を確認する。

```text
repository = chemitaro/spec-dock
branch = codex/iss-00354-chatgpt-context-contract
base = <NEW_HEAD>
head = codex/iss-00354-chatgpt-context-contract
status = identical
ahead = 0
behind = 0
```

新しい commit SHAは push後に確定した値を v8 review source として外部指定するだけとし、`report.md` へ追記しない。

## 8. Fresh Red Team v8 gate

新規の独立 thread で Fresh Red Team v8 を実行する。

```text
Repository: chemitaro/spec-dock
Branch: codex/iss-00354-chatgpt-context-contract
Source HEAD: <NEW_HEAD の full SHA>
default branch fallback: 禁止
Mutation: read-only
Review scope: RT-354-S03S04-V6-001 の残存時制だけ
```

v8 の確認対象:

1. named branch tip と `<NEW_HEAD>` が `identical`、ahead `0`、behind `0`。

2. S03-S04 worker 行から置換前文言が消えている。

3. 親統合判断が次の完全一致文言になっている。

   ```text
   v6 report-only修正はpush済み。Fresh Red Team v8でP0/P1=0を確認してから両closureをcloseし、S05へ進む
   ```

4. commit ledger の `827e439d20557ef99e05f8ac844310915acce704` と commit messageが保持されている。

5. v1〜v7 review history、source identity、artifact SHAが変更されていない。

6. runtime、tests、requirement/design/plan、provider/projection、Final Gateに差分がない。

7. `48b0c86...` または `<NEW_HEAD>` の report 内自己参照を PASS 条件として要求していない。

Fresh Red Team v8 が **P0=0 / P1=0** を返した場合に限り、同一 reviewed HEAD 上で次を実施可能とする。

* `cl-s03-path-input` / `tc-s03-001` を close
* `cl-s04-direct-transport` / `tc-s04-001` を close
* S05へ進む

v8 が FAIL、identity mismatch、または P0/P1を返した場合は、両closure、S05、PR、merge、Issue closeを保留する。

## 9. 停止条件

次のいずれかに該当した場合は commit／pushせず停止する。

* named branch tip または local HEAD が `48b0c86ee7e58ae8b971c15b14a3249db577e6d5` ではない。
* default branch fallback が必要になる。
* 作業開始時点で working tree が clean ではない。
* 置換前文言が0件または複数件存在する。
* `report.md` の差分が指定された1文字列置換と一致しない。
* `report.md` 以外に差分が発生する。
* numstat が `1:1` ではない。
* v1〜v7 review history、source identity、artifact SHA、commit ledger、Final Gateの変更が必要になる。
* runtime、tests、requirement/design/plan、provider/projectionの変更が必要になる。
* `48b0c86...` または新commit SHAの自己参照追加を要求される。
* `git diff --check`、scope audit、clean check、local／remote parity、GitHub exact comparisonのいずれかが失敗する。
* Fresh Red Team v8 PASS前にclosure、S05、PR、merge、Issue closeを要求される。
* finding外の文言整理、追加テスト、アーキテクチャ変更、patch、ZIPの生成が必要になる。

## 未検証事項

ローカル working tree の現在状態、新しく生成される commit SHA、push後の local／remote parity、Fresh Red Team v8 の判定は、本ブリーフ作成時点では未検証である。上記 preflight、scope audit、push後比較、v8 gateで確定する。
