## identity/source HEAD

* Repository: `chemitaro/spec-dock`
* Named branch: `codex/iss-00354-chatgpt-context-contract`
* GitHub Connectorでnamed branchを直接解決したcurrent tip: `68afc5bb009256231976877475d4038f3e95b728`
* Default branch fallback: 未使用・禁止
* S06 exact reviewed HEAD: `b832456e84861d7e60b7f43daa490227e03d25f7`
* Current tip `68afc5bb...` は、S06 v5 PASS後のraw review／brief証跡4ファイルだけを追加したevidence-only commitであり、commit message上も`report.md`を変更していない。
* S06 v5は`b832456e...`をexact HEADとしてfresh Red Teamがread-onlyで確認し、`PASS / P0=0 / P1=0 / P2=0`としている。ただしfocused pytest、Ruff、mypy、validate、live Oracle/browserは同レビュー内では未実行・未確認である。S07ではこのreviewとS06 artifactsをread-only入力として扱い、再判定・修正しない。
* 本ブリーフ作成中のConnector初回確認と最終再確認は、いずれも`68afc5bb...`だった。別系統の「プロンプト送信直前HEAD receipt」は提示入力に含まれていないため、そのreceiptとの一致だけは独立検証不能である。実装開始時にorchestratorが保持するpre-prompt receiptが`68afc5bb...`と一致しなければ停止する。
* 添付bundleはcanonical requirement/design/plan等の補助入力としてのみ参照し、repository authorityの代替にしない。

## observed current files

1. `plan.md`のS07カードは、provider-first更新、既存projection mechanismによるinstalled/dogfood再生成、固定allowlistを使わないrecursive byte parity、skills/docsとparent Epicの限定整合だけを要求している。

2. Provider正本のIssue Planning skillは次である。

   ```text
   src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
   ```

   現行`Operating Spine`には、S05で廃止済みのexternal JSON `--context-manifest`例が残っている。root dogfood projectionの`.agents/skills/spec-dock-issue-planning/SKILL.md`も同一内容であり、現在はbyte parityを保ったままsemantically staleである。

3. Read-only runtime contractは、create／review／reviseにrepeatableな`--provided-context-path PATH`を提供し、各値をopaque `Path`としてrequestへ渡す。`planning apply`にはこのoptionを追加していない。

4. Provider operation resourcesは現時点で次の契約を既に表しているため、S07ではread-only確認対象とする。

   * Planning: provider-owned詳細指示、exactly-one authoring ZIP、repository mutation禁止。
   * Review: fresh、read-only、defect-only、closed JSON。
   * Revision: Blue Teamによるcomplete replacement、selected P0/P1だけを修正。
   * raw transcript、session handle、private URL等をformal outputへ出さない。

5. `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`はPATH Oracle、exact branch、fresh Review、Human gate、strict outputを既に記載している一方、S05後のdirectory-oriented input、minimal body＋provider instruction resources、Blue continuity／fresh Red、normal failure boundaryを十分に説明していない。

6. `workflow_chatgpt_authoring_pack.md`、`authoring/chatgpt-pack.md`、`reference_authoring_pack_backend.md`は汎用authoring-pack evidence laneを説明しており、prompt packやconfigurable backend commandを扱う。これをIssue Planning formal routeのfallbackと誤読させない、短いscope注記が必要である。汎用lane自体の挙動は変更しない。

7. Parent Epicには、Issue Planningの現行契約と衝突する次の旧表現が残る。

   * role／output／fallback instructionをすべてprompt本文へ置き、instruction attachmentを一律禁止する表現。
   * timeout／disconnectをsubmission前後で分けず、常にsame-session harvestとして読むことのできる表現。
   * `E1-REQ-032`／`E1-AC-027`のbody・attachment境界。
   * `E1-REQ-034`／`E1-AC-029`のsession recovery境界。
   * Parent designの§4、§6.3、§6.5、§9、§10、§11にも同じ旧境界がある。

8. Projectionの生成正本は次の二treeである。

   ```text
   skill source:
     src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/

   docs source:
     src/spec_dock/assets/spec_dock/docs/
   ```

   Installerの`update`はprovider assetsからmanaged docsとmanaged skillsをroot projectionへ同期する。root `.agents/**`および`spec-dock/docs/**`は生成先でありauthoring sourceではない。

