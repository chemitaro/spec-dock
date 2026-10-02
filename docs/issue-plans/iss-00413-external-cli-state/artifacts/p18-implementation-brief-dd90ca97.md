> 採用時の実行補正は [P-18実装記録](p18-retirement-implementation.md) が正本です。本文のcommit message例を手動指定せず、現行 `git-commit` / 認可規則に従います。

# Issue #413 P-18 実装ブリーフ
## Linux/macOS対応の固定と、Windows専用接続の外科的撤去

| 項目 | 固定値 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| 対象branch | `codex/iss-00413-external-cli-state` |
| 検証済みbase SHA | `dd90ca978fd711c32df7bbdf38aea516f62bbb1c` |
| 選択scope | Issue #413 Plan **P-18のみ** |
| 実装担当 | `gpt-6.1-sol` / reasoning `max` |
| 本ブリーフ著述 | GPT-5.6 Sol / Pro |
| 対応OS | Linux / macOS |
| 非対応OS | Windows |
| 隣接・除外 | P-07 Finish修正、P-13以降、P-16実consumer切替、P-17正式import/Start |
| 本文書の状態 | 実装指示。製品変更、test実行、commit、push、review、FQは未実施 |

GitHub connectorで指定refを直接取得し、`refs/heads/codex/iss-00413-external-cli-state` の先端が期待値 `dd90ca978fd711c32df7bbdf38aea516f62bbb1c` と完全一致することを確認済みである。別branchへのfallbackはしていない。

本ブリーフはRequirement・Design・Planを変更する第二正本ではなく、選択済みstepを実装可能な作業単位へ具体化する実用上の伴走文書である。正本にない要求を追加せず、実在するsource・test・command・停止条件を使う。attachments-bundle

---

## 1. Authorityと判断順序

実装時の判断順序は次のとおりとする。

1. `artifacts/os-support-decision.md`
2. `requirement.md`
3. `design.md`
4. `plan.md#p-18`
5. `artifacts/os-support-retirement-plan.md`
6. 上記base SHAに存在する現行source・test・CI
7. `artifacts/user-decisions.md` / `interview-worktree-start.md` のQ1〜Q8と既存合意
8. 過去のWindows調査、Windows用Implementation Brief、旧review、測定logは履歴・raw evidenceとしてのみ参照

最新決定は、Windows対応を撤回し、Linux/macOSだけを対応OSとする一方、外部CLI、worktreeごとの直接対象一件、同cloneの必要時観測、Start-only排他、Git原文・partial/unknown、GitHub完了、readonly SyncというIssue #413本体を維持するものである。Windowsの代替として別のlock、store、台帳、daemon等を設計してはならない。attachments-bundle

Q1〜Q8で確定済みの、同cloneだけの観測、branch作成・checkoutを含むStart、一worktree一直接対象、GitHub Closeを含むFinish、三階層維持、work release非追加、Finish後branch保持、自動rollbackなしという契約は変更しない。attachments-bundle

---

## 2. P-18の完了像

P-18は次の状態を作る。

- `work-target/v1` の物理identityをPOSIX形だけに固定する。
- root/leaf help、`--version`、3 shell completionをbusiness admissionより先に処理する既存順序を維持する。
- 全business commandを、project・Git・GitHub・consumer fileへ触れる前の一つのOS guardへ通す。
- 非対応platformでは `UNSUPPORTED_PLATFORM`、`effects=[]`、副作用0で停止する。
- Windows専用identity、directory reader、JSON reader、named mutex、WAIT_ABANDONED、NTFS受入、Windows CI jobをcurrent product pathから撤去する。
- Linux/macOSのdescriptor、nofollow、single-link、exact bytes、file/directory `fsync`、no-replace、`flock`、観測済みbasenameだけの遅い解除を維持する。
- Linux/macOSのfocused、full、wheel、外部consoleの候補SHA単位の証拠を残す。
- 正本、reference、HTML、manifest、採用ZIPの現在状態を同期する。
- raw evidenceと過去のWindows履歴は削除・改ざんしない。

P-18計画が定める依存順、削除対象、focused gate、commit境界を維持する。

---

## 3. 明示的な非対象

次をP-18へ混載しない。

### 3.1 P-07 Finish修正

`src/spec_dock/runtime/application/direct_finish.py` の、selection観測が`invalid`または`unavailable`でも明示TARGETならGitHub Closeまたはlocal lifecycle更新へ進み得る不具合は、POSIXでも到達する独立したP1である。

対象は別TDD単位の次の二pathであり、P-18のcommitへ含めない。

- `src/spec_dock/runtime/application/direct_finish.py`
- `tests/cli_runtime/test_issue413_finish.py`

P-18完了後、全Issue認定前にP-07として修正し、fresh reviewへ渡す。現在のr12 failはP-18で閉じたことにしてはならない。

### 3.2 その他の非対象

- Scope schema3の変更
- workspace protocolの変更
- 既存Scope ID、GitHub linkage、parent/dependencyの変更
- `specdock.work-target/v1` のversion追加
- basename token形式の変更
- 実在Windows recordの自動変換・削除
- compatibility union、migration shim、旧形readerの新設
- 新しい台帳、cache、daemon、registry、journal
- lock file、PID file、mkdir lock
- ACL、chmod等による通常編集制限
- 新command、新namespace、work release
- Start以外への共通排他追加
- network filesystem、複数host、異OS同時mountの新保証
- P-13の42 AC全体認定
- P-14の実ブラウザ検証
- human merge、package公開
- P-16のdogfood切替
- P-17の既存#413 import / 正式Start

