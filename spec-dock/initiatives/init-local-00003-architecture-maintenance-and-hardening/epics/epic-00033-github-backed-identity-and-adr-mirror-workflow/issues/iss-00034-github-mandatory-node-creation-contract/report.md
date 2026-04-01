---
種別: 実装報告書（Issue）
ID: "iss-00034"
タイトル: "GitHub Mandatory Node Creation Contract"
関連GitHub: ["#34"]
状態: "approved"
作成者: "Copilot CLI"
最終更新: "2026-03-28"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00034 GitHub Mandatory Node Creation Contract — 実装報告（LOG）

## 実装サマリー
- `initiative / epic / issue` の create contract を GitHub mandatory に統一し、`--no-github` の成功経路を閉じた。
- `origin` basis の canonical repo scope を fail-closed 化し、validation / import / sync の境界を create contract と整合させた。
- import / sync では main processing や sync-generated artifact regeneration は scope 外のままとし、legacy/import behavior を保つための preflight validation boundary 調整だけを実施した。
- docs impact は active issue docs の最小差分に留め、full parity refresh は `iss-00038` へ残した。

## 実装記録（セッションログ）

### 2026-03-28 — spec gate / docs boundary fix

#### 対象
- Step: spec-gate, S90
- AC/EC: AC-003

#### 実施内容
- `.meta.json.github.issue_number` / `.meta.json.github.repo_owner` / `.meta.json.github.repo_name` の表現を requirement / design / plan で統一した。
- import / sync main processing は scope 外、ただし AC-003/S03 の preflight validation boundary 調整は scope 内であることを requirement / design / plan へ明記した。
- docs/validate/final gate の対象を `iss-00034` の boundary に合わせて明確化し、issue-level final evidence は `plan.md` S99 の `validate` + final diff review で充足する旨を明記した。

#### 実行コマンド / 結果
```bash
git diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md

spec diff を確認し、spec review を実施して pass
```

#### 変更したファイル
- `spec-dock/active/issue/requirement.md` - import / sync の out-of-scope と preflight validation boundary in-scope を明確化
- `spec-dock/active/issue/design.md` - validation contract と S99 evidence boundary を issue 実装に合わせて整理
- `spec-dock/active/issue/plan.md` - S03 / S90 / S99 の scope と issue-specific evidence note を明確化

#### コミット
- `fba707409a061894871947300e30a64be6dd761f` `docs(spec): iss-00034 の実装前ブロッカーを解消`

#### メモ
- `spec_reviewer` verdict: pass
- docs parity の全面更新は `iss-00038` へ defer する方針を維持
- `workflow_issue.md` の一般 finish step `sync --github` は issue 共通の通常フローだが、iss-00034 では sync-generated artifact regeneration が scope 外のため required evidence に採用していない

---

### 2026-03-28 — S01 canonical repo scope resolver

#### 対象
- Step: S01
- AC/EC: AC-002, EC-001, EC-002

#### 実施内容
- `origin` fetch/push の両方から canonical `owner/repo` を解決する fail-closed resolver を実装した。
- `origin missing` / `non-GitHub remote` / `fetch-push mismatch` を create 前に明示エラーとして観測できるようにした。
- best-effort resolver は維持しつつ、create-time だけ strict resolver を使う境界に分離した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_new_s08

OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` - canonical repo scope resolver を fail-closed 化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py` - strict resolver を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - GitHub create 前の repo scope precheck を追加
- `tests/cli_runtime/test_runtime_new_s08.py` - resolver failure / success の回帰テストを追加

#### コミット
- `68821042ce42e46780609cf66747ce1f8af8f9c2` `fix(runtime): origin由来のGitHub repo scope解決をfail-closed化`

#### メモ
- `code_reviewer` verdict: pass

---

### 2026-03-28 — S02 GitHub mandatory create contract

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, EC-003

#### 実施内容
- `new initiative` / `new epic` / `new issue` の default mode を GitHub create に統一した。
- `--no-github` を initiative / epic / issue で explicit contract error に変更した。
- same-repo linkage と cross-repo reject を create contract に固定し、`.meta.json.github.*` を canonical lowercase で保存するようにした。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08

OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` - default create / `--no-github` reject を反映
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - same-repo / cross-repo 境界を固定
- `tests/cli_runtime/test_new.py` - create contract と CLI reject の期待値を更新
- `tests/cli_runtime/test_runtime_new_s08.py` - application 層の contract tests を拡張

#### コミット
- `f7dc9f6c7bb4c259c5065d212271330107e5b54d` `feat(cli-runtime): new作成のGitHub既定化を反映`

#### メモ
- `code_reviewer` verdict: pass

---

### 2026-03-28 — S03 validation / migration boundary hardening

#### 対象
- Step: S03
- AC/EC: AC-003

#### 実施内容
- strict validate で local-only / legacy unscoped / malformed partial scope / blank-scope loader を reject するよう整えた。
- import / sync preflight では legacy repair 用の relax を維持しつつ、不完全な repo scope は即時失敗へ切り替えた。
- `sync --force` でも malformed partial scope が存在する場合は hard-stop するようにし、error ordering に依存しない structural detection へ置き換えた。
- GitHub-backed hierarchy helper を共通化し、CLI / domain / presentation tests を contract に合わせて移行した。

#### スコープ注記
- この step での `application/import_node.py` / `application/sync_state.py` 変更は import / sync main processing の拡張ではなく、AC-003/S03 の preflight validation boundary 調整として実施した。
- 目的は legacy/import behavior を維持したまま validation blast radius を広げず、malformed scope を fail-closed にすることであり、sync-generated artifact regeneration を要求するものではない。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08 tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_validate_s02 tests.domain_runtime.test_runtime_domain_s03 tests.cli_runtime.test_import tests.presentation_runtime.test_runtime_sync_s07
./spec-dock/scripts/spec-dock validate

Ran 193 tests in 28.587s
OK
spec-dock: ok (validate) nodes=8
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - mandatory linkage / partial scope / blank-scope pairing validation と structural helper を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py` - relaxed preflight validate を create contract boundary と整合
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - malformed scope を force でも hard-stop するよう修正
- `tests/cli_runtime/harness.py` - GitHub-backed hierarchy helper を共通化
- `tests/cli_runtime/test_import.py` - import preflight / duplicate linkage regressions を更新
- `tests/cli_runtime/test_runtime_validate_s02.py` - validation use-case expectations を更新
- `tests/cli_runtime/test_validate.py` - validate / sync の reject path と blank-scope loader regression を追加
- `tests/domain_runtime/test_runtime_domain_s03.py` - strict/relaxed validation の domain regressions を追加
- `tests/presentation_runtime/test_runtime_sync_s07.py` - sync non-force / force の malformed scope expectations を更新

#### コミット
- `2677ec95ca36154dc18c4503f048356db219cc9d` `fix(runtime): GitHub連携スコープ検証をS03契約に合わせる`

#### メモ
- `code_reviewer` verdict: pass
- `qa_reviewer` verdict: pass
- review 中の指摘（partial-scope coverage、blank-scope structural loader、`sync --force` の fatal ordering 依存）はすべて DevCoder に差し戻して修正後に再レビューした

---

### 2026-03-28 — S04 foreign issue URL strict reject correction / S90 minimal docs refresh

#### 対象
- Step: S04, S90
- AC/EC: AC-004, EC-004