## minimal changed-file allowlist

### Provider正本として直接編集してよいファイル

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md

src/spec_dock/assets/spec_dock/docs/workflow_issue.md
src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md
src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md
src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/requirement.md

spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/design.md
```

### 既存update機構だけで生成してよいprojection

```text
.agents/skills/spec-dock-issue-planning/SKILL.md

spec-dock/docs/workflow_issue.md
spec-dock/docs/workflow_chatgpt_authoring_pack.md
spec-dock/docs/authoring/chatgpt-pack.md
spec-dock/docs/reference_authoring_pack_backend.md
```

Projection側は手編集しない。更新後のdiffがこの生成集合を超えた場合、生成物を個別修正せず停止する。

### Read-only入力

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/**
src/spec_dock/assets/spec_dock/scripts/**
spec-dock/scripts/**
tests/**
iss-00354/requirement.md
iss-00354/design.md
iss-00354/plan.md
iss-00354/report.md
iss-00354/artifacts/**/s06-*
iss-00354/reviews/red-team-review-s06-*
parent Epic plan.md
```

## forbidden changes

* Runtime、CLI、application、domain、infra、tests、fixture、output validatorの変更。
* `--provided-context-path`のparser／request contract変更、別option追加、旧`--context-manifest`互換復活。
* Provider operation resource inventoryの変更。現行resourceに具体的矛盾を発見した場合は、allowlistを広げず停止する。
* Root `.agents/**`または`spec-dock/docs/**`の手編集。
* Projection parity用のfile allowlist、除外pattern、例外path、内容別skipの追加。
* 別Issueのcanonical requirement/design/plan/report、Candidate、review artifactの変更。
* iss-00354のcanonical requirement/design/plan/reportへの書込み。S07 evidenceはworker outputとしてorchestratorへ返す。
* Parent Epicの状態、frontmatter authority、Issue Boundary Map、Issue順序、依存、scope allocation、lifecycle、acceptance IDの追加・削除。
* Parent EpicのRequirement／Design全体の再設計。変更はbody／attachment／sessionの矛盾箇所だけに限定する。
* Option A／C、opaque directory input、Blue continuity、fresh Red、direct PATH Oracle、normal failure、typed output safetyの弱体化。
* Directory entryのwalk、glob、stat、read、hash、copy、archive、filter、manifest化を推奨する文言。
* Personal wrapper、arbitrary backend、API、default branch、alternate model、attachment drop、automatic ZIPをIssue Planning fallbackとして案内する文言。
* Candidate／Review PASSだけをcanonical adoption、execution-ready、PR-ready、merge-ready、Issue finishとする表現。
* Parent EpicやdocsへOracle `0.17.0`のIssue-local implementation detailを展開すること。
* S06 v5 PASSの再判定、S06 artifact修正、S06 reviewed HEADをcurrent source HEADとして偽装すること。

## implementation sequence

1. **Identity gate**

   Named branch、local HEAD、remote named-branch tip、orchestratorのpre-prompt receiptがすべて`68afc5bb...`で一致することを確認する。S06 reviewed HEAD `b832456e...`はread-only ancestry inputとして記録し、current sourceには使わない。

2. **Provider skillを現行CLIへ同期**

   `SKILL.md`のexternal JSON context-manifest説明と例を削除し、次へ置換する。

   ```bash
   ./spec-dock/scripts/spec-dock-chatgpt planning create \
     --issue <iss-id> --output <external-output-dir> \
     --provided-context-path <file-or-directory> \
     --provided-context-path <another-file-or-directory>
   ```

   同optionを`review planning`とsemantic `planning revise`でも必要時にrepeatable指定できること、`planning apply`には渡さないことを明記する。

   あわせて短く固定する。

   * Minimal bodyはoperation、目的、exact repository／branch／HEAD、authority、expected output、hard failureを保持する。
   * 詳細手順はprovider-owned operation resourcesが保持する。
   * Static attachment directoryとdynamic evidenceはoriginal top-level pathのままdirect Oracleへ渡す。
   * File／directory内部をinspect、copy、ZIP、filter、manifest化しない。
   * Planning／semantic revisionはsuccessful submissionに結び付いたverified Blueを継続し、ReviewはCandidateごとのfresh Redである。
   * Pre-submit failureはsuccessful turnではない。Post-submit failureはsame-session recoveryだけとし、別responseを自動生成しない。
   * Normal failureではrequired attachment、model、backend、branch、output validatorを黙示変更しない。