---

## 4. 検証済みbaseの現状

### 4.1 domainとschemaの差

`artifacts/data-schema.json::$defs.identity` は既に次のPOSIX限定契約である。

- `platform` は `"posix"` の定数
- `device` は10進文字列
- `file_id` は10進文字列
- `additionalProperties=false`

したがって、Redを作るためにschemaへWindows形を戻してはならない。attachments-bundle

一方、現行 `src/spec_dock/runtime/domain/work_target.py::PhysicalIdentity` は `Literal["posix", "windows"]` で、Windowsの32桁hex `file_id` を受理している。意味あるRedは「schemaとdomainが不一致で、domainがWindows payloadを受理すること」である。

### 4.2 utilityとbusiness入口

`src/spec_dock/cli.py::main` はparse後、help/completionを処理してから `runtime_dispatch.dispatch` をimportする。`--version`もparserのutility結果としてbusiness dispatchへ到達しない。これは維持すべき既存構造である。

`src/spec_dock/runtime/commands/runtime_dispatch.py::dispatch` には現在OS guardがなく、先頭から次の経路へ進み得る。

- installation
- `workspace validate --ci`
- `workspace doctor --raw`
- 通常project context解決
- 各business handler

guardはこれらより前、`dispatch` の最初の実行分岐に置く。

既存の`failure(...)`は通常の`OperationResult`とpresentation経路を使えるため、Windows専用envelopeや別rendererは作らない。

### 4.3 撤去対象の現行接続

| file | 現行接続 | P-18での扱い |
|---|---|---|
| `runtime/infra/json_store.py` | `WindowsDirectory`によるguarded JSON read分岐 | Windows import/branchだけ削除 |
| `runtime/infra/identity.py` | `_windows` field、Windows directory open/verify/close | POSIX descriptorだけへ縮小 |
| `runtime/infra/start_lock.py` | `WindowsMutex`、mutex name、abandoned処理 | POSIX `fcntl.flock`だけを維持 |
| `runtime/infra/work_target_store.py` | Windowsなら`NotImplementedError` | Windows分岐・専用文言だけ削除 |
| `runtime/infra/windows_handles.py` | Win32 directory/mutex/JSON API | module全削除、aliasなし |
| `tests/unit/infra/test_windows_*.py` | Windows専用三test | 同じsource撤去commitで削除 |
| `tests/integration/test_issue413_native_lock.py` | POSIXとNTFS/WAIT_ABANDONEDが混在 | Windows caseだけ除去 |
| `tests/unit/infra/test_start_lock.py` | Windows mutex name testが一件混在 | 当該一件だけ除去 |
| `.github/workflows/provider-ci.yml` | Windows専用job | 独立CI commitで削除 |

計画の専用三test以外に、現行 `tests/unit/infra/test_start_lock.py` には `test_windows_mutex_uses_only_canonical_physical_identity` が存在する。これもmodule削除と同じGreen単位に含め、同fileのPOSIX別process、kill後解放、identity replacement、timeout検査は残す。

CIは現在、通常`make lint` / full pytestを行う`provider-tests`、Ubuntu/macOS matrixの`provider-distribution-parity`、Windows専用の`provider-windows-native-adapters`から成る。削除するのは最後のjobだけである。

### 4.4 P-18.1 scanの扱い

既に実施済みのread-only scanでは、同cloneの7 worktreeと所有するIssue413検証consumer/backupを対象に、6 recordすべてPOSIX、Windows record 0、read error 0、write 0である。

これは未提示の外部backupまで調査した証拠ではない。新たに許可対象が提示されない限り同じscanを形式的に繰り返す必要はないが、後から実在Windows recordが一件でも判明した場合は、削除・変換せずP-18を停止する。attachments-bundle

---

## 5. 変更禁止の保全契約

| 保全対象 | 実装上の禁止事項 |
|---|---|
| work-target filename | `target-<32桁lower-hex>.json`を変更しない |
| work-target schema | `specdock.work-target/v1`を変更しない |
| record bytes | POSIX recordのfield、sort、newline、既存例を変更しない |
| publication | same-directory stage、exclusive create、flush、file fsync、no-replace rename、directory fsyncを弱めない |
| reader | descriptor基準、nofollow、regular/single-link、exact bounded bytes、前後identity確認を弱めない |
| removal | 観測済みの正確なbasename、file identity、digestだけを対象にする |
| Start lock | common-dirの既存descriptorへの`flock`、有限timeout、monotonic budget、finally解放を維持 |
| scope data | schema3、ID、linkage、parent/dependency、unknown fieldを変更しない |
| workspace | `specdock.worktree-writer/v1`を変更しない |
| operation result | Git原文、native returncode、partial/unknown、effectsの正直な報告を維持 |
| normal editing | metadata、Artifact、Workbench、通常ファイル編集へ共通Start lockを追加しない |
| historical evidence | 旧review、Windows調査、失敗log、過去測定を削除・成功へ書き換えない |

次の二fileは「Windowsらしいpath制約がある」という理由で変更してはならない。

