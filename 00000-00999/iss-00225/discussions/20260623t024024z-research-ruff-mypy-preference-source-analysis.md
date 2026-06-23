---
種別: research
ID: "20260623t024024z-research"
タイトル: "Ruff and mypy preference source analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["iss-00225"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260623t024024z-research Ruff and mypy preference source analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00225` の要件定義前に、ユーザーが好む Ruff / mypy 設定の先例を `taikyohiyou_project` から抽出し、SpecDock にそのままコピーせず適用できる思想・候補・除外すべきプロジェクト固有設定を整理する。
- SpecDock の現状構造と設定を照合し、後続の `requirement.md` / `design.md` / `plan.md` へ採用候補として渡せる source-grounded evidence を作る。

## sources / 調査方法 (必須)
- 参照先:
  - SpecDock active issue scaffold: `spec-dock/active/issue/requirement.md`
  - SpecDock parent epic: `spec-dock/active/epic/requirement.md`
  - SpecDock repository guidance: `AGENTS.md`
  - SpecDock current Python/project config: `pyproject.toml`
  - SpecDock runtime/provider layout: `src/spec_dock/` and `tests/`
  - Clarification workflow: `spec-dock/docs/workflow_clarification.md`
  - Discussion rules: `spec-dock/active/issue/discussions/rules.md`
  - User preference source project: `/Volumes/990p2t/workspace/product/taikyohiyou_project`
  - Preference source config: `/Volumes/990p2t/workspace/product/taikyohiyou_project/taikyohiyou_management_api/pyproject.toml`
  - Preference source pre-commit hook: `/Volumes/990p2t/workspace/product/taikyohiyou_project/.pre-commit-config.yaml`
  - Preference source root Makefile: `/Volumes/990p2t/workspace/product/taikyohiyou_project/Makefile`
  - Preference source API Makefile: `/Volumes/990p2t/workspace/product/taikyohiyou_project/taikyohiyou_management_api/Makefile`
  - Preference source pre-commit runner: `/Volumes/990p2t/workspace/product/taikyohiyou_project/scripts/pre_commit/run.sh`
  - Preference source Ruff overrides: `/Volumes/990p2t/workspace/product/taikyohiyou_project/taikyohiyou_management_api/**/ruff.toml`
- 検証手順:
  - `rg --files` で SpecDock と preference source の Python quality config を列挙した。
  - `sed` で対象 config と active/parent docs を読んだ。
  - `find` / `wc -l` で SpecDock の Python file surface を概算した。
- 実験条件:
  - まだ Ruff / mypy は実行していない。これは requirements authoring 前の source-grounding であり、エラー件数や具体的修正内容は未測定。

## facts / 観測できた事実 (必須)
- SpecDock の `pyproject.toml` は現在、build metadata、runtime dependency、`dev = ["pytest>=8.0"]`、pytest 設定、setuptools package-data を持つ。Ruff / mypy / pre-commit / import-linter の設定は見当たらない。
- SpecDock の Python runtime は Python `>=3.10` を前提にしている。Preference source は Python `>=3.12` / Ruff target `py312` / mypy `python_version = "3.12"` なので、そのまま転用すると SpecDock の supported Python range と衝突する。
- SpecDock は provider source of truth と dogfooding workspace を併せ持つ。AGENTS.md は、実装 source of truth を `src/spec_dock/`、特に shipped scaffold/runtime を `src/spec_dock/assets/spec_dock/...` とし、dogfooding workspace `spec-dock/` は検証・反映対象として扱うと定義している。
- SpecDock の runtime architecture は `cli`, `commands`, `application`, `domain`, `infra`, `presentation` の hybrid layered architecture。新規作業は該当 layer に置き、monolithic command files へ戻さないことが既存方針。
- SpecDock の Python file surface は概算で `src/spec_dock/**/*.py` が 88 files、runtime subtree が 82 files、`tests/**/*.py` が 58 files。
- Preference source の `pyproject.toml` は Ruff を `preview = true`、`line-length = 120`、`indent-width = 4`、`target-version = "py312"` で設定している。
- Preference source の Ruff `select` は `E`, `F`, `I`, `UP`, `B`, `C4`, `SIM`, `PTH`, `TC`, `ARG`, `RUF`, `TID`, `PLC`, `PLW` を含む。`extend-select` で `E402`, `F401`, `F402`, `TID252`, public docstring 系 `D101` / `D102` / `D103` / `D105` / `D106` / `D107` / `D419` を追加している。
- Preference source の Ruff `ignore` は `E501`, `SIM108`, `RUF010`, `RUF001`, `RUF002`, `RUF003`, `RUF029`, `PLR0913`, `PLR0912`, `PLR0915`, `PLR2004`, `PLC1901` などを含む。
- Preference source は `flake8-unused-arguments.ignore-variadic-names = true`、isort の `force-sort-within-sections = true` / `combine-as-imports = true`、`flake8-tidy-imports.ban-relative-imports = "all"` を設定している。
- Preference source は tests に対して `ARG`, `RUF012`, `PLC2401` などを per-file ignore し、日本語テスト名を許容している。
- Preference source の mypy は `allow_redefinition = false`, `check_untyped_defs = true`, `show_error_codes = true`, `show_column_numbers = true`, `show_error_context = true`, `enable_error_code = ["explicit-override"]`, `ignore_missing_imports = true`, `pretty = true` を設定している。tests override では `check_untyped_defs = false` / `disallow_untyped_defs = false` としている。
- Preference source には SQLAlchemy plugin、coverage、import-linter、FastAPI/Celery/SQLAlchemy/Alembic など、SpecDock には直接関係しない設定が含まれる。
- Preference source は layer / bounded context ごとの `ruff.toml` override で `flake8-tidy-imports.banned-api` を定義している。例: domain から application / infra / entrypoint を禁止、application から infra / entrypoint を禁止、tests から infra や他 bounded context を禁止。
- Preference source root の `.pre-commit-config.yaml` は local hook として branch protection と `scripts/pre_commit/run.sh` を呼ぶ。Ruff/mypy hook を直接列挙する形ではなく、project-local quality gate script に集約している。
- Preference source API `Makefile` は `make lint` を定義し、`clean-init-files`, `lint-imports`, `lint-arch`, `ruff check --no-cache .`, `mypy .` を `set +e` で順に実行し、各 exit code を summary として出してから最終的に失敗有無を返す。
- Preference source API `Makefile` は `lint-arch` を別 target として持ち、layer / bounded context ごとの Ruff override directory へ移動して `ruff check` を実行している。
- Preference source `scripts/pre_commit/run.sh` は staged files から影響範囲を判定し、management API 変更時には quality checks と unit tests をまとめて実行する。静的解析そのものは `ruff format --check`, `ruff check`, `mypy`, layer-specific `ruff check` を含むが、hook への組み込み・Docker/env adapter は project-specific で重い。
- SpecDock repository root には現時点で `Makefile` や root `scripts/` は見当たらない。