3. **Provider docsのIssue Planning境界を同期**

   `workflow_issue.md`に上記契約をIssue Planning節の一箇所へ集約する。長い重複説明は作らない。

   汎用authoring-pack三文書には、次のscope注記だけを加える。

   > `authoring pack`／configurable backend commandは汎用evidence laneであり、formal Issue Planning transportのfallbackではない。Issue Planningは`spec-dock-issue-planning`と`workflow_issue.md`が所有し、minimal body、provider-owned operation instruction resources、opaque original paths、PATH-resolved direct Oracle、Blue continuity／fresh Red、既存output validatorsに従う。

   汎用authoring-pack command、backend resolution、preservation checkpoint、Initiative／Epic用途は変更しない。

4. **Parent Epicの限定修正**

   Parent `requirement.md`では次の既存行だけを意味保存で補正する。

   * `E1-REQ-032`／`E1-AC-027`: Issue Planningについて、旧「全instructionをbody／attachmentはreference-only」から「minimal authoritative body＋provider-owned operation instruction resources＋opaque reference/original paths」へ限定修正する。Attachmentはcanonical docsやbodyをoverrideしない。
   * `E1-REQ-034`／`E1-AC-029`: pre-submit failureとpost-submit failureを分離する。pre-submitはsuccessful submissionではなく、Issue-local bounded decisionだけがnew executionを許可する。`promptSubmitted=true`後はsame-session recoveryのみで、duplicate successful submissionを禁止する。

   Parent `design.md`では、同じ意味の矛盾だけを§4、§6.3、§6.5、§9、§10、§11で同期する。新しいstate machine、profile、failure taxonomy、Oracle flagは追加しない。

   Parent `plan.md`、Issue Boundary Map、frontmatter lifecycle stateは変更しない。

5. **Projection再生成**

   Provider正本の編集完了後に一度だけ既存installer updateを実行する。生成先を先に編集したり、update後にprojectionだけを修正したりしない。

6. **Recursive parityとdocs-only gate**

   Provider／dogfood／fresh installed treeの全relative file setと全file bytesを比較する。個別file allowlistや除外は使わない。

7. **Evidence handoff**

   Workerは`report.md`を編集せず、下記evidence fieldsをorchestratorへ返す。Fresh spec-reviewer／qa-reviewer判定やcommit／pushは別ゲートとする。

## exact verification commands

```bash
set -euo pipefail

BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE_HEAD='68afc5bb009256231976877475d4038f3e95b728'
S06_REVIEWED_HEAD='b832456e84861d7e60b7f43daa490227e03d25f7'

test "$(git branch --show-current)" = "$BRANCH"

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}"

test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"
git merge-base --is-ancestor "$S06_REVIEWED_HEAD" "$SOURCE_HEAD"

# Orchestratorが別途保持するpre-prompt receiptを代入する。
# 提示されない場合はこのgateを未検証のまま通過させない。
PRE_PROMPT_HEAD='<orchestrator-pre-prompt-head>'
test "$PRE_PROMPT_HEAD" = "$SOURCE_HEAD"
```

Provider編集後、projectionを再生成する。

```bash
uv run python -m spec_dock.cli update .
```

Fresh installed projectionを作る。

```bash
INSTALL_TMP="$(mktemp -d)"
trap 'rm -rf "$INSTALL_TMP"' EXIT

uv run python -m spec_dock.cli init "$INSTALL_TMP"
```

個別file allowlistなしでrecursive byte parityを検証する。