- `src/spec_dock/runtime/domain/artifacts.py`
- `src/spec_dock/runtime/infra/committed_workspace.py`

reserved filename、basename、backslash、absolute/relative path、dot component等の既存防護は製品の一般path契約であり、Windows adapterではない。P-18でpath policyを変える必要が生じた場合は、変更せず停止する。

---

# 6. 実装手順

## P-18.1 — base固定、inventory、停止gate

### 目的

実装対象が正確なrepository・branch・SHAであり、未分類のWindows callerや未保全recordがないことを固定する。ここはread-onlyであり、通常はcommitを作らない。

### 開始command

```bash
BASE=dd90ca978fd711c32df7bbdf38aea516f62bbb1c
BRANCH=codex/iss-00413-external-cli-state

test "$(git rev-parse HEAD)" = "$BASE"
test "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH"
test -z "$(git status --porcelain=v1)"
test "$(git rev-parse '@{u}')" = "$BASE"
git rev-parse --symbolic-full-name '@{u}'
```

一つでも不一致なら、別branch、添付、memory、旧briefへfallbackせず停止する。

### current reference inventory

```bash
rg -n -i \
  'windows_handles|WindowsDirectory|WindowsMutex|windows_mutex_name|win32|NTFS|WAIT_ABANDONED|platform.?windows|windows-latest|provider-windows-native-adapters' \
  src/spec_dock/runtime tests .github/workflows/provider-ci.yml \
  docs/issue-plans/iss-00413-external-cli-state
```

一致は次の四群へ分類する。

1. current runtime接続
2. current test/CI受入
3. unsupported-platform negative test
4. history/raw evidenceまたは一般path policy

文字列一致だけを理由に削除しない。

importの実callerはASTでも確認する。

```bash
python - <<'PY'
from __future__ import annotations

import ast
from pathlib import Path

roots = (Path("src"), Path("tests"))
needle = "windows_handles"

for root in roots:
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            raise SystemExit(f"syntax error while scanning: {path}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or "", *(alias.name for alias in node.names)]
            else:
                continue
            if any(needle in name for name in names):
                print(f"{path}:{getattr(node, 'lineno', '?')}: {names}")
PY
```

### 変更前characterization

```bash
uv run pytest \
  tests/unit/infra/test_work_target_store.py \
  tests/unit/infra/test_directory_identity.py \
  tests/unit/infra/test_start_lock.py \
  tests/integration/test_issue413_native_lock.py \
  tests/cli_runtime/test_cli_vnext_contract.py \
  -q -s -ra
```

既存Windows専用testが存在すること自体はこの時点のbaselineである。skipをWindows成功と記録しない。

### 停止条件

- HEAD、branch、upstream SHA不一致
- dirty/untracked implementation差分
- 新しい許可対象に実在Windows work-target record
- `windows_handles.py`の未分類caller
- R/D/PとOS decisionの矛盾
- raw evidenceの削除または所在不明
- POSIX characterizationが変更前から非0で、既存失敗との分類ができない

---

## P-18.2 — POSIX identityと単一business guardのRed→Green

### 対象path

```text
src/spec_dock/runtime/domain/work_target.py
src/spec_dock/runtime/commands/runtime_dispatch.py
tests/cli_runtime/test_os_support_retirement.py    # 新規
```

原則として次は変更しない。

```text
src/spec_dock/cli.py
docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json
```

schemaは既にPOSIX限定であり、`cli.py`のutility先行構造も既に正しい。必要な回帰testは追加するが、意味のないsource churnは避ける。

### Red 1 — domain/schema不一致

新規test:

```text
test_physical_identity_contract_is_posix_only
```

検査内容:

- schemaの`platform.const`が`posix`
- schemaの`device` / `file_id`が10進文字列
- `PhysicalIdentity.from_payload()`が正常なPOSIX payloadを受理
- 現行domainがWindows payloadを受理するためRed
- Windows形をschemaへ再追加してRedを作らない

固定するnegative payload例:

```python
{
    "platform": "windows",
    "device": "123",
    "file_id": "00112233445566778899aabbccddeeff",
}
```

### Red 2 — business guard不在

新規test:

```text
test_unsupported_business_dispatch_stops_before_context_and_effects
```

実施内容:

- `sys.platform`を非対応値へsimulationする。
- parserで妥当な`work start iss-00413 --base HEAD --json`相当のnamespaceを作る。
- `runtime_dispatch.resolve_context`を、呼ばれたら即失敗するsentinelへ置換する。
- `dispatch`を実行する。
- 現行はcontextへ進むためRed。
- Greenでは次を要求する。

```text
exit_code = 3
error.code = "UNSUPPORTED_PLATFORM"
effects = []
resolve_context calls = 0
Git calls = 0
gh calls = 0
file/stage/write calls = 0
```

exit 3は既存のprecondition/readiness分類へ合わせる。既存の公開CLI schemaが別のexitを既に固定している事実が見つかった場合は、勝手にschemaを変えず停止する。

### Red 3 — 実entrypointのimport順

新規test:

```text
test_unsupported_real_entrypoint_reaches_guard_without_importing_fcntl
```

subprocess内で次を行う。

