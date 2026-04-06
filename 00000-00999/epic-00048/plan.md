---
種別: 計画書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-04-06"
依存: ["requirement.md", "design.md"]
親: ["init-local-00002"]
---

# epic-00048 Agent facing interface hardening and host adapter scaffolding — 計画

## この計画で満たす要件 / AC
- baseline requirements:
  - E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004, E-RQ-005
- extension requirements:
  - E-RQ-002-ext, E-RQ-003-ext, E-RQ-004-ext, E-RQ-005-ext
- baseline acceptance:
  - E-AC-001, E-AC-002, E-AC-003, E-AC-004
- extension acceptance:
  - E-AC-002-ext, E-AC-003-ext, E-AC-004-ext

## Issue 分割方針
- slicing principle:
  - protocol / runtime alignment と host adapter deployment を分け、設計契約を先に固定する。
  - `iss-00049` は自分が変更する protocol contract surface の runtime / provider docs / dogfooding docs / tests parity までを担当する。
  - `iss-00050` は host adapter scaffold work、adapter 起因の残件 parity、final epic parity/review を担当し、仕上げ専用 issue は作らない。
  - host-native deployment は本体 accepted scope を壊さず、後続 follow-up 1 issue で extension として扱う。
  - 上記 follow-up 1 issue の中で native shim 実装、installer sync/prune、dogfooding/manual validation、確認評価までを同じ 1 周で完結させる。
  - 各 issue は 1 つの成果責務を持ち、過細分化しない。
- exceptions:
  - architecture-level invalid artifact prevention は本 epic では扱わず follow-up。

