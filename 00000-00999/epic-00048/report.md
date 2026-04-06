---
種別: レポート（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00002"]
---

# epic-00048 Agent facing interface hardening and host adapter scaffolding — レポート（closure schema）

この report は additive-only 原則で、完了済み baseline と follow-up extension の closure を同一文書内で分離して記録する。

## baseline_inherited_closure
- accepted_issues: `iss-00049,iss-00050`
- baseline_inherited_closure_pass: `true | false`
- baseline_status_summary:
  - `iss-00049`: `done | reopened`
  - `iss-00050`: `done | reopened`
- evidence_refs:
  - `iss-00049`: `...`
  - `iss-00050`: `...`
- note:
  - extension 側の gate-2 / gate-3 / gate-4 証跡を baseline close record と混在させない。

## extension_closure
`extension_closure` の required host set は `codex` と `copilot` の両方固定とする。`fallback_evidence_*` は各 host の required evidence を代替できても、required host set 自体は減らさない。
`follow_up_issue_ref` は actual issue artifact/URL 用、`follow_up_issue_discussion_ref` は actual discussion artifact/URL 用として使い分ける。
`gate_2_sync_prune_pass` は `managed_codex_shim_generated_or_updated.pass=true`、`managed_copilot_shim_generated_or_updated.pass=true`、`obsolete_managed_fixture_pruned.pass=true`、`unknown_custom_fixture_preserved.pass=true`、`baseline_skill_and_metadata_untouched.pass=true` の 5 件が全て `true` の場合のみ `true` とする。
`host_native_scope_consistency_pass` は required host set=`codex,copilot` の両 host で `delegation_evidence_pass=true`、`non_reimplementation_evidence_pass=true`、`direct_protocol_read_pass=true` がそろった場合のみ `true` とする。
`gate_4_review_pass` は `additive_only_scope_preserved_pass=true`、`single_follow_up_issue_rule_pass=true`、`native_manifest_shape_pass=true`、`report_schema_compliance_pass=true`、`discussion_schema_compliance_pass=true`、`host_native_scope_consistency_pass=true` の 6 件が全て `true` の場合のみ `true` とする。
`extension_closure_pass` は `gate_2_sync_prune_pass=true`、required host set=`codex,copilot` の両 host で `selection_signal_pass=true`、`response_target_pass=true`、`next_doc_pass=true`、`delegation_evidence_pass=true`、`non_reimplementation_evidence_pass=true`、`direct_protocol_read_pass=true`、`fallback_evidence_pass=true`、および `gate_4_review_pass=true` を同時に満たす場合のみ `true` とする。

