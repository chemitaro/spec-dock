---
種別: disc
ID: "20260623t030652z-disc"
タイトル: "Static analysis final configuration proposal"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["iss-00225"]
関連: []
authority: "proposed"
derived_from:
  - "20260623t024024z-research"
  - "20260623t024210z-interview"
  - "20260623t025015z-interview"
reflected_to: []
---

# 20260623t030652z-disc Static analysis final configuration proposal

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - `iss-00225` で最終的に `pyproject.toml` / local script / Makefile / CI に置く静的解析設定の目標像。
  - 段階的に rule group を追加し、各段階で検出違反を inventory 化して 0 件へ閉じるための最終設定案。
- この synthesis が必要な理由:
  - canonical `requirement.md` / `design.md` / `plan.md` を書く前に、人間が「どの検査を最終的に目指すのか」を視覚的に確認できる資料が必要。
  - 初回導入は違反が大量に出る可能性があるため、最終設定と段階導入順を分けて理解できる形にする。

## derived question sheets / research (必須)
- `interview`:
  - `20260623t024210z-interview-static-analysis-target-boundary.md`: Option B adopted。Ruff/mypy の直接対象は provider source、tests、shipped runtime asset。dogfooding copy `spec-dock/` は対象外。
  - `20260623t025015z-interview-static-analysis-enforcement-entrypoint.md`: CI enforcement adopted。pre-commit は別 issue。local grouped script と Makefile target は今回 scope。
- `research`:
  - `20260623t024024z-research-ruff-mypy-preference-source-analysis.md`: `taikyohiyou_project` の Ruff/mypy/pre-commit/Makefile 先例と SpecDock への適用候補。
- その他の根拠:
  - SpecDock `pyproject.toml`: 現状は pytest のみで Ruff/mypy 設定なし。
  - SpecDock `AGENTS.md`: provider source of truth は `src/spec_dock/`。dogfooding `spec-dock/` は検証・反映対象。
  - Ruff official docs: `pyproject.toml` の `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]` で lint/format 設定できる。
  - mypy official docs: `pyproject.toml` の `[tool.mypy]` と `[[tool.mypy.overrides]]` で global / per-module 設定できる。

## synthesis (必須)
- 合意済みのこと:
  - 進め方は「段階的に rule group を追加し、各段階の違反 inventory を作成し、全解消してから次の rule group へ進む」方式。
  - 最終的には `ruff check`, `ruff format --check`, `mypy` が Option B の対象範囲で green になる。
  - CI は今回 scope に含める。
  - pre-commit hook 導入は今回 scope 外で、別 issue に切る。
  - local grouped static-analysis script と、それを呼ぶ `Makefile` target は今回 scope に含める。
- 未合意 / 未確定のこと:
  - 実際にどの違反が出るかは、段階ごとに command を実行するまで確定しない。
  - Make target 名は `lint` を第一候補にするが、canonical design で最終確定する。
  - Docstring 系 `D101` などを初回 scope に含めるかは、現時点の推奨では含めない。
- source-grounded に解決できたこと:
  - Python target は SpecDock の `requires-python = ">=3.10"` に合わせる。
  - FastAPI / SQLAlchemy / Alembic / Celery 固有の reference project 設定は SpecDock に持ち込まない。
  - dogfooding copy `spec-dock/` は direct lint/typecheck target にしない。

## 現状と最終目標

| 項目 | 現状 | 最終目標案 |
|---|---|---|
| dev dependencies | `pytest>=8.0` のみ | `pytest`, `ruff`, `mypy`, 必要なら `typing-extensions` を dev group に含める |
| Ruff lint | 未設定 | `E`, `F`, `I`, `UP`, `B`, `C4`, `SIM`, `PTH`, `TC`, `ARG`, `RUF`, `TID` を段階導入 |
| Ruff format | 未設定 | `ruff format --check` を local script と CI で実行 |
| mypy | 未設定 | Python 3.10 target で Option B 対象を typecheck |
| local entrypoint | なし | `scripts/static_analysis/run.sh` などの grouped script を追加 |
| Makefile | なし | `make lint` で grouped script を実行 |
| CI | pytest / spec-dock validate 中心 | provider CI に Ruff/mypy/static-analysis gate を追加 |
| pre-commit | なし | 今回は対象外。別 issue で導入 |

