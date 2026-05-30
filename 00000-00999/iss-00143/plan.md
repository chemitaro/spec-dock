---
種別: 実装計画書（Issue）
ID: "iss-00143"
タイトル: "Manage External Git Worktrees"
関連GitHub: ["#143"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00107", "init-local-00002"]
---

# iss-00143 Manage External Git Worktrees — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID

- AC:
  - AC-001: `worktree list` / `show` は同一 repository の Git linked worktree 全体を扱う。
  - AC-002: `list` / `show` / `remove` は `SPEC_DOCK_WORKTREE_ROOT` なしでも動作する。
  - AC-003: `worktree create` は引き続き `SPEC_DOCK_WORKTREE_ROOT` 必須。
  - AC-004: external / unmanaged linked worktree を remove でき、branch は削除しない。
  - AC-005: main / current / bare / stale / missing record は `--force` でも削除しない。
  - AC-006: `managed: bool` を維持し、classification diagnostic fields を追加する。
  - AC-007: provider docs と dogfooding docs を更新する。
- EC:
  - EC-001: ambiguous target は候補付きで拒否する。
  - EC-002: branch-only target は拒否する。
  - EC-003: Git remove failure 時は filesystem cleanup しない。
  - EC-004: invalid root は availability blocker ではなく classification diagnostic にする。
  - EC-005: cleanup は target-only で symlink / broken symlink / file / directory / unsupported type / race を明示的に扱う。
- 制約:
  - branch deletion、`git worktree prune` / repair、orphan directory cleanup、Codex Desktop 固有 lifecycle は実装しない。
  - provider-side source of truth は `src/spec_dock/assets/spec_dock/...`。

## 依存関係から導く実装順序

- 依存関係の正本:
  - `design.md` の依存関係、Module Dependency Diagram、ファイル変更計画。
- 順序ルール:
  - contract/model を先に固定し、application behavior、cleanup port、presentation/docs の順に下流へ進める。
  - tests は各 behavior slice に付ける。最後にまとめて追加しない。
- step 依存サマリー:
  - S01: `WorktreeRecordView` の additive field を固定する。S02/S03/S05 を unblock。
  - S02: root optional inventory と create root-required regression を固定する。S03/S05 を unblock。
  - S03: external remove と hard blocker matrix を固定する。S04 を unblock。
  - S04: Git-first / target-only cleanup port を固定する。S90 を unblock。
  - S05: JSON/text/help surface を更新する。S90 を unblock。
  - S90: docs parity を解消する。S99 を unblock。
  - S99: issue-wide validation / reviewer gates / report closure。

## ステップ一覧

- S01: Contract Fields and Compatibility
  - 観測可能な振る舞い: `managed` は boolean のまま、classification diagnostics が model / JSON に追加される。
  - 対象ファイル: `application/contracts.py`, `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-006
  - レビューゲート: code-reviewer
- S02: Root-Optional List / Show / Remove Inventory
  - 観測可能な振る舞い: root missing / blank / invalid でも list/show/remove inventory が Git records から構築される。create は root-required のまま。
  - 対象ファイル: `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-001, AC-002, AC-003, EC-004
  - レビューゲート: code-reviewer
- S03: External Remove and Hard Blockers
  - 観測可能な振る舞い: external linked worktree は remove 可能で、main/current/bare/path_missing/record_missing は non-bypassable。
  - 対象ファイル: `application/worktree.py`, `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-004, AC-005, EC-001, EC-002
  - レビューゲート: code-reviewer
- S04: Git-First Target-Only Cleanup
  - 観測可能な振る舞い: Git remove 成功後だけ resolved target を cleanup し、symlink を follow せず、unsupported/race は fail-closed。
  - 対象ファイル: `application/ports.py`, `application/worktree.py`, `infra/fs_cli.py`, `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-004, EC-003, EC-005
  - レビューゲート: code-reviewer
- S05: Presentation, CLI Text, and Help
  - 観測可能な振る舞い: JSON/text/help が all-linked-worktree contract と classification diagnostics を表す。
  - 対象ファイル: `presentation/cli_text.py`, `commands/worktree.py`, `cli/parser.py`, `tests/cli_runtime/test_worktree.py`
  - 閉じる要件: AC-001, AC-002, AC-006
  - レビューゲート: code-reviewer
- S90: Docs Impact Resolution
  - 観測可能な振る舞い: provider docs と dogfooding docs が runtime contract と一致する。
  - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`, `spec-dock/docs/reference_worktree.md`
  - 閉じる要件: AC-007
  - レビューゲート: spec-reviewer
- S99: Final Quality Gate
  - 観測可能な振る舞い: closure coverage、tests、validation、QA/code/spec review、report evidence が揃う。
  - 対象ファイル: product file は原則なし。report update は main orchestrator が行う。
  - 閉じる要件: AC-001..AC-007, EC-001..EC-005
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応

- AC-001 -> S02, S05, S99
- AC-002 -> S02, S05, S99
- AC-003 -> S02, S99
- AC-004 -> S03, S04, S99
- AC-005 -> S03, S99
- AC-006 -> S01, S05, S99
- AC-007 -> S90, S99
- EC-001 -> S03, S99
- EC-002 -> S03, S99
- EC-003 -> S04, S99
- EC-004 -> S02, S99
- EC-005 -> S04, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | 種別 | 仕様リンク | 固定する期待値 | 必須 | 証跡レベル |
|---|---|---|---|---|---|---|
| tc-001 | S01 | compatibility | AC-006, D-002 | `managed` は boolean のまま、classification fields が model / JSON source model に存在する | yes | red-required |
| tc-002 | S02 | acceptance | AC-001, AC-002, EC-004, D-001, D-005 | root missing / blank / invalid は list/show/remove の availability failure にならない | yes | red-required |
| tc-003 | S02 | regression | AC-003 | `worktree create` は root missing / blank / invalid で fail-fast し side effect を作らない | yes | covered-existing + targeted regression |
| tc-004 | S03 | acceptance | AC-004, D-003 | external/unmanaged linked worktree は remove 可能で、`unmanaged` は blocker ではない | yes | red-required |
| tc-005 | S03 | safety | AC-005 | main/current/bare/path_missing/record_missing は `--force` でも non-bypassable | yes | red-required |
| tc-006 | S03 | regression | EC-001, EC-002 | ambiguous target と branch-only target は Git remove 前に拒否される | yes | covered-existing + targeted regression |
| tc-007 | S04 | safety | EC-003, D-004 | Git remove failure は surfaced error になり、filesystem cleanup を呼ばない | yes | red-required |
| tc-008 | S04 | cleanup | AC-004, EC-005, D-004 | remaining directory / symlink / broken symlink / regular file は target-only cleanup される | yes | red-required |
| tc-009 | S04 | cleanup-negative | EC-005, D-004 | unsupported type、permission/race/lstat/unlink/rmtree failure は `post_remove_cleanup_failed` になり parent/root/namespace を削除しない | yes | red-required |
| tc-010 | S05 | output | AC-001, AC-002, AC-006 | JSON/text/help が classification diagnostics と all-linked-worktree wording を表す | yes | red-required |
| tc-011 | S90 | docs | AC-007 | provider docs と dogfooding docs が root optional list/show/remove、create root-required、external remove、target-only cleanup を説明する | yes | inspect-only |
| tc-012 | S99 | final-gate | AC-001..AC-007, EC-001..EC-005 | targeted/full tests、validation、sync decision、report closure、final reviewers が完了する | yes | manual-required |

## レビュー / QA ゲート方針

- RG1 step review:
  - 実施タイミング: S01..S05 / S90 の各 step 完了後、commit 前。
  - reviewer: code-reviewer（runtime / tests / scaffold behavior）、spec-reviewer（docs-only / spec alignment）。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: Issue 全体の obligation coverage、missing high-value tests、manual / integration test 要否。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / docs / implementation 整合。
- 委譲 worker の出力は reviewer pass として扱わない。

## 実行ルール（全ステップ共通）

- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary を目安にする。
- `plan.md` は planned requirements、evidence destination、closure 条件だけを所有する。observed result は `report.md` に記録する。
- 実装中に新しい仕様、bug class、外部 contract risk、未計画 closure が見つかった場合は、report 記録だけで足りるか、plan amendment と re-review が必要かを判断する。
- delegated worker は canonical spec docs を直接編集しない。canonical `report.md` の証跡更新は main orchestrator が行う。

## 実装ステップ

### 実装ステップ S01 — Contract Fields and Compatibility

- 振る舞いの目標:
  - `managed: bool` を維持しつつ、classification diagnostics を `WorktreeRecordView` に追加する。
- design 参照:
  - D-002, インターフェース契約, AC-006 mapping。
- 依存:
  - approved `requirement.md`, approved `design.md`。
- unblock:
  - S02, S03, S05。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - `managed_classification_available: bool`
  - `classification_reason: str`
  - `origin: str`
  - allowed values:
    - `classification_reason`: `root_valid`, `root_missing`, `root_blank`, `root_invalid`, `namespace_symlink`
    - `origin`: `spec_dock_managed`, `external`, `classification_unavailable`
  - existing fields は rename / remove しない。
- Red / 代替証跡の要件:
  - `red-required`: 新規 classification fields を期待する focused test を先に追加し、現行 model では missing attribute / missing JSON field で失敗することを確認する。
  - `covered-existing`: 既存 `WorktreeRecordView` construction test が破壊される場合は、field 追加による意図的な compatibility update として差分を記録する。
- 具体テストケース:
  - `tc-s01-001` acceptance: classification fields serialization
    - 前提: managed / external / classification unavailable を表す `WorktreeRecordView` fixture を用意する。
    - 操作: JSON payload 生成 path または `_worktree_payload` 相当を実行する。
    - 期待結果: `managed` は boolean、`managed_classification_available`、`classification_reason`、`origin` が design-approved value で出力される。
    - 失敗検出: field missing、`managed` nullable 化、未承認 value、既存 field rename を検出する。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-001
  - `tc-s01-002` regression: existing construction compatibility
    - 前提: 既存 tests 内の `WorktreeRecordView` construction / fake record helper を対象にする。
    - 操作: classification fields 追加後に existing focused tests を実行する。
    - 期待結果: 既存 semantic fields は同じ意味で維持され、必要な fixture update だけで通る。
    - 失敗検出: default 値で設計上必要な classification を隠す、または既存 record contract を壊す。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-001
- Green 検証:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
- Refactor / cleanup ガードレール:
  - contract field 追加に必要な dataclass / helper update に限定し、application behavior は変えない。
  - unused imports / stale helper だけを削除する。
- report 証跡:
  - TDD evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Delegated Worker Evidence、Reviewer Gate Status。
- step closure contract:
  - tc-001 の Red/Green evidence が report に記録され、code-reviewer が pass していること。
- step gate / commit:
  - step reviewer gate: code-reviewer、範囲は contract/model/test fixture。
  - commit/no-op gate: S01 の変更だけを commit boundary にし、no-op の場合は tc-001 が既存 test で既に閉じる根拠を report に記録する。
- amendment trigger:
  - field 名 / allowed values / `managed` compatibility を design から変更する必要が出た場合は plan/design amendment と re-review。
- 委任契約:
  - delegated role: dev-coder
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`
  - allowed paths: `application/contracts.py`, focused tests
  - forbidden changes: `application/worktree.py` behavior、docs、CLI wording
  - acceptance / closure: tc-001 が Red/Green evidence と code-reviewer pass で閉じる。
  - required tests or verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - output required: changed files、Red/Green result、closure id status、report evidence note、unresolved risks。
  - reviewer focus: code-reviewer
  - stop condition: field naming / enum values が design と衝突する。

### 実装ステップ S02 — Root-Optional List / Show / Remove Inventory

- 振る舞いの目標:
  - Git records を source of truth とし、root missing / blank / invalid でも list/show/remove inventory を構築する。
- design 参照:
  - D-001, D-005, `_build_inventory`, optional classification context。
- 依存:
  - S01。
- unblock:
  - S03, S05。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - create-only strict root resolver と optional classification context を分離する。
  - root missing / blank / invalid / namespace symlink は `managed=false`, `managed_classification_available=false`, `origin=classification_unavailable`。
  - valid root は namespace path から `spec_dock_managed` / `external` を判定する。
  - `worktree create` は strict root resolver を維持する。
- Red / 代替証跡の要件:
  - `red-required`: root missing / invalid で `list --json` / `show --json` が現行実装では root-required error になることを先に固定する。
  - `covered-existing`: create root-required no-side-effect は既存 coverage を確認し、不足 variant だけ追加する。
- 具体テストケース:
  - `tc-s02-001` acceptance: root missing list/show
    - 前提: repository に main worktree と external linked worktree があり、環境から `SPEC_DOCK_WORKTREE_ROOT` を削除する。
    - 操作: `worktree list --json` と `worktree show <external-basename> --json` を実行する。
    - 期待結果: command は成功し、Git records の全 linked worktree を含み、各 record は `managed=false`, `managed_classification_available=false`, `classification_reason=root_missing`, `origin=classification_unavailable` を返す。
    - 失敗検出: `SPEC_DOCK_WORKTREE_ROOT is required`、record omission、classification field missing。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-002
  - `tc-s02-002` negative: invalid root diagnostics
    - 前提: root を relative path / file path / namespace symlink など invalid state にする。
    - 操作: `worktree list --json`、`show --json`、remove preflight path を実行する。
    - 期待結果: availability failure ではなく classification unavailable diagnostic が返る。remove は target safety blocker または Git result まで進める。
    - 失敗検出: `invalid_worktree_root` で list/show/remove inventory が停止する。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-002, tc-004
  - `tc-s02-003` negative: blank root diagnostics
    - 前提: `SPEC_DOCK_WORKTREE_ROOT` を空文字または空白のみの値にし、repository に Git linked worktree が存在する。
    - 操作: `worktree list --json`、`worktree show <target> --json`、remove preflight path を実行する。
    - 期待結果: availability failure ではなく、`managed=false`, `managed_classification_available=false`, `classification_reason=root_blank`, `origin=classification_unavailable` を返す。
    - 失敗検出: blank root を `root_missing` / `root_invalid` と誤分類する、または list/show/remove inventory が停止する。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-002
  - `tc-s02-004` regression: create root-required
    - 前提: missing / blank / invalid `SPEC_DOCK_WORKTREE_ROOT` を設定する。
    - 操作: `worktree create` を実行する。
    - 期待結果: fail-fast し、branch、worktree directory、bootstrap side effect を作らない。
    - 失敗検出: create が root optional path を使って進む、または partial side effect が残る。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-003
- Green 検証:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
- Refactor / cleanup ガードレール:
  - strict root resolver は create path に残し、optional classification helper は list/show/remove inventory だけで使う。
  - Git gateway / command parser の責務を広げない。
- report 証跡:
  - TDD evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta。
- step closure contract:
  - tc-002 と tc-003 が pass し、create root-required と inventory root-optional の両方が Closure Coverage に記録されること。
- step gate / commit:
  - step reviewer gate: code-reviewer、範囲は inventory classification と create regression。
  - commit/no-op gate: S02 の behavior slice のみを commit boundary にする。
- amendment trigger:
  - root invalid を fatal error として残す必要、または create root-required を弱める必要が判明した場合。
- 委任契約:
  - delegated role: dev-coder
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`
  - allowed paths: `application/worktree.py`, focused tests
  - forbidden changes: remove execution / cleanup behavior。ただし remove preflight の inventory 構築に必要な最小変更は可。
  - acceptance / closure: tc-002 と tc-003 が pass し、root optional inventory と create root-required regression が report に記録される。
  - required tests or verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - output required: changed files、root state matrix、Red/Green result、closure id status、report evidence note、unresolved risks。
  - reviewer focus: code-reviewer
  - stop condition: root optional 化が create contract を弱める。

### 実装ステップ S03 — External Remove and Hard Blockers

- 振る舞いの目標:
  - external linked worktree を remove 可能にし、non-bypassable safety blockers を維持する。
- design 参照:
  - D-003, remove_blockers, シーケンス差分。
- 依存:
  - S01, S02。
- unblock:
  - S04。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - `unmanaged` を `_remove_blockers()` / `_non_bypassable_remove_blockers()` から外す。
  - external / unmanaged は diagnostic field で識別できるが remove blocker ではない。
  - Git remove 直前に Git records を再読込し、record missing を拒否する。
  - ambiguous target / branch-only target は Git remove 前に拒否する。
  - `branch_deleted=false` を維持する。
- Red / 代替証跡の要件:
  - `red-required`: external/unmanaged remove が現行実装では `remove_blocked` + `unmanaged` になることを固定する。
  - `covered-existing`: ambiguous / branch-only target は既存 coverage を確認し、`unmanaged` blocker removal で退行しないことを示す。
- 具体テストケース:
  - `tc-s03-001` acceptance: external remove
    - 前提: central root 外に Git linked worktree を作成し、branch を保持する。
    - 操作: `worktree remove <external-basename> --force --json` を実行する。
    - 期待結果: exit 0、`removed_record=true`、`branch_deleted=false`、Git worktree record が消え、branch は残る。
    - 失敗検出: `remove_blocked` に `unmanaged` が含まれる、branch deletion、Git record が残る。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-004
  - `tc-s03-002` safety: hard blockers
    - 前提: main/current/bare/path_missing/record_missing の各 target state を用意する。
    - 操作: `worktree remove <target> --force --json` を実行する。
    - 期待結果: `remove_blocked` で拒否され、対応 blocker が JSON に含まれ、Git remove / cleanup は呼ばれない。
    - 失敗検出: `--force` で hard blocker を bypass する、または blocker が欠落する。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-005
  - `tc-s03-003` regression: target resolution blockers
    - 前提: ambiguous basename と branch-only target を用意する。
    - 操作: `worktree remove <target> --json` を実行する。
    - 期待結果: Git remove 前に ambiguity / branch target error が返り、candidates または machine-readable code を維持する。
    - 失敗検出: Git remove が呼ばれる、target が一意でないまま削除される。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-006
- Green 検証:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
- Refactor / cleanup ガードレール:
  - blocker matrix の変更に限定し、filesystem cleanup や docs は触らない。
  - `locked` は Git force semantics に任せる設計を維持し、SpecDock hard blocker に戻さない。
- report 証跡:
  - blocker matrix、TDD evidence、Closure Coverage、Reviewer Gate Status。
- step closure contract:
  - tc-004..tc-006 が pass し、external remove と hard blockers の両方が report に記録されること。
- step gate / commit:
  - step reviewer gate: code-reviewer、範囲は remove blocker / target resolution / Git record refresh。
  - commit/no-op gate: S03 の remove blocker behavior だけを commit boundary にする。
- amendment trigger:
  - external remove を許可するには追加 persistent state や branch deletion が必要と判明した場合。
- 委任契約:
  - delegated role: dev-coder
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`
  - allowed paths: `application/worktree.py`, focused tests
  - forbidden changes: filesystem cleanup implementation、docs
  - acceptance / closure: tc-004..tc-006 が pass し、external remove と hard blocker matrix が report に記録される。
  - required tests or verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - output required: changed files、blocker matrix、Red/Green result、closure id status、report evidence note、unresolved Git portability risks。
  - reviewer focus: code-reviewer
  - stop condition: Git record refresh なしで external remove を許可する必要が出る。

### 実装ステップ S04 — Git-First Target-Only Cleanup

- 振る舞いの目標:
  - Git remove 成功後だけ、resolved target path のみを cleanup する。
- design 参照:
  - D-004, target cleanup, `remove_target(path)` contract。
- 依存:
  - S03。
- unblock:
  - S90。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - cleanup port を target-only `remove_target(path)` 相当にする。
  - existence 判定は broken symlink を扱えるよう lstat-style にする。
  - directory は tree を削除する。
  - symlink / broken symlink は symlink 自体を unlink し、target を follow しない。
  - regular file は unlink する。
  - unsupported type、`lstat` / `unlink` / `rmtree` failure、race は `post_remove_cleanup_failed`。
  - Git remove failure 時は cleanup を呼ばない。
  - parent directory、central root、namespace directory は削除しない。
- Red / 代替証跡の要件:
  - `red-required`: current `remove_tree` directory-only cleanup では symlink/broken symlink/file/unsupported failure contract を閉じられないことを failing test で固定する。
  - `manual/inspect`: real platform fixture が不安定な unsupported type / race は fake filesystem gateway で failure path を固定してよい。
- 具体テストケース:
  - `tc-s04-001` safety: Git failure no cleanup
    - 前提: Git gateway が remove failure を返し、filesystem gateway は呼ばれたら失敗する spy にする。
    - 操作: `worktree_remove()` または CLI remove path を実行する。
    - 期待結果: Git failure error が返り、filesystem cleanup は 0 回。
    - 失敗検出: Git failure 後に cleanup が呼ばれる。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-007
  - `tc-s04-002` cleanup: remaining directory
    - 前提: Git remove 成功後も resolved target directory が残り、parent/root/namespace に sentinel file を置く。
    - 操作: post-remove cleanup path を実行する。
    - 期待結果: target directory だけ消え、parent/root/namespace sentinel は残る。
    - 失敗検出: parent/root/namespace deletion、target が残る。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-008
  - `tc-s04-003` cleanup: symlink / broken symlink
    - 前提: target path が symlink または broken symlink で、symlink target 側に sentinel を置く。
    - 操作: `remove_target(path)` 相当を呼ぶ。
    - 期待結果: symlink 自体だけ unlink され、symlink target / parent は変更されない。
    - 失敗検出: symlink target を follow して削除する、broken symlink を存在しない扱いで残す。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-008
  - `tc-s04-004` cleanup: regular file
    - 前提: resolved target path が regular file として残っている。
    - 操作: post-remove cleanup path を実行する。
    - 期待結果: file 自体が unlink され、parent は残る。
    - 失敗検出: file unsupported として失敗する、または parent を削除する。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-008
  - `tc-s04-005` cleanup-negative: unsupported / race
    - 前提: fake filesystem gateway で unsupported file type、`lstat` failure、`unlink` failure、`rmtree` failure、race を模擬する。
    - 操作: Git remove 成功後の cleanup path を実行する。
    - 期待結果: `post_remove_cleanup_failed` が返り、`removed_record=true`、target cleanup failure が reportable になる。
    - 失敗検出: silent success、parent/root/namespace cleanup、Git remove 前 failure と混同する。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-009
- Green 検証:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
- Refactor / cleanup ガードレール:
  - filesystem port change は target-only cleanup に限定し、general-purpose deletion framework にしない。
  - `remove_tree` 既存用途が残る場合は互換 layer を維持し、無関係な callers を変更しない。
- report 証跡:
  - cleanup boundary evidence、TDD evidence、Closure Coverage、Discovered Tests。
- step closure contract:
  - tc-007..tc-009 が pass し、cleanup boundary と failure behavior が report に記録されること。
- step gate / commit:
  - step reviewer gate: code-reviewer、範囲は filesystem port / Git-first orchestration / tests。
  - commit/no-op gate: S04 の cleanup behavior だけを commit boundary にする。
- amendment trigger:
  - symlink non-following cleanup、broken symlink cleanup、unsupported/race fail-closed のいずれかを弱める必要が出た場合。
- 委任契約:
  - delegated role: dev-coder
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`
  - allowed paths: ports、application remove orchestration、fs infra、focused tests
  - forbidden changes: broad filesystem refactor、parent cleanup、branch deletion、`git worktree prune`
  - acceptance / closure: tc-007..tc-009 が pass し、Git-first / target-only cleanup と failure behavior が report に記録される。
  - required tests or verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - output required: changed files、cleanup boundary matrix、Red/Green result、closure id status、report evidence note、platform-specific risk。
  - reviewer focus: code-reviewer
  - stop condition: cleanup boundary が design の固定契約を満たせない。

### 実装ステップ S05 — Presentation, CLI Text, and Help

- 振る舞いの目標:
  - command output と help が all-linked-worktree management と classification diagnostics を表す。
- design 参照:
  - インターフェース契約、presentation dependency。
- 依存:
  - S01, S02。
- unblock:
  - S90。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `tests/cli_runtime/test_worktree.py`
- 計画済み契約:
  - JSON payload は list/show/remove success と embedded worktree/candidates error に classification fields を含める。
  - text output は `managed` / `origin` / `classification_reason` / `remove_blockers` を scan 可能にする。
  - help/target wording から managed-only 表現を除く。
  - cleanup failure / remove blocker error JSON は machine-readable を維持する。
- Red / 代替証跡の要件:
  - `red-required`: current JSON/text/help に classification fields または all-linked wording がないことを output test で固定する。
- 具体テストケース:
  - `tc-s05-001` output: JSON diagnostics
    - 前提: managed / external / classification unavailable worktree records を含む CLI scenario を用意する。
    - 操作: `worktree list --json`, `show --json`, remove error JSON を取得する。
    - 期待結果: embedded worktree / candidates を含めて classification fields が出力される。
    - 失敗検出: success payload だけ更新され error payload が欠落する、field 名が design と異なる。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-010
  - `tc-s05-002` output: help wording
    - 前提: CLI parser help を取得できる test harness を用意する。
    - 操作: `worktree remove --help` を実行する。
    - 期待結果: target help は `Managed worktree id` ではなく、id/path/basename を示す。
    - 失敗検出: managed-only wording が残る。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-010
  - `tc-s05-003` output: text diagnostics
    - 前提: list/show text output に managed/external/unavailable records を含める。
    - 操作: text renderer または CLI text output を実行する。
    - 期待結果: `managed`、`origin`、`classification_reason`、`remove_blockers` が scan 可能に表示される。
    - 失敗検出: diagnostic が JSON にしか出ない、または既存 blocker/removable 情報が消える。
    - 検証方法: `python -m unittest tests.cli_runtime.test_worktree -v`
    - 関連 closure id: tc-010
- Green 検証:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
- Refactor / cleanup ガードレール:
  - rendering / help wording に限定し、application behavior は変更しない。
  - JSON は additive field 追加に留め、既存 field を rename しない。
- report 証跡:
  - output contract evidence、TDD evidence、Closure Coverage。
- step closure contract:
  - tc-010 が pass し、JSON/text/help の output evidence が report に記録されること。
- step gate / commit:
  - step reviewer gate: code-reviewer、範囲は presentation / command help / output tests。
  - commit/no-op gate: S05 の output surface のみを commit boundary にする。
- amendment trigger:
  - output field を additive にできない、または text output で diagnostic を省略する必要が出た場合。
- 委任契約:
  - delegated role: dev-coder
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`
  - allowed paths: presentation、command argument help、parser help、focused tests
  - forbidden changes: application behavior、docs
  - acceptance / closure: tc-010 が pass し、JSON/text/help output evidence が report に記録される。
  - required tests or verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - output required: changed files、output samples or assertions、Red/Green result、closure id status、report evidence note、unresolved compatibility risks。
  - reviewer focus: code-reviewer
  - stop condition: JSON compatibility を破壊する必要が出る。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）

- 対象:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `spec-dock/docs/reference_worktree.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md` / `spec-dock/docs/guide.md` は stale wording が見つかった場合のみ。
- 対応:
  - `worktree create` は `SPEC_DOCK_WORKTREE_ROOT` 必須と明記する。
  - `list` / `show` / `remove` は root optional で Git records 正本と明記する。
  - classification diagnostics と `managed` compatibility を説明する。
  - external remove、Git-first behavior、target-only cleanup、branch non-deletion を説明する。
  - prune/repair、orphan cleanup、Codex Desktop-specific lifecycle は scope 外と明記する。
- stale wording scan:
  - `list/show/remove require root`
  - `remove targets only managed namespace`
  - `unmanaged is non-bypassable blocker`
  - cleanup is only directory-tree cleanup
- doc update owner:
  - doc-writer
- 委任契約:
  - delegated role: doc-writer
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`
  - allowed paths: `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`, `spec-dock/docs/reference_worktree.md`, guide docs only when stale wording is found
  - forbidden changes: runtime code、tests、canonical issue/epic docs、unrelated docs sections
  - acceptance / closure: tc-011 が inspect evidence と spec-reviewer pass で閉じる。
  - required tests or docs-only verification: stale wording `rg` scan、provider/dogfooding parity inspection、docs diff review。
  - output required: changed docs、stale wording scan result、parity inspection result、report evidence note、unresolved docs risks。
  - reviewer focus: spec-reviewer
  - stop condition: docs 更新に requirement/design と異なる user-visible contract が必要になる。
- Red / 代替証跡の要件:
  - `inspect-only`: stale wording scan を実装前に実行し、見つかった stale statement を report の docs evidence に記録する。
  - code test を置かない理由: docs-only contract であり、runtime behavior は S01..S05 tests が閉じる。
- 具体検査ケース:
  - `tc-s90-001` docs inspect: provider docs stale wording
    - 前提: provider `reference_worktree.md` を対象にする。
    - 操作: root-required / managed-only / unmanaged blocker / directory-only cleanup の stale wording を検索する。
    - 期待結果: stale wording がなく、新 contract が説明されている。
    - 失敗検出: `list/show/remove require root`、`unmanaged cannot be removed`、cleanup directory-only 記述が残る。
    - 検証方法: `rg` inspection と docs diff review。
    - 関連 closure id: tc-011
  - `tc-s90-002` docs inspect: dogfooding parity
    - 前提: provider docs と dogfooding `spec-dock/docs/reference_worktree.md` を対象にする。
    - 操作: user-visible contract の対応箇所を比較する。
    - 期待結果: root optional list/show/remove、create root-required、classification diagnostics、external remove、target-only cleanup、branch non-deletion が一致する。
    - 失敗検出: provider / dogfooding 片方だけ更新される。
    - 検証方法: docs diff inspection。
    - 関連 closure id: tc-011
  - `tc-s90-003` docs inspect: non-scope guardrails
    - 前提: updated docs を対象にする。
    - 操作: branch deletion / prune / repair / orphan cleanup / Codex Desktop lifecycle の記述を確認する。
    - 期待結果: branch deletion はしない、prune/repair/orphan cleanup/Codex lifecycle は scope 外と明記されている。
    - 失敗検出: Codex-specific lifecycle 実装を示唆する、または branch deletion を約束する。
    - 検証方法: docs inspection。
    - 関連 closure id: tc-011
- Refactor / cleanup ガードレール:
  - `reference_worktree.md` の該当 contract に限定し、guide は stale wording が見つかった場合だけ更新する。
- step closure contract:
  - tc-011 の inspect evidence と spec-reviewer pass が report に記録されること。
- step gate / commit:
  - step reviewer gate: spec-reviewer、範囲は docs/spec alignment。
  - commit/no-op gate: docs impact resolution のみを commit boundary にする。
- amendment trigger:
  - docs 更新中に requirement/design と異なる user-visible contract が必要と判明した場合。
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残っていない。
- closure ids:
  - tc-011

### 最終品質ゲートステップ S99（final quality gate）

- branch diff 範囲:
  - issue-wide runtime / tests / docs / report evidence。
- 必須 validation:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
  - `python -m unittest discover -v`。実行不能または過大な場合は targeted-only rationale を report に記録する。
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync` の要否を判断し、実施または no-op rationale を report に記録する。
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: closure coverage と integration test 要否
  - pass 条件: `review_status: pass`
- final code review gate:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff、layering、filesystem safety、Git semantics、compatibility
  - pass 条件: `review_status: pass`
- final spec review gate:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / docs / implementation alignment
  - pass 条件: `review_status: pass`
- final commit gate:
  - commit 範囲: S01..S99 の completed closure と report evidence。
  - final report ledger: all closure ids pass / approved-no-op。
  - post-commit external evidence destination: final response / PR / issue comment。
- closure ids:
  - tc-012
- 委任契約:
  - delegated role: N/A for implementation worker; review roles are qa-reviewer, code-reviewer, spec-reviewer
  - input docs: `requirement.md`, `design.md`, `plan.md`, `report.md`, final diff
  - allowed paths: report evidence updates by main orchestrator only
  - forbidden changes: product/runtime/docs changes during final gate unless a reviewer finding opens a bounded follow-up step
  - acceptance / closure: tc-012 が final coverage、validation、fresh reviewer pass で閉じる。
  - required tests or verification: targeted worktree unittest、full unittest or rationale、`spec-dock validate`、sync decision、fresh final reviewers。
  - output required: command results、closure coverage status、reviewer outputs、final risk list、commit/no-op evidence。
  - reviewer focus: qa coverage、issue-wide code layering/safety、spec alignment
  - stop condition: missing closure evidence、failed validation、fresh reviewer fail。
- Red / 代替証跡の要件:
  - `manual-required`: final gate は実装完了後の観測証跡で閉じるため、pre-implementation red は不要。代わりに closure coverage table の空欄が fail condition であることを固定する。
- 具体検証ケース:
  - `tc-s99-001` final coverage: closure ledger completeness
    - 前提: S01..S05/S90 が完了している。
    - 操作: report の Step Contract Closure / Test Contract Closure / Closure Coverage を確認する。
    - 期待結果: tc-001..tc-012 が pass / approved-no-op で閉じ、unresolved Closure Delta がない。
    - 失敗検出: 必須 closure id の missing evidence、failed/unreviewed/provisional gate。
    - 検証方法: report inspection。
    - 関連 closure id: tc-012
  - `tc-s99-002` final validation: commands
    - 前提: implementation/docs/report が統合済み。
    - 操作: targeted tests、full unittest または rationale、`spec-dock validate`、sync decision を実行/記録する。
    - 期待結果: 必須 commands が pass、または targeted-only/sync no-op rationale が report にある。
    - 失敗検出: 未実行なのに pass 記録、validate failure、sync 必要性未判断。
    - 検証方法: command output と report evidence。
    - 関連 closure id: tc-012
  - `tc-s99-003` final reviewers: fresh pass
    - 前提: final diff が固定されている。
    - 操作: qa-reviewer、code-reviewer、spec-reviewer を fresh に実行する。
    - 期待結果: すべて `review_status: pass`。unavailable/denied/provisional/waived は pass として扱わない。
    - 失敗検出: reviewer finding 未解決、stale reviewer result。
    - 検証方法: reviewer outputs と report gate。
    - 関連 closure id: tc-012
- Refactor / cleanup ガードレール:
  - final gate 中に product diff を増やさない。finding が出た場合は bounded follow-up step と re-review を行う。
- step closure contract:
  - tc-012 が final report ledger、validation、reviewer gates で閉じていること。
- step gate / commit:
  - final QA gate: qa-reviewer pass。
  - final code review gate: code-reviewer pass。
  - final spec review gate: spec-reviewer pass。
  - final commit/no-op gate: report evidence と final diff scope を確認し、post-commit clean check を記録する。
- amendment trigger:
  - final reviewers が missing closure / design gap / unplanned behavior slice を指摘した場合。

## 未確定事項

- なし。
  - locked worktree の Git force semantics は Git に従う実装詳細であり、SpecDock hard blockers を弱める未確定事項ではない。
  - unsupported file type / race cleanup は fake filesystem gateway を使う test strategy で閉じてよい。

## 最終完了条件

- AC/EC 達成:
  - tc-001..tc-012 が report の Closure Coverage で pass / approved-no-op として閉じている。
- docs 影響解決:
  - provider docs と dogfooding docs が新 contract と一致している。
- 全 implementation step 完了:
  - S01..S05 / S90 が committed / approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
  - `./spec-dock/scripts/spec-dock validate`: pass
