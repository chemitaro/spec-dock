---
種別: 実装報告書（Issue）
ID: "iss-00016"
タイトル: "Codex skills を hub + leaf 構成へ再編する"
関連GitHub: ["#16, https://github.com/chemitaro/spec-dock/issues/16"]
状態: "draft | approved"
作成者: "chemitaro"
最終更新: "2026-03-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# iss-00016 Codex skills を hub + leaf 構成へ再編する — 実装報告（LOG）

## 実装サマリー (任意)
- S01 で、installer が hub + 4 leaf の managed full set を導入できる土台を追加した。
- 4 つの leaf skill asset を配布物へ追加し、`init` 後の導入結果と bundled asset の存在をテストで固定した。

## 実装記録（セッションログ） (必須)

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, AC-007

#### 実施内容
- `src/spec_dock/cli.py` に managed skill manifest を追加し、`_install_skill()` を 5 skill 導入へ拡張した。
- 4 つの leaf skill asset を最小骨格で追加した。
- `tests/test_cli.py` を更新し、`init` 後の 5 skill 導入と bundled asset 存在保証を検証した。
- `code_reviewer` に S01 差分要約レビューを依頼し、ブロッカーなしの承認レベル判定を得た。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_cli.TestCli.test_init_creates_expected_structure \
  tests.test_cli.TestCli.test_init_no_skill_skips_skill_install \
  tests.test_cli.TestCli.test_bundled_skill_assets_cover_managed_manifest \
  tests.test_cli.TestCli.test_update_keeps_initiatives_by_default

Ran 4 tests in 0.055s
OK
```

#### 変更したファイル
- `src/spec_dock/cli.py` - managed skill manifest と multi-skill install の初期実装
- `tests/test_cli.py` - S01 の導入結果と bundled asset を検証するテスト更新
- `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` - leaf skill 骨格追加
- `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md` - leaf skill 骨格追加
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` - leaf skill 骨格追加
- `src/spec_dock/assets/codex_skills/spec-dock-adr-facilitation/SKILL.md` - leaf skill 骨格追加

#### コミット
- `330d0a0 feat(skills): full set 導入の土台を追加`

#### メモ
- reviewer 結果: `overall_correctness = patch is correct`, findings なし（要約ベースの S01 スコープ確認）
- `--no-skill` 廃止、migration / ownership boundary、routing 文面完成、README/docs 更新は S02 以降へ意図的に deferred

---

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-002, AC-002b, AC-007, AC-008, AC-009, AC-010, EC-001, EC-001b, EC-005, EC-006

#### 実施内容
- `src/spec_dock/cli.py` で `--no-skill` を削除し、`init/update` が常に skill sync を実行するように変更した。
- managed skill ownership を導入し、`copy/update -> verify -> prune` 順で managed skill だけを同期するようにした。
- `tests/test_cli.py` に legacy single-skill / legacy no-skill / interrupted sync convergence / parser rejection の回帰テストを追加した。
- `code_reviewer` に S02 差分をレビュー依頼し、静的 diff 観点でブロッカーなしの承認レベル判定を得た。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_cli.TestCli.test_no_skill_option_is_rejected \
  tests.test_cli.TestCli.test_update_migrates_legacy_single_skill_and_preserves_custom_skill \
  tests.test_cli.TestCli.test_update_installs_full_skill_set_for_legacy_no_skill_repo \
  tests.test_cli.TestCli.test_update_skill_sync_converges_after_interrupted_run \
  tests.test_cli.TestCli.test_init_creates_expected_structure \
  tests.test_cli.TestCli.test_update_keeps_initiatives_by_default \
  tests.test_cli.TestCli.test_bundled_skill_assets_cover_managed_manifest

