# S07 Blue Team minimal repair brief v1 — Fresh Red P1 four-item closure

## identity / repair target

| 項目                       | 値                                                         |
| ------------------------ | --------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                     |
| Named branch             | `codex/iss-00354-chatgpt-context-contract`                |
| Exact repair source HEAD | `21a2c4c2bfb6e30a925e64f8bb9508687b128417`                |
| S07 base                 | `68afc5bb009256231976877475d4038f3e95b728`                |
| Branch relation          | source HEAD is named-branch tip; baseよりahead 1 / behind 0 |
| Fresh Red verdict        | `FAIL`                                                    |
| Findings                 | P0=0 / P1=4 / P2=0 / P3=0                                 |
| Default-branch fallback  | 未使用・禁止                                                    |
| Repair scope             | `RT-354-S07-001`〜`RT-354-S07-004`だけ                       |

GitHub Connectorでnamed branchを直接確認し、tipがFresh Redのreviewed exact HEAD `21a2c4c2...`と一致することを確認した。現行commitはS07 docs／projection／parent wording／evidenceの15ファイルを変更した一つのcommitである。

本修正はS07の再設計ではない。現行S07 plan、元実装ブリーフ、Fresh Redの四つのP1をauthorityとし、既に確認された正の事項を変更しない。  

## repair outcome

修正後は、次の四条件を同じpushed HEADで満たすこと。

1. Parent Epic Design §6.3が、Issue Planning inputをopaque original pathとして扱い、input-side snapshot／hash／manifestを要求しない。
2. Official Issue Planning Skillが、formal runにおける`local-context` bypassを一切許可しない。
3. Official Skillが`--provided-context-path`の操作別境界をcreate／review／semantic revise／apply間で正確に示す。
4. Provider／dogfood／fresh installedのskill/docs treeについて、除外なしのrecursive byte parityとcontent-free receiptが存在し、reportがreviewed pushed HEADとFresh Red FAILを正確に記録する。

## minimal changed-file allowlist

