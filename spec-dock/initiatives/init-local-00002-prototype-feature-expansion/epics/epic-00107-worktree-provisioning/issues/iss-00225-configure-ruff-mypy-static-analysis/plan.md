---
種別: 実装計画書（Issue）
ID: "iss-00225"
タイトル: "Configure Ruff And Mypy Static Analysis Cleanup"
関連GitHub: ["#225"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00107", "init-local-00002"]
---

# iss-00225 Configure Ruff And Mypy Static Analysis Cleanup — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001 Static analysis dependency and config
  - AC-002 Target boundary
  - AC-003 Local one-command entrypoint
  - AC-004 CI enforcement
  - AC-005 Fine-grained Ruff adoption
  - AC-006 Mypy adoption
  - AC-007 Format isolation
  - AC-008 Final green baseline
  - AC-009 No hidden broad suppression
- EC:
  - EC-001 大量違反
  - EC-002 過大修正を要求する rule
  - EC-003 untyped external dependency
  - EC-004 package/path 解決 noise
  - EC-005 formatter churn
  - EC-006 dogfooding generated-copy drift
- 制約:
  - dogfooding `spec-dock/` は直接 target にしない。
  - pre-commit は実装しない。
  - 各検査項目は小刻みに追加し、違反を 0 件化してから次へ進む。

## 依存関係から導く実装順序
- 順序ルール:
  - 先に dependency / command surface を作る。
  - Ruff は rule group を一つずつ追加する。
  - 各 rule step は `run -> inventory -> fix -> zero confirmation -> report` で閉じる。
  - mypy は Ruff の semantic lint step が閉じた後に導入する。
  - Ruff format は semantic / type fix と混ぜず、独立 step とする。
  - CI wiring は local `make lint` が成立してから入れる。
- 共通 target:
  - command target: `src/spec_dock tests`
  - coverage note: shipped runtime asset `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` is covered through `src/spec_dock`
  - excluded direct target: `spec-dock/`

## ステップ一覧
| Step | 内容 | 閉じる要件 | 主な検証 |
|---|---|---|---|
| S01 | Dependency / config skeleton / local command skeleton | AC-001, AC-002, AC-003 | `make lint` skeleton inspection |
| S02 | Ruff `F` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F src/spec_dock tests` |
| S03 | Ruff `E` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E src/spec_dock tests` |
| S04 | Ruff `I` と isort settings を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I src/spec_dock tests` |
| S05 | Ruff `UP` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I,UP src/spec_dock tests` |
| S06 | Ruff `B` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I,UP,B src/spec_dock tests` |
| S07 | Ruff `C4` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I,UP,B,C4 src/spec_dock tests` |
| S08 | Ruff `SIM` と `SIM108` ignore を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I,UP,B,C4,SIM src/spec_dock tests` |
| S09 | Ruff `PTH` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH src/spec_dock tests` |
| S10 | Ruff `TC` を追加して違反 0 件化 | AC-005 | `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC src/spec_dock tests` |
| S11 | Ruff `ARG` と tests per-file ignore を追加して違反 0 件化 | AC-005, AC-009 | `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG src/spec_dock tests` |
| S12 | Ruff `RUF` と必要最小 ignore を追加して違反 0 件化 | AC-005, AC-009 | `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG,RUF src/spec_dock tests` |
| S13 | Ruff `TID` と relative import ban を追加して違反 0 件化 | AC-005, AC-009 | `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG,RUF,TID src/spec_dock tests` |
| S14 | mypy dependency / base config / command を追加して error inventory を作る | AC-006 | `uv run mypy src/spec_dock tests` |
| S15 | mypy errors を 0 件化し、必要な targeted config を確定する | AC-006, AC-009 | `uv run mypy src/spec_dock tests` |
| S16 | Ruff format config を追加し format-only 差分を閉じる | AC-007 | `uv run ruff format --check src/spec_dock tests` |
| S17 | `make lint` を最終 gate に更新し、local all-in-one を green にする | AC-003, AC-008 | `make lint` |
| S18 | provider CI に `make lint` を追加する | AC-004 | workflow inspection / CI result |
| S90 | docs / dogfooding impact resolution | AC-008, EC-006 | docs and dogfooding inspection |
| S99 | final quality gate | AC-008, AC-009 | `make lint`, `uv run pytest`, `spec-dock validate` |

## 要件 ↔ ステップ対応
- AC-001 -> S01, S14
- AC-002 -> S01, S17
- AC-003 -> S01, S17
- AC-004 -> S18
- AC-005 -> S02-S13
- AC-006 -> S14-S15
- AC-007 -> S16
- AC-008 -> S17-S99
- AC-009 -> S08, S11, S12, S13, S15, S99
- EC-001 -> S02-S15
- EC-002 -> all implementation steps as amendment trigger
- EC-003 -> S14-S15
- EC-004 -> S14-S15
- EC-005 -> S16
- EC-006 -> S90-S99

## 仕様固定クロージャ索引
| ID | Step | 種別 | 仕様リンク | 固定する期待値 | 防ぐ bug class | 必須 | 証跡レベル |
|---|---|---|---|---|---|---|---|
| tc-s01-001 | S01 | acceptance | AC-001/002/003 | dependency/config skeleton と local command skeleton が存在する | command absence / target drift | yes | inspect-only |
| tc-s02-001 | S02 | acceptance | AC-005 | `F` violation が 0 件 | undefined names / unused imports | yes | command |
| tc-s03-001 | S03 | acceptance | AC-005 | `E` violation が 0 件 | baseline style/syntax hygiene drift | yes | command |
| tc-s04-001 | S04 | acceptance | AC-005 | `I` violation が 0 件 | import order drift | yes | command |
| tc-s05-001 | S05 | acceptance | AC-005 | `UP` violation が 0 件 | outdated Python idioms | yes | command |
| tc-s06-001 | S06 | acceptance | AC-005 | `B` violation が 0 件 | bug-prone patterns | yes | command |
| tc-s07-001 | S07 | acceptance | AC-005 | `C4` violation が 0 件 | redundant comprehensions | yes | command |
| tc-s08-001 | S08 | acceptance | AC-005/009 | `SIM` violation が 0 件、`SIM108` ignore は理由付き | over-simplification / noisy rule adoption | yes | command + inspection |
| tc-s09-001 | S09 | acceptance | AC-005 | `PTH` violation が 0 件 | path handling drift | yes | command |
| tc-s10-001 | S10 | acceptance | AC-005 | `TC` violation が 0 件 | runtime-only/type-only import mixing | yes | command |
| tc-s11-001 | S11 | acceptance | AC-005/009 | `ARG` violation が 0 件、tests ignore は限定的 | unused argument drift / fixture noise | yes | command + inspection |
| tc-s12-001 | S12 | acceptance | AC-005/009 | `RUF` violation が 0 件、ignore は限定的 | Ruff-native bug classes | yes | command + inspection |
| tc-s13-001 | S13 | acceptance | AC-005/009 | `TID` violation が 0 件 | relative import / tidy import drift | yes | command |
| tc-s14-001 | S14 | characterization | AC-006 | mypy initial inventory が report に記録される | hidden typecheck gap | yes | command + report |
| tc-s15-001 | S15 | acceptance | AC-006/009 | mypy error が 0 件 | type errors / broad suppression | yes | command + inspection |
| tc-s16-001 | S16 | acceptance | AC-007 | format check が green、format-only diff が隔離される | formatter churn mixing | yes | command + diff inspection |
| tc-s17-001 | S17 | acceptance | AC-003/008 | `make lint` が final gate を実行し green | local/CI command divergence | yes | command |
| tc-s18-001 | S18 | acceptance | AC-004 | provider CI が `make lint` を実行する。local/pre-PR では workflow inspection、PR/CI 観測可能時は GitHub Actions evidence で閉じる | CI enforcement gap | yes | inspection + CI/PR evidence when available |
| tc-s90-001 | S90 | inspect-only | EC-006 | shipped runtime asset 変更時に dogfooding refresh/inspection 判断が report に残る | stale generated-copy risk | yes | inspection |
| tc-s99-001 | S99 | acceptance | AC-008/009 | final checks がすべて green | incomplete baseline | yes | command |

## レビュー / QA ゲート方針
- 各 implementation step:
  - dev-coder が実装する。
  - code / config / workflow 変更は code-reviewer pass 後に commit する。
  - docs-only の S90 は doc-writer または main authoring scopeで扱い、spec-reviewer で整合を見る。
- Final:
  - qa-reviewer: obligation coverage と test sufficiency。
  - code-reviewer: integrated diff。
  - spec-reviewer: requirement / design / plan / report / implementation 整合。
- 本計画 authoring gate:
  - requirement / design / plan の fresh spec-reviewer pass は `report.md` に記録済み。
  - 実装後の final spec-reviewer pass は S99 で再取得する。

## 実行ルール（全ステップ共通）
- 各 step の前に `git status --short` で unintended change を確認する。
- 各 rule step は次の順に実行する。
  1. 対象 rule を `pyproject.toml` に追加する、または command-level `--select` で暫定実行する。
  2. command を実行し、violation count / representative files / rule codes を `report.md` に inventory 化する。
  3. 違反を修正する。
  4. 同じ command を再実行し 0 件を確認する。
  5. 既存 tests への影響があり得る場合は focused pytest、なければ step command を closure evidence とする。
  6. code-reviewer pass 後に step commit する。
- broad suppression を追加する場合:
  - requirement/design と衝突しないか確認し、理由、範囲、代替案、revisit 条件を `report.md` に記録する。
- plan amendment trigger:
  - public API / data contract / architecture boundary を変えないと rule を満たせない。
  - dogfooding `spec-dock/` の直接修正が必要に見える。
  - pre-commit など scope 外の変更が必要になる。
  - command が環境理由で実行できず、代替検証で acceptance を満たせない。

## 実装ステップ

### S01 — Dependency / Config / Local Command Skeleton
- 目標:
  - Ruff / mypy 導入の土台を作り、target boundary と local entrypoint を固定する。
- 対象ファイル:
  - `pyproject.toml`
  - `scripts/static_analysis/run.sh`
  - `Makefile`
- 実装範囲:
  - dev dependency に `ruff` を追加する。
  - Ruff global settings と exclude を置く。
  - script は最終形の構造を持つが、未導入 phase は placeholder にしない。実行する command だけを含める。
  - `make lint` は script を呼ぶ。
- 禁止:
  - pre-commit 追加。
  - `spec-dock/` direct target。
- 検証:
  - `test -x scripts/static_analysis/run.sh`
  - `uv run ruff --version`
  - `make lint` の command surface inspection。まだ全最終 check が成立しない場合は、実行対象を S01 時点で有効な check に限定する。
  - script target が `src/spec_dock tests` であり、`spec-dock/` direct target を含まないことを inspection する。
- report 証跡:
  - target boundary と dogfooding exclusion の確認。
  - script / Makefile の command contract。

### S02 — Ruff F
- 目標:
  - Pyflakes violation を 0 件にする。
- 対象:
  - `pyproject.toml`
  - `src/spec_dock/**/*.py`
  - `tests/**/*.py`
- 検証:
  - `uv run ruff check --select F src/spec_dock tests`
- report 証跡:
  - `F` violation inventory、修正 summary、0 件確認。

### S03 — Ruff E
- 目標:
  - pycodestyle error violation を 0 件にする。
- 検証:
  - `uv run ruff check --select F,E src/spec_dock tests`
- 注意:
  - `E501` は最終 ignore として扱い、行長だけを理由に fail させない。
- report 証跡:
  - `E` violation inventory と `E501` ignore の確認。

### S04 — Ruff I / Isort
- 目標:
  - import order を Ruff / isort settings で固定する。
- 設定:
  - `I`
  - `force-sort-within-sections = true`
  - `combine-as-imports = true`
- 検証:
  - `uv run ruff check --select F,E,I src/spec_dock tests`
- report 証跡:
  - import reorder の範囲と 0 件確認。

### S05 — Ruff UP
- 目標:
  - Python 3.10+ に合う modernization violation を 0 件にする。
- 検証:
  - `uv run ruff check --select F,E,I,UP src/spec_dock tests`
- 注意:
  - Python 3.10 support を破る書き換えは行わない。
- report 証跡:
  - modernization の種類、behavior-preserving である根拠。

### S06 — Ruff B
- 目標:
  - bugbear violation を 0 件にする。
- 検証:
  - `uv run ruff check --select F,E,I,UP,B src/spec_dock tests`
- 注意:
  - mutable default など behavior bug の可能性がある修正は focused pytest を追加で実行する。
- report 証跡:
  - bug-prone pattern と修正検証。

### S07 — Ruff C4
- 目標:
  - comprehension violation を 0 件にする。
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4 src/spec_dock tests`
- report 証跡:
  - rewrite が behavior-preserving である根拠。

### S08 — Ruff SIM
- 目標:
  - simplify violation を 0 件にする。
- 設定:
  - `SIM`
  - `SIM108` ignore
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4,SIM src/spec_dock tests`
- 注意:
  - 読みやすさを下げる rewrite は避ける。
  - `SIM108` ignore の理由を config comment ではなく report/design evidence に残す。
- report 証跡:
  - `SIM` violation inventory、`SIM108` ignore rationale。

### S09 — Ruff PTH
- 目標:
  - path handling を pathlib-friendly にする。
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH src/spec_dock tests`
- 注意:
  - CLI / filesystem boundary で `str` が必要な箇所は意図を保持する。
- report 証跡:
  - path rewrite の範囲、focused pytest の要否。

### S10 — Ruff TC
- 目標:
  - type-only import を整理する。
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC src/spec_dock tests`
- 注意:
  - runtime import side effect がある module は `TYPE_CHECKING` 移動前に確認する。
- report 証跡:
  - type-only import に移したもの、runtime import として残したもの。

### S11 — Ruff ARG
- 目標:
  - unused argument violation を 0 件にする。
- 設定:
  - `ARG`
  - `tests/**/* = ["ARG"]`
  - `ignore-variadic-names = true`
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG src/spec_dock tests`
- 注意:
  - public interface / callback signature / pytest fixture signature を壊さない。
- report 証跡:
  - tests per-file ignore の必要性、source 側 unused argument 修正。

### S12 — Ruff RUF
- 目標:
  - Ruff-native violation を 0 件にする。
- 設定:
  - `RUF`
  - `RUF010`, `RUF001`, `RUF002`, `RUF003` ignore
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG,RUF src/spec_dock tests`
- 注意:
  - 追加 ignore が必要な場合は broad suppression でないことを reviewer が確認する。
- report 証跡:
  - RUF violation inventory、ignore rationale、0 件確認。

### S13 — Ruff TID
- 目標:
  - tidy import / relative import boundary を固定する。
- 設定:
  - `TID`
  - `ban-relative-imports = "all"`
- 検証:
  - `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG,RUF,TID src/spec_dock tests`
- 注意:
  - import path の変更が package layout と衝突する場合は plan amendment を検討する。
- report 証跡:
  - relative import 修正、import boundary に関する判断。

### S14 — Mypy Base Adoption / Inventory
- 目標:
  - mypy dependency と base config を追加し、初回 error inventory を作成する。
- 対象ファイル:
  - `pyproject.toml`
  - `scripts/static_analysis/run.sh`
- 設定:
  - `python_version = "3.10"`
  - `ignore_missing_imports = true`
  - output readability settings
  - `exclude` に `spec-dock/`, build artifacts, venv を含める。
- 検証:
  - `uv run mypy --version`
  - `uv run mypy src/spec_dock tests`
- close 条件:
  - この step は error 0 件でなくてもよい。inventory 作成と分類を close 条件にする。
- report 証跡:
  - mypy error count、代表 error code、分類、S15 の修正方針。

### S15 — Mypy Error Cleanup
- 目標:
  - mypy error を 0 件にする。
- 設定確定:
  - `allow_redefinition = false`
  - `check_untyped_defs = true`
  - `show_error_codes = true`
  - tests override
- 検証:
  - `uv run mypy src/spec_dock tests`
- 注意:
  - source code の型エラーを ignore で隠さない。
  - 外部 package 型情報不足は EC-003 として targeted config で扱う。
- report 証跡:
  - error category ごとの修正 summary、targeted override / ignore の理由、0 件確認。

### S16 — Ruff Format Isolation
- 目標:
  - format config を確定し、format drift を 0 件にする。
- 対象:
  - `pyproject.toml`
  - `src/spec_dock/**/*.py`
  - `tests/**/*.py`
- 検証:
  - `uv run ruff format --check src/spec_dock tests`
- 実装:
  - 必要なら `uv run ruff format src/spec_dock tests` を実行して format-only diff を作る。
- 禁止:
  - この step で semantic/type fixes を混ぜない。
- report 証跡:
  - format-only diff 確認、format check green。

### S17 — Final Local Gate
- 目標:
  - `make lint` を最終 gate として完成させる。
- 対象:
  - `scripts/static_analysis/run.sh`
  - `Makefile`
- 検証:
  - `make lint`
- close 条件:
  - Ruff check、Ruff format check、mypy がすべて実行され、すべて成功する。
  - 一部 command 失敗時に summary と non-zero exit を返す実装になっている。
- report 証跡:
  - final local gate output summary。

### S18 — Provider CI Static Analysis Gate
- 目標:
  - provider CI に `make lint` を組み込む。
- 対象:
  - `.github/workflows/provider-ci.yml`
- 検証:
  - workflow diff inspection。
  - local/pre-PR closure: workflow YAML が `make lint` を呼ぶことを inspection する。
  - external closure: GitHub Actions / PR observation が可能になった時点で provider CI の static-analysis gate 実行結果を report に追記する。
- close 条件:
  - CI が local と同じ `make lint` entrypoint を使う。
  - PR/CI evidence がまだ観測不能な場合は、AC-004 の外部 evidence を S99 / PR preparation の未観測項目として report に残す。
- report 証跡:
  - workflow change と CI validation。

### S90 — Docs / Dogfooding Impact Resolution
- 目標:
  - 実装により恒久 docs / README / workflow 更新が必要か確認し、shipped runtime asset 変更時の dogfooding impact を閉じる。
- 対象:
  - README / docs / workflow / templates / dogfooding workspace inspection / none
- 判定:
  - `make lint` が新しい標準 entrypoint になるため、README や developer docs に既存コマンド一覧がある場合は更新する。
  - 恒久 docs 更新が必要な場合は doc-writer に委任する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` に変更がある場合は、dogfooding `spec-dock/` copy の refresh 要否を inspection し、実施または非実施の理由を記録する。
- 検証:
  - docs inspection。
  - `git diff --name-only` による shipped runtime asset 差分確認。
  - 必要に応じた `spec-dock update .` 相当の refresh 判断。
- report 証跡:
  - 更新要否、更新した場合の file、更新しない場合の理由。
  - dogfooding refresh/inspection 判断と証跡。

### S99 — Final Quality Gate
- 目標:
  - issue 全体の完了条件を閉じる。
- 必須 validation:
  - `make lint`
  - `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `git status --short`
  - shipped runtime asset 差分がある場合の dogfooding impact evidence inspection
- reviewer gates:
  - qa-reviewer pass
  - issue-wide code-reviewer pass
  - final spec-reviewer pass
- close 条件:
  - AC / EC が report 上で closure されている。
  - static analysis violation が残っていない。
  - broad suppression がない、または targeted suppression の理由が記録されている。
  - unintended staged / unstaged changes がない。

## Step-Local Executable Contracts

この section は `authoring/issue-plan.md` の executable step schema を満たすための step-local contract である。上の `実装ステップ` は実行順と実装内容の読みやすい説明、この section は worker / reviewer / report handoff の契約として扱う。

### 共通契約（S02-S13 Ruff rule step）
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: `requirement.md`, `design.md`, `plan.md`, current `pyproject.toml`, target Python files.
  - allowed paths: `pyproject.toml`, `src/spec_dock/**/*.py`, `tests/**/*.py`, and `report.md` evidence updates through orchestrator integration.
  - forbidden changes: `spec-dock/` direct target 化、pre-commit 実装、unrelated refactor、別 rule step の先行導入、broad suppression。
  - acceptance criteria: target rule command が 0 violation で終了し、inventory と修正 summary が `report.md` に残る。
  - required verification: step-specific `uv run ruff check --select ... src/spec_dock tests`; behavior risk がある場合は focused pytest。
  - reviewer focus: `code-reviewer` for code/config diff; `spec-reviewer` only if plan/design amendment or docs-only decision is introduced.
  - stop conditions: rule が public API / architecture rewrite / dogfooding direct edit / scope外 hook を要求する、または command が環境理由で検証不能。
  - output required: changed files, command result, violation inventory summary, suppression rationale if any, unresolved risks, report evidence note.
- report evidence destination:
  - `report.md` Session Log。
  - `TDD / Red / Green / Refactor Evidence`。
  - `Step Contract Closure`。
  - `Test Contract Closure`。
  - `Closure Coverage`。
- step gate:
  - report evidence update -> targeted command green -> code-reviewer pass -> step commit。

### S01 executable contract
- delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: `pyproject.toml`, `uv.lock`, `scripts/static_analysis/run.sh`, `Makefile`
  - forbidden changes: mypy cleanup, CI workflow, source code cleanup, `spec-dock/` target 化, pre-commit。
  - acceptance criteria: `ruff` resolves, script is executable, `make lint` invokes the script, command target excludes `spec-dock/`.
  - required verification: `test -x scripts/static_analysis/run.sh`; `uv run ruff --version`; Makefile/script inspection; if runnable, S01-scoped `make lint`.
  - reviewer focus: command surface, root safety, target safety, summary/exit-code shape.
  - stop conditions: `uv` cannot resolve Ruff, script requires scope外 environment setup, or direct dogfooding target is needed.
  - output required: changed files, version output, inspection result, unresolved risk.
- 具体テストケース一覧:
  - `tc-s01-case-001` inspect-only: local command skeleton が安全な target を持つ
    - 前提: S01 で `scripts/static_analysis/run.sh` と `Makefile` が追加されている。
    - 操作: `test -x scripts/static_analysis/run.sh`、`uv run ruff --version`、Makefile/script inspection を行う。
    - 期待結果: script は実行可能で、`make lint` は script を呼び、direct command target は `src/spec_dock tests` だけである。
    - 失敗検出: `spec-dock/` direct target、未実行 placeholder、または Ruff が resolve できない状態を検出する。
    - 検証方法: command output と diff inspection。
    - 関連 closure id: `tc-s01-001`
- step closure contract:
  - close 条件: `tc-s01-001` の inspection と Ruff version evidence が pass。`uv.lock` に変更がある場合は Ruff dependency 追加に由来する差分として report に記録される。
  - report evidence destination: Session Log, Step Contract Closure, Test Contract Closure, Closure Coverage。
  - step gate: code-reviewer pass before commit。

### S02-S13 executable contracts
- shared step closure contract:
  - applies to: S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13。
  - close 条件:
    - step-specific Ruff command が exit 0。
    - 対象 rule の violation inventory、修正 summary、0 件確認が `report.md` に記録されている。
    - ignore / suppression / per-file ignore が追加された場合は、範囲と理由が `report.md` に記録され、broad suppression でないことを reviewer が確認している。
    - behavior risk がある修正では focused pytest または代替根拠が `report.md` に記録されている。
  - report evidence destination:
    - Session Log。
    - TDD / Red / Green / Refactor Evidence。
    - Step Contract Closure。
    - Test Contract Closure。
    - Closure Coverage。
    - Closure Delta if the step adds/removes/aliases a closure id。
  - step gate:
    - report evidence update -> step-specific Ruff command green -> optional focused pytest green -> code-reviewer pass -> step commit。
  - commit gate:
    - 1 Ruff rule step = 1 review scope = 1 commit を標準とする。まとめる必要がある場合は plan amendment と re-review が必要。
- S02 `F`:
  - 具体テストケース一覧:
    - `tc-s02-case-001` acceptance: Pyflakes violation を 0 件にする
      - 前提: S01 が完了し、Ruff が実行できる。
      - 操作: `uv run ruff check --select F src/spec_dock tests` を実行する。
      - 期待結果: command が exit 0 になり、`F` violation が残らない。
      - 失敗検出: undefined name、unused import などが残る回帰を検出する。
      - 検証方法: command output と `report.md` inventory/closure。
      - 関連 closure id: `tc-s02-001`
- S03 `E`:
  - 具体テストケース一覧:
    - `tc-s03-case-001` acceptance: pycodestyle error violation を 0 件にする
      - 前提: S02 が green。`E501` は final ignore として扱う。
      - 操作: `uv run ruff check --select F,E src/spec_dock tests` を実行する。
      - 期待結果: `E501` を除く `E` violation が残らない。
      - 失敗検出: baseline style/syntax hygiene の drift を検出する。
      - 検証方法: command output と `report.md` inventory/closure。
      - 関連 closure id: `tc-s03-001`
- S04 `I`:
  - 具体テストケース一覧:
    - `tc-s04-case-001` acceptance: import order を固定する
      - 前提: S03 が green。
      - 操作: `uv run ruff check --select F,E,I src/spec_dock tests` を実行する。
      - 期待結果: import order violation が残らない。
      - 失敗検出: import sort drift を検出する。
      - 検証方法: command output、diff inspection、`report.md` closure。
      - 関連 closure id: `tc-s04-001`
- S05 `UP`:
  - 具体テストケース一覧:
    - `tc-s05-case-001` acceptance: Python 3.10+ modernization violation を 0 件にする
      - 前提: S04 が green。
      - 操作: `uv run ruff check --select F,E,I,UP src/spec_dock tests` を実行する。
      - 期待結果: `UP` violation が残らず、Python 3.10 support を破らない。
      - 失敗検出: outdated syntax / typing idiom と unsupported modernization を検出する。
      - 検証方法: command output、必要に応じた focused pytest、`report.md` closure。
      - 関連 closure id: `tc-s05-001`
- S06 `B`:
  - 具体テストケース一覧:
    - `tc-s06-case-001` acceptance: bugbear violation を 0 件にする
      - 前提: S05 が green。
      - 操作: `uv run ruff check --select F,E,I,UP,B src/spec_dock tests` を実行する。
      - 期待結果: bug-prone pattern が残らず、behavior risk がある修正は focused pytest で確認される。
      - 失敗検出: mutable default などの subtle bug class を検出する。
      - 検証方法: command output、必要に応じた focused pytest、`report.md` closure。
      - 関連 closure id: `tc-s06-001`
- S07 `C4`:
  - 具体テストケース一覧:
    - `tc-s07-case-001` acceptance: comprehension violation を 0 件にする
      - 前提: S06 が green。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4 src/spec_dock tests` を実行する。
      - 期待結果: `C4` violation が残らない。
      - 失敗検出: redundant comprehension pattern を検出する。
      - 検証方法: command output、diff inspection、`report.md` closure。
      - 関連 closure id: `tc-s07-001`
- S08 `SIM`:
  - 具体テストケース一覧:
    - `tc-s08-case-001` acceptance: simplify violation を 0 件にする
      - 前提: S07 が green。`SIM108` ignore の理由が design/report で説明されている。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4,SIM src/spec_dock tests` を実行する。
      - 期待結果: `SIM108` 以外の `SIM` violation が残らない。
      - 失敗検出: 冗長条件分岐と、可読性を落とす過剰 simplification を検出する。
      - 検証方法: command output、ignore rationale inspection、`report.md` closure。
      - 関連 closure id: `tc-s08-001`
- S09 `PTH`:
  - 具体テストケース一覧:
    - `tc-s09-case-001` acceptance: path handling violation を 0 件にする
      - 前提: S08 が green。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH src/spec_dock tests` を実行する。
      - 期待結果: `PTH` violation が残らず、CLI/filesystem boundary の `str` 必要箇所は意図が保たれる。
      - 失敗検出: `os.path` drift と pathlib 変換による boundary regression を検出する。
      - 検証方法: command output、必要に応じた focused pytest、`report.md` closure。
      - 関連 closure id: `tc-s09-001`
- S10 `TC`:
  - 具体テストケース一覧:
    - `tc-s10-case-001` acceptance: type-only import violation を 0 件にする
      - 前提: S09 が green。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC src/spec_dock tests` を実行する。
      - 期待結果: type-only import が整理され、runtime side effect が必要な import は維持される。
      - 失敗検出: runtime import と type-only import の混在や side-effect regression risk を検出する。
      - 検証方法: command output、diff inspection、必要に応じた focused pytest、`report.md` closure。
      - 関連 closure id: `tc-s10-001`
- S11 `ARG`:
  - 具体テストケース一覧:
    - `tc-s11-case-001` acceptance: unused argument violation を 0 件にする
      - 前提: S10 が green。tests per-file ignore は `ARG` に限定されている。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG src/spec_dock tests` を実行する。
      - 期待結果: source 側 unused argument が解消され、pytest fixture/callback signature は壊れない。
      - 失敗検出: unused parameter drift と fixture signature regression を検出する。
      - 検証方法: command output、per-file ignore inspection、必要に応じた focused pytest、`report.md` closure。
      - 関連 closure id: `tc-s11-001`
- S12 `RUF`:
  - 具体テストケース一覧:
    - `tc-s12-case-001` acceptance: Ruff-native violation を 0 件にする
      - 前提: S11 が green。`RUF001/002/003/010` ignore は理由付きで限定されている。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG,RUF src/spec_dock tests` を実行する。
      - 期待結果: final ignore 以外の `RUF` violation が残らない。
      - 失敗検出: Ruff-native bug class と broad ignore の混入を検出する。
      - 検証方法: command output、ignore rationale inspection、`report.md` closure。
      - 関連 closure id: `tc-s12-001`
- S13 `TID`:
  - 具体テストケース一覧:
    - `tc-s13-case-001` acceptance: tidy import / relative import violation を 0 件にする
      - 前提: S12 が green。layer-specific `banned-api` policy は scope 外である。
      - 操作: `uv run ruff check --select F,E,I,UP,B,C4,SIM,PTH,TC,ARG,RUF,TID src/spec_dock tests` を実行する。
      - 期待結果: relative import violation が残らず、layer-boundary policy へ scope creep しない。
      - 失敗検出: relative import drift と unintended architecture-rule expansion を検出する。
      - 検証方法: command output、diff inspection、`report.md` closure。
      - 関連 closure id: `tc-s13-001`

### S14 executable contract
- delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: `pyproject.toml`, `uv.lock`, `scripts/static_analysis/run.sh`, `report.md` evidence through orchestrator integration.
  - forbidden changes: mypy error cleanup beyond inventory, source/test type fixes, broad suppression, dogfooding direct target。
  - acceptance criteria: mypy resolves and initial error inventory is captured.
  - required verification: `uv run mypy --version`; `uv run mypy src/spec_dock tests`.
  - reviewer focus: mypy config target/exclude correctness and inventory quality。
  - stop conditions: duplicate module / package path noise cannot be classified, or command target must expand beyond design。
  - output required: mypy version, error count/category summary, proposed S15 fix categories。
- 具体テストケース一覧:
  - `tc-s14-case-001` characterization: mypy initial inventory を作成する
    - 前提: S13 が green。
    - 操作: `uv run mypy --version` と `uv run mypy src/spec_dock tests` を実行する。
    - 期待結果: mypy が resolve し、error がある場合は代表 error code / count / category が `report.md` に記録される。
    - 失敗検出: tool resolution failure、target/exclude mistake、unclassified package noise を検出する。
    - 検証方法: command output と `report.md` inventory。
    - 関連 closure id: `tc-s14-001`
- step closure contract:
  - close 条件: inventory が作成され、S15 の修正方針が分類されている。`uv.lock` に変更がある場合は mypy dependency 追加に由来する差分として report に記録される。
  - report evidence destination: Session Log, Discovered Tests, Step Contract Closure, Test Contract Closure。
  - step gate: code-reviewer pass before commit。

### S15 executable contract
- delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: `pyproject.toml`, `src/spec_dock/**/*.py`, `tests/**/*.py`, `scripts/static_analysis/run.sh` if needed.
  - forbidden changes: source type errorsを ignore で隠す、broad suppression、dogfooding direct target、unrelated refactor。
  - acceptance criteria: `uv run mypy src/spec_dock tests` が exit 0。
  - required verification: mypy command、必要に応じた focused pytest。
  - reviewer focus: type-correctness、targeted overrides、suppression rationale。
  - stop conditions: public contract/API 変更が必要、external type noise と real error が区別できない。
  - output required: changed files, mypy green output, override/suppression rationale, unresolved risk。
- 具体テストケース一覧:
  - `tc-s15-case-001` acceptance: mypy error を 0 件にする
    - 前提: S14 inventory が report にある。
    - 操作: S14 の分類に従って修正し、`uv run mypy src/spec_dock tests` を実行する。
    - 期待結果: mypy command が exit 0 で、source error を broad suppression で隠していない。
    - 失敗検出: type errors、unjustified ignore、external package noise の混入を検出する。
    - 検証方法: command output、diff inspection、`report.md` closure。
    - 関連 closure id: `tc-s15-001`
- step closure contract:
  - close 条件: mypy error 0 件、targeted config rationale 記録済み。
  - report evidence destination: Session Log, Step Contract Closure, Test Contract Closure, Closure Coverage。
  - step gate: code-reviewer pass before commit。

### S16 executable contract
- delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: `pyproject.toml`, `src/spec_dock/**/*.py`, `tests/**/*.py`
  - forbidden changes: semantic/type fix、rule追加、CI変更、pre-commit。
  - acceptance criteria: `uv run ruff format --check src/spec_dock tests` が exit 0。
  - required verification: format check、format 適用時の format-only diff inspection。
  - reviewer focus: diff が format-only であること。
  - stop conditions: format が behavior change を誘発する、または semantic fix が必要になる。
  - output required: format command output、format-only diff summary。
- 具体テストケース一覧:
  - `tc-s16-case-001` acceptance: format drift を 0 件にする
    - 前提: S15 が green。
    - 操作: 必要なら `uv run ruff format src/spec_dock tests` を実行し、`uv run ruff format --check src/spec_dock tests` を実行する。
    - 期待結果: format check が exit 0 で、差分は format-only に限定される。
    - 失敗検出: semantic/type fix 混入や formatter churn 未解消を検出する。
    - 検証方法: command output、git diff inspection、`report.md` closure。
    - 関連 closure id: `tc-s16-001`
- step closure contract:
  - close 条件: format check green and format-only evidence complete。
  - report evidence destination: Session Log, Step Contract Closure, Test Contract Closure, Closure Coverage。
  - step gate: code-reviewer pass before commit。

### S17 executable contract
- delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: `scripts/static_analysis/run.sh`, `Makefile`, `pyproject.toml` if final config consolidation is needed.
  - forbidden changes: new rules without prior step closure、source cleanup、CI workflow。
  - acceptance criteria: `make lint` runs Ruff check, Ruff format check, and mypy; summary and non-zero failure behavior exist。
  - required verification: `make lint`; optional failure-behavior inspection through script logic。
  - reviewer focus: local/CI command divergence, target safety, summary/exit code。
  - stop conditions: final gate cannot run all required phases or requires scope外 setup。
  - output required: `make lint` output summary and script diff。
- 具体テストケース一覧:
  - `tc-s17-case-001` acceptance: final local gate を green にする
    - 前提: S16 が green。
    - 操作: `make lint` を実行する。
    - 期待結果: Ruff check、Ruff format check、mypy が実行され、すべて exit 0 で summary が出る。
    - 失敗検出: local command が一部 phase を飛ばす、target がずれる、failure exit を返さない回帰を検出する。
    - 検証方法: command output、script inspection、`report.md` closure。
    - 関連 closure id: `tc-s17-001`
- step closure contract:
  - close 条件: `make lint` green。
  - report evidence destination: Session Log, Step Contract Closure, Test Contract Closure, Closure Coverage。
  - step gate: code-reviewer pass before commit。

### S18 executable contract
- delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: `.github/workflows/provider-ci.yml`
  - forbidden changes: branch protection、pre-commit、unrelated workflow rewrite。
  - acceptance criteria: provider CI calls `make lint` through the same local command surface。
  - required verification: workflow diff inspection; GitHub Actions / PR evidence when available。
  - reviewer focus: CI/local command consistency and YAML minimality。
  - stop conditions: CI requires external secret/policy change or cannot call `make lint` without larger workflow redesign。
  - output required: workflow diff, local inspection, CI/PR evidence status。
- 具体テストケース一覧:
  - `tc-s18-case-001` acceptance: provider CI に static-analysis gate を追加する
    - 前提: S17 の `make lint` が green。
    - 操作: `.github/workflows/provider-ci.yml` を更新し、workflow diff を inspection する。
    - 期待結果: provider CI が `make lint` を実行する。PR/CI が観測可能な場合は実行結果も report に残る。
    - 失敗検出: CI が local と違う command を呼ぶ、または static-analysis gate が PR 上で実行されない回帰を検出する。
    - 検証方法: workflow inspection、GitHub Actions / PR observation when available。
    - 関連 closure id: `tc-s18-001`
- step closure contract:
  - close 条件: workflow inspection pass。external CI evidence が未観測なら S99/PR preparation の未観測項目として report に残す。
  - report evidence destination: Session Log, Step Contract Closure, Test Contract Closure, Closure Coverage, Final Quality Gate。
  - step gate: code-reviewer pass before commit。

### S90 executable contract
- delegation contract:
  - delegated role: `doc-writer` if persistent docs update is required; otherwise orchestrator-approved inspect-only/no-op.
  - allowed paths: README/docs/workflow/template files only if docs impact exists; `spec-dock/**` generated copy files only when `spec-dock update .` is intentionally run to refresh shipped runtime asset changes; `report.md` evidence through orchestrator integration.
  - forbidden changes: source code cleanup, static-analysis config changes, dogfooding direct lint/typecheck target。
  - acceptance criteria: docs impact and shipped runtime asset dogfooding impact are explicitly resolved。
  - required verification: docs inspection, `git diff --name-only` shipped runtime asset check, refresh/inspection decision。
  - reviewer focus: docs/spec alignment and generated-copy source-of-truth discipline。
  - stop conditions: docs update requires product policy beyond issue scope, or dogfooding refresh would create unrelated generated churn that cannot be cleanly attributed to this issue。
  - output required: docs update/no-op rationale, dogfooding refresh/inspection evidence, and either committed generated-copy refresh evidence or explicit unresolved handoff/follow-up if refresh is required but unsafe in this issue。
- 具体テストケース一覧:
  - `tc-s90-case-001` inspect-only: docs / dogfooding impact を閉じる
    - 前提: S18 までの implementation diff が存在する。
    - 操作: docs command list の有無と shipped runtime asset diff を inspection する。
    - 期待結果: docs 更新要否と dogfooding refresh/inspection 判断が `report.md` に記録される。refresh が必要かつ this issue 内で安全なら `spec-dock/` generated copy 差分を許可範囲内で含め、危険なら unresolved handoff/follow-up として記録する。
    - 失敗検出: `make lint` の新導線が docs から漏れる、または shipped runtime asset 変更後の generated-copy stale risk を見落とす。
    - 検証方法: docs inspection、`git diff --name-only`、必要に応じた `spec-dock update .` 判断。
    - 関連 closure id: `tc-s90-001`
- step closure contract:
  - close 条件: docs impact no-op/update と dogfooding impact evidence が report にある。refresh が必要な場合は、`spec-dock/` generated copy 差分がこの issue 由来として review 可能であるか、または unresolved handoff/follow-up が明示されている。
  - report evidence destination: Spec Interpretation / Decision Ledger, Step Contract Closure, Test Contract Closure, Closure Coverage, Docs Impact Resolution。
  - step gate: docs update がある場合は spec-reviewer/docs review; no-op は approved-no-op evidence。

### S99 executable contract
- delegation contract:
  - delegated role: orchestrator coordinates; qa-reviewer, code-reviewer, spec-reviewer perform final gates.
  - allowed paths: `report.md` evidence updates only unless reviewer findings require bounded fixes and plan-compatible delegation.
  - forbidden changes: unreviewed implementation changes, scope expansion, final gate bypass。
  - acceptance criteria: all AC/EC closure IDs are pass/approved-no-op and required commands/reviews are green。
  - required verification: `make lint`, `uv run pytest`, `./spec-dock/scripts/spec-dock validate`, `git status --short`, dogfooding impact evidence inspection, reviewer gates。
  - reviewer focus: whole-issue integration, obligation coverage, spec alignment。
  - stop conditions: any required command fails, reviewer returns fail, report evidence incomplete, CI evidence required but unresolved without explicit handoff note。
  - output required: final command outputs, reviewer verdicts, final report ledger, commit/no-op status。
- 具体テストケース一覧:
  - `tc-s99-case-001` acceptance: final quality gate を green にする
    - 前提: S01-S18/S90 が完了し、step-level report evidence がある。
    - 操作: `make lint`, `uv run pytest`, `./spec-dock/scripts/spec-dock validate`, `git status --short` を実行し、final reviewers を通す。
    - 期待結果: すべての required commands と reviewer gates が pass し、未解決 AC/EC closure が残らない。
    - 失敗検出: static-analysis violation、regression、spec drift、report evidence gap、unintended dirty state を検出する。
    - 検証方法: command output、reviewer verdict、`report.md` final gate ledger。
    - 関連 closure id: `tc-s99-001`
- step closure contract:
  - close 条件: final command bundle green, reviewer gates pass, final report ledger complete, clean state。
  - report evidence destination: Final Quality Gate, Reviewer Gate Status, Step Commit Gate, Closure Coverage。
  - step gate: qa-reviewer pass -> issue-wide code-reviewer pass -> final spec-reviewer pass -> final commit/clean check。

## 委任契約（全 implementation step）
- 委任ロール:
  - dev-coder: S01-S18 の implementation。
  - doc-writer: S90 で恒久 docs 更新が必要な場合。
  - code-reviewer: S01-S18 の review。
  - qa-reviewer: S99 の QA gate。
  - spec-reviewer: authoring docs と final spec consistency。
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
  - issue `discussions/*.md`
- 許可 paths:
  - 各 step の対象ファイル。
- 禁止 changes:
  - `spec-dock/` direct lint/typecheck target 化。
  - pre-commit 実装。
  - broad suppression。
  - unrelated refactor。
- 必須出力:
  - changed files。
  - command result。
  - violation inventory / closure evidence。
  - unresolved risk。
- 停止条件:
  - requirement/design/plan の衝突。
  - scope 外変更が必要。
  - acceptance を満たせない command failure。
  - destructive operation が必要。

## 最終完了条件
- `pyproject.toml` に Ruff / mypy final config がある。
- `scripts/static_analysis/run.sh` と `Makefile` `lint` がある。
- provider CI が `make lint` を実行する。
- Ruff final select の全 violation が 0 件。
- mypy error が 0 件。
- Ruff format check が green。
- `make lint`, `uv run pytest`, `./spec-dock/scripts/spec-dock validate` が成功する。
- `report.md` に各 step の violation inventory と closure evidence がある。
- shipped runtime asset 変更時は dogfooding refresh/inspection evidence が `report.md` にある。
- reviewer gates が pass している。
- final commit 後に unintended changes が残っていない。

## Final Exit Contract
- Execution handoff readiness:
  - requirement fresh spec-reviewer pass recorded。
  - design fresh spec-reviewer pass recorded。
  - plan fresh spec-reviewer pass recorded。
  - `report.md` Spec Authoring Gate marks requirement/design/plan as non-blocking。
- Implementation completion readiness:
  - S01-S18, S90, S99 have Step Contract Closure, Test Contract Closure, and Closure Coverage entries in `report.md`。
  - All required commands pass: `make lint`, `uv run pytest`, `./spec-dock/scripts/spec-dock validate`。
  - CI enforcement evidence is recorded when observable; if not observable before PR, the unresolved external evidence is explicitly carried to PR observation / merge-prep rather than silently treated as pass。
  - Dogfooding impact evidence exists when shipped runtime asset changes.
  - qa-reviewer, issue-wide code-reviewer, and final spec-reviewer gates pass。
  - final commit is created and `git status --short` is clean except for intentionally uncommitted external artifacts, if any, documented in `report.md`。
