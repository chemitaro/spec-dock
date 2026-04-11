---
種別: 実装計画書（Issue）
ID: "iss-00064"
タイトル: "Update User Facing Docs Help"
関連GitHub: ["#64"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-11"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00064 Update User Facing Docs Help — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004
- EC:
  - EC-001, EC-002, EC-003
- 制約:
  - docs-only / skill-only 修正に閉じ、runtime behavior は変更しない

## epic-00059 ownership boundary
- この issue は post-tranche docs-only follow-up であり、`epic-00059` の tranche owner を再定義しない。
- `iss-00060` が持つ provider-side dependency docs refresh ownership、`iss-00062` が持つ hard cutover `validate` / `sync` evidence ownership、`iss-00063` が持つ final parity / close review ownershipは維持する。
- 本 issue の `validate` / `sync` は docs-only follow-up の sanity check と current dogfooding evidence refresh に限定し、hard cutover judgment や epic E-AC-005 ownership を上書きしない。
- `report.md` には次の 2 節を必須とする。
  - `## Docs-Only Sanity Checks (iss-00064)`
  - `## Canonical Evidence Owners (read-only references)`

## マイルストーン一覧
- M1:
  - 対象:
    - issue 契約の固定と spec review pass
  - exit:
    - requirement / design / plan が `approved` で spec reviewer `pass`
- M2:
  - 対象:
    - provider-side docs / workflow / help-adjacent reference の整合修正
  - exit:
    - provider-side user-facing docs 群が current contract に揃う
- M3:
  - 対象:
    - dogfooding mirror / old docs / skills / docs-only close-out
  - exit:
    - mirror docs / skill guidance / sanity check / report / commit が完了する

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - provider-side docs SoT を先に更新する
  - 次に dogfooding mirror と old docs を揃える
  - 最後に skill / test / final verification を行う
- step ordering notes:
  - S01 が docs / workflow contract の入口を固定する prerequisite であり、S02 と S03 はその契約に従属する

## 対象ファイル集合
- Provider Docs SoT:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_tree.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
- Dogfooding Mirror Docs:
  - `spec-dock/docs/README.md`
  - `spec-dock/docs/guide.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow-issue.md`
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_initiative.md`
  - `spec-dock/docs/workflow-tree.md`
  - `spec-dock/docs/workflow_adr.md`
  - `spec-dock/docs/workflow-adr.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/sync.md`
  - `spec-dock/docs/spec-dock-guide-old.md`
- Skills:
  - `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- Optional Tests:
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_wrappers.py`
- Issue Docs / Report:
  - `spec-dock/.../iss-00064-update-user-facing-docs-help/requirement.md`
  - `spec-dock/.../iss-00064-update-user-facing-docs-help/design.md`
  - `spec-dock/.../iss-00064-update-user-facing-docs-help/plan.md`
  - `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`
- Non-target / reject set:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
  - `src/spec_dock/cli.py`
  - runtime / application / domain / infra 実装全般

## 機械的検証ルール
- Positive assertions:
  - provider command path required files:
    - `src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow_tree.md,workflow_adr.md,reference_deps.md,reference_sync.md,reference_github.md}`
  - mirror command path required files:
    - `spec-dock/docs/{README.md,guide.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md,reference_deps.md,reference_sync.md,reference_github.md,sync.md,spec-dock-guide-old.md}`
  - storage contract required files:
    - `src/spec_dock/assets/spec_dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md}`
    - `spec-dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md,sync.md,spec-dock-guide-old.md}`
  - mutation contract required files:
    - `src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,reference_deps.md}`
    - `spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,reference_deps.md}`
    - `src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`
    - `.agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`
  - legacy framing required files:
    - `src/spec_dock/assets/spec_dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md}`
    - `spec-dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md,sync.md,spec-dock-guide-old.md}`
  - report ownership required file:
    - `spec-dock/.../iss-00064-update-user-facing-docs-help/report.md`
- Negative assertions:
  - strict current-doc set では `./spec ` を command 例として残さない。
  - strict current-doc set では `deps.json` / `meta.json` を current storage / fallback read/write として残さない。
- Allowed exception:
  - `spec-dock/docs/spec-dock-guide-old.md` では deprecated/historical warning の中で旧表記に言及してよいが、同一文書に current doc link、current command path、legacy framing string を必須で置く。
- Strict current-doc set:
  - `src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow_tree.md,workflow_adr.md}`
  - `spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md}`
  - `src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`
  - `.agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - provider-side docs / workflow / help-adjacent reference が current command path と `.meta.json` contract を示す
  - closes:
    - AC-001, AC-002, AC-003
  - review gate:
    - RG1 implementation review
