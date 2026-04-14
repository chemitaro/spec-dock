---
種別: 実装計画書（Issue）
ID: "iss-00072"
タイトル: "Legacy authority retirement and final spec close"
関連GitHub: ["#72"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-14"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00072 Legacy authority retirement and final spec close — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
- 制約:
  - current authority uniqueness は code/tests/current docs/report evidence の 4 面で説明する
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` を provider-side authoritative manifest として必ず確認する
  - historical closed issue/report/discussion は rewrite しない
  - issue-72 で変更した docs / mirror-affecting surfaces は `spec-dock update` 後の fresh convergence evidence を残す

## マイルストーン一覧
- M1:
  - 対象:
    - issue docs readiness
  - exit:
    - requirement / design / plan が spec review pass で固定される
- M2:
  - 対象:
    - authority retirement and legacy tree deletion
  - exit:
    - `tests/test_init_update.py` と `AGENTS.md` から legacy authority assumption が retire され、`src/spec_dock/assets/codex_skills/` が削除される
- M3:
  - 対象:
    - PR review remediation
  - exit:
    - review analyses A-D に対応する修正方針が実装可能な step と validation に落ち、spec review で矛盾なく説明できる
- M4:
  - 対象:
    - closeout evidence and final spec close docs
  - exit:
    - issue-72 report と必要な current closeout docs が evidence-bearing で揃い、final quality gates を pass する

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - 先に issue-72 docs contract を固定し、次に current tests/guidance の authority retirement と legacy tree deletion を行い、最後に closeout docs/report を揃える
  - final close gate は upstream issue-69/70/71 evidence と issue-72 自身の変更結果の両方を必要とするため、report 集約は最終段に置く
- step ordering notes:
  - S01 は current tests/guidance の authority cleanup
  - S02 は mirror-affecting docs / closeout docs の current statement を揃える
  - S03 は PR review remediation を S90 / S99 の前に差し込み、mandatory の `B` / `D` と ancillary の `A` / `C` を処理する
  - S90/S99 で update convergence、final reviews、epic close evidence を固める
  - detailed section の記載順は編集都合で前後しうるが、実行順序の正本はこの step ordering notes と `## ステップ一覧` とする

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - current tests と repo guidance が `install_root` を current authority として扱い、`codex_skills` を authority source/path や surviving physical tree として期待しない
  - closes:
    - AC-001
    - EC-001
  - review gate:
    - code review pass
- S02:
  - 観測可能な振る舞い:
    - current closeout docs が authority uniqueness / historical boundary / future host extension / upstream prerequisites を issue-72 close gate として辿れる
  - closes:
    - AC-002
    - AC-003
    - AC-004
    - EC-002
  - review gate:
    - code review pass
- S03:
  - 観測可能な振る舞い:
    - PR review で出た `B` / `D` の mandatory remediation と `A` / `C` の ancillary remediation が、既存 closeout contract を壊さずに実装・検証できる状態で固定される
  - closes:
    - AC-001
    - AC-004
  - review gate:
    - spec review pass
- S90:
  - 観測可能な振る舞い:
    - issue-72 で変更した docs / mirror-affecting surfaces が `spec-dock update` 後に dogfooding mirror へ収束する
  - closes:
    - AC-001
    - AC-004
  - review gate:
    - spec review input completion
- S99:
  - 観測可能な振る舞い:
    - final code review / final spec review / quality gates が pass し、issue-72 report に close-ready evidence が残る
  - closes:
    - AC-002
    - AC-004
  - review gate:
    - final code review pass
    - final spec review pass
  - supplemental repair loop:
    - full-suite residual が issue-72 実行中に再現した場合は、まずそれが issue-72 変更により導入・顕在化した回帰かを切り分ける
    - issue-72 起因の回帰だと証明できた場合のみ、failing test を単体再現し、failure / root cause / options / recommended fix を独立 analysis report に記録してから修正に進む
    - issue-72 起因だと証明できない residual は report に informational risk として記録し、別 issue / follow-up へ切り出す
    - layering contract 違反が issue-72 起因で再現した場合は、test 緩和よりも実装修正を優先し、commands/application/domain/presentation の境界を維持する
    - current residual target:
      - `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
    - preferred fix:
      - commands 層から `domain.ids` 直 import を除去する局所修正
    - analysis source of truth:
      - `discussions/20260414t012350z-research-runtime-shell-structural-regression-analysis.md`
## 要件 ↔ ステップ対応
- AC-001 -> S01, S03, S90
- AC-002 -> S02, S99
- AC-003 -> S02
- AC-004 -> S02, S03, S90, S99
- EC-001 -> S01
- EC-002 -> S02

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S01 完了後
    - S02 完了後
    - S99 final diff
  - scope:
    - 当該 step の code/docs/test diff
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してコミットする
- SG1 spec review:
  - timing:
    - requirement / design fix 後
    - plan 作成後
    - S99 final close 前
  - scope:
    - issue-72 `requirement.md` / `design.md` / `plan.md` / `report.md`
  - commit gate:
    - pass まで review loop を回す
- QG1 validation gate:
  - timing:
    - S01 / S02 / S03 / S90 / S99
  - scope:
    - targeted unittest:
      - current authority assertion hit がある場合のみ実行
      - hit が無ければ `該当なし` を report に記録
    - scoped search
    - `spec-dock update`
    - `spec-dock validate`
    - 必要なら `spec-dock sync --github`
  - commit gate:
    - pass した command / test 結果を `report.md` に記録してからコミットする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に spec review pass まで固定する
- 各 step は 1 つの観測可能な振る舞いに閉じる
- 各 step 完了時に `report.md` へ reviewer verdict / command / test / commit を記録する
- docs 変更が provider-side に入る場合は S90 で dogfooding mirror 収束を確認する
- 最後に `git diff <base>...HEAD` を対象に S99 final diff review quality gate を実施する
- no-op 判定は report に理由を残した場合だけ許可する

## 実装ステップ

### S01 — current authority assumptions retirement
- target:
  - `tests/test_init_update.py`
  - `AGENTS.md`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `src/spec_dock/assets/codex_skills/`
- design refs:
  - `design.md`:
    - `既存実装 / 規約の理解`
    - `legacy reference verification contract`
    - `要件 → 設計マッピング`
- step boundary:
  - current tests / repo guidance から `codex_skills` を expected source/path/current authority とみなす記述を retire する
  - deletion readiness contract を満たしたうえで `src/spec_dock/assets/codex_skills/**` を削除する
  - provider-side authoritative manifest を review し、current metadata source が legacy authority に戻っていないことを execution evidence に含める
  - CLI/runtime tests は scoped search で current authority assertion が見つかった場合だけ対象化し、hit がなければ `該当なし` を report に記録する

#### B1 — authority search and contract cleanup
- purpose:
  - current tests / guidance に残る legacy authority assumption を `install_root` 基準へ揃え、provider-side manifest review を execution evidence に組み込む
- files:
  - `tests/test_init_update.py`
  - `AGENTS.md`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `src/spec_dock/assets/codex_skills/`

##### I0 — provider-side manifest verification
- slice goal:
  - asset-side acceptance check を implementation gate として明示実行する

###### Red
- failing test:
  - manifest review 未実施の状態
- expected failure:
  - issue-72 report に provider-side authority artifact review の一次証跡が残らない

###### Green
- minimum implementation:
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` を authoritative manifest として inspect する
  - current metadata source が `codex_skills` に戻っていないことを report に残す
  - package install contract と current inventory contract が `codex_skills` deletion に耐えることを確認する
- pass condition:
  - asset-manifest verification result が S01 report / S99 final gate の両方から辿れる

###### Refactor
- 目的:
  - asset-side verification wording を authority uniqueness evidence と揃える

##### I1 — tests authority contract cleanup
- slice goal:
  - `tests/test_init_update.py` の expected source/path assumptions を current authority contract に一致させる

###### Red
- failing test:
  - legacy assumption を示す targeted tests / assertions の確認
- expected failure:
  - `codex_skills` current authority 前提が issue-72 scoped search で残る

###### Green
- minimum implementation:
  - parity / duplicate / bundled-asset assertions を `install_root` 基準へ更新する
  - legacy duplicate existence や physical tree presence を期待する assertion は cutover evidence ベースへ置換する
- pass condition:
  - issue-72 targeted tests と scoped search が pass

###### Refactor
- 目的:
  - helper や constants の current authority wording を揃える
- guardrail:
  - production code へ広げない

##### I2 — repo guidance cleanup
- slice goal:
  - `AGENTS.md` の provider-side directory map と説明を現行 authority model に一致させる

###### Red
- failing test:
  - issue-72 scoped search / docs review
- expected failure:
  - `AGENTS.md` が `codex_skills` を current provider map に残す

###### Green
- minimum implementation:
  - provider-side directory map を `install_root` / `spec_dock` current model に更新
  - `codex_skills` は deleted legacy tree として説明し、現 repo に存在しないことを current guidance で明示する
- pass condition:
  - `AGENTS.md` が issue-72 requirement/design と整合する

###### Refactor
- 目的:
  - wording を current docs corpus と揃える
- guardrail:
  - repo guideline の意図を崩さない

##### I3 — legacy tree physical deletion
- slice goal:
  - deletion readiness contract を満たした状態で `src/spec_dock/assets/codex_skills/` を削除し、current repo surface から legacy tree を除去する

###### Red
- failing test:
  - `codex_skills` physical tree を expected inventory に含める current tests / docs / packaging assumptions
- expected failure:
  - deletion 後に targeted tests または current docs assertions が崩れる

###### Green
- minimum implementation:
  - `src/spec_dock/assets/codex_skills/` を削除する
  - current docs と tests を deletion-aware contract へ更新する
  - current surface search で `src/spec_dock/assets/codex_skills/` path が historical records 外に残らないことを確認する
- pass condition:
  - targeted tests、scoped search、必要な package/install smoke が pass

###### Refactor
- 目的:
  - residual historical mention と current contract mention の境界を report から再現できるようにする

#### step gate
- review:
  - code_reviewer で S01 diff を review
- expected tests:
  - issue-72 authority cleanup targeted tests
  - scoped `rg "codex_skills"` current-surface search
  - provider-side authoritative manifest review
  - relevant CLI/runtime tests:
    - scoped search で current authority assertion hit がある場合のみ targeted 実行
    - hit が無ければ `該当なし` として report に記録
- report update:
  - S01 の修正内容、search classification、provider-side manifest review、review verdict、test結果を `report.md` に残す
- commit:
  - S01 差分をコミットする

### S02 — current closeout docs and final evidence wiring
- target:
  - issue-72 `report.md`
  - `spec-dock/active/epic/report.md`
  - issue-70 current report を含む current closeout docs
- design refs:
  - `final report contract`
  - `final close gate`
  - `current docs corpus contract`
- step boundary:
  - issue-72 acceptance traceability と epic final close evidence を current docs で矛盾なく辿れる状態にする

#### B1 — report and closeout docs materialization
- purpose:
  - issue-72 report required sections を evidence-bearing にする
- files:
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/epic/report.md`
  - current closeout docs required by the issue-72 evidence chain

##### I1 — issue-72 report skeleton to evidence-bearing contract
- slice goal:
  - report の required sections を current repo evidence で埋められる下地を作る

###### Red
- failing test:
  - report required fields completeness review
- expected failure:
  - `pending_until_execution` のまま close gate を満たせない

###### Green
- minimum implementation:
  - 実装記録欄と required sections の埋め方を concrete evidence contract に更新する
  - upstream epic/issue refs / contradiction summary / final-close-gate checks を具体化する
- pass condition:
  - spec review が issue-72 report contract を追跡できる

###### Refactor
- 目的:
  - duplicate wording を減らし evidence chain を読みやすくする

##### I2 — current closeout docs reconciliation
- slice goal:
  - issue-72 acceptance traceability を壊す current closeout docs の残存不整合を最小修正する

###### Red
- failing test:
  - scoped docs review
- expected failure:
  - pending/fake-final wording が current close chain に残る

###### Green
- minimum implementation:
  - issue-70 current report と epic current report を含む、issue-72 の evidence chain に必要な current docs を最小修正する
- pass condition:
  - issue-72 report から upstream prerequisites と final-close-gate が矛盾なく辿れる

###### Refactor
- 目的:
  - closeout docs の current/historical boundary を揃える

#### step gate
- review:
  - code_reviewer で S02 diff を review
- expected tests:
  - scoped docs search
  - issue-72 report completeness checks
  - epic current report completion check:
    - `spec-dock/active/epic/report.md` の `進捗サマリー`
    - `完了した Issue / PR / Release`
    - `受け入れ条件（E-AC）の達成状況`
    - `フォローアップ（別Issue化）`
    - 上記が placeholder ではなく issue-72 report から参照可能であること
- report update:
  - S02 の doc wiring、review verdict、search/test 結果を `report.md` に残す
- commit:
  - S02 差分をコミットする

### S90 — docs refresh / dogfooding convergence
- execution-order note:
  - 実行順序は section placement ではなく `## ステップ一覧` と `step ordering notes` に従う
  - したがって S90 は S03 完了後に実施する
- 対象:
  - docs / mirror-affecting surfaces
- 対応:
  - `spec-dock update .`
  - current docs / mirror diff を確認
  - `spec-dock validate`
  - 必要なら `spec-dock sync --github`
- gate:
  - issue-72 で変更した provider-side docs / guidance が dogfooding mirror へ収束する fresh evidence を report に残す
  - parity-managed / fixture surfaces の before/after diff を整理する

### S03 — PR review remediation tranche
- target:
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
  - `src/spec_dock/assets/install_root/.github/workflows/ci.yml`
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - `tests/fixtures/wheelhouse/*`
- design refs:
  - `design.md`:
    - `PR review feedback incorporation`
    - `review repair contract`
    - `要件 → 設計マッピング`
- step boundary:
  - mandatory 指摘 `B` / `D` と user-decision scope の `A` / `C` を同一 tranche で処理する
  - AC を直接閉じる根拠は `B` / `D` に限定し、`A` / `C` は closeout 非阻害の ancillary remediation として扱う
  - top-level review body `E` は triage policy として記録のみ行い、実装修正対象に含めない

#### B1 — test hygiene repair
- purpose:
  - `A` に対応し、test-to-test call を private helper 抽出へ置換する
- files:
  - `tests/presentation_runtime/test_runtime_sync_s07.py`

##### I1 — shared assertion helper extraction
- slice goal:
  - issue traceability を維持しつつ、public test 間直接呼び出しをなくす

###### Red
- failing test:
  - current review finding `A`
- expected failure:
  - test method から別 test method を直接呼ぶ構造が残る

###### Green
- minimum implementation:
  - shared assertion 群を private helper へ抽出する
  - 既存 2 test から helper を呼ぶ
- pass condition:
  - public test 名は維持され、test-to-test call が消える

#### B2 — shipped workflow scope repair
- purpose:
  - `B` に対応し、managed repo 一般で壊れない generic CI workflow へ修正する
- files:
  - `src/spec_dock/assets/install_root/.github/workflows/ci.yml`

##### I1 — provider-specific CI assumptions removal
- slice goal:
  - `pip install .` と `tests/test_cli.py` 前提を shipped workflow から除去する

###### Red
- failing test:
  - current review finding `B`
- expected failure:
  - managed repo に配布された workflow が repo 固有構造を仮定する

###### Green
- minimum implementation:
  - local managed repo で自己完結する validation command に置換する
  - auth/network 依存の強い step は baseline workflow に入れない
- pass condition:
  - shipped workflow が managed repo generality contract を満たす

#### B3 — install plan shape repair
- purpose:
  - `C` に対応し、plan shape と apply consumer を一致させる
- files:
  - `src/spec_dock/cli.py`

##### I1 — unused field removal
- slice goal:
  - `_ManagedSkillInstallPlan` から未使用 field を外す

###### Red
- failing test:
  - current review finding `C`
- expected failure:
  - plan が apply path の実消費者とずれた field を保持する

###### Green
- minimum implementation:
  - unused field を return type から除去する
  - validation に必要な補助データは builder 内 local へ留める
- pass condition:
  - plan shape が current consumer に一致し、周辺 tests が通る

#### B4 — hermetic wheelhouse repair
- purpose:
  - `D` に対応し、Python 3.10 offline build backend dependency gap を塞ぐ
- files:
  - `tests/test_init_update.py`
  - `tests/fixtures/wheelhouse/*`

##### I1 — tomli fixture addition
- slice goal:
  - issue-69 wheelhouse contract に `tomli` を追加する

###### Red
- failing test:
  - current review finding `D`
- expected failure:
  - Python 3.10 fresh venv + `--no-index` backend install が `build==1.2.2` の条件付き依存不足で崩れる

###### Green
- minimum implementation:
  - requirements fixture と wheel filenames contract に `tomli` を追加する
  - corresponding wheel fixture を vendor する
  - fresh venv backend install を再検証する
- pass condition:
  - Python 3.10 で hermetic backend install が通る

#### step gate
- review:
  - code_reviewer で S03 diff を review
- expected tests:
  - `A` の対象 test file targeted run
  - managed repo 相当の local workspace を使った shipped workflow 再現:
    - `./spec-dock/scripts/spec-dock validate`
    - workflow に採用する他の baseline command があれば同列に実行
  - shipped workflow contract の scoped inspection
  - installer / packaging / wheelhouse targeted tests
  - Python 3.10 fresh venv + `--no-index` backend install confirmation
- report update:
  - review analyses A-D と実装修正の対応、validation 結果、review verdict を `report.md` に残す
- commit:
  - S03 差分をコミットする

### S99 — final diff review quality gate
- branch diff scope:
  - issue-72 branch 全差分
- required validation:
  - targeted authority retirement tests
  - scoped search classification
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` authoritative manifest review result
  - `src/spec_dock/assets/codex_skills/` deleted confirmation
  - relevant CLI/runtime tests:
    - current authority assertion hit があれば targeted 実行
    - hit が無ければ `該当なし`
  - epic current report を含む current docs corpus contradiction review
  - epic current report completion check:
    - `進捗サマリー` / `完了した Issue / PR / Release` / `受け入れ条件（E-AC）の達成状況` / `フォローアップ（別Issue化）` が evidence-bearing content であること
  - `spec-dock update .`
  - `./spec-dock/scripts/spec-dock validate`
  - 必要なら `./spec-dock/scripts/spec-dock sync --github`
  - `python -m unittest discover -v` は informational sweep として扱い、既知 residual risk が issue-72 scope に波及しないか確認する
- reviewer approvals:
  - final code review `pass`
  - final spec review `pass`
- report update:
  - final diff review verdict / close-ready evidence / residual risk / no-op 理由を `report.md` に残す
- commit expectation:
  - final report 更新後に必要なら closing commit を作成する

## 未確定事項
- なし:
  - legacy `codex_skills` は physical tree を削除し、historical references は records にだけ残す方針で進める

## final exit contract
- AC/EC 達成:
  - authority uniqueness、historical boundary、future host extension、upstream prerequisites、final close gate が issue-72 report から辿れる
- docs impact resolved:
  - issue-72 で変更した docs / guidance は dogfooding mirror 収束 evidence を持つ
- final diff approved:
  - final code review と final spec review が pass し、close-ready judgment が report に残る
