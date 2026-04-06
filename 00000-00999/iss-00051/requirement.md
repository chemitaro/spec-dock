---
種別: 要件定義書（Issue）
ID: "iss-00051"
タイトル: "Host native shim deployment and validation closure"
関連GitHub: ["#51"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-06"
親: ["epic-00048", "init-local-00002"]
---

# iss-00051 Host native shim deployment and validation closure — 要件定義（WHAT / WHY）

## 目的
- `spec-dock init/update` 時に Codex / GitHub Copilot の host-native shim を managed 配備できる状態にする。
- native shim の managed ownership / sync / prune / dogfooding validation を 1 issue の中で完結させる。
- orchestrator が native shim を entrypoint にしつつ、実際の spec-dock 操作は既存 skill に委譲する契約を実装可能な粒度へ固定する。

## 背景・現状
- 現状の挙動:
  - `iss-00049` / `iss-00050` で `.agents/skills/spec-dock-codex-adapter/SKILL.md`、`.agents/skills/spec-dock-copilot-adapter/SKILL.md`、`.agents/host-adapters/meta.json` までは managed asset として配備済み。
  - しかし host-native discovery 用の `.codex/agents/*.toml` と `.github/agents/*.agent.md` はまだ生成されない。
- 現状の課題:
  - Codex / Copilot のオーケストレーターは native subagent/custom agent を直接選択できず、spec-dock 操作を host-native entrypoint へ委譲できない。
  - installer sync/prune の ownership が未実装のため、managed native shim と unknown custom native agent の境界がコードで固定されていない。
  - manual validation を別 issue に分けず 1 loop で閉じる契約が必要。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock をインストールした repo で Codex CLI / GitHub Copilot CLI を使う orchestrator
- 代表シナリオ:
  - repo に `spec-dock init` または `spec-dock update` を実行すると、Codex は `.codex/agents/spec-dock.toml`、Copilot は `.github/agents/spec-dock.agent.md` を host-native entrypoint として発見できる。
  - orchestrator は native shim を選択し、shim は `.agents/skills/spec-dock-codex-adapter/SKILL.md` または `.agents/skills/spec-dock-copilot-adapter/SKILL.md` へ委譲する。
  - dogfooding workspace でも同じ配備結果を再現し、manual validation の証跡を 1 issue の report に閉じる。

## スコープ
- MUST:
  - `.agents/host-adapters/meta.json` を `targets.<host>.native_shim.{managed,owner,target_file,source_of_truth_asset,delegates_to,obsolete_managed_paths}` を含む exact shape へ拡張する。
  - additive-only compatibility として、既存の `targets.codex.entry_file` / `targets.copilot.entry_file` は削除・改名・意味変更せず維持する。
  - provider-side source of truth に native shim asset を追加し、Codex 向け `.codex/agents/spec-dock.toml`、Copilot 向け `.github/agents/spec-dock.agent.md` を managed 配備できるようにする。
  - native shim asset の正の最小契約を固定する。
    - Codex TOML は `spec-dock` 識別子、spec-dock 操作委譲を示す説明、`.agents/skills/spec-dock-codex-adapter/SKILL.md` を指す委譲表現を必須にする。
    - Copilot agent markdown は `spec-dock` 識別子、spec-dock 操作委譲を示す説明、`.agents/skills/spec-dock-copilot-adapter/SKILL.md` を指す委譲表現を必須にする。
  - `src/spec_dock/cli.py` の installer sync/prune を拡張し、managed native shim だけを更新/削除し、unknown custom native file は保持する。
  - `tests/test_init_update.py` を中心に installer regression を追加し、gate-2 sync/prune verification を機械化する。
  - dogfooding workspace と manual validation 証跡を同 issue の closure evidence として残す。
- MUST NOT:
  - native shim に runtime state payload の再定義や `active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `read-order` の直接記述を持たせない。
  - `.agents/skills/*` を host-native shim へ置き換えない。skill は正本のまま維持する。
  - unknown custom native shim や unknown custom skill を prune しない。
- OUT OF SCOPE:
  - protocol/state 契約そのものの再設計
  - `validate` / `doctor` の新しい責務追加
  - host-native shim 以外の新 host 対応

## 境界
- Always:
  - provider-side source of truth は `src/spec_dock/...` を先に直す。
  - dogfooding mirror は provider 更新の結果確認と manual validation 証跡に使う。
  - 実装と確認評価は同じ issue の中で閉じる。
- Ask:
  - なし。issue/epic docs で契約は固定済み。
- Never:
  - local-only shortcut で native shim を手作業生成しない。
  - native shim を新しい state owner にしない。

## 非交渉制約
- canonical managed target filename は `.codex/agents/spec-dock.toml` と `.github/agents/spec-dock.agent.md` に固定する。
- manifest の単一正本は `.agents/host-adapters/meta.json` に固定する。
- required host set は `codex` と `copilot` の両方固定であり、fallback は証跡種別を代替しても host 要件自体は減らさない。

## 前提
- `iss-00049` / `iss-00050` は done のまま baseline accepted scope として維持される。
- extension follow-up は `iss-00051` 単体で閉じる。

## 受け入れ条件
- AC-001:
  - Actor:
    - installer
  - Given:
    - provider-side assets と `.agents/host-adapters/meta.json` の native shim contract が更新されている
  - When:
    - `spec-dock init <repo>` または `spec-dock update <repo>` を実行する
  - Then:
    - `.codex/agents/spec-dock.toml` と `.github/agents/spec-dock.agent.md` が managed native shim として生成/更新される
    - `.agents/host-adapters/meta.json` が exact field shape を保持する
  - 観測点:
    - file tree
    - meta.json contents
    - init/update regression tests
- AC-002:
  - Actor:
    - installer
  - Given:
    - `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke` 済みの temp repo がある
    - obsolete managed native shim fixture として `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md` を配置している
    - unknown custom native shim fixture として `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md` を配置している
  - When:
    - `uvx --from . spec-dock update /tmp/spec-dock-native-shim-smoke` を実行する
  - Then:
    - obsolete managed native shim は prune される
    - unknown custom native shim と unknown custom skill は保持される
    - baseline skill / metadata は壊れず、`targets.codex.entry_file` / `targets.copilot.entry_file` は既存 contract のまま維持される
    - `gate_2_sync_prune_pass` は次の 5 subcheck が全て `true` のときのみ `true`
      - `managed_codex_shim_generated_or_updated.pass`
      - `managed_copilot_shim_generated_or_updated.pass`
      - `obsolete_managed_fixture_pruned.pass`
      - `unknown_custom_fixture_preserved.pass`
      - `baseline_skill_and_metadata_untouched.pass`
  - 観測点:
    - `gate_2_sync_prune_evidence.*`
    - installer tests
- AC-003:
  - Actor:
    - orchestrator / reviewer
  - Given:
    - dogfooding workspace に native shim が配備されている
  - When:
    - Codex では `.codex/agents/spec-dock.toml`、Copilot では `.github/agents/spec-dock.agent.md` を選択し、`Summarize the active spec-dock target and the next workflow doc to read before editing.` を実行する
  - Then:
    - 両 host とも次の fixed key が記録される
      - `selection_evidence_format`
      - `selection_signal_expected_any`
      - `selection_signal_observed`
      - `selection_signal_pass`
      - `response_target_expected`
      - `response_target_observed`
      - `response_target_pass`
      - `next_doc_expected_any`
      - `next_doc_observed`
      - `next_doc_pass`
      - `delegation_evidence_expected`
      - `delegation_evidence_observed`
      - `delegation_evidence_pass`
      - `non_reimplementation_evidence_expected`
      - `non_reimplementation_evidence_observed`
      - `non_reimplementation_evidence_pass`
      - `direct_protocol_read_expected`
      - `direct_protocol_read_observed`
      - `direct_protocol_read_pass`
      - `fallback_evidence_required`
      - `fallback_evidence_observed`
      - `fallback_evidence_pass`
    - accepted evidence format は `transcript_fragment` / `ui_screenshot` / `cli_log` の 3 種のみ
    - Codex の `selection_signal_expected_any` は `["spec-dock.toml", ".codex/agents/spec-dock.toml"]` に固定する
    - Copilot の `selection_signal_expected_any` は `["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]` に固定する
    - `selection_signal_pass` は host ごとの `selection_signal_expected_any` 配列要素が `selection_signal_observed` に exact match で含まれる場合のみ `true`
    - `response_target_expected` は両 host 共通で `active target summary or active-none stop` に固定する
    - `response_target_pass` は `response_target_observed` が active target 要約または `active-none` 停止を示す場合のみ `true`
    - `next_doc_expected_any` は両 host 共通で `["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]` に固定する
    - `next_doc_pass` は `next_doc_expected_any` 配列要素のいずれかが `next_doc_observed` に exact match で含まれる場合のみ `true`
    - Codex の `delegation_evidence_expected` は `.agents/skills/spec-dock-codex-adapter/SKILL.md` に固定する
    - Copilot の `delegation_evidence_expected` は `.agents/skills/spec-dock-copilot-adapter/SKILL.md` に固定する
    - `delegation_evidence_pass` は host ごとの `delegation_evidence_expected` が `delegation_evidence_observed` に exact match で含まれ、shim から skill への委譲成立が読める場合のみ `true`
    - `non_reimplementation_evidence_pass` は host 対象 shim に対する `rg -n '"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*=' <host shim>` の no-match と `.agent/*.json` / `context-pack.md` 非 inline を同時に示す場合のみ `true`
    - `direct_protocol_read_pass` は host 対象 shim に対する `rg -n "active\\.json|index\\.json|deps-issues\\.json|index-all\\.json|read[ -]order"` の no-match を示す場合のみ `true`
    - `fallback_evidence_pass` は `fallback_evidence_required=false` なら direct host verification 成立時のみ、`true` なら artifact snapshot・delegation static check・non-reimplementation static check・dated transcript/ui screenshot/cli log の束がそろう場合のみ `true`
    - shim は discovery/delegation only であり、skill への委譲と no direct protocol read が確認できる
  - 観測点:
    - `gate_3_manual_validation.codex.*`
    - `gate_3_manual_validation.copilot.*`
- AC-004:
  - Actor:
    - spec reviewer
  - Given:
    - issue docs / implementation / tests / report がそろっている
  - When:
    - final review を行う
  - Then:
    - report は `baseline_inherited_closure` と `extension_closure` を top-level に持つ fixed closure schema を維持する
    - `extension_closure` には `follow_up_issue_id`, `follow_up_issue_ref`, `follow_up_issue_discussion_ref`, `follow_up_issue_status`, `gate_2_sync_prune_pass`, `gate_2_sync_prune_evidence`, `gate_3_manual_validation`, `gate_4_review_pass`, `gate_4_review_evidence`, `extension_closure_pass` を保持する
    - `gate_4_review_pass=true`
    - `extension_closure_pass=true`
  - 観測点:
    - `gate_4_review_evidence.*`
    - final diff review record

## 例外・エッジケース
- EC-001:
  - 条件:
    - local で片方 host の実機確認ができない
  - 期待:
    - `fallback_evidence_required=true` とし、dated transcript / ui screenshot / cli log と artifact static check を組み合わせて required host set を満たす
  - 観測点:
    - host ごとの `fallback_evidence_*`
- EC-002:
  - 条件:
    - target repo に unknown custom native shim と unknown custom skill が存在する
  - 期待:
    - managed manifest に無い native shim / skill file は保持される
    - 同時に `targets.codex.entry_file` と `targets.copilot.entry_file` は baseline skill contract のまま維持される
  - 観測点:
    - `unknown_custom_fixture_preserved.pass`
    - `baseline_skill_and_metadata_untouched.pass`
- EC-003:
  - 条件:
    - native shim が skill に委譲せず protocol path 名や state payload key を書いてしまう
  - 期待:
    - gate-3 / gate-4 が fail になる
  - 観測点:
    - `delegation_evidence_pass`
    - `non_reimplementation_evidence_pass`
    - `direct_protocol_read_pass`
    - `host_native_scope_consistency_pass`

## 用語（ドメイン語彙）
- TERM-001:
  - native shim:
    - host-native discovery 用の最小 entrypoint。Codex は TOML、Copilot は agent markdown。
- TERM-002:
  - managed native shim:
    - manifest に列挙され、installer sync/prune の対象になる shim。
- TERM-003:
  - required host set:
    - `codex` と `copilot` の両方。fallback は各 host の証跡種別を代替するが host 要件を減らさない。

## closure report schema
- top-level:
  - `baseline_inherited_closure`
  - `extension_closure`
- `baseline_inherited_closure` required keys:
  - `accepted_issues`
  - `baseline_inherited_closure_pass`
- `extension_closure` required keys:
  - `follow_up_issue_id`
  - `follow_up_issue_ref`
  - `follow_up_issue_discussion_ref`
  - `follow_up_issue_status`
  - `gate_2_sync_prune_pass`
  - `gate_2_sync_prune_evidence`
  - `gate_3_manual_validation`
  - `gate_4_review_pass`
  - `gate_4_review_evidence`
  - `extension_closure_pass`
- gate-2 regression additions:
  - `gate_2_sync_prune_pass`:
    - `managed_codex_shim_generated_or_updated.pass=true`
    - `managed_copilot_shim_generated_or_updated.pass=true`
    - `obsolete_managed_fixture_pruned.pass=true`
    - `unknown_custom_fixture_preserved.pass=true`
    - `baseline_skill_and_metadata_untouched.pass=true`
  - `gate_2_sync_prune_evidence.baseline_skill_and_metadata_untouched`
    - expected:
      - `.agents/skills/spec-dock-codex-adapter/SKILL.md` remains present
      - `.agents/skills/spec-dock-copilot-adapter/SKILL.md` remains present
      - `targets.codex.entry_file=.agents/skills/spec-dock-codex-adapter/SKILL.md`
      - `targets.copilot.entry_file=.agents/skills/spec-dock-copilot-adapter/SKILL.md`
    - observed:
      - `...`
    - pass:
      - `true | false`
- `gate_4_review_evidence` required keys:
  - `additive_only_scope_preserved_expected/observed/pass`
  - `single_follow_up_issue_rule_expected/observed/pass`
  - `native_manifest_shape_expected/observed/pass`
  - `report_schema_compliance_expected/observed/pass`
  - `discussion_schema_compliance_expected/observed/pass`
  - `host_native_scope_consistency_expected/observed/pass`
  - `final_review_ref`

## 未確定事項
- 該当なし