### 直接編集してよいファイル

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/design.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  artifacts/20260805t-projection-cleanup-analysis.md
```

### 既存projection機構でのみ生成してよいファイル

```text
.agents/skills/spec-dock-issue-planning/SKILL.md
```

Root dogfood Skillは手編集しない。Provider Skillを修正した後、current checkoutのprovider sourceを使う既存update機構で生成する。

### Read-only

```text
src/spec_dock/assets/spec_dock/scripts/**
src/spec_dock/assets/spec_dock/docs/**
spec-dock/docs/**
tests/**

parent Epic requirement.md
parent Epic plan.md

iss-00354 requirement.md
iss-00354 design.md
iss-00354 plan.md
iss-00354 reviews/**
iss-00354 artifacts/implementation-briefs/s07-projection-docs-consistency.md
S06 artifacts / reviews
```

`workflow_issue.md`と汎用authoring-pack docsは、Fresh Redが現行S07契約との整合を正の事項として確認しているため変更しない。 現行`workflow_issue.md`はexact branch、opaque `--provided-context-path`、Blue continuity／fresh Red、pre-submit／post-submit境界を既に記載している。

## required repair 1 — `RT-354-S07-001`

### 対象

```text
parent Epic design.md
§6.3 Prompt and reference attachments
```

現行§6.3は、入力添付をbyte snapshotとし、`name`、source label、SHA、reference purposeを含むattachment manifestを要求している。これは同じDesign内のopaque original-path契約と矛盾する。 

### 必須変更

§6.3の本文だけを、次の意味へ限定置換する。

```md
### 6.3 Prompt and reference attachments

Issue Planning の formal run は、次の三つを分離する。

1. Chat フォーム本文は compact な goal、role、authority、exact repository /
   named branch / HEAD、fallback prohibition、output contract を持つ。
2. operation 固有の詳細手順は、operation identity から選択される
   provider-owned operation resources が持つ。
3. 追加 reference は repeatable な `--provided-context-path` で、選択済みの
   original top-level path のまま渡す。

`--provided-context-path` の file / directory operand は untrusted reference
data であり、本文または provider-owned resources の authority を上書きしない。
Issue Planning runtime は input operand の内容を walk、open、snapshot、hash、
archive、filter、rename、copy、または input attachment manifest 化しない。

この input-side boundary は output-side validation を変更しない。Oracle が生成した
authoring ZIP または Review JSON に対する artifact metadata、safe snapshot、
size / SHA、path、ZIP / JSON validation は §6.4 および §6.5 の既存 contract として
維持する。
```

### 不変条件

* §4、§6.5、§9の既に修正済みsession wordingを変更しない。
* Output authoring ZIP、Review JSON、Candidate MANIFEST／CHECKSUMSのvalidationを弱めない。
* Parent Requirement、AC ID、Design frontmatter、plan、Issue Boundary Mapを変更しない。
* Oracle 0.17固有flag、profile field、failure taxonomyをParentへ追加しない。

## required repair 2 — `RT-354-S07-002`

### 対象

```text
src/spec_dock/assets/install_root/.agents/skills/
  spec-dock-issue-planning/SKILL.md
Stop Conditions
```

現行Skillは次の条件を残している。

> Repository/branch evidence ... is unavailable and no explicit local-context run was approved.

この表現は、明示承認された`local-context`によってformal Issue Planningのexact GitHub gateを迂回できる正の経路を残す。 

### 必須変更

該当bulletを次へ置換する。

```md
- The exact current repository, named branch, and HEAD cannot be verified
  through GitHub for the formal Issue Planning run. Stop unconditionally.
  Do not substitute `local-context`, the default branch, another branch,
  attachments, prompt context, or memory.
```

### 不変条件

* 汎用authoring-pack laneの`local-context`機能自体は削除しない。
* `Manual Backup`のhuman-approved emergency条件は変更しない。
* Formal Candidate／Review／Human Gate／applyへ`local-context`を接続しない。
* GitHub connector unavailable、named branch unavailable、wrong branch only availableの全ケースを同じfail-closed条件に含める。

## required repair 3 — `RT-354-S07-003`

### 対象

```text
provider SKILL.md
Operating Spine
Context and attachment boundary
```

Runtimeではcreate、review、reviseが`provided_context_paths`を持つ一方、applyは持たない。argument registrationもcreate／review／reviseだけである。

現行Skillはcreate例にしかoptionを示さず、review／semantic revise／applyの境界が不明確である。

### 必須変更

#### Review手順

archive Reviewのcommand例に、必要時のrepeatable optionを示す。

```bash
./spec-dock/scripts/spec-dock-chatgpt review planning \
  --issue <iss-id> --mode archive-candidate \
  --candidate <candidate.zip> --output <external-review-dir> \
  --provided-context-path <additional-review-reference>
```

直後に次を記載する。

```md
The same repeatable option may be used with the explicit `git-bound` Review
form. Each operand remains an already-selected opaque file or directory path;
preserve operand order and identity and do not inspect or materialize its
contents.
```

#### Semantic Revision手順

既存command例へoptional referenceを追加する。

```bash
./spec-dock/scripts/spec-dock-chatgpt planning revise \
  --candidate <candidate.zip> \
  --request <external-review-dir>/planning-revision-request.json \
  --output <external-output-dir> \
  --provided-context-path <additional-revision-reference>
```

直後に操作別境界を固定する。

```md
`--provided-context-path` is available only for Planning create, Formal
Planning Review, and Semantic Revision. Do not add or pass it to
`planning apply`. A closed Mechanical Revision uses its deterministic
path / field / literal scope and does not consume this open reference option.
```

### 不変条件

* Runtime、CLI、parser、request dataclass、testsを変更しない。
* Review mode selection、same Candidate binding、fresh Redを変更しない。
* Semantic RevisionのP0/P1 trigger、fixed sibling Review JSONを変更しない。
* Mechanical laneへ新しいpublic commandまたはoptionを追加しない。
* Applyへoptionを追加しない。

## required repair 4 — `RT-354-S07-004`

### 4.1 projection source preflight

前回は異なる世代のremote packageをcurrent-branch projectionの代用として実行し、S07対象外の生成物が混入した。現行cleanup artifactはこの事実を記録しているが、fresh installed treeのrecursive receiptを持たない。 

更新前に、importされるinstallerがcurrent checkoutのprovider sourceであることを確認する。

```bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

PYTHONPATH="$ROOT/src" uv run python - <<'PY'
from pathlib import Path
import spec_dock.cli

root = Path.cwd().resolve()
observed = Path(spec_dock.cli.__file__).resolve()
expected = (root / "src/spec_dock/cli.py").resolve()

if observed != expected:
    raise SystemExit(
        f"wrong installer source: observed={observed}, expected={expected}"
    )

print(f"provider_installer_source={observed}")
PY
```

### 4.2 provider-first projection

Provider Skillだけを直接編集した後、次を一回実行する。

```bash
PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli update "$ROOT"
```

実行後、root dogfood Skillにproviderと同一bytesが生成されていることを確認する。Updateがallowlist外のtracked bytesを変更した場合は、生成先を個別修正せず停止する。

### 4.3 fresh installed target

```bash
INSTALL_TMP="$(mktemp -d)"
trap 'rm -rf "$INSTALL_TMP"' EXIT

PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli init "$INSTALL_TMP"
```

### 4.4 recursive byte parity

次の四組を、個別file allowlist、除外、glob skip、content-based exceptionなしで比較する。

```text
provider skill  ↔ dogfood skill
provider skill  ↔ fresh installed skill
provider docs   ↔ dogfood docs
provider docs   ↔ fresh installed docs
```

```bash
PYTHONPATH="$ROOT/src" uv run python - "$INSTALL_TMP" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

repo = Path.cwd().resolve()
installed = Path(sys.argv[1]).resolve()

pairs = (
    (
        "skill_provider_dogfood",
        repo / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning",
        repo / ".agents/skills/spec-dock-issue-planning",
    ),
    (
        "skill_provider_fresh_installed",
        repo / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning",
        installed / ".agents/skills/spec-dock-issue-planning",
    ),
    (
        "docs_provider_dogfood",
        repo / "src/spec_dock/assets/spec_dock/docs",
        repo / "spec-dock/docs",
    ),
    (
        "docs_provider_fresh_installed",
        repo / "src/spec_dock/assets/spec_dock/docs",
        installed / "spec-dock/docs",
    ),
)


def read_tree(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        raise SystemExit(f"missing parity root: {root}")

    result: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise SystemExit(f"unexpected symlink: {root}:{relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise SystemExit(f"unexpected non-file: {root}:{relative}")
        result[relative] = path.read_bytes()
    return result


def tree_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, data in sorted(files.items()):
        file_digest = hashlib.sha256(data).hexdigest()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(file_digest.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


for label, source_root, projection_root in pairs:
    source = read_tree(source_root)
    projection = read_tree(projection_root)

    missing = sorted(set(source) - set(projection))
    extra = sorted(set(projection) - set(source))
    changed = sorted(
        relative
        for relative in set(source) & set(projection)
        if source[relative] != projection[relative]
    )

    if missing or extra or changed:
        raise SystemExit(
            json.dumps(
                {
                    "comparison": label,
                    "status": "failed",
                    "source_root": str(source_root),
                    "projection_root": str(projection_root),
                    "missing": missing,
                    "extra": extra,
                    "changed": changed,
                    "parity_exclusions": [],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )

    source_digest = tree_digest(source)
    projection_digest = tree_digest(projection)
    if source_digest != projection_digest:
        raise SystemExit(f"{label}: tree digest mismatch")

    print(
        json.dumps(
            {
                "comparison": label,
                "status": "pass",
                "source_root": str(source_root.relative_to(repo))
                    if source_root.is_relative_to(repo)
                    else "<fresh-installed>",
                "projection_root": str(projection_root.relative_to(repo))
                    if projection_root.is_relative_to(repo)
                    else "<fresh-installed>",
                "file_count": len(source),
                "tree_sha256": source_digest,
                "parity_exclusions": [],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
PY
```

### 4.5 evidence artifact update

`20260805t-projection-cleanup-analysis.md`の既存履歴は削除しない。その末尾に、次のcontent-free receiptを追加する。

```text
repair_source_head: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
provider_source_preflight:
  command
  observed module path category
  exit_code
projection_update:
  exact command
  exit_code
fresh_install:
  exact command
  exit_code
recursive_parity:
  - comparison
  - source_root
  - projection_root
  - file_count
  - tree_sha256
  - parity_exclusions: []
  - status
validate:
  exact command
  exit_code
diff_check:
  exact command
  exit_code
scope_audit:
  unexpected_changed_files: []
```

Private temporary directory名、private host path、session handle、raw command transcriptは記録しない。Fresh installed rootは`<fresh-installed>`等のcontent-free labelに正規化する。

### 4.6 report correction

`report.md`は、current working treeや未来のcommitとして`21a2c4c2...`を扱ってはならない。現行reportには、S07を「current S07 working tree」「commit/push後にreview」とする記載が残っている。 

少なくとも次を更新する。

#### Evidence Adoption Ledger

新しいentryを追加する。

```text
source_role: chatgpt-use-red-team-docs
reviewed_head: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
verdict: FAIL
findings:
  RT-354-S07-001
  RT-354-S07-002
  RT-354-S07-003
  RT-354-S07-004
adoption_status: adopted
evidence_strength: fresh_fail
blocking: no for Issue history; yes for S07 closure/S08 start
next_action: bounded Blue repair, push new HEAD, fresh Red re-review
```

添付されたFresh Red review bytesの本セッション内SHA-256は次である。

```text
6a41c95cbaf9c193cc3a22ad7e8588e96c9da58905256eb9273cd1da06473ae8
```

この値を利用する場合は、保存先artifactのbytesが添付reviewと一致することを再確認してから記録する。

#### S07 state rows

次のすべてを同じ意味へ統一する。

```text
review source: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
review state: failed
P0: 0
P1: 4
closure: pending
repair state: active
S08 start: prohibited
```

更新対象は少なくとも次である。

* TDD／implementation observationのS07 row
* Step Contract Closure
* Test Contract Closure
* Closure Coverage
* Implementation Delegation Gate
* Delegated Worker Evidence
* Reviewer Gate Status
* Milestone／Commit Candidate Gate
* 次アクション記載

`green pending fresh review`は使用せず、`parity evidence repaired; docs review failed at 21a2...; closure pending bounded repair and fresh re-review`相当とする。

#### Commit identity semantics

* `21a2c4c2...`は既にcommit／push済みのhistorical failed-review sourceである。
* Blue repair後のresulting HEADを、同じcommit内のreportへ自己参照で書かない。
* Repair commit／push後のexact HEADはexternal handoff evidenceとしてFresh Redへ渡す。
* Fresh Red PASS後に、別evidence updateまたはowning workflowのexternal recordでreviewed HEADを束縛する。
* Fresh Red PASS前に`cl-s07-projection`をclosedにしない。

## forbidden changes

* Runtime、CLI、application、domain、infra、tests、fixturesの変更。
* `--provided-context-path`の実装変更。
* `local-context`汎用evidence laneの削除。
* Parent Requirement、Parent plan、Issue Boundary Map、frontmatter stateの変更。
* `workflow_issue.md`、汎用authoring-pack docsの追加修正。
* iss-00354 canonical requirement／design／planの変更。
* 元S07 implementation briefのrewrite。
* S06 artifacts／review／closureの変更。
* Projection parityのためのallowlist、除外、例外pathの追加。
* Projection targetの手編集。
* New runtime test、migration alias、compatibility flagの追加。
* Candidate生成、canonical adoption、assurance promotion、PR、merge、Issue close。
* Fresh Red PASSまたはLuna／Reasoning Effort Max実測成功の先取り。

## implementation sequence

1. Named branch、local HEAD、remote named-branch tipが`21a2c4c2...`で一致することを確認する。
2. Provider SkillのStop Conditionと操作別`--provided-context-path`説明だけを修正する。
3. Parent Epic Design §6.3だけをinput opaque-path／output validation分離へ修正する。
4. Local provider-source preflightを通す。
5. Providerから既存update機構を実行し、dogfood Skillを再生成する。
6. Fresh temporary targetをinitする。
7. 四組のrecursive byte parityを除外なしで実行する。
8. Cleanup analysis artifactへcontent-free parity receiptを追記する。
9. ReportへFresh Red FAIL identity、四P1、parity receipt、pending closureを統合する。
10. Scope audit、validate、diff-checkを実行する。
11. Repairをcommit／pushした後、その新しいexact HEADを別のFresh Red threadへ渡す。
12. PASS前はS07 closure、S08、PR、merge、Issue closeへ進まない。

## exact verification commands

### Identity

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='21a2c4c2bfb6e30a925e64f8bb9508687b128417'
S07_BASE='68afc5bb009256231976877475d4038f3e95b728'

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"
git merge-base --is-ancestor "$S07_BASE" "$SOURCE_HEAD"
```

### Skill contract

```bash
SKILL_PROVIDER='src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md'
SKILL_DOGFOOD='.agents/skills/spec-dock-issue-planning/SKILL.md'

if rg -n \
  'no explicit local-context run was approved|local-context run was approved' \
  "$SKILL_PROVIDER" "$SKILL_DOGFOOD"
then
  echo 'formal local-context bypass remains' >&2
  exit 1
fi

rg -n -- '--provided-context-path' \
  "$SKILL_PROVIDER" "$SKILL_DOGFOOD"

cmp "$SKILL_PROVIDER" "$SKILL_DOGFOOD"
```

### Parent §6.3 semantic guard

```bash
PARENT_DESIGN='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/design.md'

uv run python - "$PARENT_DESIGN" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
start = text.index("### 6.3 Prompt and reference attachments")
end = text.index("### 6.4 Planner authoring ZIP and Candidate ZIP")
section = text[start:end]

required = (
    "--provided-context-path",
    "original top-level path",
    "walk",
    "snapshot",
    "output-side",
    "§6.4",
    "§6.5",
)
for token in required:
    if token not in section:
        raise SystemExit(f"missing §6.3 contract token: {token}")

forbidden = (
    "添付はsource／evidenceのbyte snapshot",
    "attachment manifestはname、source label、SHA",
)
for token in forbidden:
    if token in section:
        raise SystemExit(f"stale §6.3 input contract remains: {token}")

print("parent §6.3 contract: pass")
PY
```

### Report state guard

```bash
ISSUE_ROOT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract'
REPORT="$ISSUE_ROOT/report.md"
PARITY_ARTIFACT="$ISSUE_ROOT/artifacts/20260805t-projection-cleanup-analysis.md"

if rg -n \
  'current S07 working tree|commit/push and fresh Red Team review are the next gate|commit/push後にexact HEADをfresh Red Teamへ送る' \
  "$REPORT"
then
  echo 'stale S07 identity wording remains' >&2
  exit 1
fi

rg -n \
  '21a2c4c2bfb6e30a925e64f8bb9508687b128417|RT-354-S07-001|RT-354-S07-004' \
  "$REPORT"

rg -n \
  'parity_exclusions|tree_sha256|file_count|fresh.installed|exit_code' \
  "$PARITY_ARTIFACT"
```

### Scope audit

```bash
uv run python - "$SOURCE_HEAD" <<'PY'
from __future__ import annotations

import subprocess
import sys

base = sys.argv[1]

allowed = {
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md",
    ".agents/skills/spec-dock-issue-planning/SKILL.md",
    (
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/design.md"
    ),
    (
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/"
        "issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md"
    ),
    (
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/"
        "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
        "artifacts/20260805t-projection-cleanup-analysis.md"
    ),
}

changed = set(
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

unexpected = sorted((changed | untracked) - allowed)
if unexpected:
    raise SystemExit(f"out-of-allowlist changes: {unexpected}")

print("repair changed-file allowlist: pass")
PY
```

### Read-only boundaries

```bash
PARENT_ROOT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review'

git diff --exit-code "$SOURCE_HEAD" -- \
  src/spec_dock/assets/spec_dock/scripts \
  src/spec_dock/assets/spec_dock/docs \
  spec-dock/docs \
  tests \
  "$PARENT_ROOT/requirement.md" \
  "$PARENT_ROOT/plan.md" \
  "$ISSUE_ROOT/requirement.md" \
  "$ISSUE_ROOT/design.md" \
  "$ISSUE_ROOT/plan.md" \
  "$ISSUE_ROOT/reviews" \
  "$ISSUE_ROOT/artifacts/implementation-briefs/s07-projection-docs-consistency.md"
```

### Final repository gates

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

## acceptance criteria

| Finding          | PASS条件                                                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S07-001` | Parent §6.3にinput-side byte snapshot／SHA manifest契約がなく、opaque original pathとoutput-side safe snapshotが明確に分離されている        |
| `RT-354-S07-002` | Official provider／dogfood Skillのformal Stop Conditionに`local-context`例外がない                                              |
| `RT-354-S07-003` | Skillがcreate／archive review／git-bound review／semantic reviseでrepeatable optionを案内し、mechanical lane／applyでは使用しないと明記する    |
| `RT-354-S07-004` | 四つのrecursive comparisonが全てPASSし、各file count／tree digest／`parity_exclusions=[]`／command exit codeがartifactとreportから追跡できる |
| Identity         | `21a2c4c2...`がhistorical failed-review sourceとして記録され、repair後HEADのPASSを先取りしない                                            |
| Scope            | Runtime、tests、provider docs、parent Requirement／plan、Issue canonical三文書に差分がない                                            |
| Projection       | Provider Skillとdogfood Skillがbyte-identicalで、fresh installed Skillも同一treeである                                            |
| Repository       | `spec-dock validate`と`git diff --check`がexit 0                                                                          |
| Review gate      | 新しいpushed repair HEADに対するFresh RedでP0=0／P1=0になるまでS07はpending                                                            |

## stop conditions

次のいずれかではallowlistを拡張せず停止する。

* Named branch tipが`21a2c4c2...`から変わった。
* §6.3修正にParent Requirement、plan、Issue Boundary Mapの変更が必要になる。
* Skill修正にRuntime／CLI／tests変更が必要になる。
* `local-context`をformal Issue Planningへ残す必要がある。
* Mechanical Revisionまたはapplyへ`--provided-context-path`を追加する必要がある。
* Local provider-source preflightがcurrent checkoutの`src/spec_dock/cli.py`を解決しない。
* Updateがallowlist外のtracked fileを変更する。
* Recursive parityにmissing／extra／changed fileがある。
* Parityを通すために除外や許容差分を追加する必要がある。
* Fresh installed targetをprovider sourceから再現できない。
* Reportからreviewed pushed identity、四P1、command receiptを追跡できない。
* `validate`または`git diff --check`が失敗する。
* Fresh RedがP0／P1を返す。

## report evidence fields

```text
step: S07
closure_id: cl-s07-projection
test_id: tc-s07-001
repair_source_head: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
historical_review_verdict: FAIL
historical_review_p0: 0
historical_review_p1: 4
historical_finding_ids:
  - RT-354-S07-001
  - RT-354-S07-002
  - RT-354-S07-003
  - RT-354-S07-004
provider_changed_files:
generated_projection_files:
parent_changed_sections:
  - design.md §6.3
projection_source_preflight:
projection_command:
fresh_install_command:
parity_roots:
parity_file_counts:
parity_tree_sha256:
parity_exclusions: []
validate_result:
diff_check_result:
scope_audit:
  unexpected_changed_files: []
closure_state: pending_fresh_review
next_review_target: exact new pushed repair HEAD, supplied externally
material_decision:
  No material implementation decisions beyond the approved plan.
authority_boundary:
  no Candidate generation
  no canonical adoption
  no assurance promotion
  no PR
  no merge
  no Issue close
```

## model evidence limitation

本ブリーフは`GPT-5.6 Luna`または`Reasoning Effort Max`での実測成功を主張しない。Wrapperが確認した場合だけ、次をcontent-free evidenceとして記録する。

```text
requested_model
target_model
resolved_model_label
selection_strategy
verified
reasoning_effort_requested
reasoning_effort_verified
```

Prompt本文、計画上の希望model、過去sessionのmodel evidenceから未観測値を補完しない。

## source limitation / unverified claims

* Literal path `/private/tmp/iss-00354-s07-blue-repair-prompt-20260805.md`自体はこの実行環境から取得できなかった。本ブリーフはGitHub named branchのexact HEAD、添付Fresh Red review、現行Skill／workflow／Parent Design／plan／report／S07 brief／cleanup analysisを根拠に再構成した。
* 本応答ではrepository変更、projection update、fresh init、parity script、validate、commit、push、Fresh Red再レビューを実行していない。
* Fresh Redの四P1以外の新しい欠陥判定やS07 PASS判定は行っていない。

## Fresh Red v2 repair addendum (bounded evidence correction)

Fresh Red v2 reviewed pushed HEAD `51ec44361934991c0ba347eed7e5047c719ec122` and returned FAIL with P0=0/P1=3. This addendum corrects only `RT-354-S07-V2-001` through `003`; it does not change the provider Skill, parent design, runtime, tests, or prior Red bytes.

### Exact parity command actually executed

The following complete command was executed at the source HEAD above. The temporary installed root was removed by the trap, and the command body is recorded without truncation.

```bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
SOURCE_HEAD='51ec44361934991c0ba347eed7e5047c719ec122'
cd "$ROOT"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
PYTHONPATH="$ROOT/src" uv run python - <<'PY'
from pathlib import Path
import spec_dock.cli
root = Path.cwd().resolve()
observed = Path(spec_dock.cli.__file__).resolve()
expected = (root / "src/spec_dock/cli.py").resolve()
if observed != expected:
    raise SystemExit(f"wrong installer source: {observed} != {expected}")
print("provider_installer_source=<current-checkout>/src/spec_dock/cli.py")
PY
INSTALL_TMP="$(mktemp -d /private/tmp/iss-00354-s07-fresh-v3-XXXXXX)"
trap 'rm -rf "$INSTALL_TMP"' EXIT
PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli init "$INSTALL_TMP"
PYTHONPATH="$ROOT/src" uv run python - "$INSTALL_TMP" <<'PY'
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
repo = Path.cwd().resolve()
installed = Path(sys.argv[1]).resolve()
pairs = (("skill_provider_dogfood", repo / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning", repo / ".agents/skills/spec-dock-issue-planning"), ("skill_provider_fresh_installed", repo / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning", installed / ".agents/skills/spec-dock-issue-planning"), ("docs_provider_dogfood", repo / "src/spec_dock/assets/spec_dock/docs", repo / "spec-dock/docs"), ("docs_provider_fresh_installed", repo / "src/spec_dock/assets/spec_dock/docs", installed / "spec-dock/docs"))
def manifest(root: Path) -> dict[str, tuple[int, str]]:
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink(): raise SystemExit(f"unexpected symlink: {root}:{relative}")
        if path.is_dir(): continue
        if not path.is_file(): raise SystemExit(f"unexpected non-file: {root}:{relative}")
        data = path.read_bytes(); result[relative] = (len(data), hashlib.sha256(data).hexdigest())
    return result
for label, source_root, projection_root in pairs:
    source = manifest(source_root); projection = manifest(projection_root)
    if source != projection: raise SystemExit(f"{label}: parity mismatch")
    tree_sha = hashlib.sha256("\n".join(f"{relative}\0{size}\0{digest}" for relative, (size, digest) in sorted(source.items())).encode("utf-8")).hexdigest()
    print(f"{label}: source={source_root} projection={projection_root} files={len(source)}/{len(projection)} tree_sha256={tree_sha} parity_exclusions=[] status=pass")
PY
```

Observed receipts: provider preflight exit 0; fresh `init` exit 0; recursive parity exit 0; Skill file counts 7/7 and tree SHA `2ec1f6b8951ea581a8893e8ee9fc02a14dae9b81194d53661c9a06861c40c05f`; docs file counts 37/37 and tree SHA `821ee25b75ee2db41dd660a40815b533b71e846f46fdbdff9faf653fcc47fb8a`; all comparisons used `parity_exclusions=[]`. The historical update command remained `PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli update "$ROOT"`, exit 1 due host-adapter `meta.json` operation-not-permitted; no remote package replacement was used.

### Historical eight-file scope reconciliation

The `21a2c4c2...` → `51ec4436...` range contains five direct Blue repair paths and three immutable evidence-import paths. Evidence import is not a Blue modification; this eight-path set supersedes the earlier five-path audit only for this historical range.

```text
direct_blue_edit_path_count: 5
evidence_import_path_count: 3
base: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
head: 51ec44361934991c0ba347eed7e5047c719ec122
expected_changed_file_count: 8
observed_changed_file_count: 8
missing_expected_files: []
unexpected_changed_files: []
status: pass
```

The exact audit invocation was `git diff --name-only "$BASE" "$HEAD"` compared with the sorted eight-path set (five direct Blue edits plus the v1 Blue brief and v1 Red canonical/raw evidence imports). Its observed receipt was `direct_blue_edit_path_count=5 evidence_import_path_count=3 expected_changed_file_count=8 observed_changed_file_count=8 missing_expected_files=[] unexpected_changed_files=[] status=pass`; v1 review bytes remain read-only and byte-identical.

### Current-state boundary

The v1 repair commit is pushed and its exact tip was handed to Fresh Red v2. Fresh Red v2 returned FAIL with P1×3, so S07 remains open. The next correction is limited to this addendum, the cleanup artifact, and `report.md`; a new pushed HEAD requires a fresh Red v3 review. No PASS, closure, S08 start, PR, merge, Issue close, or Issue finish is implied.
