# S07 Blue repair v2 implementation brief — Fresh Red v2 P1×3 closure

## 1. Identity and repair boundary

| 項目                       | 値                                          |
| ------------------------ | ------------------------------------------ |
| Repository               | `chemitaro/spec-dock`                      |
| Named branch             | `codex/iss-00354-chatgpt-context-contract` |
| Exact repair source HEAD | `51ec44361934991c0ba347eed7e5047c719ec122` |
| Prior repair source      | `21a2c4c2bfb6e30a925e64f8bb9508687b128417` |
| Fresh Red v2 verdict     | `FAIL`                                     |
| Findings                 | P0=0 / P1=3 / P2=0 / P3=0                  |
| Repair findings          | `RT-354-S07-V2-001`〜`003`のみ                |
| Default-branch fallback  | 未使用・禁止                                     |
| S07 closure              | pending                                    |
| S08                      | 開始禁止                                       |

GitHub Connectorでnamed branchを直接確認し、tipは指定HEAD `51ec44361934991c0ba347eed7e5047c719ec122`とidenticalだった。`21a2c4c2... → 51ec4436...`は1 commit、8 changed filesである。Fresh Red v2はこのexact HEADをreviewし、三件のP1だけを報告している。

Provider Skillとroot `.agents` projectionは現HEADで同じGit blob SHA `69b0a87c5fa23e78bbe776f75d61f154b222bf87`である。この二ファイルは今回read-onlyとし、byte-identicalのまま維持する。

## 2. Exact allowed paths

### 2.1 今回のBlue correctionで変更してよい三ファイル

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  artifacts/20260805t-projection-cleanup-analysis.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00354-define-chatgpt-context-and-attachment-contract/
  report.md
```

`v1` briefは既存本文を書き換えず、Fresh Red v2用のscope reconciliation addendumを末尾へ追記する。

### 2.2 今回変更してはならないファイル

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
.agents/skills/spec-dock-issue-planning/SKILL.md

spec-dock/.../epic-00331-planning-and-advisory-review/design.md
spec-dock/.../epic-00331-planning-and-advisory-review/requirement.md
spec-dock/.../epic-00331-planning-and-advisory-review/plan.md

iss-00354/requirement.md
iss-00354/design.md
iss-00354/plan.md

src/spec_dock/assets/spec_dock/scripts/**
spec-dock/scripts/spec_dock_runtime/**
tests/**
unrelated docs/**
```

次のRed出力もimmutable read-onlyであり、本文・空白・改行を変更しない。

```text
reviews/red-team-review-s07-v1.md
reviews/red-team-review-s07-v1-raw.md
```

両v1 review fileは現HEADで同一Git blob SHA `58ebacdd03c522a385dda9589718366d91602306`である。

Fresh Red v2のcanonical／raw出力をrepositoryへ保存する場合は、今回の三ファイル修正とは分離した**evidence import**としてbyte-identicalにコピーする。今回添付されたcanonical／raw v2 bytesは双方ともSHA-256 `fa0b73b6439e8ecaed0c9a0aefd4cb9837a855662a5cee7c1d2117e27d1cc40a`である。Blue modificationとして扱わない。 

## 3. `RT-354-S07-V2-001` — exact recursive parity receipt

現行cleanup artifactはprovider preflightを`<<'PY' ...`と省略し、fresh-installedの二rootを同じ`<fresh-installed>`へ潰し、recursive parity invocation／exit codeを記録していない。

### 3.1 Historical update boundaryを保持する

次は既に観測済みのhistorical commandとして、そのまま記録する。証跡改善のためにremote package updateへ置換しない。

```bash
PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli update "$ROOT"
```

```text
exit_code: 1
stop_reason: host-adapter meta.json operation-not-permitted
policy:
  remote package updateへ置換しない
  S07対象外projectionを採用しない
  runtime projection extrasは復元済み
```

このexit 1を成功へ書き換えず、今回の修正だけのために別世代packageを実行しない。

### 3.2 Provider preflight、fresh init、recursive parityを完全なcommandで再実行する

cleanup artifactへ、次の**省略なしの実行command全体**と各exit codeを保存する。temporary rootの実pathは保存せず、結果では`<fresh-installed>`へ正規化する。

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
    raise SystemExit(
        f"wrong installer source: observed={observed}, expected={expected}"
    )