Ran 7 tests in 0.133s
OK
```

#### 変更したファイル
- `src/spec_dock/cli.py` - ownership boundary 付き skill sync と `--no-skill` 廃止
- `tests/test_cli.py` - migration / convergence / parser rejection の回帰テスト追加

#### コミット
- `2509881 feat(skills): skill 同期の所有境界を実装`

#### メモ
- reviewer 結果: `overall_correctness = patch is correct`, findings なし（static diff inspection）
- legacy managed 名は現時点で `spec-driven-tdd-workflow` のみを ownership set に含める実装とした

---

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: S03
- AC/EC: AC-003, AC-004, AC-005, AC-005b, AC-007, EC-002, EC-004

#### 実施内容
- hub skill を entry/routing 専用文面へ更新し、4 leaf と 4 reference docs を直接列挙した。
- 4 つの leaf skill に primary workflow と direct references を反映した。
- `tests/test_cli.py` に bundled skill routing contract テストを追加し、`runtime-operations` standalone 参照がないことも検証した。
- `code_reviewer` に S03 差分をレビュー依頼し、ブロッカーなしの承認レベル判定を得た。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_cli.TestCli.test_bundled_skill_assets_cover_managed_manifest \
  tests.test_cli.TestCli.test_bundled_skill_routing_contract \
  tests.test_cli.TestCli.test_init_creates_expected_structure

Ran 3 tests in 0.025s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` - hub routing 文面へ更新
- `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` - initiative leaf routing を確定
- `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md` - epic leaf routing を確定
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` - issue leaf routing を確定
- `src/spec_dock/assets/codex_skills/spec-dock-adr-facilitation/SKILL.md` - ADR leaf routing を確定
- `tests/test_cli.py` - bundled skill routing contract の回帰テスト追加

#### コミット
- `085e280 feat(skills): hub と leaf の routing を確定`

#### メモ
- reviewer 結果: `overall_correctness = patch is correct`, findings なし
- hub の簡潔さを優先し、詳細仕様は docs 正本へ残した

---

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: S04
- AC/EC: AC-002, AC-002b, AC-006, AC-007, AC-008, EC-001, EC-001b, EC-003

#### 実施内容
- root `README.md` を multi-skill 導線へ更新し、`--no-skill` / `adrs/new-adr` / `artifacts/_template.md` の旧記述を除去した。
- 配布 docs `README.md` を hub + 4 leaf + reference layer の入口説明へ更新した。
- `workflow_{initiative,epic,issue,adr}.md` 冒頭に対応 leaf skill を追記し、docs と skills の導線を相互参照にした。
- `tests/test_cli.py` に導入後 docs 内容の回帰アサートを追加し、`code_reviewer` 承認を得た。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_cli.TestCli.test_init_creates_expected_structure \
  tests.test_cli.TestCli.test_no_skill_option_is_rejected

Ran 2 tests in 0.013s
OK
```

#### 変更したファイル
- `README.md` - root 利用案内を multi-skill / discussions 前提へ更新
- `src/spec_dock/assets/spec_dock/docs/README.md` - hub + 4 leaf の入口説明を追加
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` - initiative leaf skill 参照を追記
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` - epic leaf skill 参照を追記
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - issue leaf skill 参照を追記
- `src/spec_dock/assets/spec_dock/docs/workflow_adr.md` - ADR leaf skill 参照を追記
- `tests/test_cli.py` - docs 導線の回帰アサートを追加

#### コミット
- `53fe799 docs(skills): multi-skill 導線へ案内を更新`

#### メモ
- reviewer 結果: `Approved`
- root `README.md` 本体はテスト対象外とし、配布 docs 側の内容を回帰テストで固定した

---

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: S05
- AC/EC: AC-007, AC-010, EC-006

#### 実施内容
- `python -m unittest discover -v` を実行し、全件回帰テストを通した。
- `python -m pip install --target` ベースの packaging check を実施し、bundled skill/docs asset がインストール物に含まれることを確認した。
- `git diff main...HEAD` をスコープに `code_reviewer` へ最終レビューを依頼し、差分全体で Approved を取得した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -v

Ran 149 tests in 18.638s
OK

rm -rf /tmp/specdock-pkgcheck && \
python -m pip install -q --target /tmp/specdock-pkgcheck . && \
PYTHONPATH=/tmp/specdock-pkgcheck python -c "<asset existence check>"

