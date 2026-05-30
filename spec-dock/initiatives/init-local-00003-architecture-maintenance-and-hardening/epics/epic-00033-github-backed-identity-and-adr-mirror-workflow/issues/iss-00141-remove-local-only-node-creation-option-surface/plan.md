---
種別: 実装計画書（Issue）
ID: "iss-00141"
タイトル: "Remove Local Only Node Creation Option Surface"
関連GitHub: ["#141"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00141 Remove Local Only Node Creation Option Surface — 実装計画（実行契約 / Execution Contract）

> `plan.md` は planned executable workflow contract です。実行結果、逸脱、発見された tests、reviewer verdict、commit/no-op evidence は `report.md` に記録する。

## この計画で満たす要件ID
- AC:
  - AC-001: node creation help から `--no-github` を消し、GitHub create/link option は維持する。
  - AC-002: explicit `new initiative|epic|issue --no-github` は parser-level unsupported option として失敗する。
  - AC-003: node creation の `no_github` / `local_only` internal plumbing を削除する。
  - AC-004: docs / skills / tests から node creation `--no-github` compatibility wording と dedicated rejection expectation を削除する。
  - AC-005: provider runtime/docs と checked-in dogfooding mirror の contract を揃える。
- EC:
  - EC-001: `--create-github-issue --no-github` は mutually exclusive error ではなく unsupported option として失敗する。
  - EC-002: `sync` / `deps check` / `active set` の cache/local `--no-github` は維持する。
  - EC-003: docs に残る `--no-github` は state/cache context のみ許容する。
- 制約:
  - GitHub mandatory node linkage と accepted ADR を変更しない。
  - local-only node data の migration / cleanup は行わない。
  - `--no-github` という文字列の全削除を目的にしない。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の依存関係分析、module dependency diagram、ディレクトリ / ファイル変更計画。
- 順序ルール:
  - parser / request contract / planning branch の runtime contract を先に閉じる。
  - runtime contract が固まった後に docs / scaffold wording と expectation tests を更新する。
  - 最後に issue-wide final quality gate で runtime、docs、mirror、report の整合を確認する。
- step 依存サマリー:
  - S01:
    - 依存: approved `requirement.md`、approved `design.md`。
    - unblock: node creation CLI と internal contract の実装完了。
    - 対象ファイル: runtime provider/mirror、runtime CLI tests。
  - S90:
    - 依存: S01 runtime contract cleanup。
    - unblock: docs/scaffold wording と wrapper/init expectation の整合。
    - 対象ファイル: docs、README、scripts README、docs/scaffold tests。
  - S99:
    - 依存: S01、S90 の step review / commit gate。
    - unblock: issue execution completion readiness。
    - 対象ファイル: issue-wide diff、report ledger。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: node creation `--no-github` が CLI surface と internal contract から消える。
  - 依存: approved requirement/design。
  - unblock: docs/scaffold wording の確定。
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
    - matching files under `spec-dock/scripts/spec_dock_runtime/`
    - `tests/cli_runtime/test_new.py`
  - 閉じる要件: AC-001、AC-002、AC-003、AC-005、EC-001。
  - レビューゲート: code-reviewer。
- S90:
  - 観測可能な振る舞い: docs / scaffold tests が node creation `--no-github` compatibility path を説明しない。
  - 依存: S01。
  - unblock: final quality gate。
  - 対象ファイル:
    - `README.md`
    - `src/spec_dock/assets/spec_dock/docs/`
    - `src/spec_dock/assets/spec_dock/scripts/README.md`
    - `spec-dock/docs/`
    - `tests/cli_runtime/test_wrappers.py`
    - `tests/test_init_update.py` if scaffold expectation changes are required.
  - 閉じる要件: AC-004、AC-005、EC-002、EC-003。
  - レビューゲート: spec-reviewer for docs/spec alignment; code-reviewer if tests/scaffold behavior expectations change.
- S99:
  - 観測可能な振る舞い: issue-wide implementation が requirement/design/plan/report と整合し、必須 review gate を通過する。
  - 依存: S01、S90。
  - unblock: issue execution handoff completion readiness。
  - 対象ファイル: issue-wide diff and `report.md` evidence.
  - 閉じる要件: all AC/EC。
  - レビューゲート: qa-reviewer、issue-wide code-reviewer、spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01
- AC-004 -> S90
- AC-005 -> S01, S90
- EC-001 -> S01
- EC-002 -> S90, S99
- EC-003 -> S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

> これは Issue 全体のテスト一覧ではなく、仕様を縮小解釈・後付けテスト・過剰実装しないための coverage ledger です。実際の step-local obligation と concrete seeds は各 implementation step の `具体テストケース一覧` に置く。

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | help surface | acceptance | AC-001 | `new initiative|epic|issue --help` に `--no-github` が出ず、`--create-github-issue` と `--github-issue` は残る | CLI help output | help/docs surface drift | yes | red-required | report Step/Test Contract Closure |
| tc-002 | S01 | parser failure | negative | AC-002 | explicit `--no-github` は parser-level unsupported / unrecognized option で失敗し、dedicated contract error は出ない | `new initiative|epic|issue --no-github ...` stderr/exit code | hidden compatibility option resurrection | yes | red-required | report Step/Test Contract Closure |
| tc-003 | S01 | option conflict | negative | EC-001 | `--create-github-issue --no-github` は mutually exclusive error ではなく unsupported option で失敗する | `new issue --create-github-issue --no-github ...` stderr | stale mutually-exclusive plumbing | yes | red-required | report Step/Test Contract Closure |
| tc-004 | S01 | internal contract | structural | AC-003 | `New*Args.no_github`、node creation `--no-github` registration、dedicated helper、`local_only` node creation mode/planning branch が残らない | source inspection / structural assertion | dead local-only branch retention | yes | inspect-only | report Test Contract Closure with search output |
| tc-005 | S90 | supported non-scope options | regression | EC-002 | `sync` / `deps check` / `active set` の cache/local `--no-github` は valid option として残る | existing tests/help/docs classification | overbroad deletion | yes | covered-existing | report Closure Coverage |
| tc-006 | S90 | docs wording | docs | AC-004, EC-003 | docs/tests/skills に node creation compatibility option としての `--no-github` 説明が残らない | targeted `rg -- "--no-github|local-only|compatibility option|contract error"` classification | stale documentation guidance | yes | inspect-only | report Test Contract Closure |
| tc-007 | S01, S90 | provider/mirror parity | parity | AC-005 | provider assets と checked-in dogfooding mirror が同じ removal contract を持つ | provider/mirror targeted diff or paired inspection | shipped/dogfooding drift | yes | inspect-only | report Closure Coverage |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer: code-reviewer for code/runtime/tests/scaffold behavior; spec-reviewer for docs-only/spec alignment.
  - pass 条件: fresh `review_status: pass`。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: closure coverage、missing high-value tests、integration test 要否。
- CG1 final code review:
  - reviewer: issue-wide code-reviewer。
  - 範囲: integrated diff、責務境界、回帰リスク、保守性。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。

## 実行ルール（全ステップ共通）
- 各 implementation step は `1 behavior slice / 1 review scope / 1 commit boundary` として扱う。
- observed result は `report.md` に記録し、`plan.md` へ戻さない。
- implementation 中に hidden compatibility option、state/cache `--no-github` 変更、local-only data migration、GitHub create/link redesign、closure row の required/expectation/spec link 変更が必要になった場合は plan amendment と fresh spec review を先に行う。
- サブエージェント worker は `Ledger Note` または `No material implementation decisions beyond the approved plan.` を返す。orchestrator は accepted decision として直採用せず `report.md` で採否を判断する。

## 実装ステップ

### 実装ステップ S01 — Runtime Contract Cleanup
- 振る舞いの目標（behavior goal）:
  - `new initiative` / `new epic` / `new issue` の `--no-github` を parser/help/internal request/planning から削除し、explicit 指定を parser-level unsupported option にする。
- design 参照:
  - `インターフェース契約`
  - `クラス / インターフェース詳細設計`
  - `ディレクトリ / ファイル変更計画`
- 依存:
  - approved `requirement.md`
  - approved `design.md`
- unblock:
  - S90 docs/scaffold refresh
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - matching files under `spec-dock/scripts/spec_dock_runtime/`
  - `tests/cli_runtime/test_new.py`
- 計画済み契約（planned contract）:
  - scope:
    - `--no-github` argument registration、args dataclass field、args factory plumbing、handler branch、dedicated helper、`local_only` request/planning branch を node creation から削除する。
    - provider runtime と dogfooding runtime mirror を同じ runtime contract に揃える。
    - `app.py` の stale node creation local-only wording を修正する。
  - テスト義務（test obligation）:
    - closure id:
      - tc-001
      - tc-002
      - tc-003
      - tc-004
      - tc-007
    - coverage rationale:
      - public CLI behavior、negative parser path、internal contract cleanup、provider/mirror parity が changed contract であり、accepted ADR の回帰防止に必要。
  - Red / 代替証跡の要件:
    - red-required:
      - `tests/cli_runtime/test_new.py` で help absence と parser-level unsupported option を実装前に失敗する expectation として固定する。
      - 既存 dedicated contract error test は、parser unsupported expectation へ置き換えた直後に red になることを確認する。
    - inspect-only:
      - `rg` / source inspection で node creation `no_github` / `local_only` plumbing の不在を確認する。
  - 実装範囲（implementation scope）:
    - allowed paths:
      - listed target files only.
    - forbidden changes:
      - `sync` / `deps check` / `active set` の `--no-github` 削除。
      - local-only node data migration / cleanup。
      - GitHub create/link-existing behavior redesign。
      - docs wording updates outside `app.py` docstring; those are S90.
  - Green 検証:
    - command / inspection:
      - `python -m unittest tests.cli_runtime.test_new -v`
      - targeted source search for `no_github`, `--no-github`, `local_only`, and `Cannot combine` across S01 target files with allowed-hit classification.
  - Refactor / cleanup ガードレール:
    - 目的: `--no-github` removal で orphan になった helper/import/type branch のみ削除する。
    - 禁止する広がり: command architecture、GitHub create/link behavior、validation/import/sync logic の再設計。
  - closure 証跡要件:
    - Step Contract Closure: tc-001, tc-002, tc-003, tc-004, tc-007.
    - Test Contract Closure: red / green / inspection result.
    - Closure Coverage: provider/mirror parity evidence.
  - report 証跡の記録先:
    - `report.md` の TDD / Red / Green / Refactor Evidence、Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger（plan amendment が必要になる契機）:
    - hidden `--no-github` compatibility option を残す必要が判明する。
    - `CreateNodeRequest.github_mode` の default semantics 変更が必要になる。
    - state/cache `--no-github` の挙動変更が必要になる。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 入力 docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - current target files listed above.
- 許可 paths:
  - S01 target files only.
- 禁止 changes:
  - S90 docs files, unless only `app.py` runtime docstring wording is changed.
  - non-scope command `--no-github` behavior.
  - migrations, GitHub live behavior redesign, unrelated cleanup.
- 受け入れ条件:
  - tc-001 から tc-004、tc-007 の close condition を満たす。
- 必須 tests または docs-only verification:
  - `python -m unittest tests.cli_runtime.test_new -v`
  - targeted source inspection command with allowed-hit classification.
- reviewer focus:
  - code-reviewer: parser behavior、application contract narrowing、provider/mirror parity、test sensitivity。
- 必須出力（output required）:
  - changed files
  - red / green verification result
  - source inspection result
  - unresolved risks
  - `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- 停止条件（stop conditions）:
  - requirement/design conflict.
  - allowed paths 外の変更が必要。
  - parser-level unsupported option を満たせない。
  - cache/local `--no-github` 保護に触れる必要がある。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: node creation help から `--no-github` を消す
  - 前提: runtime tests can invoke `new initiative --help`, `new epic --help`, and `new issue --help`.
  - 操作: 各 help output を取得する。
  - 期待結果: `--no-github` は含まれず、`--create-github-issue` と `--github-issue` は含まれる。
  - 失敗検出: parser registration が残って help に表示される回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_new.py` に red-first test を追加または既存 test を更新し、`python -m unittest tests.cli_runtime.test_new -v` を実行する。
  - 関連 closure id: tc-001

- `tc-s01-002` negative: explicit `--no-github` は parser-level unsupported option として失敗する
  - 前提: fake `gh` が呼ばれると検出できる fixture を使う。
  - 操作: `new initiative --no-github --title "Example"`、`new epic --no-github --initiative init-local-00003 --title "Example"`、`new issue --no-github --epic epic-00033 --title "Example"` を実行する。
  - 期待結果: exit code は parser error 相当で、stderr は unsupported / unrecognized option を示し、dedicated contract error は出ず、fake `gh` は呼ばれない。
  - 失敗検出: hidden option または handler-level rejection branch が残る回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_new.py` の negative tests。
  - 関連 closure id: tc-002

- `tc-s01-003` negative: `--create-github-issue --no-github` は mutually exclusive error にならない
  - 前提: `new issue` に valid parent epic fixture がある。
  - 操作: `new issue --create-github-issue --no-github --epic epic-00033 --title "Example"` を実行する。
  - 期待結果: `--no-github` の unsupported / unrecognized option error で失敗し、mutually exclusive group error ではない。
  - 失敗検出: `--no-github` が mutually exclusive group に残る回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_new.py` の parser error test。
  - 関連 closure id: tc-003

- `tc-s01-004` inspect-only: internal `no_github` / `local_only` plumbing を削除する
  - テスト不要理由: private function / source shape の全てを brittle test に固定しないため、public behavior tests と source inspection を組み合わせる。
  - 代替検証方法: S01 target files に対して `rg -n -- "no_github|--no-github|local_only|Cannot combine"` を実行し、node creation plumbing の残存がないことを分類する。
  - 期待結果: node creation `no_github` field/registration/branch/helper と `local_only` request/planning branch が残らない。
  - 記録先: `report.md` Test Contract Closure and Closure Coverage。
  - 関連 closure id: tc-004

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-001
  - tc-002
  - tc-003
  - tc-004
  - tc-007
- close 条件:
  - public parser/help tests pass。
  - internal cleanup inspection pass。
  - provider/mirror runtime target files are aligned。
  - code-reviewer returns fresh pass。
- 検証 evidence:
  - `python -m unittest tests.cli_runtime.test_new -v`
  - targeted source inspection command and classification.
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Closure Delta if any closure condition changes.
- 残リスク:
  - `--no-github` string is allowed outside node creation and must be classified by command context.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S01 target files and tests.
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し fresh code-reviewer pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 target files and S01 report evidence.
  - no-op の場合: not expected; if no-op, report must justify why runtime contract already satisfies all S01 closures.

### ドキュメント影響の解消ステップ S90 — Docs And Scaffold Refresh
- 振る舞いの目標（behavior goal）:
  - docs / wrapper expectations / scaffold expectations から node creation `--no-github` compatibility wording を削除し、state/cache `--no-github` は維持する。
- design 参照:
  - `ディレクトリ / ファイル変更計画`
  - `テスト戦略`
  - `要件 / 例外 -> 検証マッピング`
- 依存:
  - S01 completed and committed.
- unblock:
  - S99 final quality gate.
- 対象ファイル:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `src/spec_dock/assets/spec_dock/docs/github.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow-tree.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/scripts/README.md`
  - matching docs under `spec-dock/docs/`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/test_init_update.py` if scaffold expectation changes are required.
- 計画済み契約（planned contract）:
  - scope:
    - node creation `--no-github` compatibility option / dedicated rejection wording を削除または GitHub-backed create/link-existing wording に置換する。
    - docs/tests に残る `--no-github` を command context で分類する。
  - テスト義務（test obligation）:
    - closure id:
      - tc-005
      - tc-006
      - tc-007
    - coverage rationale:
      - docs と shipped scaffold は future maintainer と agent の実行 surface であり、stale compatibility wording は issue の主目的を壊す。
  - Red / 代替証跡の要件:
    - covered-existing:
      - existing wrapper/init tests that assert docs content are updated to fail before docs change and pass after.
    - inspect-only:
      - targeted `rg` classification for `--no-github`, `local-only`, `compatibility option`, `contract error`.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - S90 target files.
    - forbidden changes:
      - runtime code changes from S01.
      - supported state/cache `--no-github` docs/tests removal.
      - workflow policy redesign unrelated to node creation.
  - Green 検証:
    - command / inspection:
      - `python -m unittest tests.cli_runtime.test_wrappers -v`
      - `python -m unittest tests.test_init_update -v` when scaffold expectations are touched.
      - targeted docs/search classification.
  - Refactor / cleanup ガードレール:
    - 目的: stale wording と直接関係する docs/tests expectation のみ整える。
    - 禁止する広がり: docs architecture rewrite、workflow redesign、unrelated wording cleanup。
  - closure 証跡要件:
    - Step Contract Closure: tc-005, tc-006, tc-007.
    - Test Contract Closure: docs/search classification and affected tests.
    - Closure Coverage: allowed remaining `--no-github` contexts.
  - report 証跡の記録先:
    - `report.md` の Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger（plan amendment が必要になる契機）:
    - docs が node creation local-only recovery path を必要とする。
    - `sync` / `deps check` / `active set` の option semantics を変更する必要がある。
    - docs-only ではなく runtime/scaffold behavior の追加変更が必要になる。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - doc-writer
- 入力 docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - S90 target docs/tests.
- 許可 paths:
  - S90 target files only.
- 禁止 changes:
  - runtime source changes.
  - cache/local `--no-github` docs/tests removal.
  - unrelated docs reorganization.
- 受け入れ条件:
  - tc-005、tc-006、tc-007 の close condition を満たす。
- 必須 tests または docs-only verification:
  - `python -m unittest tests.cli_runtime.test_wrappers -v`
  - `python -m unittest tests.test_init_update -v` if touched.
  - targeted docs/search classification.
- reviewer focus:
  - spec-reviewer: docs/spec alignment。
  - code-reviewer: tests/scaffold behavior expectations are changed.
- 必須出力（output required）:
  - changed files
  - docs/search classification
  - test result
  - unresolved risks
  - `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- 停止条件（stop conditions）:
  - S01 not completed.
  - supported state/cache `--no-github` wording cannot be preserved.
  - allowed paths 外の docs/skill/workflow change が必要。

#### 具体テストケース一覧

- `tc-s90-001` inspect-only: node creation `--no-github` compatibility wording を削除する
  - テスト不要理由: docs wording は targeted search と affected wrapper/init tests で検出する方が brittleness を抑えられる。
  - 代替検証方法: target docs/tests に対して `rg -n -- "--no-github|local-only|compatibility option|contract error"` を実行し、node creation compatibility wording がないことを分類する。
  - 期待結果: `new initiative|epic|issue` の `--no-github` compatibility option / dedicated rejection 説明が残らない。
  - 記録先: `report.md` Test Contract Closure。
  - 関連 closure id: tc-006

- `tc-s90-002` regression: state/cache command の `--no-github` を維持する
  - 前提: docs/tests contain valid `sync` / `deps check` / `active set` cache/local contexts.
  - 操作: targeted tests and search classification を実行する。
  - 期待結果: state/cache command の `--no-github` は docs/tests で維持され、node creation wording と混同されない。
  - 失敗検出: `--no-github` の全削除や context 誤分類を検出する。
  - 検証方法: `python -m unittest tests.cli_runtime.test_wrappers -v` and targeted search classification.
  - 関連 closure id: tc-005

- `tc-s90-003` parity: provider docs と dogfooding docs を揃える
  - テスト不要理由: docs mirror の文面差分は paired inspection が適している。
  - 代替検証方法: provider docs と `spec-dock/docs/` の対応箇所を確認し、same contract wording に揃っていることを記録する。
  - 期待結果: shipped provider docs and checked-in dogfooding docs both describe GitHub-backed create/link-existing paths without node creation `--no-github`.
  - 記録先: `report.md` Closure Coverage。
  - 関連 closure id: tc-007

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-005
  - tc-006
  - tc-007
- close 条件:
  - affected docs/tests pass or approved inspect-only evidence exists。
  - allowed remaining `--no-github` hits are state/cache context only。
  - spec-reviewer docs/spec alignment pass。
  - code-reviewer pass if test/scaffold behavior expectations changed。
- 検証 evidence:
  - `python -m unittest tests.cli_runtime.test_wrappers -v`
  - `python -m unittest tests.test_init_update -v` if touched.
  - targeted `rg` classification.
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Closure Delta if any closure condition changes.
- 残リスク:
  - repo-wide `--no-github` hits are valid when state/cache context is documented and classified.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: spec-reviewer, plus code-reviewer when tests/scaffold behavior changed.
  - review 範囲: S90 target docs/tests.
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し fresh reviewer pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S90 target files and S90 report evidence.
  - no-op の場合: only allowed if inspection proves docs/scaffold already satisfy tc-005 to tc-007 and reviewer agrees.

### 最終品質ゲートステップ S99 — Final Quality Gate
- 振る舞いの目標（behavior goal）:
  - Issue 全体の runtime/docs/tests/report evidence が approved requirement/design/plan と一致し、実装完了へ渡せる。
- design 参照:
  - 全体。
- 依存:
  - S01 committed or approved-no-op.
  - S90 committed or approved-no-op.
- unblock:
  - issue execution completion readiness.
- 対象ファイル:
  - issue-wide diff
  - `spec-dock/active/issue/report.md`
- 計画済み契約（planned contract）:
  - scope:
    - final verification commands、closure coverage、final reviewer gates、report evidence completion。
  - テスト義務（test obligation）:
    - closure id:
      - tc-001 through tc-007
    - coverage rationale:
      - step-local evidence を issue-wide に束ね、overbroad `--no-github` removal と stale docs/runtime drift を最終確認する。
  - Red / 代替証跡の要件:
    - covered-existing:
      - S01/S90 の red/green evidence and targeted tests.
    - inspect-only:
      - final search classification and spec/report alignment review.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `report.md` final gate evidence updates.
    - forbidden changes:
      - product/runtime/docs changes except reviewer-directed fixes that go back through S01 or S90 closure.
  - Green 検証:
    - command / inspection:
      - `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_wrappers -v`
      - `python -m unittest tests.test_init_update -v` if touched.
      - `python -m unittest discover -v` if S01/S90 changes remain broad after targeted tests.
      - `./spec-dock/scripts/spec-dock validate`
      - `git diff --check`
  - Refactor / cleanup ガードレール:
    - 目的: final reviewer finding に対応する最小修正だけを S01/S90 に戻して行う。
    - 禁止する広がり: final gate で未承認 requirement/design を追加しない。
  - closure 証跡要件:
    - all required closure ids have Step/Test Contract Closure and Closure Coverage in `report.md`.
  - report 証跡の記録先:
    - `report.md` Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Reviewer Gate Status, Step Commit Gate, Final Commit placeholders/external evidence destination.
  - amendment trigger（plan amendment が必要になる契機）:
    - final reviewer が missing closure、new bug class、or requirement/design mismatch を指摘する。
    - required verification cannot run and no approved alternative evidence exists.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - qa-reviewer
  - code-reviewer
  - spec-reviewer
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
  - issue-wide diff and verification results.
- 許可 paths:
  - read-only review; reviewers do not edit files.
- 禁止 changes:
  - reviewer direct edits.
  - reviewer pass substitution by worker output.
- 受け入れ条件:
  - qa-reviewer, issue-wide code-reviewer, and spec-reviewer all return fresh pass.
- 必須 tests または docs-only verification:
  - final verification command set listed above.
- reviewer focus:
  - qa-reviewer: test sufficiency and integration test need.
  - code-reviewer: integrated diff, responsibility boundary, regression risk.
  - spec-reviewer: requirement/design/plan/report/implementation/docs alignment.
- 必須出力（output required）:
  - reviewer verdicts
  - findings or pass rationale
  - unresolved risks
  - final report evidence update targets.
- 停止条件（stop conditions）:
  - any final reviewer fail.
  - any required closure id lacks evidence.
  - validate/test/check command fails due to issue changes.

#### 具体テストケース一覧

- `tc-s99-001` final coverage: 全 closure id の evidence を束ねる
  - 前提: S01 and S90 step evidence are present in `report.md`.
  - 操作: final verification command set and reviewer gates を実行する。
  - 期待結果: tc-001 through tc-007 が report closure tables で pass または approved-no-op として閉じている。
  - 失敗検出: step-local evidence の抜け、docs/runtime drift、missing high-value test を検出する。
  - 検証方法: final QA/code/spec reviewer pass and final report inspection.
  - 関連 closure id: tc-001, tc-002, tc-003, tc-004, tc-005, tc-006, tc-007

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-001
  - tc-002
  - tc-003
  - tc-004
  - tc-005
  - tc-006
  - tc-007
- close 条件:
  - final verification commands pass or approved alternatives are recorded.
  - final qa-reviewer, code-reviewer, spec-reviewer pass.
  - report ledger records closure coverage and reviewer gate status.
- 検証 evidence:
  - final command outputs and reviewer outputs.
- report evidence:
  - Final QA Gate
  - Final Code Review Gate
  - Final Spec Review Gate
  - Closure Coverage
  - Reviewer Gate Status
- 残リスク:
  - external GitHub live behavior is unchanged and should not be inferred beyond existing tests.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: qa-reviewer, issue-wide code-reviewer, spec-reviewer.
  - review 範囲: issue-wide diff and report evidence.
  - pass 条件: all three fresh pass.
  - re-review rule: 指摘は該当 step に戻して修正し、fresh review を再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: final report ledger and any reviewer-directed final fixes.
  - no-op の場合: only if final gate makes no diff and report already contains complete evidence.

## 未確定事項
- なし:
  - Option A parser-level removal と internal cleanup scope は requirement phase で確定済み。
  - `app.py` stale wording は design phase で implementation surface として確定済み。

## 最終完了条件
- AC/EC 達成:
  - tc-001 through tc-007 が report closure tables で pass または正当な approved-no-op として閉じている。
- docs 影響解決:
  - S90 が committed または reviewer-approved no-op として閉じている。
- 全 implementation step 完了:
  - S01、S90、S99 が committed または正当な approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final verification:
  - required tests / validate / diff check results are recorded in `report.md`.
- handoff:
  - `report.md` has Spec Authoring Gate plan pass evidence before execution handoff.
