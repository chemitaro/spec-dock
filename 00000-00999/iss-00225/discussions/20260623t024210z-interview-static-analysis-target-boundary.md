---
種別: interview
ID: "20260623t024210z-interview"
タイトル: "Static analysis target boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["iss-00225"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00225"
created_at: "2026-06-23T02:42:10Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: ["20260623t024024z-research"]
reflected_to: []
---

# 20260623t024210z-interview Static analysis target boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Ruff/mypy を「どの Python surface に対して green にするか」が acceptance criteria と scope/non-scope を決める。
  - `design.md`:
    - `pyproject.toml` の target、exclude、per-file ignores、layer boundary rule、mypy invocation の設計が変わる。
  - `plan.md`:
    - format-only step、Ruff manual fixes、mypy fixes、dogfooding refresh、CI/pre-commit integration の順序と分量が変わる。
  - `ADR`:
    - 現時点では ADR 候補ではない。Python quality gate を product policy として長期固定する場合のみ候補。
- chat 上の軽微な一問では足りない理由:
  - 回答が issue scope、完了条件、修正対象、レビュー単位、将来の CI/pre-commit 連携に波及するため、回答前に artifact として未回答状態を固定する。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `iss-00225` で Ruff/mypy の初回 green baseline を作る対象範囲。
- 回答が後続判断へ与える影響:
  - 対象範囲が広いほど、初回修正量・format 差分・mypy noise・dogfooding copy の扱いが増える。対象範囲が狭いほど、導入は安全だが静的解析の保証範囲が限定される。

## 質問 (必須)
- pressure-test question:
  - 「静的解析を適切に行われる状態」とみなすために、初回から dogfooding workspace / shipped runtime copy まで直接 green にする必要があるか。
- 質問:
  - 今回の `iss-00225` の合格条件として、Ruff/mypy の対象範囲はどこまでにしますか？
- 回答してほしいこと:
  - 下の Option A/B/C のどれに近いか。必要なら組み合わせや修正案でもよい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `AGENTS.md`: provider source of truth は `src/spec_dock/`。dogfooding workspace `spec-dock/` は検証・反映対象であり、通常は provider を先に編集する。
  - `pyproject.toml`: 現在は pytest 設定のみで、Ruff/mypy 設定・dev dependency はない。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`: consumer repo に copied runtime として出る Python code が provider asset 内にある。
  - `/Volumes/990p2t/workspace/product/taikyohiyou_project/taikyohiyou_management_api/pyproject.toml`: Ruff/mypy を厳しめの品質ゲートとして運用している先例。
  - `20260623t024024z-research-ruff-mypy-preference-source-analysis.md`: preference source と SpecDock への適用候補の整理。
- local context で解決できたこと:
  - FastAPI / SQLAlchemy / Alembic / Celery 固有設定は SpecDock に直接持ち込まない。
  - Python version target は SpecDock の `requires-python = ">=3.10"` に合わせる。
  - Preference source の layer-boundary 思想は、SpecDock の `cli/commands/application/domain/infra/presentation` に翻訳する候補。
- まだ人間判断が必要な理由:
  - 「適切に静的解析される状態」が provider source only なのか、generated dogfooding workspace も直接含むのかは product operation policy の判断であり、ローカル source だけでは決められない。

## 回答案 (必須)
- Option A:
  - Provider-first scope: `src/spec_dock/**/*.py` と `tests/**/*.py` を Ruff/mypy green にする。`spec-dock/` dogfooding workspace は provider 変更後の `spec-dock update .` / validation / inspection 対象に留め、直接 lint/typecheck target にはしない。
- Option B:
  - Provider + shipped runtime explicit scope: `src/spec_dock/**/*.py`, `tests/**/*.py`, かつ shipped runtime asset `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**/*.py` を明示的に green にする。dogfooding copy `spec-dock/scripts/...` は直接 target にしない。
- Option C:
  - Full dogfooding scope: provider source、tests、dogfooding workspace の copied runtime `spec-dock/scripts/spec_dock_runtime/**/*.py` まで Ruff/mypy target に含め、consumer-visible copy も直接 green にする。

## Codex の分析 (必須)
- 判断軸:
  - Source-of-truth discipline、初回修正量、mypy import/package 解決の安定性、dogfooding parity の可視性、CI/runtime コスト。
- tradeoff:
  - Option A は source-of-truth とレビュー容易性が最も安定するが、consumer-visible copy を直接静的解析する保証は弱い。
  - Option B は shipped runtime を provider asset として明示でき、SpecDock の実体に合う。`src/spec_dock/assets/...` が通常 package code と少し異なるため mypy invocation 設計が必要。
  - Option C は保証範囲が最大だが、generated/copy 側を直接修正したくなる圧力や二重エラー、path/package 解決の noise が増える。
- リスク:
  - Full scope を最初から採ると、静的解析設定 issue が dogfooding copy・generated assets・package discovery の整理 issue へ膨らむ。
  - Scope を狭くしすぎると、ユーザーが期待する「SpecDock runtime が静的解析されている」状態に届かない。
- 具体シナリオ / edge case:
  - Ruff format が provider asset と dogfooding copy の双方に似た差分を出す場合、provider-first で修正し dogfooding refresh するのか、両方を direct target にするのかで作業方法が変わる。
  - mypy が copied runtime を別 package として解釈し、provider asset と dogfooding copy で duplicate module 的な noise を出す可能性がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option B を推奨する。
- 理由:
  - SpecDock の価値は shipped runtime に強く依存するため、provider package と tests だけでなく `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**/*.py` を静的解析対象として明示するのがよい。一方で `spec-dock/` dogfooding copy は source-of-truth ではないため、直接 lint target ではなく refresh/validate/inspection の確認対象にする方が二重修正を避けやすい。
- 未回答時の影響:
  - 暫定的には Option B 前提で requirement draft を作れるが、もしユーザーが Option C を期待している場合、後から acceptance criteria と verification plan の組み替えが必要になる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User selected Option B: include provider source, tests, and shipped runtime asset in the static analysis target, and do not include the dogfooding `spec-dock/` copy as a direct Ruff/mypy target.
- 回答:
  - 「オプションBを採用します。ドックフーディングのスペックドックの部分は対象に含めません。」
- 回答日時:
  - 2026-06-23

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Whether `iss-00225` should wire Ruff/mypy into CI and/or a local quality gate, or only add runnable commands/configuration and fix the current baseline.

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - User intent directly resolves the target boundary. Option B matches provider source-of-truth discipline while still treating the shipped runtime asset as an explicit static analysis target.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Scope should include `src/spec_dock/**/*.py`, `tests/**/*.py`, and `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**/*.py`.
  - Scope should explicitly exclude dogfooding copy `spec-dock/` from direct Ruff/mypy targets.
- `design.md`:
  - Static analysis command design should avoid duplicate provider/dogfooding targets and should make shipped runtime asset coverage explicit.
- `plan.md`:
  - Verification steps should run Ruff/mypy over the accepted Option B target set and separately run SpecDock validation / dogfooding inspection as needed.
- `ADR`:
  - No ADR needed for this answer alone.
- reflected_to 更新方針:
  - Update `reflected_to` after canonical docs adopt this answer.
- adoption reflection:
  - Record the adoption in `report.md` before or during canonical requirement authoring.

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
