---
種別: 実装時観測・ドッグフーディング分析
ID: "iss-00354-s07-projection-cleanup"
対象: "S07 Projection / docs / parent consistency"
作成日: "2026-08-05"
---

# S07 余分な投影生成物の分析と処理

## 観測

S07 の実装前に `spec-dock update` を実行したところ、今回の範囲にないランタイム投影、README、ガイド、ルール文書が大量に変更され、`.agents/skills/spec-dock-issue-planning/resources/*.md` が新規生成された。これらの `resources` は現行 provider source に存在しない。

## 原因

`spec-dock/` と `.agents/` は provider source の生成投影である。今回の更新コマンドは現行ブランチの provider sourceを使う通常の投影ではなく、リモート版パッケージの異なる世代を先に適用したため、過去または別世代の runtime/resource 群が混入した。したがって、生成物の存在だけを理由に S07 の成果物へ採用してはならない。

## 分類と処理

| 分類 | 処理 | 根拠 |
|---|---|---|
| S07 対象 | provider の Issue Planning skill、provider docs、同一内容の installed/dogfood projection、S07 implementation brief | provider source が正本であり、S07 の allowlist に含まれる |
| S07 対象外の tracked projection | HEAD の内容へ限定復元 | runtime/CLI/application/domain/infra の変更は S07 の許可範囲外 |
| provider に存在しない untracked resources | 削除 | 現行 provider source から再生成されず、正本・契約・入力資料ではない |

## 再発防止の境界

- provider 側を先に編集し、projection は同じ内容をコピーまたは既存のローカル生成手順で同期する。
- S07 では `spec-dock/scripts/spec_dock_runtime/**`、無関係な docs、Issue lifecycle state を変更しない。
- リモート package の更新を、current branch の dogfooding 同期の代用にしない。
- projection の正当性は provider／installed／dogfood の byte parity と `spec-dock validate` で確認する。

## 検証結果

- provider skill と installed projection は SHA-256 `f4fd120e30aa5941ddbaa7ab747de60e855c97d3fcc649637a50da24af89a397` で一致。
- S07 対象 docs 4 件も provider と dogfood projection が各々 byte-identical。
- S07 対象外の runtime projection 19 件と untracked resources 4 件を作業ツリーから除去。
- S07 の変更後も旧 `--context-manifest` は Issue Planning の実行契約として残していない（文書中の出現は廃止を説明する注記のみ）。

この分析は S07 の implementation evidence として `report.md` の EAL に登録する。provider source、S07 projection、親 Epic 文言、S07 brief 以外の差分を S07 の成果として採用しない。

## S07 Blue repair parity receipt

```text
repair_source_head: 21a2c4c2bfb6e30a925e64f8bb9508687b128417
provider_source_preflight:
  command: PYTHONPATH="$ROOT/src" uv run python - <<'PY' ...
  observed_module_path: <current-checkout>/src/spec_dock/cli.py
  exit_code: 0
projection_update:
  command: PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli update "$ROOT"
  exit_code: 1
  stop_reason: host-adapter meta.json operation-not-permitted
  policy: no out-of-allowlist projection was adopted; runtime projection extras were restored
fresh_install:
  command: PYTHONPATH="$ROOT/src" uv run python -m spec_dock.cli init <fresh-installed>
  exit_code: 0
recursive_parity:
  - comparison: skill_provider_dogfood
    source_root: src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning
    projection_root: .agents/skills/spec-dock-issue-planning
    file_count: 7
    tree_sha256: 2ec1f6b8951ea581a8893e8ee9fc02a14dae9b81194d53661c9a06861c40c05f
    parity_exclusions: []
    status: pass
  - comparison: skill_provider_fresh_installed
    source_root: src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning
    projection_root: <fresh-installed>/.agents/skills/spec-dock-issue-planning
    file_count: 7
    tree_sha256: 2ec1f6b8951ea581a8893e8ee9fc02a14dae9b81194d53661c9a06861c40c05f
    parity_exclusions: []
    status: pass
  - comparison: docs_provider_dogfood
    source_root: src/spec_dock/assets/spec_dock/docs
    projection_root: spec-dock/docs
    file_count: 37
    tree_sha256: 821ee25b75ee2db41dd660a40815b533b71e846f46fdbdff9faf653fcc47fb8a
    parity_exclusions: []
    status: pass
  - comparison: docs_provider_fresh_installed
    source_root: src/spec_dock/assets/spec_dock/docs
    projection_root: <fresh-installed>/spec-dock/docs
    file_count: 37
    tree_sha256: 821ee25b75ee2db41dd660a40815b533b71e846f46fdbdff9faf653fcc47fb8a
    parity_exclusions: []
    status: pass
validate:
  command: ./spec-dock/scripts/spec-dock validate
  exit_code: 0
diff_check:
  command: git diff --check
  exit_code: 0
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

The failed `update` command is retained as an execution boundary observation. It
must not be replaced by a remote package update or used to justify importing
runtime projection changes. The fresh `init` and all four recursive parity
comparisons used the current checkout's provider source and completed without
exclusions.

## Exact parity invocation and scope reconciliation

The parity receipt above was produced by this complete command at source HEAD
`51ec44361934991c0ba347eed7e5047c719ec122`; it is repeated here so the receipt
does not depend on a truncated prompt or an unavailable temporary script.

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

The command exited 0 for provider preflight, fresh `init`, and recursive parity. The historical update command was separately observed as exit 1 because the host-adapter `meta.json` operation was not permitted; no remote package update was substituted.

The exact historical scope audit was:

```bash
set -euo pipefail
BASE='21a2c4c2bfb6e30a925e64f8bb9508687b128417'
HEAD='51ec44361934991c0ba347eed7e5047c719ec122'
EXPECTED="$(printf '%s\n' \
  '.agents/skills/spec-dock-issue-planning/SKILL.md' \
  'src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md' \
  'spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/design.md' \
  'spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/20260805t-projection-cleanup-analysis.md' \
  'spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md' \
  'spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md' \
  'spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v1-raw.md' \
  'spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/reviews/red-team-review-s07-v1.md' | sort)"
OBSERVED="$(git diff --name-only "$BASE" "$HEAD" | sort)"
test "$OBSERVED" = "$EXPECTED"
printf 'direct_blue_edit_path_count=5 evidence_import_path_count=3 expected_changed_file_count=8 observed_changed_file_count=8 missing_expected_files=[] unexpected_changed_files=[] status=pass\n'
```

The five direct Blue paths are the provider and projected Skill, parent design,
cleanup artifact, and report. The three evidence-import paths are the v1 Blue
brief and the v1 Red canonical/raw copies. Evidence import is read-only and is
not a Blue modification; the complete expected historical changed-file set is
eight paths.