#### 実施内容
- `import ... --allow-foreign-url` の foreign GitHub issue URL 成功経路を閉じ、single-repo / GitHub-backed identity contract に沿って strict reject へ固定した。
- reject を `gh issue view` / create lock / local scaffold / `.meta.json` write 前に行い、rejected foreign import で GitHub read / node/meta/symlink の副作用が出ないことを tests で固定した。
- same-repo URL import は維持しつつ、`--allow-foreign-url` は compatibility success path ではなく reject-only compatibility flag として扱うよう help/docs を整えた。
- `reference_github.md` / `workflow_issue.md` を foreign strict reject と GitHub mandatory create contract に最小差分で揃え、`gh issue view` が repo slug 既知時に `--repo owner/repo` を付ける実装にも記述を合わせた。
- foreign import correction path に残っていた `iss-local-*` fallback 前提を除去した。
- follow-up で checked-in runtime mirror の `application/create_node.py` / `application/repo_context.py` / `application/sync_state.py` / `application/import_node.py` / `commands/new.py` / `commands/import_cmd.py` / `domain/validation.py` / `infra/git_cli.py` を provider asset と再同期し、S04/S03 由来の checked-in dogfooding parity gap を解消した。
- `tests.test_init_update` の broadened failures は unrelated baseline ではなく、(a) checked-in runtime parity drift、(b) GitHub-mandatory contract 下での `_create_minimal_local_tree()` helper の stale `--no-github` 依存、(c) legacy fixture setup の parent dir 未作成、の issue-related gap だったことを follow-up で確認・修正した。
- checked-in dogfooding initiative metadata は read-only/no-migration 境界を広げず、GitHub mandatory contract の truthfulness を保つための最小補正だけを実施した。`init-local-00002` は新規作成済み GitHub issue `#39`、`init-local-00003` は issue 本文で明示されている既存 GitHub issue `#31` にそれぞれ訂正した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_import_s10.TestRuntimeImportS10.test_import_rejects_foreign_repo_before_github_read_lock_and_race_revalidation_writes

Ran 1 test in 0.042s
OK

python -m unittest tests.cli_runtime.test_import tests.cli_runtime.test_runtime_import_s10 tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08

Ran 131 tests in 14.569s
OK

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=8
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py` - foreign GitHub issue URL を strict reject に変更し、`--allow-foreign-url` compatibility success path を削除
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/import_cmd.py` - `--allow-foreign-url` help を reject-only compatibility flag に更新
- `spec-dock/scripts/spec_dock_runtime/application/import_node.py` - checked-in runtime mirror を provider asset と同内容へ同期
- `spec-dock/scripts/spec_dock_runtime/commands/import_cmd.py` - checked-in runtime mirror help を同期
- `tests/cli_runtime/test_import.py` - foreign import success / fallback 期待を reject / no-write 期待へ更新
- `tests/cli_runtime/test_runtime_import_s10.py` - application layer の foreign reject / same-repo import 回帰を更新し、initiative/epic coverage を追加
- `src/spec_dock/assets/spec_dock/docs/reference_github.md` - foreign import strict reject と GitHub mandatory create contract を追記
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - import workflow の strict reject boundary を更新
- `spec-dock/docs/reference_github.md` - checked-in docs mirror を同期
- `spec-dock/docs/workflow_issue.md` - checked-in docs mirror を同期
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/.meta.json` - checked-in initiative linkage を truthful な `chemitaro/spec-dock#39` へ補正
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/.meta.json` - checked-in initiative linkage を truthful な `chemitaro/spec-dock#31` へ補正

#### コミット
- 未コミット

#### メモ
- foreign issue URL reject は `gh issue view` 実行前に止まるため、rejected import で GitHub read side effect も発生しない。
- foreign issue URL reject は `_acquire_create_lock` 実行前にも止まることを targeted regression で固定した。
- foreign import correction path から `iss-local-*` fallback を除去した。
- follow-up 後は `tests.test_init_update` / broadened suite / `./spec-dock/scripts/spec-dock validate` がすべて green となり、S04/S99 evidence から baseline-noise 扱いを除外した。

---

### 2026-03-28 — S99 final diff review quality gate

#### 対象
- Step: S99
- AC/EC: AC-001, AC-002, AC-003, EC-001, EC-002, EC-003

#### 実施内容
- branch 全体の diff stat と commit scope を確認し、docs impact が minimal boundary に留まることを review した。
- implementation review / QA review / spec review の最終 verdict を揃えた。
- `report.md` に commands / results / commits / reviewer verdict を記録した。
- follow-up 後の issue-level final evidence は `plan.md` S99 に従って、`tests.test_init_update`、broadened verified suite、`./spec-dock/scripts/spec-dock validate`、final diff review を採用した。
- broadened-suite failures の分類を修正し、iss-00034 scope の parity/helper/fixture gaps が解消されたことで acceptance evidence を broader command に拡張した。
- checked-in initiative `.meta.json` correction は general migration ではなく、dogfooding workspace に既に保存されている GitHub linkage を truth-preserving に戻す最小修正として diff review に含めた。
- `sync --github` は sync-generated artifact regeneration が scope 外のため required evidence に含めないことを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update