## inference / 推測 (必須)
- 事実から推測したこと:
  - ユーザーの好みは「Ruff を formatting/import sorting だけでなく、bug-prone pattern、簡略化、pathlib、type-checking import、unused args、tidy imports、layer boundary enforcement に使う」方向にある。
  - SpecDock にそのまま必要なのは `FastAPI` / `SQLAlchemy` 等の禁止ではなく、SpecDock runtime layer に合わせた `banned-api` または import boundary check である。
  - SpecDock は Python 3.10+ を維持するため、Ruff `target-version` と mypy `python_version` は `py310` / `3.10` 相当に寄せる必要がある。
  - 初回導入では大量の Ruff / mypy finding が想定されるため、要件には「設定追加」と「既存違反を残さず修正する」を同じ issue scope に含める必要がある。ただし修正方式は一括 auto-format と behavior-preserving manual fixes を分けて計画すべき。
  - SpecDock の shipped runtime は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` 配下にあり、consumer repo へコピーされる資産でもあるため、lint/typecheck 対象に含めるかどうかは requirement 上の重要判断になる。
  - SpecDock にも reference source の `make lint` に相当する local entrypoint を置く場合、hook-specific environment preparation ではなく、repository-local script plus Makefile target の軽量形が合う。
- 推測の根拠:
  - Preference source の Ruff select / banned-api / mypy strict-ish diagnostics は品質ゲートとしての静的解析を明確に志向している。
  - SpecDock AGENTS.md の layered runtime architecture と provider/dogfooding source-of-truth ルールは、import boundary と対象範囲を定義する根拠になる。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `uv run ruff check`, `uv run ruff format --check`, `uv run mypy ...` の実行結果とエラー件数。
  - Ruff/mypy を dev dependency group に追加した場合の lock / dependency update 方針。
  - CI / pre-commit / scripts へ静的解析をどこまで組み込むか。
  - Shipped scaffold 内に同梱される Python runtime を mypy 対象にする場合、package discovery / module path / duplicate module name 問題が出るかどうか。
  - `spec-dock/` dogfooding workspace 内の copied/generated files を lint/typecheck 対象に含めるか、provider source only とするか。
  - Public docstring ルール `D101` などを SpecDock に導入するか。既存コード量から見ると初回修正コストが大きい可能性がある。
  - Makefile target の最終名称。User は Make command を希望しているため、現時点では `make lint` または `make static-analysis` が候補。
- 確認できない理由:
  - この artifact は要件定義前の調査・インタビュー準備であり、実行・修正は後続の requirement/design/plan authoring 後に行う。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 初回導入の合格条件を「provider/runtime/tests の全 Python に対して Ruff/mypy を即時 green」にするか、「provider source first で dogfooding copy は sync/validation 対象に留める」か。
  - Preference source の厳しめ docstring rule と `preview = true` を SpecDock にも最初から入れるか、まずは behavior-preserving な静的解析 baseline を優先するか。
  - CI/pre-commit まで今回の issue に含めるか、設定と修正だけに留めるか。
- pressure-test question として切り出すべき候補:
  - 今回の issue の合格条件として、Ruff/mypy の対象範囲はどこまでにするべきか。
- 質問せずに解決できた候補:
  - Python version は SpecDock の current project metadata に従い、Python 3.10+ 前提で設定すべき。
  - FastAPI / SQLAlchemy / Alembic / Celery 固有設定は SpecDock には直接持ち込まない。
  - Layer boundary の思想は SpecDock の `cli/commands/application/domain/infra/presentation` に翻訳する候補として残す。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - "SpecDock project" と "dogfooding workspace"
  - "runtime" と "installed/copied runtime asset"
  - "static analysis green" と "generated/copy parity green"
- 既存 docs / code / tests / discussions での使われ方:
  - AGENTS.md は `src/spec_dock/` を provider-side source of truth、`spec-dock/` を generated consumer-side workspace と呼び分けている。
  - Runtime architecture は provider asset under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` に存在し、実行時には consumer repo の `spec-dock/scripts/spec_dock_runtime/` として現れる。