## 最終 pyproject.toml 設定イメージ案

この block は「最終的に目指す形」の draft であり、実装時は段階的に rule group を追加する。

```toml
[dependency-groups]
dev = [
  "pytest>=8.0",
  "ruff>=0.15",
  "mypy>=1.19",
  "typing-extensions>=4.12",
]

[tool.ruff]
target-version = "py310"
line-length = 120
indent-width = 4
preview = true
exclude = [
  "build/",
  "dist/",
  "*.egg-info/",
  ".git/",
  "__pycache__/",
  ".venv/",
  "venv/",
  "spec-dock/",
]

[tool.ruff.lint]
select = [
  "E",
  "F",
  "I",
  "UP",
  "B",
  "C4",
  "SIM",
  "PTH",
  "TC",
  "ARG",
  "RUF",
  "TID",
]
ignore = [
  "E501",
  "SIM108",
  "RUF010",
  "RUF001",
  "RUF002",
  "RUF003",
]

[tool.ruff.lint.flake8-unused-arguments]
ignore-variadic-names = true

[tool.ruff.lint.isort]
force-sort-within-sections = true
combine-as-imports = true

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"

[tool.ruff.lint.per-file-ignores]
"tests/**/*" = [
  "ARG",
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
docstring-code-format = true
line-ending = "auto"

[tool.mypy]
python_version = "3.10"
allow_redefinition = false
check_untyped_defs = true
color_output = true
error_summary = true
show_column_numbers = true
show_error_context = true
show_error_codes = true
pretty = true
ignore_missing_imports = true
exclude = [
  "^spec-dock/",
  "^build/",
  "^dist/",
  "^\\.venv/",
]

[[tool.mypy.overrides]]
module = "tests.*"
check_untyped_defs = false
disallow_untyped_defs = false
```

## 各設定項目の説明

### dev dependencies

| 設定 | 目的 | 採用理由 |
|---|---|---|
| `ruff` | lint / format / import sort を実行する | reference project の好みに合わせ、formatter と linter を一体で運用する |
| `mypy` | typecheck を実行する | Python code の型安全性を CI で保証する |
| `typing-extensions` | Python 3.10 で新しめの typing helper を使えるようにする | mypy の `explicit-override` 等を将来使う場合の互換補助。必要性は実装時に再確認 |

### `[tool.ruff]`

| 設定 | 目的 | 説明 |
|---|---|---|
| `target-version = "py310"` | Python 3.10+ 前提に合わせる | SpecDock の `requires-python = ">=3.10"` と整合させる |
| `line-length = 120` | 長めの業務/CLI code を読みやすく保つ | reference project と同じ 120 幅 |
| `indent-width = 4` | Python 標準の indent | 現行 style と整合 |
| `preview = true` | Ruff の preview rules/settings を使う | reference project の好みを踏襲。ただし導入時に不安定すぎる場合は design で調整可能 |
| `exclude = ["spec-dock/", ...]` | dogfooding copy を direct target から外す | Option B の合意に従う |

### Ruff rule groups

| Rule group | 段階 | 目的 | 代表的に検出するもの |
|---|---:|---|---|
| `F` Pyflakes | 1 | 明白な Python bug を検出 | 未定義名、未使用 import など |
| `E` pycodestyle errors | 1 | 基礎的な syntax/style error を検出 | 構文周辺の不整合 |
| `I` isort | 1 | import 順序を固定 | import order drift |
| `UP` pyupgrade | 2 | Python 3.10+ に合う書き方へ更新 | 古い typing / syntax |
| `B` flake8-bugbear | 2 | bug-prone pattern を検出 | mutable default など |
| `C4` comprehensions | 2 | comprehension の冗長さを整理 | 不要な list/dict wrapping |
| `SIM` simplify | 2 | 複雑すぎる条件・分岐を簡略化 | 冗長な if/else |
| `PTH` pathlib | 3 | path 操作を `pathlib` 寄りにする | `os.path` / raw path 操作 |
| `TC` type-checking imports | 3 | type-only import を整理 | runtime import と type import の混在 |
| `ARG` unused arguments | 3 | 不要な引数を検出 | 未使用 callback args 等。tests は一部緩める |
| `RUF` Ruff-native | 3 | Ruff 独自の有用 rule | subtle bug / modernization |
| `TID` tidy imports | 4 | import boundary を締める | 相対 import、禁止 import |