print("provider_installer_source=<current-checkout>/src/spec_dock/cli.py")
PY

INSTALL_TMP="$(mktemp -d)"
trap 'rm -rf "$INSTALL_TMP"' EXIT

PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli init "$INSTALL_TMP"

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

    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise SystemExit(f"unexpected symlink: {root}:{relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise SystemExit(f"unexpected non-file: {root}:{relative}")
        files[relative] = path.read_bytes()
    return files


def tree_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, data in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def display_root(path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        relative = path.relative_to(installed).as_posix()
        return f"<fresh-installed>/{relative}"


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
                    "source_root": display_root(source_root),
                    "projection_root": display_root(projection_root),
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
                "source_root": display_root(source_root),
                "projection_root": display_root(projection_root),
                "source_file_count": len(source),
                "projection_file_count": len(projection),
                "tree_sha256": source_digest,
                "parity_exclusions": [],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
PY
```

### 3.3 Expected parity receipt

```text
provider_source_preflight:
  exact_command_recorded: true
  observed_module_path: <current-checkout>/src/spec_dock/cli.py
  exit_code: 0

projection_update:
  exact_command: PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli update "$ROOT"
  exit_code: 1
  historical_observation: true
  remote_replacement_used: false

fresh_install:
  exact_command_recorded: true
  operand: "$INSTALL_TMP"
  exit_code: 0

recursive_parity:
  exact_command_and_complete_heredoc_recorded: true
  exit_code: 0
  parity_exclusions: []
```

| comparison                       | source root                                                                 | projection root                                             |   count | tree SHA-256                                                       |
| -------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------- | ------: | ------------------------------------------------------------------ |
| `skill_provider_dogfood`         | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning` | `.agents/skills/spec-dock-issue-planning`                   |   7 / 7 | `2ec1f6b8951ea581a8893e8ee9fc02a14dae9b81194d53661c9a06861c40c05f` |
| `skill_provider_fresh_installed` | provider skill root                                                         | `<fresh-installed>/.agents/skills/spec-dock-issue-planning` |   7 / 7 | `2ec1f6b8951ea581a8893e8ee9fc02a14dae9b81194d53661c9a06861c40c05f` |
| `docs_provider_dogfood`          | `src/spec_dock/assets/spec_dock/docs`                                       | `spec-dock/docs`                                            | 37 / 37 | `821ee25b75ee2db41dd660a40815b533b71e846f46fdbdff9faf653fcc47fb8a` |
| `docs_provider_fresh_installed`  | provider docs root                                                          | `<fresh-installed>/spec-dock/docs`                          | 37 / 37 | `821ee25b75ee2db41dd660a40815b533b71e846f46fdbdff9faf653fcc47fb8a` |

値が異なる場合は既存値を保持してPASSとせず、停止する。

## 4. `RT-354-S07-V2-002` — historical eight-file scope reconciliation

### 4.1 v1 briefへappend-only addendumを追加する

`artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md`末尾に、次の区分を追加する。元のallowlist本文は削除せず、historical commit auditについて本addendumが優先すると明記する。

#### Direct Blue repair change paths — 5

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
.agents/skills/spec-dock-issue-planning/SKILL.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/design.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/20260805t-projection-cleanup-analysis.md
```

#### Immutable evidence-import paths — 3

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v1.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v1-raw.md
```

次の文をexact meaningとして置く。

> The `21a2c4c2... → 51ec4436...` historical repair commit contains five Blue repair change paths and three immutable evidence-import paths. Evidence import is not a Blue modification. The complete expected historical changed-file set therefore contains eight paths. The earlier five-path scope audit is superseded only for this historical commit-range audit.

### 4.2 Historical scope auditを実行する

```bash
set -euo pipefail

BASE='21a2c4c2bfb6e30a925e64f8bb9508687b128417'
HEAD='51ec44361934991c0ba347eed7e5047c719ec122'

uv run python - "$BASE" "$HEAD" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys

base, head = sys.argv[1:3]

direct_blue_edit_paths = (
    ".agents/skills/spec-dock-issue-planning/SKILL.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/design.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/20260805t-projection-cleanup-analysis.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md",
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md",
)

evidence_import_paths = (
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v1-raw.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v1.md",
)

expected = set(direct_blue_edit_paths) | set(evidence_import_paths)
observed = set(
    subprocess.check_output(
        ["git", "diff", "--name-only", base, head],
        text=True,
        encoding="utf-8",
    ).splitlines()
)

receipt = {
    "base": base,
    "head": head,
    "direct_blue_edit_paths": sorted(direct_blue_edit_paths),
    "evidence_import_paths": sorted(evidence_import_paths),
    "expected_changed_file_count": len(expected),
    "observed_changed_file_count": len(observed),
    "missing_expected_files": sorted(expected - observed),
    "unexpected_changed_files": sorted(observed - expected),
    "status": "pass" if observed == expected else "failed",
}

print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))

if observed != expected:
    raise SystemExit(1)
PY
```

### 4.3 Scope receiptを二箇所へ記録する

cleanup artifactと`report.md`の両方に、次をcontent-freeで記録する。

```text
historical_scope_audit:
  base: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
  head: 51ec44361934991c0ba347eed7e5047c719ec122
  direct_blue_edit_path_count: 5
  evidence_import_path_count: 3
  expected_changed_file_count: 8
  observed_changed_file_count: 8
  missing_expected_files: []
  unexpected_changed_files: []
  status: pass
```

Red v1／v2出力の内容を修正してこのscopeを成立させてはならない。

## 5. `RT-354-S07-V2-003` — report current-state correction

現行reportには、`new repair HEAD will be supplied after commit/push`、`commit/push is the next identity boundary`、`repair commit/push and v2 are pending`、`has not yet been committed/pushed`など、既にpush／v2 review済みの状態と矛盾する表現が残る。

### 5.1 EAL-045のnext actionを過去時制へ直す

現行の「repairをcommit/pushし、Fresh Red v2へ渡す」を、次へ置換する。

> The v1 repair was committed and pushed, and its exact tip was handed to Fresh Red v2. Fresh Red v2 returned FAIL with P1×3; see EAL-046. S07 remains pending bounded evidence correction and a fresh v3 review.

### 5.2 EAL-046を追加する

```text
ID: EAL-046
adoption_status: adopted
source: S07 Fresh Red Team Review v2
source_role: chatgpt-use-red-team-docs
claim:
  exact pushed HEAD 51ec44361934991c0ba347eed7e5047c719ec122
  was reviewed in a new read-only thread and returned
  FAIL / P0=0 / P1=3 / P2=0 / P3=0
findings:
  - RT-354-S07-V2-001
  - RT-354-S07-V2-002
  - RT-354-S07-V2-003
target_artifact:
  - report.md
  - artifacts/20260805t-projection-cleanup-analysis.md
  - artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md
evidence_strength: fresh_fail
evidence_sha256: fa0b73b6439e8ecaed0c9a0aefd4cb9837a855662a5cee7c1d2117e27d1cc40a
blocking:
  Issue history: no
  S07 closure: yes
  S08 start: yes
next_action:
  exact command receipt、historical eight-file scope receipt、
  pushed-state wordingを修正し、新しいpushed HEADをfresh Red v3へ渡す
```

Fresh Red v2は、Skill／parent §6.3／operation別option contract／runtime非変更を正として確認しているため、それらを再修正しない。

### 5.3 全S07 current-state rowを同じ状態へ揃える

少なくとも次を修正する。

* TDD / implementation observation
* Discovered Tests
* Step Contract Closure
* Test Contract Closure
* Closure Coverage
* Implementation Delegation Gate
* Delegated Worker Evidence
* Reviewer Gate Status
* Milestone / Commit Candidate Gate
* S07 narrative section
* S90 docs-impact row
* Final Code Review Gate
* Final Spec Review Gate
* Final Commit

すべて次の意味へ統一する。

> The S07 v1 repair commit was pushed, and its exact tip was handed to Fresh Red v2. Fresh Red v2 reviewed exact HEAD `51ec44361934991c0ba347eed7e5047c719ec122` and returned FAIL with P0=0 / P1=3 / P2=0 / P3=0. S07 remains open. The three evidence defects are under bounded correction, and a new pushed HEAD requires a fresh Red v3 review. S08, PR, merge, Issue close, and Issue finish remain prohibited.

将来作る修正commitのSHAを同じcommit内のreportへ書かない。`51ec4436...`はexternal Fresh Red v2 artifactで確定済みのhistorical review identityなので記載してよい。

### 5.4 Stale wording zero-match

```bash
REPORT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md'

if rg -n \
  'new repair HEAD will be supplied after commit/push|commit/push is the next identity boundary|repair commit/push and v2 are pending|has not yet been committed/pushed|commit/push after scope and validation checks|v2 not yet run|repair commit/push and fresh Red v2 remain|repairをcommit/pushし、Fresh Red v2へ渡す' \
  "$REPORT"
then
  echo 'stale S07 pushed-state wording remains' >&2
  exit 1
fi
```

## 6. Verification commands

### Identity

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='51ec44361934991c0ba347eed7e5047c719ec122'

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"
```

### Current repair diff allowlist

```bash
SOURCE_HEAD='51ec44361934991c0ba347eed7e5047c719ec122'

uv run python - "$SOURCE_HEAD" <<'PY'
from __future__ import annotations

import subprocess
import sys

base = sys.argv[1]

allowed = {
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/20260805t-projection-cleanup-analysis.md",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md",
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

print("current repair scope: pass")
PY
```

### Read-only boundaries

```bash
git diff --exit-code "$SOURCE_HEAD" -- \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  .agents/skills/spec-dock-issue-planning/SKILL.md \
  src/spec_dock/assets/spec_dock/scripts \
  spec-dock/scripts/spec_dock_runtime \
  tests \
  spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/requirement.md \
  spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/design.md \
  spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/plan.md \
  "$ISSUE_ROOT/requirement.md" \
  "$ISSUE_ROOT/design.md" \
  "$ISSUE_ROOT/plan.md" \
  "$ISSUE_ROOT/reviews/red-team-review-s07-v1.md" \
  "$ISSUE_ROOT/reviews/red-team-review-s07-v1-raw.md"

cmp \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  .agents/skills/spec-dock-issue-planning/SKILL.md
```

### Final gates

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

## 7. Expected final receipt

```text
source_head: 51ec44361934991c0ba347eed7e5047c719ec122

fresh_red_v2:
  verdict: FAIL
  p0: 0
  p1: 3
  p2: 0
  p3: 0
  closure_claimed: false

historical_scope_audit:
  direct_blue_edit_paths: 5
  evidence_import_paths: 3
  expected_changed_files: 8
  observed_changed_files: 8
  missing_expected_files: []
  unexpected_changed_files: []
  status: pass

parity:
  comparisons: 4
  parity_exclusions: []
  skill_files: 7
  docs_files: 37
  result: pass

current_repair_scope:
  modified_paths: 3
  unexpected_changed_files: []

provider_dogfood_skill:
  byte_identical: true

s07:
  closure: pending
  next_review: fresh Red v3 on exact new pushed HEAD
  s08_start: prohibited
  pass_claimed: false
```

## 8. Stop conditions

次のいずれかで停止し、allowlistを拡張しない。

* named branch tipが`51ec44361934991c0ba347eed7e5047c719ec122`から変わった。
* historical update command／exit 1をexactに特定できず、推測で補完する必要がある。
* provider preflightがcurrent checkoutの`src/spec_dock/cli.py`を解決しない。
* fresh initまたは四組parityがexit 0にならない。
* countまたはtree SHAが既存観測値と異なる。
* parityを通すために除外、allowlist、missing-file waiverが必要になる。
* historical eight-file auditでmissing／unexpected fileが出る。
* current correctionが三ファイルを超える。
* Provider Skill、`.agents` projection、parent design、runtime、CLI、tests、canonical requirement/design/planへ差分が出る。
* v1／v2 Red outputを修正する必要が生じる。
* reportがFresh Red v2をPASSまたはS07 closureとして扱う。
* S08、Candidate ZIP、PR、merge、Issue close、Issue finishを開始する必要が生じる。

## 9. Model evidence

本ブリーフは`GPT-5.6 Luna`または`Reasoning Effort Max`での実測成功を主張しない。Fresh Red v2添付本文にも、Luna／Maxをverifiedとするwrapper evidenceは含まれていない。

記録してよいのはwrapperが実際に返した次のfieldだけである。

```text
requested_model
target_model
resolved_model_label
selection_strategy
verified
reasoning_effort_requested
reasoning_effort_verified
```

未提示fieldは`not_observed`とし、Prompt本文、過去session、model名の推測から補完しない。