1. `spec_dock.cli`を通常importする。
2. `fcntl`を新規importしたら失敗するimport blockerを入れる。
3. `sys.platform`を非対応値へ設定する。
4. `spec_dock.cli.main()`からparser-validなbusiness commandを起動する。
5. import errorではなく`UNSUPPORTED_PLATFORM`を得る。
6. temp CWDのentry/bytesが不変であることを確認する。

これはWindows native受入ではなく、guardより前に`start_lock.py`等のPOSIX-only moduleをimportしていないことのsimulationである。

### utility回帰

新規testでは代表的utilityだけを確認し、44 leaf全部の重複testを作らない。

```text
test_unsupported_platform_keeps_utilities_context_free
```

- root help
- 代表leaf help
- `--version`
- completion

business runtimeと`fcntl`のimportを禁止してもexit 0であることを確認する。

全44 leafと3 completionは既存wheel testを引き続きauthorityにする。現行のwheel testは外部venv、`PYTHONPATH`なし、全leaf help、`--version`、bash/zsh/fish completionを既に一つの配布境界で検査している。

### Red command

```bash
uv run pytest tests/cli_runtime/test_os_support_retirement.py -q
```

期待するRedはassertion failureである。ImportError、collection failure、存在しないtest pathによるexit 4はRed完了に数えない。

### 最小Green

#### `PhysicalIdentity`

- `platform: Literal["posix"]`
- `platform == "posix"`だけを受理
- `device`と`file_id`はいずれも`[0-9]+`
- Windows union、hex32判定、compat aliasを削除
- `WorkTarget`の他field、encoder、schema versionを変更しない

#### `runtime_dispatch.dispatch`

`command = namespace.command_path`を得た直後、installation/raw/CI/context分岐より前に一回だけ判定する。

概念上の順序:

```python
command = namespace.command_path
if sys.platform not in {"linux", "darwin"}:
    return _render_result(
        namespace,
        failure(
            command,
            "UNSUPPORTED_PLATFORM",
            "business commands support Linux and macOS",
            3,
        ),
    )
```

実際のmessage文言は既存diagnostic styleへ合わせるが、code・exit・effectsは固定する。

禁止:

- `cli.py`のparser前へguardを移す
- command familyごとにguardを複製する
- 新しい`platform.py`等の抽象化moduleを作る
- Windows adapterをguardから呼ぶ
- Git/project capability probeをguardより先に行う

### Green command

```bash
python -m json.tool \
  docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json \
  >/dev/null

uv run pytest \
  tests/cli_runtime/test_os_support_retirement.py \
  tests/cli_runtime/test_cli_vnext_contract.py \
  tests/unit/infra/test_work_target_store.py \
  -q

git diff --check
```

### P-18.2完了条件

- domainとschemaがPOSIX限定で一致
- 既存POSIX record bytes不変
- utilityはbusiness runtimeをimportしない
- unsupported businessはcontext前にexit 3
- JSON/textの双方で`UNSUPPORTED_PLATFORM`
- `effects=[]`
- Git/GitHub/project/file effect 0
- guardは一箇所

---

## P-18.3 — Windows source接続と、それをimportする廃止testの同時撤去

### 最初の意味あるRed

`tests/integration/test_issue413_wheel.py::test_fresh_wheel_contains_one_normal_runtime_and_context_free_utilities` の`retired_entrypoints`へ次を追加する。

```text
spec_dock/runtime/infra/windows_handles.py
```

そのtestだけを実行し、wheelへmoduleが収録されているため失敗することを確認する。

```bash
uv run pytest \
  tests/integration/test_issue413_wheel.py::test_fresh_wheel_contains_one_normal_runtime_and_context_free_utilities \
  -q
```

このRed後、次のsource/test撤去を同じworking-tree unitで行う。Red状態のcommitは禁止する。

### 依存順

| 順 | 対象 | 削除するもの | 必ず残すもの |
|---:|---|---|---|
| 1 | `runtime/infra/json_store.py` | `WindowsDirectory` import、Windows read branch | descriptor reader、nofollow、regular/single-link、exact bytes、前後identity |
| 2 | `runtime/infra/identity.py` | `_windows` field、Windows open/verify/close | held FD、`fstat` identity、replacement detection、close |
| 3 | `runtime/infra/start_lock.py` | `WindowsMutex`、abandoned例外、mutex name、win32 branch | timeout validation、monotonic wait、`flock`、verify、finally unlock/close |
| 4 | `runtime/infra/work_target_store.py::_open` | Windows `NotImplementedError` branchと専用文言 | nofollow、fsync、no-replace、exact observed removal |
| 5 | `runtime/infra/windows_handles.py` | file全体 | alias、fallback、copyを残さない |

### 同じGreen commitで削除するtest

```text
tests/unit/infra/test_windows_mutex.py
tests/unit/infra/test_windows_directory.py
tests/unit/infra/test_windows_json_read.py
```

### 同じGreen commitで部分編集するtest

#### `tests/unit/infra/test_start_lock.py`

削除:

```text
test_windows_mutex_uses_only_canonical_physical_identity
```

維持:

- separate-process exclusion
- lock file作成0
- normal release
- kill後の解放
- directory replacement detection
- NaN/inf/負数/300秒超の拒否

#### `tests/unit/infra/test_directory_identity.py`

```python
assert held.identity.platform == "posix"
```

へ狭める。

replacement、symlink、descriptor、closeのassertionは変更しない。

