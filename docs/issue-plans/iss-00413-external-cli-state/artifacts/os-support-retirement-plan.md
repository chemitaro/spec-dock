# Issue #413 P-18 対応OS確定とWindows対応撤去計画

- 状態: 第三者提案をローカル照合して採用。P-18.1の限定scan完了、製品変更未着手
- 実装担当: 利用者指定GPT-6.1 Sol / Max。著述モデルと区別する
- authority: [対応OS決定](os-support-decision.md)
- 詳細な第三者分析: [os-support-retirement-analysis.md](os-support-retirement-analysis.md)
- verified checkpoint: `chemitaro/spec-dock` / `codex/iss-00413-external-cli-state` / `121228c6fca1fd016e7bccef009902396112ba43`
- 実装開始gate: 更新済み正本を通常push後、独立ChatGPT Implementation Brief Strict
- 著述モデル: GPT-5.6 Sol / Pro

## 目的と非目的

目的は、Linux/macOSの既存POSIX実装とIssue #413の確定機能を維持し、Windows要求・設計・source/test/CI接続だけを撤去することです。Windowsを止める代替管理基盤、schema version、ID体系、command、Release、daemon、cache、registry、journal、包括lockを追加しません。

本計画の登録、文書push、brief作成はSpecDock正式Startではありません。コード変更、commit、push、PR、Issue投稿、consumer移行は別の実施契約です。

## 実装単位一覧

| unit | 成果 | 主依存 | commit/review境界 |
|---|---|---|---|
| P-18.1 | authority/inventory/stop scan | verified branch/SHA、clean tree | docs/inventory only |
| P-18.2 | POSIX schema + unsupported guard characterization | P-18.1 | contract/test boundary |
| P-18.3 | Windows source dependencies removed | P-18.2 Green | source boundary |
| P-18.4 | Windows tests/CI removed, POSIX shared tests retained | P-18.3 | test/CI boundary |
| P-18.5 | R/D/P/reference/HTML/ZIP/evidence synchronized | P-18.4 focused Green | docs/distribution boundary |
| P-18.6 | Linux/macOS full/wheel/manual/Strict/FQ-ready evidence | P-18.5 | evidence-only boundary |

各unitは作業責務の境界です。commitは収集・importを含めGreenで成立する単位とし、module削除とそのmoduleをimportする廃止testの削除は同じsource撤去commitに含めます。独立したCI変更は別commitにします。後続briefはexact SHAと実在test pathを再確認します。

## P-18.1 authority・inventory・stop scan

### 読むauthority

1. `os-support-decision.md`
2. 更新済みrequirement/design/plan/data-schema
3. verified current source/tests/CI
4. 既存user-decisionsとraw evidence（衝突しない範囲）

### 実command

```text
git rev-parse HEAD
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse --symbolic-full-name '@{u}'
rg -n -i 'windows_handles|WindowsDirectory|WindowsMutex|windows_mutex_name|win32|NTFS|WAIT_ABANDONED' src tests .github docs/issue-plans/iss-00413-external-cli-state
rg -n -F '"platform": "windows"' src tests spec-dock
```

consumer/backup scanはread-onlyで、work-target v1 JSONの `clone_identity.platform` / `worktree_identity.platform` だけを対象にし、bodyやmetadataを書き換えません。

### 完了条件

全matchが current source/test/CI、current SSOT、history/raw evidenceに分類され、削除/変更/保全ownerが一意です。実在Windows recordは0です。

### 停止条件

branch/SHA不一致、dirty、untracked implementation差分、実在Windows record、未分類caller、raw evidence所在不明。

## P-18.2 POSIX schemaとunsupported guard

### 対象

- `domain/work_target.py::PhysicalIdentity`
- `artifacts/data-schema.json::$defs.identity`
- `commands/runtime_dispatch.py::dispatch` または実在するutility後business入口一箇所
- CLI contract/utility tests

### Red

- Windows identity payloadがdomain/schemaで通る。
- 模擬unsupported platformのwriterがGit/gh/open/mkdir/stageへ到達する。
- help/version/completionがplatform guardで失敗する。

### Green

- v1はposix/decimalだけ。既存POSIX example/record bytes・Scope schema3不変。
- utilityはexit0、businessは `UNSUPPORTED_PLATFORM`、effects=[]、side effect 0。
- guard実装は一箇所で、新module/registry/cacheなし。

### focused command

```text
uv run pytest tests/cli_runtime/test_os_support_retirement.py tests/cli_runtime/test_cli_vnext_contract.py -q
python -m json.tool docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json >/dev/null
```

## P-18.3 Windows source撤去

### 依存順

1. `json_store.py` reader branch
2. `identity.py` WindowsDirectory state/branch
3. `start_lock.py` mutex name/type/acquire/release
4. `work_target_store.py` Windows-specific stop wording
5. `windows_handles.py` file

### 保全characterization

- guarded JSON exact bytes、nofollow、single-link
- DirectoryIdentity held descriptor/verify/replacement detection
- StartLock same clone exclusion、different clone independence、timeout、kill release、Git write0
- WorkTargetStore immutable publication、fsync/no-replace、exact observed removal、late A does not delete B

### focused command

