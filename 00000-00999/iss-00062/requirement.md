---
種別: 要件定義書（Issue）
ID: "iss-00062"
タイトル: "Downstream parity and cutover readiness"
関連GitHub: ["#62"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
親: ["epic-00059", "init-local-00003"]
---

# iss-00062 Downstream parity and cutover readiness — 要件定義（WHAT / WHY）

## 目的
- `delete` / `active set` / `sync` / `validate` が `.meta.json` だけを dependency source of truth として同じ graph を解釈する状態に揃える。
- hard cutover の entry 条件を T3 integration で実施・充足・記録し、`iss-00062/report.md` を正本として cutover judgment を固定する。

## 背景・現状
- 現状の挙動:
  - `epic-00059` の requirement / design / plan で、dependency metadata の SoT を `.meta.json` に統一し、hard cutover judgment を T3 で固定する方針は決まっている。
  - `iss-00060` により `infra/deps_reader.py` は `.meta.json` を唯一の dependency read source とする契約へ移行済みで、`iss-00061` により `deps add/remove` の mutation contract と provider-side `reference_deps.md` 正本更新も完了している。
  - downstream command のうち `application/set_active.py`、`application/sync_state.py`、`application/validate_tree.py` はすでに shared topology reader を消費しているが、`application/delete_node.py` の dependency scrub はなお `deps.json` を直接読み書きしている。
  - `reference_sync.md` / `workflow_issue.md` には T3/T4 owner split、manual fix 手順、`iss-00062/report.md` fixed-key contract がまだ織り込まれておらず、checked-in dogfooding data と provider-side templates / init-update coverage には `deps.json` が残っている。
- 現状の課題:
  - mutation contract が `iss-00061` で固定されても、delete scrub と scaffold/template 側が legacy `deps.json` を残したままでは E-RQ-004 の downstream parity と cutover readiness は閉じない。
  - `set_active` / `sync` / `validate` は shared topology reader に寄っているため、T3 では広い再実装ではなく targeted regression による parity lock と mismatch 時のみの最小修正が必要である。
  - docs 更新、dogfooding checked-in data manual fix、`./spec-dock/scripts/spec-dock validate` / `sync` evidence が揃わない限り、hard cutover judgment は固定できない。
  - T3 / T4 の owner split が issue レベルで明文化されていないと、T4 が T3 judgment を再定義する余地が残る。
- 再現手順:
  1. `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/{requirement.md,design.md,plan.md}` を確認する。
  2. `spec-dock/docs/reference_deps.md` と `spec-dock/docs/reference_sync.md` を確認する。
  3. `find spec-dock/initiatives -name 'deps.json' | sort` を実行し、checked-in dogfooding data に legacy file が残っていることを確認する。
  4. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{application,infra}` 配下の downstream module を確認し、`delete_node.py` だけが legacy scrub path を保持していることを確認する。
  5. `src/spec_dock/assets/spec_dock/templates/*/deps.json` と `tests/test_init_update.py` を確認し、新規 scaffold / update coverage でも legacy file がまだ seeded されることを確認する。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
  - Filesystem:
    - `spec-dock/initiatives/**/.meta.json`
    - `spec-dock/initiatives/**/deps.json`
    - downstream application module と docs mirror
  - Report:
    - `iss-00062/report.md`
- 情報源:
  - `epic-00059/requirement.md`
  - `epic-00059/design.md`
  - `epic-00059/plan.md`
  - `iss-00060/report.md`
  - `iss-00061/report.md`
  - `epic-00059/discussions/20260410t013236z-disc-cutover-entry-criteria-and-remove-response.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - `spec-dock` runtime / docs / dogfooding data を保守する maintainer と coding agent
- 代表シナリオ:
  - maintainer が mutation contract 導入後の repo で delete / active / sync / validate を実行し、すべてが `.meta.json` SoT から同じ dependency graph を得ることを確認する。
  - maintainer が checked-in dogfooding data を manual fix し、`validate` / `sync` の実測と docs 更新を束ねて T3 judgment を固定する。

## スコープ
- MUST:
  - `application/delete_node.py` の dependency scrub contract を `.meta.json` SoT と整合させる。
  - `application/set_active.py`、`application/sync_state.py`、`application/validate_tree.py` の dependency 解釈が単一 SoT にそろっていることを targeted regression で固定し、mismatch が見つかった場合のみ最小修正する。
  - cutover boundary tests を追加し、legacy `deps.json` 残存時の boundary と manual-fix 前提を明示する。
  - provider-side docs 正本 `src/spec_dock/assets/spec_dock/docs/reference_deps.md`、`src/spec_dock/assets/spec_dock/docs/reference_sync.md`、`src/spec_dock/assets/spec_dock/docs/workflow_issue.md` と、その dogfooding docs mirror `spec-dock/docs/reference_deps.md`、`spec-dock/docs/reference_sync.md`、`spec-dock/docs/workflow_issue.md` に、dependency SoT、manual fix、`validate` / `sync` evidence、report ownership contract を反映する。
  - provider-side templates / init-update coverage が cutover 後に legacy `deps.json` を再生成しないよう、`src/spec_dock/assets/spec_dock/templates/*/deps.json` と `tests/test_init_update.py` を整合させる。
  - checked-in dogfooding data 配下の legacy dependency data を manual fix し、cutover に追従させる。
  - `iss-00062/report.md` に hard cutover entry 条件、evidence bundle、targeted regression summary、judgment verdict を固定キーで記録できる schema を定義する。
- MUST NOT:
  - `deps.json` dual-read / fallback read を downstream command に残さない。
  - hard cutover judgment の owner を T4 (`iss-00063`) 側へ移さない。
  - `iss-00061` で固定した mutation contract を downstream parity の都合で緩めない。
  - runtime auto-migration や silent fallback を manual fix の代替にしない。
- OUT OF SCOPE:
  - final regression / final parity confirmation / final spec review / epic close summary（`iss-00063` が owner）
  - dependency priority など新しい意味論の追加
  - dogfooding workspace 以外の consumer repo への一括 migration

## 境界
- Always:
  - hard cutover judgment の primary owner は T3 integration owner（`iss-00062`）である。
  - entry 条件は docs 更新 + dogfooding checked-in data manual fix + `./spec-dock/scripts/spec-dock validate` / `sync` evidence の 3 点を必須とする。
  - delete 時の dependency scrub は design / plan と整合する fail-closed contract にする。
  - `iss-00063` は T3 judgment を参照して final closure を行い、T3 judgment 自体は再定義しない。
- Ask:
  - checked-in data manual fix の途中で、epic-00059 の requirement/design/plan に未記載の新しい cutover blocker が見つかった場合。
  - report schema が `iss-00062` / `iss-00063` の分担を超えて epic-wide ADR を要求する場合。
- Never:
  - entry 条件未充足のまま `cutover judgment fixed` と記録しない。
  - `spec-dock/initiatives/**/deps.json` を cutover 後の supported source として残さない。
  - T4 issue の report で T3 verdict を上書きしない。

## 非交渉制約
- provider-side source of truth は `src/spec_dock/assets/spec_dock/...` にある。
- hard cutover judgment は T3 で固定する。
- entry 条件は docs 更新 + dogfooding manual fix + `validate` / `sync` evidence に固定する。
- cutover evidence の正本は `iss-00062/report.md` に置く。
- uppercase path を新たに増やさない。

## 前提
- `iss-00060` が `.meta.json` dependency schema と reader alignment の基盤を提供する。
- `iss-00061` が `deps add/remove` mutation contract を固定する。
- upstream prerequisite の実装完了判定は `iss-00060` / `iss-00061` の issue-level `report.md` と provider-side source / tests を権威ソースとし、front matter の状態表示だけでは判定しない。
- `iss-00063` は T3 judgment fixed 後の final closure owner として後続に控えている。

## 受け入れ条件
- AC-001 downstream delete scrub parity:
  - Actor:
    - maintainer
  - Given:
    - 削除対象 node を他 node が dependency として参照しており、dependency SoT は `.meta.json` にある。
  - When:
    - delete を実行する。
  - Then:
    - inbound dependency は scrub されるか fail-closed に検出され、保存後の graph に dangling dependency を残さない。
    - その後の `validate` / `sync` / `active set` が削除済み node を dependency として観測しない。
  - 観測点:
    - `application/delete_node.py` 系 test
    - downstream targeted validation
- AC-002 active/sync/validate parity:
  - Actor:
    - maintainer
  - Given:
    - mutation 後または manual-fix 後の同一 repo 状態
  - When:
    - `active set` / `sync` / `validate` を実行する。
  - Then:
    - 3 つの command は `.meta.json` SoT から同一の dependency graph を観測する。
    - readiness / blockers / issue edges / validation error の解釈が一致する。
  - 観測点:
    - `application/{set_active,sync_state,validate_tree}.py` 系 test
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
- AC-003 hard cutover entry completion and judgment fixation:
  - Actor:
    - T3 integration owner
  - Given:
    - docs 更新と dogfooding checked-in data manual fix が完了している。
  - When:
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行し、結果を `iss-00062/report.md` に記録する。
  - Then:
    - `iss-00062/report.md` に entry 条件の実施・充足・証跡・judgment verdict が残る。
    - hard cutover judgment は T3 で fixed として記録される。
  - 観測点:
    - `iss-00062/report.md`
    - command evidence
- AC-004 cutover evidence owner and report schema:
  - Actor:
    - maintainer / reviewer
  - Given:
    - T3/T4 の owner split がある。
  - When:
    - issue spec と report contract を確認する。
  - Then:
    - `iss-00062` が hard cutover entry 条件と judgment verdict の primary owner であることが明示される。
    - `iss-00063` は T3 evidence を参照して final closure を行うだけであることが明示される。
    - `iss-00062/report.md` に残す fixed key 群に `targeted_regression_summary` 相当が含まれ、plan/design で追跡できる。
  - 観測点:
    - `requirement.md`
    - `design.md`
    - `plan.md`
- AC-005 scaffold/template cutover parity:
  - Actor:
    - maintainer
  - Given:
    - provider-side shipped scaffold と init/update coverage が存在する。
  - When:
    - cutover readiness の観点で template / installer contract を確認する。
  - Then:
    - new init/update path は node-scoped legacy `deps.json` を再生成しない。
    - `.meta.json` only contract と checked-in dogfooding data manual fix 方針が矛盾しない。
  - 観測点:
    - `src/spec_dock/assets/spec_dock/templates/*`
    - `tests/test_init_update.py`

## 例外・エッジケース
- EC-001:
  - 条件:
    - 削除対象 node を複数の issue が dependency として参照している。
  - 期待:
    - scrub は参照元を取りこぼさず、取りこぼしがある場合は fail-closed で停止する。
  - 観測点:
    - delete scrub test
- EC-002:
  - 条件:
    - checked-in dogfooding data に legacy `deps.json` が残る、または `.meta.json` への manual fix が部分的である。
  - 期待:
    - `validate` / `sync` evidence は success として扱われず、hard cutover judgment を fixed にできない。
  - 観測点:
    - boundary test
    - `report.md`
- EC-003:
  - 条件:
    - parity test は green だが、docs 更新または report schema 記録が不足している。
  - 期待:
    - issue は complete にせず、entry 条件未充足として `report.md` に残す。
  - 観測点:
    - `report.md`
- EC-004:
  - 条件:
    - `active set` / `sync` / `validate` のいずれかで dependency 解釈が食い違う。
  - 期待:
    - T3 judgment 固定を停止し、差分を report に記録した上で parity 修正を優先する。
  - 観測点:
    - targeted runtime test
    - `report.md`
- EC-005:
  - 条件:
    - downstream runtime parity は取れているが、template / init-update path が legacy `deps.json` を再生成する。
  - 期待:
    - hard cutover judgment は fixed に進めず、template / test contract を修正する。
  - 観測点:
    - `src/spec_dock/assets/spec_dock/templates/*`
    - `tests/test_init_update.py`

## 入力→出力例
- EX-001:
  - Input:
    - docs 更新完了
    - checked-in dogfooding data manual fix 完了
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
  - Output:
    - `iss-00062/report.md` に docs update / manual fix / validate / sync / judgment verdict の fixed key が揃い、`entry_conditions_pass=true` 相当の結論が追える

## 用語（ドメイン語彙）
- TERM-001:
  - hard cutover entry 条件:
    - docs 更新、dogfooding checked-in data manual fix、`validate` / `sync` evidence の 3 点
- TERM-002:
  - cutover evidence owner:
    - hard cutover judgment の primary evidence を記録する issue owner。`iss-00062` が該当する。
- TERM-003:
  - judgment fixed:
    - T3 issue report に verdict が記録され、T4 はそれを前提に final closure へ進む状態
- TERM-004:
  - downstream parity:
    - delete / active / sync / validate が同一 SoT と同一 dependency graph 解釈を共有している状態

## 未確定事項
- なし:
  - hard cutover judgment timing、entry 条件、owner split は epic で固定済み