#### `tests/integration/test_issue413_native_lock.py`

削除するのは次だけ。

- Windows helper
- NTFS case
- WAIT_ABANDONED case
- Win32専用import

維持する。

- same cloneのmain/linked exclusion
- different clone independence
-別process timeout
- normal release
- kill後release
- physical common-dir replacement
- Git common-dirへのSpecDock独自write 0

#### `tests/integration/test_issue413_wheel.py`

- `windows_handles.py`をretired moduleへ追加
- external noneditable wheel
- source参照不能
- utility全件
- runtime一組だけ
- static assets parity
- real console lifecycle

を維持する。

### unsupported entrypointの最終回帰

P-18.2の新testへ、source撤去後だけ成立する次のassertionを追加する。

- `spec_dock.runtime.infra.windows_handles`がsource/wheelに存在しない
- unsupported business entrypointで`fcntl`をimportしない
- module absenceによるImportErrorではなくguard結果を返す

これはWindows native testではない。

### collection checkpoint

module削除後、test削除前のcollection failureをcommitしてはならない。sourceとimporting testをすべて同時に整えた後に実行する。

```bash
uv run pytest --collect-only -q
```

非0ならcommit禁止。

### focused Green

```bash
uv run pytest \
  tests/cli_runtime/test_os_support_retirement.py \
  tests/unit/infra/test_work_target_store.py \
  tests/unit/infra/test_directory_identity.py \
  tests/unit/infra/test_start_lock.py \
  tests/integration/test_issue413_native_lock.py \
  tests/integration/test_issue413_wheel.py \
  -q -s -ra

git diff --check
```

### source残存確認

negative payloadや歴史文書ではなく、current adapter/importだけを判定する。

```bash
rg -n \
  'windows_handles|WindowsDirectory|WindowsMutex|windows_mutex_name|WAIT_ABANDONED' \
  src/spec_dock/runtime tests
```

期待されるcurrent product/import matchは0。新しいunsupported negative test内の`platform="windows"`文字列は意図した残存である。

### 停止条件

- POSIX testを削除・skipしないとGreenにならない
- `json_store`のexact bytesまたはsingle-link検査が弱くなる
- no-replace publicationが通常replaceへ変わる
- late A removalがBを消し得る
- `flock`の区間がStart以外へ広がる
- `fcntl`をimport可能にするWindows fallbackが必要になる
- lock file、PID、mkdir、ACL変更を要求される
- Git原文、partial、effectsが変わる
- `domain/artifacts.py`または`committed_workspace.py`の一般path policy変更が必要になる

---

## P-18.4 — Windows専用CI jobの撤去

P-18.3のsource/test Green後に行う。source撤去とCI撤去は別commitでよい。

### 変更path

```text
.github/workflows/provider-ci.yml
```

### 削除

```text
jobs.provider-windows-native-adapters
```

### 維持

```text
jobs.provider-tests
jobs.provider-distribution-parity
matrix.os = [ubuntu-latest, macos-latest]
candidate SHA verification
make lint
uv run pytest
test_provider_distribution.py
test_cli_entrypoint_vnext.py
test_issue413_wheel.py
test_issue413_assets.py
test_issue413_e2e.py
```

現行workflowのUbuntu/macOS matrixとWindows専用jobの境界は明確なので、Windows job削除を理由にdistribution test群を縮小しない。

### static確認

```bash
! rg -n \
  'provider-windows-native-adapters|windows-latest|test_windows_mutex|test_windows_directory|test_windows_json_read' \
  .github/workflows/provider-ci.yml

rg -n \
  'provider-tests|provider-distribution-parity|ubuntu-latest|macos-latest|make lint|uv run pytest|Verify PR head candidate checkout' \
  .github/workflows/provider-ci.yml

git diff -- .github/workflows/provider-ci.yml
git diff --check
```

### 停止条件

- UbuntuまたはmacOSがmatrixから消える
- `provider-tests`のfull lint/pytestが消える
- candidate SHA確認が消える
- shared E2E/wheel/assets testが消える
- Windows testをskip markerへ変えただけでjobを残す
- Windows job削除と無関係なAction versionやCI構造を同時変更する

---

## P-18.5 — 正本、配布reference、HTML、manifest、ZIPの同期

### 6.5.1 normative document

実装結果に合わせてstatus・現行path・証拠だけを更新する。

```text
docs/issue-plans/iss-00413-external-cli-state/requirement.md
docs/issue-plans/iss-00413-external-cli-state/design.md
docs/issue-plans/iss-00413-external-cli-state/plan.md
docs/issue-plans/iss-00413-external-cli-state/artifacts/acceptance-matrix.md
docs/issue-plans/iss-00413-external-cli-state/artifacts/implementation-acceptance-evidence.md
docs/issue-plans/iss-00413-external-cli-state/artifacts/source-basis.md
docs/issue-plans/iss-00413-external-cli-state/artifacts/traceability.json
```

次は既に正しいため、実装上の差異がない限り内容変更しない。

```text
artifacts/os-support-decision.md
artifacts/os-support-retirement-analysis.md
artifacts/os-support-retirement-plan.md
artifacts/data-schema.json
artifacts/user-decisions.md
artifacts/interview-worktree-start.md
```

### 6.5.2 provider docs / skills