- 判断が必要な理由:
  - Ruff/mypy の対象を provider source only にするか、dogfooding copy も直接 lint/typecheck するかで、エラー件数・修正場所・CI時間・二重修正リスクが変わる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Ruff format が provider asset と dogfooding copy の双方に同じような差分を出す。
- その edge case が requirement / design / plan に与える影響:
  - Provider-first の修正と dogfooding refresh/inspection の境界を requirement/design で明示しないと、generated workspace を source of truth と誤認する可能性がある。
- edge case:
  - mypy が shipped runtime asset を package として解決できず、import path や duplicate module による noise を大量に出す。
- その edge case が requirement / design / plan に与える影響:
  - mypy target と invocation command を設計で固定し、必要なら config / package discovery / explicit package bases の方針を決める必要がある。
- edge case:
  - Preference source の public docstring rules をそのまま入れると、静的解析導入というより大量 docstring 作成 issue になる。
- その edge case が requirement / design / plan に与える影響:
  - docstring rules を初回から必須にするか、別 issue に切るかを要件で決める必要がある。

## implications / 判断への含意 (必須)
- Requirement には、少なくとも「Ruff check」「Ruff format check」「mypy check」が repo-local command として成功すること、既存違反を修正して green baseline を作ること、対象範囲を明示することが必要。
- Design では、`pyproject.toml` に設定を集約しつつ、SpecDock layer boundary を Ruff `banned-api` override で表すか、初回は import-linter / Ruff boundary rule を別 step にするかを検討する。
- Plan では、先に config-only / command wiring を置き、次に Ruff auto-fix/format、次に Ruff manual fixes、最後に mypy fixes、docs/CI/pre-commit integration の順に分けると、巨大差分をレビューしやすい。
- Preference source の `pre-commit` 形は、SpecDock でも `scripts/pre_commit/run.sh` 相当の集約 quality gate を作る選択肢を示す。ただし現在の SpecDock に同等 script があるかは未確認。
- 初回から CI/pre-commit mandatory にする場合、既存全違反修正が issue 完了条件になる。逆に command-only に留める場合、green baseline の実行責務は developer workflow に残る。
- User interview result updated the scope: CI enforcement is in scope; pre-commit is out of scope for this issue; a local grouped static-analysis script and Makefile target are in scope.
- The local grouped script should probably mimic the reference `make lint` behavior: run phases in a stable order, avoid stopping at the first failure when useful, print a summary, and return non-zero if any phase fails.

## リスク/制約 (任意)
- 初回導入で format-only 差分と semantic/type fixes が混ざるとレビュー不能になりやすい。
- `src/spec_dock/assets/spec_dock/...` は shipped asset API なので、formatting が consumer-visible assets に影響する。
- mypy の `ignore_missing_imports = true` は初回導入の現実解になり得るが、静的解析の厳しさをどこまで求めるかはユーザー意図確認が必要。
- Ruff `preview = true` は preference source では採用されているが、SpecDock の package/tooling stability と衝突する可能性がある。

## 反映先 (任意)
- reflected_to:
  - candidate: `requirement.md` source / scope / acceptance criteria
  - candidate: `design.md` Ruff/mypy config strategy and target boundaries
  - candidate: `plan.md` implementation order and verification commands
  - candidate: `report.md` Evidence Adoption Ledger after canonical adoption

## 参考（References） (任意)
- `/Volumes/990p2t/workspace/product/taikyohiyou_project/taikyohiyou_management_api/pyproject.toml`
- `/Volumes/990p2t/workspace/product/taikyohiyou_project/.pre-commit-config.yaml`
- `/Volumes/990p2t/workspace/product/taikyohiyou_project/taikyohiyou_management_api/**/ruff.toml`
- `pyproject.toml`
- `AGENTS.md`
- `spec-dock/docs/workflow_clarification.md`
