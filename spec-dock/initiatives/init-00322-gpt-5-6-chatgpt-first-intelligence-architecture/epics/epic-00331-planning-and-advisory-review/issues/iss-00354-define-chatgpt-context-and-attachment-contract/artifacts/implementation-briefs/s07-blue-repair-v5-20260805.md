# S07 Blue Team repair v5 implementation brief — `RT-354-S07-V5-001` one-sentence closure

## 1. Review identity

| 項目                       | 値                                                                  |
| ------------------------ | ------------------------------------------------------------------ |
| Repository               | `chemitaro/spec-dock`                                              |
| Named branch             | `codex/iss-00354-chatgpt-context-contract`                         |
| Exact repair source HEAD | `03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a`                         |
| GitHub branch comparison | `identical` / ahead `0` / behind `0`                               |
| Red v5 verdict           | `FAIL`                                                             |
| Severity                 | P0=0 / P1=1 / P2=0 / P3=0                                          |
| Formal finding           | `RT-354-S07-V5-001`                                                |
| Red v5 output SHA-256    | `1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc` |
| Default-branch fallback  | 未使用・禁止                                                             |

GitHub Connectorでnamed branchを直接確認し、branch tipが指定されたRed v5 reviewed HEADと一致することを確認した。Red v5はexact-HEAD、read-only、defect-only reviewとして、S07 v4 narrative末尾の`disposition`一文だけをP1とした。

## 2. P1の根拠

現行`report.md`の主要なEAL、delegation、milestone、S90、Final Commitは、次の状態を既に確立している。

1. v3 report-only correction `7538f74924f0052fe0a7e340b641c35ba1e2c716`はcommit/push済みで、Red v4へ渡された。
2. Red v4 canonical/raw evidenceは`76ab5b3be4ea26b88d3cfb342b1ef423d667225d`へimmutable evidenceとしてimport済みである。
3. v4 report-only current-state correctionもRed v5 reviewed candidateへcommit/push済みである。
4. v4 findingに対する追加のreport commit/pushは不要で、残っていたgateはfresh Red v5だけだった。

一方、`## S07 Fresh Red Team review v4 と Blue repair v4`の最終`disposition`は、同じreport correctionを今後修正・commit/pushしてからRed v5へ渡すものとして再度指示している。このため、完了済みmutationと次gateが相互矛盾している。Red v5は、immutable Red v4 artifactではなく、current observed-evidence ledgerである`report.md`側だけを修正対象としている。

## 3. 変更対象

変更してよいのは次の一ファイルだけである。

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  report.md
```

変更箇所は次の一文だけとする。

```text
## S07 Fresh Red Team review v4 と Blue repair v4
└── 最後の `- disposition:` 箇条書き
```

Provider／installed Skill、parent Epic、runtime、tests、cleanup receipt、Blue briefs v1〜v4、Red v1〜v5 canonical/raw、Issue/Epicのrequirement／design／plan、その他のfileはすべてread-onlyである。

## 4. Exact text-level correction

### 4.1 置換前

```md
- disposition: EAL-050/EAL-051としてv4 FAILとBlue repair briefを採用する。`report.md`のcurrent-state wordingだけを修正し、commit/push後の新しいexact HEADをv5の新規Fresh Red Team threadへ渡す。v5でP0/P1=0を確認するまで`cl-s07-projection` / `tc-s07-001`、S08、PR、merge、Issue close、Issue finishは保留する。
```

この文はGitHub上のexact reviewed HEAD `03ce7f0c...`にも存在する。

### 4.2 置換後

```md
- disposition: EAL-050/EAL-051としてv4 FAILとBlue repair briefを採用した。v3 report-only correction `7538f74924f0052fe0a7e340b641c35ba1e2c716` はcommit/push済みでRed v4へ渡され、Red v4 canonical/raw evidenceは `76ab5b3be4ea26b88d3cfb342b1ef423d667225d` にimmutable evidenceとしてimport済みである。v4 report-only current-state correctionもRed v5 reviewed candidate `03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a` にcommit/push済みであり、当該v4 repair時点で残るgateはこの修正済みexact HEADに対するfresh Red v5 reviewだけであった。Red v5 PASSまで`cl-s07-projection` / `tc-s07-001`、S07、S08、PR、merge、Issue close、Issue finishは保留する。
```

### 4.3 意味上の制約

* `7538f749...`のcommit/pushをfuture actionへ戻さない。
* `76ab5b3...`のRed v4 evidence importを未実施扱いしない。
* `03ce7f0c...`に含まれるv4 current-state correctionを未commit／未push扱いしない。
* このv4 historical dispositionにRed v5のPASSを自己主張しない。
* S07 closure、S08、PR、merge、Issue close、Issue finishを許可しない。
* Red v5 artifactの本文やhistorical review dispositionは変更しない。
* EAL、current-state table、Final Commitなど、Red v5が正として確認した他の行は変更しない。

## 5. Implementation sequence

1. Named branch、local HEAD、remote branch tipが`03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a`で一致することを確認する。
2. 対象section内の置換前`disposition`がexactly one存在することを確認する。
3. その一文だけを置換する。
4. `report.md`以外に差分がないことを確認する。
5. Section-local assertionと`git diff --check`を実行する。
6. 一ファイルだけcommit/pushする。
7. Push後のnamed branch exact tipを外部で取得し、新規Fresh Red v6へ渡す。
8. Red v6 PASS前はS07をcloseせず、S08以降へ進まない。

## 6. Verification commands

### 6.1 Identity preflight

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a'

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"
```