実体を全文確認してから、対応OS・unsupported business rejection・P-18順序に関係するhunkだけを更新する。

```text
README.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md
src/spec_dock/assets/spec_dock/docs/reference_cli.md
src/spec_dock/assets/spec_dock/docs/migration.md
src/spec_dock/assets/spec_dock/docs/cli-redesign-guide.html
src/spec_dock/assets/static-inventory.json
```

provider assetを先に更新し、`spec-dock/` dogfood consumerをこのstepで直接編集しない。

### 6.5.3 current pack

```text
docs/issue-plans/iss-00413-external-cli-state/explanation.html
docs/issue-plans/iss-00413-external-cli-state/index.html
docs/issue-plans/iss-00413-external-cli-state/manifest.json
```

反映する内容:

- 対応OSはLinux/macOS
- Windows対応義務は失効
- P-18→P-13の順序
- current Windows source/test/CI撤去結果
- gpt-6.1-sol/maxが実装担当
- GPT-5.6 Sol / Proは採用資料・元ZIP著述モデル
- 本brief/planは正式SpecDock Startではない
- P-07、Code Review、FQ、merge、P-16、P-17は別

現在のmanifestは`archive_root=iss-00413-planning-pack`、self-hash除外、filesのbytes/sha256一覧を持つ一方、basisが旧main SHAのままである。P-18候補ではcandidate branch/SHA、実際の検査状態、P-14未実施状態を正直に更新する。

HTMLを変更した後、旧manifestの`browser_dynamic=passed`を新HTMLの実ブラウザ合格として流用しない。P-18では静的整合までを行い、動的browser結果はP-14へ渡す。

### 保全対象

次を全面生成・全面置換・削除しない。

```text
report.md
implementation-report.md
artifacts/user-decisions.md
artifacts/interview-worktree-start.md
artifacts/code-review-*
過去Windows調査
過去Linux/macOS raw logs
旧Implementation Brief
GPT-5.6 Sol / Proが生成した原本ZIP
```

`implementation-report.md`への記録が既存運用上必要な場合もappend-onlyとし、既存本文を再生成しない。

### provider asset regression

```bash
uv run pytest \
  tests/unit/infra/test_provider_distribution.py \
  tests/integration/test_issue413_assets.py \
  tests/integration/test_issue413_wheel.py \
  -q
```

### JSONとdiff

```bash
python -m json.tool \
  docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json \
  >/dev/null

python -m json.tool \
  docs/issue-plans/iss-00413-external-cli-state/artifacts/traceability.json \
  >/dev/null

python -m json.tool \
  docs/issue-plans/iss-00413-external-cli-state/manifest.json \
  >/dev/null

git diff --check
```

### manifest / ZIPの再検査

原本ZIPを上書きせず、候補ZIPは一時領域へ作る。

```bash
PACK_DIR=docs/issue-plans/iss-00413-external-cli-state
SHORT_SHA="$(git rev-parse --short=12 HEAD)"
CANDIDATE_ZIP="/tmp/iss-00413-p18-${SHORT_SHA}.zip"

export PACK_DIR CANDIDATE_ZIP

python - <<'PY'
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

base = Path(os.environ["PACK_DIR"]).resolve()
out = Path(os.environ["CANDIDATE_ZIP"]).resolve()
manifest_path = base / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

root = manifest["archive_root"]
assert isinstance(root, str) and root and "/" not in root and "\\" not in root

entries: list[tuple[str, bytes]] = []
seen: set[str] = set()

for item in manifest["files"]:
    rel = item["path"]
    pure = PurePosixPath(rel)
    assert not pure.is_absolute()
    assert ".." not in pure.parts
    assert rel not in seen
    seen.add(rel)

    path = base / Path(*pure.parts)
    payload = path.read_bytes()
    assert len(payload) == item["bytes"], rel
    assert hashlib.sha256(payload).hexdigest() == item["sha256"], rel
    entries.append((rel, payload))

manifest_bytes = manifest_path.read_bytes()
members = [("manifest.json", manifest_bytes), *entries]

out.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(out, "w", compression=ZIP_DEFLATED) as archive:
    for rel, payload in members:
        archive.writestr(f"{root}/{rel}", payload)

with ZipFile(out) as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert len(names) == len(set(names))
    assert {name.split("/", 1)[0] for name in names} == {root}
    expected = {f"{root}/{rel}" for rel, _ in members}
    assert set(names) == expected
    for rel, payload in members:
        assert archive.read(f"{root}/{rel}") == payload

print(out)
PY

python -m zipfile -t "$CANDIDATE_ZIP"
```

既存の共有JS/modal/template byte検査やlink/anchor validatorは、実在pathを先に発見する。

```bash
rg -n \
  'template_scripts_styles_modal_unchanged|html_unique_ids|duplicate.*id|broken.*link|zip_crc|manifest_hashes_vs_members' \
  tests scripts docs/issue-plans/iss-00413-external-cli-state \
  -g '*.py' -g '*.sh' -g '*.md' -g '*.json'
```

実在validatorを特定できない場合、架空のcommandで合格扱いせずP-18.5を停止する。

### P-18.5停止条件

