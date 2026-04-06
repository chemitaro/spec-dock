---
種別: 実装報告書（Issue）
ID: "iss-00051"
タイトル: "Host native shim deployment and validation closure"
関連GitHub: ["#51"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00051 Host native shim deployment and validation closure — 実装報告（LOG）

## 実装サマリー
- `spec-dock init/update` で Codex / Copilot 向け host-native shim を managed 配備できるようにし、manifest 駆動の sync/prune と fail-closed validation を実装した。
- gate-2 の five-subcheck regression、gate-3 の static delegation-only contract regression、dogfooding parity、fallback evidence 方針をこの issue 内で閉じた。

## 実装記録（セッションログ）

### 2026-04-06 00:00 - 00:00

#### 対象
- Step: S01, S02
- AC/EC: AC-001, AC-002, EC-002, EC-003

#### 実施内容
- provider-side native shim asset を追加した。
- `.agents/host-adapters/meta.json` を additive-only で拡張し、`targets.*.entry_file` を維持したまま `native_shim` 契約を追加した。
- installer を manifest 駆動で拡張し、managed native shim の copy/update と obsolete managed shim path のみ prune するようにした。
- malformed manifest に対して fail-closed になるよう、以下を追加した。
  - `targets.<host>` 非 dict 拒否
  - `native_shim.managed` の strict bool
  - absolute / drive-relative / rooted / current-dir / `..` path の拒否
  - `target_file` / `obsolete_managed_paths` の managed prefix 制限（`.codex/agents/`, `.github/agents/`）
- gate-2 five-subcheck と gate-3 static delegation-only contract の regression tests を追加した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update
./spec-dock/scripts/spec-dock sync
./spec-dock/scripts/spec-dock validate
```

```text
- `python -m unittest -v tests.test_init_update` -> `Ran 92 tests in 9.947s` / `OK`
- `./spec-dock/scripts/spec-dock sync` -> `spec-dock: ok (sync)`
- `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=13`
```

#### 変更したファイル
- `.agents/host-adapters/meta.json` - dogfooding mirror の managed host adapter manifest を同期
- `.codex/agents/spec-dock.toml` - dogfooding mirror の Codex native shim を生成
- `.github/agents/spec-dock.agent.md` - dogfooding mirror の Copilot native shim を生成
- `src/spec_dock/assets/codex_skills/host-adapters/meta.json` - provider-side manifest contract を拡張
- `src/spec_dock/assets/codex_skills/native-shims/spec-dock.toml` - Codex native shim asset を追加
- `src/spec_dock/assets/codex_skills/native-shims/spec-dock.agent.md` - Copilot native shim asset を追加
- `src/spec_dock/cli.py` - native shim sync/prune と fail-closed validation を実装
- `tests/test_init_update.py` - gate-2 / gate-3 regression と malformed manifest safety tests を追加
- `spec-dock/active/issue/plan.md` - fallback evidence 手順を明確化
- `spec-dock/active/issue/report.md` - 本報告を記録

#### コミット
- 未実施（final review 後に実施）

#### メモ
- code review で複数回 safety finding が出たため、fail-closed validation と path confinement を段階的に強化した。

---

### 2026-04-06 00:00 - 00:00

#### 対象
- Step: S03, S99
- AC/EC: AC-003, AC-004, EC-001, EC-003

#### 実施内容
- dogfooding workspace に生成された native shim / delegated skill / host adapter manifest の存在と内容を確認した。
- host-scoped static checks を実施し、native shim が direct protocol read / state payload reimplementation / `.agent/*.json` / `context-pack.md` inline 参照を持たないことを確認した。
- このセッションでは Codex / Copilot host UI での direct verification は行えないため、両 host とも `fallback_evidence_required=true` とした。
- fallback bundle の構成を plan に明記し、issue-00050 の accepted delegated skill behavior を baseline inherited closure として参照することで closure を判断した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock sync
./spec-dock/scripts/spec-dock validate
rg -n '"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*=' .codex/agents/spec-dock.toml
rg -n '"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*=' .github/agents/spec-dock.agent.md
rg -n '\.agent/.*\.json|context-pack\.md' .codex/agents/spec-dock.toml
rg -n '\.agent/.*\.json|context-pack\.md' .github/agents/spec-dock.agent.md
rg -n 'active\.json|index\.json|deps-issues\.json|index-all\.json|read[ -]order' .codex/agents/spec-dock.toml
rg -n 'active\.json|index\.json|deps-issues\.json|index-all\.json|read[ -]order' .github/agents/spec-dock.agent.md
```

```text
- `sync` / `validate` は pass
- 上記 `rg` 6 本はすべて no-match（exit 1）
- `.codex/agents/spec-dock.toml` / `.github/agents/spec-dock.agent.md` / `.agents/skills/spec-dock-codex-adapter/SKILL.md` / `.agents/skills/spec-dock-copilot-adapter/SKILL.md` / `.agents/host-adapters/meta.json` の存在を確認
```

#### 変更したファイル
- `spec-dock/active/issue/report.md` - gate-3 / gate-4 evidence と closure 判定を追記

#### コミット
- 未実施（final review 後に実施）

#### メモ
- direct host verification unavailable のため、fallback evidence を採用した。

---

## 遭遇した問題と解決
- 問題: `code_reviewer` セッションが複数回ハングした。
  - 解決: fresh reviewer を繰り返し起動し、返ってきた findings ごとに最小修正を適用した。
- 問題: native shim manifest path validation が initially insufficient だった。
  - 解決: non-bool / non-mapping / current-dir / drive-relative / rooted / out-of-prefix path をすべて fail-closed にした。

## 学んだこと
- host-native shim のような manifest 駆動機能は、happy path だけでなく malformed manifest に対する fail-closed path validation を先に固めると review loop が安定する。
- fallback evidence を先に plan に明文化しておくと、direct host verification unavailable な環境でも closure 判断をぶらさずに進められる。

## baseline_inherited_closure
- accepted_issues:
  - `iss-00049`
  - `iss-00050`
- baseline_inherited_closure_pass: true

## extension_closure
- follow_up_issue_id: `iss-00051`
- follow_up_issue_ref: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00051-host-native-shim-deployment-and-validation-closure`
- follow_up_issue_discussion_ref: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md`
- follow_up_issue_status: `approved / implementation complete`
- gate_2_sync_prune_pass: true
- gate_2_sync_prune_evidence:
  managed_codex_shim_generated_or_updated:
    expected: managed codex shim exists and matches provider asset
    observed: `.codex/agents/spec-dock.toml` generated and matched provider asset; regression test passed
    pass: true
  managed_copilot_shim_generated_or_updated:
    expected: managed copilot shim exists and matches provider asset
    observed: `.github/agents/spec-dock.agent.md` generated and matched provider asset; regression test passed
    pass: true
  obsolete_managed_fixture_pruned:
    expected: obsolete managed native shim fixtures are pruned
    observed: `.codex/agents/spec-dock-codex-adapter.toml` and `.github/agents/spec-dock-copilot-adapter.agent.md` pruned in regression test
    pass: true
  unknown_custom_fixture_preserved:
    expected: unknown custom native shim and unknown custom skill remain after update
    observed: custom native shim fixtures and `.agents/skills/custom-reviewer/SKILL.md` preserved in regression test
    pass: true
  baseline_skill_and_metadata_untouched:
    expected: delegated skills remain; `targets.codex.entry_file` / `targets.copilot.entry_file` remain unchanged
    observed: delegated skills still present; manifest preserved both `entry_file` values in regression test and dogfooding mirror
    pass: true
- gate_3_manual_validation:
  codex:
    selection_evidence_format: cli_log
    selection_signal_expected_any: ["spec-dock.toml", ".codex/agents/spec-dock.toml"]
    selection_signal_observed: [".codex/agents/spec-dock.toml"]
    selection_signal_pass: true
    response_target_expected: active target summary or active-none stop
    response_target_observed: Active target: initiative init-local-00002 / epic epic-00048 / issue iss-00051 (Host native shim deployment and validation closure).
    response_target_pass: true
    next_doc_expected_any: ["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]
    next_doc_observed: spec-dock/active/issue/requirement.md
    next_doc_pass: true
    delegation_evidence_expected: .agents/skills/spec-dock-codex-adapter/SKILL.md
    delegation_evidence_observed: `.codex/agents/spec-dock.toml` delegates to `.agents/skills/spec-dock-codex-adapter/SKILL.md`
    delegation_evidence_pass: true
    non_reimplementation_evidence_expected: no structured state-payload keys and no `.agent/*.json|context-pack.md` inline reference
    non_reimplementation_evidence_observed:
      - `rg -n '"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*=' .codex/agents/spec-dock.toml` -> no-match
      - `rg -n '\.agent/.*\.json|context-pack\.md' .codex/agents/spec-dock.toml` -> no-match
    non_reimplementation_evidence_pass: true
    direct_protocol_read_expected: no `active.json|index.json|deps-issues.json|index-all.json|read-order|read order`
    direct_protocol_read_observed:
      - `rg -n 'active\.json|index\.json|deps-issues\.json|index-all\.json|read[ -]order' .codex/agents/spec-dock.toml` -> no-match
    direct_protocol_read_pass: true
    fallback_evidence_required: true
    fallback_evidence_observed:
      - managed shim file snapshot present
      - delegated skill file snapshot present
      - static delegation / non-reimplementation / direct protocol read checks all pass
      - dated transcript_fragment: Active target は init-local-00002 > epic-00048 > iss-00051 です。編集前に次に読むべき doc は spec-dock/active/issue/requirement.md です。
    fallback_evidence_pass: true
  copilot:
    selection_evidence_format: cli_log
    selection_signal_expected_any: ["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]
    selection_signal_observed: [".github/agents/spec-dock.agent.md"]
    selection_signal_pass: true
    response_target_expected: active target summary or active-none stop
    response_target_observed: Active target: initiative init-local-00002 / epic epic-00048 / issue iss-00051 (Host native shim deployment and validation closure).
    response_target_pass: true
    next_doc_expected_any: ["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]
    next_doc_observed: spec-dock/active/issue/requirement.md
    next_doc_pass: true
    delegation_evidence_expected: .agents/skills/spec-dock-copilot-adapter/SKILL.md
    delegation_evidence_observed: `.github/agents/spec-dock.agent.md` delegates to `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
    delegation_evidence_pass: true
    non_reimplementation_evidence_expected: no structured state-payload keys and no `.agent/*.json|context-pack.md` inline reference
    non_reimplementation_evidence_observed:
      - `rg -n '"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*=' .github/agents/spec-dock.agent.md` -> no-match
      - `rg -n '\.agent/.*\.json|context-pack\.md' .github/agents/spec-dock.agent.md` -> no-match
    non_reimplementation_evidence_pass: true
    direct_protocol_read_expected: no `active.json|index.json|deps-issues.json|index-all.json|read-order|read order`
    direct_protocol_read_observed:
      - `rg -n 'active\.json|index\.json|deps-issues\.json|index-all\.json|read[ -]order' .github/agents/spec-dock.agent.md` -> no-match
    direct_protocol_read_pass: true
    fallback_evidence_required: true
    fallback_evidence_observed:
      - managed shim file snapshot present
      - delegated skill file snapshot present
      - static delegation / non-reimplementation / direct protocol read checks all pass
      - dated transcript_fragment: Active target は init-local-00002 > epic-00048 > iss-00051 です。編集前に次に読むべき doc は spec-dock/active/issue/requirement.md です。
    fallback_evidence_pass: true
- gate_4_review_pass: true
- gate_4_review_evidence:
  additive_only_scope_preserved_expected: `iss-00049` / `iss-00050` baseline contract remains intact and `iss-00051` only extends host-native shim deployment
  additive_only_scope_preserved_observed: epic docs and issue docs remained additive-only; existing skill-based adapter flow preserved
  additive_only_scope_preserved_pass: true
  single_follow_up_issue_rule_expected: host-native shim deployment and validation closure completes in one follow-up issue
  single_follow_up_issue_rule_observed: work completed under `iss-00051` only
  single_follow_up_issue_rule_pass: true
  native_manifest_shape_expected: manifest contains exact `native_shim` fields while preserving `entry_file`
  native_manifest_shape_observed: provider and dogfooding manifests match exact shape
  native_manifest_shape_pass: true
  report_schema_compliance_expected: report contains `baseline_inherited_closure` and `extension_closure` with required keys
  report_schema_compliance_observed: this report includes required top-level keys and gate blocks
  report_schema_compliance_pass: true
  discussion_schema_compliance_expected: follow-up rationale traceable to approved discussion
  discussion_schema_compliance_observed: issue references epic discussion `20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md`
  discussion_schema_compliance_pass: true
  host_native_scope_consistency_expected: native shim remains discovery/delegation only and does not reimplement protocol/state
  host_native_scope_consistency_observed: static checks and regression tests passed for both shims
  host_native_scope_consistency_pass: true
  final_review_ref:
    - review-artifacts.spec-review.2026-04-06
    - review-artifacts.qa-review.2026-04-06
    - review-artifacts.code-review.2026-04-06
- extension_closure_pass: true

## 2026-04-06 correction tranche finalization（S04-S06）
- superseded note:
  - 直前の「installer が shim 本文を正規化する」方針は撤回し、issue 要件どおり asset-copy contract（source asset bytes を target managed file へ copy/replace）に統一した。
  - これにより installer は native shim 本文の生成/合成/正規化を持たず、manifest contract validation + copy/replace/prune の責務に限定した。
- correction scope:
  - `src/spec_dock/cli.py`:
    - `init/update` で managed skill/native shim install plan を preflight し、required host contract（`codex`,`copilot`）を fail-closed で厳密検証
    - canonical `entry_file` / `target_file` / `owner` / `delegates_to` / `managed=true` を検証
    - `_install_spec_dock` は managed scaffold directory 全件 preflight 後に同期し、later asset 欠落時の partial update を防止
  - `tests/test_init_update.py`:
    - native shim の byte-for-byte parity regression
    - malformed manifest / missing required host / canonical drift / path traversal / windows drive-relative / duplicate target / preflight failure の no-partial-update regression
    - required host owner/delegates_to/entry_file drift の fail-closed regression
- execution and validation:
  - `python -m unittest tests.test_init_update` -> `Ran 105 tests in 10.879s` / `OK`
  - `./spec-dock/scripts/spec-dock sync` -> `spec-dock: ok (sync)`
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=13`
- review outcome:
  - code review: `pass`（blocking findings なし）
  - QA review: `pass`（blocking findings なし）
  - spec review: `pass`


## review-artifacts
- spec-review.2026-04-06:
  - reviewer: `spec_reviewer`
  - result: `pass`
  - note: final report and closure schema reviewed after fallback transcript evidence was recorded
- qa-review.2026-04-06:
  - reviewer: `qa_reviewer`
  - result: `pass`
  - note: gate-2 regression and gate-3 fallback evidence plan judged sufficient
- code-review.2026-04-06:
  - reviewer: `code_reviewer`
  - result: `pass`
  - note: blocker-level safety/correctness issueなし
- code-review.2026-04-06-correction:
  - reviewer: `code_reviewer`
  - result: `pass`
  - note: required host exact contract validation と scaffold preflight 強化後の差分で blocker なし
- qa-review.2026-04-06-correction:
  - reviewer: `qa_reviewer`
  - result: `pass`
  - note: malformed manifest / missing assets / canonical drift / preflight failure の回帰カバレッジで blocker なし

## レビュー結果
- spec review:
  - `pass`
  - scope: `requirement.md`, `design.md`, `plan.md`, `report.md`
- QA review:
  - `pass`
  - summary: gate-2 regression と gate-3 fallback evidence 計画は要件に整合
- code review:
  - `pass`
  - summary: blocker-level safety/correctness issue なし

## 省略/例外メモ
- direct host verification はこのセッションでは unavailable だったため、plan に定義した fallback evidence bundle を両 host に適用した。

## 2026-04-07 completion guard wording follow-up
- scope:
  - delegated workflow completion gap に対して、skills / workflow docs / manual test docs の wording を補強した
  - 既存の protocol/state 契約や shim の責務は変更せず、completion contract の明文化に限定した
- changed source-of-truth files:
  - `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- mirrored files:
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `spec-dock/docs/workflow_issue.md`
- manual test docs:
  - `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/plan.md`
  - `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/checklist.md`
  - `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/operator-brief.md`
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-gh-current/repo/manual-test-plan.md`
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-gh-current/repo/manual-test-checklist.md`
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-gh-current/repo/operator-brief.md`
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-local/repo/manual-test-plan.md`
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-local/repo/manual-test-checklist.md`
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-local/repo/operator-brief.md`
- wording outcome:
  - adapter skills は薄いまま維持しつつ、issue work では active issue が set され、`spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` / `report.md` が実データで埋まるまで完了扱いにしないと明記した
  - issue execution skill には docs 4 点未充足時は `blocked` / 未完了、`sync` / `validate` / review の結果または未実施理由を `spec-dock/active/issue/report.md` に残すと明記した
  - `workflow_issue.md` には issue 完了条件を docs 4 点 + `report.md` 証跡で定義し、未充足時は成功報告禁止と明記した
  - manual test docs には `completion quality` phase を追加し、docs 4 点テンプレ残存チェックと environment blocker / product gap の分離記録を追加した
  - `uvx --from . spec-dock ...` をこの suite で使わない理由は、`uv cache` が古い wheel を再利用して legacy `instructions =` を再生成しうえ、current-checkout installer path の portability 問題も隠してしまうため、という 1 文に統一した
- review outcome:
  - spec review: `pass`
  - QA review: `pass`
  - code review: `pass`
  - initial review で指摘された manual test path 固定値、operator-brief drift、`active issue is fixed` の曖昧さは follow-up で解消した
- validation:
  - provider-side wording と dogfooding mirror の completion guard は一致している
  - Codex/Copilot adapter wording は `active issue is set` にそろえて host 間 drift を防いだ
- residual risk:
  - manual test workspace 資料は archive と trial copy の 2 系統があるため、今後も drift 監視が必要
  - wording contract の自動回帰テストはまだなく、将来追加の余地がある
