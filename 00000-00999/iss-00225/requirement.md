---
種別: 要件定義書（Issue）
ID: "iss-00225"
タイトル: "Configure Ruff And Mypy Static Analysis Cleanup"
関連GitHub: ["#225"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00107", "init-local-00002"]
---

# iss-00225 Configure Ruff And Mypy Static Analysis Cleanup — 要件定義

## 目的
- SpecDock repository に Ruff と mypy による静的解析を導入し、対象 Python code が継続的に検査される状態にする。
- 初回導入時に検出される既存違反をすべて解消し、CI とローカルコマンドの双方で green baseline を作る。
- 大量違反を一括処理せず、検査項目を小刻みに追加して、各段階で違反 inventory と修正完了証跡を残す。

## 背景・現状
- 現状の挙動:
  - `pyproject.toml` には pytest 設定と `dev = ["pytest>=8.0"]` があるが、Ruff / mypy の dependency と設定はない。
  - provider CI は Python test を実行するが、Ruff / mypy / format check は実行していない。
  - repository root に `Makefile` と静的解析用 grouped script はない。
- 現状の課題:
  - Ruff / mypy による bug-prone pattern、import order、format drift、typing error の検出が PR 上で保証されない。
  - ここまで静的解析なしでコードベースが成長しているため、初回設定を一括で有効化すると大量の違反と巨大な修正差分が発生する可能性が高い。
  - dogfooding workspace `spec-dock/` と provider source `src/spec_dock/` が併存するため、静的解析対象を誤ると generated copy を source of truth として修正するリスクがある。
- 情報源:
  - `discussions/20260623t024024z-research-ruff-mypy-preference-source-analysis.md`
  - `discussions/20260623t024210z-interview-static-analysis-target-boundary.md`
  - `discussions/20260623t025015z-interview-static-analysis-enforcement-entrypoint.md`
  - `discussions/20260623t030652z-disc-static-analysis-final-configuration-proposal.md`
  - `AGENTS.md`
  - `pyproject.toml`
  - `.github/workflows/provider-ci.yml`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock provider 実装者。
  - PR reviewer。
  - Issue execution を委任される dev-coder / reviewer agent。
- 代表シナリオ:
  - 開発者が `make lint` を実行し、Ruff check、Ruff format check、mypy をまとめて確認できる。
  - CI が静的解析を実行し、違反がある PR を失敗させる。
  - 初回導入の実装者が、rule group を一つずつ有効化し、各段階の違反を修正してから次へ進める。

## スコープ
- 必須:
  - `pyproject.toml` に SpecDock 向けの Ruff / mypy dev dependency と設定を追加する。
  - Python target は SpecDock の `requires-python = ">=3.10"` と整合する `py310` / `3.10` にする。
  - Ruff の最終目標には `E`, `F`, `I`, `UP`, `B`, `C4`, `SIM`, `PTH`, `TC`, `ARG`, `RUF`, `TID` を含める。
  - Ruff format check をローカル script、Makefile target、CI から実行できる状態にする。
  - mypy を Option B の対象範囲で実行できる状態にする。
  - grouped static-analysis script を追加し、途中の phase が失敗しても可能な限り後続 check を実行し、最後に summary と最終 exit code を返す。
  - repository root の `Makefile` に、grouped script を呼ぶ `make lint` を追加する。
  - provider CI に static-analysis gate を追加する。
  - 段階ごとに検出違反を inventory 化し、当該段階の違反を 0 件にしてから次の検査項目を追加する。
  - 最終的に `make lint`、個別の `ruff check`、`ruff format --check`、`mypy`、既存 pytest、`spec-dock validate` が成功する。
- 禁止:
  - dogfooding workspace `spec-dock/` を Ruff / mypy の直接 target に含めない。
  - `spec-dock/` 配下の generated copy を source of truth として修正しない。
  - pre-commit hook 導入、`.pre-commit-config.yaml` 追加、hook installation はこの issue で実装しない。
  - FastAPI / SQLAlchemy / Alembic / Celery など、参照元 project 固有の設定を SpecDock にそのまま持ち込まない。
  - 大量違反を隠すための broad ignore、file 全体 ignore、`type: ignore` の乱用を行わない。
  - フォーマット差分と意味変更を同一 step に混在させない。
- 対象外:
  - pre-commit 導入 issue の作成・実装。
  - import-linter 導入。
  - public docstring rule `D101` 等の導入。
  - package support version を Python 3.11+ / 3.12+ へ引き上げる判断。
  - GitHub branch protection 設定の変更。

## 境界
- 常に行う:
  - provider source of truth は `src/spec_dock/` として扱う。
  - shipped runtime asset `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` は静的解析 coverage に含める。
  - `tests/` は Ruff / mypy coverage に含める。ただし tests 固有の自然な未使用 fixture / callback 引数は per-file ignore で扱う。
  - 各 rule step の実行結果、違反分類、修正方針、0 件確認を `report.md` に記録する。
- 判断が必要:
  - 個別 rule が SpecDock の現行 architecture と衝突し、修正が大規模 architecture rewrite になる場合。
  - mypy の package 解決により duplicate module / generated asset 固有の noise が発生する場合。
  - 特定の ignore や targeted suppression を追加しなければ現実的に green にできない場合。
- 行わない:
  - dogfooding copy の直接 lint/typecheck。
  - hook installer や staged-file-aware script の実装。
  - 参照 project の layer-specific banned-api を機械的に移植すること。

## 非交渉制約
- source-of-truth discipline を守り、implementation source は provider side を優先する。
- 各検査項目は小刻みに追加し、違反が出た場合は inventory 化して修正し、0 件を確認してから次の項目へ進む。
- 最終状態では静的解析 violation を残さない。
- CI で静的解析が実行される。
- pre-commit は scope 外として残す。

## 前提
- `uv` による dev dependency 実行を前提にする。
- 参照 project `/Volumes/990p2t/workspace/product/taikyohiyou_project` の設定思想は参考にするが、SpecDock の Python version、repository structure、dogfooding boundary に合わせて翻訳する。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` は `src/spec_dock/` 配下にあるため、実行 command では重複 target を避けつつ coverage と report 上で明示する。

## 受け入れ条件
- AC-001 Static analysis dependency and config:
  - アクター: developer
  - 前提: clean checkout に dev dependency を sync できる。
  - 操作: `pyproject.toml` を確認する。
  - 期待結果: Ruff / mypy dev dependency と SpecDock 向けの Ruff / mypy 設定が存在する。
  - 観測点: `pyproject.toml`
- AC-002 Target boundary:
  - アクター: developer
  - 前提: Option B が採用済みである。
  - 操作: static-analysis script / CI / config の target と exclude を確認する。
  - 期待結果: `src/spec_dock`, `tests`, shipped runtime asset が coverage に含まれ、dogfooding `spec-dock/` は直接 target から除外される。
  - 観測点: `scripts/static_analysis/run.sh`, `pyproject.toml`, CI logs
- AC-003 Local one-command entrypoint:
  - アクター: developer
  - 前提: repository root にいる。
  - 操作: `make lint` を実行する。
  - 期待結果: Ruff check、Ruff format check、mypy が grouped script 経由で実行され、summary と正しい exit code が返る。
  - 観測点: terminal output, exit code
- AC-004 CI enforcement:
  - アクター: PR author
  - 前提: provider CI が実行される。
  - 操作: CI workflow を実行する。
  - 期待結果: static-analysis gate が実行され、違反があれば CI が失敗する。
  - 観測点: GitHub Actions workflow definition / CI log
- AC-005 Fine-grained Ruff adoption:
  - アクター: implementer
  - 前提: Ruff final rule set が設計済みである。
  - 操作: `F`, `E`, `I`, `UP`, `B`, `C4`, `SIM`, `PTH`, `TC`, `ARG`, `RUF`, `TID` を小刻みに追加する。
  - 期待結果: 各 rule step の検出違反が inventory 化され、0 件化してから次 step へ進む。
  - 観測点: `report.md` の step closure / command output summary
- AC-006 Mypy adoption:
  - アクター: implementer
  - 前提: Ruff step が green である。
  - 操作: mypy 設定を段階的に有効化して実行する。
  - 期待結果: mypy error inventory が作成され、対象範囲で error 0 件になる。
  - 観測点: `report.md`, mypy command output
- AC-007 Format isolation:
  - アクター: implementer
  - 前提: semantic lint / type fixes と混ざらない step boundary がある。
  - 操作: Ruff format を適用または check する。
  - 期待結果: format-only 差分は独立 step として扱われ、最終的に `ruff format --check` が成功する。
  - 観測点: git diff, command output
- AC-008 Final green baseline:
  - アクター: reviewer
  - 前提: すべての implementation step が完了している。
  - 操作: final quality gate を実行する。
  - 期待結果: `make lint`, `uv run pytest`, `./spec-dock/scripts/spec-dock validate` が成功し、静的解析違反が残らない。
  - 観測点: final report ledger
- AC-009 No hidden broad suppression:
  - アクター: reviewer
  - 前提: implementation diff が提示される。
  - 操作: ignore / suppression / exclude の差分を確認する。
  - 期待結果: broad suppression で違反を隠しておらず、必要な ignore は理由と範囲が明示されている。
  - 観測点: `pyproject.toml`, source diff, `report.md`

## 例外・エッジケース
- EC-001 大量違反:
  - 条件: 新しい rule を有効化した段階で多数の violation が出る。
  - 期待: rule step 内で inventory 化し、分類と修正方針を記録し、その rule の violation を 0 件にしてから次 step へ進む。
  - 観測点: `report.md`
- EC-002 過大修正を要求する rule:
  - 条件: rule 適用が大規模 architecture rewrite、public API 変更、別 issue 相当の作業を要求する。
  - 期待: plan amendment または follow-up 化を検討し、ユーザー判断が必要なら止める。
  - 観測点: decision ledger
- EC-003 untyped external dependency:
  - 条件: 外部 package の型情報不足で mypy error が発生する。
  - 期待: `ignore_missing_imports` や targeted override を検討し、source code 側の real type error と区別する。
  - 観測点: mypy output, config diff
- EC-004 package/path 解決 noise:
  - 条件: shipped runtime asset や package discovery により mypy が duplicate module などの noise を出す。
  - 期待: command target / mypy config / excludes を調整し、dogfooding copy を直接 target に含めずに coverage を満たす。
  - 観測点: mypy output, `pyproject.toml`, script
- EC-005 formatter churn:
  - 条件: Ruff format が大量の非意味差分を出す。
  - 期待: format-only step として隔離し、semantic/type fixes と混ぜない。
  - 観測点: git diff, step closure

## 用語
- TERM-001 Option B target:
  - `src/spec_dock`, `tests`, and shipped runtime asset `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` を静的解析 coverage に含め、dogfooding `spec-dock/` copy を直接 target にしない方針。
- TERM-002 grouped script:
  - Ruff check、Ruff format check、mypy を安定した順序で実行し、summary と exit code を返す repository-local script。
- TERM-003 violation inventory:
  - ある rule step で検出された違反の rule code、件数、代表 file、修正方針、0 件化確認を記録した evidence。

## 未確定事項
- Q-001:
  - 質問: なし。
  - 状態: 追加インタビュー不要。実装中に EC-002 相当の scope expansion が見つかった場合のみ再確認する。