### Ruff ignore

| Ignore | 理由 |
|---|---|
| `E501` | 行長は formatter と human readability に委ね、lint failure にはしない |
| `SIM108` | if-expression 強制は可読性と衝突することがあるため、reference project と同様に許容 |
| `RUF010` | 明示的な f-string conversion を許容 |
| `RUF001` / `RUF002` / `RUF003` | 日本語 docs/comments を含む repo で ambiguous unicode noise を避ける |

### Ruff per-file ignores

| 対象 | Ignore | 理由 |
|---|---|---|
| `tests/**/*` | `ARG` | pytest fixture / parametrized tests / callback shape で未使用引数が自然に出るため |

### Ruff format

| 設定 | 目的 |
|---|---|
| `quote-style = "double"` | quote style を統一 |
| `indent-style = "space"` | Python 標準に合わせる |
| `skip-magic-trailing-comma = false` | formatter の標準挙動を活かす |
| `docstring-code-format = true` | docstring 内の code block も整形 |
| `line-ending = "auto"` | OS 差分による line ending churn を避ける |

### mypy

| 設定 | 目的 | 説明 |
|---|---|---|
| `python_version = "3.10"` | SpecDock の supported Python に合わせる | reference project の `3.12` は持ち込まない |
| `allow_redefinition = false` | 変数再定義の曖昧さを防ぐ | 型推論の事故を減らす |
| `check_untyped_defs = true` | annotation が不完全な関数内部も確認 | 初回導入の価値を上げる |
| `show_error_codes = true` | 修正・抑制の判断をしやすくする | report の violation inventory と相性がよい |
| `show_column_numbers = true` | error location を詳細化 | 修正時の探索コストを下げる |
| `show_error_context = true` | error 周辺文脈を出す | inventory 分類しやすくする |
| `pretty = true` | human-readable output | 段階的解消時に読みやすい |
| `ignore_missing_imports = true` | 外部 typed package noise を抑える | 初回導入では repo 内型エラー解消を優先 |
| `exclude` | dogfooding copy / build artifacts を除外 | Option B と generated artifact 方針に合わせる |

## 段階導入の設定グループ案

最終 `pyproject.toml` は上記を目指すが、実装計画では次の順序で有効化する。

| Phase | 追加する検査 | 目的 | 完了条件 |
|---|---|---|---|
| P0 | tool dependency + script + Makefile + CI skeleton | 実行導線を作る | grouped script が対象 phase を実行できる |
| P1 | `F`, `E`, `I` | 基礎 lint と import order | 検出違反 inventory を作り、0 件にする |
| P2 | `UP`, `B`, `C4`, `SIM`, selected `RUF` | modernization / bug-prone pattern | 検出違反 inventory を作り、0 件にする |
| P3 | `PTH`, `TC`, `ARG`, remaining `RUF` | path/type/import hygiene | 検出違反 inventory を作り、0 件にする |
| P4 | `TID` / import boundary | 相対 import と境界違反を締める | 検出違反 inventory を作り、0 件にする |
| P5 | `mypy` | 型エラー解消 | mypy error inventory を作り、0 件にする |
| P6 | `ruff format --check` / format application | format drift 解消 | format check が green |
| P7 | final all-in-one gate | local + CI と同じ最終確認 | `make lint` / CI static analysis が green |

## local script / Makefile target 案

### ファイル案

```text
scripts/
└── static_analysis/
    └── run.sh

Makefile
```

### `make lint` の役割

```makefile
.PHONY: lint

lint:
	@./scripts/static_analysis/run.sh
```

### grouped script の実行フェーズ案