Ran 81 tests in 8.899s
OK

python -m unittest tests.cli_runtime.test_import tests.cli_runtime.test_runtime_import_s10 tests.test_init_update tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08 tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_validate_s02 tests.domain_runtime.test_runtime_domain_s03 tests.presentation_runtime.test_runtime_sync_s07

Ran 292 tests in 42.851s
OK

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=8
```

#### 変更したファイル
- `spec-dock/active/issue/report.md` - 実行ログ、commit、review verdict を記録

#### コミット
- 未コミット（この report 反映を次コミットで記録）

#### メモ
- final branch diff review (`code_reviewer`) verdict: pass
- final spec review (`spec_reviewer`) verdict: pass after `report.md` populated and S99 evidence recorded
- follow-up で broadened-suite evidence を green に更新し、`tests.test_init_update` の failure classification を iss-00034 scope に訂正した
- checked-in initiative linkage は `init-local-00002 -> chemitaro/spec-dock#39`、`init-local-00003 -> chemitaro/spec-dock#31` が正しいため、その truth-preserving correction を issue boundary 内の最小例外として記録した

---

### 2026-03-28 — S04 follow-up numeric import no-origin fail-closed fix

#### 対象
- Step: S04 follow-up
- AC/EC: AC-004, EC-004

#### 実施内容
- numeric import（`import issue 123`）で current repo origin が解決できない場合に fail-closed で reject する境界を固定した。
- reject を `gh issue view` / create lock / local scaffold / `.meta.json` write より前に配置した。
- precheck collision の no-write 優先は維持し、URL strict reject behavior も変更しないまま保持した。
- provider asset と checked-in runtime mirror の `application/import_node.py` を同内容で同期した。
- parity test 側は GitHub-mandatory 前提に合わせ、numeric import が成功する既存ケースには origin を明示して契約と整合させた。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_import tests.cli_runtime.test_runtime_import_s10

Ran 53 tests in 6.897s
OK

python -m unittest tests.test_init_update

Ran 81 tests in 10.210s
OK

python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08 tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_validate_s02 tests.domain_runtime.test_runtime_domain_s03 tests.presentation_runtime.test_runtime_sync_s07

Ran 160 tests in 22.921s
OK

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=8
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
- `spec-dock/scripts/spec_dock_runtime/application/import_node.py`
- `tests/cli_runtime/test_import.py`
- `tests/cli_runtime/test_runtime_import_s10.py`
- `tests/test_init_update.py`
- `spec-dock/active/issue/report.md`

## 遭遇した問題と解決
- 問題: partial GitHub repo scope が import / sync の relaxed preflight で current repo へ誤束縛されうる状態が見つかった。
  - 解決: `validation.py` に structural pairing check を追加し、`sync --force` でも malformed scope を hard-stop するよう修正した。
- 問題: blank string の `github.repo_owner` / `github.repo_name` を structural loader 経由で明示的に保護する end-to-end coverage が不足していた。
  - 解決: 実ファイルの `.meta.json` を whitespace-only に改変する CLI regression を追加し、loader error を確認した。

## 学んだこと
- create contract の切り替えは create path だけでなく、validation / import / sync の preflight 境界まで同時に揃えないと fail-closed を保てない。
- malformed scope のような安全性の高い不整合は、`--force` の downgrade 対象から明示的に外す必要がある。

## 今後の推奨事項
- asset mirror 側 docs の parity refresh は `iss-00038` でまとめて実施する。
- 同種の contract 変更では、CLI / domain / presentation の三層で reject path regressions を先に固定する。
- numeric import のように target repo scope を持たない経路でも、current repo scope を必須にして fail-closed を揃える。

## 省略/例外メモ
- `src/spec_dock/assets/spec_dock/docs/*` の全面 parity refresh は本 issue の scope 外とし、`iss-00038` へ defer した。
- 作業中に存在した untracked `package-lock.json` は unrelated change と判断し、未変更・未コミットのまま維持した。