- sourceを確認していない巨大fileの全文置換
- raw reviewや過去失敗の書換え
- old Windows briefを実装authorityへ復活
- `report.md` / `implementation-report.md`の再生成
- duplicate ID、broken anchor、manifest不一致
- original ZIP上書き
- 新HTMLのbrowser実行なしに`browser_dynamic=passed`
- provider assetとwheel assetのbytes不一致
- dogfood consumerへの無承認write

---

## P-18.6 — focused、full、wheel、E2E、OS別証拠

### 共通focused gate

```bash
git diff --check

make lint

uv run pytest \
  tests/cli_runtime/test_os_support_retirement.py \
  tests/cli_runtime/test_cli_vnext_contract.py \
  -q

uv run pytest \
  tests/unit/infra/test_work_target_store.py \
  tests/unit/infra/test_directory_identity.py \
  tests/unit/infra/test_start_lock.py \
  tests/integration/test_issue413_native_lock.py \
  -q -s -ra

uv run pytest \
  tests/unit/infra/test_provider_distribution.py \
  tests/integration/test_issue413_assets.py \
  tests/integration/test_issue413_wheel.py \
  tests/integration/test_issue413_e2e.py \
  -q -s -ra

uv build --wheel
```

`tests/integration/test_issue413_e2e.py` はfresh wheel、外部venv、provider source参照不能、実Git clone/linked worktree、stateful fake gh、Start重複拒否、兄弟並行、Sync、Finish、次Startを通る現行の配布境界である。P-18後も同じLinux/macOS経路を維持する。

### 通常full

```bash
uv run pytest -q --tb=short -ra
```

結果には必ず次を一組で記録する。

- candidate full SHA
- clean status
- OS / version
- architecture
- Python version
- filesystem
- command
- duration
- actual exit
- passed / failed / skipped / errors
- wheel sha256
- raw log path
- fake gh / live GitHubの区別
- 実行前後のsource/test hash

異なるSHAの件数を合算しない。

### macOS gate

必須環境:

- macOS arm64実環境
- APFS
- Python 3.12系
- Python 3.10下限の必要範囲
- clean candidate

必須確認:

1. focused gate
2. full pytest
3. fresh wheel
4. checkout外noneditable venv
5. provider source参照不能
6. root/leaf help、version、completion
7. Start
8. duplicate Start拒否
9. sibling Issue並行Start
10. readonly Sync
11. Finish
12. next Start
13. raw Git error / partial境界
14. stateful fake gh request数
15. live GitHub write 0
16. tracked specification / direct recordの前後保全

既存`2b2be5e2`の1916 passed / 4 skipped、manual console 14操作、fake gh 26 requestsは比較baselineであり、P-18候補の合格証拠へ転記しない。実際のcandidate結果を新たに取得する。

### Linux gate

必須環境:

- Linux x86_64
- Python 3.11系
- 実行FSを明記
- clean candidate

既存`121228c6`の最初のfullは、child processがPATHから`uv`を見つけられない状態でexit 1だった。これは失敗のまま保全する。同SHAでvalidation containerのPATHだけを補正したrunは1900 passed / 20 skipped、977.90秒、actual exit 0、324 input filesの前後hash一致である。

P-18候補では、製品source/testを変えてPATH問題を回避してはならない。containerのPATHだけを補正する。

```bash
UV_BIN="$(command -v uv)"
test -n "$UV_BIN"

env PATH="$(dirname "$UV_BIN"):$PATH" \
  "$UV_BIN" run pytest -q --tb=short -ra
```

再実行が非0なら、そのままLinux未合格として残す。追加調査なしに製品不具合または環境原因と断定しない。

### external wheel確認例

```bash
DIST_DIR="$(mktemp -d)"
VENV_DIR="$(mktemp -d)"

uv build --wheel --out-dir "$DIST_DIR"
WHEEL="$(find "$DIST_DIR" -maxdepth 1 -name 'spec_dock-*.whl' -print -quit)"
test -n "$WHEEL"

uv venv "$VENV_DIR"
uv pip install --python "$VENV_DIR/bin/python" "$WHEEL"

env -u PYTHONPATH -u PYTHONHOME \
  "$VENV_DIR/bin/python" -I -c \
  'import spec_dock; print(spec_dock.__file__)'

env -u PYTHONPATH -u PYTHONHOME \
  "$VENV_DIR/bin/spec-dock" --help

env -u PYTHONPATH -u PYTHONHOME \
  "$VENV_DIR/bin/spec-dock" --version

sha256sum "$WHEEL" 2>/dev/null || shasum -a 256 "$WHEEL"
```

working checkoutをrenameしたり権限変更したりせず、既存E2E harnessのように所有するcopyを参照不能にして検査する。

### P-18.6完了条件

- current runtimeにWindows専用module/import/branchがない
- Windows専用test三fileがない
- shared POSIX testsが残る
- Windows CI jobがない
- Ubuntu/macOS distribution matrixが残る
- work-target v1はPOSIX identityだけを受理
- utilityはcontext-free
- unsupported businessは副作用前に拒否
- POSIX descriptor/no-follow/single-link/exact bytes/fsync/no-replaceを維持
- Start-only flockを維持
- late observed removalを維持
- Linux/macOSのfocused/full/wheel/E2Eが候補SHA単位で合格
- skipと未実施をpassに数えない
- docs/HTML/manifest/候補ZIPが静的に整合
- cleanな通常push済みcandidateが存在
- P-07、P-13、Code Review、FQ、merge、P-16、P-17が別状態として残る