- S02:
  - 観測可能な振る舞い:
    - dogfooding mirror と old / secondary docs が current contract を誤誘導なく表現する
  - closes:
    - AC-004, EC-001, EC-002
  - review gate:
    - RG2 implementation review
- S03:
  - 観測可能な振る舞い:
    - skill guidance と docs parity verification が current contract を支持する
  - closes:
    - EC-003
  - review gate:
    - RG3 implementation review / QG1 QA review

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S03
- AC-002 -> S01, S02
- AC-003 -> S01, S03
- AC-004 -> S02
- EC-001 -> S02
- EC-002 -> S01, S02, S03
- EC-003 -> S03

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S01 完了後
  - scope:
    - Provider Docs SoT の変更
  - pass 条件:
    - `対象ファイル集合/Provider Docs SoT` の 10 ファイルが current contract に揃っている
    - Positive assertions / Negative assertions を満たす
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分とまとめてコミットする
- RG2 implementation review:
  - timing:
    - S02 完了後
  - scope:
    - Dogfooding Mirror Docs の変更
  - pass 条件:
    - `対象ファイル集合/Dogfooding Mirror Docs` の 14 ファイルが current contract に揃っている
    - `spec-dock/docs/spec-dock-guide-old.md` に deprecated/historical warning と current doc link がある
    - Positive assertions / Negative assertions / Allowed exception を満たす
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分とまとめてコミットする
- RG3 implementation review:
  - timing:
    - S03 完了後
  - scope:
    - Skills と Optional Tests の変更
  - pass 条件:
    - `対象ファイル集合/Skills` の 8 ファイルが current command path を参照し、workflow docs と矛盾しない
    - `Optional Tests` は `tests/test_init_update.py` と `tests/cli_runtime/test_wrappers.py` のみを扱い、必要な contract assertion だけを更新する
    - Positive assertions / Negative assertions を満たす
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分とまとめてコミットする
- QG1 QA review:
  - timing:
    - S03 実装後
  - scope:
    - docs/help/skill verification と required command evidence
  - pass 条件:
    - strict current-doc negative check:
      - `rg -n '\./spec\b' src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow_tree.md,workflow_adr.md} spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md} src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md .agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`
      - 期待: 0 件
    - strict legacy-name negative check:
      - `rg -n 'deps\.json|meta\.json' src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow_tree.md,workflow_adr.md} spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md} src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md .agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`
      - 期待: 0 件
    - provider command path positive check:
      - `rg -n '\./spec-dock/scripts/spec-dock' src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,workflow_issue.md,workflow_epic.md,workflow_initiative.md,workflow_tree.md,workflow_adr.md,reference_deps.md,reference_sync.md,reference_github.md}`
      - 期待: 10 ファイルすべてで 1 件以上
    - mirror command path positive check:
      - `rg -n '\./spec-dock/scripts/spec-dock' spec-dock/docs/{README.md,guide.md,workflow_issue.md,workflow-issue.md,workflow_epic.md,workflow_initiative.md,workflow-tree.md,workflow_adr.md,workflow-adr.md,reference_deps.md,reference_sync.md,reference_github.md,sync.md,spec-dock-guide-old.md}`
      - 期待: 14 ファイルすべてで 1 件以上
    - storage positive check:
      - `rg -n '\.meta\.json|depends_on' src/spec_dock/assets/spec_dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md} spec-dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md,sync.md,spec-dock-guide-old.md}`
      - 期待: 対象 10 ファイルすべてで 1 件以上
    - mutation positive check:
      - `rg -n 'deps add|deps remove|deps check' src/spec_dock/assets/spec_dock/docs/{README.md,workflow_issue.md,reference_deps.md} spec-dock/docs/{README.md,workflow_issue.md,workflow-issue.md,reference_deps.md} src/spec_dock/assets/codex_skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md .agents/skills/{spec-driven-tdd-workflow,spec-dock-issue-execution,spec-dock-codex-adapter,spec-dock-copilot-adapter}/SKILL.md`
      - 期待: 対象 15 ファイルすべてで 1 件以上
    - legacy framing positive check:
      - `rg -n 'legacy|deprecated|historical|no dual-read|manual migration' src/spec_dock/assets/spec_dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md} spec-dock/docs/{guide.md,reference_deps.md,reference_sync.md,reference_github.md,sync.md,spec-dock-guide-old.md}`
      - 期待: 対象 10 ファイルすべてで 1 件以上
    - report ownership check:
      - `rg -n '^## Docs-Only Sanity Checks \(iss-00064\)$|^## Canonical Evidence Owners \(read-only references\)$' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00064-update-user-facing-docs-help/report.md`
      - 期待: 2 行とも返る
    - optional tests:
      - `python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers`
      - 期待: pass
    - command evidence:
      - `./spec-dock/scripts/spec-dock --help`
      - `./spec-dock/scripts/spec-dock deps --help`
      - `./spec-dock/scripts/spec-dock validate`
      - `./spec-dock/scripts/spec-dock sync --github`
      - 期待: 結果が `report.md` の `Docs-Only Sanity Checks` 節に残る
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分とまとめてコミットする
- SG1 spec review:
  - timing:
    - 実装前の contract 固定時
  - scope:
    - requirement / design / plan
  - commit gate:
    - pass まで review loop を回し、pass 後に issue docs をコミットする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- docs impact が `none` ではないため `S90` を必須とする。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。