script は reference project の `make lint` と同様に、途中で失敗しても可能な範囲で後続 phase を実行し、最後に summary と exit code を返す。

| Step | Command image | 説明 |
|---|---|---|
| 1 | `uv run ruff check --select ... <targets>` | 段階ごとの Ruff lint |
| 2 | `uv run ruff format --check <targets>` | format drift check |
| 3 | `uv run mypy <targets>` | typecheck |
| 4 | summary | 各 command の exit code を一覧化 |

### direct target set

```text
src/spec_dock
tests
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
```

`spec-dock/` dogfooding copy は direct target に含めない。

## 選択肢 / tradeoff (必須)
- Option A:
  - 内容:
    - 最終設定を一括で入れ、すべての違反を一度に inventory 化して修正する。
  - Pros:
    - 最終状態を早く確認できる。
  - Cons:
    - 違反種別が混ざり、修正 diff と review scope が大きくなりやすい。
- Option B:
  - 内容:
    - 最終設定を目標として持ちつつ、rule group を段階追加して各段階で 0 件に閉じる。
  - Pros:
    - SpecDock の `1 step = 1 review scope = 1 commit` と相性がよい。
    - 各段階の violation inventory と closure evidence を report に残しやすい。
  - Cons:
    - 一括方式より step 数と reviewer cycle が増える。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `requirement.md`: 最終 target set、CI enforcement、Makefile/script、pre-commit out-of-scope、全違反解消を acceptance criteria にする。
  - `design.md`: final `pyproject.toml` target、rule group、script/Makefile/CI design、dogfooding copy exclusion を明記する。
  - `plan.md`: staged rule-group adoption と violation inventory closure を step 化する。
- まだ proposal に留める理由:
  - これは canonical docs 作成前の読み物であり、実装時の実違反 inventory はまだ未観測。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - scope / non-scope / AC / EC
- `design.md`:
  - static analysis configuration design、file change plan、execution flow
- `plan.md`:
  - staged implementation steps and closure index
- `ADR`:
  - 不要。Issue-local implementation policy として閉じる。
- `report.md` Evidence Adoption Ledger:
  - この proposal を canonical docs へ採用した事実を記録する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger

## 推奨案 (必須)
- Option B: staged rule-group adoption を推奨する。
- 最終設定案はこの doc の `最終 pyproject.toml 設定イメージ案` を起点にする。
- 実装時は段階ごとに command を実行し、検出違反を `report.md` に inventory 化し、0 件にしてから次段階へ進む。
- formatter は独立 phase にし、semantic/type fixes と同じ commit に混ぜない。

## 推奨反映先 (必須)
- `requirement.md`:
  - AC: final target set で `ruff check`, `ruff format --check`, `mypy`, `make lint`, CI static-analysis gate が green。
  - Non-scope: pre-commit hook。
- `design.md`:
  - `pyproject.toml`, `scripts/static_analysis/run.sh`, `Makefile`, `.github/workflows/provider-ci.yml` の設計。
  - Rule group と段階導入順。
- `plan.md`:
  - P0-P7 を implementation steps として落とし込む。
  - 各段階の violation inventory と closure evidence を `report.md` に残す契約。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - research/interview/disc から canonical docs へ採用した evidence を記録。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Full dogfooding direct target: source-of-truth discipline と二重修正回避のため不採用。
  - pre-commit implementation: scope が大きいため今回 issue では不採用。
  - FastAPI / SQLAlchemy / Alembic / Celery 固有設定: SpecDock に該当しないため不採用。
  - Public docstring `D101` 系: 初回 static-analysis baseline を docstring 大量作成 issue にしないため、現時点では不採用候補。
- deferred:
  - pre-commit hook / hook installer / staged-file-aware quality gate。
  - import-linter 導入。まず Ruff `TID` / script / CI baseline で閉じる。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - この proposal の最終 target set、設定案、段階導入順、script/Makefile/CI scope を canonical docs へ採用する。
- 追加で作る discussion docs:
  - なし。次は canonical `requirement.md` / `design.md` / `plan.md` 作成へ進める。
