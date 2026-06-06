---
種別: 要件定義書（Issue）
ID: "iss-00167"
タイトル: "Migrate Tests To Pytest"
関連GitHub: ["#167"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["epic-00158", "init-local-00003"]
---

# iss-00167 Migrate Tests To Pytest — 要件定義（何を、なぜ行うか）

## 目的
- SpecDock provider repo のテスト実行基盤を Python 標準 `unittest` から `pytest` へ完全移行する。
- `iss-00160-reduce-test-runtime-followup` で整理された `tests/unit` / `tests/integration` / `tests/cli_runtime` の現行構成を前提に、CI、README、AGENTS、テストコード、ロックファイルの標準契約を pytest にそろえる。
- 移行後は標準のテスト入口が pytest だけで説明・実行でき、unittest runner や unittest-style assertion / fixture API に依存しない状態にする。

## 親 Epic への trace / 位置づけ
- この Issue は、`epic-00158 Agent Workflow PDCA Hardening` の first-wave skill / docs / templates cleanup を置き換えるものではない。
- 親 Epic `plan.md` は regression checks / manual harness / runtime gate を first-wave blocker から外し、later PDCA work として deferred にしている。本 Issue は、その deferred testing / regression infrastructure lane を、ユーザーの明示指示により pytest migration として起動する後段 Issue である。
- 親 Epic との対応:
  - E-RQ-006: first-wave decomposition と deferred work の境界を維持する。pytest migration は first-wave completion の blocker ではなく、後段 regression / harness work の土台として扱う。
  - E-RQ-007 / E-AC-006: provider-side source と dogfooding verification を守る。pytest 標準化後は provider repo の検証入口が `uv run pytest ...` に統一され、後続の shipped asset / workflow change の検証証跡が安定する。
  - E-AC-004 / E-AC-005: reviewer gate と evidence adoption boundary を運用上支える。テスト成功を `python -m unittest discover` ではなく pytest の決定的 command evidence として report / reviewer gate に残せるようにする。
- 採用する親側 evidence:
  - `spec-dock/active/epic/plan.md` の Deferred work / regression checks / manual harness / runtime gate 記述。
  - `spec-dock/active/epic/discussions/20260605t034636z-01-research-branch-d-codex-eval-ci-harness-patterns-deep-research-report.md` の deterministic gate evidence として `JUnit/pytest 成功` を扱う方針。
- 採用しない解釈:
  - この Issue を `iss-00159` など first-wave context-surface cleanup issue の代替にしない。
  - pytest migration 完了をもって skill spine regression checks、manual workflow scenario harness、runtime gate が実装済みになったとは扱わない。

## 背景・現状
- 現状の挙動:
  - `iss-00160` の merge により、軽量・単体寄りのテストは `tests/unit/`、外部境界の任意確認は `tests/integration/`、重い runtime / CLI 回帰は `tests/cli_runtime/` に整理されている。
  - ただし標準コマンドはまだ `python -m unittest discover` 系であり、`README.md`、`AGENTS.md`、`.github/workflows/provider-ci.yml` は unittest を正本として案内している。
  - `pyproject.toml` / `uv.lock` に pytest 依存や pytest 設定は存在しない。
  - 多数のテストファイルと `tests/cli_runtime/harness.py` は `unittest.TestCase`、`self.assert*`、`self.subTest`、`self.assertRaises*`、`unittest.main()`、`unittest.mock` に依存している。
- 現状の課題:
  - テスト分割は現在の設計に近づいたが、runner / assertion / fixture の基盤は unittest のままで、pytest の fixture、plain assert、parameterization、collection 制御を活かせない。
  - README / AGENTS / CI が unittest を案内しているため、新しいテスト追加や CI 保守時に古い前提が残る。
  - 「pytest でも unittest.TestCase を収集できる」互換経路だけでは、ユーザーが求める完全移行にならず、後続のテスト改善が二重基盤になる。
- 再現手順:
  1. `README.md` の Testing 節、`AGENTS.md` の Build / Testing Guidelines、`.github/workflows/provider-ci.yml` の test command を確認する。
  2. `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests README.md AGENTS.md .github/workflows pyproject.toml` を実行する。
  3. `rg -n "pytest" uv.lock pyproject.toml tests README.md AGENTS.md .github/workflows src/spec_dock/assets/install_root/.github/workflows` を実行する。
- 観測点:
  - CLI / test runner:
    - 標準コマンドが `uv run pytest tests/unit`、`uv run pytest tests/integration`、`uv run pytest tests/cli_runtime`、`uv run pytest` で説明・実行できる。
  - CI:
    - GitHub Actions / provider CI が pytest で全テストを実行する。
  - Docs:
    - README / AGENTS の Testing 節とテスト配置説明が現行ディレクトリと pytest 前提に一致する。
  - Code:
    - `tests/` 配下のテスト実装から unittest runner / unittest-style API 依存が除去されている。
  - Config / lock:
    - pytest 依存と discovery 設定が project metadata / lock に残っている。
- 情報源:
  - `git log --oneline --decorate --graph -12`
  - `git diff --name-status --find-renames 7ea10f7c..2a27a8eb -- tests`
  - `find tests -type f -name '*.py' | sort`
  - `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests README.md AGENTS.md .github/workflows pyproject.toml`
  - `rg -n "pytest" uv.lock pyproject.toml tests README.md AGENTS.md .github/workflows src/spec_dock/assets/install_root/.github/workflows`
  - read-only `repo-analyst` 調査結果（2026-06-06）

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock provider repo の開発者、レビュー担当者、CI 保守者、テストを追加する coding agent。
- 代表シナリオ:
  - 開発者が局所変更後に `uv run pytest tests/unit` で日常単体 suite を実行する。
  - CI が unit、integration、runtime / CLI regression を含む provider test suite 全体を pytest で実行する。
  - runtime / CLI 変更時に `uv run pytest tests/cli_runtime` または `uv run pytest` で重い回帰 suite を実行する。
  - integration 境界を確認したいときに `uv run pytest tests/integration` を任意実行する。

## スコープ
- 必須:
  - pytest を開発・テスト用依存として導入し、`uv.lock` を更新する。
  - `pyproject.toml` に pytest discovery / warning / option の最小設定を置き、現行 `tests/` 構成を pytest の標準入口で収集できるようにする。
  - `tests/unit`、`tests/integration`、`tests/cli_runtime` の現行 test files と共有 harness を pytest idiom へ移行する。
  - `unittest.TestCase` 継承、`self.assert*`、`self.assertRaises*`、`self.subTest`、`unittest.main()`、`unittest.mock` 依存を pytest の plain assert、`pytest.raises`、`pytest.mark.parametrize`、fixture / `monkeypatch` / `tmp_path` 等へ置き換える。
  - README / AGENTS / provider CI / テスト内のコマンド文字列を pytest 標準へ更新する。
  - `iss-00160` 後の `tests/unit` / `tests/integration` / `tests/cli_runtime` の分類を維持し、旧 layout へ戻さない。
  - 移行に伴う空ディレクトリや pycache 由来の残骸が pytest collection / docs / CI を誤誘導する場合は、安全に除去または無視方針を明示する。
- 禁止:
  - unittest runner を正式 fallback として残す。
  - pytest 互換 collection に頼り、`unittest.TestCase` / `self.assert*` / `unittest.main()` を温存して完全移行とみなす。
  - テスト削除、skip / xfail の濫用、検証対象の縮小で migration を通ったように見せる。
  - `iss-00160` で作られたテスト分類を旧 `tests/test_*.py`、`tests/domain_runtime`、`tests/presentation_runtime` 中心へ戻す。
  - 本 issue の目的と無関係な runtime / CLI の機能変更、広範 refactor、テスト高速化施策を混ぜる。
- 対象外:
  - pytest-xdist、coverage、hypothesis など pytest 以外の新規テスト関連 plugin 導入。
  - runtime 挙動や CLI public contract の変更。
  - テスト実行時間そのものの追加最適化。
  - 親 Epic first-wave の skill / docs / templates cleanup、hub / leaf routing、clarification workflow 改修の代替実装。
  - `Add Skill Spine Regression Checks`、`Add Manual Workflow Scenario Harness`、runtime gate / `gate status` / issue start-finish guards の実装。
  - provider CI 以外の shipped consumer CI を pytest runner に変えること。ただし shipped CI の説明・存在確認が今回の変更と衝突しないかは確認する。
  - GitHub Actions matrix や Python version policy の拡張。

## 境界
- 常に行う:
  - `iss-00160` merge 後の現行ファイル配置を正として requirement / design / plan を作る。
  - pytest 移行後の標準コマンド、CI、docs、テスト実装の整合を同時に確認する。
  - テストの検出感度を下げず、既存の coverage intent と失敗検出力を維持する。
  - 変更した step ごとに、pytest による観測可能な検証コマンドを用意する。
- 判断が必要:
  - `tests/cli_runtime` の個別実行を日常標準に含めるか、フル回帰 / runtime 変更時の重いレーンとして扱うか。
  - 空の `tests/domain_runtime` / `tests/presentation_runtime` ディレクトリや既存 `__pycache__` を削除する必要があるか。
  - 大きい unittest-style test file を一括変換するか、pytest fixture 化のために step 分割するか。
- 行わない:
  - 互換的に pytest で unittest tests を走らせるだけで完了扱いにしない。
  - 実装中に新しい fixture / helper の抽象を過剰に作らない。
  - docs だけを pytest に書き換えて test code / CI の移行を後続へ残さない。

## 非交渉制約
- Python 3.10+ の project policy を維持する。
- テストは hermetic であり、既存どおり temp directory と `gh` stub / fake harness を使い、live network / credentialed GitHub access に依存しない。
- provider-side source of truth と dogfooding workspace の境界を守る。
- 完全移行の完了条件は pytest commands の pass と、unittest runner / API 依存の除去で判断する。
- Fresh `spec-reviewer` pass なしに requirement -> design -> plan -> execution へ進めない。

## 前提
- `iss-00160-reduce-test-runtime-followup` は main に merge 済みで、この issue branch に main が統合済みである。
- 現在の canonical issue docs は template 状態に戻っており、本 requirement は `iss-00160` 後の現物を前提に再作成する。
- ユーザーは「オプションC」、つまり pytest への完全移行を選択済みである。
- `tests/unit` は日常単体レーン、`tests/integration` は外部境界レーン、`tests/cli_runtime` は runtime / CLI regression の重いレーンとして扱う。GitHub Actions / provider CI ではこれらを含む full pytest suite を実行する。
- 親 Epic の first-wave scope は維持する。この Issue は後段の testing / regression infrastructure work として扱い、first-wave closure criteria を変更しない。

## 受け入れ条件
- AC-001: pytest 依存と標準 discovery が導入される。
  - アクター: 開発者 / CI。
  - 前提: clean checkout に project dependencies を解決できる。
  - 操作: `uv run pytest --version` と `uv run pytest --collect-only` を実行する。
  - 期待結果: pytest が lock 済み依存として利用でき、`tests/unit`、`tests/integration`、`tests/cli_runtime` の対象 tests が pytest collection で検出される。
  - 観測点: `pyproject.toml`、`uv.lock`、pytest collect output。
- AC-002: GitHub Actions / provider CI の標準入口が full pytest suite へ移行する。
  - アクター: 開発者 / provider CI。
  - 前提: `tests/unit` が `iss-00160` 後の配置で存在する。
  - 操作: GitHub Actions / provider CI の test step、または同等の local command として `uv run pytest` を実行する。
  - 期待結果: unit、integration、runtime / CLI regression を含む full suite が pytest で pass し、provider CI も同じ full-suite pytest entrypoint を使う。
  - 観測点: command output、`.github/workflows/provider-ci.yml`。
- AC-003: integration suite の任意入口が pytest へ移行する。
  - アクター: 開発者 / reviewer。
  - 前提: integration tests は live 外部依存なしに hermetic な discovery / boundary smoke を持つ。
  - 操作: `uv run pytest tests/integration` を実行する。
  - 期待結果: integration suite が pytest で pass する。
  - 観測点: command output、README / AGENTS の案内。
- AC-004: runtime / CLI regression lane が pytest で実行できる。
  - アクター: runtime / CLI 変更の実装者。
  - 前提: `tests/cli_runtime` の heavy tests が現行 harness を持つ。
  - 操作: `uv run pytest tests/cli_runtime` を実行する。
  - 期待結果: runtime / CLI regression lane が pytest で pass する。
  - 観測点: command output、移行後 harness。
- AC-005: full regression fallback が pytest へ移行する。
  - アクター: release / integration reviewer。
  - 前提: unit、integration、cli_runtime の各 lane が pytest で実行可能である。
  - 操作: `uv run pytest` を実行する。
  - 期待結果: full suite が pytest で pass し、README / AGENTS の full regression command と GitHub Actions / provider CI も pytest full-suite execution を案内・実行する。
  - 観測点: command output、README / AGENTS、`.github/workflows/provider-ci.yml`。
- AC-006: テストコードから unittest framework 依存が除去される。
  - アクター: reviewer。
  - 前提: migration 実装後の working tree。
  - 操作: `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests` を実行する。
  - 期待結果: unittest runner / framework / assertion API 依存が検出されない。標準ライブラリ由来の文字列がコメントや docs に残る場合は、pytest 移行と衝突しない理由が report に記録されている。
  - 観測点: `rg` output、report の例外記録。
- AC-007: docs / CI のテスト契約が pytest と現行配置に一致する。
  - アクター: 新規 contributor / coding agent。
  - 前提: README、AGENTS、provider CI、テスト内の command assertions を読む。
  - 操作: テスト実行案内と CI workflow を確認する。
  - 期待結果: unittest コマンドや旧 `tests/test_cli.py` / `tests/test_init_update.py` の案内が残らず、pytest と `tests/unit` / `tests/integration` / `tests/cli_runtime` の分類が一致している。
  - 観測点: `rg -n "unittest discover|Framework: `unittest`|tests/test_cli.py|tests/test_init_update.py" README.md AGENTS.md .github/workflows tests`。
- AC-008: 移行は既存 coverage intent を維持する。
  - アクター: reviewer / qa-reviewer。
  - 前提: unittest から pytest への構文・fixture migration を行う。
  - 操作: 差分と pytest 実行結果を確認する。
  - 期待結果: テスト削除、不要な skip / xfail、assertion 弱体化、外部依存追加によって検出力を落としていない。
  - 観測点: git diff、pytest output、qa-reviewer verdict。
- AC-009: 親 Epic の deferred work 境界と衝突しない。
  - アクター: spec-reviewer / orchestrator。
  - 前提: pytest migration の issue docs と親 Epic requirement / plan / report を読む。
  - 操作: 親 Epic trace と対象外を確認する。
  - 期待結果: この Issue が first-wave skill / docs / templates cleanup を置き換えず、後段 testing / regression infrastructure lane として位置づけられている。
  - 観測点: この requirement の `親 Epic への trace / 位置づけ`、`スコープ`、`対象外`、report の Spec Authoring Gate。

## 例外・エッジケース
- EC-001: pytest collection と unittest discovery の差。
  - 条件: pytest の discovery 設定が広すぎる、または狭すぎる。
  - 期待: `tests/` 配下の対象 test files は収集され、fixtures / wheelhouse / pycache / 非 test helper は誤収集されない。
  - 観測点: `uv run pytest --collect-only`。
- EC-002: `self.subTest` から pytest parameterization への移行。
  - 条件: 1 test 内で複数ケースを subTest していた箇所を移行する。
  - 期待: ケース単位の失敗可視性を維持し、1 ケース失敗で他ケースの意図が隠れない。
  - 観測点: `pytest.mark.parametrize` または明示的 helper / loop と assertion message。
- EC-003: `assertRaisesRegex` / exception assertion の移行。
  - 条件: 例外種別と message regex を同時に検証していた箇所。
  - 期待: `pytest.raises(..., match=...)` 等で同等以上の失敗検出力を維持する。
  - 観測点: test diff、pytest failure readability。
- EC-004: patch / temp directory helper の移行。
  - 条件: `unittest.mock.patch`、`tempfile.TemporaryDirectory`、`setUp` / `tearDown` 相当の処理がある。
  - 期待: pytest fixture、`monkeypatch`、`tmp_path`、context manager に移行し、cleanup と isolation を維持する。
  - 観測点: fixture implementation、pytest pass。
- EC-005: heavy runtime tests の実行時間。
  - 条件: `tests/cli_runtime` または full suite が時間を要する。
  - 期待: 完全移行のため pytest 実行可能性は必須だが、性能最適化は本 issue の主目的にしない。
  - 観測点: `uv run pytest tests/cli_runtime`、`uv run pytest` の結果と report。
- EC-006: 旧空ディレクトリ / pycache の扱い。
  - 条件: `tests/domain_runtime` / `tests/presentation_runtime` などに test file がない、または `__pycache__` が残っている。
  - 期待: pytest collection / docs / CI に影響しない場合は scope creep しない。影響する場合のみ除去または無視設定を行う。
  - 観測点: `find tests -maxdepth 2 -type d | sort`、pytest collect output、git diff。
- EC-007: docs / tests 内の文字列検査。
  - 条件: 既存 tests が README / CI の command string を assertion している。
  - 期待: その assertion も pytest 標準 command へ更新され、古い unittest command を期待しない。
  - 観測点: focused pytest output と `rg`。

## 入力→出力例
- EX-001: 日常単体 test command。
  - 入力: `uv run pytest tests/unit`
  - 出力: `tests/unit` 配下の pytest suite が pass。
- EX-002: 任意 integration test command。
  - 入力: `uv run pytest tests/integration`
  - 出力: integration boundary smoke が pass。
- EX-003: runtime / CLI regression command。
  - 入力: `uv run pytest tests/cli_runtime`
  - 出力: heavy runtime / CLI tests が pass。
- EX-004: full regression fallback。
  - 入力: `uv run pytest`
  - 出力: 全 pytest suite が pass。

## 用語（ドメイン語彙）
- TERM-001: pytest 完全移行
  - pytest を runner / assertion / fixture / docs / CI の正本にし、unittest runner / unittest-style API 依存を正式経路から除去した状態。
- TERM-002: unit lane
  - `tests/unit` 配下の日常開発用の軽量 suite。CI full suite の一部としても実行される。
- TERM-003: integration lane
  - `tests/integration` 配下の任意の境界確認 suite。live credentialed external access を必須にしない。
- TERM-004: runtime / CLI regression lane
  - `tests/cli_runtime` 配下の重い SpecDock runtime / CLI behavior suite。
- TERM-005: full regression fallback
  - `uv run pytest` によって対象テスト全体を pytest で実行する回帰確認。

## 未確定事項
- Blocking question:
  - なし。
  - ユーザーは pytest への完全移行を選択済みであり、`iss-00160` 後の現行 test layout は repo の一次情報で確認済みのため、requirement phase で追加インタビューは不要。
- Non-blocking design / plan questions:
  - 大規模 test file の変換順と helper 抽出の最小単位。
  - 空ディレクトリ / pycache の cleanup 要否。
  - full suite 実行時間が長い場合の report 証跡の残し方。