### 6.2 Target occurrence preflight

```bash
REPORT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md'

uv run python - "$REPORT" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

header = "## S07 Fresh Red Team review v4 と Blue repair v4"
next_header = "## 最終品質ゲート（Final Quality Gate / 必須）"
old = (
    "- disposition: EAL-050/EAL-051としてv4 FAILとBlue repair briefを採用する。"
    "`report.md`のcurrent-state wordingだけを修正し、commit/push後の新しいexact HEADを"
    "v5の新規Fresh Red Team threadへ渡す。v5でP0/P1=0を確認するまで"
    "`cl-s07-projection` / `tc-s07-001`、S08、PR、merge、Issue close、Issue finishは保留する。"
)

if text.count(header) != 1:
    raise SystemExit("S07 v4 narrative header is missing or ambiguous")

section = text.split(header, 1)[1].split(next_header, 1)[0]
if section.count(old) != 1:
    raise SystemExit("exact replacement target is missing or ambiguous")

print("target occurrence: pass")
PY
```

### 6.3 Post-edit semantic assertion

```bash
uv run python - "$REPORT" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

header = "## S07 Fresh Red Team review v4 と Blue repair v4"
next_header = "## 最終品質ゲート（Final Quality Gate / 必須）"
section = text.split(header, 1)[1].split(next_header, 1)[0]

required = (
    "7538f74924f0052fe0a7e340b641c35ba1e2c716",
    "76ab5b3be4ea26b88d3cfb342b1ef423d667225d",
    "03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a",
    "commit/push済み",
    "fresh Red v5 reviewだけであった",
    "S07、S08、PR、merge、Issue close、Issue finishは保留",
)

for token in required:
    if token not in section:
        raise SystemExit(f"missing corrected disposition token: {token}")

forbidden = (
    "current-state wordingだけを修正し、commit/push後",
    "新しいexact HEADをv5",
    "v5の新規Fresh Red Team threadへ渡す",
)

for token in forbidden:
    if token in section:
        raise SystemExit(f"stale future mutation remains: {token}")

if section.count("- disposition:") != 1:
    raise SystemExit("S07 v4 disposition is missing or duplicated")

print("S07 v4 disposition consistency: pass")
PY
```

### 6.4 One-file scope

```bash
SOURCE_HEAD='03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a'

test "$(
  git diff --name-only "$SOURCE_HEAD"
)" = "$REPORT"

test -z "$(
  git ls-files --others --exclude-standard
)"
```

### 6.5 Final static gate

```bash
git diff --check
git diff --stat "$SOURCE_HEAD"
git diff -- "$REPORT"
```

Expected result:

```text
changed files: 1
changed path: report.md
git diff --check: exit 0
stale future commit/push phrase: 0 matches
S07 PASS claim: none
S08 authorization: none
```

## 7. Stop conditions

次のいずれかでは修正を開始または継続しない。

* Named branch tip、local HEAD、remote branch tipのいずれかが`03ce7f0c...`と一致しない。
* 置換前のexact sentenceが0件または複数存在する。
* 一文置換だけではfindingを閉じられず、EAL、table、brief、review artifact等の変更が必要になる。
* `report.md`以外にtracked／untracked差分がある。
* Red v1〜v5 artifact、Blue brief、cleanup receipt、Skill、Epic、runtime、testsの変更が必要になる。
* 新しいfuture commit/push指示をv4 dispositionへ残す必要がある。
* Red v5 PASS、S07 closure、S08、PR、merge、Issue close、Issue finishを先取りする必要がある。
* `git diff --check`またはsection assertionが失敗する。

修正commitをpushした後、次の条件を満たすまでFresh Red v6を開始しない。

```text
repository = chemitaro/spec-dock
branch = codex/iss-00354-chatgpt-context-contract
local HEAD = origin/<same-branch> = pushed exact tip
changed production/evidence path = report.md only
default branch fallback = unused
```

Fresh Red v6は新規thread、read-only、defect-onlyとし、push後に外部で確定したexact HEADをreview identityとして受け取る。Red v6がP0=0／P1=0を返すまで、S07、S08、PR、merge、Issue close、Issue finishはblockedのままとする。

## 8. Model evidence

Red v5 artifactはreview modelを`GPT-5.6 Pro`と記録している。

`GPT-5.6 Luna`または`Reasoning Effort Max`について、wrapperが検証した実測証跡は提示されていない。したがって本ブリーフではLuna／Maxの使用または成功を主張しない。