```bash
uv run python - "$INSTALL_TMP" <<'PY'
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

repo = Path.cwd()
installed = Path(sys.argv[1])

pairs = (
    (
        "skill provider/dogfood",
        repo / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning",
        repo / ".agents/skills/spec-dock-issue-planning",
    ),
    (
        "skill provider/installed",
        repo / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning",
        installed / ".agents/skills/spec-dock-issue-planning",
    ),
    (
        "docs provider/dogfood",
        repo / "src/spec_dock/assets/spec_dock/docs",
        repo / "spec-dock/docs",
    ),
    (
        "docs provider/installed",
        repo / "src/spec_dock/assets/spec_dock/docs",
        installed / "spec-dock/docs",
    ),
)

def manifest(root: Path) -> dict[str, tuple[int, str]]:
    if not root.is_dir():
        raise SystemExit(f"missing parity root: {root}")
    result: dict[str, tuple[int, str]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise SystemExit(f"unexpected symlink in parity closure: {root}:{rel}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise SystemExit(f"unexpected non-file in parity closure: {root}:{rel}")
        data = path.read_bytes()
        result[rel] = (len(data), hashlib.sha256(data).hexdigest())
    return result

for label, source, projection in pairs:
    source_manifest = manifest(source)
    projection_manifest = manifest(projection)
    if source_manifest != projection_manifest:
        source_files = set(source_manifest)
        projection_files = set(projection_manifest)
        missing = sorted(source_files - projection_files)
        extra = sorted(projection_files - source_files)
        changed = sorted(
            path
            for path in source_files & projection_files
            if source_manifest[path] != projection_manifest[path]
        )
        raise SystemExit(
            f"{label}: parity failed; "
            f"missing={missing}, extra={extra}, changed={changed}"
        )
    tree_digest = hashlib.sha256(
        "\n".join(
            f"{path}\0{size}\0{digest}"
            for path, (size, digest) in sorted(source_manifest.items())
        ).encode("utf-8")
    ).hexdigest()
    print(
        f"{label}: pass files={len(source_manifest)} "
        f"tree_sha256={tree_digest}"
    )
PY
```

Legacy input contractがactive skillへ残っていないことを検証する。

```bash
if rg -n -- \
  '--context-manifest|external JSON[[:space:]]+context manifest' \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  .agents/skills/spec-dock-issue-planning/SKILL.md
then
  echo 'legacy context-manifest wording remains' >&2
  exit 1
fi

rg -n -- '--provided-context-path' \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  .agents/skills/spec-dock-issue-planning/SKILL.md
```

Runtime、current Issue canonical docs、S06 evidence、parent planが不変であることを検証する。

```bash
ISSUE_ROOT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract'
PARENT_ROOT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review'

git diff --exit-code "$SOURCE_HEAD" -- \
  src/spec_dock/assets/spec_dock/scripts \
  tests \
  "$ISSUE_ROOT/requirement.md" \
  "$ISSUE_ROOT/design.md" \
  "$ISSUE_ROOT/plan.md" \
  "$ISSUE_ROOT/report.md" \
  "$ISSUE_ROOT/artifacts" \
  "$ISSUE_ROOT/reviews" \
  "$PARENT_ROOT/plan.md"
```

Parent lifecycle identityとRequirement／AC ID集合が不変であることを検証する。

```bash
uv run python - "$SOURCE_HEAD" <<'PY'
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

base = sys.argv[1]
files = (
    Path(
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/requirement.md"
    ),
    Path(
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/design.md"
    ),
)

def original(path: Path) -> str:
    return subprocess.check_output(
        ["git", "show", f"{base}:{path.as_posix()}"],
        text=True,
        encoding="utf-8",
    )

def frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", text)
    if match is None:
        raise SystemExit(f"missing frontmatter key: {key}")
    return match.group(1).strip()

for path in files:
    before = original(path)
    after = path.read_text(encoding="utf-8")
    for key in ("ID", "状態", "親", "candidate_semantic_key", "canonical_path"):
        if frontmatter_value(before, key) != frontmatter_value(after, key):
            raise SystemExit(f"{path}: forbidden frontmatter change: {key}")

requirement = files[0]
before = original(requirement)
after = requirement.read_text(encoding="utf-8")
for pattern in (r"\bE1-REQ-\d{3}\b", r"\bE1-AC-\d{3}\b"):
    if set(re.findall(pattern, before)) != set(re.findall(pattern, after)):
        raise SystemExit(f"{requirement}: requirement/AC ID set changed")

print("parent identity and ID-set checks: pass")
PY
```

Changed-file scopeを検証する。