## 実装ステップ

### S01 — provider-side docs / workflow の入口 contract を固定する
- target:
  - Provider Docs SoT 10 ファイル
- design refs:
  - `design.md` の `インターフェース契約`, `実装対象ファイル集合`, `epic-00059 との所有境界`
- step boundary:
  - `対象ファイル集合/Provider Docs SoT` に閉じる

#### B1 — README / guide / workflow / reference 整合
- purpose:
  - supported execution path と command-first mutation を入口から発見可能にする
- files:
  - `対象ファイル集合/Provider Docs SoT` 全体

##### I1 — TDD cycle
- slice goal:
  - 旧 `./spec ...` 導線を current path に置き換え、`.meta.json` / `depends_on` / `deps add/remove/check` を入口 docs と workflow docs へ明示する

###### Red
- failing test:
  - `tests/test_init_update.py` と `tests/cli_runtime/test_wrappers.py` のうち provider docs contract に触れる assertion を先に失敗させる。必要ならこの 2 ファイルのみに assertion を追加する。
- expected failure:
  - 旧 command path や legacy storage 表記が検出される

###### Green
- minimum implementation:
  - Provider Docs SoT 10 ファイルを current contract に更新する
- pass condition:
  - 対象 10 ファイルが Positive / Negative assertions を満たす

###### Refactor
- 目的:
  - 文言の重複や cross-link を整理する
- guardrail:
  - 振る舞いを変えない

#### step gate
- review:
  - code_reviewer による docs contract review
- expected tests:
  - `python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers`
- report update:
  - reviewer verdict / test結果 / 修正内容を `report.md` に残す
- commit:
  - pass 後に report 更新込みでコミットする

### S02 — mirror docs と old docs を current contract に揃える
- target:
  - Dogfooding Mirror Docs 14 ファイル
- design refs:
  - `design.md` の `old-doc contract`, `実装対象ファイル集合`, `epic-00059 との所有境界`
- step boundary:
  - `対象ファイル集合/Dogfooding Mirror Docs` に閉じる

#### B1 — mirror / deprecated guidance
- purpose:
  - provider-side docs と同じ contract を dogfooding 側にも反映し、old docs の誤誘導を止める
- files:
  - `対象ファイル集合/Dogfooding Mirror Docs` 全体