---

# 7. Commit / review単位

P-18.1は既にauthority pushとscanが完了しているため、追加差分がなければcommitを作らない。

| Unit | 推奨commit message | 含めるもの | Green条件 |
|---|---|---|---|
| A | `refactor(runtime): 対応OS境界をPOSIXへ固定` | `work_target.py`、`runtime_dispatch.py`、新OS test | domain/schema一致、utility維持、guard副作用0 |
| B | `refactor(runtime): Windows専用接続を撤去` | infra四file、`windows_handles.py`削除、専用test削除、shared test整理、wheel inventory | collection成功、POSIX focused Green、wheel非収録 |
| C | `ci(provider): Windows専用ジョブを撤去` | `provider-ci.yml`だけ | Windows job 0、Ubuntu/macOS/full gate維持 |
| D | `docs(issue413): P-18の撤去結果を同期` | R/D/P state、reference、skills、HTML、manifest | asset parity、JSON、link/manifest/ZIP静的整合 |
| E | `docs(issue413): LinuxとmacOSの検証証拠を固定` | candidate実測結果だけ | SHA別のactual exit、hash、skip、raw logを記録 |

Unit Bでは、module削除とそのmoduleをimportする廃止testの削除を必ず同じcommitへ含める。Unit Bの途中状態をcheckpoint commitしない。

## staging / commit pattern

各unitで、対象path以外の変更がないことを確認する。

```bash
git status --short
git diff --name-status
git diff --check
```

新規fileは明示stageする。

```bash
git add -- tests/cli_runtime/test_os_support_retirement.py
```

変更・削除pathもunitごとに明示確認する。

```bash
git diff --cached --name-status
git diff --cached --check
```

`commit-codex -a`は、全tracked差分がそのunitだけであることを確認した場合に限る。`-a`が無関係なtracked差分を巻き込む状態では停止する。

例:

```bash
commit-codex -a \
  -m "refactor(runtime): 対応OS境界をPOSIXへ固定" \
  -m "- work-target identityをPOSIX形へ限定" \
  -m "- utility後business前のunsupported platform guardを追加" \
  -m "- 副作用前拒否とimport順を回帰検査"
```

commit後:

```bash
git status --short
git show --stat --oneline HEAD
git show --check HEAD
```

pushは通常のnonforce pushだけを使う。

```bash
git push
```

force、force-with-lease、別branch push、automatic mergeは使わない。human merge gateを維持する。

---

# 8. 全体停止条件

次のいずれかに該当したら、該当unitで停止する。

1. base SHA、branch、upstreamが不一致
2. 未分類・無関係なdirty差分
3. 実在Windows work-target recordの発見
4. Windows moduleに未分類callerが残る
5. POSIX record bytesの変更が必要
6. Scope schema3、workspace protocol、ID変更が必要
7. basename token変更が必要
8. utilityより前へguardを置く必要がある
9. guardを複数familyへ複製する必要がある
10. `fcntl`等をguard前にimportしないと成立しない
11. lock file、PID、mkdir、ACL、daemon、cache、registryが必要
12. POSIX nofollow/single-link/fsync/no-replace/flockを弱めないとGreenにならない
13. shared E2E、Python 3.10/3.11、Linux/macOS laneを削除しないとGreenにならない
14. skip、xfail、collection exclusionでGreenを作る必要がある
15. `domain/artifacts.py`または`committed_workspace.py`の一般path policy変更が必要
16. P-07のFinish変更がdiffへ混入
17. raw evidence、旧review、旧failure logの削除
18. original GPT-5.6 ZIPの上書き
19. HTML/ZIP validatorの実体が確認できない
20. focused/full/Linux/macOS gateの非0を分類できない

停止時は設計を再議論してWindows対応を復活させず、観測した具体的差分と必要な人間判断だけを報告する。

---

# 9. P-18完了と全Issue認定の区別

| 状態 | P-18完了時に主張可能か |
|---|---:|
| Windows専用runtime接続の撤去 | 可能 |
| Windows専用test/CIの撤去 | 可能 |
| POSIX work-target/guard Green | 可能 |
| Linux/macOS focused/full/wheel/E2E Green | 実測が揃えば可能 |
| docs/HTML/manifest/候補ZIP静的整合 | 実測が揃えば可能 |
| P-18のclean/pushed candidate | 実在すれば可能 |
| P-07 Finish不具合修正 | **不可・別unit** |
| r12 P1 closure | **不可** |
| Issue #413全体のCode Review Strict pass | **不可・fresh reviewが必要** |
| Final Quality Gate v2 pass | **不可・別実行** |
| P-13の42 AC認定 | **不可** |
| human merge | **不可** |
| P-16 dogfood切替 | **不可** |
| P-17既存#413 import / 正式Start | **不可** |
| SpecDock正式Start完了 | **不可** |

P-18完了後は、P-07を別TDD/commitとして修正し、そのclean/pushed SHAを含む全体候補に対してfresh Code Review StrictとFQv2を行う。P-18のfocused/full成功を、全Issueのreview/FQ通過へ読み替えない。

また、本ブリーフの完成、P-18計画の登録、通常push済み正本の存在はいずれもSpecDock正式`work start`の成功証拠ではない。P-16とP-17はhuman merge後の未着手stepとして維持する。