missing=[]
```

#### 変更したファイル
- `spec-deps/current/report.md` - S04/S05 の記録と品質ゲート結果を追記

#### コミット
- `04fa9c2 docs(report): 品質ゲート結果を記録`

#### メモ
- reviewer 結果: `Approved`（`main...HEAD` 差分全体、findings なし）
- packaging check では `spec-driven-tdd-workflow` / `spec-dock-initiative-planning` / `spec_dock/docs/README.md` の収載を確認した

---

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: follow-up docs audit
- AC/EC: docs/skill correctness follow-up

#### 実施内容
- `doc_writer` に docs / distributed docs / bundled `SKILL.md` の監査と必要最小限の整備を依頼した。
- stale だった `guide.md` の `sync` 生成物説明を現行挙動へ更新した。
- `workflow_epic.md` / `workflow_issue.md` に、`import` 時の親解決（current active fallback）を追記した。
- `SKILL.md` 群には、典型タスクと active issue の入口 (`spec-dock/active/context-pack.md`) のような最小限の agent-facing 情報だけを補強した。
- `code_reviewer` に実差分レビューを依頼し、docs を正本・skill を簡潔ルーターとする方針を維持したまま Approved を取得した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -v

Ran 149 tests in 18.638s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/README.md` - import 親解決の補足を追加
- `src/spec_dock/assets/spec_dock/docs/guide.md` - `sync` 生成物の説明を現行挙動へ修正
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` - `import epic` の親解決 fallback を追記
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - `import issue` の親解決 fallback を追記
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` - hub の最小 agent-facing 導線を補強
- `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` - 典型タスクを補強
- `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md` - 典型タスクを補強
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` - active issue の入口と典型タスクを補強
- `src/spec_dock/assets/codex_skills/spec-dock-adr-facilitation/SKILL.md` - 典型タスクを補強
- `tests/test_cli.py` - docs/skill wording の回帰アサートを追加

#### コミット
- `0d7e5f6 docs(skills): 事実情報と agent 導線を補強`

#### メモ
- `README.md` は今回の時点で致命的な誤記なしと判断され、未変更
- reviewer 結果: `Approved`

---

### 2026-03-08 13:20 - 14:10

#### 対象
- Step: issue governance template follow-up
- AC/EC: AC-011, AC-012, AC-013, AC-014 / EC-007, EC-008, EC-009

#### 実施内容
- issue 実装 governance の追補方針を `research-00002` / `disc-00003` に整理し、`requirement.md` / `design.md` / `plan.md` に契約として反映した。
- spec reviewer 指摘で「最終品質ゲートが二重化している」論点が出たため、`plan.md` の最終ゲートを `S08` に一本化した。
- `workflow_issue.md` に plan upfront approval / step result approval / docs impact / final diff review quality gate を正本ルールとして追加した。
- `templates/issue/plan.md` に全 step 共通ルール、`S90 docs impact resolution / docs refresh`、`S99 final diff review quality gate` を追加した。
- `spec-dock-issue-execution/SKILL.md` に、docs を正本として扱うことと docs impact / final gate を飛ばさない reminder を追加した。
- `tests/test_cli.py` に workflow / template / skill wording の回帰アサートを追加した。
- 差分確認では、`workflow_issue.md` / `templates/issue/plan.md` / `SKILL.md` / `tests/test_cli.py` の整合を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -v

Ran 149 tests in 18.651s
OK

rm -rf /tmp/specdock-pkgcheck && \
python -m pip install -q --target /tmp/specdock-pkgcheck . && \
PYTHONPATH=/tmp/specdock-pkgcheck python - <<'PY'
from pathlib import Path
root = Path('/tmp/specdock-pkgcheck/spec_dock/assets')
checks = [
    root / 'spec_dock/docs/workflow_issue.md',
    root / 'spec_dock/templates/issue/plan.md',
    root / 'codex_skills/spec-dock-issue-execution/SKILL.md',
]
missing = [str(p) for p in checks if not p.exists()]
print({'missing': missing})
PY

{'missing': []}

git diff origin/chemitaro/issue16...HEAD -- \
  src/spec_dock/assets/spec_dock/docs/workflow_issue.md \
  src/spec_dock/assets/spec_dock/templates/issue/plan.md \
  src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md \
  tests/test_cli.py
```

#### 変更したファイル
- `spec-deps/current/discussions/research-00002-issue-plan-governance-analysis.md` - issue plan governance の分析と論点を記録
- `spec-deps/current/discussions/disc-00003-issue-plan-governance-best-practice.md` - 運用ルールのベストプラクティス提案を記録
- `spec-deps/current/requirement.md` - governance 標準化の AC/EC と制約を追加
- `spec-deps/current/design.md` - issue governance contract と変更対象ファイルを設計へ反映
- `spec-deps/current/plan.md` - review loop / docs refresh / final gate の実装計画を追加し、最終品質ゲートを一本化
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - issue execution governance の正本ルールを追加
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md` - 共通実行ルール、`S90`、`S99` を追加
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` - governance reminder を追加
- `tests/test_cli.py` - governance wording の回帰アサートを追加

#### コミット
- `2a092ef docs(issue): issue governance の正本を追加`
- `ced27b6 docs(plan): issue 計画テンプレートに governance を追加`
- `f9f7d3a docs(skill): issue execution の governance reminder を追加`

#### メモ
- spec reviewer 結果: `Approved`（issue docs 契約の一貫性確認）
- code reviewer 結果: `Approved`（`git diff main...HEAD` スコープ、blocking finding なし）
- packaging check では `workflow_issue.md` / `templates/issue/plan.md` / `spec-dock-issue-execution/SKILL.md` の収載を確認した

---

### 2026-03-09 10:00 - 10:40

#### 対象
- Step: S09 shared phase playbook docs
- AC/EC: AC-015, AC-018 / EC-010, EC-011, EC-012

#### 実施内容
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` を docs 正本として追加した。
- 各 playbook に、目的 / 出力 / 非ゴール、調査・分析、ヒアリング、discussion sheet 条件、ADR 条件、review 前 exit criteria、次 phase へ進める条件、subagent 活用ガイダンスを整理した。
- source repo 前提の template パスになっていないことを確認し、runtime 側の `spec-dock/templates/...` を参照する形で揃っていることを確認した。
- `code_reviewer` に S09 差分をレビュー依頼し、Approved を取得した。

#### 実行コマンド / 結果
```bash
rg -n "templates/|src/spec_dock" \
  src/spec_dock/assets/spec_dock/docs/phase_requirement.md \
  src/spec_dock/assets/spec_dock/docs/phase_design.md \
  src/spec_dock/assets/spec_dock/docs/phase_plan.md

code reviewer verdict: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/phase_requirement.md` - requirement authoring playbook を追加
- `src/spec_dock/assets/spec_dock/docs/phase_design.md` - design authoring playbook を追加
- `src/spec_dock/assets/spec_dock/docs/phase_plan.md` - plan authoring playbook を追加

#### メモ
- S09 では docs 正本の追加に集中し、workflow からの直接リンクと docs 入口の導線は S10 / S11 で扱う。

---

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## 省略/例外メモ (必須)
- 該当なし