```bash
uv run python - "$SOURCE_HEAD" <<'PY'
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

base = sys.argv[1]

allowed = {
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md",
    "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
    "src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md",
    "src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md",
    "src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md",
    ".agents/skills/spec-dock-issue-planning/SKILL.md",
    "spec-dock/docs/workflow_issue.md",
    "spec-dock/docs/workflow_chatgpt_authoring_pack.md",
    "spec-dock/docs/authoring/chatgpt-pack.md",
    "spec-dock/docs/reference_authoring_pack_backend.md",
    (
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/requirement.md"
    ),
    (
        "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/design.md"
    ),
}

tracked = set(
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
unexpected = sorted((tracked | untracked) - allowed)
if unexpected:
    raise SystemExit(f"out-of-allowlist changes: {unexpected}")

print("changed-file allowlist: pass")
PY
```

最終docs-only gateを実行する。

```bash
./spec-dock/scripts/spec-dock validate
git diff --check

git diff --stat "$SOURCE_HEAD"
git diff -- "$PARENT_ROOT/requirement.md" "$PARENT_ROOT/design.md"
```

## parity and parent-wording acceptance criteria

### Projection parity

* Provider skill tree、dogfood skill tree、fresh installed skill treeのrelative file set、size、SHA-256が完全一致する。
* Provider docs tree、dogfood docs tree、fresh installed docs treeのrelative file set、size、SHA-256が完全一致する。
* Comparisonはtree全体をrecursiveに列挙し、個別file allowlist、除外、glob skip、content-based exceptionを使わない。
* Generated projectionの正本は`src/spec_dock/assets/install_root/**`および`src/spec_dock/assets/spec_dock/docs/**`だけである。
* Root `.agents/**`と`spec-dock/docs/**`にproviderに存在しない追加file、欠落file、byte差分がない。
* Projection更新は`uv run python -m spec_dock.cli update .`の一回だけで成立する。

### Skill／docs contract

* `--context-manifest`とexternal JSON context-manifestのactive guidanceがゼロになる。
* `--provided-context-path PATH`がrepeatableであり、file／directoryをopaque original pathとして扱うことが明記される。
* Option Aのminimal bodyとprovider-owned detailed instruction resourcesが区別される。
* Option Cとしてdirectory treeをinspect、materialize、archive、filterしない。
* Planning／semantic revisionのverified Blue continuityとCandidateごとのfresh Redが区別される。
* Pre-submit failureをsuccessful turnとして扱わず、post-submitをsame-session onlyとする。
* PATH-resolved direct Oracle以外をformal Issue Planning fallbackとして案内しない。
* Normal failure時もrequired attachment、logical model、branch、backend、output validatorを変更しない。
* Existing authoring ZIP／closed JSON／Candidate／Review／Human／apply safetyを緩めない。
* 汎用authoring-pack docsの既存用途を削除せず、Issue Planningとのscope境界だけを追記する。

### Parent wording

* Parent `E1-REQ-032`／`E1-AC-027`はIssue Planningのminimal body、provider instruction resources、opaque reference pathsを許容し、attachmentにcanonical authorityを与えない。
* Parent `E1-REQ-034`／`E1-AC-029`はpre-submitとpost-submitを分離し、post-submitだけをsame-session recoveryとする。
* Parent designの対応節が同じ意味になる。
* Parent requirement／AC ID集合、frontmatter state、Issue Boundary Map、plan、dependency、lifecycleは不変。
* Oracle 0.17 profile、specific flags、stage reason table等のIssue-local詳細をParentへコピーしない。
* Parent変更はbody／attachment／session wording以外を含まない。

## stop conditions

次のいずれかでS07実装を停止し、allowlistを拡張しない。