##### I1 — TDD cycle
- slice goal:
  - old docs を deprecated 化し、current entrypoint へ誘導する

###### Red
- failing test:
  - `tests/test_init_update.py` と `tests/cli_runtime/test_wrappers.py` のうち mirror docs / deprecated guidance に触れる assertion を先に失敗させる。必要ならこの 2 ファイルのみに assertion を追加する。
- expected failure:
  - warning/link 不在、旧 command path の残存

###### Green
- minimum implementation:
  - Dogfooding Mirror Docs 14 ファイルを更新し、old doc 冒頭に warning + current link を追加する
- pass condition:
  - 対象 14 ファイルが Positive / Negative assertions と Allowed exception を満たす

###### Refactor
- 目的:
  - warning 文言と link 導線を統一する
- guardrail:
  - historical note を current contract より前面に出しすぎない

#### step gate
- review:
  - code_reviewer による mirror/deprecated review
- expected tests:
  - `python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers`
- report update:
  - reviewer verdict / test結果 / 修正内容を `report.md` に残す
- commit:
  - pass 後に report 更新込みでコミットする

### S03 — skills と docs parity verification を閉じる
- target:
  - Skills 8 ファイル
  - Optional Tests 2 ファイル
  - `report.md`
- design refs:
  - `design.md` の `skill contract`, `report contract`, `テスト戦略`
- step boundary:
  - `対象ファイル集合/Skills`, `Optional Tests`, `Issue Docs / Report` に閉じる

#### B1 — skill guidance / verification
- purpose:
  - agent guidance を current workflow に揃え、docs-only follow-up の evidence を閉じる
- files:
  - Skills 8 ファイル
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `report.md`

##### I1 — TDD cycle
- slice goal:
  - skills と tests を current contract に揃え、ownership separation を report に固定する

###### Red
- failing test:
  - `tests/test_init_update.py` と `tests/cli_runtime/test_wrappers.py` を current contract 前提に更新して先に失敗させる
- expected failure:
  - skill command guidance や bundled/mirror parity assertion が古い contract を検出する

###### Green
- minimum implementation:
  - Skills 8 ファイルを current contract に更新し、必要な contract assertion だけを `Optional Tests` 2 ファイルへ追加・更新する
  - `report.md` に required headings を追加し、docs-only sanity check と canonical owner reference を分離して記録する
- pass condition:
  - Skills / Optional Tests / report ownership check が QG1 を満たす

###### Refactor
- 目的:
  - skill wording と test helper の重複を整理する
- guardrail:
  - test scope を `Optional Tests` 2 ファイル以外へ広げない

#### step gate
- review:
  - code_reviewer による skill/test review
  - qa_reviewer による QG1 review
- expected tests:
  - `python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers`
  - `./spec-dock/scripts/spec-dock --help`
  - `./spec-dock/scripts/spec-dock deps --help`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
- report update:
  - reviewer verdict / test結果 / command evidence を `report.md` に残す
- commit:
  - pass 後に report 更新込みでコミットする

## S90 / S99 / close-out
- S90 docs sync verification:
  - provider-side docs と mirror docs / skills の差分を確認し、`Optional Tests` と command evidence が一致することを確認する
- S99 final diff review quality gate:
  - scope:
    - `git diff <base>...HEAD`
  - must pass:
    - diff が `対象ファイル集合` に閉じている
    - `Non-target / reject set` に差分がない
    - `report.md` に `Docs-Only Sanity Checks` と `Canonical Evidence Owners` の 2 節がある
    - `report.md` が docs-only sanity evidence と canonical owner references を混同していない
  - reviewer:
    - code_reviewer
- close-out:
  - `report.md` に final status / review verdict / test output / commit hash を追記する

## 完了条件
- requirement / design / plan の SG1 spec review が `pass`
- S01, S02, S03 の各 RG が `pass`
- QG1 が `pass`
- S99 final diff review quality gate が `pass`
- `python -m unittest tests.test_init_update tests.cli_runtime.test_wrappers` が成功する
- required command evidence が `report.md` に残る
- 最終 diff が docs/skills/tests/report の closed set に収まる
