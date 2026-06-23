---
種別: interview
ID: "20260623t025015z-interview"
タイトル: "Static analysis enforcement entrypoint"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["iss-00225"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00225"
created_at: "2026-06-23T02:50:15Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: ["20260623t024024z-research", "20260623t024210z-interview"]
reflected_to: []
---

# 20260623t025015z-interview Static analysis enforcement entrypoint

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
    - Static analysis の完了条件を runnable command までにするか、CI/local quality gate までにするかが受け入れ条件を変える。
  - `design.md`:
    - `.github/workflows/provider-ci.yml`、`.github/workflows/ci.yml`、local script / pre-commit hook の扱いが変わる。
  - `plan.md`:
    - Config/fix step の後に CI wiring / docs update / verification step を入れるかが変わる。
  - `ADR`:
    - 現時点では ADR 候補ではない。CI quality gate 方針を長期 policy として固定する場合だけ候補。
- chat 上の軽微な一問では足りない理由:
  - 回答が issue scope、CI 変更有無、開発者 workflow、PR blocking behavior に影響するため、回答前に artifact として固定する。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - Ruff/mypy をどの entrypoint で強制するか。
- 回答が後続判断へ与える影響:
  - CI まで含める場合は PR の必須確認に近づく。command-only の場合は導入差分は小さいが、実行忘れを防ぐ保証は弱い。

## 質問 (必須)
- pressure-test question:
  - `iss-00225` の完了時点で、Ruff/mypy は「ローカルで実行できて green」なら十分か、それとも GitHub Actions / local quality gate で自動的に破れる状態まで必要か。
- 質問:
  - 今回の issue では Ruff/mypy を CI や local quality gate に組み込みますか？
- 回答してほしいこと:
  - 下の Option A/B/C のどれに近いか。必要なら組み合わせや修正案でもよい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `.github/workflows/provider-ci.yml`: 現在は Python 3.11 で `uv run pytest` のみを実行する。
  - `.github/workflows/ci.yml`: `spec-dock sync` と `spec-dock validate` を実行する。
  - `pyproject.toml`: 現在は Ruff/mypy 設定も dev dependency もない。
  - Preference source `.pre-commit-config.yaml`: branch protection と `scripts/pre_commit/run.sh` に集約する local pre-commit quality gate を持つ。
  - `20260623t024210z-interview-static-analysis-target-boundary.md`: Option B adopted; dogfooding `spec-dock/` copy is not a direct Ruff/mypy target.
- local context で解決できたこと:
  - SpecDock には現時点で repository root `scripts/` は見当たらない。
  - Existing GitHub Actions は Python quality checks を pytest 以外に実行していない。
- まだ人間判断が必要な理由:
  - CI/pre-commit の強制は開発運用上の product policy であり、単なる設定の可否だけでは決められない。

## 回答案 (必須)
- Option A:
  - Command-only baseline: `pyproject.toml` に Ruff/mypy 設定と dev dependencies を追加し、対象範囲の既存違反を修正する。CI/pre-commit への組み込みはこの issue では行わない。
- Option B:
  - CI-enforced baseline: Option A に加えて、GitHub Actions の provider CI などで `ruff check`, `ruff format --check`, `mypy` を実行し、PR で破れる状態にする。
- Option C:
  - Local quality gate + CI: Option B に加えて、pre-commit または project-local quality gate script を追加し、ローカルでも一括実行できる導線を作る。
- User refinement:
  - Adopt Option B for CI enforcement.
  - Do not implement pre-commit in this issue; track it as a separate future issue.
  - Include a repo-local script that runs static analysis in a staged/organized way.
  - Include a Makefile target that invokes that script, following the reference project's easy one-command workflow.

## Codex の分析 (必須)
- 判断軸:
  - PR での回帰防止、初回導入差分の大きさ、開発者体験、SpecDock の既存 CI simplicity、reference project との運用思想の近さ。
- tradeoff:
  - Option A は最小差分だが、静的解析が任意実行に留まる。
  - Option B は「正しく行われる状態」に近く、PR regressions を止められる。CI 差分は小さいが、既存違反を完全に直すまで merge 不能になる。
  - Option C は reference project の local quality gate 思想に最も近いが、SpecDock にはまだ root `scripts/` がないため、script/hook 設計まで scope が広がる。
- リスク:
  - CI-enforced にすると、mypy / Ruff の初回設定ミスが PR 全体を止める。
  - Local hook まで含めると、静的解析導入 issue が developer tooling / hook policy issue に膨らむ。
- 具体シナリオ / edge case:
  - CI だけに入れて local command docs が弱いと、開発者は push 後に初めて失敗を知る。
  - Local hook まで入れると、環境差分や hook installation の説明・検証が必要になる。

## Codex の推奨案 (必須)
- 推奨:
  - Option B を推奨する。
- 理由:
  - ユーザーの「静的解析は適切に行われる状態にしたい」「発生したエラーをすべて修正してほしい」という要求には、command-only より CI-enforced baseline が合う。一方で pre-commit / local quality gate script は SpecDock に既存導線がないため、初回 issue では過剰になりやすい。
- 未回答時の影響:
  - 暫定的には Option B 前提で requirement draft を作れるが、ユーザーが local pre-commit まで期待している場合、後から scope と design が増える。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User selected CI-enforced baseline and explicitly excluded pre-commit implementation from this issue. User added that this issue should still include a script for grouped/staged static analysis execution and a Makefile command to run it easily.
- 回答:
  - 「今回、オプションBを採用します。今後、プレコミットも行いますが、これはちょっと今回のissueの枠を超える変更が大きくなるため、プレコミットまでの実装は別issueにします。一方で、この参考のプロジェクト、体調費用プロジェクトは、メイクコマンドなどで静的解析、コマンド一発で実行できるようにしています。このまとめて実行するコマンドですね。まメイクコマンドが良いかもしれません。スクリプト、いずれにしてもスクリプト作成し、そのスクリプトを簡単に実行するためのメイクコマンド、メイクファイルの用意も行ってください。静的解析、まとめて段階的にですね、適切に行えるスクリプトの作成と、そのスクリプトを実行するメイクコマンド、用意してください。」
- 回答日時:
  - 2026-06-23

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - N/A

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - The answer resolves enforcement scope: CI is in scope; pre-commit is out of scope; a local script plus Makefile target is in scope as a developer entrypoint.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Acceptance criteria should require CI to run Ruff check, Ruff format check, and mypy over the adopted Option B target set.
  - Acceptance criteria should require a repo-local script for grouped/staged static analysis execution and a Makefile target that invokes it.
  - Non-scope should explicitly exclude pre-commit hook installation / pre-commit configuration from this issue.
- `design.md`:
  - Design should define the script path, script phases, summary/failure behavior, Makefile target name, and GitHub Actions integration.
  - Design should keep pre-commit as a future follow-up and avoid adding hook installation behavior.
- `plan.md`:
  - Plan should include separate steps for config/dependency setup, local script + Makefile target, CI wiring, Ruff fixes, mypy fixes, and final verification.
- `ADR`:
  - No ADR needed.
- reflected_to 更新方針:
  - Update `reflected_to` after canonical docs adopt this answer.
- adoption reflection:
  - Record this answer in `report.md` Evidence Adoption Ledger during requirement authoring.

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