## Issue 一覧（順序 / tranche 付き）
- iss-00049-protocol-contract-and-runtime-alignment:
  - 状態:
    - done
  - 目的:
    - `active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の責務を runtime・provider docs・dogfooding docs・tests で一致させ、default working set と full-history の境界を固定する。
  - deliverable:
    - protocol contract 更新、active/context 生成責務整理、artifact ごとの `projection` / `source` contract 固定、通常実行では current-future projection を優先し full-history を第一選択にしない runtime/provider-doc/dogfooding-doc/test alignment。
  - tranche:
    - tranche-1
  - closes:
    - E-RQ-001, E-RQ-002 の protocol 面
    - E-AC-001
  - depends on:
    - なし
- iss-00050-host-adapter-scaffold-and-final-parity:
  - 状態:
    - done
  - 目的:
    - Codex/Copilot 向け host adapter scaffold を `init/update` managed asset として導入し、adapter 起因の残件 parity と final spec review を閉じる。
  - deliverable:
    - adapter files、adapter metadata、installer 配布/更新、remaining adapter/provider-doc/dogfooding-doc parity 修正、host parity 証跡、final review record。
  - tranche:
    - tranche-2
  - closes:
    - E-RQ-003, E-RQ-004, E-RQ-005
    - E-AC-002, E-AC-003, E-AC-004
  - depends on:
    - iss-00049-protocol-contract-and-runtime-alignment
- follow-up-host-native-shim-deployment-and-validation-closure:
  - 状態:
    - planned
  - 目的:
    - Codex の `.codex/agents/*.toml` と GitHub Copilot の `.github/agents/*.agent.md` を thin shim として managed deployment し、manifest / source-of-truth / installer sync/prune 契約の実装から dogfooding/manual validation、確認評価までを 1 issue で閉じる。
  - deliverable:
    - provider-side native shim assets、`.agents/host-adapters/meta.json` の `targets.<host>.native_shim.{managed,owner,target_file,source_of_truth_asset,delegates_to,obsolete_managed_paths}` manifest 拡張、`src/spec_dock/cli.py` の sync/prune 追加、installer tests、host-specific artifact contract、docs refresh、dogfooding mirror 方針反映、validation/doctor 判断、manual test 記録、final review evidence。
  - tranche:
    - tranche-3
  - closes:
    - E-RQ-002-ext
    - E-RQ-003-ext
    - E-RQ-004-ext
    - E-RQ-005-ext
    - E-AC-002-ext
    - E-AC-003-ext
    - E-AC-004-ext
  - depends on:
    - iss-00050-host-adapter-scaffold-and-final-parity
  - exit gates:
    - gate-1 implementation:
      - native shim assets、manifest、installer sync/prune、tests、docs refresh を同じ changeset にそろえる。
      - manifest は `.agents/host-adapters/meta.json` を単一正本にし、`targets.<host>.native_shim.{managed,owner,target_file,source_of_truth_asset,delegates_to,obsolete_managed_paths}` の exact field 名を docs/tests/report schema と一致させる。
    - gate-2 sync-prune verification:
      - `python -m unittest discover -v`
      - gate-2 canonical command sequence は `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke` -> fixture 配置 -> `uvx --from . spec-dock update /tmp/spec-dock-native-shim-smoke` とする。
      - fixture 配置は `mkdir -p /tmp/spec-dock-native-shim-smoke/.codex/agents /tmp/spec-dock-native-shim-smoke/.github/agents`、obsolete managed fixture 2 件の配置、unknown custom fixture 2 件の配置を指す。
      - managed 扱いの旧 native file は `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md` を canonical obsolete fixture として事前配置して再現する。
      - unknown custom file は `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md` を canonical unmanaged fixture として事前配置して再現する。
      - before/after の確認対象パスは `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock.toml`, `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock.agent.md`, `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml`, `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md`, `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml`, `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md`, `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-codex-adapter/SKILL.md`, `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-copilot-adapter/SKILL.md`, `/tmp/spec-dock-native-shim-smoke/.agents/host-adapters/meta.json` とする。
      - 成功条件は、`managed_codex_shim_generated_or_updated`, `managed_copilot_shim_generated_or_updated`, `obsolete_managed_fixture_pruned`, `unknown_custom_fixture_preserved`, `baseline_skill_and_metadata_untouched` の 5 固定 subcheck が全て `pass=true` を満たすこと。
      - report では `gate_2_sync_prune_evidence.managed_codex_shim_generated_or_updated`, `managed_copilot_shim_generated_or_updated`, `obsolete_managed_fixture_pruned`, `unknown_custom_fixture_preserved`, `baseline_skill_and_metadata_untouched` を固定キーとして持ち、各キーを `expected`, `observed`, `pass` で記録する。
      - `gate_2_sync_prune_pass` は `managed_codex_shim_generated_or_updated.pass=true`、`managed_copilot_shim_generated_or_updated.pass=true`、`obsolete_managed_fixture_pruned.pass=true`、`unknown_custom_fixture_preserved.pass=true`、`baseline_skill_and_metadata_untouched.pass=true` の 5 件が全て `true` の場合のみ `true` とする。
    - gate-3 dogfooding / manual validation:
      - `spec-dock update .`
      - `spec-dock validate`
      - `gate_3_manual_validation` と `extension_closure_pass` の required host set は `codex` と `copilot` の両方固定とし、`fallback_evidence_*` は各 host の required evidence を代替できても required host set 自体は減らさない。
      - gate-3 host selection signal の accepted evidence format は `transcript_fragment` / `ui_screenshot` / `cli_log` の 3 種のみとする。
      - gate-3 の static check observed は host-scoped とし、Codex は `.codex/agents/spec-dock.toml` のみ、Copilot は `.github/agents/spec-dock.agent.md` のみを対象にした別コマンド/別記録から採取し、片方 host の match/no-match を他方の判定へ流用しない。
      - report には host ごとに `selection_evidence_format`, `selection_signal_expected_any`, `selection_signal_observed`, `selection_signal_pass` を固定キーで記録する。
      - Codex の canonical action は `.codex/agents/spec-dock.toml` を host-native agent として選択し、`Summarize the active spec-dock target and the next workflow doc to read before editing.` を実行することとする。
      - Copilot の canonical action は `.github/agents/spec-dock.agent.md` を custom agent として選択し、同じ task 文面を実行することとする。
      - `selection_signal_expected_any` の canonical serialization は JSON 互換の配列リテラル 1 形式に固定し、Codex は `["spec-dock.toml", ".codex/agents/spec-dock.toml"]`、Copilot は `["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]` とする。
      - `selection_signal_pass` は `selection_signal_observed` に host ごとの `selection_signal_expected_any` 配列のいずれか 1 要素が exact match で含まれる場合のみ `true` とし、`ui_screenshot` でも OCR または手入力転記した文字列に同じ rule を適用する。
      - report には host ごとに `response_target_expected`, `response_target_observed`, `response_target_pass`, `next_doc_expected_any`, `next_doc_observed`, `next_doc_pass` を固定キーで記録する。
      - `response_target_expected` は host 共通で `active target summary or active-none stop` に固定する。
      - `response_target_pass` は `response_target_observed` が active target 要約または `active-none` 停止を示す場合のみ `true` とする。
      - `next_doc_expected_any` の canonical serialization は JSON 互換の配列リテラル 1 形式に固定し、host 共通で `["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]` とする。
      - `next_doc_pass` は `next_doc_observed` に `next_doc_expected_any` 配列のいずれか 1 要素が exact match で含まれる場合のみ `true` とし、`ui_screenshot` でも OCR または手入力転記した文字列に同じ rule を適用する。
      - report には host ごとに `delegation_evidence_expected`, `delegation_evidence_observed`, `delegation_evidence_pass` を固定キーで記録し、Codex は `.agents/skills/spec-dock-codex-adapter/SKILL.md`、Copilot は `.agents/skills/spec-dock-copilot-adapter/SKILL.md` を `delegation_evidence_expected` に固定する。
      - `delegation_evidence_pass` は `delegation_evidence_observed` に host ごとの `delegation_evidence_expected` が exact match で含まれ、かつ shim artifact または transcript から skill への委譲成立が読める場合のみ `true` とする。
      - report には host ごとに `non_reimplementation_evidence_expected`, `non_reimplementation_evidence_observed`, `non_reimplementation_evidence_pass` を固定キーで記録し、`non_reimplementation_evidence_expected` は `no state payload key redefinition and no inline .agent/*.json/context-pack.md` に固定する。
      - `non_reimplementation_evidence_pass` は `non_reimplementation_evidence_observed` が host 対象 shim に対する `rg -n "schema_version|projection|nodes|issues|deps|source|updated_at"` の no-match と `.agent/*.json` / `context-pack.md` 非 inline を同時に示す場合のみ `true` とする。
      - report には host ごとに `direct_protocol_read_expected`, `direct_protocol_read_observed`, `direct_protocol_read_pass` を固定キーで記録し、`direct_protocol_read_expected` は `no direct active.json/index.json/deps-issues.json/index-all.json/read-order text in shim body` に固定する。
      - `direct_protocol_read_pass` は `direct_protocol_read_observed` が host 対象 shim に対する host 別コマンドの no-match を示す場合のみ `true` とする。
      - report には host ごとに `fallback_evidence_required`, `fallback_evidence_observed`, `fallback_evidence_pass` を固定キーで記録する。
      - `fallback_evidence_required` は host ごとのローカル実機確認が不能な場合のみ `true`、実機確認できた場合は `false` とする。
      - `fallback_evidence_pass` は `fallback_evidence_required=false` の場合は direct host verification が成立しているときのみ `true`、`fallback_evidence_required=true` の場合は `fallback_evidence_observed` に artifact snapshot、delegation static check、non-reimplementation static check、dated transcript / ui screenshot / cli log のいずれか 1 つが同居するときのみ `true` とする。
      - Codex の pass 条件は、report 上で `selection_signal_expected_any=["spec-dock.toml", ".codex/agents/spec-dock.toml"]` かつ `selection_signal_pass=true`、`response_target_expected=active target summary or active-none stop` かつ `response_target_pass=true`、`next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]` かつ `next_doc_pass=true` を満たし、`.agents/skills/spec-dock-codex-adapter/SKILL.md` への委譲成立を示す content check が取れ、`.codex/agents/spec-dock.toml` に state payload key 再定義や `.agent/*.json` / `context-pack.md` の inline が無く、`active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `read-order` の直接記述も無いこととする。
      - Copilot の pass 条件は、report 上で `selection_signal_expected_any=["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]` かつ `selection_signal_pass=true`、`response_target_expected=active target summary or active-none stop` かつ `response_target_pass=true`、`next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]` かつ `next_doc_pass=true` を満たし、`.agents/skills/spec-dock-copilot-adapter/SKILL.md` への委譲成立を示す content check が取れ、`.github/agents/spec-dock.agent.md` に state payload key 再定義や `.agent/*.json` / `context-pack.md` の inline が無く、`active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `read-order` の直接記述も無いこととする。
      - delegation content check の canonical static verification は Codex が `rg -n ".agents/skills/spec-dock-codex-adapter/SKILL.md" .codex/agents/spec-dock.toml`、Copilot が `rg -n ".agents/skills/spec-dock-copilot-adapter/SKILL.md" .github/agents/spec-dock.agent.md` とする。
      - runtime state 非再実装の canonical static verification は Codex が `rg -n "schema_version|projection|nodes|issues|deps|source|updated_at" .codex/agents/spec-dock.toml` の no-match、Copilot が `rg -n "schema_version|projection|nodes|issues|deps|source|updated_at" .github/agents/spec-dock.agent.md` の no-match とする。
      - direct protocol read 不在の canonical static verification は Codex が `rg -n "active\\.json|index\\.json|deps-issues\\.json|index-all\\.json|read[ -]order" .codex/agents/spec-dock.toml` の no-match、Copilot が `rg -n "active\\.json|index\\.json|deps-issues\\.json|index-all\\.json|read[ -]order" .github/agents/spec-dock.agent.md` の no-match とする。
      - 片方 host をローカル実機で確認できない場合の代替証跡は、対象 shim の artifact snapshot、delegation path の static check、runtime state 非再実装の static evidence、別環境の dated transcript / ui screenshot / cli log のいずれか 1 つから作った `selection_signal_observed` の 1 組とする。
      - gate-3 の成功条件は、host ごとの実機 pass または代替 pass がそろい、dogfooding workspace の配置結果、canonical action、delegation evidence、non-reimplementation evidence が同じ記録束で追えることとする。
    - gate-4 review pass:
      - final spec review で baseline と extension addendum の closure が分離されていることを確認して閉じる。
      - report の固定トップレベル項目は `baseline_inherited_closure` と `extension_closure` の 2 つに固定する。
      - `baseline_inherited_closure` には `accepted_issues`, `baseline_inherited_closure_pass` を必須キーとして置き、`accepted_issues` は `iss-00049,iss-00050` 固定、`baseline_inherited_closure_pass` は両 issue が done のまま reopen されず、extension 側の gate 証跡を混在させていない場合のみ `true` とする。
      - `extension_closure` には単一 follow-up issue identity を `follow_up_issue_id`, `follow_up_issue_ref`, `follow_up_issue_discussion_ref`, `follow_up_issue_status` の固定キーで保持する。
      - `follow_up_issue_ref` は actual issue artifact/URL 用の reserved field とし、issue 未作成時は placeholder を置いてよいが discussion を指さない。
      - `follow_up_issue_discussion_ref` は actual discussion artifact/URL 用の reserved field とし、issue 検討根拠の discussion を保持する。
      - `extension_closure` には `follow_up_issue_id`, `follow_up_issue_ref`, `follow_up_issue_discussion_ref`, `follow_up_issue_status`, `gate_2_sync_prune_pass`, `gate_3_manual_validation`, `gate_4_review_pass`, `extension_closure_pass` を必須キーとして置く。
      - `gate_3_manual_validation` には `codex` と `copilot` を固定キーとして置き、各 host の `selection_*`, `response_target_*`, `next_doc_*`, `delegation_*`, `non_reimplementation_*`, `direct_protocol_read_*`, `fallback_*` を配下に記録する。
      - `gate_4_review_evidence` は `additive_only_scope_preserved_expected`, `additive_only_scope_preserved_observed`, `additive_only_scope_preserved_pass`, `single_follow_up_issue_rule_expected`, `single_follow_up_issue_rule_observed`, `single_follow_up_issue_rule_pass`, `native_manifest_shape_expected`, `native_manifest_shape_observed`, `native_manifest_shape_pass`, `report_schema_compliance_expected`, `report_schema_compliance_observed`, `report_schema_compliance_pass`, `discussion_schema_compliance_expected`, `discussion_schema_compliance_observed`, `discussion_schema_compliance_pass`, `host_native_scope_consistency_expected`, `host_native_scope_consistency_observed`, `host_native_scope_consistency_pass`, `final_review_ref` を固定キーとして持つ。
      - `host_native_scope_consistency_pass` は required host set=`codex,copilot` の両 host で `delegation_evidence_pass=true`、`non_reimplementation_evidence_pass=true`、`direct_protocol_read_pass=true` がそろった場合のみ `true` とする。
      - `gate_4_review_pass` は `additive_only_scope_preserved_pass=true`、`single_follow_up_issue_rule_pass=true`、`native_manifest_shape_pass=true`、`report_schema_compliance_pass=true`、`discussion_schema_compliance_pass=true`、`host_native_scope_consistency_pass=true` の 6 件が全て `true` の場合のみ `true` とする。
      - `extension_closure_pass` は `gate_2_sync_prune_pass=true`、required host set=`codex,copilot` の両 host で `selection_signal_pass=true`、`response_target_pass=true`、`next_doc_pass=true`、`delegation_evidence_pass=true`、`non_reimplementation_evidence_pass=true`、`direct_protocol_read_pass=true`、`fallback_evidence_pass=true`、および `gate_4_review_pass=true` を同時に満たす場合のみ `true` とする。
  - 必須証跡:
    - unittest 実行ログ
    - temp repo の sync/prune before/after 証跡
    - dogfooding workspace の parity 証跡
    - manual validation 記録
    - final review pass 記録

## follow-up issue の再現手順
- gate-2 temp repo sync/prune:
  1. `python -m unittest discover -v` を実行して baseline 回帰が無いことを先に確認する。
  2. `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke` で temp repo を初期化する。
  3. `mkdir -p /tmp/spec-dock-native-shim-smoke/.codex/agents /tmp/spec-dock-native-shim-smoke/.github/agents` を実行する。
  4. `printf 'name = \"legacy managed codex shim\"\\n' > /tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml` と `printf -- '---\\nname: legacy-managed-copilot-shim\\n---\\n' > /tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md` で obsolete managed fixture を配置する。
  5. `printf 'name = \"custom reviewer\"\\n' > /tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml` と `printf -- '---\\nname: custom-reviewer\\n---\\n' > /tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md` で unknown custom fixture を配置する。
  6. update 前の `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock.toml`, `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock.agent.md`, `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml`, `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md`, `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml`, `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md`, `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-codex-adapter/SKILL.md`, `/tmp/spec-dock-native-shim-smoke/.agents/skills/spec-dock-copilot-adapter/SKILL.md`, `/tmp/spec-dock-native-shim-smoke/.agents/host-adapters/meta.json` を記録する。
  7. `uvx --from . spec-dock update /tmp/spec-dock-native-shim-smoke` を実行する。
  8. update 後に同じパスを再記録し、managed native shim の生成または更新、obsolete managed native file の削除、unknown custom file の残存、baseline managed skill と metadata の維持を照合する。
- gate-3 dogfooding/manual validation:
  1. `spec-dock update .` を実行して dogfooding workspace を同期する。
  2. `spec-dock validate` を実行して structure/error が無いことを確認する。
  3. `gate_3_manual_validation` と `extension_closure_pass` の required host set は `codex` と `copilot` の両方固定であり、`fallback_evidence_*` は各 host の証跡代替のみを許し required host set 自体は減らさない前提で記録する。
  4. Codex host では `.codex/agents/spec-dock.toml` を選択し、`Summarize the active spec-dock target and the next workflow doc to read before editing.` を実行し、`selection_evidence_format` を `transcript_fragment|ui_screenshot|cli_log` のいずれかで 1 つ選び、`selection_signal_expected_any=["spec-dock.toml", ".codex/agents/spec-dock.toml"]`、`selection_signal_observed`、`response_target_expected=active target summary or active-none stop`、`response_target_observed`、`next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`、`next_doc_observed` を記録する。
  5. Copilot host では `.github/agents/spec-dock.agent.md` を選択し、同じ task 文面を実行し、`selection_evidence_format` を `transcript_fragment|ui_screenshot|cli_log` のいずれかで 1 つ選び、`selection_signal_expected_any=["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]`、`selection_signal_observed`、`response_target_expected=active target summary or active-none stop`、`response_target_observed`、`next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`、`next_doc_observed` を記録する。
  6. `selection_signal_pass` は `selection_signal_observed` に host ごとの `selection_signal_expected_any` 配列のいずれか 1 要素が exact match で含まれる場合のみ `true` とし、`response_target_pass` は `response_target_observed` が active target 要約または `active-none` 停止を示す場合のみ `true`、`next_doc_pass` は `next_doc_observed` に `next_doc_expected_any` 配列のいずれか 1 要素が exact match で含まれる場合のみ `true` とする。`ui_screenshot` でも OCR または手入力転記した文字列に同じ rule を適用する。
  7. `rg -n ".agents/skills/spec-dock-codex-adapter/SKILL.md" .codex/agents/spec-dock.toml` と `rg -n ".agents/skills/spec-dock-copilot-adapter/SKILL.md" .github/agents/spec-dock.agent.md` を実行し、`delegation_evidence_expected`, `delegation_evidence_observed`, `delegation_evidence_pass` を host ごとに記録する。
  8. `rg -n "schema_version|projection|nodes|issues|deps|source|updated_at" .codex/agents/spec-dock.toml` と `rg -n "schema_version|projection|nodes|issues|deps|source|updated_at" .github/agents/spec-dock.agent.md` を別々に実行し、host ごとの no-match をそれぞれの `non_reimplementation_evidence_observed` として記録し、`.agent/*.json` / `context-pack.md` 非 inline を併せて `non_reimplementation_evidence_pass` を host 別に判定する。
  9. `rg -n "active\\.json|index\\.json|deps-issues\\.json|index-all\\.json|read[ -]order" .codex/agents/spec-dock.toml` と `rg -n "active\\.json|index\\.json|deps-issues\\.json|index-all\\.json|read[ -]order" .github/agents/spec-dock.agent.md` を別々に実行し、host ごとの no-match をそれぞれの `direct_protocol_read_observed` として記録し、`direct_protocol_read_pass` を host 別に判定する。
  10. 片方 host をローカル実機で確認できない場合は、artifact snapshot、delegation path の static check、runtime state 非再実装の static evidence、別環境の dated transcript / ui screenshot / cli log のいずれか 1 つを `fallback_evidence_observed` として束ね、`fallback_evidence_required=true` と `fallback_evidence_pass` を記録する。実機確認できた host は `fallback_evidence_required=false` とする。
  11. required host set=`codex,copilot` の両 host で合格または代替証跡がそろったら、report のトップレベル項目を `baseline_inherited_closure` と `extension_closure` に固定し、`baseline_inherited_closure_pass` と `extension_closure_pass` を分離して review 記録へ反映する。

## 既存 accepted scope と follow-up extension の読み方
- done として保持するもの:
  - `iss-00049` は protocol / runtime / docs / tests alignment の完了済み tranche として reopen しない。
  - `iss-00050` は thin adapter skill / metadata deployment / parity / final review の完了済み tranche として reopen しない。
- 追加するもの:
  - `follow-up-host-native-shim-deployment-and-validation-closure` は、host-native custom agent / subagent deployment を extension として追加する tranche である。
  - 旧 2 issue 推奨は採らず、実装と確認評価はこの 1 issue に統合して扱う。
  - 既存 2 issue の report / close record はそのまま残し、native artifact gap を retroactive な未完了扱いにしない。
- split rationale:
  - issue 粒度は `discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md` を根拠にしつつ、accepted scope はそのまま、host-native extension だけを 1 issue へ集約する。
  - baseline の `E-RQ/E-AC` と extension addendum の `E-RQ-*-ext` / `E-AC-*-ext` を分離して読めるため、done scope と追加 closure が競合しない。

## 統合チェックポイント
- G1 decomposition review:
  - 既存 2 issue の baseline と follow-up 1 issue の extension addendum で `E-RQ/E-AC` が全て対応しているか確認。
- G2 protocol readiness:
  - protocol 変更が `iss-00049` の runtime/provider-doc/dogfooding-doc/test scope に一貫して反映されているか確認。
- G3 adapter rollout readiness:
  - adapter 配布、`iss-00050` 担当の残件 docs parity、host parity 証跡がそろっているか確認。
- G4 native artifact contract readiness:
  - native shim / manifest / installer sync-prune 契約が確定し、gate-2 に必要な最小コマンドと証跡がそろっているか確認。
- G5 native integration readiness:
  - orchestrator 委譲、manual test、docs closure が gate-3 まででそろっているか確認。
- G9 final epic spec review:
  - baseline closure と extension closure の分離、および gate-4 review pass を確認。

## 品質ゲート
- test / observability / migration / docs:
  - `python -m unittest discover -v` 通過。
  - `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke` と `uvx --from . spec-dock update /tmp/spec-dock-native-shim-smoke` による sync/prune 確認。
  - `spec-dock update .` / `spec-dock validate` 通過。
  - host 間 parity 記録。
  - docs parity 差分ゼロまたは意図差分の説明完了。
  - native artifact manual test 記録。
  - local 実機不能 host の代替証跡記録。

## ロールアウト / docs impact
- rollout order:
  - `iss-00049` -> `iss-00050` -> `follow-up-host-native-shim-deployment-and-validation-closure`
- contract / docs refresh:
  - `iss-00049` で protocol contract surface の runtime / provider docs / dogfooding docs / tests を更新する。
  - `iss-00050` で adapter 配布と残件 parity / final review を完了する。
  - `follow-up-host-native-shim-deployment-and-validation-closure` で host-native artifact 契約、installer sync/prune、integration / validation / docs closure を同じ 1 周で完了する。

## Issue readiness contract
- Issue に要求する最低条件:
  - 変更対象の責務境界が明示されている。
  - 観測コマンドと期待結果が plan/report に残る。
  - 最小コマンド集合、必須証跡、gate 順序が issue 定義に含まれる。
  - 次 issue への handoff 条件が明確。
  - native shim が thin shim であることを review 観点に含む。

## final exit contract
- E-AC closure:
  - baseline は E-AC-001..004、extension は E-AC-002-ext..004-ext に対応する証跡が report に残る。
  - report は `baseline_inherited_closure` と `extension_closure` の 2 項目を持ち、baseline inherited closure と extension closure を一意に分離する。
- integration / rollout complete:
  - protocol と adapter が両立し、host 間で実行導線が一致し、通常実行の第一選択が full-history になっていない。
  - orchestrator が host-native agent / subagent へ spec-dock 操作を委譲できる。
- docs impact resolved:
  - `iss-00049` 対象の protocol docs parity、`iss-00050` 対象の adapter/final parity、`follow-up-host-native-shim-deployment-and-validation-closure` 対象の native artifact parity がそれぞれ完了し、final review が pass している。

## 依存 / ブロッカー
- D-001:
  - 既存 `.agents/skills` managed asset 配布機構の整合。
- D-002:
  - architecture-level invalid artifact prevention の follow-up（本 epic では非対応）。
- D-003:
  - OpenAI Codex / GitHub Copilot の host-native artifact 仕様変更が無いこと、または変更時に追随できること。

## 設計上の決定
- D-004:
  - host adapter metadata は `.agents/host-adapters/meta.json` を第一案ではなく採用決定とする。
  - `iss-00049` では artifact ごとの top-level metadata contract を固定する（`index.json`=`projection=current-future` / no new `source`、`index-all.json`=`projection=full-history` / no new `source`、`deps-issues.json`=`projection=open-issues-dependency-view` / provenance `source` 維持）。
- D-005:
  - `.agents/skills/*` を正本、`.codex/agents/*` / `.github/agents/*` を thin shim とする。