```text
uv run pytest tests/unit/infra/test_work_target_store.py tests/unit/infra/test_directory_identity.py tests/integration/test_issue413_native_lock.py -q -s -ra
```

削除後にwheel/source inventory testで `spec_dock.runtime.infra.windows_handles` が存在しないことを確認します。ImportErrorだけを意味あるRedにしません。

## P-18.4 test/CI撤去

### delete

- `tests/unit/infra/test_windows_mutex.py`
- `tests/unit/infra/test_windows_directory.py`
- `tests/unit/infra/test_windows_json_read.py`
- `provider-ci.yml::provider-windows-native-adapters`

### edit

- `test_issue413_native_lock.py`: Windows helper/NTFS/WAIT_ABANDONEDのみ削除
- `test_directory_identity.py`: POSIX expectationへ
- wheel/provider inventory test: Windows module non-inclusion

### 完了条件

current source/test/workflowのWindows実装参照0。Ubuntu/macOS lane、full lint/pytest、shared E2E、POSIX native casesは残る。skip/collection exclusionを増やさない。

## P-18.5 文書・HTML・ZIP

### update

requirement/design/plan/schema/matrix/evidence、新decision/analysis/plan、source-basis、traceability、README/reference/skills、HTML、pack manifest。

### preserve

report.md、implementation-report.md、user-decisions、interview、raw code reviews、Windows history、macOS/Linux original logs。

### check

```text
python -m json.tool docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json >/dev/null
python -m json.tool docs/issue-plans/iss-00413-external-cli-state/manifest.json >/dev/null
git diff --check
# repository-provided link/anchor/schema/HTML validatorsを実在path確認後に実行
```

sourceのない巨大fileを推測で置換せず、所有hash/templateを確認してhunk更新します。

## P-18.6 Linux/macOS gates

### common

```text
git diff --check
make lint
uv run pytest -q --tb=short -ra
uv build --wheel
```

candidate SHA、clean、OS、arch、Python、FS、wheel hash、command、duration、exit、pass/fail/skip、raw log pathを記録します。異なるSHAの件数を合算しません。

### macOS

- APFS、arm64の実環境
- Python3.12系full、必要な3.10下限
- fresh wheel→外部noneditable venv→provider source参照不能
- help/Start/duplicate/parallel sibling/Sync/Finish/next Start/raw Git partialを含む手動14操作相当
- fake gh request countとlive GitHub 0を明記

### Linux

- x86_64、Python3.11系、local/tmpfs fixtureを明記
- 既存 `121228c6fca1fd016e7bccef009902396112ba43` run: 4 failed/1884 passed/20 skipped/12 errors、exit1をrawのまま保全
- child processがuvを発見できるようvalidation container PATHだけを補正
- provider source/tests 324files hash `2bcbce60d8b318761f81529c4b998fae4d43027b52470fba317143400547494e` がbefore/after一致することを再確認
- 非0ならLinux未合格。製品不具合/環境原因を追加調査なしに断定しない

### final completion

1. Windows current code/test/CI 0、history evidence有り。
2. POSIX core guarantees all Green。
3. Linux/macOS full/lint/wheel/manual成功。
4. updated docs/HTML/ZIP/manifest整合。
5. clean pushed candidateに対するnew-scope Strict reviewとFinal Quality Gateを実行可能。
6. P-16/P-17未実施を明示。

## reviewで必ず問う点

- utilityより前にOS guardを置いていないか。
- commit revertで共通POSIX/E2Eを落としていないか。
- Windows削除を理由にlock file/daemon/cacheを追加していないか。
- work-target v1以外のScope schema/IDへ波及していないか。
- old Windows recordを黙って削除/変換していないか。
- raw failures/reviews/evidenceを消していないか。
- Linux旧PATH runを成功へ書換えていないか。
- plan/briefを正式Startと呼んでいないか。

## 2026-10-02 採用時のCodexローカル照合

第三者の回答時点の「Linux再実行予定」「r12進行中」は、下記の実測で更新します。原本ZIP・[回答原文](os-retirement-chatgpt-121228c6.md)は変更していません。

- [限定read-only scan](os-retirement-record-scan-121228c6.json): 同cloneの7 worktreeと所有するIssue413検証consumer/backupを確認。観測した6 recordはいずれもPOSIX、Windows record 0、読取error 0、書込0。未提示の外部backupまでは調査していません。実在Windows recordが後で判明すれば変換せず停止します。
- [Linux通常全件](linux-full-121228c6.md): PATHだけ補正した同SHAの通常fullは1900 passed / 20 skipped、977.90秒、actual exit0。324 input filesの前後hash一致。
- [r12 complete batch](code-review-p06-12-analysis.md): actual exit10、P1一件、review_status=fail。invalid/unavailableの選択観測でも明示FinishがCloseへ進む不具合はPOSIXにも存在するためP-07で修正します。新OS範囲のfinal passには流用しません。
- 実装担当は利用者の継続指定GPT-6.1 Sol / Max。後続briefの著述モデルはGPT-5.6 Sol / Proで、担当設定の再決定ではありません。
- Windows source撤去と、それをimportする廃止testの削除は一つのGreenなcommitにし、壊れた収集状態をcheckpointとして提出しません。独立CI変更は別commitにします。
