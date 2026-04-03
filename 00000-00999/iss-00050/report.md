# iss-00050 report

## 2026-04-03 spec authoring
- 実施内容:
  - requirement/design/plan を 2 issue split の後半 owner として具体化した。
  - host adapter scaffold、installer sync、docs parity、final spec review を同一 issue で閉じる構成にした。
  - `deps.json` で `iss-00049` 依存を追加した。

## 2026-04-03 spec review
- review scope:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - epic-00048 `requirement.md` / `design.md` / `plan.md`
  - `iss-00049` docs との責務境界
- checklist:
  - requirement:
    - thin adapter contract、installer ownership、parity owner、final review owner が明示されていること
  - design:
    - installer/asset layout、metadata path、tests、rollback が明示されていること
  - plan:
    - issue-00049 依存、installer step、parity step、final spec review step が分かれていること
- findings:
  - none
- verdict:
  - pass
- note:
  - 実装開始前の docs refresh は完了。GitHub Copilot orchestrator はこの版を前提に着手してよい
- note:
  - host adapter metadata は `.agents/host-adapters/meta.json` に固定した

## 2026-04-03 readiness review for implementation start
- review scope:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- findings:
  - `design.md` に明示的な依存関係分析がなく、S01-S04 の順序根拠が文章として固定されていなかった。
  - `plan.md` に依存関係分析から step 順を導く節がなく、shared template の現行期待とずれていた。
- action:
  - `design.md` に依存関係分析と dependency-oriented PlantUML を追記した。
  - `plan.md` に `実装順序の根拠` を追加し、design から sequencing を導く契約を明記した。

## 2026-04-03 spec re-review after readiness fixes
- review scope:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
- checklist:
  - design:
    - upstream/downstream と実装起点が明示されていること
    - module / dependency 図が implementation order と矛盾しないこと
  - plan:
    - step 順が design の依存関係分析から導かれていること
    - review/test/report-before-commit flow が維持されていること
  - scope:
    - issue-00049 protocol を再定義せず、host adapter scaffold / parity / final review に閉じていること
- findings:
  - none
- verdict:
  - pass

## 2026-04-03 S01 spec fixed point for host adapter deployment
- 実行コマンド:
  - `git --no-pager diff -- spec-dock/active/issue/design.md spec-dock/active/issue/plan.md`
- review scope:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
- 初回 reviewer verdict:
  - fail
- blocking findings:
  - `design.md` が `.agents/host-adapters/meta.json` を optional に読める表現を残しており、S01 fixed point として不十分だった
  - `plan.md` の S02 gate に unknown custom skill preservation が明示されておらず、managed prune safety の確認が不足していた
- 修正内容:
  - `design.md`
    - `.agents/host-adapters/meta.json` を必須の installer managed asset として固定した
    - host adapter metadata の source-of-truth / ownership 境界を明文化した
    - metadata contract に `schema_version` / `targets` / `generated_by` / `updated_at` / `owner` を追加した
    - metadata sync を optional ではなく required として設計に反映した
  - `plan.md`
    - S02/B2 に unknown custom skill preservation test を明示した
    - S02 の pass condition に unknown custom skills preserve を追加した
    - step gate の expected tests に preservation test を追加した
- 再 review verdict:
  - pass
- reviewer result:
  - `review_status: pass`
  - reason:
    - S01 fixed point として、metadata contract、unknown-skill preservation、issue boundary、rollout order が実装開始可能な粒度まで整合した
  - non-blocking note:
    - `meta.json.targets` の exact subshape は P2 として残っており、S02 で test 付きで pin する
- 想定外と対処:
  - 初回 spec review pass 済みでも、implementation start 観点では S01 fixed point の strictness が不足していた
  - docs-only で差分を閉じ、rerun で implementation start fixed point を通した
- refactor:
  - なし
