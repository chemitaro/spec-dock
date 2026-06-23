---
種別: 実装計画書（Issue）
ID: "iss-00225"
タイトル: "Configure Ruff And Mypy Static Analysis Cleanup"
関連GitHub: ["#225"]
状態: "draft"
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
| S90 | docs impact resolution | AC-008 | docs inspection |
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
| tc-s18-001 | S18 | acceptance | AC-004 | provider CI が `make lint` を実行する | CI enforcement gap | yes | inspection / CI |
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
- 本計画 authoring 時点:
  - fresh spec-reviewer pass は未取得。execution handoff 前に必須。

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
  - dev dependency に `ruff` を追加する。`mypy` は S14 で追加してもよいが、S01 でまとめて追加する場合は S14 まで実行失敗を expected として扱わない。
  - Ruff global settings と exclude を置く。
  - script は最終形の構造を持つが、未導入 phase は placeholder にしない。実行する command だけを含める。
  - `make lint` は script を呼ぶ。
- 禁止:
  - pre-commit 追加。
  - `spec-dock/` direct target。
- 検証:
  - `test -x scripts/static_analysis/run.sh`
  - `make lint` の command surface inspection。まだ全最終 check が成立しない場合は、実行対象を S01 時点で有効な check に限定する。
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
  - 可能なら GitHub Actions result。
- close 条件:
  - CI が local と同じ `make lint` entrypoint を使う。
- report 証跡:
  - workflow change と CI validation。

### S90 — Docs Impact Resolution
- 目標:
  - 実装により恒久 docs / README / workflow 更新が必要か確認する。
- 対象:
  - README / docs / workflow / templates / none
- 判定:
  - `make lint` が新しい標準 entrypoint になるため、README や developer docs に既存コマンド一覧がある場合は更新する。
  - 恒久 docs 更新が必要な場合は doc-writer に委任する。
- 検証:
  - docs inspection。
- report 証跡:
  - 更新要否、更新した場合の file、更新しない場合の理由。

### S99 — Final Quality Gate
- 目標:
  - issue 全体の完了条件を閉じる。
- 必須 validation:
  - `make lint`
  - `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `git status --short`
- reviewer gates:
  - qa-reviewer pass
  - issue-wide code-reviewer pass
  - final spec-reviewer pass
- close 条件:
  - AC / EC が report 上で closure されている。
  - static analysis violation が残っていない。
  - broad suppression がない、または targeted suppression の理由が記録されている。
  - unintended staged / unstaged changes がない。

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
- reviewer gates が pass している。
- final commit 後に unintended changes が残っていない。