- follow_up_issue_id: `follow-up-host-native-shim-deployment-and-validation-closure`
- follow_up_issue_ref: `pending-actual-issue-artifact-or-url`
- follow_up_issue_discussion_ref: `discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md`
- gate_2_sync_prune_pass: `true | false`
- follow_up_issue_status: `planned | in_progress | done`
- gate_2_sync_prune_evidence:
  - canonical_command_sequence:
    - `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke`
    - fixture 配置
    - `uvx --from . spec-dock update /tmp/spec-dock-native-shim-smoke`
  - before_after_path_set:
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml`
    - `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-codex-adapter/SKILL.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-copilot-adapter/SKILL.md`
    - `/tmp/spec-dock-native-shim-smoke/.agents/host-adapters/meta.json`
  - managed_codex_shim_generated_or_updated:
    - expected: `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock.toml` が update 後に生成または更新される。
    - observed: `...`
    - pass: `true | false`
  - managed_copilot_shim_generated_or_updated:
    - expected: `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock.agent.md` が update 後に生成または更新される。
    - observed: `...`
    - pass: `true | false`
  - obsolete_managed_fixture_pruned:
    - expected: `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md` が update 後に prune される。
    - observed: `...`
    - pass: `true | false`
  - unknown_custom_fixture_preserved:
    - expected: `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md` が update 後も残る。
    - observed: `...`
    - pass: `true | false`
  - baseline_skill_and_metadata_untouched:
    - expected: `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-codex-adapter/SKILL.md`、`/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-copilot-adapter/SKILL.md`、`/tmp/spec-dock-native-shim-smoke/.agents/host-adapters/meta.json` が壊れていない。
    - observed: `...`
    - pass: `true | false`
- gate_3_manual_validation:
  - Codex の static check observed は `.codex/agents/spec-dock.toml` だけから採取する。
  - Copilot の static check observed は `.github/agents/spec-dock.agent.md` だけから採取する。
  - 片方 host の match/no-match は他方 host の observed/pass に流用しない。
  - codex:
    - selection_evidence_format: `transcript_fragment | ui_screenshot | cli_log`
    - selection_signal_expected_any: `["spec-dock.toml", ".codex/agents/spec-dock.toml"]`
    - selection_signal_observed: `...`
    - selection_signal_pass: `true | false`
    - response_target_expected: `active target summary or active-none stop`
    - response_target_observed: `...`
    - response_target_pass: `true | false`
    - next_doc_expected_any: `["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`
    - next_doc_observed: `...`
    - next_doc_pass: `true | false`
    - delegation_evidence_expected: `.agents/skills/spec-dock-codex-adapter/SKILL.md`
    - delegation_evidence_observed: `...`
    - delegation_evidence_pass: `true | false`
    - non_reimplementation_evidence_expected: `no state payload key redefinition and no inline .agent/*.json/context-pack.md`
    - non_reimplementation_evidence_observed: `...`
    - non_reimplementation_evidence_pass: `true | false`
    - direct_protocol_read_expected: `no direct active.json/index.json/deps-issues.json/index-all.json/read-order text in shim body`
    - direct_protocol_read_observed: `...`
    - direct_protocol_read_pass: `true | false`
    - fallback_evidence_required: `true | false`
    - fallback_evidence_observed: `...`
    - fallback_evidence_pass: `true | false`
  - copilot:
    - selection_evidence_format: `transcript_fragment | ui_screenshot | cli_log`
    - selection_signal_expected_any: `["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]`
    - selection_signal_observed: `...`
    - selection_signal_pass: `true | false`
    - response_target_expected: `active target summary or active-none stop`
    - response_target_observed: `...`
    - response_target_pass: `true | false`
    - next_doc_expected_any: `["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`
    - next_doc_observed: `...`
    - next_doc_pass: `true | false`
    - delegation_evidence_expected: `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
    - delegation_evidence_observed: `...`
    - delegation_evidence_pass: `true | false`
    - non_reimplementation_evidence_expected: `no state payload key redefinition and no inline .agent/*.json/context-pack.md`
    - non_reimplementation_evidence_observed: `...`
    - non_reimplementation_evidence_pass: `true | false`
    - direct_protocol_read_expected: `no direct active.json/index.json/deps-issues.json/index-all.json/read-order text in shim body`
    - direct_protocol_read_observed: `...`
    - direct_protocol_read_pass: `true | false`
    - fallback_evidence_required: `true | false`
    - fallback_evidence_observed: `...`
    - fallback_evidence_pass: `true | false`
- gate_4_review_pass: `true | false`
- gate_4_review_evidence:
  - additive_only_scope_preserved_expected: `baseline accepted scope は additive-only で維持され、iss-00049 / iss-00050 の close record を未完了へ読み替えない。`
  - additive_only_scope_preserved_observed: `...`
  - additive_only_scope_preserved_pass: `true | false`
  - single_follow_up_issue_rule_expected: `host-native extension は single follow-up issue として閉じ、追加 split を増やさない。`
  - single_follow_up_issue_rule_observed: `...`
  - single_follow_up_issue_rule_pass: `true | false`
  - native_manifest_shape_expected: `.agents/host-adapters/meta.json` が `targets.<host>.native_shim.{managed,owner,target_file,source_of_truth_asset,delegates_to,obsolete_managed_paths}` の exact shape を持ち、canonical target filename が `.codex/agents/spec-dock.toml` と `.github/agents/spec-dock.agent.md` に固定されている。
  - native_manifest_shape_observed: `...`
  - native_manifest_shape_pass: `true | false`
  - report_schema_compliance_expected: `report schema は baseline_inherited_closure / extension_closure 分離、fixed host keys、fixed review keys、fixed follow-up issue identity keys を持ち、reserved_field_rule や *_rule の helper key を置かない fixed key template を満たす。`
  - report_schema_compliance_observed: `...`
  - report_schema_compliance_pass: `true | false`
  - discussion_schema_compliance_expected: `discussion は未確定 alternatives を残さず、adopted native shim contract、reserved field の使い分け、gate aggregate rule を requirement/design/plan/report と同じ語彙で記録する。`
  - discussion_schema_compliance_observed: `...`
  - discussion_schema_compliance_pass: `true | false`
  - host_native_scope_consistency_expected: `native shim は discovery/delegation only で、protocol reads は委譲先 skill/subagent が担う。`
  - host_native_scope_consistency_observed: `...`
  - host_native_scope_consistency_pass: `true | false`
  - final_review_ref: `...`
- extension_closure_pass: `true | false`