* Named branch、local HEAD、remote tip、pre-prompt receiptのいずれかが`68afc5bb...`と一致しない。
* S06 reviewed HEADからcurrent tipへのlineageを確認できない。
* S06 v5 reviewまたはS06 artifactsの修正が必要になる。
* Provider resource inventoryやruntime contractの変更が必要になる。
* `--context-manifest`廃止を説明するためにcompatibility parser、migration code、aliasを復活させる必要がある。
* Parent EpicのIssue Boundary Map、要件ID、acceptance ID、状態、依存、plan、lifecycle変更が必要になる。
* 汎用authoring-pack挙動そのものの廃止・再設計が必要になる。
* Projection commandがallowlist外のtracked fileを変更する。
* Recursive parityを通すためにfile除外、許容差分、allowlist追加が必要になる。
* Provider、dogfood、fresh installedのいずれかにmissing／extra／changed fileが残る。
* `spec-dock validate`、scope audit、parent identity check、legacy wording check、`git diff --check`のいずれかが失敗する。
* Option A／C、Blue／Red、direct Oracle、normal failure、output safetyのいずれかと整合する文言を一意に書けない。
* Private path、session handle、raw transcript、target URL、credentialをdocsまたはreport evidenceへ記録する必要が生じる。

## report evidence fields

Workerは次を構造化してorchestratorへ返す。`report.md`への統合はorchestratorが行う。

| Field                            | 必須内容                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------ |
| `step`                           | `S07`                                                                          |
| `closure_id`                     | `cl-s07-projection`                                                            |
| `test_id`                        | `tc-s07-001`                                                                   |
| `source_repository`              | `chemitaro/spec-dock`                                                          |
| `source_branch`                  | `codex/iss-00354-chatgpt-context-contract`                                     |
| `connector_source_head`          | `68afc5bb009256231976877475d4038f3e95b728`                                     |
| `pre_prompt_head`                | orchestrator receiptのfull SHA                                                  |
| `pre_prompt_match`               | `true`のみ許可                                                                     |
| `s06_reviewed_head`              | `b832456e84861d7e60b7f43daa490227e03d25f7`                                     |
| `s06_review_status`              | `PASS / P0=0 / P1=0 / P2=0`, read-only                                         |
| `provider_changed_files`         | 直接編集したprovider正本のexact list                                                    |
| `generated_projection_files`     | updateで生成されたexact list                                                         |
| `parent_changed_sections`        | Requirement ID／Design節ごとの限定一覧                                                  |
| `projection_command`             | exact command、exit code                                                        |
| `parity_roots`                   | skill/docsのprovider↔dogfood、provider↔installed四組                               |
| `parity_file_counts`             | 各treeのrecursive file count                                                     |
| `parity_tree_sha256`             | 各比較組のcontent-free tree digest                                                  |
| `parity_exclusions`              | `[]`                                                                           |
| `legacy_context_manifest_search` | searched paths、zero-match、exit semantics                                       |
| `provided_context_path_presence` | provider／dogfood双方の確認結果                                                        |
| `parent_identity_check`          | frontmatter key／REQ／AC ID-set不変                                                |
| `scope_audit`                    | unexpected changed files `[]`                                                  |
| `validate_result`                | command、exit code、要約                                                           |
| `diff_check_result`              | command、exit code                                                              |
| `docs_only_result`               | runtime/test/current Issue canonical docs/S06 evidence不変                       |
| `material_decision`              | 原則`No material implementation decisions beyond the approved plan.`             |
| `unresolved_risks`               | なし、または停止理由                                                                     |
| `review_required`                | fresh `spec-reviewer`によるdocs/spec alignment、`qa-reviewer`によるrecursive parity確認 |
| `authority_boundary`             | Candidate生成、canonical adoption、assurance promotion、PR、merge、Issue closeを未実施と明記 |

## model evidence limitation

* 本ブリーフは`GPT-5.6 Luna`または`Reasoning Effort Max`で実測成功したとは主張しない。

* 今回のGitHub Connector inspectionはmodel picker／reasoning-effortの実行証跡ではない。

* Wrapper receiptがある場合だけ、次のcontent-free fieldsをそのまま記録する。

  ```text
  requested_model
  target_model
  resolved_model_label
  selection_strategy
  verified
  reasoning_effort_requested
  reasoning_effort_verified
  ```

* Wrapperが確認していない値をChatGPT本文の自己申告、計画上の希望値、過去sessionから補完しない。

* 現在提示された入力には、このS07ブリーフ自体のLuna／Max verified receiptはないため、現時点のmodel evidenceは`not_observed`とする。

* S06 v5 PASSもlive Oracle/browser、concrete provider receipt、実provider continuity／fresh Redの成功証明ではなく、exact HEADの静的契約レビューとしてのみ扱う。
